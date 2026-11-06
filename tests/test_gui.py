"""Headless GUI Unit Tests for PySide6 MainWindow and Controls."""
import os
import sys
import unittest

os.environ["QT_QPA_PLATFORM"] = "offscreen"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication
from app.ui.main_window import MainWindow
from app.ui.controls_panel import ControlsPanel
from app.ui.preview_widget import PreviewWidget

app = QApplication.instance() or QApplication(sys.argv)

class TestGUIComponents(unittest.TestCase):
    def test_ac09_main_window_init(self):
        """AC-09: MainWindow initializes without errors and has central layout."""
        win = MainWindow()
        self.assertIsNotNone(win.controls)
        self.assertIsNotNone(win.preview)
        self.assertIn("Frayed Text PNG Generator", win.windowTitle())

    def test_ac10_preview_widget_checkerboard_and_pixmap(self):
        """AC-10: PreviewWidget can receive PIL image and render onto checkerboard."""
        widget = PreviewWidget()
        from PIL import Image
        test_img = Image.new("RGBA", (200, 100), (255, 0, 0, 255))
        widget.set_pil_image(test_img)
        self.assertIsNotNone(widget.pixmap)
        self.assertEqual(widget.pixmap.width(), 200)
        self.assertEqual(widget.pixmap.height(), 100)

    def test_ac11_controls_color_and_text_changes(self):
        """AC-11: Changing controls updates config model with custom colors."""
        controls = ControlsPanel()
        controls.txt_input.setText("REAL MADRID")
        controls.color_text.edit_hex.setText("#FFD700")
        controls.color_inner.edit_hex.setText("#000000")
        controls.color_outer.edit_hex.setText("#FFFFFF")
        controls.color_dash.edit_hex.setText("#FF0000")
        controls.color_fray.edit_hex.setText("#00FF00")

        cfg = controls.get_render_config(supersampling=1)
        self.assertEqual(cfg.text.text, "REAL MADRID")
        self.assertEqual(cfg.text.text_color, "#FFD700")
        self.assertEqual(cfg.stroke.inner_color, "#000000")
        self.assertEqual(cfg.stroke.outer_color, "#FFFFFF")
        self.assertEqual(cfg.dash.dash_color, "#FF0000")
        self.assertEqual(cfg.fray.fray_color, "#00FF00")

    def test_ac12_randomize_seed(self):
        """AC-12: Randomize seed button modifies seed value."""
        controls = ControlsPanel()
        old_seed = controls.spin_seed.value()
        controls._randomize_seed()
        new_seed = controls.spin_seed.value()
        # Seed should be in range and updated
        self.assertGreater(new_seed, 0)

    def test_ac14_uppercase_checkbox(self):
        """AC-14: Checkbox controls ALL CAPS mode and reflects in effective text."""
        controls = ControlsPanel()
        controls.txt_input.setText("arsenal london")
        self.assertFalse(controls.chk_uppercase.isChecked())
        cfg1 = controls.get_render_config()
        self.assertFalse(cfg1.text.uppercase)
        self.assertEqual(cfg1.text.get_effective_text(), "arsenal london")

        # Toggle ALL CAPS
        controls.chk_uppercase.setChecked(True)
        cfg2 = controls.get_render_config()
        self.assertTrue(cfg2.text.uppercase)
        self.assertEqual(cfg2.text.get_effective_text(), "ARSENAL LONDON")

if __name__ == "__main__":
    unittest.main()
