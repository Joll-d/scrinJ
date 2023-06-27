from custom_widgets.canvas.canvas_element import CanvasElement


class Circle(CanvasElement):

    def create(self):

        if self._element:
            self._canvas.delete(self._element)

        self._element = self._canvas.create_oval(
            self._start_x, self._start_y, self._end_x, self._end_y,
            outline=self._color, width=self._width, fill="", tags=self._tags, dash=self._dash
        )

        self._canvas.tag_raise(self._element)
