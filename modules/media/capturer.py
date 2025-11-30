"""Video frame capture module for Deep-Live-Cam."""

from typing import Any, Optional

import cv2

from modules.config import globals as config


def get_video_frame(video_path: str, frame_number: int = 0) -> Optional[Any]:
    """Extract a single frame from a video file.

    Args:
        video_path: Path to the video file.
        frame_number: Frame number to extract (1-indexed).

    Returns:
        The extracted frame as a numpy array, or None if extraction failed.
    """
    capture = cv2.VideoCapture(video_path)

    # Set MJPEG format to ensure correct color space handling
    capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))

    # Only force RGB conversion if color correction is enabled
    if config.color_correction:
        capture.set(cv2.CAP_PROP_CONVERT_RGB, 1)

    frame_total = capture.get(cv2.CAP_PROP_FRAME_COUNT)
    capture.set(cv2.CAP_PROP_POS_FRAMES, min(frame_total, frame_number - 1))
    has_frame, frame = capture.read()

    if has_frame and config.color_correction:
        # Convert the frame color if necessary
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    capture.release()
    return frame if has_frame else None


def get_video_frame_total(video_path: str) -> int:
    """Get the total number of frames in a video file.

    Args:
        video_path: Path to the video file.

    Returns:
        Total number of frames in the video.
    """
    capture = cv2.VideoCapture(video_path)
    video_frame_total = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    capture.release()
    return video_frame_total
