import cv2
import numpy as np

# Create a test image
img = np.zeros((400, 400, 3), dtype=np.uint8)
cv2.putText(img, "OpenCV Test", (100, 200), 
            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

print("Opening test window...")
cv2.imshow("Test", img)
print("Press any key in the window")
cv2.waitKey(0)
cv2.destroyAllWindows()
print("Test successful!")
