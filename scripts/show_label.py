import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from PIL import Image
import argparse

# Class constants
BACKGROUND = 0
VEGETATION = 1
WATER = 2
URBAN = 3

def visualize_multiclass_mask(mask, output_file="label_visualization.png"):
    cmap = ListedColormap(["black", "green", "blue", "red"])
    
    plt.imshow(mask, cmap=cmap)
    plt.title("Multiclass Mask")
    plt.colorbar(ticks=[0, 1, 2, 3], format=plt.FuncFormatter(
        lambda x, _: ["Background", "Vegetation", "Water", "Urban"][int(x)]))

    plt.savefig(output_file)
    print(f"✅ Saved visualization to {output_file}")


def load_png_mask(image_path):
    # Load the image in grayscale mode (as labels)
    image = Image.open(image_path).convert("L")
    mask = np.array(image)
    return mask

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Display a PNG label mask with class colors.")
    parser.add_argument("-i", "--input", required=True, help="Path to the PNG image.")
    parser.add_argument("-o", "--output", default="label_visualization.png", help="Output PNG file for visualization.")
    args = parser.parse_args()

    mask = load_png_mask(args.input)
    visualize_multiclass_mask(mask, args.output)
