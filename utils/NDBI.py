import os
import rasterio
import numpy as np
from PIL import Image

## to get urben areas



# Input and output directories
input_dir = os.getcwd()  # Folder containing .tif images
output_dir = os.path.join(input_dir, "NDBI_output")
os.makedirs(output_dir, exist_ok=True)

def compute_ndbi(image_path):
    with rasterio.open(image_path) as dataset:
        img_name = os.path.splitext(os.path.basename(image_path))[0]
        
        # Read SWIR (Band 6) and NIR (Band 5)
        swir = dataset.read(6).astype(np.float32)
        nir = dataset.read(5).astype(np.float32)

        # Compute NDBI
        ndbi = (swir - nir) / (swir + nir)  # Avoid division by zero

        # Normalize to 0-255 for PNG saving
        ndbi = ((ndbi + 1) / 2 * 255).astype(np.uint8)

        # Save as PNG
        img = Image.fromarray(ndbi, mode="L")
        img.save(os.path.join(output_dir, f"{img_name}_NDBI.png"))
        print(f"✅ Saved: {img_name}_NDBI.png")

# Process all TIFF images
for filename in os.listdir(input_dir):
    if filename.endswith(".tif"):
        compute_ndbi(os.path.join(input_dir, filename))
