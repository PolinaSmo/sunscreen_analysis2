import sys
import os
from pathlib import Path

print("DEBUG 1: Starting script")

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

sys.dont_write_bytecode = True
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'

print("DEBUG 2: Before imports")
from src.core.image_loader import ImageLoader
from src.ui.roi_setter import ROISetter
from src.core.intensity_analyzer import IntensityAnalyzer
from src.data.exporter import DataExporter
from src.visualization.plotter import Plotter
print("DEBUG 3: Imports successful")

def main():
    print("DEBUG 4: Entering main() function")
    
    image_paths = [
        'images/0hours.JPG',  
        'images/2hours.JPG',
        'images/4hours.JPG', 
        'images/6hours.JPG', 
    ]
    timepoints = [0, 2, 4, 6]
    
    print(f"DEBUG 5: Checking {len(image_paths)} images")
    
    # Check if images exist
    for path in image_paths:
        if not Path(path).exists():
            print(f"DEBUG 6: MISSING IMAGE: {path}")
            return
    
    print("DEBUG 7: All images found")
    
    Path("outputs/figures").mkdir(parents=True, exist_ok=True)
    Path("outputs/reports").mkdir(parents=True, exist_ok=True)
    print("DEBUG 8: Directories created")
    
    print("DEBUG 9: Creating components")
    image_loader = ImageLoader()
    roi_setter = ROISetter()
    intensity_analyzer = IntensityAnalyzer(roi_setter)
    
    print("DEBUG 10: Loading images")
    images = image_loader.load_images(image_paths)
    print(f"DEBUG 11: Loaded {len(images)} images")
    
    print("DEBUG 12: Setting ROIs")
    roi_setter.set_rois(images[0])
    
    print("DEBUG 13: Analyzing timepoints")
    results = intensity_analyzer.analyze_all_timepoints(images, timepoints)
    print(f"DEBUG 14: Analyzed {len(results)} timepoints")
    
    print("DEBUG 15: Exporting results")
    DataExporter.print_statistics(results)
    DataExporter.export_all(results, 'uv_analysis')
    
    print("DEBUG 16: Generating plots")
    Plotter.plot_intensity_distributions(results, 'outputs/figures/histograms.png')
    
    print("DEBUG 17: Analysis complete!")

if __name__ == "__main__":
    print("DEBUG 18: __name__ == '__main__' is True")
    main()
    print("DEBUG 19: After main() call")
