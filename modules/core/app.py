import os
import sys

# single thread doubles cuda performance - needs to be set before torch import
if any(arg.startswith("--execution-provider") for arg in sys.argv):
    os.environ["OMP_NUM_THREADS"] = "1"
# reduce tensorflow log level
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
import argparse
import platform
import shutil
import signal
import warnings
from typing import List

import onnxruntime
import tensorflow
import torch

from modules.config import globals as config
from modules.config import metadata
from modules.media import (
    clean_temp,
    create_temp,
    create_video,
    detect_fps,
    extract_frames,
    get_temp_frame_paths,
    has_image_extension,
    is_image,
    is_video,
    move_temp,
    normalize_output_path,
    restore_audio,
)
from modules.processors.registry import get_frame_processors_modules
from modules.ui import app as ui

if "ROCMExecutionProvider" in config.execution_providers:
    del torch

warnings.filterwarnings("ignore", category=FutureWarning, module="insightface")
warnings.filterwarnings("ignore", category=UserWarning, module="torchvision")


def parse_args() -> None:
    signal.signal(signal.SIGINT, lambda signal_number, frame: destroy())
    program = argparse.ArgumentParser()
    program.add_argument(
        "-s", "--source", help="select an source image", dest="source_path"
    )
    program.add_argument(
        "-t", "--target", help="select an target image or video", dest="target_path"
    )
    program.add_argument(
        "-o", "--output", help="select output file or directory", dest="output_path"
    )
    program.add_argument(
        "--frame-processor",
        help="pipeline of frame processors",
        dest="frame_processor",
        default=["face_swapper"],
        choices=["face_swapper", "face_enhancer"],
        nargs="+",
    )
    program.add_argument(
        "--keep-fps",
        help="keep original fps",
        dest="keep_fps",
        action="store_true",
        default=False,
    )
    program.add_argument(
        "--keep-audio",
        help="keep original audio",
        dest="keep_audio",
        action="store_true",
        default=True,
    )
    program.add_argument(
        "--keep-frames",
        help="keep temporary frames",
        dest="keep_frames",
        action="store_true",
        default=False,
    )
    program.add_argument(
        "--many-faces",
        help="process every face",
        dest="many_faces",
        action="store_true",
        default=False,
    )
    program.add_argument(
        "--nsfw-filter",
        help="filter the NSFW image or video",
        dest="nsfw_filter",
        action="store_true",
        default=False,
    )
    program.add_argument(
        "--map-faces",
        help="map source target faces",
        dest="map_faces",
        action="store_true",
        default=False,
    )
    program.add_argument(
        "--mouth-mask",
        help="mask the mouth region",
        dest="mouth_mask",
        action="store_true",
        default=False,
    )
    program.add_argument(
        "--video-encoder",
        help="adjust output video encoder",
        dest="video_encoder",
        default="libx264",
        choices=["libx264", "libx265", "libvpx-vp9"],
    )
    program.add_argument(
        "--video-quality",
        help="adjust output video quality",
        dest="video_quality",
        type=int,
        default=18,
        choices=range(52),
        metavar="[0-51]",
    )
    program.add_argument("-l", "--lang", help="Ui language", default="en")
    program.add_argument(
        "--live-mirror",
        help="The live camera display as you see it in the front-facing camera frame",
        dest="live_mirror",
        action="store_true",
        default=False,
    )
    program.add_argument(
        "--live-resizable",
        help="The live camera frame is resizable",
        dest="live_resizable",
        action="store_true",
        default=False,
    )
    program.add_argument(
        "--max-memory",
        help="maximum amount of RAM in GB",
        dest="max_memory",
        type=int,
        default=suggest_max_memory(),
    )
    program.add_argument(
        "--execution-provider",
        help="execution provider",
        dest="execution_provider",
        default=["cpu"],
        choices=suggest_execution_providers(),
        nargs="+",
    )
    program.add_argument(
        "--execution-threads",
        help="number of execution threads",
        dest="execution_threads",
        type=int,
        default=suggest_execution_threads(),
    )
    program.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"{metadata.name} {metadata.version}",
    )

    # register deprecated args
    program.add_argument(
        "-f", "--face", help=argparse.SUPPRESS, dest="source_path_deprecated"
    )
    program.add_argument(
        "--cpu-cores", help=argparse.SUPPRESS, dest="cpu_cores_deprecated", type=int
    )
    program.add_argument(
        "--gpu-vendor", help=argparse.SUPPRESS, dest="gpu_vendor_deprecated"
    )
    program.add_argument(
        "--gpu-threads", help=argparse.SUPPRESS, dest="gpu_threads_deprecated", type=int
    )

    args = program.parse_args()

    config.source_path = args.source_path
    config.target_path = args.target_path
    config.output_path = normalize_output_path(
        config.source_path, config.target_path, args.output_path
    )
    config.frame_processors = args.frame_processor
    config.headless = args.source_path or args.target_path or args.output_path
    config.keep_fps = args.keep_fps
    config.keep_audio = args.keep_audio
    config.keep_frames = args.keep_frames
    config.many_faces = args.many_faces
    config.mouth_mask = args.mouth_mask
    config.nsfw_filter = args.nsfw_filter
    config.map_faces = args.map_faces
    config.video_encoder = args.video_encoder
    config.video_quality = args.video_quality
    config.live_mirror = args.live_mirror
    config.live_resizable = args.live_resizable
    config.max_memory = args.max_memory
    config.execution_providers = decode_execution_providers(args.execution_provider)
    config.execution_threads = args.execution_threads
    config.lang = args.lang

    # for ENHANCER tumbler:
    if "face_enhancer" in args.frame_processor:
        config.fp_ui["face_enhancer"] = True
    else:
        config.fp_ui["face_enhancer"] = False

    # translate deprecated args
    if args.source_path_deprecated:
        print(
            "\033[33mArgument -f and --face are deprecated. Use -s and --source instead.\033[0m"
        )
        config.source_path = args.source_path_deprecated
        config.output_path = normalize_output_path(
            args.source_path_deprecated, config.target_path, args.output_path
        )
    if args.cpu_cores_deprecated:
        print(
            "\033[33mArgument --cpu-cores is deprecated. Use --execution-threads instead.\033[0m"
        )
        config.execution_threads = args.cpu_cores_deprecated
    if args.gpu_vendor_deprecated == "apple":
        print(
            "\033[33mArgument --gpu-vendor apple is deprecated. Use --execution-provider coreml instead.\033[0m"
        )
        config.execution_providers = decode_execution_providers(["coreml"])
    if args.gpu_vendor_deprecated == "nvidia":
        print(
            "\033[33mArgument --gpu-vendor nvidia is deprecated. Use --execution-provider cuda instead.\033[0m"
        )
        config.execution_providers = decode_execution_providers(["cuda"])
    if args.gpu_vendor_deprecated == "amd":
        print(
            "\033[33mArgument --gpu-vendor amd is deprecated. Use --execution-provider cuda instead.\033[0m"
        )
        config.execution_providers = decode_execution_providers(["rocm"])
    if args.gpu_threads_deprecated:
        print(
            "\033[33mArgument --gpu-threads is deprecated. Use --execution-threads instead.\033[0m"
        )
        config.execution_threads = args.gpu_threads_deprecated


def encode_execution_providers(execution_providers: List[str]) -> List[str]:
    return [
        execution_provider.replace("ExecutionProvider", "").lower()
        for execution_provider in execution_providers
    ]


def decode_execution_providers(execution_providers: List[str]) -> List[str]:
    return [
        provider
        for provider, encoded_execution_provider in zip(
            onnxruntime.get_available_providers(),
            encode_execution_providers(onnxruntime.get_available_providers()),
        )
        if any(
            execution_provider in encoded_execution_provider
            for execution_provider in execution_providers
        )
    ]


def suggest_max_memory() -> int:
    if platform.system().lower() == "darwin":
        return 4
    return 16


def suggest_execution_providers() -> List[str]:
    return encode_execution_providers(onnxruntime.get_available_providers())


def suggest_execution_threads() -> int:
    if "DmlExecutionProvider" in config.execution_providers:
        return 1
    if "ROCMExecutionProvider" in config.execution_providers:
        return 1
    return 8


def limit_resources() -> None:
    # prevent tensorflow memory leak
    gpus = tensorflow.config.experimental.list_physical_devices("GPU")
    for gpu in gpus:
        tensorflow.config.experimental.set_memory_growth(gpu, True)
    # limit memory usage
    if config.max_memory:
        memory = config.max_memory * 1024**3
        if platform.system().lower() == "darwin":
            memory = config.max_memory * 1024**6
        if platform.system().lower() == "windows":
            import ctypes

            kernel32 = ctypes.windll.kernel32
            kernel32.SetProcessWorkingSetSize(
                -1, ctypes.c_size_t(memory), ctypes.c_size_t(memory)
            )
        else:
            import resource

            resource.setrlimit(resource.RLIMIT_DATA, (memory, memory))


def release_resources() -> None:
    if "CUDAExecutionProvider" in config.execution_providers:
        torch.cuda.empty_cache()


def pre_check() -> bool:
    if sys.version_info < (3, 9):
        update_status(
            "Python version is not supported - please upgrade to 3.9 or higher."
        )
        return False
    if not shutil.which("ffmpeg"):
        update_status("ffmpeg is not installed.")
        return False
    return True


def update_status(message: str, scope: str = "DLC.CORE") -> None:
    print(f"[{scope}] {message}")
    if not config.headless:
        ui.update_status(message)


def start() -> None:
    for frame_processor in get_frame_processors_modules(config.frame_processors):
        if not frame_processor.pre_start():
            return
    update_status("Processing...")
    # process image to image
    if has_image_extension(config.target_path):
        if config.nsfw_filter and ui.check_and_ignore_nsfw(config.target_path, destroy):
            return
        try:
            shutil.copy2(config.target_path, config.output_path)
        except Exception as e:
            print("Error copying file:", str(e))
        for frame_processor in get_frame_processors_modules(config.frame_processors):
            update_status("Progressing...", frame_processor.NAME)
            frame_processor.process_image(
                config.source_path, config.output_path, config.output_path
            )
            release_resources()
        if is_image(config.target_path):
            update_status("Processing to image succeed!")
        else:
            update_status("Processing to image failed!")
        return
    # process image to videos
    if config.nsfw_filter and ui.check_and_ignore_nsfw(config.target_path, destroy):
        return

    if not config.map_faces:
        update_status("Creating temp resources...")
        create_temp(config.target_path)
        update_status("Extracting frames...")
        extract_frames(config.target_path)

    temp_frame_paths = get_temp_frame_paths(config.target_path)
    for frame_processor in get_frame_processors_modules(config.frame_processors):
        update_status("Progressing...", frame_processor.NAME)
        frame_processor.process_video(config.source_path, temp_frame_paths)
        release_resources()
    # handles fps
    if config.keep_fps:
        update_status("Detecting fps...")
        fps = detect_fps(config.target_path)
        update_status(f"Creating video with {fps} fps...")
        create_video(config.target_path, fps)
    else:
        update_status("Creating video with 30.0 fps...")
        create_video(config.target_path)
    # handle audio
    if config.keep_audio:
        if config.keep_fps:
            update_status("Restoring audio...")
        else:
            update_status("Restoring audio might cause issues as fps are not kept...")
        restore_audio(config.target_path, config.output_path)
    else:
        move_temp(config.target_path, config.output_path)
    # clean and validate
    clean_temp(config.target_path)
    if is_video(config.target_path):
        update_status("Processing to video succeed!")
    else:
        update_status("Processing to video failed!")


def destroy(to_quit=True) -> None:
    if config.target_path:
        clean_temp(config.target_path)
    if to_quit:
        quit()


def run() -> None:
    parse_args()
    if not pre_check():
        return
    for frame_processor in get_frame_processors_modules(config.frame_processors):
        if not frame_processor.pre_check():
            return
    limit_resources()
    if config.headless:
        start()
    else:
        window = ui.init(start, destroy, config.lang)
        window.mainloop()
