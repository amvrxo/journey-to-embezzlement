import pygame
import sys
from pygame import Rect
from todo_list import TodoList

WIDTH, HEIGHT = 960, 600
FPS = 120

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (180, 180, 180)
DARK_GRAY = (40, 40, 40)
RED = (200, 32, 32)
RED_H = (255, 64, 64)
TEXT = (220, 220, 220)
CLICK_THRESHOLD = 5  # pixels

ICON_PATH = "notepad-icon.png"

class ToDoApp:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 22)
        self.font_small = pygame.font.SysFont(None, 18)
        self.todo = TodoList()

        # --- icon ---
        self.icon_img = self._load_icon(ICON_PATH)
        self.icon_rect = self.icon_img.get_rect(topleft=(16, 16))
        self.dragging = False
        self.drag_off = (0, 0)
        self.drag_start_pos = None
        self.hover_icon = False

        # --- panel ---
        self.panel_visible = False
        self.panel_rect = Rect(220, 60, 420, 220)

        # input field
        self.input_rect = Rect(self.panel_rect.x + 12, self.panel_rect.y + 12, 300, 28)
        self.add_btn_rect = Rect(self.input_rect.right + 8, self.input_rect.y, 70, 28)
        self.input_active = False
        self.input_text = ""

        # rows start
        self.list_start_y = self.input_rect.bottom + 10

    def _load_icon(self, path):
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

                if event.type == pygame.KEYDOWN and self.panel_visible and self.input_active:
                    self.on_key(event)

            self.draw()

    # ---------------- input handlers ----------------
    def on_mouse_down(self, pos):
        if self.icon_rect.collidepoint(pos):
            # if click without moving -> we will toggle panel on mouse up if short click
            self.dragging = True
            mx, my = pos
            ix, iy = self.icon_rect.topleft
            self.drag_off = (mx - ix, my - iy)
            self.drag_start_pos = pos
        elif self.panel_visible:
            # focus input if clicked in input rect
            if self.input_rect.collidepoint(pos):
                self.input_active = True
            else:
                self.input_active = False

            # add button
            if self.add_btn_rect.collidepoint(pos):
                self._add_task_from_input()

            # task rows click handling
            self._handle_task_click(pos)

    def on_mouse_up(self, pos):
        if self.dragging:
            self.dragging = False
            start_x, start_y = self.drag_start_pos
            end_x, end_y = pos
            distance = ((end_x - start_x) ** 2 + (end_y - start_y) ** 2) ** 0.5
            if distance <= CLICK_THRESHOLD and self.icon_rect.collidepoint(pos):
                # treat as a click
                self.panel_visible = not self.panel_visible

    def on_mouse_move(self, pos):
        self.hover_icon = self.icon_rect.collidepoint(pos)
        if self.dragging and pygame.mouse.get_pressed(num_buttons=3)[0]:
            mx, my = pos
            offx, offy = self.drag_off
            nx, ny = mx - offx, my - offy
            # clamp to screen
            nx = max(0, min(WIDTH - self.icon_rect.width, nx))
            ny = max(0, min(HEIGHT - self.icon_rect.height, ny))
            self.icon_rect.topleft = (nx, ny)

    def on_key(self, event):
        if event.key == pygame.K_RETURN:
            self._add_task_from_input()
        elif event.key == pygame.K_BACKSPACE:
            self.input_text = self.input_text[:-1]
        else:
            # basic ASCII text; ignore control characters
            if event.unicode and event.unicode.isprintable():
                self.input_text += event.unicode

    # ---------------- tasks ----------------
    def _add_task_from_input(self):
        text = self.input_text.strip()
        if not text:
            return
        item = self.todo.add(text)
        self.input_text = ""

    def _handle_task_click(self, pos):
        # iterate rows and see which checkbox or X was hit
        y = self.list_start_y
        for item in list(self.todo.tasks):
            checkbox_rect = Rect(self.panel_rect.x + 12, y + 6, 18, 18)
            text_rect = Rect(checkbox_rect.right + 10, y + 6, self.panel_rect.width - 80, 18)
            del_rect = Rect(self.panel_rect.right - 32, y + 4, 24, 24)

            if checkbox_rect.collidepoint(pos):
                self.todo.toggle_done(item["id"])
                return
            if del_rect.collidepoint(pos):
                self.todo.delete(item["id"])
                return
            y += 30

    # ---------------- draw ----------------
    def draw(self):
        self.screen.fill(BLACK)

        # icon
        self.screen.blit(self.icon_img, self.icon_rect.topleft)

        # hover label
        if self.hover_icon and not self.dragging:
            label = self.font_small.render("todo n dat", True, TEXT)
            lx = self.icon_rect.left
            ly = self.icon_rect.bottom + 2
            self.screen.blit(label, (lx, ly))

        # panel
        if self.panel_visible:
            pygame.draw.rect(self.screen, DARK_GRAY, self.panel_rect, border_radius=6)
            pygame.draw.rect(self.screen, GRAY, self.panel_rect, 1, border_radius=6)

            # input field
            pygame.draw.rect(self.screen, (20,20,20), self.input_rect, border_radius=4)
            pygame.draw.rect(self.screen, GRAY if self.input_active else (90,90,90), self.input_rect, 1, border_radius=4)
            txt_surf = self.font.render(self.input_text or "Add task:", True, TEXT if self.input_text else (120,120,120))
            self.screen.blit(txt_surf, (self.input_rect.x + 8, self.input_rect.y + 6))

            # add button
            pygame.draw.rect(self.screen, (32,32,32), self.add_btn_rect, border_radius=4)
            pygame.draw.rect(self.screen, GRAY, self.add_btn_rect, 1, border_radius=4)
            add_s = self.font.render("Add", True, TEXT)
            ax = self.add_btn_rect.centerx - add_s.get_width()//2
            ay = self.add_btn_rect.centery - add_s.get_height()//2
            self.screen.blit(add_s, (ax, ay))

            # list rows
            y = self.list_start_y
            for item in self.todo.tasks:
                # checkbox
                checkbox_rect = Rect(self.panel_rect.x + 12, y + 6, 18, 18)
                pygame.draw.rect(self.screen, GRAY, checkbox_rect, 1)
                if item.get("done"):
                    inner = checkbox_rect.inflate(-8, -8)
                    pygame.draw.rect(self.screen, WHITE, inner)

                # text
                text_col = (150,150,150) if item.get("done") else TEXT
                text_s = self.font.render(item["text"], True, text_col)
                self.screen.blit(text_s, (checkbox_rect.right + 10, y + 6))

                # delete button
                del_rect = Rect(self.panel_rect.right - 32, y + 4, 24, 24)
                mouse_over_del = del_rect.collidepoint(pygame.mouse.get_pos())
                pygame.draw.rect(self.screen, RED_H if mouse_over_del else RED, del_rect, border_radius=4)
                x_s = self.font.render("X", True, WHITE)
                self.screen.blit(x_s, (del_rect.centerx - x_s.get_width()//2, del_rect.centery - x_s.get_height()//2))

                y += 30

        pygame.display.flip()


def main():
    pygame.init()
    pygame.display.set_caption("embezzlement")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    app = ToDoApp(screen)
    app.run()

if __name__ == "__main__":
    main()
