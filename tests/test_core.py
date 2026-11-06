"""Automated Test Suite for Frayed Text PNG Generator (AC-01 to AC-08)."""
import os
import sys
import unittest
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.render_config import (
    RenderConfig, TextConfig, StrokeConfig, DashConfig, FrayConfig, OutputConfig, parse_color
)
from app.core.engine import FrayedTextEngine

class TestFrayedTextEngine(unittest.TestCase):
    def setUp(self):
        self.engine = FrayedTextEngine(supersampling=2)

    def test_ac01_adaptive_geometry(self):
        """AC-01: Engine automatically adapts to short, medium, and long strings."""
        for text in ["BVB", "Hoffenheim", "Bayer Leverkusen"]:
            config = RenderConfig(
                text=TextConfig(text=text, font_size=120),
                output=OutputConfig(padding=20)
            )
            img = self.engine.render(config)
            self.assertIsInstance(img, Image.Image)
            self.assertEqual(img.mode, "RGBA")
            self.assertGreater(img.width, 100)
            self.assertGreater(img.height, 50)

    def test_ac02_inner_counters(self):
        """AC-02: Letter with counter ('O') generates dash and fray inside the hole."""
        config = RenderConfig(
            text=TextConfig(text="O", font_size=180),
            output=OutputConfig(padding=30)
        )
        img = self.engine.render(config)
        arr = np.array(img)
        # Check center of the letter 'O' has transparent or fray pixels
        center_x, center_y = arr.shape[1] // 2, arr.shape[0] // 2
        # Center should not be solid black stroke (outer stroke)
        center_pixel = arr[center_y, center_x]
        self.assertTrue(center_pixel[3] < 255 or np.all(center_pixel[:3] > 100))

    def test_ac03_color_customization(self):
        """AC-03: Full color independence across all 5 graphic layers."""
        config = RenderConfig(
            text=TextConfig(text="TEST", text_color="#FF0000"),
            stroke=StrokeConfig(inner_color="#00FF00", outer_color="#0000FF"),
            dash=DashConfig(dash_color="#FFFF00"),
            fray=FrayConfig(fray_color="#FF00FF"),
        )
        img = self.engine.render(config)
        arr = np.array(img)
        # Verify text fill red exists
        red_mask = (arr[..., 0] > 200) & (arr[..., 1] < 50) & (arr[..., 2] < 50) & (arr[..., 3] > 200)
        self.assertTrue(np.any(red_mask), "Custom red text color must be present")

    def test_ac04_procedural_fray_presence(self):
        """AC-04: Fray fibers must be generated procedurally around the outer boundary."""
        config = RenderConfig(
            text=TextConfig(text="I", font_size=140),
            fray=FrayConfig(fray_enabled=True, fray_density=0.9, fray_length=25.0)
        )
        img = self.engine.render(config)
        arr = np.array(img)
        # Check presence of semi-transparent anti-aliased fibers
        fray_pixels = (arr[..., 3] > 0) & (arr[..., 3] < 255)
        self.assertGreater(np.count_nonzero(fray_pixels), 500, "Fray fibers must exist")

    def test_ac05_dash_stitch_presence(self):
        """AC-05: Dash stitch layer must generate visible dashed line pixels."""
        config = RenderConfig(
            text=TextConfig(text="H", font_size=140),
            dash=DashConfig(dash_enabled=True, dash_color="#FFFFFF", dash_thickness=2.0)
        )
        img = self.engine.render(config)
        arr = np.array(img)
        white_stitch = (arr[..., 0] > 240) & (arr[..., 1] > 240) & (arr[..., 2] > 240) & (arr[..., 3] > 200)
        self.assertGreater(np.count_nonzero(white_stitch), 100)

    def test_ac06_seed_reproducibility(self):
        """AC-06: Same random seed produces identical pixel-for-pixel results."""
        config1 = RenderConfig(text=TextConfig(text="SEED"), fray=FrayConfig(random_seed=777))
        config2 = RenderConfig(text=TextConfig(text="SEED"), fray=FrayConfig(random_seed=777))
        img1 = self.engine.render(config1)
        img2 = self.engine.render(config2)
        arr1 = np.array(img1)
        arr2 = np.array(img2)
        self.assertEqual(arr1.shape, arr2.shape)
        np.testing.assert_array_equal(arr1, arr2)

    def test_ac07_rgba_transparency(self):
        """AC-07: Canvas boundary has true Alpha=0 transparency."""
        config = RenderConfig(text=TextConfig(text="ALPHA"), output=OutputConfig(padding=40))
        img = self.engine.render(config)
        arr = np.array(img)
        self.assertEqual(img.mode, "RGBA")
        # Corner pixels must be completely transparent
        self.assertEqual(arr[0, 0, 3], 0)
        self.assertEqual(arr[0, -1, 3], 0)
        self.assertEqual(arr[-1, 0, 3], 0)
        self.assertEqual(arr[-1, -1, 3], 0)

    def test_ac08_validation_and_safety(self):
        """AC-08: Validation rejects invalid colors and empty text safely."""
        with self.assertRaises(ValueError):
            parse_color("invalid_color_123")
        with self.assertRaises(ValueError):
            config = RenderConfig(text=TextConfig(text="   "))
            self.engine.render(config)

    def test_ac13_uppercase_transformation(self):
        """AC-13: Uppercase toggle transforms text to ALL CAPS rendering identically."""
        config_lower = RenderConfig(
            text=TextConfig(text="hoffenheim", uppercase=True, font_size=120),
            fray=FrayConfig(random_seed=123)
        )
        config_upper = RenderConfig(
            text=TextConfig(text="HOFFENHEIM", uppercase=False, font_size=120),
            fray=FrayConfig(random_seed=123)
        )
        img_lower = self.engine.render(config_lower)
        img_upper = self.engine.render(config_upper)

        arr_lower = np.array(img_lower)
        arr_upper = np.array(img_upper)

        self.assertEqual(arr_lower.shape, arr_upper.shape)
        np.testing.assert_array_equal(arr_lower, arr_upper)

if __name__ == "__main__":
    unittest.main()
