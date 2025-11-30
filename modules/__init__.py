"""
Deep-Live-Cam modules package.

This package provides the core functionality for face swapping and enhancement.

New Structure:
    - config/     : Configuration and global settings
    - core/       : Core application logic and types
    - face/       : Face detection, analysis, and clustering
    - media/      : Video/image capture and FFmpeg utilities
    - processors/ : Frame processors (swapper, enhancer, masking)
    - ui/         : User interface components
    - i18n/       : Internationalization support
"""

# Backward compatibility imports
from modules.config import globals, metadata
from modules.core.types import Face, Frame

__all__ = [
    "globals",
    "metadata",
    "Face",
    "Frame",
]
