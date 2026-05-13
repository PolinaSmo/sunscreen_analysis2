import sys
import os
import json
from pathlib import Path
import matplotlib.pyplot as plt
import cv2

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Disable bytecode cache
sys.dont_write_bytecode = True
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'

from src.core.image_loader import ImageLoader
from src.ui.rect_selector import RectangleROISelector
from src.core.intensity_analyzer import IntensityAnalyzer
from src.data.exporter import DataExporter
from src.visualization.plotter import Plotter


def main():
    # Get the subject/folder number from user
    subject = input("Enter subject/folder number (11-20): ").strip()

    # Base path for this subject
    base_path = Path(f"images/{subject}")

    # Try different possible file extensions/cases
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

    # Create output directories with subject number
    Path(f"outputs/figures/{subject}").mkdir(parents=True, exist_ok=True)
    Path(f"outputs/reports/{subject}").mkdir(parents=True, exist_ok=True)

    # Load all images
    loader = ImageLoader()
    images = loader.load_images(image_paths)
    first_image = images[0]

    # Get number of ROIs from user
    try:
        num_rois = int(input("How many ROIs do you want to define? "))
    except ValueError:
        print("Invalid input. Using default: 2 ROIs.")
        num_rois = 2

    # ROI SELECTION LOOP with preview/redo option
    rois = {}
    confirmed = False

    while not confirmed:
        rois = {}
        for i in range(num_rois):
            name = input(
                f"Enter name for ROI #{i + 1} (e.g., 'sunscreen_left', 'control', 'sunscreen_right'): ").strip()
            if not name:
                name = f"ROI_{i + 1}"
            print(f"\n--- Defining ROI: {name} ---")
            selector = RectangleROISelector(first_image)
            roi_coords = selector.get_roi()
            if roi_coords is None:
                print("ROI selection cancelled. Exiting.")
                return
            rois[name] = roi_coords

        # ============================================
        # PREVIEW STEP: Show all ROIs on one image
        # ============================================
        print("\n" + "=" * 50)
        print("PREVIEW: Review your ROI selections")
        print("=" * 50)

        preview_img = first_image.copy()
        colors = [(0, 255, 0), (0, 0, 255), (255, 0, 0), (255, 255, 0), (255, 0, 255)]
        for idx, (name, (x, y, w, h)) in enumerate(rois.items()):
            color = colors[idx % len(colors)]
            cv2.rectangle(preview_img, (x, y), (x + w, y + h), color, 3)
            cv2.putText(preview_img, name, (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        # Resize for display
        h, w = preview_img.shape[:2]
        max_height = 800
        scale = max_height / h
        display_w = int(w * scale)
        preview_resized = cv2.resize(preview_img, (display_w, max_height))

        cv2.imshow("ROI Preview - Press ENTER to accept, ESC to redo", preview_resized)
        key = cv2.waitKey(0)
        cv2.destroyAllWindows()

        if key == 27:  # ESC - redo
            print("Redoing ROI selection...\n")
        else:  # ENTER or any other key - accept
            confirmed = True
            print("ROIs accepted!")

    # Save ROI positions for this subject
    Path("config").mkdir(exist_ok=True)
    with open(f"config/roi_positions_{subject}.json", 'w') as f:
        json.dump(rois, f, indent=2)
    print(f"✓ ROI positions saved to config/roi_positions_{subject}.json")

    analyzer = IntensityAnalyzer(rois, subject=subject, output_dir="outputs/roi_images")

    results = analyzer.analyze_all_timepoints(images, timepoints, save_roi_images=True)

    DataExporter.print_statistics(results)
    DataExporter.export_all(results, f'uv_analysis_{subject}')

    # plots
    Plotter.plot_intensity_distributions(results, f'outputs/figures/{subject}/histograms.png')

    print(f"\nAnalysis complete for subject {subject}!")


if __name__ == "__main__":
    main()