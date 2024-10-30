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
        self.exporter.save_tilemap()
        
    def import_tilemap_from_path(self, path: str, recenter_camera=True) -> None:
        self.import_tools.import_tilemap_from_path(path, recenter_camera=recenter_camera)

    def import_empty_map(self):
        self.import_tools.import_empty_map()
        
    def import_empty_map_ask_save(self):
        self.importer.ask_save_first_empty_tilemap()

    def import_tilemap(self):
        self.importer.import_tilemap()
        


Iie_obj: I_importexport = None

def create_Iie(screen):
    global Iie_obj
    Iie_obj = I_importexport(screen)