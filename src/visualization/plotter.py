import matplotlib.pyplot as plt
import numpy as np

class Plotter:
    @staticmethod
    def plot_intensity_distributions(results, save_path='intensity_distributions.png'):
        timepoints = sorted(results.keys())
        n_times = len(timepoints)

        #create subplots grid
        cols = 2
        rows = (n_times + cols - 1) // cols
        fig, axes = plt.subplots(rows, cols, figsize=(15, 5 * rows))

        if n_times > 1:
            axes = axes.flatten()
        else:
            axes = [axes]
        first_time = timepoints[0]
        roi_names = list(results[first_time].keys())
        n_rois = len(roi_names)
        colors = plt.cm.tab10(np.linspace(0, 1, n_rois))
        color_map = {name: colors[i] for i, name in enumerate(roi_names)}

        for idx, time in enumerate(timepoints):
            ax = axes[idx]
            time_data = results[time]
            for roi_name in roi_names:
                intensities = time_data[roi_name]['intensities']
                ax.hist(intensities, bins=50, alpha=0.6,
                        label=roi_name, color=color_map[roi_name],
                        edgecolor='black')

            ax.set_xlabel('Intensity')
            ax.set_ylabel('Pixel Count')
            ax.set_title(f'Timepoint: {time} hours')
            ax.legend()
            ax.grid(True, alpha=0.3)
        for idx in range(n_times, len(axes)):
            axes[idx].set_visible(False)

        plt.tight_layout()
        plt.savefig(save_path, dpi=300)
        print(f"Histograms saved to: {save_path}")
        plt.close()