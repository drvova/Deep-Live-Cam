"""Frame processors package for Deep-Live-Cam."""

from modules.processors.registry import (
    get_frame_processors_modules,
    load_frame_processor_module,
    multi_process_frame,
    process_video,
    set_frame_processors_modules_from_ui,
)

__all__ = [
    "get_frame_processors_modules",
    "load_frame_processor_module",
    "set_frame_processors_modules_from_ui",
    "multi_process_frame",
    "process_video",
]
