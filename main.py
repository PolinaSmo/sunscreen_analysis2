import sys
import os
from pathlib import Path
# import importlib

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

#disabling pycache for now
sys.dont_write_bytecode = True
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'

from src.core.image_loader import ImageLoader
# from src.ui.roi_selector import ROISelector
from src.ui.roi_setter import ROISetter
from src.core.intensity_analyzer import IntensityAnalyzer
from src.data.exporter import DataExporter
# importlib.reload(DataExporter)
from src.visualization.plotter import Plotter




def main():
    image_paths = [
        'images/0hours.JPG',  
        'images/2hours.JPG',
        'images/4hours.JPG', 
        'images/6hours.JPG', 
    ]
    timepoints = [0, 2, 4, 6]
    Path("outputs/figures").mkdir(parents=True, exist_ok=True)
    Path("outputs/reports").mkdir(parents=True, exist_ok=True)
    
        
    image_loader = ImageLoader()
    # roi_selector = ROISelector()
    roi_setter = ROISetter()
    # intensity_analyzer = IntensityAnalyzer(roi_selector)
    intensity_analyzer = IntensityAnalyzer(roi_setter)
    images = image_loader.load_images(image_paths)
    
    # roi_selector.set_rois(images[0])
    roi_setter.set_rois(images[0])
    
    results = intensity_analyzer.analyze_all_timepoints(images, timepoints)

    DataExporter.print_statistics(results)
    DataExporter.export_all(results, 'uv_analysis')

    #PLOTS WORRY ABOUT LATER, WORK ON CODE STRUCTURE AND FINDINGS FIRST
    Plotter.plot_intensity_distributions(results, 'outputs/figures/histograms.png')
    
if __name__ == "__main__":
    main()