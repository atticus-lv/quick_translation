import os
import bpy

from bpy.utils import previews
from pathlib import Path

G_PV_COLL = dict()
G_ICON_ID = dict()


def register_icon():
    # global G_PV_COLL, G_ICON_ID

    icon_dir = Path(__file__).parent.joinpath('icons')
    icons = []

    for file in os.listdir(str(icon_dir)):
        if file.endswith('.png'):
            icons.append(icon_dir.joinpath(file))
    # 注册
    pcoll = previews.new()

    for icon_path in icons:
        pcoll.load(icon_path.name[:-4], str(icon_path), 'IMAGE')
        G_ICON_ID[icon_path.name[:-4]] = pcoll.get(icon_path.name[:-4]).icon_id

    G_PV_COLL['quick_translate_icon'] = pcoll


def unregister_icon():
    # global G_PV_COLL, G_MAT_ICON_ID

    for pcoll in G_PV_COLL.values():
        previews.remove(pcoll)

    G_PV_COLL.clear()

    G_ICON_ID.clear()


def register():
    register_icon()


def unregister():
    unregister_icon()
