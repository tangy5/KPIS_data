from PIL import Image, ImageDraw, ImageFile
import numpy as np
import os

# from aicsimageio import AICSImage
import cv2 
from scipy.ndimage import center_of_mass
from openslide import OpenSlide

def downsample_image(openslide_image, level):
    """Downsample the image by selecting the appropriate level."""
    pil_image = openslide_image.read_region((0, 0), level, openslide_image.level_dimensions[level])
    return pil_image


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
        print("Saved image {}: Index:{}, Coord: {}_{}".format(subject_name, index, x, y))

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

def process_images(subject_name, image_path, mask_path, output_folder, level_load):
    Image.MAX_IMAGE_PIXELS = None

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Load the WSI TIFF image using OpenSlide
    wsi_image = OpenSlide(image_path)

    # Assuming the mask is not a WSI and can be opened with PIL
    mask_image = Image.open(mask_path).convert('L')

    # Adjust the downsample level according to your needs
    # Level 0 is the highest resolution; higher levels provide lower resolutions
    image = downsample_image(wsi_image, level_load)
    mask = mask_image.resize(wsi_image.level_dimensions[level_load], Image.ANTIALIAS)

    # The rest of the operations remain the same...
    tile_size = (2048, 2048)  # Adjust as necessary
    overlap = 0.5  # Adjust as necessary

    tiles = calculate_tiles(image.size, tile_size, overlap)

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    save_tiles(image, mask, tiles, tile_size, output_folder, subject_name)

# # Example usage
# subject_name = "11-356"
# tiff_path = '/RW/2024/MICCAI24/holohisto/dastaset/DN/11-356.tiff'  # Adjusted for TIFF
# mask_path = '/RW/2024/MICCAI24/holohisto/dastaset/DN/11-356

level_load = 0
# Example usage
subject_name = "08_474_01"
czi_path = '/RW/2024/MICCAI24/holohisto/dastaset/NEP25_02/08-474_01.tiff'
mask_path = '/RW/2024/MICCAI24/holohisto/dastaset/NEP25_02/08-474_01_mask.png'
output_folder = '/RW/2024/MICCAI24/holohisto/KPIS/NEP25_patch/08_474_01'

if not os.path.isdir(output_folder):
    os.makedirs(output_folder)

process_images(subject_name, czi_path, mask_path, output_folder, level_load)


