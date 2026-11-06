"""Configuration data models for Frayed Text PNG Generator."""
from dataclasses import dataclass, field
from typing import Tuple
import re

def parse_color(c: str) -> Tuple[int, int, int]:
    """Parse color string in HEX (#RGB, #RRGGBB) or rgb(r,g,b) format to (R, G, B)."""
    c = c.strip()
    if c.startswith('#'):
        c = c[1:]
    if len(c) == 3:
        c = ''.join([ch * 2 for ch in c])
    if len(c) == 6 and re.match(r'^[0-9a-fA-F]{6}$', c):
        return (int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16))
    
    # Try rgb(r, g, b)
    m = re.match(r'^rgb\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)$', c, re.IGNORECASE)
    if m:
        r, g, b = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if 0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255:
            return (r, g, b)
            
    raise ValueError(f"Invalid color format: '{c}'. Must be #RRGGBB or rgb(r,g,b).")

@dataclass
class TextConfig:
    text: str = "Hoffenheim"
    font_path: str = "C:/Windows/Fonts/arialbd.ttf"
    font_size: int = 160
    letter_spacing: int = 2
    text_color: str = "#1961B5"
    uppercase: bool = False

    def get_effective_text(self) -> str:
        return self.text.upper() if self.uppercase else self.text

    def get_rgb(self) -> Tuple[int, int, int]:
        return parse_color(self.text_color)

@dataclass
class SubTextConfig:
    enabled: bool = False
    text: str = "FRANKFURT"
    font_path: str = ""           # Empty string = inherit primary font
    scale_ratio: float = 0.45     # Secondary font size ratio relative to primary (e.g. 0.45x)
    letter_spacing: int = 2
    alignment: str = "right"      # 'left', 'center', 'right'
    offset_x: int = 0             # Fine horizontal offset in pixels
    offset_y: int = -8            # Vertical distance in pixels (negative to tuck into tier 1)
    uppercase: bool = True
    color: str = ""               # Empty string = inherit primary text color

    def get_effective_text(self) -> str:
        return self.text.upper() if self.uppercase else self.text

    def get_rgb(self, fallback_hex: str) -> Tuple[int, int, int]:
        c = self.color.strip() if self.color and self.color.strip() else fallback_hex
        return parse_color(c)

@dataclass
class StrokeConfig:
    inner_color: str = "#FFFFFF"
    inner_width: int = 4
    inner_enabled: bool = True
    outer_color: str = "#000000"
    outer_width: int = 16
    outer_enabled: bool = True

    def get_inner_rgb(self) -> Tuple[int, int, int]:
        return parse_color(self.inner_color)

    def get_outer_rgb(self) -> Tuple[int, int, int]:
        return parse_color(self.outer_color)

@dataclass
class DashConfig:
    dash_color: str = "#FFFFFF"
    dash_length: float = 10.0
    dash_gap: float = 6.0
    dash_thickness: float = 2.0
    dash_offset: float = 0.0
    dash_enabled: bool = True

    def get_rgb(self) -> Tuple[int, int, int]:
        return parse_color(self.dash_color)

@dataclass
class FrayConfig:
    fray_color: str = "#FFFFFF"
    fray_density: float = 0.85
    fray_length: float = 26.0
    fray_length_variance: float = 10.0
    fray_thickness: float = 1.0
    fray_angle_variance: float = 35.0  # degrees deviation from normal
    fray_randomness: float = 0.65
    fray_opacity: float = 0.90
    random_seed: int = 42
    fray_enabled: bool = True

    def get_rgb(self) -> Tuple[int, int, int]:
        return parse_color(self.fray_color)

@dataclass
class OutputConfig:
    padding: int = 35
    supersampling: int = 2  # 2x supersampling for razor sharp anti-aliased fibers
    output_path: str = "output/result.png"

@dataclass
class RenderConfig:
    text: TextConfig = field(default_factory=TextConfig)
    subtext: SubTextConfig = field(default_factory=SubTextConfig)
    stroke: StrokeConfig = field(default_factory=StrokeConfig)
    dash: DashConfig = field(default_factory=DashConfig)
    fray: FrayConfig = field(default_factory=FrayConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
