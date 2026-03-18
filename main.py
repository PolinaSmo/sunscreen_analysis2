import sys
import os
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Disable bytecode cache
sys.dont_write_bytecode = True
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'

from src.core.image_loader import ImageLoader
from src.ui.roi_dragger import ROIDragger
from src.core.intensity_analyzer import IntensityAnalyzer
from src.data.exporter import DataExporter
from src.visualization.plotter import Plotter


def main():
    subject = input("Enter subject/folder number (11-20): ").strip()

    base_path = Path(f"images/{subject}")
    time_files = ['0hours', '2hours', '4hours', '6hours']
    timepoints = [0, 2, 4, 6]
    image_paths = []

    for tf in time_files:
        possible_paths = [
            base_path / f"{tf}.JPG",
            base_path / f"{tf}.jpg",
            base_path / f"{tf}.jpeg",
            base_path / f"{tf}.JPEG",
        ]

        found = False
        for path in possible_paths:
            if path.exists():
                image_paths.append(str(path))
                found = True
                print(f"Found: {path}")
                break

        if not found:
            print(f"Error: Could not find {tf} image in {base_path}")
            print(f"Files in folder: {[f.name for f in base_path.iterdir()]}")
            return
    Path(f"outputs/figures/{subject}").mkdir(parents=True, exist_ok=True)
    Path(f"outputs/reports/{subject}").mkdir(parents=True, exist_ok=True)

    loader = ImageLoader()
    images = loader.load_images(image_paths)
    first_image = images[0]
    try:
        num_rois = int(input("Number of ROIs to define? "))
        roi_size_input = input("Enter ROI size (width height) [test with 300 300]: ").strip()
        if roi_size_input:
            roi_w, roi_h = map(int, roi_size_input.split())
        else:
            roi_w, roi_h = 300, 300
    except ValueError:
        print("Invalid input. Using defaults: 2 ROIs, size 300x300.")
        num_rois = 2
        roi_w, roi_h = 300, 300
    dragger = ROIDragger(roi_size=(roi_w, roi_h))
    rois = {}
    for i in range(num_rois):
        name = input(f"Enter name for ROI #{i + 1} ('sunscreen', 'control', etc.): ").strip()
        if not name:
            name = f"ROI_{i + 1}"
        print(f"\nDefining ROI: {name}")
        roi_coords = dragger.select_roi_interactive(first_image, name, window_name=f"Drag ROI: {name}")
        if roi_coords is None:
            print("ROI selection cancelled. Exiting.")
            return
        rois[name] = roi_coords

    # Save ROI positions for this subject
    dragger.save_selections(f"roi_positions_{subject}.json")

    # Initialize analyzer with all ROIs
    analyzer = IntensityAnalyzer(rois)

    # Run analysis
    results = analyzer.analyze_all_timepoints(images, timepoints)

    # Export results with subject in filename
    DataExporter.print_statistics(results)
    DataExporter.export_all(results, f'uv_analysis_{subject}')

    # Generate plots
    Plotter.plot_intensity_distributions(results, f'outputs/figures/{subject}/histograms.png')

    print(f"\nAnalysis complete for subject {subject}!")


if __name__ == "__main__":
    main()