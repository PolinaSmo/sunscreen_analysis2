import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from subject_mapping import all_subjects

csv_files = list(Path("outputs/reports").glob("uv_analysis_*.csv"))
print(f"Found {len(csv_files)} CSV files")
if len(csv_files) == 0:
    print("No CSV files found! Run main.py first to generate data.")
    exit()
all_data = []
for file in csv_files:
    subject_num = int(file.stem.replace("uv_analysis_", ""))
    if subject_num in all_subjects:
        df = pd.read_csv(file)
        df['subject'] = subject_num
        df['group'] = all_subjects[subject_num]['group']
        all_data.append(df)
        print(f"Loaded subject {subject_num} ({all_subjects[subject_num]['group']})")
    else:
        print(f"Warning: Subject {subject_num} not in mapping")

if len(all_data) == 0:
    print("No matching subjects found in mapping!")
    exit()

master_df = pd.concat(all_data, ignore_index=True)
print(f"\nTotal rows: {len(master_df)}")

active_df = master_df[master_df['group'] == 'active']
inactive_df = master_df[master_df['group'] == 'inactive']

print(f"Active subjects: {active_df['subject'].unique().tolist()}")
print(f"Inactive subjects: {inactive_df['subject'].unique().tolist()}")
def create_line_plot(data, group_name, application_type, ax):
    subset = data[data['roi_name'] == application_type]
    if len(subset) == 0:
        print(f"Warning: No data for {group_name} - {application_type}")
        ax.text(0.5, 0.5, f'No data for {group_name}\n{application_type}',
                ha='center', va='center', transform=ax.transAxes)
        return

    # group by timepoint and calculate mean and std across subjects
    grouped = subset.groupby('timepoint_hours')['mean_intensity'].agg(['mean', 'std']).reset_index()
    ax.plot(grouped['timepoint_hours'], grouped['mean'],
            marker='o', linewidth=2, markersize=8, label=f'{group_name} - {application_type}')
    ax.fill_between(grouped['timepoint_hours'], grouped['mean'] - grouped['std'], grouped['mean'] + grouped['std'], alpha=0.2)
    ax.set_xlabel('Time (hours)')
    ax.set_ylabel('Mean Blue Channel Intensity (0-255)\nLower = Better Protection')
    ax.set_title(f'{group_name} Group: {application_type.capitalize()} Application')
    ax.grid(True, alpha=0.3)
    ax.set_xticks([0, 2, 4, 6])
    ax.set_ylim(0, 100)
    ax.legend()

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
# Graph 1: Non-active, Single
create_line_plot(inactive_df, 'Non-Active', 'single', axes[0, 0])
# Graph 2: Non-active, Multiple
create_line_plot(inactive_df, 'Non-Active', 'multiple', axes[0, 1])
# Graph 3: Active, Single
create_line_plot(active_df, 'Active', 'single', axes[1, 0])
# Graph 4: Active, Multiple
create_line_plot(active_df, 'Active', 'multiple', axes[1, 1])

plt.suptitle('Mean Blue Channel Intensity Over Time\n(Lower = Better Protection)', fontsize=16)
plt.tight_layout()
plt.savefig('outputs/FOUR_GRAPHS.png', dpi=150)

for group_name, group_data, color in [('Non-Active', inactive_df, 'blue'), ('Active', active_df, 'red')]:
    fig, ax = plt.subplots(figsize=(10, 6))
    for app_type in ['single', 'multiple']:
        subset = group_data[group_data['roi_name'] == app_type]
        if len(subset) > 0:
            grouped = subset.groupby('timepoint_hours')['mean_intensity'].agg(['mean', 'std']).reset_index()
            ax.plot(grouped['timepoint_hours'], grouped['mean'],
                    marker='o', linewidth=2, markersize=8, label=f'{app_type.capitalize()} Application')
            ax.fill_between(grouped['timepoint_hours'],
                            grouped['mean'] - grouped['std'],
                            grouped['mean'] + grouped['std'],
                            alpha=0.2)
    ax.set_xlabel('Time (hours)')
    ax.set_ylabel('Mean Blue Channel Intensity (0-255)')
    ax.set_title(f'{group_name} Group: Single vs Multiple Application')
    ax.set_xticks([0, 2, 4, 6])
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f'outputs/{group_name}_comparison.png', dpi=150)
    print(f"✓ Saved outputs/{group_name}_comparison.png")