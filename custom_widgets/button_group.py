import customtkinter as ctk
from typing import Union, Tuple, List, Dict, Callable, Optional, Sequence
import tkinter

from PIL import ImageTk, Image
from customtkinter import CTkImage


class ImageButtonGroup(ctk.CTkFrame):
    def __init__(self,
                 master: any,
                 width: int = 140,
                 height: int = 28,
                 corner_radius: Optional[int] = 5,
                 border_width: int = 0,
                 button_size: int = 20,
                 border_spacing: int = 0,

                 bg_color: Union[str, Tuple[str, str]] = "transparent",
                 images: Union[Sequence[Image.Image], None] = None,
                 fg_color: Optional[Union[str, Tuple[str, str]]] = None,
                 text_color: Optional[Union[str, Tuple[str, str]]] = None,
                 text_color_disabled: Optional[Union[str, Tuple[str, str]]] = None,
                 background_corner_colors: Union[Tuple[Union[str, Tuple[str, str]]], None] = None,

                 orientation: str = "horizontal",
                 font: Optional[Union[tuple, ctk.CTkFont]] = None,
                 values: Optional[list] = None,
                 command: Union[Callable[[str], None], None] = None,
                 state: str = "normal",
                 **kwargs):

        if values is None:
            values = []

        if values is not None and images is None:
            images = tuple([None] * len(values))

        if orientation == "horizontal":
            width = len(values) * button_size * 2
            height = button_size * 2
        elif orientation == "vertical":
            width = button_size * 2
            height = len(values) * button_size * 2

        super().__init__(master=master, bg_color=bg_color, width=width, height=height, **kwargs)

        self.buttons = []
        for i, (value, image) in enumerate(zip(values, images)):
            icon = ctk.CTkImage(light_image=image, dark_image=image, size=(button_size, button_size))

            button = ctk.CTkButton(self, text="", command=lambda v=value: command(v), width=button_size,
                                   height=button_size, corner_radius=corner_radius, border_width=border_width,
                                   border_spacing=border_spacing, fg_color=fg_color, text_color=text_color, state=state,
                                   font=font, text_color_disabled=text_color_disabled, image=icon,
                                   background_corner_colors=background_corner_colors)
            if orientation == "horizontal":
                button.grid(row=0, column=i)
            elif orientation == "vertical":
                button.grid(row=i, column=0)
            self.buttons.append(button)
