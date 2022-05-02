bl_info = {
    "name": "Quick Translation",
    "author": "Atticus",
    "version": (0, 2),
    "blender": (2, 83, 0),
    "location": "Panels",
    "description": "Add Quick Translation Button",
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


def draw_end_separator(self, context):
    layout = self.layout

    layout.operator('wm.toggle_translation',
                    icon_value=getattr(icon_bk if get_pref().icon_invert else icon, 'icon_value'),
                    text='', emboss=False)
    layout.separator()


def draw_end_norm(self, context):
    layout = self.layout

    layout.operator('wm.toggle_translation',
                    icon_value=getattr(icon_bk if get_pref().icon_invert else icon, 'icon_value'),
                    text='', emboss=False)


def update_visual_settings(menu, attr, drawing_func, unregister=False):
    if unregister:
        try:
            menu.remove(drawing_func)
        except Exception as e:
            print('Already removed')
        return

    show = getattr(get_pref(), attr)
    if not show:
        try:
            menu.remove(drawing_func)
        except Exception as e:
            print('Already removed')
    else:
        try:
            menu.remove(drawing_func)
        except Exception as e:
            print('Already removed')
        menu.prepend(drawing_func)


d_list = [
    {
        'menu': bpy.types.TOPBAR_MT_editor_menus,
        'attr': 'topbar',
        'drawing_func': draw_end_separator
    },
    {
        'menu': bpy.types.NODE_HT_header,
        'attr': 'node_header',
        'drawing_func': draw_end_norm
    },
    {
        'menu': bpy.types.PROPERTIES_HT_header,
        'attr': 'properties_header',
        'drawing_func': draw_end_norm
    },
    {
        'menu': bpy.types.VIEW3D_HT_header,
        'attr': 'view3d_header',
        'drawing_func': draw_end_norm
    }
]


def update_icons(self, context):
    for d in d_list:
        update_visual_settings(d['menu'], d['attr'], d['drawing_func'])


class QuickTranslatePreference(bpy.types.AddonPreferences):
    bl_idname = __package__

    icon_invert: bpy.props.BoolProperty(name='Invert Icon Color')

    topbar: bpy.props.BoolProperty(name='Workspace', default=True, update=update_icons)
    node_header: bpy.props.BoolProperty(name='Shader Editor', default=True,
                                        update=update_icons)
    properties_header: bpy.props.BoolProperty(name='Properties', default=True,
                                              update=update_icons)
    view3d_header: bpy.props.BoolProperty(name='3D Viewport', default=False, update=update_icons)

    def draw(self, context):
        layout = self.layout
        split = layout.split(factor=0.5)
        box = split.box()

        box.label(text='Settings')
        row = box.row()
        row.label(text='', icon='ARROW_LEFTRIGHT')
        row.prop(self, 'icon_invert')

        col = box.column()

        row = col.row()
        row.label(text='', icon='BLENDER')
        row.prop(self, 'topbar')

        row = col.row()
        row.label(text='', icon='NODETREE')
        row.prop(self, 'node_header')

        row = col.row()
        row.label(text='', icon='PROPERTIES')
        row.prop(self, 'properties_header')

        row = col.row()
        row.label(text='', icon='VIEW3D')
        row.prop(self, 'view3d_header')

        box = split.box()
        box.label(text='Style')

        col = box.column()
        col.scale_y = 1.75
        col.scale_x = 1.5

        row = col.row(align=True)
        row.alignment = 'CENTER'

        row.separator()
        row.box().operator('wm.toggle_translation',
                           icon_value=getattr(icon_bk if get_pref().icon_invert else icon, 'icon_value'),
                           text='', emboss=True)
        row.separator()
        row.box().operator('wm.toggle_translation',
                           icon_value=getattr(icon_bk if get_pref().icon_invert else icon, 'icon_value'),
                           text='', emboss=False)
        row.separator()


def init_visual_settings(unregister=False):
    for d in d_list:
        update_visual_settings(d['menu'], d['attr'], d['drawing_func'],unregister)


def register():
    icon.register()
    icon_bk.register()

    bpy.utils.register_class(WM_OT_toggle_translation)
    bpy.utils.register_class(QuickTranslatePreference)

    from .translation import auto_translation
    auto_translation.register()

    init_visual_settings()


def unregister():
    icon.unregister()
    icon_bk.unregister()

    bpy.utils.unregister_class(WM_OT_toggle_translation)
    bpy.utils.unregister_class(QuickTranslatePreference)

    from .translation import auto_translation
    auto_translation.unregister()

    init_visual_settings(unregister=True)


if __name__ == '__main__':
    register()
