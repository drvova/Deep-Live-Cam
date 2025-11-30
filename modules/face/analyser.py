import os
import shutil
from pathlib import Path
from typing import Any, List, Optional

import cv2
import insightface
import numpy as np
from tqdm import tqdm

from modules.config import globals as config
from modules.core.types import Frame
from modules.face.cluster import find_closest_centroid, find_cluster_centroids
from modules.media import (
    clean_temp,
    create_temp,
    extract_frames,
    get_temp_directory_path,
    get_temp_frame_paths,
)

FACE_ANALYSER = None


def get_face_analyser() -> Any:
    global FACE_ANALYSER
    if FACE_ANALYSER is None:
        FACE_ANALYSER = insightface.app.FaceAnalysis(
            name="buffalo_l", providers=config.execution_providers
        )
        FACE_ANALYSER.prepare(ctx_id=0, det_size=(640, 640))
    return FACE_ANALYSER


def get_one_face(frame: Frame) -> Any:
    face = get_face_analyser().get(frame)
    try:
        return min(face, key=lambda x: x.bbox[0])
    except ValueError:
        return None


def get_many_faces(frame: Frame) -> Any:
    try:
        return get_face_analyser().get(frame)
    except IndexError:
        return None


def has_valid_map() -> bool:
    return any("source" in m and "target" in m for m in config.source_target_map)


def default_source_face() -> Any:
    for m in config.source_target_map:
        if "source" in m:
            return m["source"]["face"]
    return None


def simplify_maps() -> None:
    source_target_map = config.source_target_map
    valid_maps = [
        (m["source"]["face"], m["target"]["face"].normed_embedding)
        for m in source_target_map
        if "source" in m and "target" in m
    ]
    if valid_maps:
        faces, centroids = zip(*valid_maps)
        config.simple_map = {
            "source_faces": list(faces),
            "target_embeddings": list(centroids),
        }
    else:
        config.simple_map = {"source_faces": [], "target_embeddings": []}


def add_blank_map() -> None:
    source_target_map = config.source_target_map
    max_id = max((m["id"] for m in source_target_map), default=-1)
    source_target_map.append({"id": max_id + 1})


def get_unique_faces_from_target_image() -> None:
    config.source_target_map = []
    target_frame = cv2.imread(config.target_path)
    if target_frame is None:
        return
    many_faces = get_many_faces(target_frame)
    if not many_faces:
        return
    for i, face in enumerate(many_faces):
        x_min, y_min, x_max, y_max = map(int, face["bbox"])
        config.source_target_map.append(
            {
                "id": i,
                "target": {"cv2": target_frame[y_min:y_max, x_min:x_max], "face": face},
            }
        )


def get_unique_faces_from_target_video() -> None:
    target_path = config.target_path
    config.source_target_map = []

    print("Creating temp resources...")
    clean_temp(target_path)
    create_temp(target_path)
    print("Extracting frames...")
    extract_frames(target_path)

    temp_frame_paths = sorted(get_temp_frame_paths(target_path))
    if not temp_frame_paths:
        return

    frame_face_embeddings = []
    face_embeddings = []

    for i, temp_frame_path in enumerate(
        tqdm(temp_frame_paths, desc="Extracting face embeddings")
    ):
        temp_frame = cv2.imread(temp_frame_path)
        if temp_frame is None:
            continue
        many_faces = get_many_faces(temp_frame) or []
        face_embeddings.extend(face.normed_embedding for face in many_faces)
        frame_face_embeddings.append(
            {"frame": i, "faces": many_faces, "location": temp_frame_path}
        )

    if not face_embeddings:
        return

    centroids = find_cluster_centroids(face_embeddings)
    num_centroids = len(centroids)

    # Assign centroid to each face in single pass
    for frame in frame_face_embeddings:
        for face in frame["faces"]:
            idx, _ = find_closest_centroid(centroids, face.normed_embedding)
            face["target_centroid"] = idx

    # Build centroid maps in single pass (O(n) instead of O(n*k))
    centroid_frames = {i: [] for i in range(num_centroids)}
    for frame in tqdm(frame_face_embeddings, desc="Building centroid maps"):
        for i in range(num_centroids):
            matching_faces = [f for f in frame["faces"] if f["target_centroid"] == i]
            centroid_frames[i].append(
                {
                    "frame": frame["frame"],
                    "faces": matching_faces,
                    "location": frame["location"],
                }
            )

    for i in range(num_centroids):
        config.source_target_map.append(
            {"id": i, "target_faces_in_frame": centroid_frames[i]}
        )

    default_target_face()


def default_target_face() -> None:
    for m in config.source_target_map:
        frames_with_faces = [
            (frame, face)
            for frame in m.get("target_faces_in_frame", [])
            for face in frame["faces"]
        ]
        if not frames_with_faces:
            continue
        best_frame, best_face = max(frames_with_faces, key=lambda x: x[1]["det_score"])
        x_min, y_min, x_max, y_max = map(int, best_face["bbox"])
        target_frame = cv2.imread(best_frame["location"])
        if target_frame is not None:
            m["target"] = {
                "cv2": target_frame[y_min:y_max, x_min:x_max],
                "face": best_face,
            }


def dump_faces(centroids: Any, frame_face_embeddings: list) -> None:
    temp_directory_path = get_temp_directory_path(config.target_path)
    num_centroids = len(centroids)

    # Prepare directories
    for i in range(num_centroids):
        centroid_dir = os.path.join(temp_directory_path, str(i))
        if os.path.isdir(centroid_dir):
            shutil.rmtree(centroid_dir)
        Path(centroid_dir).mkdir(parents=True, exist_ok=True)

    # Process frames once, write to appropriate centroid dirs
    for frame in tqdm(frame_face_embeddings, desc="Copying faces to temp"):
        temp_frame = cv2.imread(frame["location"])
        if temp_frame is None:
            continue
        for j, face in enumerate(frame["faces"]):
            i = face.get("target_centroid")
            if i is None:
                continue
            x_min, y_min, x_max, y_max = map(int, face["bbox"])
            face_crop = temp_frame[y_min:y_max, x_min:x_max]
            if face_crop.size > 0:
                out_path = os.path.join(
                    temp_directory_path, str(i), f"{frame['frame']}_{j}.png"
                )
                cv2.imwrite(out_path, face_crop)
