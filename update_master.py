import pandas as pd
from pathlib import Path

# Find all CSV files
csv_files = list(Path("outputs/reports").glob("uv_analysis_*.csv"))

# Read and combine all files with latest data
all_data = []
for file in csv_files:
    subject = file.stem.split("_")[-1]
    df = pd.read_csv(file)
    df['subject'] = subject
    all_data.append(df)

# Combine into one DataFrame
master_df = pd.concat(all_data, ignore_index=True)

# Save master spreadsheet (overwrites with latest data)
master_df.to_excel("MASTER_ALL_SUBJECTS.xlsx", index=False)

print(f"✅ Updated MASTER_ALL_SUBJECTS.xlsx with {len(csv_files)} subjects")
print(f"Total rows: {len(master_df)}")