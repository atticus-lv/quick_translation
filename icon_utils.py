import os
import bpy

from bpy.utils import previews

icons_dir = os.path.join(os.path.dirname(__file__), "icons")


class RSN_Preview():
    def __init__(self, image, name):
        self.preview_collections = {}
        self.image = os.path.join(icons_dir, image)
        self.name = name

    def register(self):
        pcoll = previews.new()
        pcoll.load(self.name, self.image, 'IMAGE')
        self.preview_collections["qt_icon"] = pcoll

    def unregister(self):
        for pcoll in self.preview_collections.values():
            previews.remove(pcoll)
        self.preview_collections.clear()

    @property
    def icon_value(self):
        image = self.preview_collections["qt_icon"][self.name]
        return image.icon_id
