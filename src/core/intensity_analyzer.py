import cv2
import numpy as np
from src.data.statistics import calculate_statistics

class IntensityAnalyzer:
    def __init__(self, roi_selector):
        self.roi_selector = roi_selector
    
    def extract_roi_intensities(self, image, roi):
        """Extract intensity values from ROI"""
        x, y, w, h = roi
        roi_region = image[y:y+h, x:x+w]
        
        # Convert to grayscale
        if len(roi_region.shape) == 3:
            gray = cv2.cvtColor(roi_region, cv2.COLOR_BGR2GRAY)
        else:
            gray = roi_region
        
        return gray.flatten()
    
    def analyze_timepoint(self, image, time):
        """Analyze single timepoint"""
        sunscreen_intensities = self.extract_roi_intensities(image, self.roi_selector.sunscreen_roi)
        control_intensities = self.extract_roi_intensities(image, self.roi_selector.control_roi)
        
        return {
            'sunscreen': {
                'intensities': sunscreen_intensities,
                'stats': calculate_statistics(sunscreen_intensities)
            },
            'control': {
                'intensities': control_intensities,
                'stats': calculate_statistics(control_intensities)
            }
        }
    
    def analyze_all_timepoints(self, images, timepoints):
        """Analyze both ROIs across all timepoints"""
        if self.roi_selector.sunscreen_roi is None or self.roi_selector.control_roi is None:
            raise ValueError("ROIs not set! Call set_rois() first")
        
        results = {}
        
        for i, (img, time) in enumerate(zip(images, timepoints)):
            results[time] = self.analyze_timepoint(img, time)
            
        return results
