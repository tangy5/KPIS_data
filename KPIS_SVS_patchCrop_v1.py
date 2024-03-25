# pip install openslide-python Pillow
# pip install pyvips


import openslide
from PIL import Image, ImageOps, ImageDraw
import numpy as np
import pyvips
Image.MAX_IMAGE_PIXELS = None  # Disables the limit entirely


def convert_distance_to_image_points(image_dim, distance_dim, distance_points):
    """
    Convert points from distance dimensions to image dimensions, with results rounded to the nearest integer.
    
    Args:
    - image_dim: The dimensions of the image [width, height].
    - distance_dim: The real-world dimensions corresponding to the image dimensions [width, height].
    - distance_points: A list of points in the format [x1, y1, x2, y2, x3, y3, x4, y4] in the distance space.
    
    Returns:
    - A list of converted points in the image dimension space, rounded to nearest integers.
    """
    # Calculate scaling factors for x and y dimensions
    scale_x = image_dim[0] / distance_dim[0]
    scale_y = image_dim[1] / distance_dim[1]
    
    # Apply the scaling to each point and round to nearest integer
    image_points = [0] * len(distance_points)
    for i in range(0, len(distance_points), 2):  # Step through x,y pairs
        image_points[i] = round(distance_points[i] * scale_x)
        image_points[i+1] = round(distance_points[i+1] * scale_y)
    
    return image_points

# Function to check if the dimensions match and print their sizes
def check_and_print_sizes(image, mask):
    image_size = image.dimensions
    mask_size = mask.size
    print(f"WSI size: {image_size}, Mask size: {mask_size}")
    return image_size == mask_size


# Function to crop and possibly pad the images
def crop_and_pad(image, mask, coordinates):
    # Convert coordinates to a PIL-friendly bounding box (left, upper, right, lower)
    left = min(coordinates[::2])
    upper = min(coordinates[1::2])
    right = max(coordinates[::2])
    lower = max(coordinates[1::2])
    bbox = (left, upper, right, lower)
    
    # Crop the images
    image_cropped = image.read_region((left, upper), 0, (right-left, lower-upper))
    mask_cropped = mask.crop(bbox)
    
    # Convert the cropped WSI region to a PIL image for uniformity
    image_cropped = Image.fromarray(np.array(image_cropped)[:, :, :3])  # Discard the alpha channel if present
    
    # Assuming the coordinates could potentially not form a perfect rectangle, and hence padding could be required
    # However, by definition, the bbox used will always form a rectangle for cropping. Padding logic is provided
    # for educational purposes or specific edge cases outside typical rectangle cropping.
    
    # Determine the required padding (if any)
    target_width = right - left
    target_height = lower - upper
    pad_width = target_width - image_cropped.width
    pad_height = target_height - image_cropped.height
    
    # Pad the images if necessary (left, top, right, bottom)
    if pad_width > 0 or pad_height > 0:
        padding = (0, 0, max(pad_width, 0), max(pad_height, 0))
        image_cropped = ImageOps.expand(image_cropped, padding)
        mask_cropped = ImageOps.expand(mask_cropped, padding)
    
    return image_cropped, mask_cropped


def save_with_pyramid(image_pil, filename):
    """
    Save a PIL image as a pyramidal TIFF using pyvips.
    """
    # Convert the PIL image to a format pyvips can use
    memory_file = image_pil.tobytes()
    np_img = np.array(image_pil)
    vips_image = pyvips.Image.new_from_memory(np_img.data, np_img.shape[1], np_img.shape[0], np_img.shape[2], 'uchar')
    
    # Save the image as a pyramidal TIFF
    vips_image.tiffsave(filename, tile=True, pyramid=True, compression='jpeg', tile_width=1024, tile_height=1024, bigtiff=True)

    
def create_overlay_and_save_thumbnail(wsi_image_pil, mask_image_pil, output_filename, thumbnail_size=(512, 512)):
    """
    Create an overlay of the WSI and mask, then save a thumbnail of the overlay.
    
    Args:
    - wsi_image_pil: The cropped WSI image as a PIL image.
    - mask_image_pil: The corresponding cropped mask as a PIL image.
    - output_filename: The filename for the saved thumbnail image.
    - thumbnail_size: The size of the thumbnail to be saved (default is 512x512).
    """
    # Ensure the mask is in RGBA to use the alpha channel for blending
    if mask_image_pil.mode != 'RGBA':
        mask_image_pil = mask_image_pil.convert('RGBA')
    
    # Overlay the mask on the WSI using the alpha channel for transparency
    overlay_image = Image.alpha_composite(wsi_image_pil.convert('RGBA'), mask_image_pil)
    
    # Resize for the thumbnail
    thumbnail = overlay_image.resize(thumbnail_size, Image.ANTIALIAS)
    
    # Save the thumbnail
    thumbnail.save(output_filename)

    
    
#--------------------------------------------------------------------------------------------------------------------
# Path to your WSI and mask files
wsi_path = '08-474-2023-10-20_13_21_25.svs'
subject_name = '08-474'
part = '_03'
mask_path = subject_name + '.png'

# image_dim = [180094, 67609] # 08-368
# distance_dim = [43132.87, 16192.49]

# image_dim = [176119, 52282] # 08-373
# distance_dim = [42180.85, 12521.64]

image_dim = [200135, 59478] # 08-471
distance_dim = [47932.73, 14245.10]

# image_dim = [174097, 63511] # 08-472
# distance_dim = [41696.58, 15211.01]

# distance_points = [19918.08, 754.33, 19918.08, 5024.16, 25459.77, 754.33, 25459.77, 5024.16] # 08-368 01
# distance_points = [20003.92, 5318.49, 20003.92, 10160.86, 25055.91, 5318.49, 25055.91, 10160.86] # 08-368 02
# distance_points = [18368.83, 10957.43, 18368.83, 16114.24, 23316.01, 10957.43, 23316.01, 16114.24] # 08-368 03

# distance_points = [20720.25, 877.72, 20720.25, 5214.90, 24699.44, 877.72, 24699.44, 5214.90] # 08-373 01
# distance_points = [16656.97, 4717.68, 16656.97, 8574.05, 20735.29, 4717.68, 20735.29, 8574.05] # 08-373 02
# distance_points = [16164.30, 8914.71, 16164.30, 12308.69, 20020.67, 8914.71, 20020.67, 12308.69] # 08-373 03



# distance_points = [20559.50, 927.63, 20731.93, 4964.32, 25225.03, 1079.76, 25042.47, 5735.15] # 08-471 01
# distance_points = [19356.58, 5081.62, 19356.58, 9838.12, 24355.27, 5081.62, 24355.27, 9838.12] # 08-471 01
# distance_points = [17440.63, 9027.71, 17440.63, 13134.00, 22579.0, 9027.71, 22579.9, 13134.00] # 08-471 01

# distance_points = [18014.93, 818.61, 18014.93, 5457.42, 23154.52, 818.61, 23154.52, 5457.42] # 08-472 01
# distance_points = [17197.86, 5984.56, 17197.86, 10825.34, 22523.52, 5984.56, 22523.52, 10825.34] # 08-472 02
# distance_points = [17060.17, 10778.83, 17060.17, 14891.62, 21859.76, 10778.83, 21859.76, 14891.62] # 08-472 03

# distance_points = [24104.17, 1798.47, 24104.17, 6252.80, 29475.86, 1798.47, 29475.86, 6252.80] # 08-472 01
# distance_points = [21347.36, 5529.10, 21347.36, 10253.14, 27281.15, 5529.10, 27281.15, 10253.14] # 08-472 02
distance_points = [18646.04, 9646.10, 18646.04, 13622.20, 23305.05, 9646.10, 23305.05, 13622.20] # 08-472 03

#--------------------------------------------------------------------------------------------------------------------

# Convert points
coordinates = convert_distance_to_image_points(image_dim, distance_dim, distance_points)
print("Converted points in image dimension space:", coordinates)


# Load the WSI at the largest resolution
wsi = openslide.OpenSlide(wsi_path)
# Read the corresponding mask
mask = Image.open(mask_path)


# Ensure they are the same size
if not check_and_print_sizes(wsi, mask):
    raise ValueError("WSI and mask sizes do not match!")


# Crop and pad (if necessary)
cropped_wsi, cropped_mask = crop_and_pad(wsi, mask, coordinates)
# save mask
out_maskname = subject_name + part + '_mask.png'
cropped_mask.save('./' + out_maskname)

# Convert the cropped WSI to a PIL image (this step might already be done depending on your cropping logic)
cropped_wsi_pil = Image.fromarray(np.array(cropped_wsi)[:, :, :3])  # Assuming RGB
# Save the cropped WSI as a pyramidal TIFF
out_imgname = subject_name + part + '.tiff'
save_with_pyramid(cropped_wsi_pil, out_imgname)

mask_colored = cropped_mask.convert("L").point(lambda x: 255 if x > 0 else 0)  # Convert mask to binary
mask_rgba = Image.merge('RGBA', [mask_colored, Image.new('L', mask_colored.size, 0), Image.new('L', mask_colored.size, 0), mask_colored])

# Now, create the overlay and save the thumbnail
out_thumbnailname = subject_name + part + '_thumbnail.png'
create_overlay_and_save_thumbnail(cropped_wsi, mask_rgba, out_thumbnailname)