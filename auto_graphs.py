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
# CREATE COMPLETE SUMMARY WITH ALL TIMEPOINTS
# ============================================
print("\nCreating complete summary with all timepoints...")

summary_data = []

for subject in sorted(df['subject'].unique()):
    subject_data = df[df['subject'] == subject]

    row = {'subject': subject}

    for roi in ['sunscreen_left', 'sunscreen_right', 'control']:
        roi_data = subject_data[subject_data['roi_name'] == roi].sort_values('timepoint_hours')

        if len(roi_data) > 0:
            # Mean intensity at each timepoint
            for t in [0, 2, 4, 6]:
                t_data = roi_data[roi_data['timepoint_hours'] == t]
                if len(t_data) > 0:
                    row[f'{roi}_mean_{t}h'] = t_data['mean_intensity'].values[0]
                    row[f'{roi}_std_{t}h'] = t_data['std_dev'].values[0]  # WITHIN-ROI STD DEV!
                else:
                    row[f'{roi}_mean_{t}h'] = np.nan
                    row[f'{roi}_std_{t}h'] = np.nan

            # Overall average across all timepoints
            row[f'{roi}_mean_avg'] = roi_data['mean_intensity'].mean()
            row[f'{roi}_kurtosis'] = roi_data['kurtosis'].values[0] if 'kurtosis' in roi_data.columns else np.nan

    # Calculate protection % at each timepoint
    for t in [0, 2, 4, 6]:
        control_mean = row.get(f'control_mean_{t}h', np.nan)
        left_mean = row.get(f'sunscreen_left_mean_{t}h', np.nan)
        right_mean = row.get(f'sunscreen_right_mean_{t}h', np.nan)

        if not np.isnan(control_mean) and control_mean > 0:
            row[f'sunscreen_left_protection_{t}h'] = ((control_mean - left_mean) / control_mean) * 100
            row[f'sunscreen_right_protection_{t}h'] = ((control_mean - right_mean) / control_mean) * 100
        else:
            row[f'sunscreen_left_protection_{t}h'] = np.nan
            row[f'sunscreen_right_protection_{t}h'] = np.nan

    summary_data.append(row)

summary_df = pd.DataFrame(summary_data)

# Add AVERAGE row
avg_row = {'subject': 'AVERAGE'}
for col in summary_df.columns:
    if col != 'subject':
        values = summary_df[col].dropna().values
        avg_row[col] = round(values.mean(), 2) if len(values) > 0 else np.nan
summary_df = pd.concat([summary_df, pd.DataFrame([avg_row])], ignore_index=True)

# Add STD_DEV row (across subjects)
std_row = {'subject': 'STD_DEV'}
subjects_only = summary_df[summary_df['subject'] != 'AVERAGE']
for col in summary_df.columns:
    if col != 'subject':
        values = subjects_only[col].dropna().values
        std_row[col] = round(values.std(), 2) if len(values) > 0 else ''
summary_df = pd.concat([summary_df, pd.DataFrame([std_row])], ignore_index=True)

# Save to Excel
summary_df.to_excel('outputs/master_analysis/COMPLETE_SUMMARY.xlsx', index=False)
print("  ✓ Complete summary saved with all timepoints and within-ROI std dev")

# ============================================
# PRINT PREVIEW
# ============================================
print("\n" + "=" * 80)
print("PREVIEW - What each column means:")
print("=" * 80)
print("  *_mean_Xh = Average brightness at that timepoint (lower = better)")
print("  *_std_Xh  = Standard deviation WITHIN the ROI at that timepoint")
print("             (lower = more even coverage)")
print("  *_protection_Xh = % of UV blocked at that timepoint")
print("=" * 80)

print("\nFirst few columns of summary:")
print(summary_df.columns.tolist()[:15])
print("\nFirst data row (subject 11):")
print(summary_df.iloc[0].to_dict())

print("\n✅ COMPLETE_SUMMARY.xlsx now includes:")
print("  - All timepoints (0, 2, 4, 6 hours)")
print("  - Mean intensity at each timepoint")
print("  - WITHIN-ROI standard deviation at each timepoint")
print("  - Protection % at each timepoint")
print("  - AVERAGE row (across subjects)")
print("  - STD_DEV row (variation across subjects)")