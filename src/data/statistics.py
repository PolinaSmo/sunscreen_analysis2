import numpy as np

def calculate_statistics(intensities):
    stats = {
        'min': np.min(intensities),
        'max': np.max(intensities),
        'mean': np.mean(intensities),
        'median': np.median(intensities),
        'std': np.std(intensities),
        'range': np.max(intensities) - np.min(intensities),
        'pixel_count': len(intensities),
        'variance': np.var(intensities),
        'q1': np.percentile(intensities, 25),
        'q3': np.percentile(intensities, 75),
        'iqr': np.percentile(intensities, 75) - np.percentile(intensities, 25)
    }
    return stats
