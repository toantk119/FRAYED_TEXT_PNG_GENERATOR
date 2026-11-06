"""Stroke expansion engine for inner and outer strokes."""
import cv2
import numpy as np
from typing import Tuple
from app.models.render_config import StrokeConfig

class StrokeEngine:
    def __init__(self, scale: int = 2):
        self.scale = scale

    def generate_strokes(
        self, base_mask: np.ndarray, config: StrokeConfig
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Expands base_mask to generate inner and outer stroke masks.
        Returns:
            inner_mask: Full region including text + inner stroke (uint8, 0/255)
            outer_mask: Full region including text + inner + outer stroke (uint8, 0/255)
            outer_stroke_band: Only the outer stroke area (uint8, 0/255)
        """
        # Binarize base mask
        _, binary_base = cv2.threshold(base_mask, 127, 255, cv2.THRESH_BINARY)

        # 1. Inner Stroke
        scaled_inner_r = int(round(config.inner_width * self.scale))
        if config.inner_enabled and scaled_inner_r > 0:
            kernel_inner = cv2.getStructuringElement(
                cv2.MORPH_ELLIPSE, (scaled_inner_r * 2 + 1, scaled_inner_r * 2 + 1)
            )
            inner_mask = cv2.dilate(binary_base, kernel_inner)
        else:
            inner_mask = binary_base.copy()

        # 2. Outer Stroke
        scaled_outer_r = int(round(config.outer_width * self.scale))
        if config.outer_enabled and scaled_outer_r > 0:
            total_r = scaled_inner_r + scaled_outer_r
            kernel_outer = cv2.getStructuringElement(
                cv2.MORPH_ELLIPSE, (total_r * 2 + 1, total_r * 2 + 1)
            )
            outer_mask = cv2.dilate(binary_base, kernel_outer)
        else:
            outer_mask = inner_mask.copy()

        # Outer stroke band: pixels in outer_mask but not in inner_mask
        outer_stroke_band = cv2.subtract(outer_mask, inner_mask)

        return inner_mask, outer_mask, outer_stroke_band
