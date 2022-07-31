import os.path

bl_info = {
    "name": "Quick Translation",
    "author": "Atticus",
    "version": (0, 3),
    "blender": (2, 83, 0),
    "location": "Panels",
    "description": "Quick translation button & Custom file / 快速翻译按钮 & 自定义文件",
    "warning": "",
    "doc_url": "",
    "category": "Interface",
}

import bpy
import json
import csv
from pathlib import Path

from bpy.props import (BoolProperty,
                       StringProperty,
                       EnumProperty,
                       IntProperty,
                       FloatProperty,
                       CollectionProperty)

# register icon
from .icon_utils import G_ICON_ID

icon_utils.register()

icon = G_ICON_ID['translate']
icon_bk = G_ICON_ID['translate_bk']


def get_pref():
    return bpy.context.preferences.addons.get(__name__).preferences


# main operator
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


# ui append
def draw_end_separator(self, context):
    layout = self.layout

    layout.operator('wm.toggle_translation',
                    icon_value=icon_bk if get_pref().icon_invert else icon,
                    text='', emboss=False)
    layout.separator()


def draw_end_norm(self, context):
    layout = self.layout

    layout.operator('wm.toggle_translation',
                    icon_value=icon_bk if get_pref().icon_invert else icon,
                    text='', emboss=False)


# update ui append/remove
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

C_custom_translate = {}


def update_icons(self, context):
    for d in d_list:
        update_visual_settings(d['menu'], d['attr'], d['drawing_func'])


# custom translation register
def register_translation(self, context):
    global C_custom_translate
    from .translation.__init__ import TranslationHelper

    def get_path():
        return self.filepath if Path(self.filepath).exists() else None

    path = get_path()
    if not path: return

    encoding = self.encoding
    if encoding == 'CUSTOM':
        encoding = self.custom_encoding

    self.error_msg = ''

    if self.type == 'JSON' and path.endswith('.json'):

        with open(path, encoding=encoding) as f:
            try:
                d = json.load(f)
                help_cls = TranslationHelper(self.name, d, lang=self.lang)

                # update the enabled languages
                if self.enable:
                    if self.name in C_custom_translate:
                        help_cls.unregister()
                        C_custom_translate[self.name] = help_cls

                    help_cls.register()
                    C_custom_translate[self.name] = help_cls

                else:
                    help_cls.unregister()

            except Exception:
                # load file in error encoding with unregister the origin one
                if self.name in C_custom_translate:
                    help_cls = C_custom_translate[self.name]
                    help_cls.unregister()



    elif self.type == 'CSV' and path.endswith('.csv'):
        with open(path, encoding=encoding) as f:
            try:
                c = csv.reader(f)
                d = {}

                for row in c:
                    if len(row) != 2: continue
                    d[row[0]] = row[1]

                help_cls = TranslationHelper(self.name, d, lang=self.lang)

                if self.enable:
                    if self.name in C_custom_translate:
                        help_cls.unregister()
                        C_custom_translate[self.name] = help_cls

                    help_cls.register()
                    C_custom_translate[self.name] = help_cls

                else:
                    help_cls.unregister()

            except Exception:
                if self.name in C_custom_translate:
                    help_cls = C_custom_translate[self.name]
                    help_cls.unregister()


# set and get name -> register/unregister
def get_name(self):
    return self['name']


def check_name(self, value):
    if value in C_custom_translate:
        C_custom_translate[value].unregister()

    self.name = value


# custom translation props
class CustomTranslation(bpy.types.PropertyGroup):
    name: StringProperty(name='Name', default='', get=get_name, set=check_name)
    lang: EnumProperty(name='Language', items=sorted([(l, l, '') for l in bpy.app.translations.locales]),
                       default='zh_CN',
                       update=register_translation)
    enable: BoolProperty(name='Enable', default=True, update=register_translation)

    filepath: StringProperty(name='File Path', default='', subtype='FILE_PATH', update=register_translation)
    type: EnumProperty(name='File Type', items=[('JSON', 'JSON', ''), ('CSV', 'CSV', '')], default='JSON')
    encoding: EnumProperty(name='File Encoding',
                           items=[('utf-8', 'utf-8', ''), ('ascii', 'ascii', ''), ('gbk', 'gbk', ''),
                                  ('gb2312', 'gb2312', ''), ('CUSTOM', 'Custom', '')], default='utf-8',
                           update=register_translation)
    custom_encoding: StringProperty(name='Custom Encoding', default='utf-8', update=register_translation)

    error_msg: StringProperty(name='Error', default='')


# add / remove custom translation operator
class WM_OT_add_custom_translation(bpy.types.Operator):
    """Add Custom Translation"""

    bl_label = 'Add'
    bl_idname = 'wm.add_custom_translation'

    def invoke(self, context, event):
        custom_translations = get_pref().custom_translations
        item = custom_translations.add()
        item.name = 'Translation' + str(len(custom_translations))
        return {'FINISHED'}


class WM_OT_remove_custom_translation(bpy.types.Operator):
    """Remove Custom Translation"""

    bl_label = 'Remove'
    bl_idname = 'wm.remove_custom_translation'

    index: IntProperty(name='Index', default=0)

    def execute(self, context):
        global C_custom_translate
        custom_translations = get_pref().custom_translations
        C_custom_translate[custom_translations[self.index].name].unregister()
        custom_translations.remove(self.index)

        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)


class QuickTranslatePreference(bpy.types.AddonPreferences):
    bl_idname = __package__

    # ui
    tab: EnumProperty(items=[('SETTINGS', 'Settings', ''), ('CUSTOM', 'Custom', '')], default='SETTINGS')
    # settings
    icon_invert: bpy.props.BoolProperty(name='Invert Icon Color')

    topbar: bpy.props.BoolProperty(name='Workspace', default=True, update=update_icons)
    node_header: bpy.props.BoolProperty(name='Shader Editor', default=True,
                                        update=update_icons)
    properties_header: bpy.props.BoolProperty(name='Properties', default=True,
                                              update=update_icons)
    view3d_header: bpy.props.BoolProperty(name='3D Viewport', default=False, update=update_icons)

    # custom
    custom_translations: CollectionProperty(name='Custom Translations', type=CustomTranslation)

    def draw(self, context):
        layout = self.layout

        row = layout.row(align=True)
        row.prop(self, 'tab', expand=True)

        if self.tab == 'SETTINGS':
            self.draw_settings(context, layout)
        elif self.tab == 'CUSTOM':
            self.draw_custom_list(context, layout)

    def draw_settings(self, context, layout):
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
                           icon_value=icon_bk if get_pref().icon_invert else icon,
                           text='', emboss=True)
        row.separator()
        row.box().operator('wm.toggle_translation',
                           icon_value=icon_bk if get_pref().icon_invert else icon,
                           text='', emboss=False)
        row.separator()

    def draw_custom_list(self, context, layout):
        col = layout.column()
        col.alert = True
        col.label(text='Test Me')

        col = layout.column()
        col.label(text='Custom Translation', icon_value=icon_bk if get_pref().icon_invert else icon)
        # draw custom translations

        for i, item in enumerate(self.custom_translations):
            box = col.box()

            row = box.row()
            row.prop(item, 'name', text='')
            row.prop(item, 'lang')
            row.prop(item, 'enable')

            d = row.row()
            d.alert = True
            d.operator('wm.remove_custom_translation', icon='X', text='').index = i

            file_box = box.box().column()
            file_box.use_property_split = True
            file_box.use_property_decorate = False

            file_box.prop(item, 'filepath', text='')

            file_box.separator(factor=0.5)

            if os.path.exists(item.filepath):
                file_box.prop(item, 'type')
                file_box.separator(factor=0.5)

                row = file_box.row()
                row.prop(item, 'encoding')
                if item.encoding == 'CUSTOM':
                    row.prop(item, 'custom_encoding', text='')
            else:
                row = file_box.column()
                row.alert = True
                row.label(text='File Not Found')

        col.separator()
        col.operator('wm.add_custom_translation', icon='ADD')


# init the addon ui
def init_visual_settings(unregister=False):
    for d in d_list:
        update_visual_settings(d['menu'], d['attr'], d['drawing_func'], unregister)

    for item in get_pref().custom_translations:
        register_translation(item, bpy.context)
    # global register
    for cls in C_custom_translate.values():
        if not unregister:
            cls.register()
        else:
            cls.unregister()


def register():
    from . import translation

    bpy.utils.register_class(WM_OT_toggle_translation)
    bpy.utils.register_class(WM_OT_add_custom_translation)
    bpy.utils.register_class(WM_OT_remove_custom_translation)
    bpy.utils.register_class(CustomTranslation)
    bpy.utils.register_class(QuickTranslatePreference)

    translation.register()

    init_visual_settings()


def unregister():
    bpy.utils.unregister_class(WM_OT_toggle_translation)
    bpy.utils.unregister_class(WM_OT_add_custom_translation)
    bpy.utils.unregister_class(WM_OT_remove_custom_translation)
    bpy.utils.unregister_class(QuickTranslatePreference)
    bpy.utils.unregister_class(CustomTranslation)

    from . import icon_utils, translation
    translation.unregister()
    icon_utils.unregister()

    init_visual_settings(unregister=True)


if __name__ == '__main__':
    register()
