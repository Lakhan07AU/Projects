"""Pothole detector.

When DEMO_MODE is true the detector returns deterministic mock detections so
the whole pipeline works before a custom model is available. The response is
explicitly flagged as ``demo`` so callers never mistake it for real inference.

When DEMO_MODE is false an Ultralytics YOLO model is loaded from MODEL_PATH.
"""
from __future__ import annotations

import hashlib

from app.core.config import get_settings

settings = get_settings()


class Detector:
    """YOLO-based pothole detector with a demo fallback."""

    def __init__(self, model_path: str | None = None, demo: bool | None = None) -> None:
        self.demo_mode = settings.DEMO_MODE if demo is None else demo
        self.model_path = model_path or settings.MODEL_PATH
        self.model = None
        if not self.demo_mode:
            self._load_model()

    def _load_model(self) -> None:
        if not self.model_path:
            raise RuntimeError(
                "MODEL_PATH is not configured but DEMO_MODE=false. "
                "Provide a trained YOLO model or enable DEMO_MODE."
            )
        try:
            from ultralytics import YOLO  # optional dependency
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError(
                "ultralytics is not installed. Install it or use DEMO_MODE=true."
            ) from exc
        self.model = YOLO(self.model_path)

    def _demo_detections(self, image_bytes: bytes, size: tuple[int, int]) -> list[dict]:
        """Deterministic mock detections derived from the image content."""
        seed = int(hashlib.sha256(image_bytes[:4096]).hexdigest()[:8], 16)
        rng = __import__("random").Random(seed)
        width, height = size
        n = rng.choice([0, 1, 1, 2, 2, 3])
        if n == 0:
            return []
        detections = []
        for _ in range(n):
            bw = int(width * rng.uniform(0.12, 0.4))
            bh = int(height * rng.uniform(0.1, 0.35))
            x1 = rng.randint(0, max(1, width - bw))
            y1 = rng.randint(0, max(1, height - bh))
            detections.append(
                {
                    "class": "pothole",
                    "confidence": round(rng.uniform(0.72, 0.98), 3),
                    "bbox": [x1, y1, x1 + bw, y1 + bh],
                }
            )
        return detections

    def detect(self, image_bytes: bytes, image_size: tuple[int, int]) -> dict:
        if self.demo_mode:
            detections = self._demo_detections(image_bytes, image_size)
            return {
                "demo": True,
                "model_name": "demo-pothole-detector",
                "model_version": "demo-v1",
                "detected": len(detections) > 0,
                "detections": detections,
            }

        result = self.model.predict(image_bytes, verbose=False)
        detections = []
        for r in result:
            if r.boxes is None:
                continue
            for cls_id, conf, box in zip(r.boxes.cls.tolist(), r.boxes.conf.tolist(), r.boxes.xyxy.tolist()):
                detections.append(
                    {
                        "class": r.names[int(cls_id)],
                        "confidence": round(float(conf), 3),
                        "bbox": [round(v, 1) for v in box],
                    }
                )
        return {
            "demo": False,
            "model_name": "yolo-pothole",
            "model_version": self.model_path,
            "detected": len(detections) > 0,
            "detections": detections,
        }
