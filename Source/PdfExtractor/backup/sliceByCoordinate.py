from __future__ import division
import os
import numpy as np
import cv2
from wand.image import Image

fileName = "VN101466/SI_HANV07496600.pdf"

with (Image(filename = fileName, resolution = 360)) as source:
    pdfImage = source.convert("jpeg")
    i = 0
    for img in pdfImage.sequence:
        page = Image(image = img)
        page.save(filename = fileName[:-4] + "_" + str(i) + ".jpg")
        i +=1

img = cv2.imread("VN101466/SI_HANV07496600_0.jpg", 0)
print(img.shape)
rect = [10, 20, 1000, 500]

(x, y, width, height) = rect
crop = img[y:y + height, x:x + width]

cv2.imshow("Image", crop)

cv2.waitKey(0)
cv2.destroyAllWindows()
