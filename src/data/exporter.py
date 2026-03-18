import pandas as pd
import json
from datetime import datetime
from pathlib import Path

class DataExporter:
    @staticmethod
    def export_all(results, base_name='uv_analysis'):
        """Export results to CSV and JSON."""
        Path('outputs/reports').mkdir(parents=True, exist_ok=True)

        df = DataExporter._results_to_dataframe(results)
        csv_path = f'outputs/reports/{base_name}.csv'
        df.to_csv(csv_path, index=False, float_format='%.2f')

        json_path = f'outputs/reports/{base_name}.json'
        json_data = {
            'metadata': {'timestamp': datetime.now().isoformat()},
            'statistics': df.to_dict('records'),
            'summary': {'total_measurements': len(df)}
        }
        with open(json_path, 'w') as f:
            json.dump(json_data, f, indent=2)

        print(f"✓ Exported {csv_path} and {json_path}")
        return df

    @staticmethod
    def _results_to_dataframe(results):
        """Convert nested results dictionary to a flat DataFrame."""
        rows = []
        for time in sorted(results.keys()):
            for roi_name, roi_data in results[time].items():
                s = roi_data['stats']
                rows.append({
                    'timepoint_hours': time,
                    'roi_name': roi_name,
                    'min_intensity': s['min'],
                    'max_intensity': s['max'],
                    'mean_intensity': s['mean'],
                    'median_intensity': s['median'],
                    'std_dev': s['std'],
                    'range': s['range'],
                    'pixel_count': s['pixel_count']
                })
        return pd.DataFrame(rows)

    @staticmethod
    def print_statistics(results):
        """Print a human‑readable table of statistics."""
        df = DataExporter._results_to_dataframe(results)
        print("\n" + "=" * 80)
        print("ANALYSIS RESULTS")
        print("=" * 80)
        print(df.round(2).to_string(index=False))