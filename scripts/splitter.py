#! /bin/python3
import os
import argparse
import rasterio
from rasterio.windows import Window

def split_tif(image_path, output_dir, tile_size):
    """Splits a GeoTIFF into smaller tiles and saves them in output_dir."""
    
    # Ensure output directory exists
    output_dir = os.path.abspath(output_dir)  # Convert to absolute path
    os.makedirs(output_dir, exist_ok=True)

    # Open the TIFF file
    with rasterio.open(image_path) as src:
        width, height = src.width, src.height  # Get image dimensions
        num_tiles_x = width // tile_size
        num_tiles_y = height // tile_size

        for i in range(num_tiles_x):
            for j in range(num_tiles_y):
                # Define window (sub-region)
                window = Window(i * tile_size, j * tile_size, tile_size, tile_size)
                tile = src.read(window=window)

                # Define output profile
                profile = src.profile
                profile.update(
                    width=tile_size,
                    height=tile_size,
                    transform=rasterio.windows.transform(window, src.transform)
                )

                # Save each tile in the specified directory
                output_name = os.path.join(output_dir, f"tile_{i}_{j}.tif")
                with rasterio.open(output_name, "w", **profile) as dst:
                    dst.write(tile)

                print(f"Saved {output_name}")

if __name__ == "__main__":
    # Command-line argument parsing
    parser = argparse.ArgumentParser(description="Split a GeoTIFF into smaller tiles.")
    parser.add_argument("image_path", help="Path to the input GeoTIFF file")
    parser.add_argument("output_dir", help="Directory to save the output tiles")
    parser.add_argument("--tile_size", type=int, default=256, help="Tile size in pixels (default: 256x256)")
    args = parser.parse_args()

    # Run the function
    split_tif(args.image_path, args.output_dir, args.tile_size)
