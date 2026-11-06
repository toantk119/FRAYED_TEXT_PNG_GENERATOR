"""Command-line interface runner for Frayed Text PNG Generator."""
import argparse
import os
import sys

# Ensure root folder is in python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.models.render_config import (
    RenderConfig, TextConfig, StrokeConfig, DashConfig, FrayConfig, OutputConfig
)
from app.core.engine import FrayedTextEngine

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate transparent Frayed Text PNG graphics.")
    # Text
    parser.add_argument("--text", type=str, default="Hoffenheim", help="Input text string")
    parser.add_argument("--font", type=str, default="C:/Windows/Fonts/arialbd.ttf", help="Path to TTF/OTF font")
    parser.add_argument("--font-size", type=int, default=160, help="Font size in pixels")
    parser.add_argument("--letter-spacing", type=int, default=2, help="Letter spacing in pixels")
    parser.add_argument("--color", type=str, default="#1961B5", help="Text fill color HEX")
    parser.add_argument("--uppercase", action="store_true", help="Convert text to uppercase (ALL CAPS)")

    # Strokes
    parser.add_argument("--inner-stroke-color", type=str, default="#FFFFFF", help="Inner stroke color HEX")
    parser.add_argument("--inner-stroke-width", type=int, default=4, help="Inner stroke width in pixels")
    parser.add_argument("--outer-stroke-color", type=str, default="#000000", help="Outer stroke color HEX")
    parser.add_argument("--outer-stroke-width", type=int, default=16, help="Outer stroke width in pixels")

    # Dash Stitch
    parser.add_argument("--dash-color", type=str, default="#FFFFFF", help="Dash stitch color HEX")
    parser.add_argument("--dash-length", type=float, default=10.0, help="Dash segment length")
    parser.add_argument("--dash-gap", type=float, default=6.0, help="Dash gap length")
    parser.add_argument("--dash-thickness", type=float, default=2.0, help="Dash line thickness")

    # Fray
    parser.add_argument("--fray-color", type=str, default="#FFFFFF", help="Fray fibers color HEX")
    parser.add_argument("--fray-density", type=float, default=0.85, help="Fray density (0.1 - 1.0)")
    parser.add_argument("--fray-length", type=float, default=26.0, help="Fray fiber length")
    parser.add_argument("--fray-randomness", type=float, default=0.65, help="Fray randomness factor")
    parser.add_argument("--seed", type=int, default=42, help="Deterministic random seed")

    # Output
    parser.add_argument("--padding", type=int, default=35, help="Canvas padding")
    parser.add_argument("--supersampling", type=int, default=2, help="Supersampling multiplier (1 or 2)")
    parser.add_argument("--output", type=str, default="output/result.png", help="Output file path")

    return parser

def main():
    parser = build_parser()
    args = parser.parse_args()

    config = RenderConfig(
        text=TextConfig(
            text=args.text,
            font_path=args.font,
            font_size=args.font_size,
            letter_spacing=args.letter_spacing,
            text_color=args.color,
            uppercase=args.uppercase,
        ),
        stroke=StrokeConfig(
            inner_color=args.inner_stroke_color,
            inner_width=args.inner_stroke_width,
            outer_color=args.outer_stroke_color,
            outer_width=args.outer_stroke_width,
        ),
        dash=DashConfig(
            dash_color=args.dash_color,
            dash_length=args.dash_length,
            dash_gap=args.dash_gap,
            dash_thickness=args.dash_thickness,
        ),
        fray=FrayConfig(
            fray_color=args.fray_color,
            fray_density=args.fray_density,
            fray_length=args.fray_length,
            fray_randomness=args.fray_randomness,
            random_seed=args.seed,
        ),
        output=OutputConfig(
            padding=args.padding,
            supersampling=args.supersampling,
            output_path=args.output,
        )
    )

    print(f"[FrayedTextEngine] Rendering text: '{config.text.text}' with seed {config.fray.random_seed}...")
    engine = FrayedTextEngine(supersampling=config.output.supersampling)
    img = engine.render(config)

    # Ensure output dir exists
    out_dir = os.path.dirname(config.output.output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    img.save(config.output.output_path, "PNG")
    print(f"[FrayedTextEngine] Successfully exported RGBA PNG to: {config.output.output_path}")
    print(f"[FrayedTextEngine] Output dimensions: {img.size[0]}x{img.size[1]}, Mode: {img.mode}")

if __name__ == "__main__":
    main()
