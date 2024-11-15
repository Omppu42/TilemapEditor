import time, os
import pytest
import threading
import pygame

from tests._constants import *
from tests import _utils as utils
from tests._utils import inject_click_at_pos_events, inject_keydown

import sidebar
import manager
import palette

# TODO: Implement can_run variable to continue straight after process_cycles have finished
# FIXME: Make sure if saving a tilemap with a name 'tests-sVLkGQUpMQokDdScZWsr' nothing bad happens (not in export so maybe a problem?)


class TestsButtons():
    def test_grid_toggle_key(self):
        grid_btn_state = sidebar.s_obj.buttons_dict["GridButton"].is_clicked()
        grid_on_state = manager.m_obj.grid_on

        inject_keydown(pygame.K_g, pygame.KSCAN_G)

        assert grid_btn_state != sidebar.s_obj.buttons_dict["GridButton"].is_clicked(), "Grid button state didn't change"
        assert grid_on_state  != manager.m_obj.grid_on, "Grid on state didn't change"

    def test_grid_toggle_mouse(self):
        btn_pos = sidebar.s_obj.buttons_dict["GridButton"].pos

        grid_btn_state = sidebar.s_obj.buttons_dict["GridButton"].is_clicked()
        grid_on_state = manager.m_obj.grid_on

        inject_click_at_pos_events(LEFT_CLICK, (btn_pos[0] + 10, btn_pos[1] + 10))

        assert grid_btn_state != sidebar.s_obj.buttons_dict["GridButton"].is_clicked(), "Grid button state didn't change"
        assert grid_on_state  != manager.m_obj.grid_on, "Grid on state didn't change"

    def test_tool_buttons(self):
        buttons_binary = sidebar.s_obj.brushes_group.get_pressed_all_binary()
        assert buttons_binary == "100", "Only the brush should be equipped"
        
        inject_keydown(pygame.K_e, pygame.KSCAN_E)
        buttons_binary = sidebar.s_obj.brushes_group.get_pressed_all_binary()
        assert buttons_binary == "010", "Only the eraser should be equipped"

        inject_keydown(pygame.K_o, pygame.KSCAN_O)
        buttons_binary = sidebar.s_obj.brushes_group.get_pressed_all_binary()
        assert buttons_binary == "001", "Only the Color Picker should be equipped"

        inject_keydown(pygame.K_p, pygame.KSCAN_P)
        buttons_binary = sidebar.s_obj.brushes_group.get_pressed_all_binary()
        assert buttons_binary == "100", "Only the brush should be equipped"

    def test_tool_mouse(self):
        brush_pos = sidebar.s_obj.buttons_dict["BrushButton"].pos
        eraser_pos = sidebar.s_obj.buttons_dict["EraserButton"].pos
        colorpick_pos = sidebar.s_obj.buttons_dict["ColorPickButton"].pos

        buttons_binary = sidebar.s_obj.brushes_group.get_pressed_all_binary()
        assert buttons_binary == "100", "Only the brush should be equipped"
        
        inject_click_at_pos_events(LEFT_CLICK, (eraser_pos[0]+10, eraser_pos[1]+10))
        buttons_binary = sidebar.s_obj.brushes_group.get_pressed_all_binary()
        assert buttons_binary == "010", "Only the eraser should be equipped"

        inject_click_at_pos_events(LEFT_CLICK, (colorpick_pos[0]+10, colorpick_pos[1]+10))
        buttons_binary = sidebar.s_obj.brushes_group.get_pressed_all_binary()
        assert buttons_binary == "001", "Only the Color Picker should be equipped"

        inject_click_at_pos_events(LEFT_CLICK, (brush_pos[0]+10, brush_pos[1]+10))
        buttons_binary = sidebar.s_obj.brushes_group.get_pressed_all_binary()
        assert buttons_binary == "100", "Only the brush should be equipped"

    def test_page_turn(self):
        left_pos = sidebar.s_obj.buttons_dict["PageLeftButton"].pos
        right_pos = sidebar.s_obj.buttons_dict["PageRightButton"].pos

        pages = palette.pm_obj.get_total_pages()
        first_page_first_data = palette.pm_obj.get_data_current_page()[0]

        assert pages == 2, "For testing purposes, palette at 'Data\\Palettes\\Palette_tests' must have 2 pages of tiles"
        assert sidebar.s_obj.tiles_page == 0, "In the beginning tiles page should be 0"
        assert first_page_first_data["id"] == 0, "The first tile should be ID 0"

        inject_click_at_pos_events(LEFT_CLICK, (right_pos[0]+10, right_pos[1]+10))

        assert sidebar.s_obj.tiles_page == 1, "After turning page should be one"
        assert palette.pm_obj.get_data_current_page()[0]["id"] != first_page_first_data["id"], "ID Should be different than 0"

        inject_click_at_pos_events(LEFT_CLICK, (left_pos[0]+10, left_pos[1]+10))

        assert sidebar.s_obj.tiles_page == 0, "After turning the page back, the page should be 0"
        assert first_page_first_data["id"] == 0, "After turning back the first tile should be ID 0"
