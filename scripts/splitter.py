import os
import argparse
import rasterio
from rasterio.windows import Window
from rasterio.transform import Affine
import numpy as np
from PIL import Image

WIDTH_DEFAULT = 1280
HEIGHT_DEFAULT = 720

def normalize_to_png(tile_data, tile_min, tile_max):
    """Normalize and convert tile data to an 8-bit grayscale image."""
    tile_data = np.clip((tile_data - tile_min) / (tile_max - tile_min) * 255, 0, 255).astype(np.uint8)
    return Image.fromarray(tile_data[0], mode='L')

def split_tif(image_path, output_dir, tile_width, tile_height, output_format):
    """Splits a GeoTIFF into smaller tiles and stores min/max values as metadata."""
    
    output_dir = os.path.abspath(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    with rasterio.open(image_path) as src:
        width, height = src.width, src.height
        print(f"Image size: {width}x{height}")
        
        global_min = np.inf
        global_max = -np.inf
        for band in range(1, src.count + 1):
            band_data = src.read(band, masked=True)
            global_min = min(global_min, band_data.min())
            global_max = max(global_max, band_data.max())
        
        print(f"Global min: {global_min}, Global max: {global_max}")

        num_tiles_x = width // tile_width
        num_tiles_y = height // tile_height
        extra_width = width % tile_width
        extra_height = height % tile_height
        transform = src.transform
        
        for i in range(num_tiles_x + (1 if extra_width else 0)):
            for j in range(num_tiles_y + (1 if extra_height else 0)):
                current_tile_width = tile_width if i < num_tiles_x else extra_width
                current_tile_height = tile_height if j < num_tiles_y else extra_height
                if current_tile_width == 0 or current_tile_height == 0:
                    continue
                
                window = Window(i * tile_width, j * tile_height, current_tile_width, current_tile_height)
                tile_data = src.read(window=window)
                tile_transform = transform * Affine.translation(i * tile_width, j * tile_height)
                tile_min = tile_data.min()
                tile_max = tile_data.max()
                
                if output_format == 'tif':
                    tile_filename = os.path.join(output_dir, f"tile_{i}_{j}.tif")
                    with rasterio.open(
                        tile_filename, 'w', 
                        driver='GTiff', 
                        count=src.count, 
                        dtype=tile_data.dtype.name, 
                        crs=src.crs, 
                        transform=tile_transform, 
                        width=current_tile_width, 
                        height=current_tile_height
                    ) as dst:
                        dst.write(tile_data)
                        dst.update_tags(tile_min=tile_min, tile_max=tile_max, global_min=global_min, global_max=global_max)
                elif output_format == 'png':
                    tile_filename = os.path.join(output_dir, f"tile_{i}_{j}.png")
                    png_image = normalize_to_png(tile_data, global_min, global_max)
                    png_image.save(tile_filename)
    
    print("✅ Splitting completed!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Split a GeoTIFF into smaller tiles with metadata.")
    parser.add_argument("image_path", help="Path to the input GeoTIFF file")
    parser.add_argument("output_dir", help="Directory to save the output tiles")
    parser.add_argument("-width", type=int, default=WIDTH_DEFAULT, help=f"Tile width in pixels (default: {WIDTH_DEFAULT})")
    parser.add_argument("-height", type=int, default=HEIGHT_DEFAULT, help=f"Tile height in pixels (default: {HEIGHT_DEFAULT})")
    parser.add_argument("-format", choices=['tif', 'png'], default='tif', help="Output format: 'tif' or 'png' (default: 'tif')")
    args = parser.parse_args()
    
    split_tif(args.image_path, args.output_dir, args.width, args.height, args.format)