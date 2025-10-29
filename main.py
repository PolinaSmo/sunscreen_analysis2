import sys
import os
from pathlib import Path
from src.core.image_loader import ImageLoader
from src.ui.roi_selector import ROISelector
from src.core.intensity_analyzer import IntensityAnalyzer
from src.data.exporter import DataExporter
from src.visualization.plotter import Plotter

#adding the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))



def main():
    image_paths = [
        'images/0hours.JPG',  
        'images/2hours.JPG',
        'images/4hours.JPG', 
        'images/6hours.JPG', 
    ]
    timepoints = [0, 2, 4, 6]
    #creating output directories if they don't exist
    Path("outputs/figures").mkdir(parents=True, exist_ok=True)
    Path("outputs/reports").mkdir(parents=True, exist_ok=True)
    #just in case - can delete later
    print(f"Current directory: {Path.cwd()}")
    
    #make sure images are there - good for later progress in project
    for path in image_paths:
        if Path(path).exists():
            print(f"Found: {path}")
        else:
            print(f"Missing: {path}")
            return
    try:
        image_loader = ImageLoader()
        roi_selector = ROISelector()
        intensity_analyzer = IntensityAnalyzer(roi_selector)
        images = image_loader.load_images(image_paths)
        
        roi_selector.set_rois(images[0])
        
        results = intensity_analyzer.analyze_all_timepoints(images, timepoints)
    
        DataExporter.print_statistics(results)
        DataExporter.save_to_csv(results, 'outputs/reports/uv_data.csv')
        DataExporter.save_to_json(results, 'outputs/reports/analysis_results.json')
        
        #PLOTS WORRY ABOUT LATER, WORK ON CODE STRUCTURE AND FINDINGS FIRST
        Plotter.plot_intensity_distributions(results, 'outputs/figures/histograms.png')
        
        sunscreen_0h = results[0]['sunscreen']['intensities']
        print(f"\nTotal pixels analyzed at 0h sunscreen ROI: {len(sunscreen_0h)}")
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()