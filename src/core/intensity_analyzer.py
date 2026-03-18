import cv2
import numpy as np
from src.data.statistics import calculate_statistics

class IntensityAnalyzer:
    def __init__(self, rois_dict):
        """
        rois_dict : dict mapping ROI name to (x, y, width, height) tuple
        """
        self.rois = rois_dict

    def extract_roi_intensities(self, image, roi):
        """Extract grayscale intensities from a single ROI."""
        x, y, w, h = roi
        img_h, img_w = image.shape[:2]

        # Clamp ROI to image boundaries
        x = max(0, min(x, img_w - 1))
        y = max(0, min(y, img_h - 1))
        w = min(w, img_w - x)
        h = min(h, img_h - y)

        roi_region = image[y:y+h, x:x+w]

        if len(roi_region.shape) == 3:
            # Proper luminance conversion (human perception)
            b, g, r = cv2.split(roi_region)
            gray = (0.299 * r + 0.587 * g + 0.114 * b).astype(np.uint8)
        else:
            gray = roi_region

        # Optional: remove extreme values (potential artifacts)
        valid = gray[(gray > 5) & (gray < 250)]
        return valid.flatten() if len(valid) > 0 else gray.flatten()

    def analyze_timepoint(self, image, time):
        """Analyze all ROIs for one timepoint."""
        results_for_time = {}
        for name, roi in self.rois.items():
            intensities = self.extract_roi_intensities(image, roi)
            results_for_time[name] = {
                'intensities': intensities,
                'stats': calculate_statistics(intensities),
                'roi': roi,
                'pixel_count': len(intensities)
            }
        return results_for_time

    def analyze_all_timepoints(self, images, timepoints):
        """Analyze all ROIs across all timepoints."""
        results = {}
        for i, (img, t) in enumerate(zip(images, timepoints)):
            print(f"Analyzing timepoint {t}h...")
            results[t] = self.analyze_timepoint(img, t)
        return results