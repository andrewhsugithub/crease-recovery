import cv2
import numpy as np
import os
from PIL import Image, ImageOps

def dilate(img, gaussian_sigma):
    blurred_img = cv2.GaussianBlur(img, (gaussian_sigma, gaussian_sigma), 0)
    # cv2.imshow("blurred_img", blurred_img)
    # new_mask = cv2.threshold(blurred_img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    (threshold_value, new_mask) = cv2.threshold(blurred_img, 0, 255, cv2.THRESH_BINARY)
    print("threshold_value",threshold_value)
    return new_mask

source_path = "sources/foil.jpg"
cwd = os.getcwd()

# source_image = cv2.imread(source_path,cv2.IMREAD_GRAYSCALE|cv2.IMREAD_IGNORE_ORIENTATION)
# source_image = Image.open(source_path)
# source_image = np.asarray(source_image)



# # TODO: https://hackmd.io/@cws0701/SJiFl5Ghq edge detection 
# #! change to edge detection instead of remove bg api
# edge_mask = cv2.Canny(mask_img, 100, 200)

# cv2.imshow("org_mask_img", edge_mask)
# cv2.imshow("new_mask_img", new_edge_mask_img)
# cv2.waitKey(0)


import requests
with open(source_path, 'rb') as image_file_object:
    r = requests.post('https://clipdrop-api.co/remove-background/v1',
    files = {
        'image_file': ('image.jpg', image_file_object, 'image/jpeg'),
        },
    headers = { 'x-api-key': 'ab1766927c62c3dc638f0e08f635c2dc6efb012ebdf82bab8014a2cfa423dd1badbdf2fadb47022ba43c915c8eb06891'}
    )
    if (r.ok):
        # r.content contains the bytes of the returned image
        print("success")
        # r.content contains the bytes of the returned image
        extracted_path = f"{cwd}\\extractedObj\extracted_{source_path[8:-4]}.png"
        with open(extracted_path, 'wb') as f:
            f.write(r.content)
        foreground = Image.open(extracted_path)
        # foreground = ImageOps.exif_transpose(foreground)
        # foreground = cv2.imread(extracted_path, cv2.IMREAD_IGNORE_ORIENTATION)
        # exif = foreground.getexif()
        # height, width = foreground.shape
        width, height = foreground.size
        edge_mask = np.asarray(foreground)
        # edge_mask = cv2.imread(mask_path)
        # print(edge_mask)
        # cv2.imshow("org_mask_img", edge_mask)
        # cv2.waitKey(0)

        guassian_sigma = 11 #! change sigma to generate fake results
        new_edge_mask_img = dilate(edge_mask, guassian_sigma)
        new_edge_mask_image = Image.fromarray(np.uint8(new_edge_mask_img))
        background = Image.new('RGBA', (width, height), (0, 0, 0, 1))
        background.paste(new_edge_mask_image, (0, 0), new_edge_mask_image)
        mask_path = f"{cwd}\mask\\foreground_mask_{source_path[8:-4]}_sigma={guassian_sigma}.png"
        new_edge_mask= np.asarray(background)
        # cv2.imwrite(mask_path, new_edge_mask)
        background.save(mask_path)
    else:
        print("failure",r.json())
        r.raise_for_status()


# Open the image and mask files
image_file_object = Image.open(f'{source_path}')
# image_file_object = ImageOps.exif_transpose(image_file_object)
mask_file_object = Image.open(f'{mask_path}')
# mask_file_object = ImageOps.exif_transpose(mask_file_object)
# image_file_object.show()
# # mask_file_object.show()
print(f"Image Size: {image_file_object.size} bytes")
print(f"Mask Size: {mask_file_object.size} bytes")

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
        with open(f"{cwd}\clean\clean_{source_path[8:-4]}.jpg", 'wb') as f:
            f.write(r.content)
    else:
        print("failure",r.json())
        r.raise_for_status()
        
