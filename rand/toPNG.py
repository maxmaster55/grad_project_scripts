import os
import rasterio
import numpy as np
from PIL import Image

# Use current directory
input_dir = os.getcwd()
output_dir = os.path.join(input_dir, "output_png")
os.makedirs(output_dir, exist_ok=True)

for filename in os.listdir(input_dir):
    if filename.endswith(".tif") or filename.endswith(".tiff"):
        image_path = os.path.join(input_dir, filename)

        with rasterio.open(image_path) as dataset:
            if dataset.count >= 3:  # Ensure at least 3 bands
                r, g, b = dataset.read(1), dataset.read(2), dataset.read(3)
                
                # Normalize bands
                r = np.clip(r, 0, 255).astype(np.uint8)
                g = np.clip(g, 0, 255).astype(np.uint8)
                b = np.clip(b, 0, 255).astype(np.uint8)

                img = np.stack([r, g, b], axis=-1)

                # Save PNG
                img_name = os.path.splitext(filename)[0] + ".png"
                Image.fromarray(img).save(os.path.join(output_dir, img_name))

                print(f"✅ Converted {filename} to RGB PNG")

print("🎯 Conversion complete! ✅")
