import cv2
import matplotlib.pyplot as plt


def show_preview_grid(images, timepoint_labels):
    """
    Display a grid of images with ROIs drawn.
    Returns True if user accepts, False if they want to redo.
    """
    n_images = len(images)
    cols = min(4, n_images)
    rows = (n_images + cols - 1) // cols

    fig, axes = plt.subplots(rows, cols, figsize=(16, 4 * rows))
    if rows == 1 and cols == 1:
        axes = [axes]
    else:
        axes = axes.flatten()

    fig.suptitle("ROI Preview - Check all timepoints", fontsize=16)

    for idx, (img, label) in enumerate(zip(images, timepoint_labels)):
        ax = axes[idx]
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        ax.imshow(img_rgb)
        ax.set_title(f"{label}", fontsize=12)
        ax.axis('off')

    # Hide unused subplots
    for idx in range(len(images), len(axes)):
        axes[idx].axis('off')

    plt.tight_layout()
    plt.show()

    response = input("\nAre these ROIs correct for ALL timepoints? (y/n): ").strip().lower()
    return response == 'y'