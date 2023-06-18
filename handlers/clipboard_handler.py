import io

import win32clipboard
from PIL import Image


def copy_screenshot_to_clipboard(screenshot: Image):

    output = io.BytesIO()
    screenshot.convert("RGB").save(output, "BMP")
    data = output.getvalue()[14:]
    output.close()

    send_to_clipboard(win32clipboard.CF_DIB, data)


def send_to_clipboard(clip_type: int, data: any) -> None:
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(clip_type, data)
    win32clipboard.CloseClipboard()
