from custom_widgets.canvas.canvas_element import CanvasElement


class RectangleOutsideDimming(CanvasElement):

    def create(self):

        if self._element:
            self._canvas.delete(self._element)
            self._canvas.delete("dimming_rect")

        self._element = self._canvas.create_rectangle(
            self._start_x, self._start_y, self._end_x, self._end_y,
            outline=self._color, width=self._width, fill="", tags="selection", dash=self._dash
        )

        corners_coordinates = self.get_corners_coordinates()

        self._create_outside_dimming(corners_coordinates)

        self._canvas.tag_raise(self._element)

    def _create_outside_dimming(self, corners_coordinates: list):
        x1, y1 = corners_coordinates[0][0], corners_coordinates[0][1]
        x2, y2 = corners_coordinates[1][0], corners_coordinates[1][1]

        dimming_rects = [
            (0, 0, self._canvas.winfo_width(), y1),  # Upper dimming rectangle
            (0, y2, self._canvas.winfo_width(), self._canvas.winfo_height()),  # Lower dimming rectangle
            (0, y1, x1, y2),  # Left dimming rectangle
            (x2, y1, self._canvas.winfo_width(), y2),  # Right dimming rectangle
        ]

        dimming_tags = "dimming_rect"

        for dimming_rect in dimming_rects:
            self._canvas.create_rectangle(
                *dimming_rect, fill="black", stipple="gray50", outline="", tags=dimming_tags
            )
        self._canvas.tag_raise(dimming_tags, self._element)

