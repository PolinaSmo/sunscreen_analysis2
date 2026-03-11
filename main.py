import sys
import os
from pathlib import Path
import matplotlib
from matplotlib.font_manager import json_load

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np

import cv2
#test comment on new laptop - ignore
print("DEBUG 1: Start running script")

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

sys.dont_write_bytecode = True
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
os.environ['DISPLAY'] = ':0'  
os.environ['QT_QPA_PLATFORM'] = 'xcb'

print("DEBUG 2: Before imports")
from src.core.image_loader import ImageLoader
# from src.ui.roi_setter import ROI
#
# Setter
from src.ui.roi_dragger import ROIDragger
from src.core.intensity_analyzer import IntensityAnalyzer
from src.data.exporter import DataExporter
from src.visualization.plotter import Plotter
print("DEBUG 3: Imports successful")

def analyze_person(person_id):
    print(f"\nDEBUG: Starting subject {person_id} ===")
    
    image_paths = [
        f'images/{person_id}/0hours.JPG',
        f'images/{person_id}/2hours.JPG', 
        f'images/{person_id}/4hours.JPG',
        f'images/{person_id}/6hours.JPG'
    ]
    
    # CHECK 1: Do files exist?
    print(f"DEBUG: Checking {len(image_paths)} image paths")
    for path in image_paths:
        exists = Path(path).exists()
        print(f"  {path}: {'-exists-' if exists else '-does not exist-'}")
        if not exists:
            print(f"ERROR: Missing image: {path}")
            return None
    
    print("DEBUG: All images found, now loading them in")
    
    # Load images
    image_loader = ImageLoader()
    images = image_loader.load_images(image_paths)
    print(f"DEBUG: Loaded {len(images)} images")
    
    # CHECK 2: Are images valid?
    for i, img in enumerate(images):
        print(f"  Image {i}: Shape {img.shape}, Type {img.dtype}")
    # CHECK 3: Before ROI selection
    print("DEBUG: Creating ROIDragger...")
    roi_dragger = ROIDragger(roi_size=(300, 300))
    sunscreen_roi = roi_dragger.select_roi_interactive(images[0], "sunscreen")
    control_roi = roi_dragger.select_roi_interactive(images[0], "control")

    # Save for next time
    roi_dragger.save_selections("my_rois.json")
    
    # CHECK 4: Try minimal ROI test
    print("DEBUG: Testing simple ROI display...")
    
    # Test with a simple OpenCV window
    test_image = images[0].copy()
    cv2.putText(test_image, "TEST - Press any key", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    # cv2.imshow("Simple Test Window", cv2.resize(test_image, (800, 600)))
    #check above for manual values later - squished or not ? - potential to run through each iteration of ROI dragging stage ?

    cv2.namedWindow('Some Name', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Some Name', 900, 700)  # Adjust these numbers!
    cv2.imshow('Some Name', test_image)

    print("DEBUG: Test window should appear - Press any key")
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    print("DEBUG: Test window closed")
    
    # Now try the actual ROI selector
    print("DEBUG: Now trying ROI selector...")
    roi = roi_dragger.select_roi_interactive(
        images[0], 
        f"{person_id}_0h", 
        f"{person_id} - 0h"
    )
    
    if roi:
        print(f"DEBUG: ROI selected: {roi}")
    else:
        print("DEBUG: ROI selection failed or cancelled")
    
    return None  # Stop here for testing

def main():
    # List of people to analyze
    person_ids = [11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
    
    all_results = {}
    for person_id in person_ids:
        results = analyze_person(person_id)
        if results:
            all_results[person_id] = results

# import sys
# import os
# from pathlib import Path

# print("DEBUG 1: Starting script")

# project_root = Path(__file__).parent
# sys.path.insert(0, str(project_root))

# sys.dont_write_bytecode = True
# os.environ['PYTHONDONTWRITEBYTECODE'] = '1'

# print("DEBUG 2: Before imports")
# from src.core.image_loader import ImageLoader
# from src.ui.roi_setter import ROISetter
# from src.core.intensity_analyzer import IntensityAnalyzer
# from src.data.exporter import DataExporter
# from src.visualization.plotter import Plotter
# print("DEBUG 3: Imports successful")

# def main():
#     print("DEBUG 4: Entering main() function")
    
#     image_paths = [
#         'images/11/0hours.JPG',  
#         'images/11/2hours.JPG',
#         'images/11/4hours.JPG', 
#         'images/11/6hours.JPG',

#         'images/13/0hours.JPG',  
#         'images/13/2hours.JPG',
#         'images/13/4hours.JPG', 
#         'images/13/6hours.JPG', 
#     ]
#     timepoints = [0, 2, 4, 6]
    
#     print(f"DEBUG 5: Checking {len(image_paths)} images")
    
#     for path in image_paths:
#         if not Path(path).exists():
#             print(f"DEBUG 6: MISSING IMAGE: {path}")
#             return
    
#     print("DEBUG 7: All images found")
    
#     Path("outputs/figures").mkdir(parents=True, exist_ok=True)
#     Path("outputs/reports").mkdir(parents=True, exist_ok=True)
#     print("DEBUG 8: Directories created")
    
#     print("DEBUG 9: Creating components")
#     image_loader = ImageLoader()
#     roi_setter = ROISetter()
#     intensity_analyzer = IntensityAnalyzer(roi_setter)
    
#     print("DEBUG 10: Loading images")
#     images = image_loader.load_images(image_paths)
#     print(f"DEBUG 11: Loaded {len(images)} images")
    
#     print("DEBUG 12: Setting ROIs")
#     roi_setter.set_rois(images[0])
    
#     print("DEBUG 13: Analyzing timepoints")
#     results = intensity_analyzer.analyze_all_timepoints(images, timepoints)
#     print(f"DEBUG 14: Analyzed {len(results)} timepoints")
    
#     print("DEBUG 15: Exporting results")
#     DataExporter.print_statistics(results)
#     DataExporter.export_all(results, 'uv_analysis')

    
#     print("DEBUG 16: Generating plots")
#     Plotter.plot_intensity_distributions(results, 'outputs/figures/histograms.png')
    
#     print("DEBUG 17: Analysis done")

# if __name__ == "__main__":
#     print("DEBUG 18: __name__ == '__main__' is True")
#     main()
#     print("DEBUG 19: After main() call")

if __name__ == "__main__":
    print("=== MAIN STARTING ===")
    main()
    print("=== MAIN FINISHED ===")

