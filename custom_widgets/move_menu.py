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
            del_func: Union[Callable[[], None], None] = None,
            limits: bool = True):

        self._target_min_size = target.get_min_size()
        self._target_symmetry = target.get_symmetry()
        self._corner_button_max_size = corner_button_max_size
        self._additional_func = additional_func
        self._del_func = del_func
        self._limits = limits

        self._end_y = [0]
        self._end_x = [0]
        self._start_y = [0]
        self._start_x = [0]

        self._target = target
        self._master = master
        self._screenshot = screenshot

        self._click_offset_y = None
        self._click_offset_x = None
        self._initial_target_height = None
        self._initial_target_width = None

    def _create_symmetrical_move_menu(self):

        corners_coordinates = self._target.get_corners_coordinates()
        self._start_x[0], self._end_x[0] = corners_coordinates[0][0], corners_coordinates[1][0]
        self._start_y[0], self._end_y[0] = corners_coordinates[0][1], corners_coordinates[1][1]

        if self._target.get_width() <= 5 or self._target.get_height() <= 5:
            corners_coordinates = corners_coordinates[:2]

        for i, position in enumerate(corners_coordinates):
            self._create_move_button(position, "corner", button_index=i + 1)

        if self._target.get_width() > 5 and self._target.get_height() > 5:
            coordinate_indices = [0, 0, 3, 2]
            orientations = ['horizontal', 'vertical', 'horizontal', 'vertical']
            button_indices = [5, 6, 7, 8]

            for coord_index, orientation, button_index in zip(coordinate_indices, orientations, button_indices):
                self._create_move_button(corners_coordinates[coord_index], "side", side=orientation,
                                         button_index=button_index)

        center_position = [self._start_x[0] + self._target.get_width() / 2,
                           self._end_y[0] - self._target.get_height() / 2]
        self._create_move_button(center_position, "center", button_index=0)

    def _create_unsymmetrical_move_menu(self):

        corners_coordinates = self._target.get_current_corners_coordinates()
        self._start_x[0], self._end_x[0] = corners_coordinates[0][0], corners_coordinates[1][0]
        self._start_y[0], self._end_y[0] = corners_coordinates[0][1], corners_coordinates[1][1]

        if self._target.get_width() <= 5 or self._target.get_height() <= 5:
            corners_coordinates = corners_coordinates[:2]

        for i, position in enumerate(corners_coordinates):
            self._create_unsymmetrical_move_button(position, "corner", button_index=i + 1)

        if self._target.get_width() > 5 and self._target.get_height() > 5:
            corners_coordinates = self._target.get_corners_coordinates()
            coordinate_indices = [0, 0, 3, 2]
            orientations = ['horizontal', 'vertical', 'horizontal', 'vertical']
            button_indices = [5, 6, 7, 8]

            for coord_index, orientation, button_index in zip(coordinate_indices, orientations, button_indices):
                self._create_unsymmetrical_move_button(corners_coordinates[coord_index], "side", side=orientation,
                                         button_index=button_index)

        corners_coordinates = self._target.get_corners_coordinates()

        center_position = [corners_coordinates[0][0], corners_coordinates[0][1]]
        self._create_unsymmetrical_move_button(center_position, "center", button_index=0)

    def _create_unsymmetrical_move_button(self, position, button_type: str, side: str = None,
                            button_index: int = None):
        x = position[0]
        y = position[1]

        target_width = self._target.get_width()
        target_height = self._target.get_height()

        width = height = x_offset = y_offset = 0

        cursor = None

        if button_type == "center":
            cursor = "size"

            x_offset = int(min(int(target_width / 4), self._corner_button_max_size) / 2)
            y_offset = int(min(int(target_height / 4), self._corner_button_max_size) / 2)

            x += x_offset
            y += y_offset
            width = int(target_width - (x_offset * 2))
            height = int(target_height - (y_offset * 2))

        elif button_type == "side":
            if side == "horizontal":
                cursor = 'sb_v_double_arrow'
                x_offset = int(min(int(target_width / 4), self._corner_button_max_size) +
                               min(int((self._end_x[0] - self._start_x[0]) / 4),
                                   self._corner_button_max_size) / 2)
                y_offset = int(min(int(target_height / 4), self._corner_button_max_size) / 2)

                x += x_offset
                y += y_offset
                width = int(self._end_x[0] - self._start_x[0] -
                            min(int((self._end_x[0] - self._start_x[0]) / 4),
                                self._corner_button_max_size))
                height = min(int(target_height / 4), self._corner_button_max_size)
            elif side == "vertical":
                cursor = 'sb_h_double_arrow'
                x_offset = int(min(int(target_width / 4), self._corner_button_max_size) -
                               min(int(target_width / 4), self._corner_button_max_size) / 2)
                y_offset = int(min(int(target_height / 4), self._corner_button_max_size) +
                               min(int(target_height / 4), self._corner_button_max_size) / 2)

                x += x_offset
                y += y_offset

                width = int(min(int(target_width / 4), self._corner_button_max_size))
                height = int(target_height - min(int(target_height / 4), self._corner_button_max_size))

            x_offset = min(int(target_width / 4), self._corner_button_max_size)
            y_offset = min(int(target_height / 4), self._corner_button_max_size)
        elif button_type == "corner":
            if button_index == 1 or button_index == 2:
                cursor = "size_nw_se"
            elif button_index == 3 or button_index == 4:
                cursor = "size_ne_sw"
            width = min(int(abs(self._end_x[0] - self._start_x[0]) / 4), self._corner_button_max_size)
            height = min(int(abs(self._end_y[0] - self._start_y[0]) / 4), self._corner_button_max_size)

            x_offset = width / 2
            y_offset = height / 2

        if width <= 5:
            width = 5
            x -= 2

        if height <= 5:
            height = 5
            y -= 2

        screenshot = self._screenshot.crop((x - x_offset, y - y_offset, x - x_offset + width, y - y_offset + height))
        resized_screenshot = ImageTk.PhotoImage(screenshot.resize((width, height)))

        button = self._master.create_image(
            x - x_offset, y - y_offset, image=resized_screenshot, tags=f"button_{button_index}", anchor="nw"
        )

        self._master.tag_bind(f"button_{button_index}", "<Enter>", lambda event: self._master.config(cursor=cursor))
        self._master.tag_bind(f"button_{button_index}", "<Leave>", lambda event: self._master.config(cursor=""))
        self._master.tag_bind(f"button_{button_index}", "<Button-1>",
                              lambda event: self._bind_move_button(event, button_index, x, y))

        return button

    def _create_move_button(self, position, button_type: str, side: str = None,
                            button_index: int = None):
        x = position[0]
        y = position[1]

        target_width = self._target.get_width()
        target_height = self._target.get_height()

        width = height = x_offset = y_offset = 0

        cursor = None

        if button_type == "center":
            cursor = "size"

            x_offset = int(min(int(target_width / 4), self._corner_button_max_size) / 2)
            y_offset = int(min(int(target_height / 4), self._corner_button_max_size) / 2)

            x += x_offset
            y += y_offset
            width = int(target_width - (x_offset * 2))
            height = int(target_height - (y_offset * 2))

            x_offset = target_width / 2
            y_offset = target_height / 2
        elif button_type == "side":
            if side == "horizontal":
                cursor = 'sb_v_double_arrow'
                x_offset = int(min(int(target_width / 4), self._corner_button_max_size) +
                               min(int((self._end_x[0] - self._start_x[0]) / 4),
                                   self._corner_button_max_size) / 2)
                y_offset = int(min(int(target_height / 4), self._corner_button_max_size) / 2)

                x += x_offset
                y += y_offset
                width = int(self._end_x[0] - self._start_x[0] -
                            min(int((self._end_x[0] - self._start_x[0]) / 4),
                                self._corner_button_max_size))
                height = min(int(target_height / 4), self._corner_button_max_size)
            elif side == "vertical":
                cursor = 'sb_h_double_arrow'
                x_offset = int(min(int(target_width / 4), self._corner_button_max_size) -
                               min(int(target_width / 4), self._corner_button_max_size) / 2)
                y_offset = int(min(int(target_height / 4), self._corner_button_max_size) +
                               min(int(target_height / 4), self._corner_button_max_size) / 2)

                x += x_offset
                y += y_offset

                width = int(min(int(target_width / 4), self._corner_button_max_size))
                height = int(target_height - min(int(target_height / 4), self._corner_button_max_size))

            x_offset = min(int(target_width / 4), self._corner_button_max_size)
            y_offset = min(int(target_height / 4), self._corner_button_max_size)
        elif button_type == "corner":
            if button_index == 1 or button_index == 2:
                cursor = "size_nw_se"
            elif button_index == 3 or button_index == 4:
                cursor = "size_ne_sw"
            width = min(int((self._end_x[0] - self._start_x[0]) / 4), self._corner_button_max_size)
            height = min(int((self._end_y[0] - self._start_y[0]) / 4), self._corner_button_max_size)

            x_offset = width / 2
            y_offset = height / 2

        if width <= 5:
            width = 5
            x -= 2

        if height <= 5:
            height = 5
            y -= 2

        screenshot = self._screenshot.crop((x - x_offset, y - y_offset, x - x_offset + width, y - y_offset + height))
        resized_screenshot = ImageTk.PhotoImage(screenshot.resize((width, height)))
        button = self._master.create_image(
            x - x_offset, y - y_offset, image=resized_screenshot, tags=f"button_{button_index}", anchor="nw"
        )

        self._master.tag_bind(f"button_{button_index}", "<Enter>", lambda event: self._master.config(cursor=cursor))
        self._master.tag_bind(f"button_{button_index}", "<Leave>", lambda event: self._master.config(cursor=""))
        self._master.tag_bind(f"button_{button_index}", "<Button-1>",
                              lambda event: self._bind_move_button(event, button_index, x, y))

        return button

    def _bind_move_button(self, event, button_index, x, y):
        if self._del_func() is not None:
            self._del_func()

        self.destroy()

        if button_index == 0:
            self._bind_center(x, y)
        elif 1 <= button_index <= 4:
            self._bind__corners(button_index)
        elif 5 <= button_index <= 8:
            self._bind_side(button_index)

        self._master.tag_unbind(f"button_{button_index}", "<Leave>")
        self._master.tag_unbind(f"button_{button_index}", "<Button-1>")

    def _bind_center(self, x: int, y: int):
        self._master.bind("<B1-Motion>", lambda event: self._move(event.x, event.y, x, y))
        self._master.bind("<ButtonRelease-1>", self.create)

    def _bind_side(self, side: int):
        self._master.bind("<B1-Motion>", lambda event: self._stretch_sides(event.x, event.y, side))
        self._master.bind("<ButtonRelease-1>", self.create)

    def _bind__corners(self, corner: int):

        self._master.bind("<B1-Motion>", lambda event: self._stretch_corners(event.x, event.y, corner))
        self._master.bind("<ButtonRelease-1>", self.create)

    def _move(self, cursor_x, cursor_y, x: int, y: int):
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

        if not self._target_symmetry:
            x += self._initial_target_width / 2
            y += self._initial_target_height / 2

        if x - self._initial_target_width + cursor_x >= 0 and x + self._initial_target_width <= canvas_width:
            if self._start_x[0] < self._end_x[0]:
                self._start_x[0] = x - self._initial_target_width + cursor_x
                self._end_x[0] = x + cursor_x
            else:
                self._start_x[0] = x + cursor_x
                self._end_x[0] = x - self._initial_target_width + cursor_x

        if x - self._initial_target_width + cursor_x < 0:
            if self._start_x[0] < self._end_x[0]:
                self._start_x[0] = 0
                self._end_x[0] = self._initial_target_width
            else:
                self._start_x[0] = self._initial_target_width
                self._end_x[0] = 0
        elif x + cursor_x > canvas_width:
            if self._start_x[0] < self._end_x[0]:
                self._start_x[0] = canvas_width - self._initial_target_width
                self._end_x[0] = canvas_width
            else:
                self._start_x[0] = canvas_width
                self._end_x[0] = canvas_width - self._initial_target_width

        if cursor_y + y - self._initial_target_height >= 0 and cursor_y + y <= canvas_height:
            if self._start_y[0] < self._end_y[0]:
                self._start_y[0] = cursor_y + y - self._initial_target_height
                self._end_y[0] = cursor_y + y
            else:
                self._start_y[0] = cursor_y + y
                self._end_y[0] = cursor_y + y - self._initial_target_height

        if cursor_y + y - self._initial_target_height < 0:
            if self._start_y[0] < self._end_y[0]:
                self._start_y[0] = 0
                self._end_y[0] = self._initial_target_height
            else:
                self._start_y[0] = self._initial_target_height
                self._end_y[0] = 0
        elif cursor_y + y > canvas_height:
            if self._start_y[0] < self._end_y[0]:
                self._start_y[0] = canvas_height - self._initial_target_height
                self._end_y[0] = canvas_height
            else:
                self._start_y[0] = canvas_height
                self._end_y[0] = canvas_height - self._initial_target_height

        self._target.set_coordinates(self._start_x[0], self._start_y[0], self._end_x[0], self._end_y[0])
        self._target.create()

    def _stretch_sides(self, cursor_x, cursor_y, side: int):

        def _stretch_top_side(top_y, bottom_y):
            if top_y[0] <= bottom_y[0] - self._target_min_size:
                top_y[0] = cursor_y

            if top_y[0] > bottom_y[0] - self._target_min_size:
                top_y[0] = bottom_y[0] - self._target_min_size

        def _stretch_bottom_side(top_y, bottom_y):
            if bottom_y[0] >= top_y[0] + self._target_min_size:
                bottom_y[0] = cursor_y

            if bottom_y[0] < top_y[0] + self._target_min_size:
                bottom_y[0] = top_y[0] + self._target_min_size

        def _stretch_left_side(left_x, right_x):
            if left_x[0] <= right_x[0] - self._target_min_size:
                left_x[0] = cursor_x

            if left_x[0] > right_x[0] - self._target_min_size:
                left_x[0] = right_x[0] - self._target_min_size

        def _stretch_right_side(left_x, right_x):
            if right_x[0] >= left_x[0] + self._target_min_size:
                right_x[0] = cursor_x

            if right_x[0] < left_x[0] + self._target_min_size:
                right_x[0] = left_x[0] + self._target_min_size

        match side:
            case 5:
                if self._start_y[0] < self._end_y[0]:
                    _stretch_top_side(self._start_y, self._end_y)
                else:
                    _stretch_top_side(self._end_y, self._start_y)
            case 6:
                if self._start_x[0] < self._end_x[0]:
                    _stretch_left_side(self._start_x, self._end_x)
                else:
                    _stretch_left_side(self._end_x, self._start_x)
            case 7:
                if self._start_y[0] < self._end_y[0]:
                    _stretch_bottom_side(self._start_y, self._end_y)
                else:
                    _stretch_bottom_side(self._end_y, self._start_y)
            case 8:
                if self._start_x[0] < self._end_x[0]:
                    _stretch_right_side(self._start_x, self._end_x)
                else:
                    _stretch_right_side(self._end_x, self._start_x)

        self._target.set_coordinates(self._start_x[0], self._start_y[0], self._end_x[0], self._end_y[0])
        self._target.create()

    def _stretch_corners(self, cursor_x, cursor_y, corner: int):

        match corner:
            case 1:
                if self._limits:
                    if self._start_x[0] <= self._end_x[0] - self._target_min_size:
                        self._start_x[0] = cursor_x

                    if self._start_x[0] > self._end_x[0] - self._target_min_size:
                        self._start_x[0] = self._end_x[0] - self._target_min_size

                    if self._start_y[0] <= self._end_y[0] - self._target_min_size:
                        self._start_y[0] = cursor_y

                    if self._start_y[0] > self._end_y[0] - self._target_min_size:
                        self._start_y[0] = self._end_y[0] - self._target_min_size
                else:
                    self._start_x[0] = cursor_x
                    self._start_y[0] = cursor_y
            case 2:
                if self._limits:
                    if self._end_x[0] >= self._start_x[0] + self._target_min_size:
                        self._end_x[0] = cursor_x

                    if self._end_x[0] < self._start_x[0] + self._target_min_size:
                        self._end_x[0] = self._start_x[0] + self._target_min_size

                    if self._end_y[0] >= self._start_y[0] + self._target_min_size:
                        self._end_y[0] = cursor_y

                    if self._end_y[0] < self._start_y[0] + self._target_min_size:
                        self._end_y[0] = self._start_y[0] + self._target_min_size
                else:
                    self._end_x[0] = cursor_x
                    self._end_y[0] = cursor_y
            case 3:
                if self._limits:
                    if self._end_x[0] >= self._start_x[0] + self._target_min_size:
                        self._end_x[0] = cursor_x

                    if self._end_x[0] < self._start_x[0] + self._target_min_size:
                        self._end_x[0] = self._start_x[0] + self._target_min_size

                    if self._start_y[0] <= self._end_y[0] - self._target_min_size:
                        self._start_y[0] = cursor_y

                    if self._start_y[0] > self._end_y[0] - self._target_min_size:
                        self._start_y[0] = self._end_y[0] - self._target_min_size
                else:
                    self._end_x[0] = cursor_x
                    self._start_y[0] = cursor_y
            case 4:
                if self._limits:
                    if self._start_x[0] <= self._end_x[0] - self._target_min_size:
                        self._start_x[0] = cursor_x

                    if self._start_x[0] > self._end_x[0] - self._target_min_size:
                        self._start_x[0] = self._end_x[0] - self._target_min_size

                    if self._end_y[0] >= self._start_y[0] + self._target_min_size:
                        self._end_y[0] = cursor_y

                    if self._end_y[0] < self._start_y[0] + self._target_min_size:
                        self._end_y[0] = self._start_y[0] + self._target_min_size
                else:
                    self._start_x[0] = cursor_x
                    self._end_y[0] = cursor_y

        self._target.set_coordinates(self._start_x[0], self._start_y[0], self._end_x[0], self._end_y[0])
        self._target.create()

    def create(self, event=None):
        if self._target_symmetry:
            self._create_symmetrical_move_menu()
        else:
            self._create_unsymmetrical_move_menu()

        self._click_offset_y = None
        self._click_offset_x = None

        self._initial_target_height = None
        self._initial_target_width = None
        if self._additional_func is not None:
            self._additional_func()

        self.menu_tag_rise()

    def handle_up_move(self, event):
        if self._del_func() is not None:
            self._del_func()
        self.destroy()

        if self._start_y[0] - 1 >= 0:
            self._start_y[0] -= 1
            self._end_y[0] -= 1

        self._target.set_coordinates(self._start_x[0], self._start_y[0], self._end_x[0], self._end_y[0])
        self._target.create()

    # Move
    def handle_right_move(self, event):
        if self._del_func() is not None:
            self._del_func()
        self.destroy()

        canvas_width = self._master.winfo_width()
        if self._end_x[0] + 1 <= canvas_width:
            self._start_x[0] += 1
            self._end_x[0] += 1

        self._target.set_coordinates(self._start_x[0], self._start_y[0], self._end_x[0], self._end_y[0])
        self._target.create()

    def handle_down_move(self, event):
        if self._del_func() is not None:
            self._del_func()
        self.destroy()

        canvas_height = self._master.winfo_height()
        if self._end_y[0] + 1 <= canvas_height:
            self._start_y[0] += 1
            self._end_y[0] += 1

        self._target.set_coordinates(self._start_x[0], self._start_y[0], self._end_x[0], self._end_y[0])
        self._target.create()

    def handle_left_move(self, event):
        if self._del_func() is not None:
            self._del_func()
        self.destroy()

        if self._start_x[0] - 1 >= 0:
            self._start_x[0] -= 1
            self._end_x[0] -= 1

        self._target.set_coordinates(self._start_x[0], self._start_y[0], self._end_x[0], self._end_y[0])
        self._target.create()

    def handle_up_stretch(self, event):
        if self._del_func() is not None:
            self._del_func()

        if self._start_y[0] - 1 >= 0:
            self._start_y[0] -= 1

        self._target.set_coordinates(self._start_x[0], self._start_y[0], self._end_x[0], self._end_y[0])
        self._target.create()

    # Stretch

    def handle_right_stretch(self, event):
        if self._del_func() is not None:
            self._del_func()

        canvas_width = self._master.winfo_width()
        if self._end_x[0] + 1 <= canvas_width:
            self._end_x[0] += 1

        self._target.set_coordinates(self._start_x[0], self._start_y[0], self._end_x[0], self._end_y[0])
        self._target.create()

    def handle_down_stretch(self, event):
        if self._del_func() is not None:
            self._del_func()

        canvas_height = self._master.winfo_height()
        if self._end_y[0] + 1 <= canvas_height:
            self._end_y[0] += 1

        self._target.set_coordinates(self._start_x[0], self._start_y[0], self._end_x[0], self._end_y[0])
        self._target.create()

    def handle_left_stretch(self, event):
        if self._del_func() is not None:
            self._del_func()

        if self._start_x[0] - 1 >= 0:
            self._start_x[0] -= 1

        self._target.set_coordinates(self._start_x[0], self._start_y[0], self._end_x[0], self._end_y[0])
        self._target.create()

    def set_target(self, target):
        self._target = target
        self._target_min_size = target.get_min_size()
        self._target_symmetry = target.get_symmetry()

    def set_limits(self, limits: bool):
        self._limits = limits

    def menu_tag_rise(self):
        for i in range(9):
            self._master.tag_raise(f"button_{i}")

    # Destroy
    def destroy(self):
        for i in range(9):
            self._master.delete(f"button_{i}")

    def __del__(self):
        self.destroy()
