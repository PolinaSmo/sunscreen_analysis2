import numpy as np

def calculate_statistics(intensities):
    """Calculate statistics for intensity array"""
    stats = {
        'min': np.min(intensities),
        'max': np.max(intensities),
        'mean': np.mean(intensities),
        'median': np.median(intensities),
        'std': np.std(intensities),
        'range': np.max(intensities) - np.min(intensities),
        'pixel_count': len(intensities)
    }
    return stats
