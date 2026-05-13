import pandas as pd
from pathlib import Path

# Find all CSV files
csv_files = list(Path("outputs/reports").glob("uv_analysis_*.csv"))

all_data = []

for file in csv_files:
    # This gets the number after the last underscore
    subject = file.stem.split("_")[-1]

    # If subject is like "1" or "2" (not "11"), it will still work
    df = pd.read_csv(file)
    df['subject'] = subject
    all_data.append(df)
    print(f"Loaded subject {subject} from {file.name}")

# Combine everything
if all_data:
    master_df = pd.concat(all_data, ignore_index=True)
    master_df.to_excel("MASTER_ALL_SUBJECTS.xlsx", index=False)
    print(f"\n✅ Updated MASTER_ALL_SUBJECTS.xlsx with {len(csv_files)} subjects")
    print(f"Total rows: {len(master_df)}")
    print(f"Subjects included: {sorted(master_df['subject'].unique())}")
else:
    print("No CSV files found!")