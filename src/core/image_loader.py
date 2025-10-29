import cv2
from pathlib import Path

class ImageLoader:
    def __init__(self):
        self.images = []
        self.image_paths = []
    
    def load_images(self,image_paths):
        self.image_paths = sorted(image_paths)
        self.images = []
        #make sure image exists - saves time later
        for path in self.image_paths:
            img = cv2.imread(str(path))
            if img is None:
                raise FileNotFoundError(f"Could not load image: {path}")
            self.images.append(img)
            print(f"Loaded: {path} - Shape: {img.shape}")
        
        return self.images
