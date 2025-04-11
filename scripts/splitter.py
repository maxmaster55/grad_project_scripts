import os
import argparse
import rasterio
from rasterio.windows import Window
from rasterio.transform import Affine
import numpy as np
from PIL import Image
from tqdm import tqdm

WIDTH_DEFAULT = 1280
HEIGHT_DEFAULT = 720
LANDSAT_RGB_BANDS = [1, 2, 3, 4, 5, 6, 7]

def compute_global_percentiles(image_path):
    """Compute global 2%-98% percentile range for normalization across all tiles."""
    with rasterio.open(image_path) as src:
        all_band_mins, all_band_maxs = [], []
        for band in LANDSAT_RGB_BANDS:
            band_data = src.read(band).flatten()
            band_min, band_max = np.percentile(band_data[band_data > 0], (2, 98))  # Ignore zero values
            all_band_mins.append(band_min)
            all_band_maxs.append(band_max)
    return np.array(all_band_mins), np.array(all_band_maxs)

def normalize_to_png(tile_data, global_min, global_max):
    """Normalize tile using global min/max values computed from the whole raster."""
    normalized_bands = []
    for band, band_min, band_max in zip(tile_data, global_min, global_max):
        if band_max > band_min:
            band = np.clip((band - band_min) / (band_max - band_min) * 255, 0, 255).astype(np.uint8)
        else:
            band = np.full_like(band, 128, dtype=np.uint8)  # Assign neutral gray if no variation
        normalized_bands.append(band)
    
    tile_data = np.stack(normalized_bands, axis=-1)  # Convert from (bands, height, width) to (height, width, bands)
    return Image.fromarray(tile_data, mode='RGB')

def split_tif(image_path, output_dir, tile_width, tile_height, output_format):
    """Splits a GeoTIFF into smaller tiles and applies cumulative count cut normalization for PNG output."""
    
    output_dir = os.path.abspath(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    global_min, global_max = compute_global_percentiles(image_path)
    print(f"Global min: {global_min}, Global max: {global_max}")
    
    with rasterio.open(image_path) as src:
        width, height = src.width, src.height
        print(f"Image size: {width}x{height}")
        
        num_tiles_x = width // tile_width
        num_tiles_y = height // tile_height
        extra_width = width % tile_width
        extra_height = height % tile_height
        transform = src.transform
        
        total_tiles = (num_tiles_x + (1 if extra_width else 0)) * (num_tiles_y + (1 if extra_height else 0))
        progress_bar = tqdm(total=total_tiles, desc="Processing tiles", unit="tile")
        
        for i in range(num_tiles_x + (1 if extra_width else 0)):
            for j in range(num_tiles_y + (1 if extra_height else 0)):
                current_tile_width = tile_width if i < num_tiles_x else extra_width
                current_tile_height = tile_height if j < num_tiles_y else extra_height
                if current_tile_width == 0 or current_tile_height == 0:
                    continue
                
                window = Window(i * tile_width, j * tile_height, current_tile_width, current_tile_height)
                tile_data = src.read(LANDSAT_RGB_BANDS, window=window)
                tile_transform = transform * Affine.translation(i * tile_width, j * tile_height)
                
                if output_format == 'tif':
                    tile_filename = os.path.join(output_dir, f"tile_{i}_{j}.tif")
                    with rasterio.open(
                        tile_filename, 'w', 
                        driver='GTiff', 
                        count=len(LANDSAT_RGB_BANDS), 
                        dtype=tile_data.dtype.name, 
                        crs=src.crs, 
                        transform=tile_transform, 
                        width=current_tile_width, 
                        height=current_tile_height
                    ) as dst:
                        dst.write(tile_data)
                elif output_format == 'png':
                    tile_filename = os.path.join(output_dir, f"tile_{i}_{j}.png")
                    png_image = normalize_to_png(tile_data, global_min, global_max)
                    png_image.save(tile_filename)
                
                progress_bar.update(1)
        
        progress_bar.close()
    
    print("✅ Splitting completed!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Split a GeoTIFF into smaller tiles with cumulative count cut normalization.")
    parser.add_argument("image_path", help="Path to the input GeoTIFF file")
    parser.add_argument("output_dir", help="Directory to save the output tiles")
    parser.add_argument("-width", type=int, default=WIDTH_DEFAULT, help=f"Tile width in pixels (default: {WIDTH_DEFAULT})")
    parser.add_argument("-height", type=int, default=HEIGHT_DEFAULT, help=f"Tile height in pixels (default: {HEIGHT_DEFAULT})")
    parser.add_argument("-format", choices=['tif', 'png'], default='tif', help="Output format: 'tif' or 'png' (default: 'tif')")
    args = parser.parse_args()
    
    split_tif(args.image_path, args.output_dir, args.width, args.height, args.format)
