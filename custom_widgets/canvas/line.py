import tkinter as tk

from custom_widgets.canvas.canvas_element import CanvasElement


class Line(CanvasElement):
    def __init__(self, canvas, min_size: int = 10, color: hex = "#000000", width: int = 1, tags: str = "",
                 dash: tuple = (), symmetry: bool = False, is_arrow: bool = False):
        super().__init__(canvas, min_size=min_size, color=color, width=width, tags=tags, dash=dash, symmetry=symmetry)

        self.is_arrow = is_arrow
        if self.is_arrow:
            self._arrow = tk.LAST
            self._arrowshape = (8, 15, 8)
        else:
            self._arrow = ""
            self._arrowshape = (0, 0, 0)

    def create(self):
        if self._element:
            self._canvas.delete(self._element)

        self._element = self._canvas.create_line(
            self._start_x, self._start_y, self._end_x, self._end_y,
            fill=self._color, width=self._width, tags=self._tags, dash=self._dash, arrow=self._arrow,
            arrowshape=self._arrowshape
        )

        self._canvas.tag_raise(self._element)

    def switch_arrow(self):
        if not self.is_arrow:
            self._arrow = tk.LAST
            self._arrowshape = (8, 15, 8)
            self.is_arrow = True
        else:
            self._arrow = ""
            self._arrowshape = (0, 0, 0)
            self.is_arrow = False

    def switch_fill(self):
        pass
