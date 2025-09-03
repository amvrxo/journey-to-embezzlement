import pygame
from pygame import Rect

GRAY = (180, 180, 180)

def load_icon(path):
    try:
        img = pygame.image.load(path).convert_alpha()
    except Exception as e:
        # placeholder 64x64
        img = pygame.Surface((64, 64), pygame.SRCALPHA)
        img.fill((0,0,0,0))
        pygame.draw.rect(img, GRAY, img.get_rect(), border_radius=10, width=2)
        pygame.draw.rect(img, GRAY, Rect(14,10,36,44), width=2, border_radius=4)
        for y in range(16, 50, 8):
            pygame.draw.line(img, GRAY, (18,y), (46,y), 1)
    return img