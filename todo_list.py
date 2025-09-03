# todo_list.py
import pygame
from pygame import Rect

# Canvas / timing (container may override, but we keep sensible defaults)
WIDTH, HEIGHT = 960, 600
FPS = 120

# Colors
WHITE = (255, 255, 255)
TEXT = (220, 220, 220)
GRAY = (180, 180, 180)
OUTLINE = (70, 70, 70)
DARK = (32, 32, 32)
DARK_PANEL = (28, 28, 28)
RED = (200, 32, 32)
RED_H = (255, 64, 64)

CLICK_THRESHOLD = 5

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

class _BaseWindow:
    TITLE_H = 28
    RADIUS = 8
    BORDER = 1
    RESIZE_PAD = 14
    MIN_W, MIN_H = 280, 180

    def __init__(self, rect: Rect, title: str, font, font_small, on_close):
        self.rect = Rect(rect)
        self.title = title
        self.font = font
        self.font_small = font_small
        self.on_close = on_close

        self._drag_title = False
        self._drag_off = (0, 0)
        self._resizing = False
        self._resize_start = (0, 0, 0, 0)
        self._hover_close = False
        self._close_rect = Rect(0, 0, self.TITLE_H - 8, self.TITLE_H - 8)

    @property
    def client(self) -> Rect:
        r = self.rect.copy()
        r.y += self.TITLE_H
        r.h -= self.TITLE_H
        return r

    def _update_close_rect(self):
        self._close_rect.size = (self.TITLE_H - 8, self.TITLE_H - 8)
        self._close_rect.x = self.rect.right - self._close_rect.w - 6
        self._close_rect.y = self.rect.y + (self.TITLE_H - self._close_rect.h) // 2

    # -------- events for window frame --------
    def handle_mouse_down(self, pos, button=1):
        if not self.rect.collidepoint(pos) or button != 1:
            return False
        self._update_close_rect()

        if self._close_rect.collidepoint(pos):
            # Close immediately; caller must not use window after this.
            self.on_close()
            return True

        # resize bottom-right corner
        rh = Rect(self.rect.right - self.RESIZE_PAD, self.rect.bottom - self.RESIZE_PAD,
                  self.RESIZE_PAD, self.RESIZE_PAD)
        if rh.collidepoint(pos):
            self._resizing = True
            self._resize_start = (pos[0], pos[1], self.rect.w, self.rect.h)
            return True

        # title drag
        title_bar = Rect(self.rect.x, self.rect.y, self.rect.w, self.TITLE_H)
        if title_bar.collidepoint(pos):
            self._drag_title = True
            self._drag_off = (pos[0] - self.rect.x, pos[1] - self.rect.y)
            return True

        # inside client area: delegate
        if self.client.collidepoint(pos):
            return self.on_client_mouse_down(pos, button)

        return True

    def handle_mouse_up(self, pos, button=1):
        self._drag_title = False
        self._resizing = False
        self.on_client_mouse_up(pos, button)

    def handle_mouse_move(self, pos, buttons):
        self._update_close_rect()
        self._hover_close = self._close_rect.collidepoint(pos)

        if self._drag_title and buttons[0]:
            nx = clamp(pos[0] - self._drag_off[0], 0, WIDTH - self.rect.w)
            ny = clamp(pos[1] - self._drag_off[1], 0, HEIGHT - self.rect.h)
            self.rect.topleft = (nx, ny)
            self.on_moved(0, 0)  # hook if children need notification

        if self._resizing and buttons[0]:
            sx, sy, sw, sh = self._resize_start
            nw = clamp(sw + (pos[0] - sx), self.MIN_W, WIDTH - self.rect.x)
            nh = clamp(sh + (pos[1] - sy), self.MIN_H, HEIGHT - self.rect.y)
            old_client = self.client.copy()
            self.rect.size = (nw, nh)
            self.on_resized(old_client, self.client.copy())

        self.on_client_mouse_move(pos, buttons)

    # -------- overridable client hooks --------
    def on_moved(self, dx, dy): pass
    def on_resized(self, old_client: Rect, new_client: Rect): pass
    def on_client_mouse_down(self, pos, button): return False
    def on_client_mouse_up(self, pos, button): pass
    def on_client_mouse_move(self, pos, buttons): pass
    def on_client_key(self, e): pass

    # -------- drawing --------
    def draw_frame(self, screen):
        # window body + border
        pygame.draw.rect(screen, DARK, self.rect, border_radius=self.RADIUS)
        pygame.draw.rect(screen, OUTLINE, self.rect, self.BORDER, border_radius=self.RADIUS)
        # title bar
        title_r = Rect(self.rect.x, self.rect.y, self.rect.w, self.TITLE_H)
        pygame.draw.rect(screen, (40, 40, 40), title_r, border_radius=self.RADIUS)
        pygame.draw.line(screen, OUTLINE, (self.rect.x, self.rect.y + self.TITLE_H),
                         (self.rect.right, self.rect.y + self.TITLE_H))
        # title text
        ts = self.font.render(self.title, True, TEXT)
        screen.blit(ts, (self.rect.x + 10, self.rect.y + (self.TITLE_H - ts.get_height()) // 2))
        # close button
        self._update_close_rect()
        pygame.draw.rect(screen, RED_H if self._hover_close else RED, self._close_rect, border_radius=6)
        x_txt = self.font_small.render("X", True, WHITE)
        screen.blit(x_txt, (self._close_rect.centerx - x_txt.get_width() // 2,
                            self._close_rect.centery - x_txt.get_height() // 2))
        # resize handle square
        rh = Rect(self.rect.right - 14, self.rect.bottom - 14, 14, 14)
        pygame.draw.rect(screen, (70, 70, 70), rh)
        pygame.draw.rect(screen, (110, 110, 110), rh, 1)



class TodoList:
    def __init__(self):
        self._next_id = 1
        self.icon_img = self._load_icon("notepad-icon.png")
        self.icon_rect = self.icon_img.get_rect(topleft=(16, 16))
        self.hover_icon = False
        self._drag_icon = False
        self._drag_off_icon = (0, 0)
        self._drag_start_icon = (0, 0)

        self.tasks = []
        self.input_text = ""
        self.input_active = False

        self.font = pygame.font.SysFont(None, 22)
        self.font_small = pygame.font.SysFont(None, 18)

        # Window state
        self.window = None   # instance of _TodoWindow when open
        self.should_draw = False

    # ---------- icon ----------
    def _load_icon(self, path):
        try:
            return pygame.image.load(path).convert_alpha()
        except Exception:
            img = pygame.Surface((64, 64), pygame.SRCALPHA)
            pygame.draw.rect(img, GRAY, img.get_rect(), border_radius=10, width=2)
            pygame.draw.rect(img, GRAY, Rect(14, 10, 36, 44), width=2, border_radius=4)
            for y in range(16, 50, 8):
                pygame.draw.line(img, GRAY, (18, y), (46, y), 1)
            return img

    # ---------- public API ----------
    def add(self, text: str):
        item = {"id": self._next_id, "text": text, "done": False}
        self._next_id += 1
        self.tasks.append(item)
        return item

    def toggle_done(self, tid: int):
        for t in self.tasks:
            if t["id"] == tid:
                t["done"] = not t["done"]
                return t["done"]
        return None

    def delete(self, tid: int):
        self.tasks = [t for t in self.tasks if t["id"] != tid]

    # ---------- window lifecycle ----------
    def _open_window(self):
        if not self.window:
            rect = Rect(220, 60, 460, 280)
            self.window = _TodoWindow(rect, "todo n dat", self.font, self.font_small,
                                      on_close=self._close_window, owner=self)

    def _close_window(self):
        self.should_draw = False
        self.window = None
        self.input_active = False

    # ---------- input helpers ----------
    def _add_task_from_input(self):
        text = self.input_text.strip()
        if text:
            self.add(text)
            self.input_text = ""

    # ---------- event routing ----------
    def on_mouse_down(self, pos):
        # icon first
        if self.icon_rect.collidepoint(pos):
            self._drag_icon = True
            ix, iy = self.icon_rect.topleft
            self._drag_off_icon = (pos[0] - ix, pos[1] - iy)
            self._drag_start_icon = pos
            return

        if not self.should_draw or not self.window:
            return

        # Let the window handle frame/client clicks (may close itself)
        self.window.handle_mouse_down(pos, 1)

    def on_mouse_up(self, pos):
        if self._drag_icon:
            self._drag_icon = False
            sx, sy = self._drag_start_icon
            dx, dy = pos[0] - sx, pos[1] - sy
            if (dx*dx + dy*dy) ** 0.5 <= CLICK_THRESHOLD and self.icon_rect.collidepoint(pos):
                # toggle window
                self.should_draw = not self.should_draw
                if self.should_draw:
                    self._open_window()
                else:
                    self._close_window()
            return

        if not self.should_draw or not self.window:
            return
        self.window.handle_mouse_up(pos, 1)

    def on_mouse_move(self, pos):
        self.hover_icon = self.icon_rect.collidepoint(pos)
        if self._drag_icon and pygame.mouse.get_pressed(num_buttons=3)[0]:
            nx = clamp(pos[0] - self._drag_off_icon[0], 0, WIDTH - self.icon_rect.width)
            ny = clamp(pos[1] - self._drag_off_icon[1], 0, HEIGHT - self.icon_rect.height)
            self.icon_rect.topleft = (nx, ny)

        if not self.should_draw or not self.window:
            return
        buttons = pygame.mouse.get_pressed(num_buttons=3)
        self.window.handle_mouse_move(pos, buttons)

    def on_key(self, event):
        # send text input only when the window input is focused
        if self.input_active and event.key == pygame.K_RETURN:
            self._add_task_from_input()
            return
        if self.input_active and event.key == pygame.K_BACKSPACE:
            self.input_text = self.input_text[:-1]
            return
        if self.input_active and event.unicode and event.unicode.isprintable():
            self.input_text += event.unicode

    # ---------- draw ----------
    def draw(self, screen):
        # draw icon first
        screen.blit(self.icon_img, self.icon_rect.topleft)
        if self.hover_icon and not self._drag_icon:
            hint = self.font_small.render("todo n dat", True, TEXT)
            screen.blit(hint, (self.icon_rect.left, self.icon_rect.bottom + 2))

        # draw window last (so it sits above icons)
        if self.should_draw and self.window:
            self.window.draw(screen)


class _TodoWindow(_BaseWindow):
    def __init__(self, rect, title, font, font_small, on_close, owner: TodoList):
        super().__init__(rect, title, font, font_small, on_close)
        self.owner = owner

        # Layout offsets relative to client area
        self.input_off = Rect(12, 12, 300, 28)
        self.add_off = Rect(self.input_off.right + 8, self.input_off.y, 70, 28)
        self.list_top_off = self.input_off.bottom + 10

        # Absolute rects (computed each draw from offsets)
        self.input_abs = Rect(0, 0, 0, 0)
        self.add_abs = Rect(0, 0, 0, 0)

    # ---------- client event handlers ----------
    def on_client_mouse_down(self, pos, button):
        c = self.client
        self._place_abs(c)

        # focus input
        if self.input_abs.collidepoint(pos):
            self.owner.input_active = True
        else:
            self.owner.input_active = False

        # add button
        if self.add_abs.collidepoint(pos):
            self.owner._add_task_from_input()
            return True

        # task rows click handling
        y = c.y + self.list_top_off
        for item in list(self.owner.tasks):
            checkbox = Rect(c.x + 12, y + 6, 18, 18)
            del_rect = Rect(c.right - 32, y + 4, 24, 24)
            if checkbox.collidepoint(pos):
                self.owner.toggle_done(item["id"])
                return True
            if del_rect.collidepoint(pos):
                self.owner.delete(item["id"])
                return True
            y += 30

        return False

    def on_client_mouse_up(self, pos, button): pass
    def on_client_mouse_move(self, pos, buttons): pass
    def on_client_key(self, e): pass
    def on_moved(self, dx, dy): pass

    def on_resized(self, old_client: Rect, new_client: Rect):
        # Keep input inside new client; widths recomputed in draw
        self.input_off.x = clamp(self.input_off.x, 12, max(12, new_client.w - 12 - 8 - 70 - 12))
        # list area adapts implicitly by reading client each draw

    def _place_abs(self, client_rect: Rect):
        # responsive input width
        avail_w = max(160, client_rect.w - 12 - 8 - 70 - 12)
        self.input_abs = Rect(client_rect.x + 12, client_rect.y + 12, avail_w, 28)
        self.add_abs = Rect(self.input_abs.right + 8, self.input_abs.y, 70, 28)

    # ---------- drawing ----------
    def draw(self, screen):
        # frame
        self.draw_frame(screen)

        # client background
        c = self.client
        pygame.draw.rect(screen, DARK_PANEL, c, border_radius=6)
        pygame.draw.rect(screen, OUTLINE, c, 1, border_radius=6)

        # input + add button
        self._place_abs(c)

        pygame.draw.rect(screen, (20, 20, 20), self.input_abs, border_radius=4)
        pygame.draw.rect(screen, GRAY if self.owner.input_active else (90, 90, 90),
                         self.input_abs, 1, border_radius=4)

        txt = self.owner.input_text or "Add task:"
        col = TEXT if self.owner.input_text else (120, 120, 120)
        s = self.font.render(txt, True, col)
        screen.blit(s, (self.input_abs.x + 8, self.input_abs.y + 6))

        pygame.draw.rect(screen, (32, 32, 32), self.add_abs, border_radius=4)
        pygame.draw.rect(screen, GRAY, self.add_abs, 1, border_radius=4)
        add_s = self.font.render("Add", True, TEXT)
        screen.blit(add_s, (self.add_abs.centerx - add_s.get_width() // 2,
                            self.add_abs.centery - add_s.get_height() // 2))

        # list rows
        y = c.y + self.input_abs.height + 12 + 10
        mouse = pygame.mouse.get_pos()
        for item in self.owner.tasks:
            checkbox = Rect(c.x + 12, y + 6, 18, 18)
            pygame.draw.rect(screen, GRAY, checkbox, 1)
            if item.get("done"):
                pygame.draw.rect(screen, WHITE, checkbox.inflate(-8, -8))

            text_col = (150, 150, 150) if item.get("done") else TEXT
            t = self.font.render(item["text"], True, text_col)
            screen.blit(t, (checkbox.right + 10, y + 6))

            del_rect = Rect(c.right - 32, y + 4, 24, 24)
            over = del_rect.collidepoint(mouse)
            pygame.draw.rect(screen, RED_H if over else RED, del_rect, border_radius=4)
            x_s = self.font.render("X", True, WHITE)
            screen.blit(x_s, (del_rect.centerx - x_s.get_width() // 2,
                              del_rect.centery - x_s.get_height() // 2))

            y += 30
