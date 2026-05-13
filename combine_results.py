import pandas as pd
from pathlib import Path

csv_files = list(Path("outputs/reports").glob("uv_analysis_*.csv"))

# Read and combine all files
all_data = []
for file in csv_files:
    subject = file.stem.split("_")[-1]  # gets "11" from "uv_analysis_11"

    df = pd.read_csv(file)

    df['subject'] = subject

    all_data.append(df)

master_df = pd.concat(all_data, ignore_index=True)

# Save master spreadsheet
master_df.to_excel("MASTER_ALL_SUBJECTS.xlsx", index=False)
master_df.to_csv("MASTER_ALL_SUBJECTS.csv", index=False)

print(f"✓ Combined {len(csv_files)} files into MASTER_ALL_SUBJECTS.xlsx")
print(f"Total rows: {len(master_df)}")
print("\nColumns include: subject, timepoint_hours, roi_name, mean_intensity, etc.")