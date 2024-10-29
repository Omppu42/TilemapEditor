import os

from . import tilemap_util
from . import import_map
from . import export

import manager


class I_importexport:
    def __init__(self, screen):
        self.exporter = export.Exporter(screen, self)
        self.export_tools = self.exporter.export_tools

        self.importer = import_map.Importer(screen, self)
        self.import_tools = self.importer.import_tools


    def export_tilemap(self):
        self.exporter.start_export_tilemap()

    # TODO: Saving... text in the bottom right of viewport?
    def save_tilemap(self):
        map_name = manager.m_obj.loaded_tilemap
        if map_name is None:
            # Map not saved yet
            self.export_tilemap()
            return

        tilemap_util.delete_tilemap(map_name, move_to_deleted=False)
        self.export_tools.export_tilemap(os.path.basename(map_name))


    def import_tilemap_from_path(self, path: str, recenter_camera=True) -> None:
        # Check that path isn't None and it points to a valid folder
        self.import_tools.import_tilemap_from_path(path, recenter_camera=recenter_camera)


    def import_empty_map(self):
        self.import_tools.import_empty_map()

    def import_tilemap(self):
        self.importer.import_tilemap()
        


Iie_obj: I_importexport = None

def create_Iie(screen):
    global Iie_obj
    Iie_obj = I_importexport(screen)