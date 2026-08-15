"""Segmentation of detected potholes.

Kept modular: in demo mode a mask is approximated from the detection bounding
box. A real segmentation model (YOLOv8-seg / SAM) can be plugged into
``Segmenter.segment`` without changing the rest of the pipeline.
"""
from __future__ import annotations

import numpy as np
from PIL import Image


class Segmenter:
    def __init__(self, demo: bool = True) -> None:
        self.demo_mode = demo

    def segment(self, image: Image.Image, detections: list[dict]) -> list[dict]:
        """Return per-detection segmentation info.

        Each item: {index, mask_available, pixel_area, bbox, mask_base64?}
        Mask payloads are intentionally omitted from API responses to keep them
        light; only the pixel area and mask availability are exposed.
        """
        gray = np.asarray(image.convert("L"))
        results = []
        for i, det in enumerate(detections):
            bbox = det["bbox"]
            x1, y1, x2, y2 = (int(v) for v in bbox)
            x1, y1 = max(0, x1), max(0, y1)
            x2 = min(gray.shape[1], x2)
            y2 = min(gray.shape[0], y2)
            if x2 <= x1 or y2 <= y1:
                results.append(
                    {"index": i, "mask_available": False, "pixel_area": 0.0, "bbox": bbox}
                )
                continue

            patch = gray[y1:y2, x1:x2]
            if self.demo_mode:
                # Approximate the "damaged" region inside the box: darker pixels
                # (asphalt cracks/pothole shadows) minus a fixed offset.
                thr = int(patch.mean()) - 12
                mask = patch < thr
                area = float(mask.sum())
            else:
                area = float(patch.size)  # real segmentation replaces this

            results.append(
                {"index": i, "mask_available": True, "pixel_area": round(area, 1), "bbox": bbox}
            )
        return results
