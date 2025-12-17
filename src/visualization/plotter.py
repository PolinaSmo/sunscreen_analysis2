import matplotlib.pyplot as plt
import numpy as np
import matplotlib
matplotlib.use('TkAgg')

class Plotter:
    @staticmethod

    def optimal_bins(data):
            #freedman-diaconis rule
            iqr = np.percentile(data,75) - np.percentile(data,25)
            bin_width = 2 * iqr * (len(data) ** (-1/3))
            return max(10, int((max(data) - min(data)) / bin_width))
    
    def plot_intensity_distributions(results, save_path='intensity_distributions.png'):
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Intensity Distributions Across Timepoints', fontsize=16)
        
        for idx, time in enumerate(sorted(results.keys())):
            ax = axes[idx // 2, idx % 2]
            
            sunscreen_int = results[time]['sunscreen']['intensities']
            control_int = results[time]['control']['intensities']
            
            bins = Plotter.optimal_bins(np.concatenate([sunscreen_int, control_int]))

            ax.hist(sunscreen_int, bins=50, alpha=0.6, label='Sunscreen', color='green', edgecolor='black')
            ax.hist(control_int, bins=50, alpha=0.6, label='Control', color='red', edgecolor='black')
            
            ax.set_xlabel('Intensity (0-255)')
            ax.set_ylabel('Pixel Count')
            ax.set_title(f'Timepoint: {time} hours')
            ax.legend()
            ax.grid(True, alpha=0.3)
        
        
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Histograms saved to: {save_path}")
        # Removed plt.show() to avoid the non-interactive warning
