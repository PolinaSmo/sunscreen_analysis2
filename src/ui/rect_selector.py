import cv2
import matplotlib.pyplot as plt
from matplotlib.widgets import RectangleSelector

class RectangleROISelector:
    def __init__(self, image_bgr):
        self.image = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        self.fig, self.ax = plt.subplots(figsize=(10, 8))
        self.ax.imshow(self.image)
        self.ax.set_title("Draw a rectangle. Press Enter when done.")

        self.rect_selector = RectangleSelector(
            self.ax, self.on_select,
            useblit=True,
            button=[1],          # left click
            minspanx=5, minspany=5,
            spancoords='data',
            interactive=True,
            props=dict(facecolor='none', edgecolor='green', alpha=0.8, linewidth=2)
        )
        self.roi = None
        self.finished = False
        self.fig.canvas.mpl_connect('key_press_event', self.on_key)

    def on_select(self, eclick, erelease):
        x1, y1 = eclick.xdata, eclick.ydata
        x2, y2 = erelease.xdata, erelease.ydata
        self.roi = (min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))

    def on_key(self, event):
        if event.key == 'enter':
            self.finished = True
            plt.close(self.fig)

    def get_roi(self):
        plt.show(block=True)
        if self.roi is None:
            return None
        x, y, w, h = self.roi
        x = int(max(0, x))
        y = int(max(0, y))
        w = int(min(w, self.image.shape[1] - x))
        h = int(min(h, self.image.shape[0] - y))
        return (x, y, w, h)