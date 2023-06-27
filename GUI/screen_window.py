import time
from tkinter import colorchooser
from tkinter.filedialog import asksaveasfilename

import customtkinter as ctk
import pyautogui as pyautogui
from PIL import ImageTk, Image

from custom_widgets.button_group import ImageButtonGroup
from custom_widgets.canvas.circle import Circle
from custom_widgets.canvas.line import Line
from custom_widgets.canvas.rectangle import Rectangle
from custom_widgets.canvas.rectangle_outside_dimming import RectangleOutsideDimming
from custom_widgets.move_menu import MoveMenu
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

        self.focus()

        self.corner_button_max_size = 10
        self.selection_min_size = 20

        self.current_mode = "selection"
        self.selection_rect = RectangleOutsideDimming(self.canvas)

        self.main_menu = None
        self.main_menu_position = None

        self.draw_menu = None
        self.color_picker_button = None
        self.drawing_element = None
        self.drawing_selection = Rectangle(self.canvas, color="gray50", tags="drawing_selection", dash=(5, 3), min_size=3)

        self.move_menu = MoveMenu(
            self.canvas,
            self.selection_rect,
            pyautogui.screenshot(),
            corner_button_max_size=self.corner_button_max_size,
            additional_func=lambda: self.creating_menu(),
            del_func=lambda: self.del_func())

        self.drawing_color = "#FF0000"

        self.holding_shift_l = False

        self.bind_events()

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
        self.bind(f"<{key_up}>", self.move_menu.handle_up_move)
        self.bind(f"<{key_left}>", self.move_menu.handle_left_move)
        self.bind(f"<{key_right}>", self.move_menu.handle_right_move)
        self.bind(f"<{key_down}>", self.move_menu.handle_down_move)

    def bind_keys_move_release(self, key_up: str, key_left: str, key_right: str, key_down: str):
        self.bind(f"<KeyRelease-{key_up}>", self.create_menus)
        self.bind(f"<KeyRelease-{key_left}>", self.create_menus)
        self.bind(f"<KeyRelease-{key_right}>", self.create_menus)
        self.bind(f"<KeyRelease-{key_down}>", self.create_menus)

    def bind_mouse_events(self, event=None):
        self.canvas.bind("<Button-1>", self.start_selection)
        self.canvas.bind("<B1-Motion>", self.update_selection)
        self.canvas.bind("<ButtonRelease-1>", self.create_menus)

    def bind_destroy(self, destroy: str):
        self.bind(f"<{destroy}>", self.destroy_window)

    def bind_configure(self):
        self.canvas.bind("<Configure>", self.create_dimming_rectangle)

    def bind_control_l(self):
        self.bind("<KeyPress-Control_L>", self.bind_mouse_events)
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
        self.bind_stretch(key_up, key_left, key_right, key_down)
        self.bind_keys_move_release(key_up, key_left, key_right, key_down)

    def bind_stretch(self, key_up: str, key_left: str, key_right: str, key_down: str):
        self.bind(f"<{key_up}>", self.move_menu.handle_up_stretch)
        self.bind(f"<{key_left}>", self.move_menu.handle_left_stretch)
        self.bind(f"<{key_right}>", self.move_menu.handle_right_stretch)
        self.bind(f"<{key_down}>", self.move_menu.handle_down_stretch)

    # Bind handlers

    # # Dimming
    def create_menus(self, event=None):

        self.selection_rect.expand_to_minimum_size()
        self.selection_rect.create()

        self.creating_menu()
        if self.current_mode == "selection":
            self.move_menu.set_target(self.selection_rect)
            self.move_menu.set_limits(True)
            self.move_menu.create()
            self.destroy_canvas_elements()
        elif self.current_mode == "draw":
            self.move_menu.destroy()
            if self.drawing_element is not None:
                self.move_menu.set_target(self.drawing_element)
                self.move_menu.set_limits(False)
                self.move_menu.create()

    def del_func(self):
        self.destroy_menus()
        self.destroy_canvas_elements()

    def creating_menu(self):
        self.main_menu_position = self.create_menu()

        if self.current_mode == "draw":
            self.create_color_picker_menu(self.main_menu_position)
            self.create_draw_menu(self.main_menu_position)
            if self.drawing_element is not None:
                corners = self.drawing_element.get_corners_coordinates()
                self.drawing_selection.set_coordinates(start_x=corners[0][0], start_y=corners[0][1],
                                                       end_x=corners[1][0], end_y=corners[1][1])
                self.drawing_selection.create()

        self.bind_control_l()
        self.disable_mouse_selection()

    def disable_mouse_selection(self, event=None):
        self.canvas.unbind("<Button-1>")
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ButtonRelease-1>")

    ##
    def start_selection(self, event):
        self.destroy_menus()
        self.move_menu.destroy()
        self.selection_rect.set_coordinates(start_x=event.x, start_y=event.y)

    def update_selection(self, event):
        self.selection_rect.set_coordinates(end_x=event.x, end_y=event.y)
        self.selection_rect.create()

    ##
    def bind_draw_mouse_events(self, event=None):
        self.canvas.bind("<Button-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.update_draw)
        self.canvas.bind("<ButtonRelease-1>", self.create_menus)

    def start_draw(self, event):
        self.destroy_menus()
        self.move_menu.destroy()
        self.drawing_element.set_coordinates(start_x=event.x, start_y=event.y)
        self.drawing_selection.set_coordinates(start_x=event.x, start_y=event.y)

    def update_draw(self, event):
        self.drawing_element.set_coordinates(end_x=event.x, end_y=event.y)
        self.drawing_element.create()
        self.drawing_selection.set_coordinates(end_x=event.x, end_y=event.y)
        self.drawing_selection.create()
        self.canvas.tag_raise(self.drawing_selection.get_tags())
        self.canvas.tag_raise(self.drawing_element.get_tags())

    def create_dimming_rectangle(self, event):
        self.canvas.coords(self.dimming_rect, 0, 0, event.width, event.height)

    # Menu
    def create_menu(self, event=None):
        self.destroy_menus()

        corners_coordinates = self.selection_rect.get_corners_coordinates()
        start_x, end_x = corners_coordinates[0][0], corners_coordinates[1][0]
        start_y, end_y = corners_coordinates[0][1], corners_coordinates[1][1]

        draw_icon = Image.open("images/draw-icon.png")
        move_icon = Image.open("images/move-icon.jpg")

        save_icon = Image.open("images/save-icon.png")
        copy_icon = Image.open("images/copy-icon.png")

        images = None
        values = None

        if self.current_mode == "draw":
            images = (move_icon, save_icon, copy_icon)
            values = ["draw", "save", "copy"]
        elif self.current_mode == "selection":
            images = (draw_icon, save_icon, copy_icon)
            values = ["move", "save", "copy"]

        self.main_menu = ImageButtonGroup(self, border_width=0, orientation="horizontal",
                                          values=values, images=images, fg_color="gray50",
                                          command=self.main_menu_callback)

        possible_positions = [
            (start_x, start_y - self.main_menu.cget("height") + 5),
            (end_x - self.main_menu.cget("width"), end_y + 5),
            (end_x - self.main_menu.cget("width"), start_y - self.main_menu.cget("height") + 5),
            (start_x, end_y + 5),
            (end_x - self.main_menu.cget("width"), end_y - self.main_menu.cget("height") + 10)]

        position = self.find_suitable_position(possible_positions, self.main_menu.cget("width"),
                                               self.main_menu.cget("height"))
        self.main_menu.place_configure(x=position[0] + 5, y=position[1])

        return position

    def create_draw_menu(self, position):

        line_icon = Image.open("images/line-icon.png")
        rectangle_icon = Image.open("images/rectangle-icon.png")
        circle_icon = Image.open("images/circle-icon.png")
        images = (line_icon, rectangle_icon, circle_icon)
        values = ["line", "rectangle", "circle"]

        self.draw_menu = ImageButtonGroup(self, border_width=0, orientation="horizontal",
                                          values=values, images=images, fg_color="gray50",
                                          command=self.draw_menu_callback)

        possible_positions = [(position[0], position[1] - self.draw_menu.cget("height"))]

        position = self.find_suitable_position(possible_positions, self.main_menu.cget("width"),
                                               self.main_menu.cget("height"))
        self.draw_menu.place_configure(x=position[0], y=position[1] + 5)

    def create_color_picker_menu(self, position):
        self.destroy_color_picker_menu()
        hover_color = self.lighten_color(self.drawing_color)
        self.color_picker_button = ctk.CTkButton(self, border_width=5, fg_color=self.drawing_color, text="",
                                                 border_color="gray50", width=25, height=25, bg_color="transparent",
                                                 hover=True, hover_color=hover_color, command=lambda: self.pick_color())
        possible_positions = [(position[0] - self.color_picker_button.cget("width"), position[1]),
                              (position[0] + 5, position[1] - self.color_picker_button.cget("height") - 5 - 1),
                              (position[0] + 5, position[1] + self.color_picker_button.cget("height") + 5 + 1),
                              (position[0] - self.color_picker_button.cget("width"), position[1])]

        position = self.find_suitable_position(possible_positions, self.main_menu.cget("width"),
                                               self.main_menu.cget("height"))
        self.color_picker_button.place_configure(x=position[0], y=position[1])

    def lighten_color(self, hex_color: hex, brightness_increase: float = 0.2):
        red = int(hex_color[1:3], 16)
        green = int(hex_color[3:5], 16)
        blue = int(hex_color[5:7], 16)

        red += int((255 - red) * brightness_increase)
        green += int((255 - green) * brightness_increase)
        blue += int((255 - blue) * brightness_increase)

        red = min(red, 240)
        green = min(green, 240)
        blue = min(blue, 240)

        lightened_color = f"#{red:02X}{green:02X}{blue:02X}"
        return lightened_color

    def pick_color(self):
        self.attributes("-topmost", False)

        drawing_color = colorchooser.askcolor()
        if drawing_color[1] is not None:
            self.drawing_color = drawing_color[1]

        self.attributes("-topmost", True)
        self.create_color_picker_menu(self.main_menu_position)

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

    def main_menu_callback(self, value):
        if value == "move":
            self.current_mode = "draw"
            self.create_menus()
        elif value == "draw":
            self.current_mode = "selection"
            self.create_menus()
        elif value == "save":
            result = self.save_image()
            if not self.holding_shift_l and result:
                self.destroy_window()
        elif value == "copy":
            self.copy_image()
            self.destroy_window()

    def draw_menu_callback(self, value):
        self.bind_draw_mouse_events()
        if value == "line":
            self.drawing_element = Line(self.canvas, color=self.drawing_color, width=2, tags="line", min_size=1)
        elif value == "rectangle":
            self.drawing_element = Rectangle(self.canvas, color=self.drawing_color, width=2, tags="rectangle", min_size=1)
        elif value == "circle":
            self.drawing_element = Circle(self.canvas, color=self.drawing_color, width=2, tags="circle", min_size=1)

    #

    def save_image(self):
        corners_coordinates = self.selection_rect.get_corners_coordinates()
        start_x, end_x = corners_coordinates[0][0], corners_coordinates[1][0]
        start_y, end_y = corners_coordinates[0][1], corners_coordinates[1][1]

        width = self.selection_rect.get_width()
        height = self.selection_rect.get_height()

        self.unbind_mouse()

        self.move_menu.destroy()
        self.destroy_menus()
        self.destroy_canvas_elements()

        selection = self.canvas.find_withtag("selection")
        self.canvas.itemconfig(selection, width=0)
        self.attributes("-topmost", False)
        ticks = str(time.time()).replace('.', '')[:13]
        default_filename = f"{ticks}_screenshot.png"
        save_path = asksaveasfilename(defaultextension='', filetypes=[("All Files", "*.*")],
                                      initialfile=default_filename, parent=self)

        time.sleep(0.2)
        screenshot = pyautogui.screenshot()
        screenshot = screenshot.crop((start_x, start_y, start_x + width + 1, start_y + height + 1))
        if save_path:
            screenshot.save(save_path)
        self.attributes("-topmost", True)

        self.after(100, self.create_menus)

        return True if save_path else False

    def copy_image(self):
        corners_coordinates = self.selection_rect.get_corners_coordinates()
        start_x, end_x = corners_coordinates[0][0], corners_coordinates[1][0]
        start_y, end_y = corners_coordinates[0][1], corners_coordinates[1][1]

        width = self.selection_rect.get_width()
        height = self.selection_rect.get_height()

        self.unbind_mouse()

        self.move_menu.destroy()
        self.destroy_menus()
        self.destroy_canvas_elements()

        selection = self.canvas.find_withtag("selection")
        self.canvas.itemconfig(selection, width=0)

        time.sleep(0.2)
        screenshot = pyautogui.screenshot()
        screenshot = screenshot.crop((start_x, start_y, start_x + width + 1, start_y + height + 1))
        copy_screenshot_to_clipboard(screenshot)

        self.after(100, self.create_menus)

    # Destroy

    def destroy_menus(self):
        items_to_destroy = {
            "main_menu": self.main_menu,
            "color_picker_button": self.color_picker_button,
            "draw_menu": self.draw_menu,
        }
        for attr_name, item in items_to_destroy.items():
            if item is not None:
                item.destroy()
                setattr(self, attr_name, None)

    def destroy_canvas_elements(self):
        items_to_destroy = [self.drawing_selection]
        for item in items_to_destroy:
            if item is not None:
                item.destroy()

    def destroy_color_picker_menu(self):
        items_to_destroy = {
            "color_picker_button": self.color_picker_button,
        }
        for attr_name, item in items_to_destroy.items():
            if item is not None:
                item.destroy()
                setattr(self, attr_name, None)

    def destroy_window(self, event=None):
        self.destroy()
