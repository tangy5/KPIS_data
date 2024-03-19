import os
os.environ["OPENCV_IO_MAX_IMAGE_PIXELS"] = pow(2,40).__str__()
import cv2 # import after setting OPENCV_IO_MAX_IMAGE_PIXELS
import numpy as np
import json
from matplotlib import pyplot as plt
from PIL import Image
Image.MAX_IMAGE_PIXELS = None



def json_to_contour():
    json_file = '/home/yuchengt/Downloads/KPI/KIP_process/post/normal-20240304T204345Z-001/normal/out/outnormal mouse W12-M1576 L.czi - Scene #1.json'
    output_dir = '/home/yuchengt/Downloads/KPI/KIP_process/post/normal-20240304T204345Z-001/normal/out'
    name = 'normal mouse W12-M1576 L.czi - Scene #1.json'
    imageshape = [75744,36173] #(y,x)

    f = open(json_file)
    data = json.load(f)
    mask = np.zeros(imageshape, np.uint8)
    
    for i in range(0, len(data)):
        for coord in data[i]['geometry']['coordinates']:
            contours = np.array(coord)
            mask = cv2.fillPoly(mask, [contours.astype(np.int32)], color=(255, 255, 255))
    f.close()
    
    contours = Image.fromarray(mask)
    contours.save(os.path.join(output_dir, f'{name}.png'))

json_to_contour()


def cut_image(contour, xmin, ymin, cnt, classification, width=3840, height=2160):
    # Load image

    directory = 'YOUR_DIRECTORY'
    output_dir = 'YOUR_OUTPUT_DIRECTORY'
    categories = ['']

    for (root, dirs, _) in os.walk(directory, topdown=True):
        for scn in dirs:
            dir = os.path.join(root, scn)
            for filename in os.listdir(dir):
                # if filename.endswith(".jpg"):
                # modify based on your need
                patch_x = int(filename.split(',')[0].split('=')[1])
                patch_y = int(filename.split(',')[1].split('=')[1])

                if not(xmin > patch_x and xmin < patch_x + width and ymin > patch_y and ymin < patch_y + height):
                    continue

                # Crop image
                contour_patch = contour[patch_y:patch_y+height, patch_x:patch_x+width]

                # Convert array to image
                contour_patch = Image.fromarray(contour_patch)

                # Save the cropped image
                # if len(filename.split('_')) == 3:
                #     name = filename.split('.')[0]
                #     contour_patch.save(os.path.join(dir, f'{name}.jpg'))

                # # Display image
                # image.imshow()

                cnt = cnt + 1

def cut_mask(file, contour, xmin, ymin, cnt, classification, width=3840, height=2160):
    # Load image

    directory = 'YOUR_DIRECTORY'
    output_dir = 'YOUR_OUTPUT_DIRECTORY'
    categories = ['']

    for (root, dirs, _) in os.walk(directory, topdown=True):
        for scn in dirs:
            dir = os.path.join(root, scn)
            for filename in os.listdir(dir):
                if file[4:8] == filename[4:8] and filename.endswith(".jpg"):
                    patch_x = int(filename.split(',')[0].split('=')[1])
                    patch_y = int(filename.split(',')[1].split('=')[1])

                    if not(xmin > patch_x and xmin < patch_x + width and ymin > patch_y and ymin < patch_y + height):
                        continue

                    # Crop image
                    contour_patch = contour[patch_y:patch_y+height, patch_x:patch_x+width]

                    # Convert array to image
                    contour_patch = Image.fromarray(contour_patch)

                    # Save the cropped image
                    # if len(filename.split('_')) == 3:

                    if filename.endswith(".jpg"):
                        name = filename.split("]")[0] + "]"
                        contour_patch.save(os.path.join(dir, f'{name}_{cnt}_{classification}.png'))

                    # # Display image
                    # image.imshow()

                    cnt = cnt + 1

if __name__ == "__main__":
    json_to_contour()