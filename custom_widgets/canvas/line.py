from custom_widgets.canvas.canvas_element import CanvasElement


class Line(CanvasElement):

    def create(self):

        if self._element:
            self._canvas.delete(self._element)

        self._element = self._canvas.create_line(
            self._start_x, self._start_y, self._end_x, self._end_y,
            fill=self._color, width=self._width, tags=self._tags, dash=self._dash
        )

        self._canvas.tag_raise(self._element)
