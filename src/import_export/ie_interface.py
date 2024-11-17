import os

from . import tilemap_util
from . import import_map
from . import export

import manager
import palette


class I_importexport:
    def __init__(self, screen):
        self.exporter = export.Exporter(screen, self)
        self.export_tools = self.exporter.export_tools

        self.importer = import_map.Importer(screen, self)
        self.import_tools = self.importer.import_tools


    def export_tilemap(self):
        self.exporter.start_export_tilemap()

    def save_tilemap(self):
        self.exporter.save_tilemap()

    def save_tilemap_quiet(self):
        self.exporter.save_tilemap_quiet()
    
    def import_tilemap_from_path(self, path: str, recenter_camera=True, check_palette_change=True) -> None:
        self.import_tools.import_tilemap_from_path(path, recenter_camera=recenter_camera, check_palette_change=check_palette_change)

    def import_empty_map(self):
        self.import_tools.import_empty_map()
        
    def import_empty_map_ask_save(self, ui_obj):
        if tilemap_util.tilemap_has_changes(manager.m_obj.loaded_tilemap, ui_obj.blocks, ui_obj.grid_size_rows_cols, palette.pm_obj.current_palette.tiles_order):
            self.importer.ask_save_first_empty_tilemap()
            return
        
        self.import_tools.import_empty_map()

    def import_tilemap(self):
        self.importer.import_tilemap()
        


Iie_obj: I_importexport = None

def create_Iie(screen):
    global Iie_obj
    Iie_obj = I_importexport(screen)