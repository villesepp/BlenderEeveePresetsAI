<img width="600" height="337" alt="ezgif-51fb90eafdb8fc17" src="https://github.com/user-attachments/assets/3f1f361e-7881-43f2-a89a-195a9f2568c0" />

# Eevee Presets

A Blender add-on that lets you instantly switch between **Performance**, **Quality**, and **User** presets for Eevee.

Eevee Presets offers two very different configurations:

- Maximum viewport performance while building and iterating
- Higher visual quality when checking lighting, materials, and presentation

Instead of manually changing multiple settings every time or switching rendering modes, Eevee Presets applies your preferred configuration with a single click.

Some rendering modes do not work well with volumetrics, or other objects with transparency, making them not suitable for everyone as a way of increasing viewport performance (FPS).

In some test scenes, switching to Performance mode increased viewport framerate by **10× or more**.

<img width="1543" height="918" alt="fpscomparisonn" src="https://github.com/user-attachments/assets/ecc82d3d-5848-484c-932c-dfb86e2b7d2e" />

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

<img width="863" height="505" alt="fpsinstall" src="https://github.com/user-attachments/assets/8e04e7a7-f1fe-4ec5-a1ab-520d224f7948" />


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
