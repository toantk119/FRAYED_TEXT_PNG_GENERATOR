"""High-level rendering coordinator engine."""
from PIL import Image
from app.models.render_config import RenderConfig
from app.core.text_renderer import TextRenderer
from app.core.stroke_engine import StrokeEngine
from app.core.dash_engine import DashEngine
from app.core.fray_engine import FrayEngine
from app.core.compositor import Compositor

class FrayedTextEngine:
    def __init__(self, supersampling: int = 2):
        self.scale = supersampling
        self.text_renderer = TextRenderer(scale=self.scale)
        self.stroke_engine = StrokeEngine(scale=self.scale)
        self.dash_engine = DashEngine(scale=self.scale)
        self.fray_engine = FrayEngine(scale=self.scale)
        self.compositor = Compositor(scale=self.scale)

    def render(self, config: RenderConfig) -> Image.Image:
        """Executes the full pipeline and returns a transparent RGBA PIL Image."""
        # 1. Text & Base Alpha Mask (with optional dual-tier subtext)
        subtext_cfg = getattr(config, "subtext", None)
        text_mask, bbox, sub_mask = self.text_renderer.render_mask(
            config.text, padding=config.output.padding + 60, subtext_config=subtext_cfg
        )

        # 2. Inner and Outer Strokes
        inner_mask, outer_mask, _ = self.stroke_engine.generate_strokes(
            text_mask, config.stroke
        )

        # 3. Dashed Stitch Outline
        dash_mask = self.dash_engine.generate_dash_mask(
            inner_mask, outer_mask, config.dash, config.stroke
        )

        # 4. Procedural Frayed Fringe
        fray_rgba = self.fray_engine.generate_fray_layer(
            outer_mask, config.fray
        )

        # 5. Compositing & Anti-aliased Downsampling
        image = self.compositor.composite(
            text_mask, inner_mask, outer_mask, dash_mask, fray_rgba, config, subtext_mask=sub_mask
        )

        return image
