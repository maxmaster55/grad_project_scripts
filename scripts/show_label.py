import numpy as np
import rasterio
import cv2
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import argparse
import os

# Class values
BACKGROUND = 0
VEGETATION = 1
WATER = 2
URBAN = 3

# Color map: black=background, green=vegetation, blue=water, red=urban
cmap = ListedColormap(["black", "green", "blue", "red"])
class_labels = ["Background", "Vegetation", "Water", "Urban"]

def visualize_mask(mask):
    plt.imshow(mask, cmap=cmap)
    plt.colorbar(ticks=[0, 1, 2, 3], format=plt.FuncFormatter(lambda x, _: class_labels[int(x)]))
    plt.title("Multiclass Mask Visualization")
    plt.axis("off")
    plt.show()

def load_mask(path):
    if path.endswith('.tif'):
        with rasterio.open(path) as src:
            return src.read(1)  # First band
    elif path.endswith('.png'):
        return cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    else:
        raise ValueError("Unsupported file format. Use .tif or .png.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Visualize a multiclass mask.")
    parser.add_argument("mask_path", type=str, help="Path to the mask file (.tif or .png)")
    args = parser.parse_args()

    if not os.path.exists(args.mask_path):
        print("❌ Mask file not found.")
        exit()

    mask = load_mask(args.mask_path)
    visualize_mask(mask)
