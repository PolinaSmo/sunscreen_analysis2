import json
import csv
from datetime import datetime
import numpy as np

class DataExporter:
    @staticmethod
    def save_to_csv(results, output_file='uv_analysis_results.csv'):
        """Save results to CSV file"""
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            # Header
            writer.writerow(["Timepoint (hours)", "ROI Type", "Min", "Max", "Mean", 
                            "Median", "Std Dev", "Range", "Pixel Count"])
            
            # Data
            for time in sorted(results.keys()):
                for roi_type in ['sunscreen', 'control']:
                    stats = results[time][roi_type]['stats']
                    intensities = results[time][roi_type]['intensities']
                    
                    writer.writerow([
                        time, roi_type, f"{stats['min']:.2f}", f"{stats['max']:.2f}",
                        f"{stats['mean']:.2f}", f"{stats['median']:.2f}", f"{stats['std']:.2f}",
                        f"{stats['range']:.2f}", len(intensities)
                    ])
        
        print(f"CSV results saved to: {output_file}")
    
    @staticmethod
    def save_to_json(results, output_file='analysis_results.json'):
        """Save results to JSON file with human-readable structure"""
        
        # Convert numpy data to JSON-serializable format
        json_results = {}
        for time, data in results.items():
            json_results[time] = {
                'sunscreen': {
                    'intensities': DataExporter._convert_to_serializable(data['sunscreen']['intensities']),
                    'stats': DataExporter._convert_stats_to_serializable(data['sunscreen']['stats'])
                },
                'control': {
                    'intensities': DataExporter._convert_to_serializable(data['control']['intensities']),
                    'stats': DataExporter._convert_stats_to_serializable(data['control']['stats'])
                }
            }
        
        json_data = {
            'analysis_metadata': {
                'timestamp': datetime.now().isoformat(),
                'timepoints': list(results.keys()),
                'total_timepoints': len(results)
            },
            'results': json_results,
            'summary': {
                'total_pixels_analyzed': {
                    str(time): {
                        'sunscreen': len(results[time]['sunscreen']['intensities']),
                        'control': len(results[time]['control']['intensities'])
                    } for time in results.keys()
                }
            }
        }
        
        with open(output_file, 'w') as f:
            json.dump(json_data, f, indent=2)
        
        print(f"JSON results saved to: {output_file}")
    
    @staticmethod
    def _convert_to_serializable(data):
        """Convert numpy arrays to Python lists with native types"""
        if hasattr(data, 'tolist'):
            # Convert numpy array to list and ensure native Python types
            return [int(x) for x in data.tolist()]
        elif isinstance(data, (np.integer, np.floating)):
            # Convert numpy scalars to Python native types
            return data.item()
        elif isinstance(data, (list, np.ndarray)):
            # Handle lists and arrays
            return [int(x) if isinstance(x, (np.integer, np.uint8)) else float(x) if isinstance(x, np.floating) else x for x in data]
        return data
    
    @staticmethod
    def _convert_stats_to_serializable(stats):
        """Convert statistics to JSON-serializable types"""
        serializable_stats = {}
        for key, value in stats.items():
            if isinstance(value, (np.integer, np.uint8)):
                serializable_stats[key] = int(value)
            elif isinstance(value, np.floating):
                serializable_stats[key] = float(value)
            else:
                serializable_stats[key] = value
        return serializable_stats
    
    @staticmethod
    def print_statistics(results):
        """Print statistics in a readable format"""
        print("\n" + "="*80)
        print("ANALYSIS RESULTS")
        print("="*80)
        
        for time in sorted(results.keys()):
            print(f"\n--- Timepoint: {time} hours ---")
            
            for roi_type in ['sunscreen', 'control']:
                stats = results[time][roi_type]['stats']
                print(f"\n  {roi_type.upper()} ROI:")
                print(f"    Min intensity:    {stats['min']:.2f}")
                print(f"    Max intensity:    {stats['max']:.2f}")
                print(f"    Mean intensity:   {stats['mean']:.2f}")
                print(f"    Median intensity: {stats['median']:.2f}")
                print(f"    Std Dev:          {stats['std']:.2f}")
                print(f"    Range:            {stats['range']:.2f}")
