from typing import Union, Callable

from PIL import Image, ImageTk


class MoveMenu:

    def __init__(
            self,
            master: any,
            target: any,
            screenshot: Image,
            corner_button_max_size: int = 10,
            additional_func: Union[Callable[[], None], None] = None,
            del_func: Union[Callable[[], None], None] = None):

        self._target_min_size = target.get_min_size()
        self._corner_button_max_size = corner_button_max_size
        self._additional_func = additional_func
        self._del_func = del_func

        self._end_y = 0
        self._end_x = 0
        self._start_y = 0
        self._start_x = 0

        self._target = target
        self._master = master
        self._screenshot = screenshot

        self._click_offset_y = None
        self._click_offset_x = None
        self._initial_target_height = None
        self._initial_target_width = None

    def create_move_menu(self):

        corners_coordinates = self._target.get_corners_coordinates()
        self._start_x, self._end_x = corners_coordinates[0][0], corners_coordinates[1][0]
        self._start_y, self._end_y = corners_coordinates[0][1], corners_coordinates[1][1]

        for i, position in enumerate(corners_coordinates):
            self.create_move_button(position, "corner", button_index=i + 1)

        coordinate_indices = [0, 0, 3, 2]
        orientations = ['horizontal', 'vertical', 'horizontal', 'vertical']
        button_indices = [5, 6, 7, 8]

        for coord_index, orientation, button_index in zip(coordinate_indices, orientations, button_indices):
            self.create_move_button(corners_coordinates[coord_index], "side", side=orientation,
                                    button_index=button_index)

        center_position = [self._start_x + self._target.get_width() / 2,
                           self._end_y - self._target.get_height() / 2]

        self.create_move_button(center_position, "center", button_index=0)

    def create_move_button(self, position, button_type: str, side: str = None,
                           button_index: int = None):
        x = position[0]
        y = position[1]

        selection_width = self._target.get_width()
        selection_height = self._target.get_height()

        width = 0
        height = 0

        x_offset = 0
        y_offset = 0

        cursor = None

        if button_type == "center":
            cursor = "size"

            x_offset = int(min(int(selection_width / 4), self._corner_button_max_size) / 2)
            y_offset = int(min(int(selection_height / 4), self._corner_button_max_size) / 2)

            x += x_offset
            y += y_offset
            width = max(int(selection_width - self._corner_button_max_size),
                        self._target_min_size - self._corner_button_max_size)
            height = max(int(selection_height - self._corner_button_max_size),
                         self._target_min_size - self._corner_button_max_size)

            x_offset = selection_width / 2
            y_offset = selection_height / 2
        elif button_type == "side":
            if side == "horizontal":
                cursor = 'sb_v_double_arrow'
                x_offset = int(min(int(selection_width / 4), self._corner_button_max_size) +
                               min(int((self._end_x - self._start_x) / 4),
                                   self._corner_button_max_size) / 2)
                y_offset = int(min(int(selection_height / 4), self._corner_button_max_size) / 2)

                x += x_offset
                y += y_offset
                width = int(self._end_x - self._start_x -
                            min(int((self._end_x - self._start_x) / 4),
                                self._corner_button_max_size))
                height = min(int(selection_height / 4), self._corner_button_max_size)
            elif side == "vertical":
                cursor = 'sb_h_double_arrow'
                x_offset = int(min(int(selection_width / 4), self._corner_button_max_size) -
                               min(int(selection_width / 4), self._corner_button_max_size) / 2)
                y_offset = int(min(int(selection_height / 4), self._corner_button_max_size) +
                               min(int(selection_height / 4), self._corner_button_max_size) / 2)

                x += x_offset
                y += y_offset

                width = int(min(int(selection_width / 4), self._corner_button_max_size))
                height = int(selection_height - min(int(selection_height / 4), self._corner_button_max_size))

            x_offset = min(int(selection_width / 4), self._corner_button_max_size)
            y_offset = min(int(selection_height / 4), self._corner_button_max_size)
        elif button_type == "corner":
            if button_index == 1 or button_index == 2:
                cursor = "size_nw_se"
            elif button_index == 3 or button_index == 4:
                cursor = "size_ne_sw"
            width = min(int((self._end_x - self._start_x) / 4), self._corner_button_max_size)
            height = min(int((self._end_y - self._start_y) / 4), self._corner_button_max_size)

            x_offset = width / 2
            y_offset = height / 2

        screenshot = self._screenshot.crop((x - x_offset, y - y_offset, x - x_offset + width, y - y_offset + height))
        resized_screenshot = ImageTk.PhotoImage(screenshot.resize((width, height)))

        button = self._master.create_image(
            x - x_offset, y - y_offset, image=resized_screenshot, tags=f"button_{button_index}", anchor="nw"
        )

        self._master.tag_bind(f"button_{button_index}", "<Enter>", lambda event: self._master.config(cursor=cursor))
        self._master.tag_bind(f"button_{button_index}", "<Leave>", lambda event: self._master.config(cursor=""))
        self._master.tag_bind(f"button_{button_index}", "<Button-1>",
                              lambda event: self.bind_move_button(event, button_index, x, y))

        return button

    def bind_move_button(self, event, button_index, x, y):
        if self._del_func() is not None:
            self._del_func()

        if button_index == 0:
            self.update_bind_selection_center(x, y)
        elif 1 <= button_index <= 4:
            self.update_bind_selection_corners(button_index)
        elif 5 <= button_index <= 8:
            self.update_bind_selection_side(button_index)

        self._master.tag_unbind(f"button_{button_index}", "<Leave>")
        self._master.tag_unbind(f"button_{button_index}", "<Button-1>")

    def update_bind_selection_center(self, x: int, y: int):
        self._master.bind("<B1-Motion>", lambda event: self.move(event.x, event.y, x, y))
        self._master.bind("<ButtonRelease-1>", self.create)

    def update_bind_selection_side(self, side: int):
        self._master.bind("<B1-Motion>", lambda event: self.stretch_sides(event.x, event.y, side))
        self._master.bind("<ButtonRelease-1>", self.create)

    def update_bind_selection_corners(self, corner: int):

        self._master.bind("<B1-Motion>", lambda event: self.stretch_corners(event.x, event.y, corner))
        self._master.bind("<ButtonRelease-1>", self.create)

    def move(self, cursor_x, cursor_y, x: int, y: int):
        if self._initial_target_width is None:
            self._initial_target_width = self._target.get_width()
        if self._initial_target_height is None:
            self._initial_target_height = self._target.get_height()
        if self._click_offset_x is None:
            self._click_offset_x = int(self._initial_target_width / 2) - cursor_x
        if self._click_offset_y is None:
            self._click_offset_y = int(self._initial_target_height / 2) - cursor_y

        canvas_width = self._master.winfo_width()
        canvas_height = self._master.winfo_height()

        target_width = self._target.get_width()
        target_height = self._target.get_height()

        x += self._click_offset_x - int(min(int(target_width / 4), self._corner_button_max_size) / 2)
        y += self._click_offset_y - int(min(int(target_height / 4), self._corner_button_max_size) / 2)

        if x - self._initial_target_width + cursor_x >= 0 and x + self._initial_target_width <= canvas_width:
            self._start_x = x - self._initial_target_width + cursor_x
            self._end_x = x + cursor_x

        if x - self._initial_target_width + cursor_x < 0:
            self._start_x = 0
            self._end_x = self._initial_target_width
        elif x + cursor_x > canvas_width:
            self._start_x = canvas_width - self._initial_target_width
            self._end_x = canvas_width

        if cursor_y + y - self._initial_target_height >= 0 and cursor_y + y <= canvas_height:
            self._start_y = cursor_y + y - self._initial_target_height
            self._end_y = cursor_y + y

        if cursor_y + y - self._initial_target_height < 0:
            self._start_y = 0
            self._end_y = self._initial_target_height
        elif cursor_y + y > canvas_height:
            self._start_y = canvas_height - self._initial_target_height
            self._end_y = canvas_height
        self._target.set_coordinates(self._start_x, self._start_y, self._end_x, self._end_y)
        self._target.create()

    def stretch_sides(self, cursor_x, cursor_y, side: int):

        match side:
            case 5:
                if self._start_y <= self._end_y - self._target_min_size:
                    self._start_y = cursor_y

                if self._start_y > self._end_y - self._target_min_size:
                    self._start_y = self._end_y - self._target_min_size
            case 6:
                if self._start_x <= self._end_x - self._target_min_size:
                    self._start_x = cursor_x

                if self._start_x > self._end_x - self._target_min_size:
                    self._start_x = self._end_x - self._target_min_size
            case 7:
                if self._end_y >= self._start_y + self._target_min_size:
                    self._end_y = cursor_y

                if self._end_y < self._start_y + self._target_min_size:
                    self._end_y = self._start_y + self._target_min_size
            case 8:
                if self._end_x >= self._start_x + self._target_min_size:
                    self._end_x = cursor_x

                if self._end_x < self._start_x + self._target_min_size:
                    self._end_x = self._start_x + self._target_min_size

        self._target.set_coordinates(self._start_x, self._start_y, self._end_x, self._end_y)
        self._target.create()

    def stretch_corners(self, cursor_x, cursor_y, corner: int):

        match corner:
            case 1:
                if self._start_x <= self._end_x - self._target_min_size:
                    self._start_x = cursor_x

                if self._start_x > self._end_x - self._target_min_size:
                    self._start_x = self._end_x - self._target_min_size

                if self._start_y <= self._end_y - self._target_min_size:
                    self._start_y = cursor_y

                if self._start_y > self._end_y - self._target_min_size:
                    self._start_y = self._end_y - self._target_min_size
            case 2:
                if self._end_x >= self._start_x + self._target_min_size:
                    self._end_x = cursor_x

                if self._end_x < self._start_x + self._target_min_size:
                    self._end_x = self._start_x + self._target_min_size

                if self._end_y >= self._start_y + self._target_min_size:
                    self._end_y = cursor_y

                if self._end_y < self._start_y + self._target_min_size:
                    self._end_y = self._start_y + self._target_min_size
            case 3:
                if self._end_x >= self._start_x + self._target_min_size:
                    self._end_x = cursor_x

                if self._end_x < self._start_x + self._target_min_size:
                    self._end_x = self._start_x + self._target_min_size

                if self._start_y <= self._end_y - self._target_min_size:
                    self._start_y = cursor_y

                if self._start_y > self._end_y - self._target_min_size:
                    self._start_y = self._end_y - self._target_min_size
            case 4:
                if self._start_x <= self._end_x - self._target_min_size:
                    self._start_x = cursor_x

                if self._start_x > self._end_x - self._target_min_size:
                    self._start_x = self._end_x - self._target_min_size

                if self._end_y >= self._start_y + self._target_min_size:
                    self._end_y = cursor_y

                if self._end_y < self._start_y + self._target_min_size:
                    self._end_y = self._start_y + self._target_min_size

        self._target.set_coordinates(self._start_x, self._start_y, self._end_x, self._end_y)
        self._target.create()

    def create(self, event=None):
        corners_coordinates = self._target.get_corners_coordinates()
        self._start_x, self._start_y = corners_coordinates[0][0], corners_coordinates[0][1]
        self._end_x, self._end_y = corners_coordinates[1][0], corners_coordinates[1][1]
        self._target.set_coordinates(self._start_x, self._start_y, self._end_x, self._end_y)
        self._target.expand_to_minimum_size()
        self._target.create()

        self.create_move_menu()

        self._click_offset_y = None
        self._click_offset_x = None

        self._initial_target_height = None
        self._initial_target_width = None
        if self._additional_func is not None:
            self._additional_func()

    # Move
    def handle_up_move(self, event):
        if self._del_func() is not None:
            self._del_func()
        self.destroy_move_menu()

        if self._start_y - 1 >= 0:
            self._start_y -= 1
            self._end_y -= 1

        self._target.set_coordinates(self._start_x, self._start_y, self._end_x, self._end_y)
        self._target.create()

    def handle_right_move(self, event):
        if self._del_func() is not None:
            self._del_func()
        self.destroy_move_menu()

        canvas_width = self._master.winfo_width()
        if self._end_x + 1 <= canvas_width:
            self._start_x += 1
            self._end_x += 1

        self._target.set_coordinates(self._start_x, self._start_y, self._end_x, self._end_y)
        self._target.create()

    def handle_down_move(self, event):
        if self._del_func() is not None:
            self._del_func()
        self.destroy_move_menu()

        canvas_height = self._master.winfo_height()
        if self._end_y + 1 <= canvas_height:
            self._start_y += 1
            self._end_y += 1

        self._target.set_coordinates(self._start_x, self._start_y, self._end_x, self._end_y)
        self._target.create()

    def handle_left_move(self, event):
        if self._del_func() is not None:
            self._del_func()
        self.destroy_move_menu()

        if self._start_x - 1 >= 0:
            self._start_x -= 1
            self._end_x -= 1

        self._target.set_coordinates(self._start_x, self._start_y, self._end_x, self._end_y)
        self._target.create()

    # Stretch

    def handle_up_stretch(self, event):
        if self._del_func() is not None:
            self._del_func()

        if self._start_y - 1 >= 0:
            self._start_y -= 1

        self._target.set_coordinates(self._start_x, self._start_y, self._end_x, self._end_y)
        self._target.create()

    def handle_right_stretch(self, event):
        if self._del_func() is not None:
            self._del_func()

        canvas_width = self._master.winfo_width()
        if self._end_x + 1 <= canvas_width:
            self._end_x += 1

        self._target.set_coordinates(self._start_x, self._start_y, self._end_x, self._end_y)
        self._target.create()

    def handle_down_stretch(self, event):
        if self._del_func() is not None:
            self._del_func()

        canvas_height = self._master.winfo_height()
        if self._end_y + 1 <= canvas_height:
            self._end_y += 1

        self._target.set_coordinates(self._start_x, self._start_y, self._end_x, self._end_y)
        self._target.create()

    def handle_left_stretch(self, event):
        if self._del_func() is not None:
            self._del_func()

        if self._start_x - 1 >= 0:
            self._start_x -= 1

        self._target.set_coordinates(self._start_x, self._start_y, self._end_x, self._end_y)
        self._target.create()

    # Destroy

    def destroy_move_menu(self):
        for i in range(9):
            self._master.delete(f"button_{i}")

    def __del__(self):
        self.destroy_move_menu()
