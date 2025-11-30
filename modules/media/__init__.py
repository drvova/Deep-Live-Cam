"""Media I/O package for Deep-Live-Cam."""

from modules.media.capturer import get_video_frame, get_video_frame_total
from modules.media.ffmpeg import (
    clean_temp,
    conditional_download,
    create_temp,
    create_video,
    detect_fps,
    extract_frames,
    get_temp_directory_path,
    get_temp_frame_paths,
    get_temp_output_path,
    has_image_extension,
    is_image,
    is_video,
    move_temp,
    normalize_output_path,
    resolve_relative_path,
    restore_audio,
    run_ffmpeg,
)

__all__ = [
    # Capturer
    "get_video_frame",
    "get_video_frame_total",
    # FFmpeg utilities
    "run_ffmpeg",
    "detect_fps",
    "extract_frames",
    "create_video",
    "restore_audio",
    "get_temp_frame_paths",
    "get_temp_directory_path",
    "get_temp_output_path",
    "normalize_output_path",
    "create_temp",
    "move_temp",
    "clean_temp",
    "has_image_extension",
    "is_image",
    "is_video",
    "conditional_download",
    "resolve_relative_path",
]
