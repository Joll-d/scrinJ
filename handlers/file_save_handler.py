import time
from tkinter.filedialog import asksaveasfilename


def save_image_to_file(screenshot):
    ticks = str(time.time()).replace('.', '')[:13]
    default_filename = f"{ticks}_screenshot.png"
    save_path = asksaveasfilename(defaultextension='', filetypes=[("All Files", "*.*")], initialfile=default_filename)

    if save_path:
        screenshot.save(save_path)