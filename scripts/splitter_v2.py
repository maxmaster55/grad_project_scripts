#!/bin/python3
import os
import argparse
import rasterio
from rasterio.windows import Window
from rasterio.transform import Affine

WIDTH_DEFAULT = 1280
HEIGHT_DEFAULT = 720



def split_tif(image_path, output_dir, tile_width, tile_height):
    """Splits a GeoTIFF into smaller tiles of user-defined width and height."""
    
    # Ensure output directory exists
    output_dir = os.path.abspath(output_dir)  # Convert to absolute path
    os.makedirs(output_dir, exist_ok=True)

    # Open the TIFF file
    with rasterio.open(image_path) as src:
        width, height = src.width, src.height  # Get image dimensions
        print(f"Image size: {width}x{height}")
        
        # Calculate the number of full tiles we can fit
        num_tiles_x = width // tile_width
        num_tiles_y = height // tile_height

        # Handle the remaining part of the image
        extra_width = width % tile_width
        extra_height = height % tile_height

        # Get the original affine transform
        transform = src.transform
        
        # Iterate over the image and extract tiles
        for i in range(num_tiles_x + (1 if extra_width else 0)):
            for j in range(num_tiles_y + (1 if extra_height else 0)):
                # Compute tile width and height dynamically for the last column/row
                current_tile_width = tile_width if i < num_tiles_x else extra_width
                current_tile_height = tile_height if j < num_tiles_y else extra_height

                if current_tile_width == 0 or current_tile_height == 0:
                    continue  # Skip empty tiles
                
                # Define the window (tile) to read
                window = Window(i * tile_width, j * tile_height, current_tile_width, current_tile_height)
                
                # Read the data from the window
                tile_data = src.read(window=window)
                
                # Calculate the new transform for the tile
                tile_transform = transform * Affine.translation(i * tile_width, j * tile_height)
                
                # Define the output file path for each tile
                tile_filename = os.path.join(output_dir, f"tile_{i}_{j}.tif")
                
                # Write the tile to a new GeoTIFF file
                with rasterio.open(
                    tile_filename, 'w', 
                    driver='GTiff', 
                    count=src.count, 
                    dtype=tile_data.dtype.name,  # Convert dtype properly
                    crs=src.crs, 
                    transform=tile_transform,  # Apply the correct transform
                    width=current_tile_width, 
                    height=current_tile_height
                ) as dst:
                    dst.write(tile_data)

    print("✅ Splitting completed!")

if __name__ == "__main__":
    # Command-line argument parsing
    parser = argparse.ArgumentParser(description="Split a GeoTIFF into smaller tiles.")
    parser.add_argument("image_path", help="Path to the input GeoTIFF file")
    parser.add_argument("output_dir", help="Directory to save the output tiles")
    parser.add_argument("-width", type=int, default=WIDTH_DEFAULT, help=f"Tile width in pixels (default: {WIDTH_DEFAULT})")
    parser.add_argument("-height", type=int, default=HEIGHT_DEFAULT, help=f"Tile height in pixels (default: {HEIGHT_DEFAULT})")
    args = parser.parse_args()

    # Run the function
    split_tif(args.image_path, args.output_dir, args.width, args.height)
