import numpy as np
from scipy import stats


def calculate_statistics(intensities):
    """Calculate comprehensive statistics for intensity array"""
    if len(intensities) == 0:
        return {}

    # Remove outliers for more accurate kurtosis
    q1 = np.percentile(intensities, 25)
    q3 = np.percentile(intensities, 75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    filtered = intensities[(intensities >= lower) & (intensities <= upper)]

    if len(filtered) < 4:
        filtered = intensities  # fallback if too few points

    stats_dict = {
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
        'iqr': iqr,
        # KURTOSIS - this is what your boss wants!
        # Higher = more consistent coverage, Lower = more variable
        'kurtosis': stats.kurtosis(filtered, fisher=True),  # Fisher=True gives 0 for normal distribution
        'kurtosis_peakedness': 'high' if stats.kurtosis(filtered) > 1 else 'low' if stats.kurtosis(
            filtered) < -1 else 'normal',
        'skewness': stats.skew(filtered) if len(filtered) > 1 else 0,
    }
    return stats_dict