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

    # Calculate base statistics
    kurt = stats.kurtosis(filtered, fisher=True)
    skew = stats.skew(filtered) if len(filtered) > 1 else 0

    # NEW: Quality Score = Kurtosis / |Skewness|
    # Higher score = better, more even coverage
    if abs(skew) > 0.01:
        quality_score = kurt / abs(skew)
    else:
        quality_score = kurt * 10 if kurt > 0 else 0  # Handle near-zero skew

    # Classification based on quality score
    if quality_score > 2:
        quality_rating = "Excellent"
    elif quality_score > 1:
        quality_rating = "Good"
    elif quality_score > 0.5:
        quality_rating = "Moderate"
    else:
        quality_rating = "Poor"

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
        'kurtosis': kurt,
        'kurtosis_peakedness': 'high' if kurt > 1 else 'low' if kurt < -1 else 'normal',
        'skewness': skew,
        'quality_score': quality_score,
        'quality_rating': quality_rating,
    }
    return stats_dict