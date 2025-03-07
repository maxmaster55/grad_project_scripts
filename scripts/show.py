import argparse
import os
import rasterio
import numpy as np
import rasterio.plot as plt


def normalize(array):
    return (array - array.min()) / (array.max() - array.min())


def show_tif(image_path, red_band, green_band, blue_band):
    """Loads and displays a GeoTIFF image using Rasterio and Matplotlib."""
    if not os.path.exists(image_path):
        print(f"Error: File '{image_path}' not found.")
        return

    with rasterio.open(image_path) as src:
        # Plot image
        red = src.read(red_band)
        green = src.read(green_band)
        blue = src.read(blue_band)
        
        red_norm = normalize(red)
        green_norm = normalize(green)
        blue_norm = normalize(blue)

        rgb = np.stack((red_norm, green_norm, blue_norm))
 
        plt.show(rgb)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Display a GeoTIFF image.")
    parser.add_argument("image_path", help="Path to the GeoTIFF file")

    parser.add_argument("-r", type=int, default=4, help="Band number for Red channel")
    parser.add_argument("-g",type=int, default=3, help="Band number for Green channel")
    parser.add_argument("-b", type=int, default=2, help="Band number for Blue channel")

    args = parser.parse_args()

    show_tif(args.image_path, args.r, args.g, args.b)
