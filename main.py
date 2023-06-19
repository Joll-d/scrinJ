import customtkinter as ctk
from PIL import ImageGrab

from GUI.screen_window import ScreenWindow
from handlers.clipboard_handler import copy_screenshot_to_clipboard
from handlers.file_save_handler import save_image_to_file


class CustomApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.geometry("600x500")

        self.frame = ctk.CTkFrame(self)
        self.frame.pack()

        self.label = ctk.CTkLabel(self.frame, text="Hello!")
        self.copy_image = ctk.CTkButton(self.frame, text="Click me", command=self.copy_image)
        self.save_button = ctk.CTkButton(self.frame, text="Save image", command=self.save_image)
        self.bbox_button = ctk.CTkButton(self.frame, text="Capture BBox", command=self.capture_bbox)

        self.label.pack()
        self.copy_image.pack()
        self.save_button.pack()
        self.bbox_button.pack()

        self.frame.place(relx=0.5, rely=0.5, anchor="center")

    def copy_image(self):
        # Capture the screenshot
        screenshot = ImageGrab.grab()

        copy_screenshot_to_clipboard(screenshot)

    def save_image(self):
        # Capture the screenshot
        screenshot = ImageGrab.grab()

        save_image_to_file(screenshot)

    def capture_bbox(self):
        bbox_capture = ScreenWindow(self)


if __name__ == "__main__":
    app = CustomApp()
    app.mainloop()
