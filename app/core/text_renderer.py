"""Text rendering and base mask generation module with dual-tier support."""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from typing import Tuple, Optional, List
from app.models.render_config import TextConfig, SubTextConfig

class TextRenderer:
    def __init__(self, scale: int = 2):
        self.scale = scale

    def _measure_text_glyphs(self, text: str, font: ImageFont.FreeTypeFont, letter_spacing: int):
        chars = list(text)
        char_widths = []
        char_bboxes = []
        for ch in chars:
            bbox = font.getbbox(ch)
            char_bboxes.append(bbox)
            w = bbox[2] - bbox[0] if bbox else 0
            char_widths.append(max(w, int(font.size * 0.25)))
        total_width = sum(char_widths) + letter_spacing * max(0, len(chars) - 1)
        ascent, descent = font.getmetrics()
        return chars, char_widths, char_bboxes, total_width, ascent, descent

    def _draw_glyphs(
        self,
        draw: ImageDraw.ImageDraw,
        chars: List[str],
        char_widths: List[int],
        char_bboxes: list,
        font: ImageFont.FreeTypeFont,
        start_x: int,
        baseline_y: int,
        letter_spacing: int
    ):
        ascent = font.getmetrics()[0]
        cursor_x = start_x
        for i, ch in enumerate(chars):
            bbox = char_bboxes[i]
            draw.text((cursor_x - bbox[0], baseline_y - ascent), ch, font=font, fill=255)
            cursor_x += char_widths[i] + letter_spacing

    def render_mask(
        self,
        config: TextConfig,
        padding: int = 60,
        subtext_config: Optional[SubTextConfig] = None
    ) -> Tuple[np.ndarray, Tuple[int, int, int, int], Optional[np.ndarray]]:
        """
        Renders the primary text (and optional secondary subtext tier) to an 8-bit alpha mask.
        Returns:
            combined_mask: np.ndarray (uint8, shape (H, W), values 0-255)
            bbox: (min_x, min_y, max_x, max_y) bounding box of the non-zero pixels
            subtext_mask: np.ndarray or None (subtext layer mask for individual color shading)
        """
        effective_text = (
            config.get_effective_text()
            if hasattr(config, "get_effective_text")
            else (config.text.upper() if getattr(config, "uppercase", False) else config.text)
        )
        if not effective_text or not effective_text.strip():
            raise ValueError("Text cannot be empty.")
        if not os.path.exists(config.font_path):
            raise FileNotFoundError(f"Font file not found: {config.font_path}")

        scaled_font_size = int(config.font_size * self.scale)
        scaled_letter_spacing = int(config.letter_spacing * self.scale)
        scaled_padding = int(padding * self.scale)

        font1 = ImageFont.truetype(config.font_path, scaled_font_size)
        chars1, widths1, bboxes1, total_w1, ascent1, descent1 = self._measure_text_glyphs(
            effective_text, font1, scaled_letter_spacing
        )

        has_subtext = (
            subtext_config is not None
            and subtext_config.enabled
            and bool(subtext_config.text and subtext_config.text.strip())
        )

        if not has_subtext:
            # Single-tier rendering
            canvas_w = total_w1 + scaled_padding * 2 + int(scaled_font_size * 0.5)
            canvas_h = (ascent1 + descent1) + scaled_padding * 2 + int(scaled_font_size * 0.5)

            img = Image.new("L", (canvas_w, canvas_h), color=0)
            draw = ImageDraw.Draw(img)
            self._draw_glyphs(
                draw, chars1, widths1, bboxes1, font1,
                start_x=scaled_padding,
                baseline_y=scaled_padding + ascent1,
                letter_spacing=scaled_letter_spacing
            )

            mask = np.array(img, dtype=np.uint8)
            non_zeros = np.argwhere(mask > 0)
            if len(non_zeros) == 0:
                raise ValueError("Rendered text mask is completely empty.")
            min_y, min_x = non_zeros.min(axis=0)
            max_y, max_x = non_zeros.max(axis=0)

            return mask, (min_x, min_y, max_x, max_y), None

        # Dual-tier rendering
        sub_font_path = (
            subtext_config.font_path
            if subtext_config.font_path and os.path.exists(subtext_config.font_path)
            else config.font_path
        )
        sub_font_size = max(12, int(config.font_size * subtext_config.scale_ratio))
        scaled_sub_font_size = int(sub_font_size * self.scale)
        scaled_sub_letter_spacing = int(subtext_config.letter_spacing * self.scale)
        font2 = ImageFont.truetype(sub_font_path, scaled_sub_font_size)

        effective_subtext = subtext_config.get_effective_text()
        chars2, widths2, bboxes2, total_w2, ascent2, descent2 = self._measure_text_glyphs(
            effective_subtext, font2, scaled_sub_letter_spacing
        )

        # Alignment calculation
        scaled_offset_x = int(subtext_config.offset_x * self.scale)
        scaled_offset_y = int(subtext_config.offset_y * self.scale)
        align = (subtext_config.alignment or "right").lower().strip()

        if align == "left":
            rel_x2 = scaled_offset_x
        elif align == "center":
            rel_x2 = (total_w1 - total_w2) // 2 + scaled_offset_x
        else:  # right
            rel_x2 = (total_w1 - total_w2) + scaled_offset_x

        min_rel_x = min(0, rel_x2)
        max_rel_x = max(total_w1, rel_x2 + total_w2)
        cluster_w = max_rel_x - min_rel_x

        draw_x1 = scaled_padding - min_rel_x
        draw_x2 = scaled_padding + rel_x2 - min_rel_x

        baseline1_y = scaled_padding + ascent1
        baseline2_y = baseline1_y + descent1 + ascent2 + scaled_offset_y

        canvas_w = cluster_w + scaled_padding * 2 + int(scaled_font_size * 0.5)
        canvas_h = baseline2_y + descent2 + scaled_padding * 2 + int(scaled_font_size * 0.5)

        img1 = Image.new("L", (canvas_w, canvas_h), color=0)
        self._draw_glyphs(
            ImageDraw.Draw(img1), chars1, widths1, bboxes1, font1,
            start_x=draw_x1, baseline_y=baseline1_y, letter_spacing=scaled_letter_spacing
        )

        img2 = Image.new("L", (canvas_w, canvas_h), color=0)
        self._draw_glyphs(
            ImageDraw.Draw(img2), chars2, widths2, bboxes2, font2,
            start_x=draw_x2, baseline_y=baseline2_y, letter_spacing=scaled_sub_letter_spacing
        )

        mask1 = np.array(img1, dtype=np.uint8)
        mask2 = np.array(img2, dtype=np.uint8)
        combined_mask = np.maximum(mask1, mask2)

        non_zeros = np.argwhere(combined_mask > 0)
        if len(non_zeros) == 0:
            raise ValueError("Rendered combined text mask is completely empty.")
        min_y, min_x = non_zeros.min(axis=0)
        max_y, max_x = non_zeros.max(axis=0)

        return combined_mask, (min_x, min_y, max_x, max_y), mask2
