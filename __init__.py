bl_info = {
    "name": "Quick Translation",
    "author": "Atticus",
    "version": (0, 1),
    "blender": (2, 83, 0),
    "location": "Topbar",
    "description": "Adds a new Mesh Object",
    "warning": "",
    "doc_url": "",
    "category": "Interface",
}

import bpy

from .icon_utils import RSN_Preview

icon = RSN_Preview('translate.png', 'translate')
icon_bk = RSN_Preview('translate_bk.png', 'translate_bk')


def get_pref():
    return bpy.context.preferences.addons.get(__name__).preferences


def draw(self, context):
    layout = self.layout

    layout.operator('wm.toggle_translation',
                    icon_value=getattr(icon_bk if get_pref().icon_invert else icon, 'icon_value'),
                    text='', emboss=False)
    layout.separator()


class WM_OT_toggle_translation(bpy.types.Operator):
    """Ctrl: Open addon Preference\nShift: Invert Icon Color"""

    bl_label = 'Translation'
    bl_idname = 'wm.toggle_translation'

    def invoke(self, context, event):
        if event.ctrl:
            bpy.ops.preferences.addon_show(module=__name__)
        elif event.shift:
            get_pref().icon_invert = True if get_pref().icon_invert is False else False
        else:
            view = context.preferences.view
            view.use_translate_interface = True if view.use_translate_interface is False else False
            view.use_translate_tooltips = view.use_translate_interface

        return {'FINISHED'}


class QuickTranslatePreference(bpy.types.AddonPreferences):
    bl_idname = __package__

    icon_invert: bpy.props.BoolProperty(name='Invert Icon Color')


def register():
    icon.register()
    icon_bk.register()

    bpy.utils.register_class(WM_OT_toggle_translation)
    bpy.utils.register_class(QuickTranslatePreference)

    bpy.types.TOPBAR_MT_editor_menus.prepend(draw)

    from .translation import auto_translation
    auto_translation.register()

def unregister():
    icon.unregister()
    icon_bk.unregister()

    bpy.utils.unregister_class(WM_OT_toggle_translation)
    bpy.utils.unregister_class(QuickTranslatePreference)

    bpy.types.TOPBAR_MT_editor_menus.remove(draw)

    from .translation import auto_translation
    auto_translation.unregister()

if __name__ == '__main__':
    register()
