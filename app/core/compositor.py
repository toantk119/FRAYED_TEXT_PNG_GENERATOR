"""Compositor module for layering, color assignment, and anti-aliasing."""
import cv2
import numpy as np
from PIL import Image
from typing import Tuple
from app.models.render_config import RenderConfig

class Compositor:
    def __init__(self, scale: int = 2):
        self.scale = scale

    def composite(
        self,
        text_mask: np.ndarray,
        inner_mask: np.ndarray,
        outer_mask: np.ndarray,
        dash_mask: np.ndarray,
        fray_rgba: np.ndarray,
        config: RenderConfig,
        subtext_mask: np.ndarray = None,
    ) -> Image.Image:
        """
        Composites all graphical layers with their respective colors.
        Returns:
            final_img: PIL Image in RGBA mode with transparency.
        """
        h, w = text_mask.shape[:2]

        # Allocate high-res canvas (H, W, 4) in float32 for alpha blending
        canvas_rgba = np.zeros((h, w, 4), dtype=np.float32)

        # 1. Base Layer: Fray Fibers
        if config.fray.fray_enabled and fray_rgba is not None:
            fray_f = fray_rgba.astype(np.float32) / 255.0
            canvas_rgba = self._blend_over(canvas_rgba, fray_f)

        # 2. Outer Stroke Layer
        if config.stroke.outer_enabled and config.stroke.outer_width > 0:
            outer_rgb = np.array(config.stroke.get_outer_rgb(), dtype=np.float32) / 255.0
            outer_layer = np.zeros((h, w, 4), dtype=np.float32)
            mask_idx = (outer_mask > 0)
            outer_layer[mask_idx, :3] = outer_rgb
            outer_layer[mask_idx, 3] = 1.0
            canvas_rgba = self._blend_over(canvas_rgba, outer_layer)

        # 3. Dash Stitch Layer
        if config.dash.dash_enabled and np.any(dash_mask > 0):
            dash_rgb = np.array(config.dash.get_rgb(), dtype=np.float32) / 255.0
            dash_layer = np.zeros((h, w, 4), dtype=np.float32)
            dash_f = (dash_mask.astype(np.float32) / 255.0)
            dash_layer[..., :3] = dash_rgb
            dash_layer[..., 3] = dash_f
            canvas_rgba = self._blend_over(canvas_rgba, dash_layer)

        # 4. Inner Stroke Layer
        if config.stroke.inner_enabled and config.stroke.inner_width > 0:
            inner_rgb = np.array(config.stroke.get_inner_rgb(), dtype=np.float32) / 255.0
            inner_layer = np.zeros((h, w, 4), dtype=np.float32)
            mask_idx = (inner_mask > 0)
            inner_layer[mask_idx, :3] = inner_rgb
            inner_layer[mask_idx, 3] = 1.0
            canvas_rgba = self._blend_over(canvas_rgba, inner_layer)

        # 5. Text Fill Layer (Dual-tier support with independent colors)
        text_rgb = np.array(config.text.get_rgb(), dtype=np.float32) / 255.0
        subtext_cfg = getattr(config, "subtext", None)
        has_sub_color = (
            subtext_mask is not None
            and subtext_cfg is not None
            and subtext_cfg.enabled
            and bool(subtext_cfg.color and subtext_cfg.color.strip())
        )

        if has_sub_color:
            sub_rgb = np.array(subtext_cfg.get_rgb(config.text.text_color), dtype=np.float32) / 255.0
            primary_mask = np.clip(text_mask.astype(np.int32) - subtext_mask.astype(np.int32), 0, 255).astype(np.uint8)

            t1_layer = np.zeros((h, w, 4), dtype=np.float32)
            t1_layer[..., :3] = text_rgb
            t1_layer[..., 3] = (primary_mask.astype(np.float32) / 255.0)
            canvas_rgba = self._blend_over(canvas_rgba, t1_layer)

            t2_layer = np.zeros((h, w, 4), dtype=np.float32)
            t2_layer[..., :3] = sub_rgb
            t2_layer[..., 3] = (subtext_mask.astype(np.float32) / 255.0)
            canvas_rgba = self._blend_over(canvas_rgba, t2_layer)
        else:
            text_layer = np.zeros((h, w, 4), dtype=np.float32)
            text_f = (text_mask.astype(np.float32) / 255.0)
            text_layer[..., :3] = text_rgb
            text_layer[..., 3] = text_f
            canvas_rgba = self._blend_over(canvas_rgba, text_layer)

        # Convert back to uint8
        result_uint8 = np.clip(canvas_rgba * 255.0, 0, 255).astype(np.uint8)

        # Find visible bounding box to crop tightly with configured padding
        alpha = result_uint8[..., 3]
        non_zeros = np.argwhere(alpha > 0)
        if len(non_zeros) == 0:
            return Image.fromarray(result_uint8, mode="RGBA")

        min_y, min_x = non_zeros.min(axis=0)
        max_y, max_x = non_zeros.max(axis=0)

        scaled_pad = int(config.output.padding * self.scale)
        crop_min_x = max(0, min_x - scaled_pad)
        crop_min_y = max(0, min_y - scaled_pad)
        crop_max_x = min(w, max_x + scaled_pad + 1)
        crop_max_y = min(h, max_y + scaled_pad + 1)

        cropped = result_uint8[crop_min_y:crop_max_y, crop_min_x:crop_max_x]
        pil_img = Image.fromarray(cropped, mode="RGBA")

        # Downsample if supersampling scale > 1
        if self.scale > 1:
            target_w = max(1, pil_img.width // self.scale)
            target_h = max(1, pil_img.height // self.scale)
            pil_img = pil_img.resize((target_w, target_h), Image.Resampling.LANCZOS)

        return pil_img

    def _blend_over(self, bg: np.ndarray, fg: np.ndarray) -> np.ndarray:
        """Standard Porter-Duff 'Over' alpha compositing."""
        fg_a = fg[..., 3:4]
        bg_a = bg[..., 3:4]
        out_a = fg_a + bg_a * (1.0 - fg_a)
        
        # Avoid division by zero
        denom = np.where(out_a > 1e-6, out_a, 1.0)
        out_rgb = (fg[..., :3] * fg_a + bg[..., :3] * bg_a * (1.0 - fg_a)) / denom
        
        return np.concatenate([out_rgb, out_a], axis=-1)
