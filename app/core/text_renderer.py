"""Text rendering and base mask generation module."""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from typing import Tuple
from app.models.render_config import TextConfig

class TextRenderer:
    def __init__(self, scale: int = 2):
        self.scale = scale

    def render_mask(self, config: TextConfig, padding: int = 60) -> Tuple[np.ndarray, Tuple[int, int, int, int]]:
        """
        Renders the text to an 8-bit alpha mask at (scale x resolution).
        Returns:
            mask: np.ndarray (uint8, shape (H, W), values 0-255)
            bbox: (min_x, min_y, max_x, max_y) bounding box of the non-zero pixels
        """
        effective_text = config.get_effective_text() if hasattr(config, "get_effective_text") else (config.text.upper() if getattr(config, "uppercase", False) else config.text)
        if not effective_text or not effective_text.strip():
            raise ValueError("Text cannot be empty.")
        if not os.path.exists(config.font_path):
            raise FileNotFoundError(f"Font file not found: {config.font_path}")

        scaled_font_size = int(config.font_size * self.scale)
        scaled_letter_spacing = int(config.letter_spacing * self.scale)
        scaled_padding = int(padding * self.scale)

        font = ImageFont.truetype(config.font_path, scaled_font_size)

        # Measure dimensions
        # Measure individual glyphs to support letter spacing accurately
        chars = list(effective_text)
        char_widths = []
        char_bboxes = []
        for ch in chars:
            bbox = font.getbbox(ch)
            char_bboxes.append(bbox)
            # Advance width can be estimated from bbox right
            w = bbox[2] - bbox[0] if bbox else 0
            char_widths.append(max(w, int(scaled_font_size * 0.25)))

        total_width = sum(char_widths) + scaled_letter_spacing * (len(chars) - 1)
        # Font metrics for height
        ascent, descent = font.getmetrics()
        line_height = ascent + descent
        
        canvas_w = total_width + scaled_padding * 2 + int(scaled_font_size * 0.5)
        canvas_h = line_height + scaled_padding * 2 + int(scaled_font_size * 0.5)

        img = Image.new("L", (canvas_w, canvas_h), color=0)
        draw = ImageDraw.Draw(img)

        # Draw characters with letter spacing
        cursor_x = scaled_padding
        baseline_y = scaled_padding + ascent

        for i, ch in enumerate(chars):
            bbox = char_bboxes[i]
            # Draw at (cursor_x, baseline_y - ascent)
            draw.text((cursor_x - bbox[0], baseline_y - ascent), ch, font=font, fill=255)
            cursor_x += char_widths[i] + scaled_letter_spacing

        mask = np.array(img, dtype=np.uint8)

        # Find tight bounding box
        non_zeros = np.argwhere(mask > 0)
        if len(non_zeros) == 0:
            raise ValueError("Rendered text mask is completely empty.")
        min_y, min_x = non_zeros.min(axis=0)
        max_y, max_x = non_zeros.max(axis=0)

        return mask, (min_x, min_y, max_x, max_y)
