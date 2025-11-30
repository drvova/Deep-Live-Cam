"""Frame processor registry for Deep-Live-Cam."""

import importlib
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from types import ModuleType
from typing import Any, Callable, List

from tqdm import tqdm

from modules.config import globals as config

FRAME_PROCESSORS_MODULES: List[ModuleType] = []
FRAME_PROCESSORS_INTERFACE = [
    "pre_check",
    "pre_start",
    "process_frame",
    "process_image",
    "process_video",
]

# Batch size for frame processing - reduces thread overhead
BATCH_SIZE = 8


def load_frame_processor_module(frame_processor: str) -> Any:
    try:
        frame_processor_module = importlib.import_module(
            f"modules.processors.frame.{frame_processor}"
        )
        for method_name in FRAME_PROCESSORS_INTERFACE:
            if not hasattr(frame_processor_module, method_name):
                sys.exit()
    except ImportError:
        print(f"Frame processor {frame_processor} not found")
        sys.exit()
    return frame_processor_module


def get_frame_processors_modules(frame_processors: List[str]) -> List[ModuleType]:
    global FRAME_PROCESSORS_MODULES

    if not FRAME_PROCESSORS_MODULES:
        for frame_processor in frame_processors:
            frame_processor_module = load_frame_processor_module(frame_processor)
            FRAME_PROCESSORS_MODULES.append(frame_processor_module)
    set_frame_processors_modules_from_ui(frame_processors)
    return FRAME_PROCESSORS_MODULES


def set_frame_processors_modules_from_ui(frame_processors: List[str]) -> None:
    global FRAME_PROCESSORS_MODULES
    current_names = {proc.__name__.split(".")[-1] for proc in FRAME_PROCESSORS_MODULES}
    fp_ui = config.fp_ui

    for frame_processor, state in fp_ui.items():
        if state and frame_processor not in current_names:
            try:
                module = load_frame_processor_module(frame_processor)
                FRAME_PROCESSORS_MODULES.append(module)
                if frame_processor not in config.frame_processors:
                    config.frame_processors.append(frame_processor)
            except (SystemExit, Exception) as e:
                print(f"Warning: Failed to load frame processor {frame_processor}: {e}")

        elif not state and frame_processor in current_names:
            try:
                module = next(
                    (
                        m
                        for m in FRAME_PROCESSORS_MODULES
                        if m.__name__.endswith(f".{frame_processor}")
                    ),
                    None,
                )
                if module:
                    FRAME_PROCESSORS_MODULES.remove(module)
                if frame_processor in config.frame_processors:
                    config.frame_processors.remove(frame_processor)
            except Exception as e:
                print(f"Warning: Error removing frame processor {frame_processor}: {e}")


def multi_process_frame(
    source_path: str,
    temp_frame_paths: List[str],
    process_frames: Callable[[str, List[str], Any], None],
    progress: Any = None,
) -> None:
    """Process frames in batches to reduce thread overhead."""
    num_threads = config.execution_threads or 4
    total_frames = len(temp_frame_paths)

    # Create batches
    batches = [
        temp_frame_paths[i : i + BATCH_SIZE] for i in range(0, total_frames, BATCH_SIZE)
    ]

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = {
            executor.submit(process_frames, source_path, batch, progress): batch
            for batch in batches
        }
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Error processing batch: {e}")


def process_video(
    source_path: str,
    frame_paths: List[str],
    process_frames: Callable[[str, List[str], Any], None],
) -> None:
    """Process video frames with optimized batching."""
    # Cache globals for faster access
    execution_providers = config.execution_providers
    execution_threads = config.execution_threads
    max_memory = config.max_memory

    progress_format = (
        "{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]"
    )
    total = len(frame_paths)

    with tqdm(
        total=total,
        desc="Processing",
        unit="frame",
        dynamic_ncols=True,
        bar_format=progress_format,
    ) as progress:
        progress.set_postfix(
            {
                "providers": execution_providers,
                "threads": execution_threads,
                "memory": max_memory,
            }
        )
        multi_process_frame(source_path, frame_paths, process_frames, progress)
