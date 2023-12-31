from abc import ABC, abstractmethod


class CanvasElement(ABC):

    def __init__(
            self,
            canvas,
            min_size: int = 10,
            color: hex = "#000000",
            width: int = 1,
            tags: str = "",
            dash: tuple = (),
            symmetry: bool = True,
            is_dashed: bool = False,
            is_filled: bool = False):

        self._canvas = canvas

        self._min_size = min_size
        self._color = color
        self._width = width
        self._tags = tags
        self._dash = dash
        self._symmetry = symmetry
        self._fill = None

        self.is_filled = is_filled

        if self.is_filled:
            self._fill = self._color
        else:
            self._fill = ""
        self.is_dashed = is_dashed

        if self.is_dashed:
            self._dash = (5, 3)
        else:
            self._dash = ()

        self._start_x = 0
        self._start_y = 0
        self._end_x = 0
        self._end_y = 0

        self._element = None

    def set_coordinates(self, start_x: int = None, start_y: int = None, end_x: int = None, end_y: int = None):
        if start_x is not None:
            self._start_x = start_x
        if start_y is not None:
            self._start_y = start_y
        if end_x is not None:
            self._end_x = end_x
        if end_y is not None:
            self._end_y = end_y

    @abstractmethod
    def create(self):
        pass

    def get_corners_coordinates(self) -> list:
        x1, x2 = sorted([self._start_x, self._end_x])
        y1, y2 = sorted([self._start_y, self._end_y])
        corner1 = [x1, y1]
        corner2 = [x2, y2]
        corner3 = [x2, y1]
        corner4 = [x1, y2]
        return [corner1, corner2, corner3, corner4]

    def get_current_corners_coordinates(self) -> list:
        x1, x2 = [self._start_x, self._end_x]
        y1, y2 = [self._start_y, self._end_y]
        corner1 = [x1, y1]
        corner2 = [x2, y2]
        corner3 = [x2, y1]
        corner4 = [x1, y2]
        return [corner1, corner2, corner3, corner4]

    def get_width(self) -> int:
        return abs(self._start_x - self._end_x)

    def get_height(self) -> int:
        return abs(self._start_y - self._end_y)

    def get_min_size(self) -> int:
        return self._min_size

    def get_tags(self) -> str:
        return self._tags

    def get_element(self):
        return self._element

    def get_symmetry(self) -> bool:
        return self._symmetry

    def destroy(self):
        self._canvas.delete(self._element)

    def expand_to_minimum_size(self):
        if self.get_width() < self._min_size:
            self._end_x = self._start_x + self._min_size
        if self.get_height() < self._min_size:
            self._end_y = self._start_y + self._min_size

    def switch_dash(self):
        if not self.is_dashed:
            self._dash = (5, 3)
            self.is_dashed = True
        else:
            self._dash = ()
            self.is_dashed = False

    def switch_fill(self):
        if not self.is_filled:
            self._fill = self._color
            self.is_filled = True
        else:
            self._fill = ""
            self.is_filled = False
            
    def set_color(self, color: hex):
        self._color = color

    def change_width(self, width):
        if self._width + width > 0:
            self._width += width
