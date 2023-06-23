import threading
import time
import tkinter
from tkinter.filedialog import asksaveasfilename

import customtkinter as ctk
import pyautogui as pyautogui
from PIL import ImageTk, Image

from custom_widgets.button_group import ImageButtonGroup
from handlers.clipboard_handler import copy_screenshot_to_clipboard


class ScreenWindow(ctk.CTkToplevel):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.configure(fg_color="black")  # Темный цвет фона

        self.attributes("-topmost", True)
        self.attributes("-fullscreen", True)  # Окно на весь экран

        self.screenshot = pyautogui.screenshot()
        self.resized_screenshot = ImageTk.PhotoImage(self.screenshot)

        self.canvas = ctk.CTkCanvas(self, highlightthickness=0, bg="black")
        self.canvas.pack(fill=ctk.BOTH, expand=True)
        self.canvas.create_image(0, 0, anchor="nw", image=self.resized_screenshot)
        self.canvas.tag_lower("image")

        self.dimming_rect = self.canvas.create_rectangle(
            0, 0, 0, 0, fill="black", stipple="gray50", tags="dimming_rect"
        )

        self.bind_events()

        self.focus()

        self.selection_start_x = 0
        self.selection_start_y = 0
        self.selection_end_x = 0
        self.selection_end_y = 0

        self.corner_button_max_size = 10
        self.selection_min_size = 20

        self.selection_rect = None
        self.buttons_menu = None

        self.selection_width = None
        self.selection_height = None

        self.move_click_y = None
        self.move_click_x = None

        self.holding_shift_l = False

    # Binds

    def unbind_mouse(self) -> None:
        self.unbind("<ButtonRelease-1>")

    def bind_events(self):
        key_up = "Up"
        key_left = "Left"
        key_right = "Right"
        key_down = "Down"
        self.bind_keys_move(key_up, key_left, key_right, key_down)
        self.bind_keys_move_release(key_up, key_left, key_right, key_down)

        self.bind_mouse_events()

        destroy = "Escape"
        self.bind_destroy(destroy)

        self.bind_control_l()

        self.bind_shift_l(key_up, key_left, key_right, key_down)

        self.bind_configure()

    def bind_keys_move(self, key_up: str, key_left: str, key_right: str, key_down: str):
        self.bind(f"<{key_up}>", self.handle_up_move)
        self.bind(f"<{key_left}>", self.handle_left_move)
        self.bind(f"<{key_right}>", self.handle_right_move)
        self.bind(f"<{key_down}>", self.handle_down_move)

    def bind_keys_move_release(self, key_up: str, key_left: str, key_right: str, key_down: str):
        self.bind(f"<KeyRelease-{key_up}>", self.create_menu_and_unbind_selection)
        self.bind(f"<KeyRelease-{key_left}>", self.create_menu_and_unbind_selection)
        self.bind(f"<KeyRelease-{key_right}>", self.create_menu_and_unbind_selection)
        self.bind(f"<KeyRelease-{key_down}>", self.create_menu_and_unbind_selection)

    def bind_mouse_events(self):
        self.bind("<Button-1>", self.start_selection)
        self.bind("<B1-Motion>", self.update_selection)
        self.bind("<ButtonRelease-1>", self.create_menu_and_unbind_selection)

    def bind_destroy(self, destroy: str):
        self.bind(f"<{destroy}>", self.destroy_window)

    def bind_configure(self):
        self.canvas.bind("<Configure>", self.create_dimming_rectangle)

    def bind_control_l(self):
        self.bind("<KeyPress-Control_L>", self.enable_mouse_selection)
        self.bind("<KeyRelease-Control_L>", self.disable_mouse_selection)

    def bind_shift_l(self, key_up: str, key_left: str, key_right: str, key_down: str):
        self.bind("<KeyPress-Shift_L>", lambda event: self.handle_stretch(event, key_up, key_left, key_right, key_down))
        self.bind("<KeyRelease-Shift_L>",
                  lambda event: self.handle_stretch_release(event, key_up, key_left, key_right, key_down))

    def handle_stretch_release(self, event, key_up: str, key_left: str, key_right: str, key_down: str):
        self.holding_shift_l = False
        self.bind_keys_move(key_up, key_left, key_right, key_down)
        self.bind_keys_move_release(key_up, key_left, key_right, key_down)

    def handle_stretch(self, event, key_up: str, key_left: str, key_right: str, key_down: str):
        self.holding_shift_l = True
        self.bind_shift_arrows(key_up, key_left, key_right, key_down)
        self.bind_keys_move_release(key_up, key_left, key_right, key_down)

    def bind_shift_arrows(self, key_up: str, key_left: str, key_right: str, key_down: str):
        self.bind(f"<{key_up}>", self.handle_up_stretch)
        self.bind(f"<{key_left}>", self.handle_left_stretch)
        self.bind(f"<{key_right}>", self.handle_right_stretch)
        self.bind(f"<{key_down}>", self.handle_down_stretch)

    # Bind handlers
    # # Stretch
    def handle_up_stretch(self, event):
        self.destroy_menu()
        self.destroy_move_menu()

        if self.selection_start_y - 1 >= 0:
            self.selection_start_y -= 1

        self.create_selection_rect()

    def handle_right_stretch(self, event):
        self.destroy_menu()
        self.destroy_move_menu()

        canvas_width = self.canvas.winfo_width()
        if self.selection_end_x + 1 <= canvas_width:
            self.selection_end_x += 1

        self.create_selection_rect()

    def handle_down_stretch(self, event):
        self.destroy_menu()
        self.destroy_move_menu()

        canvas_height = self.canvas.winfo_height()
        if self.selection_end_y + 1 <= canvas_height:
            self.selection_end_y += 1

        self.create_selection_rect()

    def handle_left_stretch(self, event):
        self.destroy_menu()
        self.destroy_move_menu()

        if self.selection_start_x - 1 >= 0:
            self.selection_start_x -= 1

        self.create_selection_rect()

    def handle_up_move(self, event):
        self.destroy_menu()
        self.destroy_move_menu()

        if self.selection_start_y - 1 >= 0:
            self.selection_start_y -= 1
            self.selection_end_y -= 1

        self.create_selection_rect()

    def handle_right_move(self, event):
        self.destroy_menu()
        self.destroy_move_menu()

        canvas_width = self.canvas.winfo_width()
        if self.selection_end_x + 1 <= canvas_width:
            self.selection_start_x += 1
            self.selection_end_x += 1

        self.create_selection_rect()

    def handle_down_move(self, event):
        self.destroy_menu()
        self.destroy_move_menu()

        canvas_height = self.canvas.winfo_height()
        if self.selection_end_y + 1 <= canvas_height:
            self.selection_start_y += 1
            self.selection_end_y += 1

        self.create_selection_rect()

    def handle_left_move(self, event):
        self.destroy_menu()
        self.destroy_move_menu()

        if self.selection_start_x - 1 >= 0:
            self.selection_start_x -= 1
            self.selection_end_x -= 1

        self.create_selection_rect()

    # # Dimming
    def create_menu_and_unbind_selection(self, event=None):

        if self.get_selection_width() < self.selection_min_size:
            self.selection_end_x = self.selection_start_x + self.selection_min_size
        if self.get_selection_height() < self.selection_min_size:
            self.selection_end_y = self.selection_start_y + self.selection_min_size

        self.create_menu(self)

        self.bind("<KeyPress-Control_L>", self.enable_mouse_selection)
        self.bind("<KeyRelease-Control_L>", self.disable_mouse_selection)

        self.disable_mouse_selection(self)

        self.selection_width = None
        self.selection_height = None

        self.move_click_x = None
        self.move_click_y = None

    # # Menu
    def enable_mouse_selection(self, event):
        self.bind("<Button-1>", self.start_selection)
        self.bind("<B1-Motion>", self.update_selection)

    # #
    def disable_mouse_selection(self, event):
        self.unbind("<Button-1>")
        self.unbind("<B1-Motion>")
        self.canvas.unbind("<B1-Motion>")

    def start_selection(self, event):
        self.destroy_menu()
        self.destroy_move_menu()

        self.selection_start_x = event.x
        self.selection_start_y = event.y

    # #
    def update_selection(self, event):
        self.selection_end_x = event.x
        self.selection_end_y = event.y

        self.create_selection_rect()

    def create_selection_rect(self):

        if self.selection_rect:
            self.canvas.delete(self.selection_rect)
            self.canvas.delete("dimming_rect")

        self.selection_rect = self.canvas.create_rectangle(
            self.selection_start_x, self.selection_start_y, self.selection_end_x, self.selection_end_y,
            outline="#000000", width=1, fill="", tags="selection"
        )

        corners_coordinates = self.get_corners_coordinates()

        self.create_outside_dimming(corners_coordinates)

        self.canvas.tag_raise(self.selection_rect)

    # #
    def create_outside_dimming(self, corners_coordinates: list):
        x1, y1 = corners_coordinates[0][0], corners_coordinates[0][1]
        x2, y2 = corners_coordinates[1][0], corners_coordinates[1][1]

        dimming_rects = [
            (0, 0, self.canvas.winfo_width(), y1),  # Upper dimming rectangle
            (0, y2, self.canvas.winfo_width(), self.canvas.winfo_height()),  # Lower dimming rectangle
            (0, y1, x1, y2),  # Left dimming rectangle
            (x2, y1, self.canvas.winfo_width(), y2),  # Right dimming rectangle
        ]

        dimming_tags = "dimming_rect"

        for dimming_rect in dimming_rects:
            self.canvas.create_rectangle(
                *dimming_rect, fill="black", stipple="gray50", outline="", tags=dimming_tags
            )
        self.canvas.tag_raise(dimming_tags, self.selection_rect)

    def create_dimming_rectangle(self, event):
        self.canvas.coords(self.dimming_rect, 0, 0, event.width, event.height)

    def get_corners_coordinates(self) -> list:
        x1, x2 = sorted([self.selection_start_x, self.selection_end_x])
        y1, y2 = sorted([self.selection_start_y, self.selection_end_y])
        corner1 = [x1, y1]
        corner2 = [x2, y2]
        corner3 = [x2, y1]
        corner4 = [x1, y2]
        return [corner1, corner2, corner3, corner4]

    def get_selection_width(self) -> int:
        return abs(self.selection_start_x - self.selection_end_x)

    def get_selection_height(self):
        return abs(self.selection_start_y - self.selection_end_y)

    # Menu
    def create_menu(self, event):
        self.destroy_menu()
        self.destroy_move_menu()

        self.create_selection_rect()

        corners_coordinates = self.get_corners_coordinates()
        self.selection_start_x, self.selection_end_x = corners_coordinates[0][0], corners_coordinates[1][0]
        self.selection_start_y, self.selection_end_y = corners_coordinates[0][1], corners_coordinates[1][1]

        move_icon = Image.open("images/move-icon.jpg")
        save_icon = Image.open("images/save-icon.png")
        copy_icon = Image.open("images/copy-icon.png")
        images = (move_icon, save_icon, copy_icon)

        self.buttons_menu = ImageButtonGroup(self, border_width=0, orientation="horizontal",
                                             values=["move", "save", "copy"], images=images, fg_color="gray50",
                                             command=self.buttons_menu_callback)

        possible_positions = [(self.selection_start_x, self.selection_start_y - self.buttons_menu.cget("height") + 5),
                              (self.selection_end_x - self.buttons_menu.cget("width"), self.selection_end_y + 5),
                              (self.selection_end_x - self.buttons_menu.cget("width"),
                               self.selection_start_y - self.buttons_menu.cget("height") + 5),
                              (self.selection_start_x, self.selection_end_y + 5),
                              (self.selection_end_x - self.buttons_menu.cget("width"),
                               self.selection_end_y - self.buttons_menu.cget("height") + 10)]

        position = self.find_suitable_position(possible_positions, self.buttons_menu.cget("width"),
                                               self.buttons_menu.cget("height"))
        self.buttons_menu.place_configure(x=position[0], y=position[1])

        attribute_names = ["top_left_button", "bottom_right_button", "top_right_button", "bottom_left_button"]

        for i, (position, attribute_name) in enumerate(zip(corners_coordinates, attribute_names)):
            self.create_move_button(position, "corner", button_index=i + 1)

        attribute_names = ['top_button', 'left_button', 'bottom_button', 'right_button']
        coordinate_indices = [0, 0, 3, 2]
        orientations = ['horizontal', 'vertical', 'horizontal', 'vertical']
        button_indices = [5, 6, 7, 8]

        for attr_name, coord_index, orientation, button_index in zip(attribute_names, coordinate_indices, orientations,
                                                                     button_indices):
            self.create_move_button(corners_coordinates[coord_index], "side", side=orientation,
                                    button_index=button_index)

        center_position = [self.selection_start_x + (self.selection_end_x - self.selection_start_x) / 2,
                           self.selection_end_y - (self.selection_end_y - self.selection_start_y) / 2]

        self.create_move_button(center_position, "center", button_index=0)

    def find_suitable_position(self, possible_positions, width: int, height: int):

        for position in possible_positions:
            x, y = position
            if self.check_screen_fit(x, y, width, height):
                return position

        return possible_positions[-1]

    def check_screen_fit(self, x: int, y: int, width: int, height: int):
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        return x + width <= canvas_width and y + height <= canvas_height and x >= 0 and y >= 0

    # # Buttons for moving/stretching the selection
    def update_bind_selection_center(self, x: int, y: int):
        self.canvas.bind("<B1-Motion>", lambda event: self.move_selection(event.x, event.y, x, y))
        self.bind("<ButtonRelease-1>", self.create_menu_and_unbind_selection)

    def update_bind_selection_side(self, side: int, x: int, y: int):
        self.canvas.bind("<B1-Motion>", lambda event: self.stretch_selection_sides(event.x, event.y, x, y, side))
        self.bind("<ButtonRelease-1>", self.create_menu_and_unbind_selection)

    def update_bind_selection_corners(self, corner: int, x: int, y: int):

        self.canvas.bind("<B1-Motion>", lambda event: self.stretch_selection_corners(event.x, event.y, corner, x, y))
        self.bind("<ButtonRelease-1>", self.create_menu_and_unbind_selection)

    def create_move_button(self, position, button_type: str, side: str = None, button_index: int = None):
        x = position[0]
        y = position[1]

        selection_width = self.get_selection_width()
        selection_height = self.get_selection_height()

        width = 0
        height = 0

        x_offset = 0
        y_offset = 0

        cursor = None

        if button_type == "center":
            cursor = "size"

            x_offset = int(min(int(selection_width / 4), self.corner_button_max_size) / 2)
            y_offset = int(min(int(selection_height / 4), self.corner_button_max_size) / 2)

            x += x_offset
            y += y_offset
            width = max(int(selection_width - self.corner_button_max_size),
                        self.selection_min_size - self.corner_button_max_size)
            height = max(int(selection_height - self.corner_button_max_size),
                         self.selection_min_size - self.corner_button_max_size)

            x_offset = selection_width / 2
            y_offset = selection_height / 2
        elif button_type == "side":
            if side == "horizontal":
                cursor = 'sb_v_double_arrow'
                x_offset = int(min(int(selection_width / 4), self.corner_button_max_size) +
                               min(int((self.selection_end_x - self.selection_start_x) / 4),
                                   self.corner_button_max_size) / 2)
                y_offset = int(min(int(selection_height / 4), self.corner_button_max_size) / 2)

                x += x_offset
                y += y_offset
                width = int(self.selection_end_x - self.selection_start_x -
                            min(int((self.selection_end_x - self.selection_start_x) / 4), self.corner_button_max_size))
                height = min(int(selection_height / 4), self.corner_button_max_size)
            elif side == "vertical":
                cursor = 'sb_h_double_arrow'
                x_offset = int(min(int(selection_width / 4), self.corner_button_max_size) -
                               min(int(selection_width / 4), self.corner_button_max_size) / 2)
                y_offset = int(min(int(selection_height / 4), self.corner_button_max_size) +
                               min(int(selection_height / 4), self.corner_button_max_size) / 2)

                x += x_offset
                y += y_offset

                width = int(min(int(selection_width / 4), self.corner_button_max_size))
                height = int(selection_height - min(int(selection_height / 4), self.corner_button_max_size))

            x_offset = min(int(selection_width / 4), self.corner_button_max_size)
            y_offset = min(int(selection_height / 4), self.corner_button_max_size)
        elif button_type == "corner":
            if button_index == 1 or button_index == 2:
                cursor = "size_nw_se"
            elif button_index == 3 or button_index == 4:
                cursor = "size_ne_sw"
            width = min(int((self.selection_end_x - self.selection_start_x) / 4), self.corner_button_max_size)
            height = min(int((self.selection_end_y - self.selection_start_y) / 4), self.corner_button_max_size)

            x_offset = width / 2
            y_offset = height / 2

        screenshot = pyautogui.screenshot()
        screenshot = screenshot.crop((x - x_offset, y - y_offset, x - x_offset + width, y - y_offset + height))
        resized_screenshot = ImageTk.PhotoImage(screenshot.resize((width, height)))

        button = self.canvas.create_image(
            x - x_offset, y - y_offset, image=resized_screenshot, tags=f"button_{button_index}", anchor="nw"
        )

        self.canvas.tag_bind(f"button_{button_index}", "<Enter>", lambda event: self.canvas.config(cursor=cursor))
        self.canvas.tag_bind(f"button_{button_index}", "<Leave>", lambda event: self.canvas.config(cursor=""))
        self.canvas.tag_bind(f"button_{button_index}", "<Button-1>",
                             lambda event: self.bind_move_button(event, button_index, x, y))

        return button

    def bind_move_button(self, event, button_index, x, y):

        if button_index == 0:
            self.update_bind_selection_center(x, y)
        elif 1 <= button_index <= 4:
            self.update_bind_selection_corners(button_index, x, y)
        elif 5 <= button_index <= 8:
            self.update_bind_selection_side(button_index, x, y)

        self.destroy_menu()
        self.canvas.tag_unbind(f"button_{button_index}", "<Leave>")
        self.canvas.tag_unbind(f"button_{button_index}", "<Button-1>")

    def move_selection(self, cursor_x, cursor_y, x: int, y: int):
        if self.selection_width is None:
            self.selection_width = self.get_selection_width()
        if self.selection_height is None:
            self.selection_height = self.get_selection_height()
        if self.move_click_x is None:
            self.move_click_x = int(self.selection_width / 2) - cursor_x
        if self.move_click_y is None:
            self.move_click_y = int(self.selection_height / 2) - cursor_y

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        selection_width = self.get_selection_width()
        selection_height = self.get_selection_height()

        x += self.move_click_x - int(min(int(selection_width / 4), self.corner_button_max_size) / 2)
        y += self.move_click_y - int(min(int(selection_height / 4), self.corner_button_max_size) / 2)

        if x - self.selection_width + cursor_x >= 0 and x + self.selection_width <= canvas_width:
            self.selection_start_x = x - self.selection_width + cursor_x
            self.selection_end_x = x + cursor_x

        if x - self.selection_width + cursor_x < 0:
            self.selection_start_x = 0
            self.selection_end_x = self.selection_width
        elif x + cursor_x > canvas_width:
            self.selection_start_x = canvas_width - self.selection_width
            self.selection_end_x = canvas_width

        if cursor_y + y - self.selection_height >= 0 and cursor_y + y <= canvas_height:
            self.selection_start_y = cursor_y + y - self.selection_height
            self.selection_end_y = cursor_y + y

        if cursor_y + y - self.selection_height < 0:
            self.selection_start_y = 0
            self.selection_end_y = self.selection_height
        elif cursor_y + y > canvas_height:
            self.selection_start_y = canvas_height - self.selection_height
            self.selection_end_y = canvas_height

        self.create_selection_rect()

    def stretch_selection_sides(self, cursor_x, cursor_y, x: int, y: int, side: int):

        match side:
            case 5:
                if self.selection_start_y <= self.selection_end_y - self.selection_min_size:
                    self.selection_start_y = cursor_y

                if self.selection_start_y > self.selection_end_y - self.selection_min_size:
                    self.selection_start_y = self.selection_end_y - self.selection_min_size
            case 6:
                if self.selection_start_x <= self.selection_end_x - self.selection_min_size:
                    self.selection_start_x = cursor_x

                if self.selection_start_x > self.selection_end_x - self.selection_min_size:
                    self.selection_start_x = self.selection_end_x - self.selection_min_size
            case 7:
                if self.selection_end_y >= self.selection_start_y + self.selection_min_size:
                    self.selection_end_y = cursor_y

                if self.selection_end_y < self.selection_start_y + self.selection_min_size:
                    self.selection_end_y = self.selection_start_y + self.selection_min_size
            case 8:
                if self.selection_end_x >= self.selection_start_x + self.selection_min_size:
                    self.selection_end_x = cursor_x

                if self.selection_end_x < self.selection_start_x + self.selection_min_size:
                    self.selection_end_x = self.selection_start_x + self.selection_min_size

        self.create_selection_rect()

    def stretch_selection_corners(self, cursor_x, cursor_y, corner: int, x: int, y: int):

        match corner:
            case 1:
                if self.selection_start_x <= self.selection_end_x - self.selection_min_size:
                    self.selection_start_x = cursor_x

                if self.selection_start_x > self.selection_end_x - self.selection_min_size:
                    self.selection_start_x = self.selection_end_x - self.selection_min_size

                if self.selection_start_y <= self.selection_end_y - self.selection_min_size:
                    self.selection_start_y = cursor_y

                if self.selection_start_y > self.selection_end_y - self.selection_min_size:
                    self.selection_start_y = self.selection_end_y - self.selection_min_size
            case 2:
                if self.selection_end_x >= self.selection_start_x + self.selection_min_size:
                    self.selection_end_x = cursor_x

                if self.selection_end_x < self.selection_start_x + self.selection_min_size:
                    self.selection_end_x = self.selection_start_x + self.selection_min_size

                if self.selection_end_y >= self.selection_start_y + self.selection_min_size:
                    self.selection_end_y = cursor_y

                if self.selection_end_y < self.selection_start_y + self.selection_min_size:
                    self.selection_end_y = self.selection_start_y + self.selection_min_size
            case 3:
                if self.selection_end_x >= self.selection_start_x + self.selection_min_size:
                    self.selection_end_x = cursor_x

                if self.selection_end_x < self.selection_start_x + self.selection_min_size:
                    self.selection_end_x = self.selection_start_x + self.selection_min_size

                if self.selection_start_y <= self.selection_end_y - self.selection_min_size:
                    self.selection_start_y = cursor_y

                if self.selection_start_y > self.selection_end_y - self.selection_min_size:
                    self.selection_start_y = self.selection_end_y - self.selection_min_size
            case 4:
                if self.selection_start_x <= self.selection_end_x - self.selection_min_size:
                    self.selection_start_x = cursor_x

                if self.selection_start_x > self.selection_end_x - self.selection_min_size:
                    self.selection_start_x = self.selection_end_x - self.selection_min_size

                if self.selection_end_y >= self.selection_start_y + self.selection_min_size:
                    self.selection_end_y = cursor_y

                if self.selection_end_y < self.selection_start_y + self.selection_min_size:
                    self.selection_end_y = self.selection_start_y + self.selection_min_size

        self.create_selection_rect()

    def buttons_menu_callback(self, value):
        if value == "move":
            pass
        elif value == "save":
            result = self.save_image()
            if not self.holding_shift_l and result:
                self.destroy_window()
        elif value == "copy":
            self.copy_image()
            self.destroy_window()

    #

    def save_image(self):
        width = self.get_selection_width()
        height = self.get_selection_height()

        self.unbind_mouse()

        self.destroy_move_menu()
        self.destroy_menu()

        selection = self.canvas.find_withtag("selection")
        self.canvas.itemconfig(selection, width=0)
        self.attributes("-topmost", False)
        ticks = str(time.time()).replace('.', '')[:13]
        default_filename = f"{ticks}_screenshot.png"
        save_path = asksaveasfilename(defaultextension='', filetypes=[("All Files", "*.*")],
                                      initialfile=default_filename, parent=self)

        time.sleep(0.2)
        screenshot = pyautogui.screenshot()
        screenshot = screenshot.crop(
            (self.selection_start_x, self.selection_start_y, self.selection_start_x + width + 1,
             self.selection_start_y + height + 1))
        if save_path:
            screenshot.save(save_path)
        self.attributes("-topmost", True)

        self.after(100, self.create_menu_and_unbind_selection)

        return True if save_path else False

    def copy_image(self):
        width = self.get_selection_width()
        height = self.get_selection_height()

        self.unbind_mouse()

        self.destroy_move_menu()
        self.destroy_menu()

        selection = self.canvas.find_withtag("selection")
        self.canvas.itemconfig(selection, width=0)

        def delay_and_screenshot():
            time.sleep(0.2)
            screenshot = pyautogui.screenshot()
            screenshot = screenshot.crop(
                (self.selection_start_x, self.selection_start_y, self.selection_start_x + width + 1,
                 self.selection_start_y + height + 1))
            copy_screenshot_to_clipboard(screenshot)

        screenshot_thread = threading.Thread(target=delay_and_screenshot)
        screenshot_thread.start()

        self.after(100, self.create_menu_and_unbind_selection)

    # Destroy

    def destroy_menu(self):
        buttons_to_destroy = [
            self.buttons_menu,
        ]
        attribute_names = [
            "buttons_menu",
        ]
        for button, attr_name in zip(buttons_to_destroy, attribute_names):
            if button is not None:
                button.destroy()
                setattr(self, attr_name, None)

    def destroy_move_menu(self):
        for i in range(8):
            self.canvas.delete(f"button_{i}")

    def destroy_window(self, event=None):
        self.destroy()
