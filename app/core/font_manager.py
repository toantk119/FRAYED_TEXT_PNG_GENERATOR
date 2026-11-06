"""Windows system font manager and registry scanner with PSD-style grouping."""
import os
import re
import json
import winreg
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple

STYLES = [
    'Extra Black Italic', 'Extra Black', 'Ultra Black Italic', 'Ultra Black',
    'Black Italic', 'Bold Italic', 'SemiBold Italic', 'Semibold Italic',
    'Light Italic', 'Ultra Bold Italic', 'Ultra Bold', 'Semi Bold', 'SemiBold',
    'Demi Bold', 'Demi Italic', 'Heavy Italic', 'Heavy', 'Black', 'Bold',
    'Italic', 'Medium Italic', 'Medium', 'Light', 'Ultra Light', 'Thin',
    'Regular', 'Condensed Bold', 'Condensed', 'Expanded', 'Oblique'
]

PREFS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".font_prefs.json")

@dataclass
class FontVariant:
    family: str
    style: str
    path: str
    full_name: str
    is_custom: bool = False

@dataclass
class FontFamily:
    name: str
    variants: List[FontVariant] = field(default_factory=list)

    def get_default_variant(self) -> FontVariant:
        """Returns Regular or Bold or the first available variant."""
        for v in self.variants:
            if v.style.lower() in ("bold", "regular"):
                return v
        return self.variants[0] if self.variants else None


class FontManager:
    """Scans and manages system fonts grouped into families and styles."""
    _instance = None

    def __init__(self):
        self.families: Dict[str, FontFamily] = {}
        self.recent_paths: List[str] = []
        self.favorite_names: List[str] = []
        self._load_prefs()
        self.scan_system_fonts()

    @classmethod
    def get_instance(cls) -> "FontManager":
        if cls._instance is None:
            cls._instance = FontManager()
        return cls._instance

    def _parse_font_name(self, reg_name: str) -> Tuple[str, str]:
        """Extracts family name and style from registry font description."""
        name = re.sub(r'\s*\((TrueType|OpenType)\)\s*$', '', reg_name, flags=re.IGNORECASE).strip()
        for style in STYLES:
            pattern = r'\b' + re.escape(style) + r'$'
            m = re.search(pattern, name, re.IGNORECASE)
            if m:
                family = name[:m.start()].strip()
                if family:
                    return family, style
        return name, 'Regular'

    def scan_system_fonts(self):
        """Scans Windows Registry for all installed TTF/OTF fonts."""
        self.families.clear()
        found_paths = set()

        def scan_reg(root, path):
            try:
                with winreg.OpenKey(root, path) as key:
                    for i in range(winreg.QueryInfoKey(key)[1]):
                        name, val, _ = winreg.EnumValue(key, i)
                        if not os.path.isabs(val):
                            val = os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts', val)
                        if os.path.exists(val) and val.lower().endswith(('.ttf', '.otf')):
                            if val in found_paths:
                                continue
                            found_paths.add(val)
                            family, style = self._parse_font_name(name)
                            if family not in self.families:
                                self.families[family] = FontFamily(name=family)
                            self.families[family].variants.append(
                                FontVariant(family=family, style=style, path=val, full_name=name)
                            )
            except Exception:
                pass

        scan_reg(winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts')
        scan_reg(winreg.HKEY_CURRENT_USER, r'SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts')

        # Ensure default fallbacks exist if registry scan returned empty (e.g. non-Windows test runners)
        if not self.families:
            fallback_path = "C:/Windows/Fonts/arialbd.ttf"
            self.families["Arial"] = FontFamily(
                name="Arial",
                variants=[FontVariant(family="Arial", style="Bold", path=fallback_path, full_name="Arial Bold")]
            )

    def add_custom_font(self, font_path: str) -> Optional[FontVariant]:
        """Registers an external custom TTF/OTF font file."""
        if not os.path.exists(font_path) or not font_path.lower().endswith(('.ttf', '.otf')):
            return None
        base = os.path.splitext(os.path.basename(font_path))[0]
        family, style = self._parse_font_name(base)
        variant = FontVariant(family=family, style=style, path=font_path, full_name=base, is_custom=True)

        if family not in self.families:
            self.families[family] = FontFamily(name=family)
        # Avoid duplicate path
        if not any(v.path.lower() == font_path.lower() for v in self.families[family].variants):
            self.families[family].variants.append(variant)

        self.add_recent(font_path)
        return variant

    def get_sorted_families(self) -> List[FontFamily]:
        """Returns font families sorted alphabetically A-Z."""
        return [self.families[k] for k in sorted(self.families.keys(), key=lambda s: s.lower())]

    def find_variant_by_path(self, path: str) -> Optional[FontVariant]:
        norm_path = os.path.normpath(path).lower()
        for fam in self.families.values():
            for v in fam.variants:
                if os.path.normpath(v.path).lower() == norm_path:
                    return v
        return None

    def is_favorite(self, name_or_family: str) -> bool:
        return name_or_family in self.favorite_names

    def toggle_favorite(self, name_or_family: str):
        if name_or_family in self.favorite_names:
            self.favorite_names.remove(name_or_family)
        else:
            self.favorite_names.append(name_or_family)
        self._save_prefs()

    def add_recent(self, font_path: str):
        norm = os.path.normpath(font_path)
        if norm in self.recent_paths:
            self.recent_paths.remove(norm)
        self.recent_paths.insert(0, norm)
        self.recent_paths = self.recent_paths[:20]  # Keep 20 most recent
        self._save_prefs()

    def _load_prefs(self):
        if os.path.exists(PREFS_FILE):
            try:
                with open(PREFS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.favorite_names = data.get("favorites", [])
                    self.recent_paths = data.get("recent", [])
            except Exception:
                pass

    def _save_prefs(self):
        try:
            with open(PREFS_FILE, "w", encoding="utf-8") as f:
                json.dump({
                    "favorites": self.favorite_names,
                    "recent": self.recent_paths
                }, f, indent=2)
        except Exception:
            pass
