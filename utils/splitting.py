import os
import rasterio
from rasterio.windows import Window

# Define parameters
input_dir = os.getcwd()  # Set current directory as input directory
output_dir = os.path.join(input_dir, "output_tiles")  # Create output directory
tile_size = 512  # Change this to adjust tile size

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# Function to split image
def split_image(image_path):
    with rasterio.open(image_path) as dataset:
        img_name = os.path.splitext(os.path.basename(image_path))[0]
        img_output_folder = os.path.join(output_dir, img_name)
        os.makedirs(img_output_folder, exist_ok=True)

        img_width, img_height = dataset.width, dataset.height
        x_tiles = img_width // tile_size
        y_tiles = img_height // tile_size

        for i in range(x_tiles):
            for j in range(y_tiles):
                x_off, y_off = i * tile_size, j * tile_size
                window = Window(x_off, y_off, tile_size, tile_size)
                tile_data = dataset.read(window=window)

                # Save tile
                tile_filename = f"{img_name}_tile_{i}_{j}.tif"
                tile_path = os.path.join(img_output_folder, tile_filename)

                with rasterio.open(
                    tile_path, "w",
                    driver="GTiff",
                    height=tile_size,
                    width=tile_size,
                    count=dataset.count,
                    dtype=dataset.dtypes[0],
                    crs=dataset.crs,
                    transform=dataset.window_transform(window)
                ) as dest:
                    dest.write(tile_data)

                print(f"✅ Saved: {tile_path}")

# Process all GeoTIFF images
for filename in os.listdir(input_dir):
    if filename.endswith(".tif") or filename.endswith(".tiff"):
        image_path = os.path.join(input_dir, filename)
        print(f"📌 Processing: {filename}")
        split_image(image_path)
