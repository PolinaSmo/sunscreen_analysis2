import cv2
import numpy as np
import json
from pathlib import Path

class ROIDragger:
    def __init__(self, roi_size=(300, 300)):
        self.roi_size = roi_size  # (width, height)
        self.current_roi = None
        self.dragging = False
        self.selections = {}  # Store selections per image
    
    def select_roi_interactive(self, image, image_name, window_name="Drag ROI"):
        img_display = image.copy()
        h, w = img_display.shape[:2]
        
        #default starting position (making it center of the image)
        default_x = w // 2 - self.roi_size[0] // 2
        default_y = h // 2 - self.roi_size[1] // 2
        self.current_roi = [default_x, default_y, self.roi_size[0], self.roi_size[1]]
        
        def mouse_callback(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:
                rx, ry, rw, rh = self.current_roi
                if rx <= x <= rx + rw and ry <= y <= ry + rh:
                    self.dragging = True
                    self.drag_offset = (x - rx, y - ry)
            
            elif event == cv2.EVENT_MOUSEMOVE and self.dragging:
                # moves roi with mouse
                new_x = x - self.drag_offset[0]
                new_y = y - self.drag_offset[1]
                
                new_x = max(0, min(new_x, w - rw))
                new_y = max(0, min(new_y, h - rh))
                
                self.current_roi = [new_x, new_y, rw, rh]
            
            elif event == cv2.EVENT_LBUTTONUP:
                self.dragging = False
        
        cv2.namedWindow(window_name)
        cv2.setMouseCallback(window_name, mouse_callback)
        
        print(f"\n=== Selecting ROI for {image_name} ===")
        print("Drag the green square to desired position")
        print("Press SPACE to confirm, 'r' to reset, ESC to cancel")
        
        while True:
            display_img = img_display.copy()
            x, y, w, h = self.current_roi
            
            cv2.rectangle(display_img, (x, y), (x + w, y + h), (0, 255, 0), 3)
            center_x, center_y = x + w // 2, y + h // 2
            cv2.circle(display_img, (center_x, center_y), 5, (0, 0, 255), -1)
            
            cv2.putText(display_img, f"ROI: ({x},{y})", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(display_img, f"Size: {w}x{h}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            cv2.putText(display_img, "Drag to move | SPACE: Save | ESC: Cancel", (10, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            cv2.imshow(window_name, display_img)
            
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord(' '): 
                cv2.destroyWindow(window_name)
                self.selections[image_name] = tuple(self.current_roi)
                print(f"✓ ROI saved for {image_name}: {self.current_roi}")
                return tuple(self.current_roi)
            
            elif key == ord('r'):
                self.current_roi = [default_x, default_y, self.roi_size[0], self.roi_size[1]]
            
            elif key == 27:  # esc key is 27
                cv2.destroyWindow(window_name)
                return None
    
    def save_selections(self, filename="roi_positions.json"):
        """Save all ROI positions to JSON file"""
        Path("config").mkdir(exist_ok=True)
        with open(f"config/{filename}", 'w') as f:
            json.dump(self.selections, f, indent=2)
        print(f"ROI positions saved to config/{filename}")
    
    def load_selections(self, filename="roi_positions.json"):
        """Load previously saved ROI positions"""
        try:
            with open(f"config/{filename}", 'r') as f:
                self.selections = json.load(f)
            print(f"Loaded {len(self.selections)} ROI positions")
            return self.selections
        except FileNotFoundError:
            print("No saved ROI positions found")
            return {}