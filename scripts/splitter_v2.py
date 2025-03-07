#!/bin/python3
import os
import argparse
import rasterio
from rasterio.windows import Window

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
        width_used = tile_width * num_tiles_x
        height_used = tile_height * num_tiles_y

        # Get the original affine transform
        transform = src.transform
        
        # Iterate over the image and extract tiles
        for i in range(num_tiles_x):
            for j in range(num_tiles_y):
                # Define the window (tile) to read
                window = Window(i * tile_width, j * tile_height, tile_width, tile_height)
                
                # Read the data from the window
                tile_data = src.read(window=window)
                
                # Calculate the new transform for the tile
                tile_transform = transform * transform.translation(i * tile_width, j * tile_height)
                
                # Define the output file path for each tile
                tile_filename = os.path.join(output_dir, f"tile_{i}_{j}.tif")
                
                # Write the tile to a new GeoTIFF file
                with rasterio.open(
                    tile_filename, 'w', 
                    driver='GTiff', 
                    count=src.count, 
                    dtype=tile_data.dtype, 
                    crs=src.crs, 
                    transform=tile_transform,  # Apply the correct transform
                    width=tile_width, 
                    height=tile_height
                ) as dst:
                    dst.write(tile_data)

        # If there are any remaining rows or columns, handle them separately (optional)
        if width_used < width or height_used < height:
            print("Handling remaining rows or columns.")

if __name__ == "__main__":
    # Command-line argument parsing
    parser = argparse.ArgumentParser(description="Split a GeoTIFF into smaller tiles.")
    parser.add_argument("image_path", help="Path to the input GeoTIFF file")
    parser.add_argument("output_dir", help="Directory to save the output tiles")
    parser.add_argument("-width", type=int, default=256, help="Tile width in pixels (default: 256)")
    parser.add_argument("-hight", type=int, default=256, help="Tile height in pixels (default: 256)")
    args = parser.parse_args()

    # Run the function
    split_tif(args.image_path, args.output_dir, args.width, args.hight)
