import cv2
import matplotlib.pyplot as plt
from matplotlib.widgets import RectangleSelector
import numpy as np


class RectangleROISelector:
    def __init__(self, image_bgr):
        self.image = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        self.roi = None
        self.finished = False

        self.fig, self.ax = plt.subplots(figsize=(12, 9))
        self.ax.imshow(self.image)
        self.ax.set_title("Draw a rectangle. Press Enter when done.")

        self.rect_selector = RectangleSelector(
            self.ax, self.on_select,
            useblit=True, button=[1], minspanx=5, minspany=5,
            spancoords='data', interactive=True,
            props=dict(facecolor='none', edgecolor='green', alpha=0.8, linewidth=2)
        )

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


class SameSizeROISelector:
    def __init__(self, image_bgr):
        self.image = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        self.first_roi = None
        self.fixed_size = None
        self.current_roi = None
        self.current_patch = None
        self.dragging = False
        self.drag_offset = (0, 0)

    def select_roi(self, prompt, is_first=True):
        fig, ax = plt.subplots(figsize=(12, 9))
        ax.imshow(self.image)

        if is_first:
            ax.set_title(f"{prompt} - Click and drag to draw rectangle")
            self.result = None
            self.finished = False

            def on_select(eclick, erelease):
                x1, y1 = eclick.xdata, eclick.ydata
                x2, y2 = erelease.xdata, erelease.ydata
                x = min(x1, x2)
                y = min(y1, y2)
                w = abs(x2 - x1)
                h = abs(y2 - y1)
                if w > 0 and h > 0:
                    self.first_roi = (int(x), int(y), int(w), int(h))
                    self.fixed_size = (int(w), int(h))
                    self.result = self.first_roi
                    print(f"ROI size set to: {int(w)} x {int(h)}")

            selector = RectangleSelector(
                ax, on_select,
                useblit=True, button=[1], minspanx=5, minspany=5,
                spancoords='data', interactive=True,
                props=dict(facecolor='none', edgecolor='green', alpha=0.8, linewidth=2)
            )

            def on_key(event):
                if event.key == 'enter' and self.result is not None:
                    self.finished = True
                    plt.close(fig)
                elif event.key == 'escape':
                    self.result = None
                    self.finished = True
                    plt.close(fig)

            fig.canvas.mpl_connect('key_press_event', on_key)
            plt.show(block=True)
            return self.result

        else:
            # Second ROI - same size, just position
            ax.set_title(f"{prompt} - Size: {self.fixed_size[0]}x{self.fixed_size[1]}. Click and drag to position.")
            h_img, w_img = self.image.shape[:2]
            default_x = w_img // 2 - self.fixed_size[0] // 2
            default_y = h_img // 2 - self.fixed_size[1] // 2
            self.current_roi = [default_x, default_y, self.fixed_size[0], self.fixed_size[1]]

            rect = plt.Rectangle((default_x, default_y), self.fixed_size[0], self.fixed_size[1],
                                 fill=False, edgecolor='green', linewidth=2)
            ax.add_patch(rect)
            self.current_patch = rect

            self.dragging = False
            self.drag_offset = (0, 0)
            self.result = None
            self.finished = False

            def on_press(event):
                if event.inaxes != ax:
                    return
                x, y = event.xdata, event.ydata
                rx, ry, rw, rh = self.current_roi
                if rx <= x <= rx + rw and ry <= y <= ry + rh:
                    self.dragging = True
                    self.drag_offset = (x - rx, y - ry)

            def on_release(event):
                self.dragging = False

            def on_motion(event):
                if not self.dragging or event.inaxes != ax:
                    return
                new_x = event.xdata - self.drag_offset[0]
                new_y = event.ydata - self.drag_offset[1]
                new_x = max(0, min(new_x, w_img - self.fixed_size[0]))
                new_y = max(0, min(new_y, h_img - self.fixed_size[1]))
                self.current_roi = [new_x, new_y, self.fixed_size[0], self.fixed_size[1]]
                self.current_patch.set_xy((new_x, new_y))
                fig.canvas.draw_idle()

            def on_key(event):
                if event.key == 'enter':
                    self.result = tuple(self.current_roi)
                    self.finished = True
                    plt.close(fig)
                elif event.key == 'escape':
                    self.result = None
                    self.finished = True
                    plt.close(fig)

            fig.canvas.mpl_connect('button_press_event', on_press)
            fig.canvas.mpl_connect('button_release_event', on_release)
            fig.canvas.mpl_connect('motion_notify_event', on_motion)
            fig.canvas.mpl_connect('key_press_event', on_key)

            plt.show(block=True)
            return self.result


def preview_rois_on_timepoints(images, rois, timepoints):
    from preview_utils import show_preview_grid
    return show_preview_grid(images, timepoints)