import dearpygui.dearpygui as dpg
from todo_list import TodoList

ICON_FILE = "notepad-icon.png"

TAG_TODO_WIN = "todo_window"
TAG_TODO_GROUP = "todo_group"
TAG_TODO_INPUT = "todo_input"
TAG_DONE_THEME = "done_text_theme"
TAG_ICON_TEX = "todo_icon_tex"
TAG_ICON_WIN = "todo_icon_window"
TAG_ICON_BTN = "todo_icon_button"
TAG_ICON_WIN_THEME = "icon_window_theme"
TAG_ICON_BTN_THEME = "icon_button_theme"
TAG_HOVER_WIN = "hover_window"
TAG_HOVER_TEXT = "hover_text"
TAG_BOX_EMPTY_TEX = "box_empty_tex"
TAG_BOX_FILLED_TEX = "box_filled_tex"
# Bello!

def rgba(r, g, b, a=255):
    return (r/255.0, g/255.0, b/255.0, a/255.0)

todo_list = TodoList()

dragging = {"active": False, "start_mouse": (0.0, 0.0), "start_win": (0.0, 0.0)}

def make_box_textures(size=18):
    w = h = size
    data_empty = []
    data_filled = []
    for y in range(h):
        for x in range(w):
            border = x == 0 or y == 0 or x == w-1 or y == h-1
            if border:
                data_empty.extend(rgba(180, 180, 180, 255))
                data_filled.extend(rgba(180, 180, 180, 255))
            else:
                data_empty.extend(rgba(0, 0, 0, 0))
                inner = 3 <= x <= w-4 and 3 <= y <= h-4
                if inner:
                    data_filled.extend(rgba(255, 255, 255, 255))
                else:
                    data_filled.extend(rgba(0, 0, 0, 0))
    dpg.add_static_texture(w, h, data_empty, tag=TAG_BOX_EMPTY_TEX)
    dpg.add_static_texture(w, h, data_filled, tag=TAG_BOX_FILLED_TEX)

def ensure_todo_window(create_if_missing=True):
    exists = dpg.does_item_exist(TAG_TODO_WIN)
    if not exists and create_if_missing:
        with dpg.window(tag=TAG_TODO_WIN, label="To-Do", pos=(220, 60), width=400, height=120, show=True):
            with dpg.group(tag=TAG_TODO_GROUP):
                with dpg.group(horizontal=True):
                    dpg.add_input_text(tag=TAG_TODO_INPUT, hint="Add task:", on_enter=True, callback=on_add_task, width=300)
                    dpg.add_button(label="Add", callback=on_add_task, width=70)
                with dpg.group(tag="todo_list_group"):
                    pass
    return dpg.does_item_exist(TAG_TODO_WIN)

def toggle_todo_window(_s=None, _a=None, _u=None):
    if not ensure_todo_window(False):
        ensure_todo_window(True)
        dpg.configure_item(TAG_TODO_WIN, show=True)
    else:
        dpg.configure_item(TAG_TODO_WIN, show=not dpg.is_item_shown(TAG_TODO_WIN))
    for task in todo_list.tasks:
        create_task_window(task)

def on_add_task(_s, _a, _u=None):
    text = dpg.get_value(TAG_TODO_INPUT) if dpg.does_item_exist(TAG_TODO_INPUT) else ""
    text = text.strip()
    if not text:
        return
    dpg.set_value(TAG_TODO_INPUT, "")
    item = todo_list.add(text)
    create_task_window(item)

def on_box_click(sender, app_data, user_data):
    tid = user_data["id"]
    done = todo_list.toggle_done(tid)
    if done is not None:
        tex = TAG_BOX_FILLED_TEX if done else TAG_BOX_EMPTY_TEX
        dpg.configure_item(sender, texture_tag=tex)

def on_delete_task_window(sender, app_data, user_data):
    tid = user_data["id"]
    todo_list.delete(tid)
    table_row = dpg.get_item_parent(sender)
    dpg.delete_item(table_row)

def create_task_window(item):
    with dpg.table(header_row=False, policy=dpg.mvTable_SizingStretchProp, parent="todo_list_group"):
        dpg.add_table_column(width_fixed=True, init_width_or_weight=28)
        dpg.add_table_column()
        dpg.add_table_column(width_fixed=True, init_width_or_weight=28)
        with dpg.table_row():
            tex = TAG_BOX_FILLED_TEX if item.get("done") else TAG_BOX_EMPTY_TEX
            dpg.add_image_button(texture_tag=tex, width=18, height=18, callback=on_box_click,
                                    user_data={"id": item["id"]})
            dpg.add_text(item["text"])
            with dpg.theme() as red_btn_theme:
                with dpg.theme_component(dpg.mvButton):
                    dpg.add_theme_color(dpg.mvThemeCol_Button, (150, 0, 0, 255))
                    dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (200, 0, 0, 255))
                    dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (255, 0, 0, 255))
            btn = dpg.add_button(label="X", width=24, callback=on_delete_task_window,
                                    user_data={"id": item["id"]})
            dpg.bind_item_theme(btn, red_btn_theme)

# ---------------- ICON DRAG & HOVER ----------------
def on_icon_mouse_down(sender, app_data, user_data=None):
    if dpg.is_item_hovered(TAG_ICON_BTN):
        dragging["active"] = True
        dragging["start_mouse"] = dpg.get_mouse_pos()
        dragging["start_win"] = dpg.get_item_pos(TAG_ICON_WIN)
        dpg.focus_item(TAG_ICON_WIN)
        if _is_shown(TAG_HOVER_WIN):
            dpg.configure_item(TAG_HOVER_WIN, show=False)

def on_icon_mouse_release(sender, app_data, user_data=None):
    dragging["active"] = False

def on_global_mouse_move(sender, app_data):
    if dragging["active"] and dpg.is_mouse_button_down(dpg.mvMouseButton_Left):
        mx, my = dpg.get_mouse_pos()
        sx, sy = dragging["start_mouse"]
        wx, wy = dragging["start_win"]
        nx = int(wx + (mx - sx))
        ny = int(wy + (my - sy))
        dpg.set_item_pos(TAG_ICON_WIN, (nx, ny))
        if _is_shown(TAG_HOVER_WIN):
            dpg.configure_item(TAG_HOVER_WIN, show=False)
    else:
        dragging["active"] = False
        if not dpg.is_item_hovered(TAG_ICON_BTN) and _is_shown(TAG_HOVER_WIN):
            dpg.configure_item(TAG_HOVER_WIN, show=False)

def _is_shown(tag):
    return dpg.does_item_exist(tag) and dpg.get_item_configuration(tag).get("show", False)

def _position_hover_text():
    bx, by = dpg.get_item_rect_min(TAG_ICON_BTN)
    _, by2 = dpg.get_item_rect_max(TAG_ICON_BTN)
    dpg.configure_item(TAG_HOVER_WIN, pos=(int(bx), int(by2 + 1)))

def on_icon_hover(_s=None, _a=None, _u=None):
    if not dragging["active"]:
        _position_hover_text()
        dpg.configure_item(TAG_HOVER_WIN, show=True)

# ------------------- GUI SETUP -------------------
dpg.create_context()
dpg.create_viewport(title="embezzlement", width=960, height=600)
dpg.configure_app(docking=False)

with dpg.theme(tag=TAG_DONE_THEME):
    with dpg.theme_component(dpg.mvText):
        dpg.add_theme_color(dpg.mvThemeCol_Text, (150, 150, 150, 255))

with dpg.theme() as global_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (0, 0, 0, 255))
        dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (0, 0, 0, 255))
        dpg.add_theme_color(dpg.mvThemeCol_PopupBg, (0, 0, 0, 255))
dpg.bind_theme(global_theme)
dpg.set_viewport_clear_color((0, 0, 0, 255))

with dpg.theme(tag=TAG_ICON_WIN_THEME):
    with dpg.theme_component(dpg.mvWindowAppItem):
        dpg.add_theme_style(dpg.mvStyleVar_WindowBorderSize, 0.0)
        dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 0.0, 0.0)

with dpg.theme(tag=TAG_ICON_BTN_THEME):
    with dpg.theme_component(dpg.mvImageButton):
        dpg.add_theme_color(dpg.mvThemeCol_Button, (0, 0, 0, 0))
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (0, 0, 0, 0))
        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (0, 0, 0, 0))
        dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 0.0)
        dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 0.0, 0.0)

icon_ok = False
with dpg.texture_registry(show=False):
    try:
        w, h, c, data = dpg.load_image(ICON_FILE)
        dpg.add_static_texture(w, h, data, tag=TAG_ICON_TEX)
        icon_ok = True
    except Exception as e:
        print(f"Icon load failed: {e}")
    make_box_textures(18)

with dpg.window(tag=TAG_ICON_WIN, label="", pos=(16, 16), width=64, height=64,
                no_title_bar=True, no_resize=True, no_collapse=True, no_close=True,
                no_scrollbar=True):
    if icon_ok:
        dpg.add_image_button(texture_tag=TAG_ICON_TEX, tag=TAG_ICON_BTN, width=64, height=64, callback=toggle_todo_window)
        dpg.bind_item_theme(TAG_ICON_BTN, TAG_ICON_BTN_THEME)
    else:
        dpg.add_button(label="", tag=TAG_ICON_BTN, width=64, height=64, callback=toggle_todo_window)
dpg.bind_item_theme(TAG_ICON_WIN, TAG_ICON_WIN_THEME)

with dpg.theme() as hover_theme:
    with dpg.theme_component(dpg.mvWindowAppItem):
        dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (0, 0, 0, 0))
        dpg.add_theme_style(dpg.mvStyleVar_WindowBorderSize, 0.0)
        dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 0.0, 0.0)
        dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 0.0, 0.0)

with dpg.window(tag=TAG_HOVER_WIN, label="", pos=(0, 0), no_title_bar=True,
                no_move=True, no_resize=True, no_collapse=True, no_close=True,
                no_scrollbar=True, show=False):
    dpg.add_text("todo n dat", tag=TAG_HOVER_TEXT)
dpg.bind_item_theme(TAG_HOVER_WIN, hover_theme)

with dpg.item_handler_registry() as icon_handlers:
    dpg.add_item_hover_handler(callback=on_icon_hover)
dpg.bind_item_handler_registry(TAG_ICON_BTN, icon_handlers)

with dpg.handler_registry():
    dpg.add_mouse_down_handler(callback=on_icon_mouse_down, button=dpg.mvMouseButton_Left)
    dpg.add_mouse_release_handler(callback=on_icon_mouse_release, button=dpg.mvMouseButton_Left)
    dpg.add_mouse_move_handler(callback=on_global_mouse_move)

# Re-create existing tasks
dpg.setup_dearpygui()

dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()