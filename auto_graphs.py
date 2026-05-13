import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
from pathlib import Path

# ============================================
# LOAD YOUR DATA
# ============================================
df = pd.read_excel("MASTER_ALL_SUBJECTS.xlsx")

# Sort properly
df['subject'] = df['subject'].astype(int)
df['timepoint_hours'] = df['timepoint_hours'].astype(int)
df = df.sort_values(['subject', 'timepoint_hours'])

# Create output folder
Path("outputs/master_analysis").mkdir(parents=True, exist_ok=True)

print(f"Loaded {len(df)} rows")
print(f"Subjects: {sorted(df['subject'].unique())}")
print(f"Timepoints: {sorted(df['timepoint_hours'].unique())}")

# ============================================
# CREATE LONG-FORMAT SUMMARY (One row per subject per timepoint)
# ============================================
print("\nCreating detailed timepoint summary...")

detailed_rows = []

for subject in sorted(df['subject'].unique()):
    subject_data = df[df['subject'] == subject]

    for timepoint in [0, 2, 4, 6]:
        time_data = subject_data[subject_data['timepoint_hours'] == timepoint]

        row = {
            'subject': subject,
            'timepoint_hours': timepoint,
        }

        for roi in ['sunscreen_left', 'sunscreen_right', 'control']:
            roi_data = time_data[time_data['roi_name'] == roi]

            if len(roi_data) > 0:
                row[f'{roi}_mean'] = roi_data['mean_intensity'].values[0]
                row[f'{roi}_std'] = roi_data['std_dev'].values[0]
                row[f'{roi}_kurtosis'] = roi_data['kurtosis'].values[0] if 'kurtosis' in roi_data.columns else np.nan
                row[f'{roi}_skewness'] = roi_data['skewness'].values[0] if 'skewness' in roi_data.columns else np.nan
            else:
                row[f'{roi}_mean'] = np.nan
                row[f'{roi}_std'] = np.nan
                row[f'{roi}_kurtosis'] = np.nan
                row[f'{roi}_skewness'] = np.nan

        # Calculate protection at this timepoint
        control_mean = row.get('control_mean', np.nan)
        left_mean = row.get('sunscreen_left_mean', np.nan)
        right_mean = row.get('sunscreen_right_mean', np.nan)

        if not np.isnan(control_mean) and control_mean > 0:
            row['sunscreen_left_protection'] = ((control_mean - left_mean) / control_mean) * 100
            row['sunscreen_right_protection'] = ((control_mean - right_mean) / control_mean) * 100
        else:
            row['sunscreen_left_protection'] = np.nan
            row['sunscreen_right_protection'] = np.nan

        detailed_rows.append(row)

detailed_df = pd.DataFrame(detailed_rows)

# Save detailed summary (one row per subject per timepoint)
detailed_df.to_excel('outputs/master_analysis/DETAILED_TIMEPOINT_SUMMARY.xlsx', index=False)
print(f"  ✓ Detailed summary saved: {len(detailed_df)} rows (subjects × 4 timepoints)")

# ============================================
# ALSO CREATE PIVOT SUMMARY (Wide format - easier for comparison)
# ============================================
print("\nCreating pivot summary...")

# Pivot for mean intensity
mean_pivot = detailed_df.pivot_table(
    index='subject',
    columns='timepoint_hours',
    values='sunscreen_left_mean',
    aggfunc='first'
).add_prefix('sunscreen_left_mean_')

# Pivot for kurtosis
kurtosis_pivot = detailed_df.pivot_table(
    index='subject',
    columns='timepoint_hours',
    values='sunscreen_left_kurtosis',
    aggfunc='first'
).add_prefix('sunscreen_left_kurtosis_')

# Combine everything
pivot_summary = pd.concat([mean_pivot, kurtosis_pivot], axis=1)
pivot_summary.reset_index().to_excel('outputs/master_analysis/PIVOT_SUMMARY.xlsx', index=False)

print("  ✓ Pivot summary saved")

# ============================================
# WHAT EACH FILE CONTAINS
# ============================================
print("\n" + "=" * 60)
print("FILES CREATED:")
print("=" * 60)
print("\n1. DETAILED_TIMEPOINT_SUMMARY.xlsx")
print("   → One row per subject per timepoint (4 rows per subject)")
print("   → Columns: subject, timepoint, mean, std, kurtosis, skewness for each ROI")
print("\n2. PIVOT_SUMMARY.xlsx")
print("   → One row per subject, columns split by timepoint")
print("   → Easier to compare 0h vs 6h directly")
print("\n3. COMPLETE_SUMMARY.xlsx (existing)")
print("   → Averaged across timepoints (one row per subject)")
print("=" * 60)