import sys
import os
import json
import cv2
import numpy as np
import pandas as pd
from pathlib import Path
from scipy import stats

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.dont_write_bytecode = True
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'

from src.ui.rect_selector import SameSizeROISelector, RectangleROISelector, preview_rois_on_timepoints
def calculate_statistics_from_intensities(intensities):
    if len(intensities) == 0:
        return {}

    return {
        'min': np.min(intensities),
        'max': np.max(intensities),
        'mean': np.mean(intensities),
        'median': np.median(intensities),
        'std': np.std(intensities),
        'range': np.max(intensities) - np.min(intensities),
        'pixel_count': len(intensities),
        'variance': np.var(intensities),
        'kurtosis': stats.kurtosis(intensities) if len(intensities) > 3 else 0,
        'skewness': stats.skew(intensities) if len(intensities) > 2 else 0,
    }


def extract_blue_channel_intensities(image, roi):
    x, y, w, h = roi
    #convert to integers (fixes the TypeError)
    x, y, w, h = int(x), int(y), int(w), int(h)

    img_h, img_w = image.shape[:2]
    x = max(0, min(x, img_w - 1))
    y = max(0, min(y, img_h - 1))
    w = min(w, img_w - x)
    h = min(h, img_h - y)

    roi_region = image[y:y + h, x:x + w]
    blue_channel = roi_region[:, :, 0]
    return blue_channel.flatten()


def main():
    subject_num = int(input("Enter subject number (1-20): ").strip())
    base_path = Path(f"images/{subject_num}")
    pre_app_path = base_path / "pre_application.JPG"
    timepoint_paths = {
        0: base_path / "0hours.JPG",
        2: base_path / "2hours.JPG",
        4: base_path / "4hours.JPG",
        6: base_path / "6hours.JPG",
    }

    if pre_app_path.exists():
        control_image = cv2.imread(str(pre_app_path))
        print(f"Using pre-application image as control: {pre_app_path}")
    else:
        control_image = cv2.imread(str(timepoint_paths[0]))
        print(f"Warning: No pre-application image. Using 0hours as control.")

    if control_image is None:
        print(f"Error: Could not load control image")
        return
    images = {}
    for t, path in timepoint_paths.items():
        if path.exists():
            img = cv2.imread(str(path))
            images[t] = img
            print(f"Loaded: {path}")
        else:
            print(f"Warning: Missing {path}")

    if len(images) == 0:
        print("No images found!")
        return

    all_preview_images = [control_image] + [images[t] for t in [0, 2, 4, 6]]
    preview_timepoints = ['Control'] + [0, 2, 4, 6]


    # ROI SELECTION with same size for left/right
    selector = SameSizeROISelector(control_image)
    print("\n=== Select LEFT sunscreen ROI (this will set the size for both) ===")
    left_roi = selector.select_roi("Select LEFT sunscreen ROI", is_first=True)
    if left_roi is None:
        print("Selection cancelled")
        return
    print("\n=== Select RIGHT sunscreen ROI (same size, drag to position) ===")
    right_roi = selector.select_roi("Select RIGHT sunscreen ROI", is_first=False)
    if right_roi is None:
        print("Selection cancelled")
        return
    print("\n=== Select CONTROL ROI (bare skin, no sunscreen) ===")
    print(f"Control ROI will use the same size as left/right: {left_roi[2]} x {left_roi[3]}")
    control_selector = SameSizeROISelector(control_image)
    #set the fixed size from left_roi first
    control_selector.fixed_size = (left_roi[2], left_roi[3])
    control_roi = control_selector.select_roi("Select CONTROL ROI (same size, drag to position)", is_first=False)
    if control_roi is None:
        print("Selection cancelled")
        return

    # convert to integers
    rois = {
        'sunscreen_left': (int(left_roi[0]), int(left_roi[1]), int(left_roi[2]), int(left_roi[3])),
        'sunscreen_right': (int(right_roi[0]), int(right_roi[1]), int(right_roi[2]), int(right_roi[3])),
        'control': (int(control_roi[0]), int(control_roi[1]), int(control_roi[2]), int(control_roi[3])),
    }

    # PREVIEW: Show all ROIs on all timepoints
    print("\n=== PREVIEW: Checking ROIs on all timepoints ===")
    preview_images = []
    for img in all_preview_images:
        img_copy = img.copy()
        for roi_name, (x, y, w, h) in rois.items():
            if roi_name == 'sunscreen_left':
                color = (0, 255, 0)
            elif roi_name == 'sunscreen_right':
                color = (255, 0, 0)
            else:
                color = (0, 0, 255)
            x, y, w, h = int(x), int(y), int(w), int(h)
            cv2.rectangle(img_copy, (x, y), (x + w, y + h), color, 3)
            cv2.putText(img_copy, roi_name, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        preview_images.append(img_copy)

    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, len(preview_images), figsize=(20, 5))
    fig.suptitle("ROI Preview - Check all timepoints", fontsize=14)
    for idx, (img, label) in enumerate(zip(preview_images, preview_timepoints)):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        axes[idx].imshow(img_rgb)
        axes[idx].set_title(f"{label}")
        axes[idx].axis('off')
    plt.tight_layout()
    plt.show()

    response = input("\nAre these ROIs correct for ALL timepoints? (y/n): ").strip().lower()
    if response != 'y':
        print("ROIs rejected. Please re-run.")
        return


    # ANALYZE each timepoint
    results = {}
    timepoints = [0, 2, 4, 6]
    for t in timepoints:
        if t not in images:
            continue
        img = images[t]
        print(f"\nAnalyzing timepoint {t}h...")
        time_result = {}
        for roi_name, roi in rois.items():
            intensities = extract_blue_channel_intensities(img, roi)
            stats_dict = calculate_statistics_from_intensities(intensities)
            time_result[roi_name] = {
                'intensities': intensities.tolist(),
                'stats': stats_dict,
                'roi': roi,
                'pixel_count': len(intensities)
            }
            print(f"  {roi_name}: mean={stats_dict['mean']:.2f}, std={stats_dict['std']:.2f}")

        results[t] = time_result

    # EXPORT to CSV
    #rows = []
    for t in timepoints:
        if t not in results:
            continue
        for roi_name, roi_data in results[t].items():
            s = roi_data['stats']
            rows.append({
                'timepoint_hours': t,
                'roi_name': roi_name,
                'min_intensity': s['min'],
                'max_intensity': s['max'],
                'mean_intensity': s['mean'],
                'median_intensity': s['median'],
                'std_dev': s['std'],
                'range': s['range'],
                'pixel_count': s['pixel_count'],
                'kurtosis': s['kurtosis'],
                'skewness': s['skewness'],
            })

    df = pd.DataFrame(rows)
    output_file = f'outputs/reports/uv_analysis_{subject_num}.csv'
    df.to_csv(output_file, index=False)
    print(f"\n✓ Results saved to {output_file}")

    print(f"\nAnalysis complete for subject {subject_num}")


if __name__ == "__main__":
    main()