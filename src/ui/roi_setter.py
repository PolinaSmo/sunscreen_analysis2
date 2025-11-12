import cv2

class ROISetter:
    def __init__(self):
        self.sunscreen_roi = (620, 813, 300, 326)  
        self.control_roi = (1240, 773, 300, 373)    
        self.roi_size = (300, 300)  
        print("Using fixed ROIs:")
        print(f"  Sunscreen: {self.sunscreen_roi}")
        print(f"  Control: {self.control_roi}")
    
    def set_rois(self, reference_image):
        """Show current ROIs and allow updating"""
        img_with_rois = reference_image.copy()
        
        x, y, w, h = self.sunscreen_roi
        cv2.rectangle(img_with_rois, (x, y), (x+w, y+h), (0, 255, 0), 3)
        cv2.putText(img_with_rois, "Sunscreen", (x, y-10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        x, y, w, h = self.control_roi
        cv2.rectangle(img_with_rois, (x, y), (x+w, y+h), (0, 0, 255), 3)
        cv2.putText(img_with_rois, "Control", (x, y-10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        display_height = 800 
        h, w = img_with_rois.shape[:2]
        scale = display_height / h
        display_width = int(w * scale)
        
        display_img = cv2.resize(img_with_rois, (display_width, display_height))
        cv2.imshow("Current ROIs - Press any key to continue", display_img)
        cv2.waitKey(0) 
        cv2.destroyAllWindows()
        
        # Ask if user wants to update ROIs
        response = input("Update ROIs? (y/n): ").lower().strip()
        if response == 'y':
            self._update_rois_interactively(reference_image)
        
        return self.sunscreen_roi, self.control_roi
    
    def _update_rois_interactively(self, image):
        """Interactively set new ROIs with fixed size"""
        print("\n=== Setting NEW Sunscreen ROI ===")
        self.sunscreen_roi = self._select_fixed_size_roi(image, "Sunscreen ROI", (0, 255, 0))
        
        print("\n=== Setting NEW Control ROI ===")
        self.control_roi = self._select_fixed_size_roi(image, "Control ROI", (0, 0, 255))
        
        print(f"\nNew ROIs set:")
        print(f"  Sunscreen: {self.sunscreen_roi}")
        print(f"  Control: {self.control_roi}")
    
    def _select_fixed_size_roi(self, image, roi_name, color):
        """Select ROI center point - size is fixed"""
        img_display = image.copy()
        h, w = img_display.shape[:2]
        
        # for display, resizing
        display_height = 800
        scale = display_height / h
        display_width = int(w * scale)
        img_resized = cv2.resize(img_display, (display_width, display_height))
        
        
        cv2.putText(img_resized, f"Click center for {roi_name}", (50, 50),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        cv2.putText(img_resized, f"ROI size: {self.roi_size[0]}x{self.roi_size[1]}", (50, 100),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        
        center_point = [None]
        
        def mouse_callback(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:
                center_point[0] = (int(x/scale), int(y/scale))  # Convert back to original coordinates
                # Draw the fixed-size ROI
                roi_w, roi_h = self.roi_size
                roi_x = max(0, center_point[0][0] - roi_w//2)
                roi_y = max(0, center_point[0][1] - roi_h//2)
                cv2.rectangle(img_resized, 
                            (int(roi_x*scale), int(roi_y*scale)),
                            (int((roi_x+roi_w)*scale), int((roi_y+roi_h)*scale)),
                            color, 2)
                cv2.imshow(f"Select {roi_name}", img_resized)
        
        cv2.imshow(f"Select {roi_name}", img_resized)
        cv2.setMouseCallback(f"Select {roi_name}", mouse_callback)
        
        print(f"Click the center point for {roi_name}...")
        while center_point[0] is None:
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):  # Allow quitting
                cv2.destroyAllWindows()
                return self.sunscreen_roi if roi_name == "Sunscreen ROI" else self.control_roi
        
        cv2.destroyAllWindows()
        
        # Calculate final ROI coordinates (centered on clicked point)
        roi_w, roi_h = self.roi_size
        center_x, center_y = center_point[0]
        roi_x = max(0, center_x - roi_w//2)
        roi_y = max(0, center_y - roi_h//2)
        
        # Ensure ROI stays within image bounds
        h, w = image.shape[:2]
        roi_x = min(roi_x, w - roi_w)
        roi_y = min(roi_y, h - roi_h)
        
        return (roi_x, roi_y, roi_w, roi_h)