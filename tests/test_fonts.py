"""Automated Test Suite for PSD-Style Font Manager and Font Picker Dialog (AC-19 to AC-22)."""
import os
import sys
import unittest

os.environ["QT_QPA_PLATFORM"] = "offscreen"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication
app = QApplication.instance() or QApplication(sys.argv)

from app.core.font_manager import FontManager, FontVariant, FontFamily
from app.ui.font_picker_dialog import FontPickerDialog
from app.ui.controls_panel import ControlsPanel

class TestFontSystem(unittest.TestCase):
    def setUp(self):
        self.mgr = FontManager.get_instance()

    def test_ac19_font_manager_scan_and_parse(self):
        """AC-19: FontManager scans Windows fonts and parses Family/Style correctly."""
        families = self.mgr.get_sorted_families()
        self.assertGreater(len(families), 5, "Must discover system font families")

        # Test regex parser
        family, style = self.mgr._parse_font_name("Arial Bold (TrueType)")
        self.assertEqual(family, "Arial")
        self.assertEqual(style, "Bold")

        family2, style2 = self.mgr._parse_font_name("Zurich XBlk BT Extra Black (TrueType)")
        self.assertEqual(family2, "Zurich XBlk BT")
        self.assertEqual(style2, "Extra Black")

        # Test A-Z sorting
        names = [f.name.lower() for f in families]
        self.assertEqual(names, sorted(names))

    def test_ac20_font_favorites_and_recents(self):
        """AC-20: FontManager tracks Favorites and Recent fonts reliably."""
        test_font = "TestFontFamily"
        if self.mgr.is_favorite(test_font):
            self.mgr.toggle_favorite(test_font)
        
        self.assertFalse(self.mgr.is_favorite(test_font))
        self.mgr.toggle_favorite(test_font)
        self.assertTrue(self.mgr.is_favorite(test_font))
        self.mgr.toggle_favorite(test_font)
        self.assertFalse(self.mgr.is_favorite(test_font))

        # Recent fonts
        dummy_path = "C:/Windows/Fonts/arialbd.ttf"
        self.mgr.add_recent(dummy_path)
        self.assertIn(os.path.normpath(dummy_path), self.mgr.recent_paths)

    def test_ac21_font_picker_dialog_ui_and_search(self):
        """AC-21: FontPickerDialog initializes, populates tree, and filters via search query."""
        dlg = FontPickerDialog(current_font_path="C:/Windows/Fonts/arialbd.ttf", sample_text="TEST")
        self.assertGreater(dlg.tree.topLevelItemCount(), 5)

        # Filter by search
        dlg.edit_search.setText("Arial")
        # Check that Arial item is visible
        arial_found = False
        for i in range(dlg.tree.topLevelItemCount()):
            item = dlg.tree.topLevelItem(i)
            if not item.isHidden() and "arial" in (item.data(0, 0x0100 + 1) or "").lower():
                arial_found = True
                break
        self.assertTrue(arial_found, "Arial must be visible when searching 'Arial'")

        # Clear search
        dlg.edit_search.setText("")

    def test_ac22_controls_panel_font_selection(self):
        """AC-22: ControlsPanel properly applies PSD font selections to render config."""
        controls = ControlsPanel()
        impact_path = "C:/Windows/Fonts/impact.ttf"
        if os.path.exists(impact_path):
            controls._set_font("Impact", impact_path)
            cfg = controls.get_render_config()
            self.assertEqual(cfg.text.font_path, impact_path)

        # Secondary tier font
        arial_path = "C:/Windows/Fonts/arialbd.ttf"
        controls.grp_subtext.setChecked(True)
        controls.chk_custom_sub_font.setChecked(True)
        controls._set_sub_font("Arial Bold", arial_path)
        cfg2 = controls.get_render_config()
        self.assertEqual(cfg2.subtext.font_path, arial_path)

if __name__ == "__main__":
    unittest.main()
