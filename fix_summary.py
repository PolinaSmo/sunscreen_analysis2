import pandas as pd
import numpy as np
from pathlib import Path

csv_files = list(Path('outputs/reports').glob('uv_analysis_*.csv'))
print(f'Found {len(csv_files)} CSV files')

all_data = []
for f in csv_files:
    subject = f.stem.replace('uv_analysis_', '')
    df = pd.read_csv(f)
    df['subject'] = subject
    all_data.append(df)
    print(f'  Loaded subject {subject}')
master_df = pd.concat(all_data, ignore_index=True)

summary_data = []

for subject in sorted(master_df['subject'].unique(), key=lambda x: int(x)):
    subject_data = master_df[master_df['subject'] == subject]

    row = {'subject': subject}

    for roi in ['sunscreen_left', 'sunscreen_right', 'control']:
        roi_data = subject_data[subject_data['roi_name'] == roi]

        if len(roi_data) > 0:
            row[f'{roi}_mean_0h'] = roi_data[roi_data['timepoint_hours'] == 0]['mean_intensity'].values[0] if len(
                roi_data[roi_data['timepoint_hours'] == 0]) > 0 else np.nan
            row[f'{roi}_std_0h'] = roi_data[roi_data['timepoint_hours'] == 0]['std_dev'].values[0] if len(
                roi_data[roi_data['timepoint_hours'] == 0]) > 0 else np.nan

            row[f'{roi}_mean_2h'] = roi_data[roi_data['timepoint_hours'] == 2]['mean_intensity'].values[0] if len(
                roi_data[roi_data['timepoint_hours'] == 2]) > 0 else np.nan
            row[f'{roi}_std_2h'] = roi_data[roi_data['timepoint_hours'] == 2]['std_dev'].values[0] if len(
                roi_data[roi_data['timepoint_hours'] == 2]) > 0 else np.nan

            row[f'{roi}_mean_4h'] = roi_data[roi_data['timepoint_hours'] == 4]['mean_intensity'].values[0] if len(
                roi_data[roi_data['timepoint_hours'] == 4]) > 0 else np.nan
            row[f'{roi}_std_4h'] = roi_data[roi_data['timepoint_hours'] == 4]['std_dev'].values[0] if len(
                roi_data[roi_data['timepoint_hours'] == 4]) > 0 else np.nan

            row[f'{roi}_mean_6h'] = roi_data[roi_data['timepoint_hours'] == 6]['mean_intensity'].values[0] if len(
                roi_data[roi_data['timepoint_hours'] == 6]) > 0 else np.nan
            row[f'{roi}_std_6h'] = roi_data[roi_data['timepoint_hours'] == 6]['std_dev'].values[0] if len(
                roi_data[roi_data['timepoint_hours'] == 6]) > 0 else np.nan

            row[f'{roi}_mean_avg'] = roi_data['mean_intensity'].mean()

            row[f'{roi}_kurtosis'] = roi_data['kurtosis'].values[0] if 'kurtosis' in roi_data.columns and len(
                roi_data) > 0 else np.nan

    control_avg = row.get('control_mean_avg', np.nan)
    left_avg = row.get('sunscreen_left_mean_avg', np.nan)
    right_avg = row.get('sunscreen_right_mean_avg', np.nan)

    if not np.isnan(control_avg) and control_avg > 0:
        row['sunscreen_left_protection'] = ((control_avg - left_avg) / control_avg) * 100
        row['sunscreen_right_protection'] = ((control_avg - right_avg) / control_avg) * 100
    else:
        row['sunscreen_left_protection'] = np.nan
        row['sunscreen_right_protection'] = np.nan

    summary_data.append(row)

summary_df = pd.DataFrame(summary_data)

column_order = [
    'subject',
    'sunscreen_left_mean_0h', 'sunscreen_left_std_0h',
    'sunscreen_left_mean_2h', 'sunscreen_left_std_2h',
    'sunscreen_left_mean_4h', 'sunscreen_left_std_4h',
    'sunscreen_left_mean_6h', 'sunscreen_left_std_6h',
    'sunscreen_left_mean_avg', 'sunscreen_left_kurtosis',
    'sunscreen_right_mean_0h', 'sunscreen_right_std_0h',
    'sunscreen_right_mean_2h', 'sunscreen_right_std_2h',
    'sunscreen_right_mean_4h', 'sunscreen_right_std_4h',
    'sunscreen_right_mean_6h', 'sunscreen_right_std_6h',
    'sunscreen_right_mean_avg', 'sunscreen_right_kurtosis',
    'control_mean_0h', 'control_std_0h',
    'control_mean_2h', 'control_std_2h',
    'control_mean_4h', 'control_std_4h',
    'control_mean_6h', 'control_std_6h',
    'control_mean_avg', 'control_kurtosis',
    'sunscreen_left_protection', 'sunscreen_right_protection'
]

existing_cols = [col for col in column_order if col in summary_df.columns]
summary_df = summary_df[existing_cols]

for col in summary_df.columns:
    if col != 'subject':
        summary_df[col] = summary_df[col].apply(
            lambda x: round(x, 2) if isinstance(x, (int, float)) and not pd.isna(x) else x)
avg_row = {'subject': 'AVERAGE'}
for col in existing_cols:
    if col != 'subject':
        values = summary_df[col].dropna().values
        if len(values) > 0 and isinstance(values[0], (int, float)):
            avg_row[col] = round(values.mean(), 2)
        else:
            avg_row[col] = ''
summary_df = pd.concat([summary_df, pd.DataFrame([avg_row])], ignore_index=True)

std_row = {'subject': 'STD_DEV'}
subjects_only = summary_df[summary_df['subject'] != 'AVERAGE']
for col in existing_cols:
    if col != 'subject':
        values = subjects_only[col].dropna().values
        if len(values) > 0 and isinstance(values[0], (int, float)):
            std_row[col] = round(values.std(), 2)
        else:
            std_row[col] = ''
summary_df = pd.concat([summary_df, pd.DataFrame([std_row])], ignore_index=True)

Path('outputs/master_analysis').mkdir(exist_ok=True)
summary_df.to_excel('outputs/master_analysis/COMPLETE_SUMMARY.xlsx', index=False)

print(f'\n✓ COMPLETE_SUMMARY.xlsx saved in EXACT format')
print(f'  Shape: {summary_df.shape}')
print(f'  Columns: {list(summary_df.columns)[:5]}...{list(summary_df.columns)[-3:]}')
print(f'\nSubjects: {summary_df["subject"].tolist()}')