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

from src.ui.rect_selector import SameSizeROISelector


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
    x, y, w, h = int(roi[0]), int(roi[1]), int(roi[2]), int(roi[3])
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
    timepoint_paths = {0: base_path / "0hours.JPG", 2: base_path / "2hours.JPG", 4: base_path / "4hours.JPG",
                       6: base_path / "6hours.JPG"}

    if pre_app_path.exists():
        control_image = cv2.imread(str(pre_app_path))
        print(f"Using pre-application image as control")
    else:
        control_image = cv2.imread(str(timepoint_paths[0]))
        print(f"Warning: No pre-application image. Using 0hours as control.")

    if control_image is None:
        print("Error: Could not load control image")
        return

    images = {}
    for t, path in timepoint_paths.items():
        if path.exists():
            images[t] = cv2.imread(str(path))
            print(f"Loaded: {path}")

    if len(images) == 0:
        print("No images found!")
        return

    # ROI SELECTION
    selector = SameSizeROISelector(control_image)

    print("\n=== Select LEFT sunscreen ROI (this sets the size for ALL) ===")
    left_roi = selector.select_roi("Select LEFT sunscreen ROI", is_first=True)
    if left_roi is None:
        return
    left_roi = tuple(int(v) for v in left_roi)

    print("\n=== Select RIGHT sunscreen ROI (same size, drag to position) ===")
    right_roi = selector.select_roi("Select RIGHT sunscreen ROI", is_first=False)
    if right_roi is None:
        return
    right_roi = tuple(int(v) for v in right_roi)

    print(f"\n=== Select CONTROL ROI (same size: {left_roi[2]}x{left_roi[3]}, drag to position) ===")
    control_selector = SameSizeROISelector(control_image)
    control_selector.fixed_size = (left_roi[2], left_roi[3])
    control_roi = control_selector.select_roi("Select CONTROL ROI (bare skin)", is_first=False)
    if control_roi is None:
        return
    control_roi = tuple(int(v) for v in control_roi)

    rois = {
        'sunscreen_left': left_roi,
        'sunscreen_right': right_roi,
        'control': control_roi,
    }

    # PREVIEW
    print("\n=== PREVIEW: Checking ROIs on all timepoints ===")
    all_images = [control_image, images[0], images[2], images[4], images[6]]
    labels = ['Control', '0h', '2h', '4h', '6h']

    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 5, figsize=(20, 4))
    fig.suptitle("ROI Preview - Check all timepoints", fontsize=14)

    for idx, (img, label) in enumerate(zip(all_images, labels)):
        img_copy = img.copy()
        for roi_name, (x, y, w, h) in rois.items():
            if roi_name == 'sunscreen_left':
                color = (0, 255, 0)
            elif roi_name == 'sunscreen_right':
                color = (255, 0, 0)
            else:
                color = (0, 0, 255)
            cv2.rectangle(img_copy, (x, y), (x + w, y + h), color, 3)
            cv2.putText(img_copy, roi_name, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

        img_rgb = cv2.cvtColor(img_copy, cv2.COLOR_BGR2RGB)
        axes[idx].imshow(img_rgb)
        axes[idx].set_title(label)
        axes[idx].axis('off')

    plt.tight_layout()
    plt.show()

    response = input("\nAccept these ROIs? (y/n): ").strip().lower()
    if response != 'y':
        print("ROIs rejected. Exiting.")
        return

    # Save ROIs
    Path("config").mkdir(exist_ok=True)
    with open(f"config/roi_positions_{subject_num}.json", 'w') as f:
        json.dump(rois, f, indent=2)

    # Analyze
    results = {}
    for t in [0, 2, 4, 6]:
        if t not in images:
            continue
        img = images[t]
        print(f"\nAnalyzing timepoint {t}h...")
        for roi_name, roi in rois.items():
            intensities = extract_blue_channel_intensities(img, roi)
            stats_dict = calculate_statistics_from_intensities(intensities)
            if t not in results:
                results[t] = {}
            results[t][roi_name] = {'stats': stats_dict, 'pixel_count': len(intensities)}
            print(f"  {roi_name}: mean={stats_dict['mean']:.2f}, std={stats_dict['std']:.2f}")

    # Export CSV
    rows = []
    for t in [0, 2, 4, 6]:
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
    df.to_csv(f'outputs/reports/uv_analysis_{subject_num}.csv', index=False)
    print(f"\n✓ Results saved to outputs/reports/uv_analysis_{subject_num}.csv")
    print(f"\n✅ Analysis complete for subject {subject_num}!")


if __name__ == "__main__":
    main()