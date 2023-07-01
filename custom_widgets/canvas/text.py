from custom_widgets.canvas.canvas_element import CanvasElement


class Text(CanvasElement):

    def __init__(self, canvas, min_size: int = 10, color: hex = "#000000", width: int = 10, tags: str = ""):
        super().__init__(canvas, min_size=min_size, color=color, width=width, tags=tags)
        self._text = "Text"
        self._descriptions = True

    def create(self):

        if self._element:
            self._canvas.delete(self._element)
        self._element = self._canvas.create_text(
            self._start_x, self._start_y, text=self._text, fill=self._color, tags=self._tags,
            font=f'Helvetica {self._width} bold', anchor="nw"
        )

        self._canvas.tag_raise(self._element)

    def change_width(self, width):
        if self._width + width > 0:
            self._width += int(width)

    def add(self, symbol: str):
        if self._descriptions:
            self._text = ""
            self._descriptions = False
        self._text += symbol

    def subtract(self,):
        self._text = self._text[:-1]
