import pygame
pygame.init()

def load_sprites(folder, sprite_name, sprite_count, image_extension, img_size: tuple, sprite_count_start=None) -> list:
    sprites = []
    sprite_path = folder+sprite_name

    if sprite_count_start is None:
        for i in range(sprite_count):
            sprites.append(generate_sprite(i, sprite_path, image_extension, img_size))
    else: 
        for i in range(sprite_count_start, sprite_count):
            sprites.append(generate_sprite(i, sprite_path, image_extension, img_size))

    return sprites


def generate_sprite(i, path, extension, img_size):
        sprite = pygame.image.load(path+str(i)+extension)
        sprite = pygame.transform.scale(sprite, img_size)
        return sprite