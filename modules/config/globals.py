"""Global configuration module with type hints and sensible defaults."""

import os
from typing import Any, Dict, List, Optional

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKFLOW_DIR = os.path.join(ROOT_DIR, "workflow")

file_types = [
    ("Image", ("*.png", "*.jpg", "*.jpeg", "*.gif", "*.bmp")),
    ("Video", ("*.mp4", "*.mkv")),
]

# Face Mapping Data
source_target_map: List[Dict[str, Any]] = []
simple_map: Dict[str, Any] = {}

# Paths
source_path: Optional[str] = None
target_path: Optional[str] = None
output_path: Optional[str] = None

# Processing Options
frame_processors: List[str] = []
keep_fps: bool = True
keep_audio: bool = True
keep_frames: bool = False
many_faces: bool = False
map_faces: bool = False
color_correction: bool = False
nsfw_filter: bool = False

# Video Output Options
video_encoder: str = "libx264"
video_quality: int = 18

# Live Mode Options
live_mirror: bool = False
live_resizable: bool = True
camera_input_combobox: Optional[Any] = None
webcam_preview_running: bool = False
show_fps: bool = False

# System Configuration
max_memory: Optional[int] = None
execution_providers: List[str] = []
execution_threads: int = 8
headless: bool = False
log_level: str = "error"
lang: str = "en"

# Face Processor UI Toggles
fp_ui: Dict[str, bool] = {"face_enhancer": False}

# Face Swapper Options
face_swapper_enabled: bool = True
opacity: float = 1.0
sharpness: float = 0.0

# Mouth Mask Options
mouth_mask: bool = False
show_mouth_mask_box: bool = False
mask_feather_ratio: int = 12
mask_down_size: float = 0.1
mask_size: float = 1.0

# Frame Interpolation
enable_interpolation: bool = True
interpolation_weight: float = 0.0
