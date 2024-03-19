from PIL import Image, ImageDraw, ImageFile
import numpy as np
import os

from aicsimageio import AICSImage
import cv2 
from scipy.ndimage import center_of_mass

def downsample_image(image, factor=2):
    """Downsample the image by a specified factor: load highest 40x resolution WSI and use 20x for patch cropping"""
    new_size = (image.width // factor, image.height // factor)
    return image.resize(new_size, Image.ANTIALIAS)

def calculate_tiles(image_size, tile_size, overlap):
    """Calculate tile coordinates for cropping, with overlap."""
    x_coords = range(0, image_size[0], int(tile_size[0] * (1 - overlap)))
    y_coords = range(0, image_size[1], int(tile_size[1] * (1 - overlap)))
    return [(x, y) for y in y_coords for x in x_coords]

def crop_and_pad(image, mask, top_left, tile_size):
    """Crop and pad."""
    bottom_right = (top_left[0] + tile_size[0], top_left[1] + tile_size[1])
    cropped_image = Image.new('RGB', tile_size, (255, 255, 255))
    cropped_mask = Image.new('L', tile_size, (255,))

    cropped_image.paste(image.crop((top_left[0], top_left[1], bottom_right[0], bottom_right[1])), (0, 0))
    cropped_mask.paste(mask.crop((top_left[0], top_left[1], bottom_right[0], bottom_right[1])), (0, 0))
    return cropped_image, cropped_mask

def save_tiles(image, mask, tiles, tile_size, output_folder, subject_name):
    """Save image and mask tiles"""
    for index, (x, y) in enumerate(tiles):
        cropped_image, cropped_mask = crop_and_pad(image, mask, (x, y), tile_size)
        image_name = f"{subject_name}_{index}_{x}_{y}_img.jpg"
        mask_name = f"{subject_name}_{index}_{x}_{y}_mask.jpg"

        cropped_image.save(os.path.join(output_folder, image_name), 'JPEG')
        cropped_mask.save(os.path.join(output_folder, mask_name), 'JPEG')

        overlay_image(cropped_image, cropped_mask, os.path.join(output_folder, f"{subject_name}_{index}_{x}_{y}_overlay.jpg"))
        print("Saved image {}: Index:{}, Coord: {}_{}".format(subject_name, index, x,y))

def overlay_image(image, mask, output_path, transparency=0.6):
    """Overlay image and mask"""
    mask = mask.convert("RGBA")
    overlay = Image.new("RGBA", image.size, (255, 255, 255, 0))
    for x in range(mask.width):
        for y in range(mask.height):
            r, g, b, _ = mask.getpixel((x, y))
            if r < 255:  
                overlay.putpixel((x, y), (r, g, b, int(255 * transparency)))
    combined = Image.alpha_composite(image.convert("RGBA"), overlay)
    combined.convert("RGB").save(output_path, 'JPEG')

def process_images(subject_name, image_path, mask_path, output_folder):
    Image.MAX_IMAGE_PIXELS = None

    mask_image = Image.open(mask_path).convert('L')

    czi_image = AICSImage(czi_path)
    czi_image.set_scene(czi_image.scenes[1])
    img_data = czi_image.get_image_data("SYX", T=0, Z=0, C=0).astype(np.uint8)
    if img_data.shape[0] == 3:
        img_data = img_data.transpose(1, 2, 0)
    img_data = img_data[:, :, [2, 1, 0]]
    wsi_image = Image.fromarray(img_data)

    image = downsample_image(wsi_image)
    mask = downsample_image(mask_image)

    tile_size = (2048, 2048)
    overlap = 0.5

    tiles = calculate_tiles(image.size, tile_size, overlap)

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    save_tiles(image, mask, tiles, tile_size, output_folder, subject_name)

# Example usage
subject_name = "DN_11_357"
czi_path = '/RW/2024/MICCAI24/holohisto/dastaset/DN/11-357.czi'
mask_path = '/RW/2024/MICCAI24/holohisto/dastaset/DN/11-357_scene2.png'
output_folder = '/RW/2024/MICCAI24/holohisto/KPIS/DN/11_357'

if not os.path.isdir(output_folder):
    os.makedirs(output_folder)

process_images(subject_name, czi_path, mask_path, output_folder)


