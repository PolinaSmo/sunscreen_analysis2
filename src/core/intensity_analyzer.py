import cv2
import numpy as np
from pathlib import Path
from src.data.statistics import calculate_statistics


class IntensityAnalyzer:
    def __init__(self, rois_dict, subject=None, output_dir="outputs/roi_images"):
        """
        rois_dict : dict mapping ROI name to (x, y, width, height) tuple
        subject : subject ID/folder number for organizing saved images
        output_dir : base directory to save ROI images
        """
        self.rois = rois_dict
        self.subject = subject
        self.output_dir = Path(output_dir) / subject if subject else Path(output_dir)

        # Create output directory if it doesn't exist
        if subject:
            self.output_dir.mkdir(parents=True, exist_ok=True)

    def extract_roi_intensities(self, image, roi, roi_name="", save_roi_image=False, image_name="", timepoint=""):
        """Extract grayscale intensities from a single ROI."""
        x, y, w, h = roi
        img_h, img_w = image.shape[:2]

        # Clamp ROI to image boundaries
        x = max(0, min(x, img_w - 1))
        y = max(0, min(y, img_h - 1))
        w = min(w, img_w - x)
        h = min(h, img_h - y)

        roi_region = image[y:y + h, x:x + w]

        # Save ROI as image if requested
        if save_roi_image and self.subject and roi_name:
            roi_img_path = self.output_dir / f"{image_name}_{timepoint}_{roi_name}.png"
            cv2.imwrite(str(roi_img_path), roi_region)
            print(f"  Saved ROI image: {roi_img_path}")

        if len(roi_region.shape) == 3:
            # Proper luminance conversion
            b, g, r = cv2.split(roi_region)
            gray = (0.299 * r + 0.587 * g + 0.114 * b).astype(np.uint8)
        else:
            gray = roi_region

        # Optional: remove extreme values
        valid = gray[(gray > 5) & (gray < 250)]
        return valid.flatten() if len(valid) > 0 else gray.flatten()

    def analyze_timepoint(self, image, time, save_roi_images=False, image_name=""):
        """Analyze all ROIs for one timepoint."""
        results_for_time = {}
        for roi_name, roi in self.rois.items():
            intensities = self.extract_roi_intensities(
                image, roi,
                roi_name=roi_name,  # ← Pass the ROI name here
                save_roi_image=save_roi_images,
                image_name=image_name,
                timepoint=f"{time}h"
            )
            results_for_time[roi_name] = {
                'intensities': intensities,
                'stats': calculate_statistics(intensities),
                'roi': roi,
                'pixel_count': len(intensities)
            }
        return results_for_time

    def analyze_all_timepoints(self, images, timepoints, save_roi_images=False):
        """Analyze all ROIs across all timepoints."""
        results = {}
        for i, (img, t) in enumerate(zip(images, timepoints)):
            print(f"Analyzing timepoint {t}h...")
            image_name = f"timepoint_{t}h"
            results[t] = self.analyze_timepoint(img, t, save_roi_images, image_name)
        return results