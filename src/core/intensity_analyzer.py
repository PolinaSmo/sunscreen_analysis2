import cv2
import numpy as np
from src.data.statistics import calculate_statistics
from src.ui.roi_setter import ROISetter

class IntensityAnalyzer:
    # def __init__(self, roi_selector):
    #     self.roi_selector = roi_selector

    def __init__(self, roi_setter):
        self.roi_setter = roi_setter
    
    def extract_roi_intensities(self, image, roi):
        x, y, w, h = roi

        img_height, img_width = image.shape[:2]
        x = max(0, min(x, img_width - 1))
        y = max(0, min(y, img_height - 1))
        w = min(w, img_width - x)
        h = min(h, img_height - y)

        roi_region = image[y:y+h, x:x+w]
        
        #converting to grayscale
        if len(roi_region.shape) == 3:
            gray = cv2.cvtColor(roi_region, cv2.COLOR_BGR2GRAY)
        else:
            gray = roi_region
        
        #get rid of any fully black or fully white pixels (potential errors)
        valid_pixels = gray[(gray > 5) & (gray < 250)]
        # return gray.flatten()
        return valid_pixels.flatten() if len(valid_pixels) > 0 else gray.flatten()
    
    def analyze_timepoint(self, image, time):
        # sunscreen_intensities = self.extract_roi_intensities(image, self.roi_selector.sunscreen_roi)
        # control_intensities = self.extract_roi_intensities(image, self.roi_selector.control_roi)
        sunscreen_intensities = self.extract_roi_intensities(image, self.roi_setter.sunscreen_roi)
        control_intensities = self.extract_roi_intensities(image, self.roi_setter.control_roi)
        
        
        return {
            'sunscreen': {
              'intensities': sunscreen_intensities,
                'stats': calculate_statistics(sunscreen_intensities),
                'roi': self.roi_setter.sunscreen_roi,
                'pixel_count': len(sunscreen_intensities)
            },
            'control': {
                'intensities': control_intensities,
                'stats': calculate_statistics(control_intensities),
                'roi': self.roi_setter.control_roi,
                'pixel_count': len(control_intensities),
            }
        }
    
    def analyze_all_timepoints(self, images, timepoints):
        results = {}
        for i, (img, time) in enumerate(zip(images, timepoints)):
            results[time] = self.analyze_timepoint(img, time)
        return results