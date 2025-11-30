"""NSFW prediction module for Deep-Live-Cam."""

import cv2
import numpy
import opennsfw2
from PIL import Image

from modules.config import globals as config
from modules.core.types import Frame

MAX_PROBABILITY = 0.85

# Preload the model once for efficiency
model = None


def predict_frame(target_frame: Frame) -> bool:
    """Predict if a frame contains NSFW content."""
    # Convert the frame to RGB before processing if color correction is enabled
    if config.color_correction:
        target_frame = cv2.cvtColor(target_frame, cv2.COLOR_BGR2RGB)

    image = Image.fromarray(target_frame)
    image = opennsfw2.preprocess_image(image, opennsfw2.Preprocessing.YAHOO)

    global model
    if model is None:
        model = opennsfw2.make_open_nsfw_model()

    views = numpy.expand_dims(image, axis=0)
    _, probability = model.predict(views)[0]
    return probability > MAX_PROBABILITY


def predict_image(target_path: str) -> bool:
    """Predict if an image file contains NSFW content."""
    return opennsfw2.predict_image(target_path) > MAX_PROBABILITY


def predict_video(target_path: str) -> bool:
    """Predict if a video file contains NSFW content."""
    _, probabilities = opennsfw2.predict_video_frames(
        video_path=target_path, frame_interval=100
    )
    return any(probability > MAX_PROBABILITY for probability in probabilities)
