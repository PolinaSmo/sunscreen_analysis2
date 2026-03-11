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
        
        #better luminance
        if len(roi_region.shape) == 3:
            b,g,r = cv2.split(roi_region)
            gray = (0.114*b + 0.587*g + 0.299*r).astype(np.uint8)
        else:gray = roi_region

        
        # #converting to grayscale
        # if len(roi_region.shape) == 3:
            # gray = cv2.cvtColor(roi_region, cv2.COLOR_BGR2GRAY)
        # else:
            # gray = roi_region
        

        #get rid of any fully black or fully white pixels (potential errors)
        valid_pixels = gray[(gray > 5) & (gray < 250)]
        # return gray.flatten()
        return valid_pixels.flatten() if len(valid_pixels) > 0 else gray.flatten()
    
    def remove_outliers(self, intensities):
        q1 = np.percentile(intensities, 25)
        q3 = np.percentile(intensities, 75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        return intensities[(intensities >= lower_bound) & (intensities <= upper_bound)]

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