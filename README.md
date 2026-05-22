
# Eevee Presets

A Blender add-on that lets you instantly switch between **Performance**, **Quality**, and **User** presets for Eevee.

Eevee Presets offers two very different configurations:

- Maximum viewport performance while building and iterating
- Higher visual quality when checking lighting, materials, and presentation

Instead of manually changing multiple settings every time or switching rendering modes, Eevee Presets applies your preferred configuration with a single click.

Some rendering modes do not work well with volumetrics, or other objects with transparency, making them not suitable for everyone as a way of increasing viewport performance (FPS).

In some test scenes, switching to Performance mode increased viewport framerate by **10× or more**.

---

## Development Note

This was developed with assistance from generative AI for planning, code iteration, debugging, and documentation. The project was manually tested.

---

## Features

### Instant Preset Switching

### Custom Preset Names

- Rename presets to fit your workflow.

### Save Custom Presets

### Preset Difference Warning

- Useful when you have unsaved changes.

### Hotkey Support

- Presets can be assigned to keyboard shortcuts.

### Quick Favorites Support

### JSON Import / Export

- Back up and Share Export presets easily.

### Global Storage

- User presets are stored in Blender preferences and are available across projects.

---

## Settings Included

The following Eevee settings are saved and restored:

- Viewport Samples
- Denoising
- Fast GI Approximation
- Volumes Resolution
- Simplify
- Viewport Pixel Size
- Raytracing Resolution
- Shading Compositor
  - Disabled
  - Camera
  - Always

---

## Installation

No special steps required (do as you would with any other add-on):

1. Download.
2. Open Blender. Go to **Edit → Preferences → Add-ons**.
3. Click **Install...**
4. Select the downloaded file.
5. Enable **Eevee Presets** add-on.

---

## Usage

1. Open Blender.
2. Go to **Render Properties**.
3. Locate the **Eevee Presets** panel.
4. Click:
   - **Performance** for maximum viewport responsiveness
   - **Quality** for improved visual fidelity

To customize a preset:

1. Adjust Eevee settings as desired.
2. Click **Save Preset**.
3. Review the highlighted changes.
4. Confirm the save.

---

## Why This Exists

This add-on was created to reduce friction in everyday Blender workflows.

Repeatedly navigating through multiple Eevee settings can interrupt creative flow. A single-click solution keeps the focus on creating rather than configuration.

---

## Future Development

?

---

## License

MIT License

See `LICENSE` for details.
