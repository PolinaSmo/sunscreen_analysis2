import cv2
import numpy as np
import json
from pathlib import Path


class ROIDragger:
    def __init__(self, roi_size=(300, 300)):
        self.roi_size = roi_size  # (width, height) in ORIGINAL image coordinates
        self.current_roi = None
        self.dragging = False
        self.selections = {}  # store selections per image
        self.scale_factor = 1.0
        self.display_size = None

    def select_roi_interactive(self, image, image_name, window_name="Drag ROI"):
        img_display = image.copy()
        h, w = img_display.shape[:2]

        # Resize for display (keeping aspect ratio)
        max_display_height = 700
        max_display_width = 1200

        # Calculate scaling factor
        scale_h = max_display_height / h
        scale_w = max_display_width / w
        self.scale_factor = min(scale_h, scale_w)

        display_h = int(h * self.scale_factor)
        display_w = int(w * self.scale_factor)
        self.display_size = (display_w, display_h)

        # Create resized image for display
        display_img_resized = cv2.resize(img_display, (display_w, display_h))

        # Calculate ROI size in display coordinates
        roi_w_display = int(self.roi_size[0] * self.scale_factor)
        roi_h_display = int(self.roi_size[1] * self.scale_factor)

        # Start ROI at center of display
        default_x = display_w // 2 - roi_w_display // 2
        default_y = display_h // 2 - roi_h_display // 2

        # Store display coordinates for dragging
        self.current_roi = [default_x, default_y, roi_w_display, roi_h_display]

        def mouse_callback(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:
                rx, ry, rw, rh = self.current_roi
                # Check if click is inside the ROI (in display coordinates)
                if rx <= x <= rx + rw and ry <= y <= ry + rh:
                    self.dragging = True
                    self.drag_offset_x = x - rx
                    self.drag_offset_y = y - ry
                    print(f"Started dragging at display coordinates ({x}, {y})")

            elif event == cv2.EVENT_MOUSEMOVE and self.dragging:
                # Calculate new position
                new_x = x - self.drag_offset_x
                new_y = y - self.drag_offset_y

                # Keep within display bounds
                new_x = max(0, min(new_x, display_w - roi_w_display))
                new_y = max(0, min(new_y, display_h - roi_h_display))

                self.current_roi = [new_x, new_y, roi_w_display, roi_h_display]

            elif event == cv2.EVENT_LBUTTONUP:
                self.dragging = False
                print(f"Stopped dragging at display coordinates {self.current_roi[:2]}")

        cv2.namedWindow(window_name)
        cv2.resizeWindow(window_name, display_w, display_h)
        cv2.setMouseCallback(window_name, mouse_callback)

        print(f"\nSelecting ROI for {image_name} \n")
        print(f"ROI Size: {self.roi_size[0]}x{self.roi_size[1]} pixels")
        print("Click and drag the green square to position it")
        print("Press SPACE to confirm, 'r' to reset, ESC to cancel")

        while True:
            display_copy = display_img_resized.copy()
            x, y, w_disp, h_disp = self.current_roi

            cv2.rectangle(display_copy, (x, y), (x + w_disp, y + h_disp), (0, 255, 0), 3)
            center_x, center_y = x + w_disp // 2, y + h_disp // 2 #center point just to have it
            cv2.circle(display_copy, (center_x, center_y), 5, (0, 0, 255), -1)

            # original image coordinates
            orig_x = int(x / self.scale_factor)
            orig_y = int(y / self.scale_factor)
            orig_w = int(w_disp / self.scale_factor)
            orig_h = int(h_disp / self.scale_factor)

            # Add instructions and info
            cv2.putText(display_copy, f"Original: ({orig_x}, {orig_y})", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(display_copy, f"Display: ({x}, {y})", (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(display_copy, "DRAG the green square | SPACE: Save | ESC: Cancel",
                        (10, display_h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.imshow(window_name, display_copy)
            key = cv2.waitKey(1) & 0xFF
            if key == ord(' '):  # space to confirm
                cv2.destroyWindow(window_name)
                # save og  coordinates
                final_roi = (orig_x, orig_y, orig_w, orig_h)
                self.selections[image_name] = final_roi
                print(f"✓ ROI saved for {image_name}: {final_roi}")
                return final_roi
            elif key == ord('r'):  # 'r' to reset to center
                self.current_roi = [default_x, default_y, roi_w_display, roi_h_display]
                print("ROI reset to center")
            elif key == 27:  # click esc key to cancel
                cv2.destroyWindow(window_name)
                print("ROI selection cancelled")
                return None

    def save_selections(self, filename="roi_positions.json"):
        Path("config").mkdir(exist_ok=True)
        with open(f"config/{filename}", 'w') as f:
            json.dump(self.selections, f, indent=2)
        print(f"✓ ROI positions saved to config/{filename}")

    def load_selections(self, filename="roi_positions.json"):
        """Load previously saved ROI positions"""
        try:
            with open(f"config/{filename}", 'r') as f:
                self.selections = json.load(f)
            print(f"✓ Loaded {len(self.selections)} ROI positions")
            return self.selections
        except FileNotFoundError:
            print("No saved ROI positions found")
            return {}