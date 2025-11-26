import cv2
import numpy as np

class ROIDetector:
    def __init__(self):
        self.sunscreen_roi = None
        self.control_roi = None
    
    def detect_rois(self, image):
        # try:
        #     self.sunscreen_roi, self.control_roi = self._auto_detect_aggressive(image)
        #     print("ROIs detected automatically")
        # except Exception as e:
        #     print(f"Auto-detection failed: {e}")
        #     print("Using fallback manual ROIs")
        #     self.sunscreen_roi = (620, 813, 300, 300)
        #     self.control_roi = (1240, 773, 300, 300)
        
    
        self.sunscreen_roi, self.control_roi = self._auto_detect_aggressive(image)
        self.debug_image_analysis(image)
        
        print(f"Sunscreen ROI: {self.sunscreen_roi}")
        print(f"Control ROI: {self.control_roi}")
        
        self._visualize_rois(image)
        
        return self.sunscreen_roi, self.control_roi
    
    def _auto_detect_aggressive(self, image):
        """More aggressive ROI detection"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        #try with different thresholding
        _, thresh1 = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)
        _, thresh2 = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
        
        #combine both thresholding methods
        combined = cv2.bitwise_or(thresh1, thresh2)
        
        contours, _ = cv2.findContours(combined, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        rectangles = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if 10000 < area < 500000:  
                x, y, w, h = cv2.boundingRect(contour)
                
                aspect_ratio = w / h
                if 0.5 < aspect_ratio < 2.0: 
                    rectangles.append((x, y, w, h, area))
        
        print(f"Found {len(rectangles)} potential rectangles")
        
        if len(rectangles) >= 2:
            rectangles.sort(key=lambda r: r[4], reverse=True)  #sort by area
            largest_rectangles = rectangles[:2]
            
            largest_rectangles.sort(key=lambda r: r[0])
            
            sunscreen = largest_rectangles[0][:4]  # (x,y,w,h)
            control = largest_rectangles[1][:4]
            
            return sunscreen, control
        else:
            return self._edge_based_detection(gray)
    
    def _edge_based_detection(self, gray):
        
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        edges = cv2.Canny(blurred, 30, 100)
        
        #dilate edges to connect broken lines
        kernel = np.ones((5, 5), np.uint8)
        dilated = cv2.dilate(edges, kernel, iterations=2)
        
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        rectangles = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if 50000 < area < 300000:
                # Use bounding rectangle instead of polygon approximation
                x, y, w, h = cv2.boundingRect(contour)
                rectangles.append((x, y, w, h, area))
        
        print(f"Edge-based found {len(rectangles)} rectangles")
        
        if len(rectangles) >= 2:
            rectangles.sort(key=lambda r: r[0])  # Sort by x
            return rectangles[0][:4], rectangles[1][:4]
        else:
            raise Exception(f"Only found {len(rectangles)} suitable areas")
    
    def _visualize_rois(self, image):
        """Show detected ROIs for verification"""
        img_with_rois = image.copy()
        
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
        
        cv2.imshow("Automatically Detected ROIs - Press any key", display_img)
        cv2.waitKey(3000)  #show for 3 seconds
        cv2.destroyAllWindows()