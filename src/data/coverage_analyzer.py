import numpy as np


class CoverageAnalyzer:
    @staticmethod
    def classify_coverage(intensity_stats, kurtosis_threshold_high=1.0, kurtosis_threshold_low=-1.0):

        kurtosis = intensity_stats['kurtosis']
        mean_intensity = intensity_stats['mean']

        if kurtosis > kurtosis_threshold_high:
            if mean_intensity < 30:
                return "EXCELLENT - Even coverage, good protection"
            elif mean_intensity < 50:
                return "GOOD - Even coverage, moderate protection"
            else:
                return "FAIR - Even coverage but weak protection"
        elif kurtosis < kurtosis_threshold_low:
            if mean_intensity < 30:
                return "POOR - Uneven coverage (streaky), but some protection"
            else:
                return "VERY POOR - Uneven, spotty coverage, weak protection"
        else:
            if mean_intensity < 30:
                return "MODERATE - Decent coverage, consistent enough"
            else:
                return "MODERATE - Acceptable coverage, room for improvement"

    @staticmethod
    def compare_methods(results_method1, results_method2, timepoint=4):

        method1_kurtosis = results_method1[timepoint]['sunscreen']['stats']['kurtosis']
        method2_kurtosis = results_method2[timepoint]['sunscreen']['stats']['kurtosis']
        method1_mean = results_method1[timepoint]['sunscreen']['stats']['mean']
        method2_mean = results_method2[timepoint]['sunscreen']['stats']['mean']

        print(f"\n=== Comparison at {timepoint}h ===")
        print(f"Method 1 (Single application): Kurtosis={method1_kurtosis:.2f}, Mean={method1_mean:.2f}")
        print(f"Method 2 (Reapplication):     Kurtosis={method2_kurtosis:.2f}, Mean={method2_mean:.2f}")

        if method2_kurtosis > method1_kurtosis and method2_mean < method1_mean:
            return "Reapplication method provides MORE EVEN and BETTER PROTECTION"
        elif method2_kurtosis > method1_kurtosis:
            return "Reapplication provides MORE EVEN coverage, but protection similar"
        elif method2_mean < method1_mean:
            return "Reapplication provides BETTER PROTECTION, but coverage similar"
        else:
            return "Methods show similar performance"