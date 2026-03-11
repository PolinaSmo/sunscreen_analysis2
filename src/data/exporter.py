import pandas as pd
import json
from datetime import datetime
from pathlib import Path

class DataExporter:
    @staticmethod
    def export_all(results, base_name='uv_analysis'):
        Path('outputs/reports').mkdir(parents=True, exist_ok=True)
    
        #CSV using pandas
        df = DataExporter._results_to_dataframe(results)
        csv_path = f'outputs/reports/{base_name}.csv' #define csv_path seperately, doesn't work otherwise (?)
        df.to_csv(csv_path, index=False, float_format='%.2f')
        
        #JSON using pandas to_dict
        json_path = f'outputs/reports/{base_name}.json'
        json_data = {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'exported_from': 'automated_exporter',
            },
            'statistics': df.to_dict('records'),
            'summary': {
                'total_measurements': len(df),
                'timepoints_analyzed': len(results),
            }}
        with open(json_path, 'w') as f:
            json.dump(json_data, f, indent=2)
        # print(f"Exported {csv_path} and {json_path}")
        return df
    @staticmethod
    def _results_to_dataframe(results):
        rows = []
        for time in sorted(results.keys()):
            for roi_type in ['sunscreen', 'control']:
                stats = results[time][roi_type]['stats']
                rows.append({
                    'timepoint_hours': time,
                    'roi_type': roi_type,
                    'min_intensity': stats['min'],
                    'max_intensity': stats['max'],
                    'mean_intensity': stats['mean'],
                    'median_intensity': stats['median'],
                    'std_dev': stats['std'],
                    'range': stats['range'],
                    'pixel_count': stats['pixel_count']
                })
        return pd.DataFrame(rows)
    @staticmethod
    def print_statistics(results):
        df = DataExporter._results_to_dataframe(results)
        print("ANALYSIS RESULTS")
        print(df.round(2).to_string(index=False))