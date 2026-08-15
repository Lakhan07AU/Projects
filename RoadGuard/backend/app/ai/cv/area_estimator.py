"""Physical area estimation from an RGB image.

IMPORTANT: A normal RGB image cannot reliably determine exact real-world
dimensions without calibration or depth information. This module returns an
*estimated* area and clearly labels it as such.
"""
from __future__ import annotations

import math


class AreaEstimator:
    def __init__(self, pixels_per_metre: float = 30.0, confidence: float = 0.72) -> None:
        # Demo default: assume ~30 px per metre. Configurable later via camera
        # calibration / depth estimation.
        self.pixels_per_metre = pixels_per_metre
        self.base_confidence = confidence

    def estimate(self, pixel_area: float, confidence: float) -> dict:
        if pixel_area <= 0:
            return {
                "estimated_area_m2": 0.0,
                "confidence": 0.0,
                "label": "Estimated Area",
                "note": "RGB images cannot reliably determine exact dimensions without calibration.",
            }
        px_per_m2 = self.pixels_per_metre**2
        area_m2 = pixel_area / px_per_m2
        # Lower confidence when the estimate is large (more error surface).
        eff_conf = max(0.35, self.base_confidence - min(0.2, area_m2 / 100.0))
        return {
            "estimated_area_m2": round(area_m2, 2),
            "confidence": round(eff_conf, 2),
            "label": "Estimated Area",
            "note": "Estimated, not exact. Calibration/depth input improves accuracy.",
        }


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in kilometres between two coordinates."""
    r = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))
