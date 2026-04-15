import cv2
import numpy as np
import json
from pathlib import Path

class ROIDragger:
    def __init__(self):
        self.rect = None          # (x, y, w, h) in original coordinates
        self.start_point = None
        self.dragging_rect = False
        self.drag_offset = (0, 0)
        self.scale_factor = 1.0
        self.display_size = None
        self.selections = {}       # store ROI per image name (for saving)

    def select_roi_interactive(self, image, image_name, window_name="Draw ROI"):
        """
        Let user draw a rectangle (click and drag) and optionally move it.
        Returns (x, y, w, h) in original image coordinates.
        """
        # Copy original image
        original = image.copy()
        h, w = original.shape[:2]

        # Compute display size (max 800 height, keep aspect)
        max_display_h = 700
        scale = max_display_h / h
        if w * scale > 1200:
            scale = 1200 / w
        self.scale_factor = scale
        display_h = int(h * scale)
        display_w = int(w * scale)

        display_img = cv2.resize(original, (display_w, display_h))

        # State variables
        self.rect = None
        self.start_point = None
        self.dragging_rect = False
        self.drag_offset = (0, 0)

        # Mouse callback
        def mouse_callback(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:
                # Check if we clicked inside an existing rectangle
                if self.rect is not None:
                    rx, ry, rw, rh = self.rect
                    rx_disp = int(rx * self.scale_factor)
                    ry_disp = int(ry * self.scale_factor)
                    rw_disp = int(rw * self.scale_factor)
                    rh_disp = int(rh * self.scale_factor)
                    if rx_disp <= x <= rx_disp + rw_disp and ry_disp <= y <= ry_disp + rh_disp:
                        self.dragging_rect = True
                        self.drag_offset = (x - rx_disp, y - ry_disp)
                        return
                # Start drawing a new rectangle
                self.start_point = (x, y)
                self.rect = None
                self.dragging_rect = False

            elif event == cv2.EVENT_MOUSEMOVE:
                if self.dragging_rect:
                    # Move existing rectangle
                    new_x_disp = x - self.drag_offset[0]
                    new_y_disp = y - self.drag_offset[1]
                    rw_disp = int(self.rect[2] * self.scale_factor)
                    rh_disp = int(self.rect[3] * self.scale_factor)
                    new_x_disp = max(0, min(new_x_disp, display_w - rw_disp))
                    new_y_disp = max(0, min(new_y_disp, display_h - rh_disp))
                    new_x = new_x_disp / self.scale_factor
                    new_y = new_y_disp / self.scale_factor
                    self.rect = (new_x, new_y, self.rect[2], self.rect[3])

            elif event == cv2.EVENT_LBUTTONUP:
                if self.start_point is not None and not self.dragging_rect:
                    # Finish drawing rectangle
                    x1, y1 = self.start_point
                    x2, y2 = x, y
                    x1, x2 = min(x1, x2), max(x1, x2)
                    y1, y2 = min(y1, y2), max(y1, y2)
                    orig_x = x1 / self.scale_factor
                    orig_y = y1 / self.scale_factor
                    orig_w = (x2 - x1) / self.scale_factor
                    orig_h = (y2 - y1) / self.scale_factor
                    orig_w = max(1, orig_w)
                    orig_h = max(1, orig_h)
                    self.rect = (orig_x, orig_y, orig_w, orig_h)
                    self.start_point = None
                elif self.dragging_rect:
                    self.dragging_rect = False

        cv2.namedWindow(window_name)
        cv2.setMouseCallback(window_name, mouse_callback)

        print(f"\n=== Selecting ROI for {image_name} ===")
        print("Click and drag to draw a rectangle.")
        print("Drag the rectangle to reposition it.")
        print("Press 'r' to clear and start over.")
        print("Press SPACE to confirm.")
        print("Press ESC to cancel.")

        while True:
            display_copy = display_img.copy()
            if self.rect is not None:
                rx, ry, rw, rh = self.rect
                rx_disp = int(rx * self.scale_factor)
                ry_disp = int(ry * self.scale_factor)
                rw_disp = int(rw * self.scale_factor)
                rh_disp = int(rh * self.scale_factor)
                cv2.rectangle(display_copy, (rx_disp, ry_disp),
                              (rx_disp + rw_disp, ry_disp + rh_disp),
                              (0, 255, 0), 2)
                cv2.putText(display_copy, f"Size: {int(rw)}x{int(rh)}",
                            (rx_disp, ry_disp - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            cv2.putText(display_copy, "Draw rectangle | Drag to move | r: reset | SPACE: confirm | ESC: cancel",
                        (10, display_h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

            cv2.imshow(window_name, display_copy)

            key = cv2.waitKey(1) & 0xFF
            if key == ord(' '):   # SPACE confirm
                if self.rect is not None:
                    cv2.destroyWindow(window_name)
                    # Ensure rectangle is within image bounds
                    x, y, w, h = self.rect
                    x = max(0, x)
                    y = max(0, y)
                    w = min(w, image.shape[1] - x)
                    h = min(h, image.shape[0] - y)
                    final_rect = (int(x), int(y), int(w), int(h))
                    print(f"✓ ROI saved for {image_name}: {final_rect}")
                    self.selections[image_name] = final_rect
                    return final_rect
                else:
                    print("No rectangle drawn yet. Please draw a rectangle.")
            elif key == ord('r'):   # reset
                self.rect = None
                self.start_point = None
                self.dragging_rect = False
                print("ROI cleared. Draw a new rectangle.")
            elif key == 27:         # ESC cancel
                cv2.destroyWindow(window_name)
                print("ROI selection cancelled.")
                return None

    def save_selections(self, filename="roi_positions.json"):
        """Save all ROI selections to a JSON file."""
        Path("config").mkdir(exist_ok=True)
        with open(f"config/{filename}", 'w') as f:
            json.dump(self.selections, f, indent=2)
        print(f"✓ ROI positions saved to config/{filename}")

    def load_selections(self, filename="roi_positions.json"):
        """Load previously saved ROI selections."""
        try:
            with open(f"config/{filename}", 'r') as f:
                self.selections = json.load(f)
            print(f"✓ Loaded {len(self.selections)} ROI positions")
            return self.selections
        except FileNotFoundError:
            print("No saved ROI positions found")
            return {}