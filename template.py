import pygame
from utils import load_icon
from pygame import Rect

WIDTH, HEIGHT = 960, 600
TEXT = (220, 220, 220)
GRAY = (180, 180, 180)
DARK_GRAY = (40, 40, 40)
CLICK_THRESHOLD = 5

class Template:
    def __init__(self, app_number):
        self.icon_img = load_icon("new_app.png")
        self.icon_rect = self.icon_img.get_rect(topleft=(16 + 80 * app_number, 16))
        self.dragging = False
        self.drag_off = (0, 0)
        self.drag_start_pos = None
        self.hover_icon = False
        self.should_draw = False
        self.panel_rect = Rect(220, 60, 420, 220)
        self.margin_rect = Rect(220, 60, 420, 20)
        self.font = pygame.font.SysFont(None, 22)
        self.font_small = pygame.font.SysFont(None, 18)
        self.dragging_obj = None

    def on_mouse_down(self, pos):
        if self.icon_rect.collidepoint(pos):
            # if click without moving -> we will toggle panel on mouse up if short click
            self.dragging = True
            self.dragging_obj = 'icon'
            mx, my = pos
            ix, iy = self.icon_rect.topleft
            self.drag_off = (mx - ix, my - iy)
            self.drag_start_pos = pos
        elif self.should_draw:
            if self.margin_rect.collidepoint(pos):
                self.dragging = True
                self.dragging_obj = 'margin'
                mx, my = pos
                ix, iy = self.margin_rect.topleft
                self.drag_off = (mx - ix, my - iy)
                self.drag_start_pos = pos

    def on_mouse_up(self, pos):
        if self.dragging:
            self.dragging = False
            start_x, start_y = self.drag_start_pos
            end_x, end_y = pos
            distance = ((end_x - start_x) ** 2 + (end_y - start_y) ** 2) ** 0.5
            if distance <= CLICK_THRESHOLD and self.icon_rect.collidepoint(pos):
                self.should_draw = not self.should_draw

    def on_mouse_move(self, pos):
        self.hover_icon = self.icon_rect.collidepoint(pos)
        if self.dragging and pygame.mouse.get_pressed(num_buttons=3)[0]:
            mx, my = pos
            offx, offy = self.drag_off
            nx, ny = mx - offx, my - offy
            if self.dragging_obj == 'icon':
                nx = max(0, min(WIDTH - self.icon_rect.width, nx))
                ny = max(0, min(HEIGHT - self.icon_rect.height, ny))
                self.icon_rect.topleft = (nx, ny)
            elif self.dragging_obj == 'margin':
                nx = max(0, min(WIDTH - self.margin_rect.width, nx))
                ny = max(0, min(HEIGHT - self.margin_rect.height, ny))
                self.panel_rect.topleft = (nx, ny)
                self.margin_rect.topleft = (nx, ny)

    def on_key(self, event):
        # Handle key events
        pass

    def draw_icon(self, screen):
        screen.blit(self.icon_img, self.icon_rect.topleft)

        if self.hover_icon and not self.dragging:
            label = self.font_small.render("new app n dat", True, TEXT)
            lx = self.icon_rect.left
            ly = self.icon_rect.bottom + 2
            screen.blit(label, (lx, ly))


    def draw(self, screen):
        if self.should_draw:
            pygame.draw.rect(screen, DARK_GRAY, self.panel_rect, border_radius=6)
            pygame.draw.rect(screen, GRAY, self.panel_rect, 1, border_radius=6)
            pygame.draw.rect(screen, TEXT, self.margin_rect, border_top_left_radius=6, border_top_right_radius=6)