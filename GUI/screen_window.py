import tkinter

import customtkinter as ctk
import pyautogui as pyautogui
from PIL import ImageTk
from PIL import Image


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

        self.start_x = 0
        self.start_y = 0
        self.end_x = 0
        self.end_y = 0

        self.corner_button_max_size = 10
        self.selection_min_size = 20

        self.selection_rect = None
        self.buttons_menu = None

        self.bottom_right_button = None
        self.bottom_left_button = None
        self.top_right_button = None
        self.top_left_button = None
        self.center_button = None
        self.top_button = None
        self.bottom_button = None
        self.left_button = None
        self.right_button = None

        self.selection_width = None
        self.selection_height = None

        self.move_click_y = None
        self.move_click_x = None

    # Binds
    def bind_events(self):
        self.bind_arrows()
        self.bind_key_releases()
        self.bind_mouse_events()
        self.bind_escape()
        self.bind_configure()
        self.bind_control_l()
        self.bind_shift_l()

    def bind_arrows(self):
        self.bind("<Up>", self.handle_up_arrow)
        self.bind("<Left>", self.handle_left_arrow)
        self.bind("<Right>", self.handle_right_arrow)
        self.bind("<Down>", self.handle_down_arrow)

    def bind_key_releases(self):
        self.bind("<KeyRelease-Up>", self.create_menu_and_unbind_selection)
        self.bind("<KeyRelease-Left>", self.create_menu_and_unbind_selection)
        self.bind("<KeyRelease-Right>", self.create_menu_and_unbind_selection)
        self.bind("<KeyRelease-Down>", self.create_menu_and_unbind_selection)

    def bind_mouse_events(self):
        self.bind("<Button-1>", self.start_selection)
        self.bind("<B1-Motion>", self.update_selection)
        self.bind("<ButtonRelease-1>", self.create_menu_and_unbind_selection)

    def bind_escape(self):
        self.bind("<Escape>", self.destroy_window)

    def bind_configure(self):
        self.canvas.bind("<Configure>", self.create_dimming_rectangle)

    def bind_control_l(self):
        self.bind("<KeyPress-Control_L>", self.enable_mouse_selection)
        self.bind("<KeyRelease-Control_L>", self.disable_mouse_selection)

    def bind_shift_l(self):
        self.bind("<KeyPress-Shift_L>", self.handle_press_shift_arrow)
        self.bind("<KeyRelease-Shift_L>", self.handle_release_shift_arrow)

    def handle_release_shift_arrow(self, event):
        self.bind_arrows()
        self.bind_key_releases()

    def handle_press_shift_arrow(self, event):
        self.bind_shift_arrows()
        self.bind_key_releases()

    def bind_shift_arrows(self):
        self.bind("<Up>", self.handle_shift_up_arrow)
        self.bind("<Left>", self.handle_shift_left_arrow)
        self.bind("<Right>", self.handle_shift_right_arrow)
        self.bind("<Down>", self.handle_shift_down_arrow)

    # Bind handlers
    # # Arrows
    def handle_shift_up_arrow(self, event):
        if self.start_y - 1 >= 0:
            self.start_y -= 1

        self.create_selection_rect()

    def handle_shift_right_arrow(self, event):
        canvas_width = self.canvas.winfo_width()
        if self.end_x + 1 <= canvas_width:
            self.end_x += 1

        self.create_selection_rect()

    def handle_shift_down_arrow(self, event):
        canvas_height = self.canvas.winfo_height()
        if self.end_y + 1 <= canvas_height:
            self.end_y += 1

        self.create_selection_rect()

    def handle_shift_left_arrow(self, event):
        if self.start_x - 1 >= 0:
            self.start_x -= 1

        self.create_selection_rect()

    def handle_up_arrow(self, event):
        if self.start_y - 1 >= 0:
            self.start_y -= 1
            self.end_y -= 1

        self.create_selection_rect()

    def handle_right_arrow(self, event):
        canvas_width = self.canvas.winfo_width()
        if self.end_x + 1 <= canvas_width:
            self.start_x += 1
            self.end_x += 1

        self.create_selection_rect()

    def handle_down_arrow(self, event):
        canvas_height = self.canvas.winfo_height()
        if self.end_y + 1 <= canvas_height:
            self.start_y += 1
            self.end_y += 1

        self.create_selection_rect()

    def handle_left_arrow(self, event):
        if self.start_x - 1 >= 0:
            self.start_x -= 1
            self.end_x -= 1

        self.create_selection_rect()

    # # Dimming
    def create_dimming_rectangle(self, event):
        self.canvas.coords(self.dimming_rect, 0, 0, event.width, event.height)

    # # Menu
    def create_menu_and_unbind_selection(self, event):
        self.create_menu(self)

        self.bind("<KeyPress-Control_L>", self.enable_mouse_selection)
        self.bind("<KeyRelease-Control_L>", self.disable_mouse_selection)

        self.disable_mouse_selection(self)

        self.selection_width = None
        self.selection_height = None

        self.move_click_x = None
        self.move_click_y = None

    # #
    def enable_mouse_selection(self, event):
        self.bind("<Button-1>", self.start_selection)
        self.bind("<B1-Motion>", self.update_selection)

    def disable_mouse_selection(self, event):
        self.unbind("<Button-1>")
        self.unbind("<B1-Motion>")

    # #
    def start_selection(self, event):
        self.destroy_buttons()

        self.start_x = event.x
        self.start_y = event.y

    def update_selection(self, event):
        self.end_x = event.x
        self.end_y = event.y

        self.create_selection_rect()

    # #
    def create_selection_rect(self):

        if self.selection_rect:
            self.canvas.delete(self.selection_rect)
            self.canvas.delete("dimming_rect")

        self.selection_rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.end_x, self.end_y, outline="#000000", width=1, fill=""
        )

        corners_coordinates = self.get_corners_coordinates()

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

        self.canvas.tag_lower(dimming_tags, self.selection_rect)
        self.canvas.tag_raise(self.selection_rect)

    def get_corners_coordinates(self) -> list:
        x1, x2 = sorted([self.start_x, self.end_x])
        y1, y2 = sorted([self.start_y, self.end_y])
        corner1 = [x1, y1]
        corner2 = [x2, y2]
        corner3 = [x2, y1]
        corner4 = [x1, y2]
        return [corner1, corner2, corner3, corner4]

    # Menu
    def create_menu(self, event):
        self.destroy_buttons()

        corners_coordinates = self.get_corners_coordinates()
        self.start_x, self.end_x = corners_coordinates[0][0], corners_coordinates[1][0]
        self.start_y, self.end_y = corners_coordinates[0][1], corners_coordinates[1][1]

        self.buttons_menu = ctk.CTkSegmentedButton(self, values=["move", "save", "copy"], border_width=0,
                                                   command=self.buttons_menu_callback)

        possible_positions = [(self.start_x, self.start_y - self.buttons_menu.cget("height") - 10),
                              (self.end_x - self.buttons_menu.cget("width") - 20, self.end_y + 5),
                              (self.end_x - self.buttons_menu.cget("width") - 22,
                               self.start_y - self.buttons_menu.cget("height") - 9),
                              (self.start_x, self.end_y + 5),
                              (self.end_x - self.buttons_menu.cget("width") - 22,
                               self.end_y - self.buttons_menu.cget("height") - 9)]

        position = self.find_suitable_position(possible_positions, self.buttons_menu.cget("width"),
                                               self.buttons_menu.cget("height"))
        self.buttons_menu.place_configure(x=position[0], y=position[1])

        attribute_names = ["top_left_button", "bottom_right_button", "top_right_button", "bottom_left_button"]

        for i, (position, attribute_name) in enumerate(zip(corners_coordinates, attribute_names)):
            button = self.create_moving_button(position, "corner", button_index=i + 1)
            setattr(self, attribute_name, button)

        attribute_names = ['top_button', 'left_button', 'bottom_button', 'right_button']
        coordinate_indices = [0, 0, 3, 2]
        orientations = ['horizontal', 'vertical', 'horizontal', 'vertical']
        button_indices = [5, 6, 7, 8]

        for attr_name, coord_index, orientation, button_index in zip(attribute_names, coordinate_indices, orientations,
                                                                     button_indices):
            button = self.create_moving_button(corners_coordinates[coord_index], "side", side=orientation,
                                               button_index=button_index)
            setattr(self, attr_name, button)

        center_position = [self.start_x + (self.end_x - self.start_x) / 2, self.end_y - (self.end_y - self.start_y) / 2]

        self.center_button = self.create_moving_button(center_position, "center", button_index=0)

    def find_suitable_position(self, possible_positions, width: int, height: int):

        for position in possible_positions:
            x, y = position
            if self.check_fit(x, y, width, height):
                return position

        return possible_positions[-1]

    def check_fit(self, x: int, y: int, width: int, height: int):
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        return x + width <= canvas_width and y + height <= canvas_height and x >= 0 and y - height >= 0

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

    def create_moving_button(self, position, button_type: str, side: str = None, button_index: int = None):
        x = position[0]
        y = position[1]

        selection_width = (self.end_x - self.start_x)
        selection_height = (self.end_y - self.start_y)

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
                               min(int((self.end_x - self.start_x) / 4), self.corner_button_max_size) / 2)
                y_offset = int(min(int(selection_height / 4), self.corner_button_max_size) / 2)

                x += x_offset
                y += y_offset
                width = int(self.end_x - self.start_x -
                            min(int((self.end_x - self.start_x) / 4), self.corner_button_max_size))
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
            width = min(int((self.end_x - self.start_x) / 4), self.corner_button_max_size)
            height = min(int((self.end_y - self.start_y) / 4), self.corner_button_max_size)

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
        self.canvas.tag_bind(f"button_{button_index}", "<Button-1>", lambda event: self.bind_move_button(event, button_index, x, y))

        return button

    def bind_move_button(self, event, button_index, x, y):

        if button_index == 0:
            self.update_bind_selection_center(x, y)
        elif 1 <= button_index <= 4:
            self.update_bind_selection_corners(button_index, x, y)
        elif 5 <= button_index <= 8:
            self.update_bind_selection_side(button_index, x, y)

    def move_selection(self, cursor_x, cursor_y, x: int, y: int):
        if self.selection_width is None:
            self.selection_width = self.end_x - self.start_x
        if self.selection_height is None:
            self.selection_height = self.end_y - self.start_y
        if self.move_click_x is None:
            self.move_click_x = self.selection_width / 2 - cursor_x
        if self.move_click_y is None:
            self.move_click_y = self.selection_height / 2 - cursor_y

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        x += self.move_click_x
        y += self.move_click_y

        if x - self.selection_width + cursor_x >= 0 and x + self.selection_width <= canvas_width:
            self.start_x = x - self.selection_width + cursor_x
            self.end_x = x + cursor_x

        if x - self.selection_width + cursor_x < 0:
            self.start_x = 0
            self.end_x = self.selection_width
        elif x + cursor_x > canvas_width:
            self.start_x = canvas_width - self.selection_width
            self.end_x = canvas_width

        if cursor_y + y - self.selection_height >= 0 and cursor_y + y <= canvas_height:
            self.start_y = cursor_y + y - self.selection_height
            self.end_y = cursor_y + y

        if cursor_y + y - self.selection_height < 0:
            self.start_y = 0
            self.end_y = self.selection_height
        elif cursor_y + y > canvas_height:
            self.start_y = canvas_height - self.selection_height
            self.end_y = canvas_height

        self.create_selection_rect()

    def stretch_selection_sides(self, cursor_x, cursor_y, x: int, y: int, side):

        selection_height = self.end_y - self.start_y
        selection_width = self.end_y - self.start_y

        match side:
            case 5:
                if self.start_y <= self.end_y - self.selection_min_size:
                    self.start_y = cursor_y
                elif self.start_y - cursor_y > 0:
                    self.start_y = cursor_y

                if selection_height < self.selection_min_size:
                    self.start_y = self.end_y - self.selection_min_size
            case 6:
                if self.start_x < self.end_x - self.selection_min_size:
                    self.start_x = cursor_x
                elif self.start_x - cursor_x > 0:
                    self.start_x = cursor_x

                if selection_width < self.selection_min_size:
                    self.start_x = self.end_x - self.selection_min_size
            case 7:
                if self.start_y + self.selection_min_size < self.end_y:
                    self.end_y = cursor_y
                elif self.end_y - cursor_y < 0:
                    self.end_y = cursor_y

                if selection_height < self.selection_min_size:
                    self.end_y = self.start_y + self.selection_min_size
            case 8:
                if self.start_x + self.selection_min_size < self.end_x:
                    self.end_x = cursor_x
                elif self.end_x - cursor_x < 0:
                    self.end_x = cursor_x

                if selection_width < self.selection_min_size:
                    self.end_x = self.start_x + self.selection_min_size

        self.create_selection_rect()

    def stretch_selection_corners(self, cursor_x, cursor_y, corner, x: int, y: int):

        cursor_x += x
        cursor_y += y

        match corner:
            case 1:
                if self.start_x <= self.end_x - self.selection_min_size:
                    self.start_x = cursor_x
                elif self.start_x - cursor_x > 0:
                    self.start_x = cursor_x
                if self.end_x - self.start_x < self.selection_min_size:
                    self.start_x = self.end_x - self.selection_min_size

                if self.start_y <= self.end_y - self.selection_min_size:
                    self.start_y = cursor_y
                elif self.start_y - cursor_y > 0:
                    self.start_y = cursor_y
                if self.end_y - self.start_y < self.selection_min_size:
                    self.start_y = self.end_y - self.selection_min_size
            case 2:
                if self.start_x + self.selection_min_size < self.end_x:
                    self.end_x = cursor_x
                elif self.end_x - cursor_x < 0:
                    self.end_x = cursor_x
                if self.end_x - self.start_x < self.selection_min_size:
                    self.end_x = self.start_x + self.selection_min_size

                if self.start_y + self.selection_min_size < self.end_y:
                    self.end_y = cursor_y
                elif self.end_y - cursor_y < 0:
                    self.end_y = cursor_y
                if self.end_y - self.start_y < self.selection_min_size:
                    self.end_y = self.start_y + self.selection_min_size
            case 3:
                if self.start_x + self.selection_min_size < self.end_x:
                    self.end_x = cursor_x
                elif self.end_x - cursor_x < 0:
                    self.end_x = cursor_x
                if self.end_x - self.start_x < self.selection_min_size:
                    self.end_x = self.start_x + self.selection_min_size

                if self.start_y < self.end_y - self.selection_min_size:
                    self.start_y = cursor_y
                elif self.start_y - cursor_y > 0:
                    self.start_y = cursor_y
                if self.end_y - self.start_y < self.selection_min_size:
                    self.start_y = self.end_y - self.selection_min_size
            case 4:
                if self.start_x < self.end_x - self.selection_min_size:
                    self.start_x = cursor_x
                elif self.start_x - cursor_x > 0:
                    self.start_x = cursor_x
                if self.end_x - self.start_x < self.selection_min_size:
                    self.start_x = self.end_x - self.selection_min_size

                if self.start_y + self.selection_min_size < self.end_y:
                    self.end_y = cursor_y
                elif self.end_y - cursor_y < 0:
                    self.end_y = cursor_y
                if self.end_y - self.start_y < self.selection_min_size:
                    self.end_y = self.start_y + self.selection_min_size

        self.create_selection_rect()

    def buttons_menu_callback(self, value):
        if value == "move":
            pass
        elif value == "save":
            pass
        elif value == "copy":
            pass

    #
    def capture_bbox(self):

        self.mainloop()

        # Определяем координаты верхнего левого и нижнего правого углов bbox
        x1 = min(self.start_x, self.end_x)
        y1 = min(self.start_y, self.end_y)
        x2 = max(self.start_x, self.end_x)
        y2 = max(self.start_y, self.end_y)

        # Обрезаем скриншот по координатам bbox
        bbox_screenshot = self.screenshot.crop((x1, y1, x2, y2))

        # Делаем что-то с полученным скриншотом bbox, например, сохраняем в файл
        bbox_screenshot.save("bbox_screenshot.png")

    # Destroy

    def destroy_buttons(self):
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

    def destroy_window(self, event):
        self.destroy()
