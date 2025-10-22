import matplotlib.pyplot as plt

class Plotter:
    @staticmethod
    def plot_intensity_distributions(results, save_path='intensity_distributions.png'):
        """Plot histograms of intensity distributions"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Intensity Distributions Across Timepoints', fontsize=16)
        
        for idx, time in enumerate(sorted(results.keys())):
            ax = axes[idx // 2, idx % 2]
            
            sunscreen_int = results[time]['sunscreen']['intensities']
            control_int = results[time]['control']['intensities']
            
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
