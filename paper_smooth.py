from skimage.feature import hessian_matrix, hessian_matrix_eigvals
import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
from PIL import Image

def detect_ridges(gray, sigma=2.5):
    hessian = hessian_matrix(gray, sigma)
    i1, i2 = hessian_matrix_eigvals(hessian)
    print(i1.shape, i2.shape)
    return i1, i2

original = "sources/foil.jpg"
source_path = f"clean/clean_{original[8:-4]}.jpg"
ridge_detection_sigma = 7.0 #! change sigma to generate fake results
cwd = os.getcwd()

source_image = cv2.imread(source_path,cv2.IMREAD_GRAYSCALE|cv2.IMREAD_IGNORE_ORIENTATION)
# source_image = Image.open(source_image)

i1, i2 = detect_ridges(source_image, ridge_detection_sigma)

# # Apply a threshold to get a binary image
thresh = np.mean(i1)
i1_binary = (i1 > thresh).astype(np.uint8)

thresh = np.mean(i2)
i2_binary = (i2 > thresh).astype(np.uint8)

# # Normalize the binary images for display
i1_normalized = cv2.normalize(i1_binary, None, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)
i2_normalized = cv2.normalize(i2_binary, None, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)

# print(i1, i2)

# Scale the images back to the range [0, 255]
i1_scaled = (i1_normalized * 255).astype(np.uint8)
i2_scaled = (i2_normalized * 255).astype(np.uint8)
mask_img = i1_scaled

mask_path = f"{cwd}\mask\mask_ridge\{original[8:-4]}_ridge_{ridge_detection_sigma}.png"
cv2.imwrite(mask_path,mask_img)


# Open the image and mask files
image_file_object = Image.open(f'{source_path}')
mask_file_object = Image.open(f'{mask_path}')
# image_file_object.show()
# mask_file_object.show()
print(f"Image Size: {image_file_object.size} bytes")
print(f"Mask Size: {mask_file_object.size} bytes")

import requests

with open(source_path, 'rb') as image_file_object, open(mask_path, 'rb') as mask_file_object:
    print("sending request",image_file_object,mask_file_object)
    r = requests.post('https://clipdrop-api.co/cleanup/v1',
    files = {
        'image_file': ('image.jpg', image_file_object, 'image/jpeg'),
        'mask_file': ('mask.png', mask_file_object, 'image/png')
        },
    headers = { 'x-api-key': 'ab1766927c62c3dc638f0e08f635c2dc6efb012ebdf82bab8014a2cfa423dd1badbdf2fadb47022ba43c915c8eb06891'}
    )

    if (r.ok):
        print("success")
        # r.content contains the bytes of the returned image
        with open(f"{cwd}\clean\clean_curves\clean_curves_{original[8:-4]}.jpg", 'wb') as f:
            f.write(r.content)
    else:
        print("failure",r.json())
        r.raise_for_status()

# # Display the results
result_path = f"{cwd}\\results\\final_{original[8:-4]}_sigma={ridge_detection_sigma}.jpg"
background = Image.open(f"{cwd}\clean\clean_curves\clean_curves_{original[8:-4]}.jpg")
foreground = Image.open(f"{cwd}\\extractedObj\extracted_{original[8:-4]}.png")
background.paste(foreground, (0, 0), foreground)
background.save(result_path)