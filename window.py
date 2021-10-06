import win32process
import win32gui


def _handler(handle, window):
    if window.handle is None and window.process.processInfo.pid in win32process.GetWindowThreadProcessId(handle):
        window.handle = handle

class Window:
    def __init__(self, process):
        self.process = process
        self.handle = None

    def findWindow(self):
        while self.handle is None:
            win32gui.EnumWindows(_handler, self)

    def windowInfo(self):
        rect = win32gui.GetWindowRect(self.handle)
        x, y = rect[0], rect[1]
        w, h = rect[2] - x, rect[3] - y
        return (x, y, w, h)
