import os
import sys
import rasterio
from rasterio.windows import Window

# --- Check for command line argument ---
if len(sys.argv) < 2:
    print("Usage: python split_geotiff.py <your_image.tif>")
    sys.exit(1)

input_file = sys.argv[1]  # Get the file from command line
tile_width = 640
tile_height = 480
output_dir = f"tiles_{os.path.splitext(os.path.basename(input_file))[0]}"

# Create output directory
os.makedirs(output_dir, exist_ok=True)

# Open the source dataset
with rasterio.open(input_file) as src:
    img_width = src.width
    img_height = src.height
    meta = src.meta.copy()
    
    tile_count = 0

    for top in range(0, img_height, tile_height):
        if top + tile_height > img_height:
            continue
        for left in range(0, img_width, tile_width):
            if left + tile_width > img_width:
                continue

            window = Window(left, top, tile_width, tile_height)
            transform = rasterio.windows.transform(window, src.transform)

            meta.update({
                "height": tile_height,
                "width": tile_width,
                "transform": transform
            })

            tile_data = src.read(window=window)

            tile_filename = f"{os.path.splitext(os.path.basename(input_file))[0]}_tile_{top}_{left}.tif"
            output_path = os.path.join(output_dir, tile_filename)

            with rasterio.open(output_path, "w", **meta) as dst:
                dst.write(tile_data)

            tile_count += 1
            print(f"Saved {tile_filename}")

print(f"✅ Done! Total tiles saved: {tile_count}")