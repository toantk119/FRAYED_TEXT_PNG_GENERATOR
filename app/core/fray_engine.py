"""Procedural Fray / Fringe Engine for textile patch raw edges."""
import cv2
import numpy as np
from typing import Tuple, List
from app.models.render_config import FrayConfig

class FrayEngine:
    def __init__(self, scale: int = 2):
        self.scale = scale

    def generate_fray_layer(
        self, outer_mask: np.ndarray, config: FrayConfig
    ) -> np.ndarray:
        """
        Generates an RGBA image layer containing procedural frayed fibers around outer_mask.
        Returns:
            fray_rgba: np.ndarray (H, W, 4, uint8)
        """
        h, w = outer_mask.shape[:2]
        fray_rgba = np.zeros((h, w, 4), dtype=np.uint8)

        if not config.fray_enabled or config.fray_density <= 0 or config.fray_length <= 0:
            return fray_rgba

        rng = np.random.default_rng(config.random_seed)

        # 1. Compute outward normal field via Distance Transform gradient
        dist_ext = cv2.distanceTransform(255 - outer_mask, cv2.DIST_L2, 5)
        gx = cv2.Sobel(dist_ext, cv2.CV_32F, 1, 0, ksize=3)
        gy = cv2.Sobel(dist_ext, cv2.CV_32F, 0, 1, ksize=3)
        mag = np.sqrt(gx**2 + gy**2)
        mag[mag == 0] = 1.0
        nx_map = gx / mag
        ny_map = gy / mag

        # 2. Extract all contours (outer boundary and inner holes)
        contours, hierarchy = cv2.findContours(
            outer_mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE
        )
        if not contours or hierarchy is None:
            return fray_rgba

        all_boundary_pts = []
        for cnt in contours:
            pts = cnt.reshape(-1, 2)
            if len(pts) >= 4:
                all_boundary_pts.append(pts)

        if not all_boundary_pts:
            return fray_rgba

        scaled_base_len = config.fray_length * self.scale
        scaled_len_var = config.fray_length_variance * self.scale
        scaled_thickness = max(1, int(round(config.fray_thickness * self.scale)))
        base_rgb = np.array(config.get_rgb(), dtype=float)

        fiber_img = np.zeros((h, w, 4), dtype=np.uint8)

        # Multi-pass fiber generation for authentic plush chenille/frayed textile border:
        # Pass 1: Dense plush undercoat (short, highly dense, wide angle spread)
        # Pass 2: Mid-body fiber coat (standard length, dense)
        # Pass 3: Outer fringe fibers (longer, natural spread)
        # Pass 4: Stray whisker threads (long, accentuating frayed edge)
        passes = [
            {"len_mult": 0.38, "density_mult": 2.2, "var_angle": 55.0, "thick": scaled_thickness + 1, "alpha": 0.95},
            {"len_mult": 0.72, "density_mult": 1.6, "var_angle": 40.0, "thick": scaled_thickness, "alpha": 0.92},
            {"len_mult": 1.05, "density_mult": 1.1, "var_angle": 32.0, "thick": scaled_thickness, "alpha": 0.88},
            {"len_mult": 1.40, "density_mult": 0.4, "var_angle": 25.0, "thick": max(1, scaled_thickness - 1), "alpha": 0.80},
        ]

        for p in passes:
            p_density = config.fray_density * p["density_mult"]
            max_angle_rad = np.radians(p["var_angle"])
            
            for pts in all_boundary_pts:
                n_pts = len(pts)
                sample_count = int(round(n_pts * p_density * 0.85))
                if sample_count <= 0:
                    continue
                
                indices = np.linspace(0, n_pts - 1, sample_count, dtype=int)
                jitter = rng.integers(-1, 2, size=len(indices))
                indices = np.clip(indices + jitter, 0, n_pts - 1)

                for idx in indices:
                    x0, y0 = pts[idx]
                    
                    nx = nx_map[y0, x0]
                    ny = ny_map[y0, x0]
                    
                    base_angle = np.arctan2(ny, nx)
                    angle = base_angle + rng.uniform(-max_angle_rad, max_angle_rad)
                    
                    f_len = (scaled_base_len * p["len_mult"] + 
                             rng.uniform(-scaled_len_var * 0.4, scaled_len_var * 0.4))
                    f_len = max(3.0 * self.scale, f_len)

                    # 3-point curved fiber
                    mid_frac = rng.uniform(0.45, 0.55)
                    mid_angle = angle + rng.uniform(-np.radians(10.0), np.radians(10.0))
                    x1 = x0 + f_len * mid_frac * np.cos(mid_angle)
                    y1 = y0 + f_len * mid_frac * np.sin(mid_angle)

                    tip_angle = mid_angle + rng.uniform(-np.radians(12.0), np.radians(12.0))
                    x2 = x1 + f_len * (1.0 - mid_frac) * np.cos(tip_angle)
                    y2 = y1 + f_len * (1.0 - mid_frac) * np.sin(tip_angle)

                    fiber_poly = np.array([[x0, y0], [x1, y1], [x2, y2]], dtype=np.int32)

                    color_jitter = rng.uniform(-10.0, 5.0)
                    fiber_rgb = np.clip(base_rgb + color_jitter, 0, 255).astype(int)
                    alpha_val = int(round(255 * config.fray_opacity * p["alpha"] * rng.uniform(0.85, 1.0)))
                    color_rgba = (int(fiber_rgb[0]), int(fiber_rgb[1]), int(fiber_rgb[2]), alpha_val)

                    cv2.polylines(
                        fiber_img,
                        [fiber_poly],
                        isClosed=False,
                        color=color_rgba,
                        thickness=p["thick"],
                        lineType=cv2.LINE_AA,
                    )

        # Clear any fibers accidentally inside outer_mask
        inside_mask = (outer_mask > 0)
        fiber_img[inside_mask] = 0

        return fiber_img
