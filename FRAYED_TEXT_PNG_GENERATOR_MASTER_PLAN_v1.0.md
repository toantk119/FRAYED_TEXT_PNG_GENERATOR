# FRAYED TEXT PNG GENERATOR — MASTER DEVELOPMENT PLAN v1.0

## 1. Project Objective

Build a Windows desktop application named **Frayed Text PNG Generator**.

The application must generate high-quality text graphics as transparent RGBA PNG files.

The user can enter:

- Arbitrary text.
- Any installed or selected font.
- Text color using HEX.
- White stroke.
- Black stroke.
- Dashed/stitch outline.
- Procedural fray/fringe effect.
- Output resolution and padding.

The most important requirement is that the **Fray effect must be procedural and generated from the actual alpha-mask geometry of the rendered text**.

Do NOT use a fixed PNG texture pasted around the text.

When the user changes:

```text
Bayer Leverkusen
```

to:

```text
Hoffenheim
```

or:

```text
Hamburger SV
```

all outlines, dashed contours and fray must automatically follow the new text geometry.

---

# 2. Visual Reference

Use the supplied Bayer Leverkusen reference image as the primary visual reference for the effect.

Reference structure:

```text
TEXT
↓
WHITE STROKE
↓
BLACK STROKE
↓
DASHED / STITCH OUTLINE
↓
FRAY / FRINGE
↓
TRANSPARENT BACKGROUND
```

Initial acceptance example:

```text
Text  = Hoffenheim
Color = #1961B5
```

The visual target is a sports/jersey-style wordmark with:

- Clean bold text.
- Thin white inner stroke.
- Strong black outline.
- White dashed/stitch contour.
- Dense irregular white/light-gray frayed fibers.
- Transparent background.

The reference should be treated as a visual target, not as a source texture.

---

# 3. Technology Stack

## Core

Use:

```text
Python 3.12+
```

## Image Processing

Prefer:

```text
Pillow
NumPy
OpenCV
```

## Font Rendering

Use:

```text
FreeType
```

Pillow's FreeType backend is acceptable.

Optionally use:

```text
fontTools
```

for advanced font metadata/handling.

## GUI

Use:

```text
PySide6
```

Do NOT use Tkinter.

---

# 4. Project Architecture

Do not put the whole application into one Python file.

Recommended structure:

```text
frayed-text-generator/
│
├── app/
│   ├── main.py
│   │
│   ├── core/
│   │   ├── text_renderer.py
│   │   ├── mask_processor.py
│   │   ├── stroke_engine.py
│   │   ├── dash_engine.py
│   │   ├── fray_engine.py
│   │   ├── compositor.py
│   │   ├── export_engine.py
│   │   └── geometry.py
│   │
│   ├── models/
│   │   ├── text_config.py
│   │   ├── stroke_config.py
│   │   ├── fray_config.py
│   │   └── project_config.py
│   │
│   ├── ui/
│   │   ├── main_window.py
│   │   ├── preview_widget.py
│   │   ├── controls_panel.py
│   │   ├── color_picker.py
│   │   └── font_selector.py
│   │
│   ├── presets/
│   │   ├── preset_manager.py
│   │   └── default_presets.json
│   │
│   └── utils/
│       ├── color_utils.py
│       ├── image_utils.py
│       ├── font_utils.py
│       └── file_utils.py
│
├── assets/
│   ├── fonts/
│   └── reference/
│
├── output/
│
├── tests/
│   ├── test_text_renderer.py
│   ├── test_stroke_engine.py
│   ├── test_dash_engine.py
│   ├── test_fray_engine.py
│   ├── test_export.py
│   └── test_transparency.py
│
├── config/
│   └── app_config.json
│
├── requirements.txt
├── README.md
└── run.py
```

Keep the core independent from the GUI.

The GUI must call the same core engine that the CLI uses.

---

# 5. Processing Pipeline

The rendering pipeline must be:

```text
USER INPUT
    │
    ▼
Text Configuration
    │
    ▼
Font Rendering
    │
    ▼
Base Alpha Mask
    │
    ├───────────────┐
    ▼               ▼
Text Fill       Geometry
                    │
                    ▼
             Stroke Expansion
                    │
                    ▼
             Dashed Outline
                    │
                    ▼
              Fray Generator
                    │
                    ▼
                Composite
                    │
                    ▼
             RGBA PNG Export
```

All effects must use the same underlying text geometry/mask system.

Do not independently render each effect against a rectangular bounding box.

---

# 6. Text Renderer

## Inputs

```text
text
font_path
font_size
letter_spacing
alignment
```

V1 only needs to support:

```text
Single-line text
```

Multiline text is not required for V1.

## Output

The renderer should return a structured result similar to:

```python
TextRenderResult(
    image=...,
    alpha_mask=...,
    bbox=...,
    width=...,
    height=...
)
```

The alpha mask is the foundation for all later processing.

---

# 7. Text Color

The GUI must provide:

```text
Text Color
[ #1961B5 ]
```

Accept:

```text
#1961B5
1961B5
rgb(25,97,181)
```

Invalid color values must produce a clear validation error.

Do not crash the application.

---

# 8. White Stroke

The first outline around the text is the white stroke.

Required layer order:

```text
TEXT
↓
WHITE STROKE
```

Parameter:

```text
White Stroke Width
```

Suggested range:

```text
0–20 px
```

Suggested default:

```text
2 px
```

The stroke must be sharp.

Do not use blur as a substitute for the stroke.

Morphological dilation or an equivalent precise contour expansion is acceptable.

---

# 9. Black Stroke

The second outline is the black stroke.

Required order:

```text
TEXT
↓
WHITE STROKE
↓
BLACK STROKE
```

Parameter:

```text
Black Stroke Width
```

Suggested range:

```text
0–30 px
```

Suggested default:

```text
5 px
```

The black stroke must expand outside the white stroke.

---

# 10. Dashed / Stitch Outline

The dashed outline must follow the actual contour of the text.

It must NOT be a rectangular border around the entire text.

It must support:

- Outer contours.
- Inner contours.
- Counters/holes in letters.

Examples of letters that must be handled correctly:

```text
A
B
D
O
P
R
a
e
```

## Parameters

```text
Dash Length
Gap Length
Dash Thickness
Dash Offset
```

Suggested defaults:

```text
Dash Length    = 7 px
Gap Length     = 5 px
Dash Thickness = 1.5 px
Dash Offset    = 0 px
```

## Geometry

Use contour extraction, preferably:

```python
cv2.findContours()
```

Convert contours into polylines.

Use arc-length parameterization to distribute dash/gap segments evenly.

Do not distribute dashes using simple pixel stepping if that produces uneven spacing.

---

# 11. Fray Engine — CRITICAL COMPONENT

The Fray Engine is the most important component of this project.

It MUST be procedural.

Do not implement fray as:

- Blur.
- Glow.
- Drop shadow.
- Generic noise.
- Static PNG texture.
- Fixed rectangular texture.
- Simple outer halo.

The fray must be generated from the actual text contour.

---

# 12. Fray Geometry

The Fray Engine must process:

```python
base_mask
outer_contours
inner_contours
fray_config
random_seed
```

It must generate fibers around:

1. Outer boundaries.
2. Inner boundaries/counters.

For example, an `O` must have fray around both:

```text
Outer edge
```

and:

```text
Inner edge
```

This requirement is mandatory.

---

# 13. Fray Generation Algorithm

Recommended implementation:

## Step 1 — Extract contours

Use the alpha mask:

```python
contours = cv2.findContours(...)
```

Classify outer and inner contours correctly.

## Step 2 — Calculate tangent

For each sampled contour point, estimate the local tangent direction.

## Step 3 — Calculate normal

Calculate a normal vector to the contour.

Example:

```text
          normal
            ↑
            │
        ────●────
           contour
```

## Step 4 — Sample contour points

Randomly sample points along the contour according to Fray Density.

Example:

```text
density = 0.80
```

means relatively dense fiber generation.

## Step 5 — Generate fibers

At each sampled point, generate one or more fibers.

Each fiber should vary in:

```text
length
angle
thickness
opacity
curvature
branching
```

The direction should generally follow the local normal but have controlled random deviation.

Example:

```text
normal angle ± 35°
```

Do not make every fiber perfectly perpendicular to the contour.

---

# 14. Fray Parameters

The GUI should expose:

```text
Fray Density
Fray Length
Fray Thickness
Fray Randomness
Fray Spread
Fray Opacity
```

Suggested starting defaults:

```text
Density     = 0.80
Length      = 12 px
Thickness   = 0.7 px
Randomness  = 0.65
Spread      = 0.75
Opacity     = 0.85
```

These are starting values only and must remain configurable.

---

# 15. Fray Appearance

The fray must NOT look like a uniform comb:

```text
|||||||||||||||||||||
```

or:

```text
/////////////////////
```

It should contain:

- Short fibers.
- Medium fibers.
- Occasional longer fibers.
- Small clusters.
- Local density variation.
- Angle variation.
- Slight curvature.
- Small gaps.
- Slightly irregular spacing.

Conceptually:

```text
✳  ✳✳   ✳
  ✳    ✳✳
✳✳      ✳
   ✳✳
```

The result should resemble dense, irregular textile/fiber/frayed material.

---

# 16. Fray Color

Default:

```text
#FFFFFF
```

V1 only requires white/light-gray fray.

Optional future parameters:

```text
Primary Fray Color
Secondary Fray Color
```

Do not make this a V1 priority.

---

# 17. Inner and Outer Fray

The Fray Engine must support both:

```text
EXTERNAL CONTOUR
INTERNAL CONTOUR
```

For example:

```text
B
```

must produce fray around both the outside and the internal counters.

This is a mandatory visual acceptance criterion.

---

# 18. Relative vs Pixel Fray

Do not lock fray size to absolute pixels only.

Support:

```text
Fray Length Mode:
[ Pixel ]
[ Relative ]
```

The relative mode should scale fray proportionally to text size.

For example:

```text
150 px tall text → approximately 12 px fray
300 px tall text → proportionally larger fray
```

The same principle should eventually be available for stroke widths.

This is important for generating many team names with different text lengths and font sizes.

---

# 19. Canvas

Canvas must automatically fit the complete generated effect.

It must include:

```text
Text
Strokes
Dash
Fray
Padding
```

Suggested default:

```text
Canvas Padding = 30 px
```

The canvas must be RGBA.

The output must contain no baked background.

---

# 20. PNG Export

Output:

```text
PNG
RGBA
Transparent Background
```

Suggested filename:

```text
Hoffenheim_frayed.png
```

If the filename already exists:

```text
Hoffenheim_frayed_001.png
Hoffenheim_frayed_002.png
...
```

Do not overwrite existing output unless the user explicitly chooses overwrite.

---

# 21. GUI

The GUI should contain two main areas:

```text
┌──────────────────────────────────────────────┐
│                    TOOLBAR                   │
├──────────────────┬───────────────────────────┤
│                  │                           │
│    CONTROLS      │          PREVIEW          │
│                  │                           │
│    Text          │                           │
│    Font          │       Hoffenheim          │
│    Color         │                           │
│                  │                           │
│    Strokes       │                           │
│    Dash          │                           │
│    Fray          │                           │
│                  │                           │
├──────────────────┴───────────────────────────┤
│       GENERATE        EXPORT PNG              │
└──────────────────────────────────────────────┘
```

---

# 22. Preview

The preview must show a checkerboard background to indicate transparency.

The checkerboard is UI-only.

It must NEVER be included in the exported PNG.

The preview should support zoom if practical.

---

# 23. Live Preview

When changing:

```text
Text
Color
Stroke
Dash
Fray
```

the preview should update automatically.

Use debounce, approximately:

```text
100–250 ms
```

to prevent excessive rendering while sliders are moving.

---

# 24. Preview vs Export Quality

Preview may use reduced quality for speed.

Example:

```text
Preview:
50% fray density
2x supersampling
```

Export:

```text
100% fray density
4x supersampling
```

Exact implementation can be tuned after profiling.

---

# 25. Random Seed

The Fray Engine must use a configurable deterministic seed.

Example:

```text
Seed = 123456
```

If the following remain unchanged:

```text
Text
Font
Color
Parameters
Seed
```

the generated fray should be reproducible.

Provide:

```text
[ Randomize Seed ]
```

to create a new visual variation.

This is important for POD reproducibility.

---

# 26. Preset System

Support JSON presets.

Example:

```json
{
  "name": "Football Frayed",
  "text_color": "#1961B5",
  "white_stroke": 2,
  "black_stroke": 5,
  "dash_length": 7,
  "dash_gap": 5,
  "dash_thickness": 1.5,
  "fray_density": 0.8,
  "fray_length": 12,
  "fray_thickness": 0.7,
  "fray_randomness": 0.65,
  "fray_spread": 0.75
}
```

GUI:

```text
Preset:
[ Football Frayed ▼ ]

[ Save Preset ]
[ Delete Preset ]
```

---

# 27. Font System

Allow the user to:

- Select an installed font.
- Browse for `.ttf`.
- Browse for `.otf`.

Windows fonts should be discoverable from:

```text
C:\Windows\Fonts
```

Do not hard-code a specific font.

---

# 28. Typography Controls

V1:

```text
Font
Font Size
Letter Spacing
```

Future versions may add:

```text
Horizontal Scale
Vertical Scale
Tracking
Kerning
```

Do not delay V1 for advanced typography features.

---

# 29. Output Resolution

Support:

```text
Auto
Custom Width
Custom Height
```

Default:

```text
Auto
```

In Auto mode:

```text
Canvas =
Text Bounds
+ Stroke Bounds
+ Dash Bounds
+ Fray Bounds
+ Padding
```

When custom resolution is used, scale the complete composition consistently.

Do not distort individual stroke widths or fray geometry.

---

# 30. Anti-Aliasing and Supersampling

The output must have clean anti-aliased edges.

This applies to:

- Text.
- White stroke.
- Black stroke.
- Dashed line.
- Fray fibers.

Consider supersampling:

```text
Render at 2x or 4x
↓
Generate effects
↓
Downsample
↓
Final PNG
```

This is especially important for very thin fray fibers.

---

# 31. Compositor

Keep each logical layer separate in memory:

```python
layers = {
    "text": ...,
    "white_stroke": ...,
    "black_stroke": ...,
    "dash": ...,
    "fray": ...
}
```

Composite only after all effects have been generated.

Required logical order:

```text
FRAY
DASH
BLACK STROKE
WHITE STROKE
TEXT
TRANSPARENT BACKGROUND
```

This architecture must remain compatible with future layered PSD export.

---

# 32. PSD Future Compatibility

V1 only needs PNG export.

However, the internal architecture must make future PSD export possible.

Future PSD structure:

```text
FRAY
DASH
BLACK STROKE
WHITE STROKE
TEXT
```

Do not design the core as a single irreversible bitmap operation.

---

# 33. Batch Generation

The core should support future batch generation.

Example JSON:

```json
[
  {
    "text": "Hoffenheim",
    "color": "#1961B5"
  },
  {
    "text": "Bayer Leverkusen",
    "color": "#E32221"
  },
  {
    "text": "Hamburger SV",
    "color": "#1E5CB3"
  }
]
```

Expected output:

```text
Hoffenheim_frayed.png
Bayer_Leverkusen_frayed.png
Hamburger_SV_frayed.png
```

Batch GUI can be implemented later.

---

# 34. CLI Mode

The core must also be callable from command line.

Example:

```bash
python run.py \
  --text "Hoffenheim" \
  --font "Arial Bold" \
  --color "#1961B5" \
  --white-stroke 2 \
  --black-stroke 5 \
  --dash-length 7 \
  --dash-gap 5 \
  --fray-density 0.8 \
  --fray-length 12 \
  --seed 12345 \
  --output "./output/Hoffenheim.png"
```

The CLI and GUI must use the same core engine.

---

# 35. Configuration

Do not hard-code effect parameters throughout the source code.

Use structured configuration models.

Possible files:

```text
config/default.json
config/football.json
config/custom.json
```

All rendering parameters must be represented in configuration/data models.

---

# 36. Input Validation

Validate:

## Text

Text must not be empty.

## Font

Font file must exist and be readable.

## Color

HEX/RGB value must be valid.

## Stroke

Values must be:

```text
>= 0
```

## Fray

Density, length and thickness must be valid positive values.

Invalid input must show a user-friendly GUI error.

Never crash the application because of normal invalid input.

---

# 37. Performance

Fray generation may involve thousands of fibers.

Avoid inefficient Python per-pixel processing.

Prefer:

```text
NumPy
OpenCV
Vectorized operations
```

Use Python-level loops only where appropriate, such as fiber-level geometry generation.

Profile before optimizing prematurely.

---

# 38. Required Automated Tests

Create tests for:

## Text Rendering

- Normal text.
- Long text.
- Short text.
- Different fonts.
- Different sizes.

## Stroke Engine

- Zero stroke.
- Small stroke.
- Large stroke.
- Correct layer order.

## Dash Engine

- Outer contour.
- Inner contour.
- Multiple counters.
- Dash/gap consistency.

## Fray Engine

- Outer contour.
- Inner contour.
- Different densities.
- Different lengths.
- Different seeds.
- Same seed reproducibility.

## Export

- PNG created.
- RGBA mode.
- Transparent background.
- Correct dimensions.

---

# 39. Mandatory Visual Test Strings

At minimum test:

```text
Hoffenheim
Bayer Leverkusen
Hamburger SV
ABC
OOOO
MMMM
A B R O P
```

The purpose of the last four tests is to verify:

- Inner contours.
- Counters.
- Thick letters.
- Multiple separated glyphs.
- Different contour geometries.

---

# 40. Transparency Test

Verify programmatically:

```python
image.mode == "RGBA"
```

The output must contain transparent pixels outside the generated bounds.

Do not bake:

```text
Black background
White background
Checkerboard
```

into the PNG.

---

# 41. Visual Acceptance Criteria

The generated result must visually follow this hierarchy:

```text
FRAY
  ✳✳✳✳✳✳✳✳
DASH
  - - - - - -
BLACK STROKE
  ███████████
WHITE STROKE
  ───────────
TEXT
  Hoffenheim
```

Reject output if:

- Fray looks like glow.
- Fray looks like blur.
- Fray looks like a drop shadow.
- Fray is just generic noise.
- Fray is based on a rectangular bounding box.
- Dashed line becomes a rectangle.
- Dashed line does not follow glyph contours.
- Inner counters have no fray.
- Transparent background is flattened.

---

# 42. Visual Target

The goal is not pixel-for-pixel duplication.

The goal is to reproduce the visual language of the supplied reference:

## Text

- Bold.
- Clean.
- Sports/jersey aesthetic.

## White Stroke

- Thin.
- Clean.
- Sharp.

## Black Stroke

- Strong.
- Clearly visible.
- Thicker than white stroke.

## Dashed Line

- White.
- Evenly distributed.
- Follows glyph contours.
- Works on both outer and inner contours.

## Fray

- White/light gray.
- Dense.
- Irregular.
- Fibrous.
- Many tiny fibers.
- Some longer fibers.
- Variable density.
- Follows the actual text silhouette.

---

# 43. No AI Image Generation in Core

Do NOT use DALL-E, Sora, or any other AI image generation system to create the actual output.

The generator must be:

```text
Procedural
Deterministic
Parameter-driven
Repeatable
```

AI may only be used externally for visual reference or development assistance.

The actual generated PNG must come from the program.

---

# 44. Development Roadmap

## Phase 1 — Foundation

Implement:

```text
Project structure
Config models
Font loader
Text renderer
Alpha mask
RGBA canvas
PNG export
```

Acceptance:

Generate a basic:

```text
Hoffenheim.png
```

with transparent background.

---

## Phase 2 — Stroke Engine

Implement:

```text
White Stroke
Black Stroke
```

Acceptance:

```text
TEXT
↓
WHITE
↓
BLACK
```

with correct geometry.

---

## Phase 3 — Dash Engine

Implement:

```text
Contour extraction
Arc-length sampling
Dash/gap generation
Outer contour
Inner contour
```

Acceptance:

Dashed line follows actual glyph contours.

---

## Phase 4 — Fray Engine

This is the highest-priority visual phase.

Implement:

```text
Contour sampling
Normal calculation
Fiber generation
Length variation
Angle variation
Thickness variation
Density control
Random seed
Inner contour fray
Outer contour fray
```

Acceptance:

Visual appearance is close to the supplied reference.

---

## Phase 5 — Compositor

Combine:

```text
TEXT
WHITE
BLACK
DASH
FRAY
```

while preserving alpha.

---

## Phase 6 — GUI

Implement:

```text
Text input
Font selector
Color picker
Stroke controls
Dash controls
Fray controls
Preview
Generate
Export
```

---

## Phase 7 — Presets

Implement:

```text
Save preset
Load preset
Delete preset
```

---

## Phase 8 — CLI

Implement command-line generation.

---

## Phase 9 — Batch

Implement JSON/CSV batch generation.

---

## Phase 10 — PSD

Future phase.

Do not block V1 on PSD export.

---

# 45. Definition of Done

V1 is complete only when all of the following work:

## Input

```text
Text = Hoffenheim
Color = #1961B5
Any supported font
```

## Output

```text
Hoffenheim_frayed.png
```

## PNG

```text
RGBA
Transparent
High quality
Anti-aliased
```

## Logical Layers

```text
TEXT
WHITE STROKE
BLACK STROKE
DASH
FRAY
```

## Fray

Must be:

```text
Procedural
Randomized
Seedable
Contour-aware
Inner-contour-aware
```

## Text Replacement

Changing:

```text
Hoffenheim
```

to:

```text
Bayer Leverkusen
```

must require no code changes.

## Color Replacement

Changing:

```text
#1961B5
```

to another valid color must require no code changes.

---

# 46. Important Implementation Order

Do NOT start by building the complete GUI.

Required development order:

```text
1. Core text rendering
2. Alpha mask
3. Geometry
4. White stroke
5. Black stroke
6. Dash engine
7. Fray engine
8. Compositor
9. PNG export
10. Automated tests
11. GUI
12. Presets
13. CLI
14. Batch generation
```

After each phase, run tests.

The Fray Engine must be testable independently.

---

# 47. Antigravity Execution Brief

Build the project according to this specification.

Do not simplify the Fray Engine into blur, glow, noise, shadow, or a static texture overlay.

The Fray Engine must be procedural and generated from the actual alpha-mask contours of the rendered text.

The system must support both outer and inner contours.

The visual layer order is strictly:

```text
TEXT
→ WHITE STROKE
→ BLACK STROKE
→ DASHED/STITCH OUTLINE
→ FRAY
```

Output must be a genuine RGBA PNG with a transparent background.

The core must be independent from the GUI.

Implement the core first and write automated tests before building the GUI.

Do not use AI image generation.

Do not hard-code the word "Hoffenheim".

The same engine must work with arbitrary text, fonts, colors, stroke widths, dash parameters and fray parameters.

Implement deterministic randomization using a configurable seed.

Use the supplied Bayer Leverkusen reference image as the visual reference for the effect.

The first visual acceptance test must use:

```text
Text  = Hoffenheim
Color = #1961B5
```

and must produce a transparent PNG with the same general layered visual structure as the reference.

Before implementing the GUI, demonstrate that the CLI/core can generate the target PNG successfully.

After each implementation phase, report:

- Files created/modified.
- Tests executed.
- Test results.
- Known limitations.
- Next phase.

Do not silently change the architecture or remove requested features.

If a technical decision is necessary, document it in:

```text
DECISIONS.md
```

---

# 48. Final Instruction

Prioritize **visual fidelity of the procedural fray system** over GUI polish.

The primary success criterion is:

> Given any text + font + color, the application can generate a transparent PNG whose layered appearance resembles the supplied Bayer Leverkusen reference, with clean white stroke, black outline, contour-following dashed/stitch line, and dense irregular procedural fray around both outer and inner text contours.

Build the core rendering engine first.
