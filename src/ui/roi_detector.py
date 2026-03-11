import cv2
import numpy as np

class ROIDetector:
    def __init__(self):
        self.sunscreen_roi = None
        self.control_roi = None
    
    def detect_rois(self, image):
        self._debug_image_analysis(image)
        
        self.sunscreen_roi = (620, 813, 300, 300)
        self.control_roi = (1240, 773, 300, 300)
        
        print(f"ROIs: {self.sunscreen_roi}, {self.control_roi}")
        return self.sunscreen_roi, self.control_roi
    
    def _debug_image_analysis(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        cv2.imwrite('debug_original.jpg', gray)
        
        _, thresh1 = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)
        _, thresh2 = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
        
        cv2.imwrite('debug_thresh1.jpg', thresh1)
        cv2.imwrite('debug_thresh2.jpg', thresh2)
        
        edges = cv2.Canny(gray, 50, 150)
        cv2.imwrite('debug_edges.jpg', edges)
        
        #count contours
        contours1, _ = cv2.findContours(thresh1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours2, _ = cv2.findContours(thresh2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours_edges, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        print(f"Contours - thresh1: {len(contours1)}, thresh2: {len(contours2)}, edges: {len(contours_edges)}")
        
        if contours1:
            areas = [cv2.contourArea(c) for c in contours1]
            print(f"Largest area: {max(areas)}")