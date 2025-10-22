import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import modules directly
from src.core.image_loader import ImageLoader
from src.ui.roi_selector import ROISelector
from src.core.intensity_analyzer import IntensityAnalyzer
from src.data.exporter import DataExporter
from src.visualization.plotter import Plotter

def main():
    # Configuration
    image_paths = [
        'images/0hours.JPG',  
        'images/2hours.JPG',
        'images/4hours.JPG', 
        'images/6hours.JPG', 
    ]
    timepoints = [0, 2, 4, 6]
    
    # Create output directories
    Path("outputs/figures").mkdir(parents=True, exist_ok=True)
    Path("outputs/reports").mkdir(parents=True, exist_ok=True)
    
    print("Starting UV Sunscreen Analysis...")
    print(f"Current directory: {Path.cwd()}")
    
    # Check if images exist
    for path in image_paths:
        if Path(path).exists():
            print(f"✓ Found: {path}")
        else:
            print(f"✗ Missing: {path}")
            return
    
    try:
        # Initialize components
        image_loader = ImageLoader()
        roi_selector = ROISelector()
        intensity_analyzer = IntensityAnalyzer(roi_selector)
        
        # Load images
        images = image_loader.load_images(image_paths)
        
        # Set ROIs
        roi_selector.set_rois(images[0])
        
        # Analyze all timepoints
        results = intensity_analyzer.analyze_all_timepoints(images, timepoints)
        
        # Export results
        DataExporter.print_statistics(results)
        DataExporter.save_to_csv(results, 'outputs/reports/uv_data.csv')
        DataExporter.save_to_json(results, 'outputs/reports/analysis_results.json')
        
        # Generate plots
        Plotter.plot_intensity_distributions(results, 'outputs/figures/histograms.png')
        
        # Print raw data info
        sunscreen_0h = results[0]['sunscreen']['intensities']
        print(f"\nTotal pixels analyzed at 0h sunscreen ROI: {len(sunscreen_0h)}")
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()