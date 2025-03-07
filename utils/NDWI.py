import os
import rasterio
import numpy as np
from PIL import Image

## to get water surfaces



# Input and output directories
input_dir = os.getcwd()
output_dir = os.path.join(input_dir, "NDWI_output")
os.makedirs(output_dir, exist_ok=True)

def compute_ndwi(image_path):
    with rasterio.open(image_path) as dataset:
        img_name = os.path.splitext(os.path.basename(image_path))[0]

        # Read Green (Band 3) and NIR (Band 5)
        green = dataset.read(3).astype(np.float32)
        nir = dataset.read(5).astype(np.float32)

        # Compute NDWI
        ndwi = (green - nir) / (green + nir + 1e-10)

        # Normalize to 0-255
        ndwi = ((ndwi + 1) / 2 * 255).astype(np.uint8)

        # Save as PNG
        img = Image.fromarray(ndwi, mode="L")
        img.save(os.path.join(output_dir, f"{img_name}_NDWI.png"))
        print(f"✅ Saved: {img_name}_NDWI.png")

# Process all TIFF images
for filename in os.listdir(input_dir):
    if filename.endswith(".tif"):
        compute_ndwi(os.path.join(input_dir, filename))
