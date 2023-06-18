import customtkinter as ctk
import pyautogui as pyautogui
from PIL import ImageGrab, ImageTk

from handlers.clipboard_handler import copy_screenshot_to_clipboard
from handlers.file_save_handler import save_image_to_file


class BBoxCaptureWindow(ctk.CTkToplevel):
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

        self.focused_corner = None

        self.selection_width = None
        self.selection_height = None

    def bind_events(self):
        self.bind("<Button-1>", self.start_selection)  # Start selection
        self.bind("<B1-Motion>", self.update_selection)  # Update selection
        self.bind("<Escape>", self.close_window)  # End selection
        self.bind("<ButtonRelease-1>", self.create_menu_and_unbind_selection)
        self.canvas.bind("<Configure>", self.update_dimming_rectangle)
        self.bind("<KeyPress-Control_L>", self.enable_mouse_selection)
        self.bind("<KeyRelease-Control_L>", self.disable_mouse_selection)

    def update_dimming_rectangle(self, event):
        self.canvas.coords(self.dimming_rect, 0, 0, event.width, event.height)

    def create_menu_and_unbind_selection(self, event):
        self.create_menu(self)

        self.bind("<KeyPress-Control_L>", self.enable_mouse_selection)
        self.bind("<KeyRelease-Control_L>", self.disable_mouse_selection)

        self.disable_mouse_selection(self)

        self.selection_width = None
        self.selection_height = None

    def enable_mouse_selection(self, event):
        self.bind("<Button-1>", self.start_selection)
        self.bind("<B1-Motion>", self.update_selection)

    def disable_mouse_selection(self, event):
        self.unbind("<Button-1>")
        self.unbind("<B1-Motion>")

    def start_selection(self, event):
        self.destroy_buttons()

        self.start_x = event.x
        self.start_y = event.y

    def update_selection(self, event):
        self.end_x = event.x
        self.end_y = event.y

        self.create_selection_rect()

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

        corner_labels = ["size_nw_se", "size_nw_se", "size_ne_sw", "size_ne_sw"]
        buttons = [self.top_left_button, self.bottom_right_button, self.top_right_button, self.bottom_left_button]
        attribute_names = ["top_left_button", "bottom_right_button", "top_right_button", "bottom_left_button"]

        for i, (corner, label, attribute_name) in enumerate(zip(corners_coordinates, corner_labels, attribute_names)):
            buttons[i] = self.create_corner_moving_button(corner, label, i + 1)
            setattr(self, attribute_name, buttons[i])

        attribute_names = ['top_button', 'left_button', 'bottom_button', 'right_button']
        coordinate_indices = [0, 0, 3, 2]
        orientations = ['horizontal', 'vertical', 'horizontal', 'vertical']
        button_indices = [5, 6, 7, 8]

        buttons = []

        for attr_name, coord_index, orientation, button_index in zip(attribute_names, coordinate_indices, orientations,
                                                                     button_indices):
            button = self.create_side_moving_button(corners_coordinates[coord_index], orientation, button_index)
            buttons.append(button)
            setattr(self, attr_name, button)

        self.center_button = self.create_center_moving_button(self.start_x + (self.end_x - self.start_x) / 2,
                                                              self.end_y - (self.end_y - self.start_y) / 2,
                                                              "size")

    def find_suitable_position(self, possible_positions, width, height):

        for position in possible_positions:
            x, y = position
            if self.check_fit(x, y, width, height):
                return position

        return possible_positions[-1]

    def check_fit(self, x, y, width, height):
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        return x + width <= canvas_width and y + height <= canvas_height and x >= 0 and y - height >= 0

    def create_center_moving_button(self, x, y, cursor: str):
        x += int(min(int((self.end_x - self.start_x) / 4), self.corner_button_max_size) / 2) + 1
        y += int(min(int((self.end_y - self.start_y) / 4), self.corner_button_max_size) / 2) + 1

        width = max(int(self.end_x - self.start_x - (self.end_x - self.start_x) / 5 - self.corner_button_max_size),
                    self.selection_min_size - self.corner_button_max_size)
        height = max(int(self.end_y - self.start_y - self.corner_button_max_size - (self.end_y - self.start_y) / 5),
                     self.selection_min_size - self.corner_button_max_size)
        button = ctk.CTkButton(
            self.canvas, text="", width=width,
            height=height,
            fg_color="transparent", hover=False,
            command=lambda: update_bind_selection_center()
        )
        button.configure(cursor=cursor)
        button.place_configure(x=x - (self.end_x - self.start_x) / 2, y=y - (self.end_y - self.start_y) / 2)

        def update_bind_selection_center():
            self.bind("<B1-Motion>", lambda event: self.move_selection(event.x, event.y, x, y))
            self.bind("<ButtonRelease-1>", self.create_menu_and_unbind_selection)
            button.lower()

        return button

    def move_selection(self, cursor_x, cursor_y, x, y):
        if self.selection_width is None:
            self.selection_width = self.end_x - self.start_x
        if self.selection_height is None:
            self.selection_height = self.end_y - self.start_y

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        print(canvas_width, self.end_x + cursor_x)
        if x - self.selection_width + cursor_x >= 0 and cursor_x + self.selection_width <= canvas_width:
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

    def update_selection_sides(self, cursor_x, cursor_y, x, y, side):

        cursor_x = cursor_x + x
        cursor_y = cursor_y + y

        match side:
            case 5:
                if self.start_y <= self.end_y - self.selection_min_size:
                    self.start_y = cursor_y
                elif self.start_y - cursor_y > 0:
                    self.start_y = cursor_y
                if self.end_y - self.start_y < self.selection_min_size:
                    self.start_y = self.end_y - self.selection_min_size
            case 6:
                if self.start_x < self.end_x - self.selection_min_size:
                    self.start_x = cursor_x
                elif self.start_x - cursor_x > 0:
                    self.start_x = cursor_x
                if self.end_x - self.start_x < self.selection_min_size:
                    self.start_x = self.end_x - self.selection_min_size
            case 7:
                if self.start_y + self.selection_min_size < self.end_y:
                    self.end_y = cursor_y
                elif self.end_y - cursor_y < 0:
                    self.end_y = cursor_y
                if self.end_y - self.start_y < self.selection_min_size:
                    self.end_y = self.start_y + self.selection_min_size
            case 8:
                if self.start_x + self.selection_min_size < self.end_x:
                    self.end_x = cursor_x
                elif self.end_x - cursor_x < 0:
                    self.end_x = cursor_x
                if self.end_x - self.start_x < self.selection_min_size:
                    self.end_x = self.start_x + self.selection_min_size

        self.create_selection_rect()

    def update_selection_corners(self, cursor_x, cursor_y, corner):
        x = self.focused_corner[0]
        y = self.focused_corner[1]
        print(cursor_x)
        cursor_x = cursor_x + x
        cursor_y = cursor_y + y

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

    def create_side_moving_button(self, position, direction: str, side: int):
        x = position[0]
        y = position[1]

        if direction == "horizontal":
            cursor = 'sb_v_double_arrow'
            x += int(min(int((self.end_x - self.start_x) / 4), self.corner_button_max_size) + min(int((self.end_x - self.start_x) / 4), self.corner_button_max_size) / 2)
            y += int(min(int((self.end_y - self.start_y) / 4), self.corner_button_max_size) / 2)

            width = int(
                self.end_x - self.start_x - (self.end_x - self.start_x) / 5 - min(int((self.end_x - self.start_x) / 4),
                                                                                  self.corner_button_max_size) / 2)
            height = min(int((self.end_y - self.start_y) / 4), self.corner_button_max_size)
        elif direction == "vertical":
            cursor = 'sb_h_double_arrow'
            x += int(min(int((self.end_x - self.start_x) / 4), self.corner_button_max_size) - min(int((self.end_x - self.start_x) / 4), self.corner_button_max_size) / 2)
            y += int(min(int((self.end_y - self.start_y) / 4), self.corner_button_max_size) + min(int((self.end_y - self.start_y) / 4), self.corner_button_max_size) / 2)

            width = int(min(int((self.end_x - self.start_x) / 4), self.corner_button_max_size))
            height = int(
                self.end_y - self.start_y - (self.end_y - self.start_y) / 5 - min(int((self.end_y - self.start_y) / 4),
                                                                                  self.corner_button_max_size) / 2)

        button = ctk.CTkButton(
            self.canvas, text="", width=width,
            height=height,
            fg_color="transparent", hover=False,
            command=lambda: update_bind_selection_side(side)
        )
        button.configure(cursor=cursor)
        button.place_configure(x=x - min(int((self.end_x - self.start_x) / 4), self.corner_button_max_size),
                               y=y - min(int((self.end_y - self.start_y) / 4), self.corner_button_max_size))

        def update_bind_selection_side(side: int):
            self.bind("<B1-Motion>", lambda event: self.update_selection_sides(event.x, event.y, x, y, side))
            self.bind("<ButtonRelease-1>", self.create_menu_and_unbind_selection)
            button.lower()

        return button

    def create_corner_moving_button(self, position, cursor: str, corner: int):

        x = position[0]
        y = position[1]

        width = min(int((self.end_x - self.start_x) / 4), self.corner_button_max_size)
        height = min(int((self.end_y - self.start_y) / 4), self.corner_button_max_size)

        button = ctk.CTkButton(
            self.canvas, text="", width=width, height=height, fg_color="transparent", hover=False,
            command=lambda: update_bind_selection_corners(corner)
        )
        button.configure(cursor=cursor)
        button.place_configure(x=x - width / 2, y=y - height / 2)

        x -= width / 2
        y -= height / 2

        def update_bind_selection_corners(corner: int):
            self.focused_corner = [x, y]

            self.bind("<B1-Motion>", lambda event: self.update_selection_corners(event.x, event.y, corner))
            self.bind("<ButtonRelease-1>", self.create_menu_and_unbind_selection)
            button.lower()

        return button

    def buttons_menu_callback(self, value):
        if value == "move":
            pass
        elif value == "save":
            pass
        elif value == "copy":
            pass

    def destroy_buttons(self):
        buttons_to_destroy = [
            self.buttons_menu,
            self.top_left_button,
            self.top_right_button,
            self.bottom_left_button,
            self.bottom_right_button,
            self.center_button,
            self.top_button,
            self.bottom_button,
            self.left_button,
            self.right_button
        ]

        for button in buttons_to_destroy:
            if button is not None:
                button.destroy()

        self.buttons_menu = None
        self.top_left_button = None
        self.top_right_button = None
        self.bottom_left_button = None
        self.bottom_right_button = None
        self.center_button = None
        self.top_button = None
        self.bottom_button = None
        self.left_button = None
        self.right_button = None

    def close_window(self, event):
        self.destroy()

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


class CustomApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.geometry("600x500")

        self.frame = ctk.CTkFrame(self)
        self.frame.pack()

        self.label = ctk.CTkLabel(self.frame, text="Hello!")
        self.copy_image = ctk.CTkButton(self.frame, text="Click me", command=self.copy_image)
        self.save_button = ctk.CTkButton(self.frame, text="Save image", command=self.save_image)
        self.bbox_button = ctk.CTkButton(self.frame, text="Capture BBox", command=self.capture_bbox)

        self.label.pack()
        self.copy_image.pack()
        self.save_button.pack()
        self.bbox_button.pack()

        self.frame.place(relx=0.5, rely=0.5, anchor="center")

    def copy_image(self):
        # Capture the screenshot
        screenshot = ImageGrab.grab()

        copy_screenshot_to_clipboard(screenshot)

    def save_image(self):
        # Capture the screenshot
        screenshot = ImageGrab.grab()

        save_image_to_file(screenshot)

    def capture_bbox(self):
        bbox_capture = BBoxCaptureWindow(self)


if __name__ == "__main__":
    app = CustomApp()
    app.mainloop()
