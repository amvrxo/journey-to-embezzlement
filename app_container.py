# app_container.py
import sys
import pygame
from todo_list import TodoList
from fidget_ting import FidgetTing, WIDTH, HEIGHT, FPS  # removed BG import

BLACK = (0, 0, 0)

class AppContainer:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.apps = {
            "todo": TodoList(),
            "adhd": FidgetTing(),  # "adhd n dat" app
        }

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0  # seconds

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                # Route mouse + keys to every app. Use ONLY (pos) so both TodoList and FidgetTing are happy.
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for app in self.apps.values():
                        if hasattr(app, "on_mouse_down"):
                            app.on_mouse_down(event.pos)

                if event.type == pygame.MOUSEBUTTONUP:
                    for app in self.apps.values():
                        if hasattr(app, "on_mouse_up"):
                            app.on_mouse_up(event.pos)

                if event.type == pygame.MOUSEMOTION:
                    for app in self.apps.values():
                        if hasattr(app, "on_mouse_move"):
                            app.on_mouse_move(event.pos)

                if event.type == pygame.KEYDOWN:
                    for app in self.apps.values():
                        if hasattr(app, "on_key"):
                            app.on_key(event)

            # Per-frame updates (physics, timers, etc.)
            for app in self.apps.values():
                if hasattr(app, "update"):
                    app.update(dt)

            self.draw()

    def draw(self):
        # Main app container background = always black
        self.screen.fill(BLACK)

        # Pass 1: draw icons (or legacy draw for apps without split API)
        for app in self.apps.values():
            if hasattr(app, "draw_icon"):
                app.draw_icon(self.screen)
            elif hasattr(app, "draw"):
                app.draw(self.screen)

        # Pass 2: overlays/windows on top (each window handles its own background)
        for app in self.apps.values():
            if hasattr(app, "draw_overlay"):
                app.draw_overlay(self.screen)

        pygame.display.flip()


def main():
    pygame.init()
    pygame.display.set_caption("embezzlement")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    AppContainer(screen).run()

if __name__ == "__main__":
    main()
