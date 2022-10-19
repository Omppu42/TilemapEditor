import pygame
pygame.init()

def export_tilemap(ui):
    explanation_dict = create_explanations_dict(ui)
    print(explanation_dict)

    #TODO: EXPORT Tilemap. create list of tile_ids and write them to file. explanations too

def create_explanations_dict(ui) -> dict:
    output = {}
    for i in range(len(ui.tiles_dict)):
        output[i] = ui.tiles_dict[i][0]

    return output