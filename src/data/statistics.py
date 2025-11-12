import numpy as np
from scipy import stats as scipy_stats
def calculate_statistics(intensities):
    stats_dict = {
        'min': np.min(intensities),
        'max': np.max(intensities),
        'mean': np.mean(intensities),
        'median': np.median(intensities),
        'std': np.std(intensities),
        'range': np.max(intensities) - np.min(intensities),
        'pixel_count': len(intensities),
        #as many stats as could be useful, can delete/add more later
        'variance': np.var(intensities),
        'q1': np.percentile(intensities, 25),
        'q3': np.percentile(intensities, 75),
        'iqr': np.percentile(intensities, 75) - np.percentile(intensities, 25), 
        'skewness': scipy_stats.skew(intensities) if len(intensities) > 1 else 0,
        'kurtosis': scipy_stats.kurtosis(intensities) if len(intensities) > 1 else 0,
    }
    return stats_dict