import cv2

class ROISelector:
    def __init__(self):
        self.sunscreen_roi = None
        self.control_roi = None
    
    def select_roi(self, image, roi_name="ROI", scale=0.3):
        img = image.copy()
        #grayscale
        img_display = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        #display is too big automatically, resize for now to select ROIs
        display_h, display_w = img_display.shape
        new_w = int(display_w * scale)
        new_h = int(display_h * scale)
        img_resized = cv2.resize(img_display, (new_w, new_h))
        print(f"Select {roi_name} - press ENTER when done, 'c' to cancel")
        print(f"Image scaled to {int(scale*100)}% for display")
        roi_scaled = cv2.selectROI(f"Select {roi_name}", img_resized, fromCenter=False)
        cv2.destroyAllWindows()

        x, y, w, h = roi_scaled
        roi = (int(x/scale), int(y/scale), int(w/scale), int(h/scale))
        return roi
    
    def set_rois(self, reference_image):
        print("Selecting Sunscreen ROI (left square)")
        self.sunscreen_roi = self.select_roi(reference_image, "Sunscreen ROI")
        #
        print("Selecting Control ROI (between squares)")
        self.control_roi = self.select_roi(reference_image, "Control ROI")
        print(f"\nSunscreen ROI: {self.sunscreen_roi}")
        print(f"Control ROI: {self.control_roi}")
        return self.sunscreen_roi, self.control_roi