import cv2

class ROISetter:
    def __init__(self):
        # HARDCODED ROIs based on your previous selection
        self.sunscreen_roi = (620, 813, 300, 326)   # Your left square
        self.control_roi = (1240, 773, 300, 373)    # Your between squares
        print("Using fixed ROIs:")
        print(f"  Sunscreen: {self.sunscreen_roi}")
        print(f"  Control: {self.control_roi}")
    
    def set_rois(self, reference_image):
        """No longer interactive - just use fixed ROIs"""
        # Optional: Visualize the ROIs for verification
        img_with_rois = reference_image.copy()
        
        # Draw sunscreen ROI (green)
        x, y, w, h = self.sunscreen_roi
        cv2.rectangle(img_with_rois, (x, y), (x+w, y+h), (0, 255, 0), 3)
        
        # Draw control ROI (red)  
        x, y, w, h = self.control_roi
        cv2.rectangle(img_with_rois, (x, y), (x+w, y+h), (0, 0, 255), 3)
        
        # Show the image with ROIs (optional)
        cv2.imshow("Fixed ROIs", cv2.resize(img_with_rois, (800, 600)))
        cv2.waitKey(1000)  # Show for 1 second
        cv2.destroyAllWindows()
        
        return self.sunscreen_roi, self.control_roi
