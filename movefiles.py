from PIL import Image
import os
import shutil

def contains_foreground(mask_path):
    mask = Image.open(mask_path).convert("L")
    return any(pixel > 0 for pixel in mask.getdata())

def copy_files(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for file in os.listdir(input_folder):
        if file.endswith("_mask.jpg"):
            mask_path = os.path.join(input_folder, file)
            if contains_foreground(mask_path):
                base_name = file.replace("_mask.jpg", "")
                image_name = f"{base_name}_img.jpg"
                overlay_name = f"{base_name}_overlay.jpg"

                image_path = os.path.join(input_folder, image_name)
                overlay_path = os.path.join(input_folder, overlay_name)

                if os.path.exists(image_path):
                    shutil.copy(image_path, os.path.join(output_folder, image_name))
                if os.path.exists(overlay_path):
                    shutil.copy(overlay_path, os.path.join(output_folder, overlay_name))
                shutil.copy(mask_path, os.path.join(output_folder, file))

                print(f"Copied: {image_name}, {file}, and {overlay_name}")

# Example usage
input_folder = "/RW/2024/MICCAI24/holohisto/KPIS/DN/11_357"  
output_folder = "/RW/2024/MICCAI24/holohisto/KPIS/DN/out/11_357" 

copy_files(input_folder, output_folder)
