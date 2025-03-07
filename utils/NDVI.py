import os
import rasterio
import numpy as np
from PIL import Image

## to get farms like ndvi



# Input and output directories
input_dir = os.getcwd()
output_dir = os.path.join(input_dir, "NDVI_output")
os.makedirs(output_dir, exist_ok=True)

def compute_evi(image_path):
    with rasterio.open(image_path) as dataset:
        img_name = os.path.splitext(os.path.basename(image_path))[0]

        # Read NIR (Band 5), Red (Band 4), and Blue (Band 2)
        nir = dataset.read(5).astype(np.float32)
        red = dataset.read(4).astype(np.float32)

        # Compute EVI
        ndvi =((nir - red) / (nir + red))

        # Normalize to 0-255
        ndvi = ((ndvi + 1) / 2 * 255).astype(np.uint8)

        # Save as PNG
        img = Image.fromarray(ndvi, mode="L")
        img.save(os.path.join(output_dir, f"{img_name}_NDVI.png"))
        print(f"✅ Saved: {img_name}_NDVI.png")

# Process all TIFF images
for filename in os.listdir(input_dir):
    if filename.endswith(".tif"):
        compute_evi(os.path.join(input_dir, filename))
