from abc import ABC, abstractmethod


class CanvasElement(ABC):

    def __init__(
            self,
            canvas,
            _min_size: int = 20):

        self._min_size = _min_size
        self._start_x = 0
        self._start_y = 0
        self._end_x = 0
        self._end_y = 0
        self._element = None
        self._canvas = canvas

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

    def get_width(self) -> int:
        return abs(self._start_x - self._end_x)

    def get_height(self) -> int:
        return abs(self._start_y - self._end_y)

    def get_min_size(self) -> int:
        return self._min_size

    def expand_to_minimum_size(self):
        if self.get_width() < self._min_size:
            self._end_x = self._start_x + self._min_size
        if self.get_height() < self._min_size:
            self._end_y = self._start_y + self._min_size

