"""FFmpeg and file utilities for Deep-Live-Cam."""

import glob
import mimetypes
import os
import platform
import shutil
import ssl
import subprocess
import urllib.request
from pathlib import Path
from typing import Any, List, Optional

from tqdm import tqdm

from modules.config import globals as config

TEMP_FILE = "temp.mp4"
TEMP_DIRECTORY = "temp"

# Monkey patch SSL for macOS
if platform.system().lower() == "darwin":
    ssl._create_default_https_context = ssl._create_unverified_context


def run_ffmpeg(args: List[str]) -> bool:
    """Execute ffmpeg command with hardware acceleration."""
    commands = [
        "ffmpeg",
        "-hide_banner",
        "-hwaccel",
        "auto",
        "-loglevel",
        config.log_level,
        *args,
    ]
    try:
        subprocess.check_output(commands, stderr=subprocess.STDOUT)
        return True
    except subprocess.CalledProcessError:
        return False


def detect_fps(target_path: str) -> float:
    """Detect video FPS using ffprobe."""
    command = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=r_frame_rate",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        target_path,
    ]
    try:
        output = subprocess.check_output(command).decode().strip()
        if "/" in output:
            num, denom = map(int, output.split("/"))
            return num / denom if denom else 30.0
    except (subprocess.CalledProcessError, ValueError, ZeroDivisionError):
        pass
    return 30.0


def extract_frames(target_path: str) -> None:
    """Extract frames from video using ffmpeg."""
    temp_dir = get_temp_directory_path(target_path)
    run_ffmpeg(
        ["-i", target_path, "-pix_fmt", "rgb24", os.path.join(temp_dir, "%04d.png")]
    )


def create_video(target_path: str, fps: float = 30.0) -> None:
    """Create video from frames using ffmpeg."""
    temp_output = get_temp_output_path(target_path)
    temp_dir = get_temp_directory_path(target_path)
    run_ffmpeg(
        [
            "-r",
            str(fps),
            "-i",
            os.path.join(temp_dir, "%04d.png"),
            "-c:v",
            config.video_encoder,
            "-crf",
            str(config.video_quality),
            "-pix_fmt",
            "yuv420p",
            "-vf",
            "colorspace=bt709:iall=bt601-6-625:fast=1",
            "-y",
            temp_output,
        ]
    )


def restore_audio(target_path: str, output_path: str) -> None:
    """Restore audio from source video to output."""
    temp_output = get_temp_output_path(target_path)
    success = run_ffmpeg(
        [
            "-i",
            temp_output,
            "-i",
            target_path,
            "-c:v",
            "copy",
            "-map",
            "0:v:0",
            "-map",
            "1:a:0",
            "-y",
            output_path,
        ]
    )
    if not success:
        move_temp(target_path, output_path)


def get_temp_frame_paths(target_path: str) -> List[str]:
    """Get sorted list of temporary frame paths."""
    temp_dir = get_temp_directory_path(target_path)
    pattern = os.path.join(glob.escape(temp_dir), "*.png")
    return sorted(glob.glob(pattern))


def get_temp_directory_path(target_path: str) -> str:
    """Get temporary directory path for target."""
    target_name = Path(target_path).stem
    target_dir = os.path.dirname(target_path)
    return os.path.join(target_dir, TEMP_DIRECTORY, target_name)


def get_temp_output_path(target_path: str) -> str:
    """Get temporary output file path."""
    return os.path.join(get_temp_directory_path(target_path), TEMP_FILE)


def normalize_output_path(
    source_path: Optional[str], target_path: Optional[str], output_path: Optional[str]
) -> Any:
    """Normalize output path based on source and target."""
    if source_path and target_path and output_path and os.path.isdir(output_path):
        source_stem = Path(source_path).stem
        target_stem = Path(target_path).stem
        target_ext = Path(target_path).suffix
        return os.path.join(output_path, f"{source_stem}-{target_stem}{target_ext}")
    return output_path


def create_temp(target_path: str) -> None:
    """Create temporary directory."""
    Path(get_temp_directory_path(target_path)).mkdir(parents=True, exist_ok=True)


def move_temp(target_path: str, output_path: str) -> None:
    """Move temporary output to final destination."""
    temp_output = get_temp_output_path(target_path)
    if os.path.isfile(temp_output):
        if os.path.isfile(output_path):
            os.remove(output_path)
        shutil.move(temp_output, output_path)


def clean_temp(target_path: str) -> None:
    """Clean up temporary files."""
    temp_dir = get_temp_directory_path(target_path)
    parent_dir = os.path.dirname(temp_dir)

    if not config.keep_frames and os.path.isdir(temp_dir):
        shutil.rmtree(temp_dir)

    if os.path.exists(parent_dir) and not os.listdir(parent_dir):
        os.rmdir(parent_dir)


def has_image_extension(image_path: str) -> bool:
    """Check if path has image extension."""
    return image_path.lower().endswith(("png", "jpg", "jpeg"))


def is_image(image_path: str) -> bool:
    """Check if path is a valid image file."""
    if image_path and os.path.isfile(image_path):
        mimetype, _ = mimetypes.guess_type(image_path)
        return bool(mimetype and mimetype.startswith("image/"))
    return False


def is_video(video_path: str) -> bool:
    """Check if path is a valid video file."""
    if video_path and os.path.isfile(video_path):
        mimetype, _ = mimetypes.guess_type(video_path)
        return bool(mimetype and mimetype.startswith("video/"))
    return False


def conditional_download(download_directory_path: str, urls: List[str]) -> None:
    """Download files if they don't exist."""
    os.makedirs(download_directory_path, exist_ok=True)

    for url in urls:
        filename = os.path.basename(url)
        download_path = os.path.join(download_directory_path, filename)

        if os.path.exists(download_path):
            continue

        try:
            request = urllib.request.urlopen(url)
            total = int(request.headers.get("Content-Length", 0))

            with tqdm(
                total=total,
                desc=f"Downloading {filename}",
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
            ) as progress:
                urllib.request.urlretrieve(
                    url,
                    download_path,
                    reporthook=lambda count, block_size, total_size: progress.update(
                        block_size
                    ),
                )
        except Exception as e:
            print(f"Error downloading {url}: {e}")


def resolve_relative_path(path: str) -> str:
    """Resolve path relative to this module."""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), path))
