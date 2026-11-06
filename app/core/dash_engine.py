"""Dashed stitch outline engine using contour arc-length parameterization."""
import cv2
import numpy as np
from typing import List, Tuple
from app.models.render_config import DashConfig, StrokeConfig

class DashEngine:
    def __init__(self, scale: int = 2):
        self.scale = scale

    def generate_dash_mask(
        self,
        inner_mask: np.ndarray,
        outer_mask: np.ndarray,
        dash_config: DashConfig,
        stroke_config: StrokeConfig,
    ) -> np.ndarray:
        """
        Generates an 8-bit mask of the dashed stitch line following both outer and inner contours.
        Returns:
            dash_mask: np.ndarray (uint8, 0/255, same shape as outer_mask)
        """
        h, w = outer_mask.shape[:2]
        dash_mask = np.zeros((h, w), dtype=np.uint8)

        if not dash_config.dash_enabled:
            return dash_mask

        # Determine reference mask for dash placement:
        # Place the stitch roughly at the midline of the outer stroke
        scaled_inner_r = int(round(stroke_config.inner_width * self.scale))
        scaled_outer_r = int(round(stroke_config.outer_width * self.scale))
        
        # Position stitch at ~45% into the outer stroke from inner stroke boundary
        mid_r = scaled_inner_r + int(round(scaled_outer_r * 0.45))
        if mid_r <= 0:
            mid_r = 1

        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (mid_r * 2 + 1, mid_r * 2 + 1))
        # Dilate from the base/inner region to find the stitch path
        # Or erode outer_mask by (scaled_outer_r * 0.55)
        erode_amount = max(1, int(round(scaled_outer_r * 0.52)))
        kernel_erode = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (erode_amount * 2 + 1, erode_amount * 2 + 1))
        stitch_region = cv2.erode(outer_mask, kernel_erode)

        # Extract contours (both outer and inner holes)
        contours, hierarchy = cv2.findContours(
            stitch_region, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE
        )

        if not contours or hierarchy is None:
            return dash_mask

        scaled_dash_len = dash_config.dash_length * self.scale
        scaled_gap_len = dash_config.dash_gap * self.scale
        scaled_thickness = max(1, int(round(dash_config.dash_thickness * self.scale)))
        cycle_len = scaled_dash_len + scaled_gap_len
        
        if cycle_len <= 0:
            return dash_mask

        for cnt in contours:
            # Squeeze to (N, 2)
            pts = cnt.reshape(-1, 2)
            if len(pts) < 4:
                continue

            # Compute cumulative perimeter
            # Add the first point at end to close contour
            closed_pts = np.vstack([pts, pts[0:1]])
            diffs = np.diff(closed_pts, axis=0)
            seg_lengths = np.sqrt((diffs ** 2).sum(axis=1))
            total_len = seg_lengths.sum()

            if total_len < cycle_len:
                continue

            cum_dist = np.concatenate([[0.0], np.cumsum(seg_lengths)])

            # Generate dashes along arc length
            offset = (dash_config.dash_offset * self.scale) % cycle_len
            cur_s = offset
            
            while cur_s < total_len:
                d_start = cur_s
                d_end = min(cur_s + scaled_dash_len, total_len)

                # Extract sub-polyline between d_start and d_end
                dash_sub_pts = self._interpolate_segment(closed_pts, cum_dist, d_start, d_end)
                if len(dash_sub_pts) >= 2:
                    cv2.polylines(
                        dash_mask,
                        [np.int32(dash_sub_pts)],
                        isClosed=False,
                        color=255,
                        thickness=scaled_thickness,
                        lineType=cv2.LINE_AA,
                    )
                cur_s += cycle_len

        return dash_mask

    def _interpolate_segment(
        self, pts: np.ndarray, cum_dist: np.ndarray, s_start: float, s_end: float
    ) -> List[np.ndarray]:
        """Interpolates polyline points between arc-length s_start and s_end."""
        # Find indices
        i_start = np.searchsorted(cum_dist, s_start, side='right') - 1
        i_start = max(0, min(i_start, len(pts) - 2))

        i_end = np.searchsorted(cum_dist, s_end, side='left')
        i_end = max(0, min(i_end, len(pts) - 1))

        # Start point interpolation
        denom_start = cum_dist[i_start + 1] - cum_dist[i_start]
        if denom_start > 1e-6:
            t_s = (s_start - cum_dist[i_start]) / denom_start
            p_s = pts[i_start] + t_s * (pts[i_start + 1] - pts[i_start])
        else:
            p_s = pts[i_start].astype(float)

        # End point interpolation
        denom_end = cum_dist[i_end] - cum_dist[i_end - 1] if i_end > 0 else 1.0
        if denom_end > 1e-6 and i_end > 0:
            t_e = (s_end - cum_dist[i_end - 1]) / denom_end
            p_e = pts[i_end - 1] + t_e * (pts[i_end] - pts[i_end - 1])
        else:
            p_e = pts[i_end].astype(float)

        # Intermediate points
        sub_pts = [p_s]
        for idx in range(i_start + 1, i_end):
            sub_pts.append(pts[idx].astype(float))
        sub_pts.append(p_e)

        return sub_pts
