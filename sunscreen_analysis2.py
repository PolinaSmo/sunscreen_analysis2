import cv2
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

class UVSunscreenAnalyzer:
    def __init__(self, image_paths):
        """
        Initialize with list of image paths in chronological order
        image_paths: list of paths to 0h, 2h, 4h, 6h images
        """
        self.image_paths = sorted(image_paths)
        self.images = []
        
        for path in self.image_paths:
            img = cv2.imread(str(path))
            if img is None:
                raise FileNotFoundError(f"Could not load image: {path}\nMake sure the file exists and path is correct!")
            self.images.append(img)
            print(f"✓ Loaded: {path} - Shape: {img.shape}")
        
        self.timepoints = [0, 2, 4, 6]  # hours
        self.sunscreen_roi = None
        self.control_roi = None
        
    def select_roi(self, image_index=0, roi_name="ROI", scale=0.3):
        """
        Manually select ROI from image
        image_index: which timepoint to use for selection (default 0h)
        roi_name: name for the ROI being selected
        scale: scaling factor for display (0.3 = 30% of original size)
        """
        img = self.images[image_index].copy()
        
        #go to grayscale for display
        img_display = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        #resize for display
        display_h, display_w = img_display.shape
        new_w = int(display_w * scale)
        new_h = int(display_h * scale)
        img_resized = cv2.resize(img_display, (new_w, new_h))
        
        print(f"Select {roi_name} - press ENTER when done, 'c' to cancel")
        print(f"Image scaled to {int(scale*100)}% for display")
        
        #select ROI on resized image
        roi_scaled = cv2.selectROI(f"Select {roi_name}", img_resized, fromCenter=False)
        cv2.destroyAllWindows()
        
        x, y, w, h = roi_scaled
        roi = (int(x/scale), int(y/scale), int(w/scale), int(h/scale))
        
        # roi format: (x,y, width, height)
        return roi
    
    def set_rois(self):
        """
        Set both sunscreen and control ROIs interactively
        """
        print("=== Selecting Sunscreen ROI (left square) ===")
        self.sunscreen_roi = self.select_roi(0, "Sunscreen ROI")
        
        print("\n=== Selecting Control ROI (between squares) ===")
        self.control_roi = self.select_roi(0, "Control ROI")
        
        print(f"\nSunscreen ROI: {self.sunscreen_roi}")
        print(f"Control ROI: {self.control_roi}")
    
    def extract_roi_intensities(self, image, roi):
        """
        Extract intensity values from ROI
        Returns 1D array of grayscale intensities
        """
        x, y, w, h = roi
        roi_region = image[y:y+h, x:x+w]
        
        #to grayscale
        if len(roi_region.shape) == 3:
            gray = cv2.cvtColor(roi_region, cv2.COLOR_BGR2GRAY)
        else:
            gray = roi_region
        
        #flatten to 1D array
        intensities = gray.flatten() # ??
        
        return intensities
    
    def calculate_statistics(self, intensities):
        """
        Calculate statistics for intensity array
        """
        stats = {
            'min': np.min(intensities),
            'max': np.max(intensities),
            'mean': np.mean(intensities),
            'median': np.median(intensities),
            'std': np.std(intensities),
            'range': np.max(intensities) - np.min(intensities)
        }
        return stats
    
    def analyze_all_timepoints(self) -> dict:
        """
        Analyze both ROIs across all timepoints
        Returns dictionary with results
        """
        if self.sunscreen_roi is None or self.control_roi is None:
            raise ValueError("ROIs not set! Call set_rois() first")
        
        results = {}
        
        for i, (img, time) in enumerate(zip(self.images, self.timepoints)):
            sunscreen_intensities = self.extract_roi_intensities(img, self.sunscreen_roi)
            control_intensities = self.extract_roi_intensities(img, self.control_roi)
            
            results[time] = {
                'sunscreen': {
                    'intensities': sunscreen_intensities,
                    'stats': self.calculate_statistics(sunscreen_intensities)
                },
                'control': {
                    'intensities': control_intensities,
                    'stats': self.calculate_statistics(control_intensities)
                }
            }
            
        return results
    
    def print_statistics(self, results):
        """
        Print statistics in a readable format
        """
        print("\n" + "="*80)
        print("ANALYSIS RESULTS")
        print("="*80)
        
        for time in sorted(results.keys()):
            print(f"\n--- Timepoint: {time} hours ---")
            
            for roi_type in ['sunscreen', 'control']:
                stats = results[time][roi_type]['stats']
                print(f"\n  {roi_type.upper()} ROI:")
                print(f"    Min intensity:    {stats['min']:.2f}")
                print(f"    Max intensity:    {stats['max']:.2f}")
                print(f"    Mean intensity:   {stats['mean']:.2f}")
                print(f"    Median intensity: {stats['median']:.2f}")
                print(f"    Std Dev:          {stats['std']:.2f}")
                print(f"    Range:            {stats['range']:.2f}")
    
    def save_results_to_csv(self, results, output_file='uv_analysis_results.csv'):
        """
        Save results to CSV file
        """
        with open(output_file, 'w') as f:
            # Header
            f.write("Timepoint (hours),ROI Type,Min,Max,Mean,Median,Std Dev,Range,Pixel Count\n")
            
            # Data
            for time in sorted(results.keys()):
                for roi_type in ['sunscreen', 'control']:
                    stats = results[time][roi_type]['stats']
                    intensities = results[time][roi_type]['intensities']
                    
                    f.write(f"{time},{roi_type},{stats['min']:.2f},{stats['max']:.2f},")
                    f.write(f"{stats['mean']:.2f},{stats['median']:.2f},")
                    f.write(f"{stats['std']:.2f},{stats['range']:.2f},{len(intensities)}\n")
        
        print(f"\nResults saved to: {output_file}")
    
    def plot_intensity_distributions(self, results, save_path='intensity_distributions.png'):
        """
        Plot histograms of intensity distributions
        This is your "messed up bell curve" you mentioned!
        """
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Intensity Distributions Across Timepoints', fontsize=16)
        
        for idx, time in enumerate(sorted(results.keys())):
            ax = axes[idx // 2, idx % 2]
            
            sunscreen_int = results[time]['sunscreen']['intensities']
            control_int = results[time]['control']['intensities']
            
            ax.hist(sunscreen_int, bins=50, alpha=0.6, label='Sunscreen', color='green', edgecolor='black')
            ax.hist(control_int, bins=50, alpha=0.6, label='Control', color='red', edgecolor='black')
            
            ax.set_xlabel('Intensity (0-255)')
            ax.set_ylabel('Pixel Count')
            ax.set_title(f'Timepoint: {time} hours')
            ax.legend()
            ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"\nHistograms saved to: {save_path}")
        plt.show()


if __name__ == "__main__":
    
    image_paths = [
        'images/0hours.JPG',  
        'images/2hours.JPG',
        'images/4hours.JPG', 
        'images/6hours.JPG', 
    ]
    
    
    print("Starting UV Sunscreen Analysis...")
    print(f"Looking for images in: {Path.cwd()}")
    print("\nAttempting to load images...")
    
    # initialize analyzer
    analyzer = UVSunscreenAnalyzer(image_paths)
    analyzer.set_rois()
    
    # all timepoints
    results = analyzer.analyze_all_timepoints()
    
    # statistics
    analyzer.print_statistics(results)
    
    #save to csv file
    analyzer.save_results_to_csv(results, 'uv_data.csv')
    
    #plot histograms
    analyzer.plot_intensity_distributions(results, 'histograms.png')
    
    #raw data if i need it
    sunscreen_0h = results[0]['sunscreen']['intensities']
    print(f"\nTotal pixels analyzed at 0h sunscreen ROI: {len(sunscreen_0h)}")
