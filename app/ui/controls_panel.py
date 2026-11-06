"""Controls panel widget for configuring typography, strokes, dash, and fray."""
import os
import random
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QSpinBox, QDoubleSpinBox, QSlider, QCheckBox, QComboBox, QFileDialog,
    QColorDialog, QGroupBox, QScrollArea, QFrame
)
from PySide6.QtGui import QColor, QFontDatabase
from PySide6.QtCore import Qt, Signal
from app.models.render_config import (
    RenderConfig, TextConfig, SubTextConfig, StrokeConfig, DashConfig, FrayConfig, OutputConfig
)

class ColorPickerWidget(QWidget):
    """Color picker with swatch button and HEX text field."""
    colorChanged = Signal(str)

    def __init__(self, initial_hex="#FFFFFF", parent=None):
        super().__init__(parent)
        self.hex_value = initial_hex

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self.btn_swatch = QPushButton()
        self.btn_swatch.setFixedSize(30, 26)
        self.btn_swatch.clicked.connect(self._open_dialog)

        self.edit_hex = QLineEdit(initial_hex)
        self.edit_hex.setMaxLength(7)
        self.edit_hex.setFixedWidth(80)
        self.edit_hex.textChanged.connect(self._on_hex_edited)

        layout.addWidget(self.btn_swatch)
        layout.addWidget(self.edit_hex)
        layout.addStretch()

        self._update_swatch(initial_hex)

    def _update_swatch(self, hex_code):
        color = QColor(hex_code)
        if color.isValid():
            self.btn_swatch.setStyleSheet(f"background-color: {hex_code}; border: 1px solid #999; border-radius: 3px;")
            self.hex_value = hex_code

    def _open_dialog(self):
        c = QColorDialog.getColor(QColor(self.hex_value), self, "Select Color")
        if c.isValid():
            hex_str = c.name().upper()
            self.edit_hex.setText(hex_str)
            self._update_swatch(hex_str)
            self.colorChanged.emit(hex_str)

    def _on_hex_edited(self, text):
        text = text.strip()
        if not text.startswith("#"):
            text = "#" + text
        c = QColor(text)
        if c.isValid() and len(text) == 7:
            self._update_swatch(text)
            self.colorChanged.emit(text)

    def get_color(self) -> str:
        return self.hex_value


class ControlsPanel(QWidget):
    configChanged = Signal()
    exportRequested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(360)
        self.setMaximumWidth(420)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        container = QWidget()
        self.layout = QVBoxLayout(container)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(12)

        self._setup_typography_group()
        self._setup_strokes_group()
        self._setup_dash_group()
        self._setup_fray_group()
        self._setup_export_group()

        scroll.setWidget(container)
        main_layout.addWidget(scroll)

    def _setup_typography_group(self):
        grp = QGroupBox("1. Typography")
        l = QVBoxLayout(grp)
        l.setSpacing(6)

        # Text input
        l.addWidget(QLabel("Text:"))
        self.txt_input = QLineEdit("Hoffenheim")
        self.txt_input.textChanged.connect(self._notify_change)
        l.addWidget(self.txt_input)

        # Uppercase (ALL CAPS) Checkbox
        self.chk_uppercase = QCheckBox("ALL CAPS (Viết HOA toàn bộ)")
        self.chk_uppercase.setChecked(False)
        self.chk_uppercase.toggled.connect(self._notify_change)
        l.addWidget(self.chk_uppercase)

        # Font
        l.addWidget(QLabel("Font:"))
        font_row = QHBoxLayout()
        self.combo_font = QComboBox()
        self.combo_font.addItem("Arial Bold", "C:/Windows/Fonts/arialbd.ttf")
        self.combo_font.addItem("Impact", "C:/Windows/Fonts/impact.ttf")
        self.combo_font.addItem("Arial Regular", "C:/Windows/Fonts/arial.ttf")
        self.combo_font.currentIndexChanged.connect(self._notify_change)
        font_row.addWidget(self.combo_font, 1)

        btn_browse = QPushButton("Browse...")
        btn_browse.clicked.connect(self._browse_font)
        font_row.addWidget(btn_browse)
        l.addLayout(font_row)

        # Font size
        l.addWidget(QLabel("Font Size (px):"))
        size_row = QHBoxLayout()
        self.spin_font_size = QSpinBox()
        self.spin_font_size.setRange(20, 500)
        self.spin_font_size.setValue(180)
        self.spin_font_size.valueChanged.connect(self._notify_change)
        size_row.addWidget(self.spin_font_size)
        l.addLayout(size_row)

        # Text color
        l.addWidget(QLabel("Text Color:"))
        self.color_text = ColorPickerWidget("#1961B5")
        self.color_text.colorChanged.connect(self._notify_change)
        l.addWidget(self.color_text)

        # Dual-tier Subtext Group
        self.grp_subtext = QGroupBox("Chữ Tầng 2 (Dual-tier / Sub-text)")
        self.grp_subtext.setCheckable(True)
        self.grp_subtext.setChecked(False)
        self.grp_subtext.toggled.connect(self._notify_change)
        sub_l = QVBoxLayout(self.grp_subtext)
        sub_l.setSpacing(6)

        sub_l.addWidget(QLabel("Text Tầng 2:"))
        self.txt_subtext = QLineEdit("FRANKFURT")
        self.txt_subtext.textChanged.connect(self._notify_change)
        sub_l.addWidget(self.txt_subtext)

        self.chk_sub_uppercase = QCheckBox("ALL CAPS (Viết HOA tầng 2)")
        self.chk_sub_uppercase.setChecked(True)
        self.chk_sub_uppercase.toggled.connect(self._notify_change)
        sub_l.addWidget(self.chk_sub_uppercase)

        # Alignment
        sub_l.addWidget(QLabel("Căn Lề (Alignment):"))
        self.combo_alignment = QComboBox()
        self.combo_alignment.addItem("Lệch Phải (Right)", "right")
        self.combo_alignment.addItem("Chính Giữa (Center)", "center")
        self.combo_alignment.addItem("Lệch Trái (Left)", "left")
        self.combo_alignment.currentIndexChanged.connect(self._notify_change)
        sub_l.addWidget(self.combo_alignment)

        # Size ratio & offsets
        ratio_row = QHBoxLayout()
        v_ratio = QVBoxLayout()
        v_ratio.addWidget(QLabel("Tỉ lệ cỡ chữ:"))
        self.spin_scale_ratio = QDoubleSpinBox()
        self.spin_scale_ratio.setRange(0.15, 1.0)
        self.spin_scale_ratio.setSingleStep(0.05)
        self.spin_scale_ratio.setValue(0.45)
        self.spin_scale_ratio.valueChanged.connect(self._notify_change)
        v_ratio.addWidget(self.spin_scale_ratio)
        ratio_row.addLayout(v_ratio)

        v_offset_y = QVBoxLayout()
        v_offset_y.addWidget(QLabel("Khoảng cách Y:"))
        self.spin_offset_y = QSpinBox()
        self.spin_offset_y.setRange(-80, 80)
        self.spin_offset_y.setValue(-8)
        self.spin_offset_y.setToolTip("Số âm để ăn khớp/tiếp xúc với chân tầng 1")
        self.spin_offset_y.valueChanged.connect(self._notify_change)
        v_offset_y.addWidget(self.spin_offset_y)
        ratio_row.addLayout(v_offset_y)

        v_offset_x = QVBoxLayout()
        v_offset_x.addWidget(QLabel("Lệch ngang X:"))
        self.spin_offset_x = QSpinBox()
        self.spin_offset_x.setRange(-300, 300)
        self.spin_offset_x.setValue(0)
        self.spin_offset_x.valueChanged.connect(self._notify_change)
        v_offset_x.addWidget(self.spin_offset_x)
        ratio_row.addLayout(v_offset_x)

        sub_l.addLayout(ratio_row)

        # Color
        self.chk_custom_sub_color = QCheckBox("Dùng màu riêng cho tầng 2")
        self.chk_custom_sub_color.setChecked(False)
        self.chk_custom_sub_color.toggled.connect(self._toggle_sub_color)
        sub_l.addWidget(self.chk_custom_sub_color)

        self.color_subtext = ColorPickerWidget("#1961B5")
        self.color_subtext.setEnabled(False)
        self.color_subtext.colorChanged.connect(self._notify_change)
        sub_l.addWidget(self.color_subtext)

        l.addWidget(self.grp_subtext)

        self.layout.addWidget(grp)

    def _setup_strokes_group(self):
        grp = QGroupBox("2. Strokes")
        l = QVBoxLayout(grp)
        l.setSpacing(6)

        # Inner stroke
        l.addWidget(QLabel("Inner Stroke Color:"))
        self.color_inner = ColorPickerWidget("#FFFFFF")
        self.color_inner.colorChanged.connect(self._notify_change)
        l.addWidget(self.color_inner)

        l.addWidget(QLabel("Inner Stroke Width (px):"))
        self.spin_inner_w = QSpinBox()
        self.spin_inner_w.setRange(0, 30)
        self.spin_inner_w.setValue(3)
        self.spin_inner_w.valueChanged.connect(self._notify_change)
        l.addWidget(self.spin_inner_w)

        # Outer stroke
        l.addWidget(QLabel("Outer Stroke Color:"))
        self.color_outer = ColorPickerWidget("#000000")
        self.color_outer.colorChanged.connect(self._notify_change)
        l.addWidget(self.color_outer)

        l.addWidget(QLabel("Outer Stroke Width (px):"))
        self.spin_outer_w = QSpinBox()
        self.spin_outer_w.setRange(0, 50)
        self.spin_outer_w.setValue(15)
        self.spin_outer_w.valueChanged.connect(self._notify_change)
        l.addWidget(self.spin_outer_w)

        self.layout.addWidget(grp)

    def _setup_dash_group(self):
        grp = QGroupBox("3. Dash Stitch")
        l = QVBoxLayout(grp)
        l.setSpacing(6)

        self.chk_dash = QCheckBox("Enable Dash Stitch")
        self.chk_dash.setChecked(True)
        self.chk_dash.toggled.connect(self._notify_change)
        l.addWidget(self.chk_dash)

        l.addWidget(QLabel("Stitch Color:"))
        self.color_dash = ColorPickerWidget("#FFFFFF")
        self.color_dash.colorChanged.connect(self._notify_change)
        l.addWidget(self.color_dash)

        dash_row = QHBoxLayout()
        v1 = QVBoxLayout()
        v1.addWidget(QLabel("Length:"))
        self.spin_dash_len = QDoubleSpinBox()
        self.spin_dash_len.setRange(1.0, 50.0)
        self.spin_dash_len.setValue(11.0)
        self.spin_dash_len.valueChanged.connect(self._notify_change)
        v1.addWidget(self.spin_dash_len)
        dash_row.addLayout(v1)

        v2 = QVBoxLayout()
        v2.addWidget(QLabel("Gap:"))
        self.spin_dash_gap = QDoubleSpinBox()
        self.spin_dash_gap.setRange(1.0, 50.0)
        self.spin_dash_gap.setValue(7.0)
        self.spin_dash_gap.valueChanged.connect(self._notify_change)
        v2.addWidget(self.spin_dash_gap)
        dash_row.addLayout(v2)

        v3 = QVBoxLayout()
        v3.addWidget(QLabel("Thickness:"))
        self.spin_dash_thick = QDoubleSpinBox()
        self.spin_dash_thick.setRange(0.5, 10.0)
        self.spin_dash_thick.setValue(2.2)
        self.spin_dash_thick.valueChanged.connect(self._notify_change)
        v3.addWidget(self.spin_dash_thick)
        dash_row.addLayout(v3)

        l.addLayout(dash_row)
        self.layout.addWidget(grp)

    def _setup_fray_group(self):
        grp = QGroupBox("4. Procedural Fray")
        l = QVBoxLayout(grp)
        l.setSpacing(6)

        self.chk_fray = QCheckBox("Enable Fray")
        self.chk_fray.setChecked(True)
        self.chk_fray.toggled.connect(self._notify_change)
        l.addWidget(self.chk_fray)

        l.addWidget(QLabel("Fray Color:"))
        self.color_fray = ColorPickerWidget("#FFFFFF")
        self.color_fray.colorChanged.connect(self._notify_change)
        l.addWidget(self.color_fray)

        l.addWidget(QLabel("Fray Length (px):"))
        self.spin_fray_len = QDoubleSpinBox()
        self.spin_fray_len.setRange(2.0, 80.0)
        self.spin_fray_len.setValue(24.0)
        self.spin_fray_len.valueChanged.connect(self._notify_change)
        l.addWidget(self.spin_fray_len)

        l.addWidget(QLabel("Fray Density:"))
        self.spin_fray_density = QDoubleSpinBox()
        self.spin_fray_density.setRange(0.1, 1.0)
        self.spin_fray_density.setSingleStep(0.05)
        self.spin_fray_density.setValue(0.95)
        self.spin_fray_density.valueChanged.connect(self._notify_change)
        l.addWidget(self.spin_fray_density)

        # Seed row
        l.addWidget(QLabel("Random Seed:"))
        seed_row = QHBoxLayout()
        self.spin_seed = QSpinBox()
        self.spin_seed.setRange(0, 9999999)
        self.spin_seed.setValue(42)
        self.spin_seed.valueChanged.connect(self._notify_change)
        seed_row.addWidget(self.spin_seed, 1)

        btn_rand_seed = QPushButton("🎲 Randomize")
        btn_rand_seed.clicked.connect(self._randomize_seed)
        seed_row.addWidget(btn_rand_seed)
        l.addLayout(seed_row)

        self.layout.addWidget(grp)

    def _setup_export_group(self):
        btn_export = QPushButton("💾 Export Transparent PNG...")
        btn_export.setFixedHeight(40)
        btn_export.setStyleSheet("font-weight: bold; font-size: 14px; background-color: #2E7D32; color: white; border-radius: 4px;")
        btn_export.clicked.connect(self.exportRequested.emit)
        self.layout.addWidget(btn_export)

    def _browse_font(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Font File", "C:/Windows/Fonts", "Fonts (*.ttf *.otf)")
        if path:
            name = os.path.basename(path)
            self.combo_font.addItem(name, path)
            self.combo_font.setCurrentIndex(self.combo_font.count() - 1)
            self._notify_change()

    def _toggle_sub_color(self, enabled):
        self.color_subtext.setEnabled(enabled)
        self._notify_change()

    def _randomize_seed(self):
        new_seed = random.randint(1, 999999)
        self.spin_seed.setValue(new_seed)

    def _notify_change(self, *args):
        self.configChanged.emit()

    def get_render_config(self, supersampling: int = 1) -> RenderConfig:
        font_path = self.combo_font.currentData()
        if not font_path or not os.path.exists(font_path):
            font_path = "C:/Windows/Fonts/arialbd.ttf"

        return RenderConfig(
            text=TextConfig(
                text=self.txt_input.text() or "Hoffenheim",
                font_path=font_path,
                font_size=self.spin_font_size.value(),
                letter_spacing=2,
                text_color=self.color_text.get_color(),
                uppercase=self.chk_uppercase.isChecked(),
            ),
            subtext=SubTextConfig(
                enabled=self.grp_subtext.isChecked(),
                text=self.txt_subtext.text() or "FRANKFURT",
                scale_ratio=self.spin_scale_ratio.value(),
                alignment=self.combo_alignment.currentData() or "right",
                offset_x=self.spin_offset_x.value(),
                offset_y=self.spin_offset_y.value(),
                uppercase=self.chk_sub_uppercase.isChecked(),
                color=self.color_subtext.get_color() if self.chk_custom_sub_color.isChecked() else "",
            ),
            stroke=StrokeConfig(
                inner_color=self.color_inner.get_color(),
                inner_width=self.spin_inner_w.value(),
                inner_enabled=(self.spin_inner_w.value() > 0),
                outer_color=self.color_outer.get_color(),
                outer_width=self.spin_outer_w.value(),
                outer_enabled=(self.spin_outer_w.value() > 0),
            ),
            dash=DashConfig(
                dash_color=self.color_dash.get_color(),
                dash_length=self.spin_dash_len.value(),
                dash_gap=self.spin_dash_gap.value(),
                dash_thickness=self.spin_dash_thick.value(),
                dash_enabled=self.chk_dash.isChecked(),
            ),
            fray=FrayConfig(
                fray_color=self.color_fray.get_color(),
                fray_density=self.spin_fray_density.value(),
                fray_length=self.spin_fray_len.value(),
                random_seed=self.spin_seed.value(),
                fray_enabled=self.chk_fray.isChecked(),
            ),
            output=OutputConfig(
                padding=35,
                supersampling=supersampling,
            )
        )
