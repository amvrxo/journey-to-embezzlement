import pygame
import sys
from pygame import Rect
from todo_list import TodoList
from fidget import Fidget
from template import Template

WIDTH, HEIGHT = 960, 600
FPS = 120

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

class AppContainer:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 22)
        self.font_small = pygame.font.SysFont(None, 18)
        self.apps = {
            "todo": TodoList(0),
            "fidget": Fidget(1),
            "template": Template(2),  # replace with actual app
        }

    def run(self):
        while True:
            dt = self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.on_mouse_down(event.pos)
                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    self.on_mouse_up(event.pos)
                if event.type == pygame.MOUSEMOTION:
                    self.on_mouse_move(event.pos)
                if event.type == pygame.KEYDOWN:
                    self.on_key(event)

            self.draw()

    # ---------------- input handlers ----------------
    def on_mouse_down(self, pos):
        for key in self.apps:
            self.apps[key].on_mouse_down(pos)

    def on_mouse_up(self, pos):
        for key in self.apps:
            self.apps[key].on_mouse_up(pos)

    def on_mouse_move(self, pos):
        for key in self.apps:
            self.apps[key].on_mouse_move(pos)

    def on_key(self, event):
        for key in self.apps:
            self.apps[key].on_key(event)
    
    # ---------------- draw ----------------
    def draw(self):
        self.screen.fill(BLACK)
        for key in self.apps:
            self.apps[key].draw_icon(self.screen)
        for key in self.apps:
            self.apps[key].draw(self.screen)
        pygame.display.flip()

def main():
    pygame.init()
    pygame.display.set_caption("embezzlement")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    app = AppContainer(screen)
    app.run()

if __name__ == "__main__":
    main()
