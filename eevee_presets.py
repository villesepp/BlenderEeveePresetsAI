bl_info = {
    "name": "Eevee Presets",
    "author": "OpenAI",
    "version": (1, 0, 0),
    "blender": (4, 5, 5),
    "location": "Render Properties > Eevee Presets",
    "description": "Save and load simple Eevee performance and quality presets.",
    "category": "Render",
}

import json

import bpy
from bpy_extras.io_utils import ExportHelper, ImportHelper
from bpy.props import EnumProperty, StringProperty
from bpy.types import AddonPreferences, Operator, Panel, PropertyGroup


PRESET_ITEMS = (
    ("PERFORMANCE", "Performance", "Performance-oriented Eevee settings"),
    ("QUALITY", "Quality", "Quality-oriented Eevee settings"),
    ("USER", "User", "User-defined Eevee settings"),
)

PRESET_IDS = {item[0] for item in PRESET_ITEMS}

DEFAULT_PRESET_NAMES = {
    "PERFORMANCE": "Performance",
    "QUALITY": "Quality",
    "USER": "User",
}

DEFAULT_PRESETS = {
    "PERFORMANCE": {
        "viewport_samples": 2,
        "denoising": True,
        "fast_gi_approximation": False,
        "volumes_resolution": "16",
        "simplify": True,
        "viewport_pixel_size": "8",
        "raytracing_resolution": "4",
        "shading_compositor": "DISABLED",
    },
    "QUALITY": {
        "viewport_samples": 16,
        "denoising": True,
        "fast_gi_approximation": True,
        "volumes_resolution": "4",
        "simplify": False,
        "viewport_pixel_size": "1",
        "raytracing_resolution": "1",
        "shading_compositor": "ALWAYS",
    },
    "USER": {},
}

SETTINGS = (
    {
        "key": "viewport_samples",
        "label": "Viewport Samples",
        "owner": "eevee",
        "prop": "taa_samples",
    },
    {
        "key": "denoising",
        "label": "Denoising",
        "owner": "eevee",
        "prop": "use_taa_reprojection",
    },
    {
        "key": "fast_gi_approximation",
        "label": "Fast GI Approximation",
        "owner": "eevee",
        "prop": "use_fast_gi",
    },
    {
        "key": "volumes_resolution",
        "label": "Volumes Resolution",
        "owner": "eevee",
        "prop": "volumetric_tile_size",
    },
    {
        "key": "simplify",
        "label": "Simplify",
        "owner": "render",
        "prop": "use_simplify",
    },
    {
        "key": "viewport_pixel_size",
        "label": "Viewport Pixel Size",
        "owner": "render",
        "prop": "preview_pixel_size",
    },
    {
        "key": "raytracing_resolution",
        "label": "Raytracing Resolution",
        "owner": "raytracing",
        "prop": "resolution_scale",
    },
    {
        "key": "shading_compositor",
        "label": "Shading Compositor",
        "owner": "viewport_shading",
        "prop": "use_compositor",
    },
)

SHORTCUTS = (
    ("eevee_presets.load_performance", "F5"),
    ("eevee_presets.load_quality", "F6"),
    ("eevee_presets.load_user", "F7"),
)

addon_keymaps = []


def _settings_owner(scene, owner):
    if owner == "eevee":
        return scene.eevee
    if owner == "raytracing":
        return scene.eevee.ray_tracing_options
    return scene.render


def _viewport_shading(context):
    if not context.screen:
        return None

    for area in context.screen.areas:
        if area.type != "VIEW_3D":
            continue

        for space in area.spaces:
            if space.type == "VIEW_3D":
                return space.shading

    return None


def _viewport_shadings(context):
    if not context.screen:
        return

    for area in context.screen.areas:
        if area.type != "VIEW_3D":
            continue

        for space in area.spaces:
            if space.type == "VIEW_3D":
                yield space.shading


def _read_setting(context, setting):
    if setting["owner"] == "viewport_shading":
        shading = _viewport_shading(context)
        return getattr(shading, setting["prop"]) if shading else "DISABLED"

    scene = context.scene
    return getattr(_settings_owner(scene, setting["owner"]), setting["prop"])


def _write_setting(context, setting, value):
    if setting["owner"] == "viewport_shading":
        for shading in _viewport_shadings(context):
            setattr(shading, setting["prop"], value)
        return

    scene = context.scene
    setattr(_settings_owner(scene, setting["owner"]), setting["prop"], value)


def _display_value(value):
    if isinstance(value, bool):
        return "On" if value else "Off"
    if value in {"DISABLED", "CAMERA", "ALWAYS"}:
        return value.title()
    return str(value)


def _addon_preferences():
    return bpy.context.preferences.addons[__name__].preferences


def _load_presets():
    presets = {
        preset_id: values.copy()
        for preset_id, values in DEFAULT_PRESETS.items()
    }
    raw = _addon_preferences().presets_json
    if not raw:
        return presets

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return presets

    if not isinstance(data, dict):
        return presets

    for preset_id, values in data.items():
        if isinstance(values, dict):
            preset = presets.setdefault(preset_id, {})
            preset.update(values)

    return presets


def _save_presets(presets):
    _addon_preferences().presets_json = json.dumps(presets, sort_keys=True)


def _load_preset_names():
    names = DEFAULT_PRESET_NAMES.copy()
    raw = _addon_preferences().preset_names_json
    if not raw:
        return names

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return names

    if not isinstance(data, dict):
        return names

    for preset_id, name in data.items():
        if preset_id in names and isinstance(name, str) and name.strip():
            names[preset_id] = name.strip()

    return names


def _save_preset_names(names):
    _addon_preferences().preset_names_json = json.dumps(names, sort_keys=True)


def _preset_name(identifier):
    return _load_preset_names().get(identifier, identifier.title())


def _save_user_preferences():
    try:
        bpy.ops.wm.save_userpref()
    except RuntimeError:
        pass


def _export_data(preset_id):
    return {
        "version": 1,
        "preset_id": preset_id,
        "preset_name": _preset_name(preset_id),
        "preset": _load_presets().get(preset_id, {}),
    }


def _sanitize_import_data(data, target_preset_id):
    if not isinstance(data, dict):
        raise ValueError("Preset file must contain a JSON object")

    imported_preset = data.get("preset")
    if not isinstance(imported_preset, dict):
        raise ValueError("Preset file is missing a preset object")

    presets = _load_presets()
    preset = {}
    for setting in SETTINGS:
        key = setting["key"]
        if key in imported_preset:
            preset[key] = imported_preset[key]

    presets[target_preset_id] = preset

    names = _load_preset_names()
    imported_name = data.get("preset_name")
    if isinstance(imported_name, str) and imported_name.strip():
        names[target_preset_id] = imported_name.strip()

    return presets, names


def _capture_scene_settings(context):
    return {setting["key"]: _read_setting(context, setting) for setting in SETTINGS}


def _apply_scene_settings(context, preset):
    for setting in SETTINGS:
        if setting["key"] in preset:
            _write_setting(context, setting, preset[setting["key"]])


def _selected_preset(context):
    return context.scene.eevee_presets_settings.preset


def _selected_preset_modified(context):
    preset = _load_presets().get(_selected_preset(context), {})
    current = _capture_scene_settings(context)

    for key, saved_value in preset.items():
        if key in current and current[key] != saved_value:
            return True

    return False


class EEVEE_PRESETS_AddonPreferences(AddonPreferences):
    bl_idname = __name__

    presets_json: StringProperty(
        name="Saved Presets",
        default="{}",
        options={"HIDDEN"},
    )

    preset_names_json: StringProperty(
        name="Preset Names",
        default="{}",
        options={"HIDDEN"},
    )

    def draw(self, context):
        layout = self.layout
        layout.label(text="Optional preset shortcuts are available in Preferences > Keymap > Add-ons > Eevee Presets.")
        layout.label(text="Enable and edit Load Performance Preset, Load Quality Preset, or Load User Preset there.")


class EEVEE_PRESETS_Settings(PropertyGroup):
    preset: EnumProperty(
        name="Preset",
        description="Choose which Eevee preset to save or load",
        items=PRESET_ITEMS,
        default="PERFORMANCE",
    )


class EEVEE_PRESETS_OT_save(Operator):
    bl_idname = "eevee_presets.save"
    bl_label = "Save Preset"
    bl_description = "Review and save the current Eevee settings into the selected preset"

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(
            self,
            width=520,
            confirm_text="Save",
        )

    def execute(self, context):
        preset_id = _selected_preset(context)
        presets = _load_presets()
        presets[preset_id] = _capture_scene_settings(context)
        _save_presets(presets)
        _save_user_preferences()

        self.report({"INFO"}, f"Saved {_preset_name(preset_id)} Eevee preset")
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        preset_id = _selected_preset(context)
        saved = _load_presets().get(preset_id, {})
        current = _capture_scene_settings(context)

        layout.label(text=f"Save {_preset_name(preset_id)} preset?")
        layout.separator()

        for setting in SETTINGS:
            key = setting["key"]
            old_exists = key in saved
            old_value = saved.get(key)
            new_value = current[key]
            changed = (not old_exists) or old_value != new_value

            box = layout.box()
            row = box.row()
            row.alert = changed
            row.enabled = changed
            row.label(text=setting["label"])
            row.label(text=f"{_display_value(old_value) if old_exists else 'Not saved'} -> {_display_value(new_value)}")

class EEVEE_PRESETS_OT_load_preset_base(Operator):
    bl_description = "Load an Eevee preset into the current scene"

    preset = ""

    def execute(self, context):
        preset_id = self.preset
        if context.scene.eevee_presets_settings.preset == preset_id:
            self.report({"INFO"}, f"{_preset_name(preset_id)} Eevee preset is already active")
            return {"CANCELLED"}

        context.scene.eevee_presets_settings.preset = preset_id
        presets = _load_presets()
        preset = presets.get(preset_id)

        if not preset:
            self.report({"WARNING"}, "No saved settings found for this preset")
            return {"CANCELLED"}

        _apply_scene_settings(context, preset)
        self.report({"INFO"}, f"Loaded {_preset_name(preset_id)} Eevee preset")
        return {"FINISHED"}


class EEVEE_PRESETS_OT_load_performance(EEVEE_PRESETS_OT_load_preset_base):
    bl_idname = "eevee_presets.load_performance"
    bl_label = "Load Performance Preset"
    preset = "PERFORMANCE"


class EEVEE_PRESETS_OT_load_quality(EEVEE_PRESETS_OT_load_preset_base):
    bl_idname = "eevee_presets.load_quality"
    bl_label = "Load Quality Preset"
    preset = "QUALITY"


class EEVEE_PRESETS_OT_load_user(EEVEE_PRESETS_OT_load_preset_base):
    bl_idname = "eevee_presets.load_user"
    bl_label = "Load User Preset"
    preset = "USER"


class EEVEE_PRESETS_OT_rename_presets(Operator):
    bl_idname = "eevee_presets.rename_presets"
    bl_label = "Rename Presets"
    bl_description = "Rename the Eevee preset buttons"

    performance_name: StringProperty(name="Performance")
    quality_name: StringProperty(name="Quality")
    user_name: StringProperty(name="User")

    def invoke(self, context, event):
        names = _load_preset_names()
        self.performance_name = names["PERFORMANCE"]
        self.quality_name = names["QUALITY"]
        self.user_name = names["USER"]
        return context.window_manager.invoke_props_dialog(self, width=360)

    def execute(self, context):
        names = {
            "PERFORMANCE": self.performance_name.strip() or DEFAULT_PRESET_NAMES["PERFORMANCE"],
            "QUALITY": self.quality_name.strip() or DEFAULT_PRESET_NAMES["QUALITY"],
            "USER": self.user_name.strip() or DEFAULT_PRESET_NAMES["USER"],
        }
        _save_preset_names(names)
        _save_user_preferences()
        self.report({"INFO"}, "Renamed Eevee presets")
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "performance_name", text="Performance")
        layout.prop(self, "quality_name", text="Quality")
        layout.prop(self, "user_name", text="User")


class EEVEE_PRESETS_OT_export_json(Operator, ExportHelper):
    bl_idname = "eevee_presets.export_json"
    bl_label = "Export Preset"
    bl_description = "Export the active Eevee preset to a JSON file"

    filename_ext = ".json"
    filter_glob: StringProperty(
        default="*.json",
        options={"HIDDEN"},
    )

    def execute(self, context):
        preset_id = _selected_preset(context)
        try:
            with open(self.filepath, "w", encoding="utf-8") as output:
                json.dump(_export_data(preset_id), output, indent=2, sort_keys=True)
                output.write("\n")
        except OSError as error:
            self.report({"ERROR"}, f"Could not export preset: {error}")
            return {"CANCELLED"}

        self.report({"INFO"}, f"Exported {_preset_name(preset_id)} Eevee preset")
        return {"FINISHED"}


class EEVEE_PRESETS_OT_import_json(Operator, ImportHelper):
    bl_idname = "eevee_presets.import_json"
    bl_label = "Import Preset"
    bl_description = "Import a JSON file into the active Eevee preset"

    filename_ext = ".json"
    filter_glob: StringProperty(
        default="*.json",
        options={"HIDDEN"},
    )

    def execute(self, context):
        preset_id = _selected_preset(context)
        try:
            with open(self.filepath, "r", encoding="utf-8") as input_file:
                data = json.load(input_file)
            presets, names = _sanitize_import_data(data, preset_id)
        except (OSError, json.JSONDecodeError, ValueError) as error:
            self.report({"ERROR"}, f"Could not import preset: {error}")
            return {"CANCELLED"}

        _save_presets(presets)
        _save_preset_names(names)
        _save_user_preferences()

        self.report({"INFO"}, f"Imported {_preset_name(preset_id)} Eevee preset")
        return {"FINISHED"}


class EEVEE_PRESETS_PT_render_panel(Panel):
    bl_label = "Eevee Presets"
    bl_idname = "EEVEE_PRESETS_PT_render_panel"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"

    @classmethod
    def poll(cls, context):
        return context.scene is not None and hasattr(context.scene, "eevee")

    def draw(self, context):
        layout = self.layout
        settings = context.scene.eevee_presets_settings
        names = _load_preset_names()

        row = layout.row(align=True)
        row.operator(
            EEVEE_PRESETS_OT_load_performance.bl_idname,
            text=names["PERFORMANCE"],
            depress=settings.preset == "PERFORMANCE",
        )

        row.operator(
            EEVEE_PRESETS_OT_load_quality.bl_idname,
            text=names["QUALITY"],
            depress=settings.preset == "QUALITY",
        )

        row.operator(
            EEVEE_PRESETS_OT_load_user.bl_idname,
            text=names["USER"],
            depress=settings.preset == "USER",
        )

        layout.operator(EEVEE_PRESETS_OT_save.bl_idname, text="Save Preset")

        if _selected_preset_modified(context):
            row = layout.row()
            row.alert = True
            row.alignment = "CENTER"
            row.label(text="Modified from preset", icon="ERROR")


class EEVEE_PRESETS_PT_tools_panel(Panel):
    bl_label = "Tools"
    bl_idname = "EEVEE_PRESETS_PT_tools_panel"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    bl_parent_id = "EEVEE_PRESETS_PT_render_panel"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        return context.scene is not None and hasattr(context.scene, "eevee")

    def draw(self, context):
        layout = self.layout

        layout.operator(EEVEE_PRESETS_OT_rename_presets.bl_idname, text="Rename Presets")

        row = layout.row(align=True)
        row.operator(EEVEE_PRESETS_OT_import_json.bl_idname, text="Import Preset")
        row.operator(EEVEE_PRESETS_OT_export_json.bl_idname, text="Export Preset")


classes = (
    EEVEE_PRESETS_AddonPreferences,
    EEVEE_PRESETS_Settings,
    EEVEE_PRESETS_OT_save,
    EEVEE_PRESETS_OT_load_performance,
    EEVEE_PRESETS_OT_load_quality,
    EEVEE_PRESETS_OT_load_user,
    EEVEE_PRESETS_OT_rename_presets,
    EEVEE_PRESETS_OT_export_json,
    EEVEE_PRESETS_OT_import_json,
    EEVEE_PRESETS_PT_render_panel,
    EEVEE_PRESETS_PT_tools_panel,
)


def register_shortcuts():
    keyconfig = bpy.context.window_manager.keyconfigs.addon
    if not keyconfig:
        return

    keymap = keyconfig.keymaps.new(name="Window", space_type="EMPTY")
    for operator_id, key in SHORTCUTS:
        keymap_item = keymap.keymap_items.new(operator_id, key, "PRESS")
        keymap_item.active = False
        addon_keymaps.append((keymap, keymap_item))


def unregister_shortcuts():
    for keymap, keymap_item in addon_keymaps:
        keymap.keymap_items.remove(keymap_item)

    addon_keymaps.clear()


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.eevee_presets_settings = bpy.props.PointerProperty(type=EEVEE_PRESETS_Settings)
    register_shortcuts()


def unregister():
    unregister_shortcuts()
    del bpy.types.Scene.eevee_presets_settings

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
