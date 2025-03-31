import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from argparse import ArgumentParser
import random


def generate_distinct_colors(n):
    """Generates n distinct strong colors."""
    np.random.seed(42)  # Ensure consistent colors across runs
    colors = [tuple(np.random.randint(0, 256, 3).tolist()) for _ in range(n)]
    return colors

def load_classes(csv_path):
    """Loads class ID to strong color mapping from a CSV file, ensuring unique colors."""
    df = pd.read_csv(csv_path)
    class_ids = df['Pixel Value'].tolist()
    colors = generate_distinct_colors(len(class_ids))
    class_colors = {class_id: color for class_id, color in zip(class_ids, colors)}
    return class_colors

def count_classes(mask_path, class_colors):
    """Counts the occurrences of each class in the mask and ensures all classes are printed."""
    mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
    unique, counts = np.unique(mask, return_counts=True)
    class_counts = {class_id: 0 for class_id in class_colors.keys()}  # Initialize all to zero
    class_counts.update(dict(zip(unique, counts)))
    
    print("Unique values found in mask:", unique)
    print("Class frequencies in the mask:")
    for class_id in sorted(class_counts.keys()):
        color = class_colors.get(class_id, (255, 255, 255))  # Default to white if missing
        count = class_counts[class_id]
        print(f"Class {class_id}: {count} pixels, Color: {color}")
    return class_counts

def apply_mask(image_path, mask_path, class_colors, output_path, selected_class):
    """Applies color mask to the image based on a selected class ID."""
    image = cv2.imread(image_path)
    mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
    
    color_mask = np.zeros_like(image)
    
    if selected_class in class_colors:
        color_mask[mask == selected_class] = class_colors[selected_class]
    
    blended = cv2.addWeighted(image, 0.7, color_mask, 0.3, 0)
    cv2.imwrite(output_path, blended)
    print(f"Saved colorized image to {output_path}")
    
    show_color_map(class_colors)

def show_color_map(class_colors):
    """Displays a color legend using matplotlib."""
    fig, ax = plt.subplots(figsize=(5, len(class_colors) * 0.5))
    ax.set_title("Class Color Mapping")
    
    y_positions = range(len(class_colors))
    colors = [tuple(c/255 for c in color) for color in class_colors.values()]
    labels = [f"Class {class_id}" for class_id in class_colors.keys()]
    
    for y, color, label in zip(y_positions, colors, labels):
        ax.add_patch(plt.Rectangle((0, y), 1, 1, color=color))
        ax.text(1.2, y + 0.5, label, va='center', fontsize=12)
    
    ax.set_xlim(0, 2)
    ax.set_ylim(0, len(class_colors))
    ax.set_xticks([])
    ax.set_yticks([])
    plt.show()

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--image", required=True, help="Path to the input image")
    parser.add_argument("--mask", required=True, help="Path to the segmentation mask")
    parser.add_argument("--classes", required=True, help="Path to the _classes.csv file")
    parser.add_argument("--output", required=True, help="Path to save the output image")
    parser.add_argument("--class_id", type=int, required=True, help="Class ID to highlight")
    
    args = parser.parse_args()
    class_colors = load_classes(args.classes)
    count_classes(args.mask, class_colors)
    apply_mask(args.image, args.mask, class_colors, args.output, args.class_id)
