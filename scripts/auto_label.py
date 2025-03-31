import rasterio
import numpy as np
import cv2
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import argparse
import csv
import os

# Constants for the classes
VEGETATION = 1
WATER = 2
URBAN = 3

# thresholds for the classes
NDVI_THRESHOLD = 0.6
NDWI_THRESHOLD = 0.85
NDBI_THRESHOLD = 0.8


# Calculate NDVI
def calculate_ndvi(image):
    nir = image[4]
    red = image[3]
    ndvi = (nir - red) / (nir + red)  # NDVI formula
    return ndvi

# Calculate NDWI
def calculate_ndwi(image):
    green = image[2]  # Band 3 (Green) → Index 2
    swir = image[5]   # Band 6 (SWIR1) → Index 5
    ndwi = (green - swir) / (green + swir)  # NDWI formula
    return ndwi


# Calculate NDBI
def calculate_ndbi(image):
    swir = image[5]  # SWIR1 (Band 6, index 5)
    nir = image[4]   # NIR (Band 5, index 4)
    # Avoid division by zero by adding a small constant (epsilon)
    epsilon = 1e-6  
    ndbi = (swir - nir) / (swir + nir + epsilon)
    return ndbi


def save_image_tif(image, filename, src=None):
    # Ensure the image has shape (1, height, width)
    image = np.expand_dims(image, axis=0)  # Add band dimension

    with rasterio.open(
        filename, "w",
        driver="GTiff",
        height=image.shape[1],  # Height
        width=image.shape[2],  # Width
        count=1,  # Single band
        dtype=image.dtype,
        crs=src.crs,
        transform=src.transform
    ) as dst:
        dst.write(image)  # Write as (bands, height, width)

    print(f"✅ Saved as tif: {filename}")

# show example of the images
def show_thresholded_images(ndvi_thresholded, ndwi_thresholded, ndbi_thresholded):
    plt.subplot(1, 3, 1)
    plt.imshow(ndvi_thresholded, cmap="viridis")
    plt.title("NDVI Thresholded")
    plt.colorbar()
    plt.subplot(1, 3, 2)
    plt.imshow(ndwi_thresholded, cmap="viridis")
    plt.title("NDWI Thresholded")
    plt.colorbar()
    plt.subplot(1, 3, 3)
    plt.imshow(ndbi_thresholded, cmap="viridis")
    plt.title("NDBI Thresholded")
    plt.colorbar()
    plt.show()

def save_image_png(image, filename):
    # Normalize to 0-255
    image = ((image + 1) / 2 * 255).astype(np.uint8)
    # Save as PNG
    cv2.imwrite(filename, image)
    print(f"✅ Saved as png: {filename}")


# Thresholding (only show max 90% of the pixels)
def threshold_image(image, threshold=0.8):
    threshold_value = np.percentile(image, threshold * 100)
    min_value = image.min()  
    thresholded_image = np.where(image >= threshold_value, image, min_value)  
    
    return thresholded_image


# normalize the images and calculate the percentage of the pixal
def percentage_calculate(image):
    image = (image - image.min()) / (image.max() - image.min())
    return image

# Visualize the multiclass mask with a color for each class
def visualize_multiclass_mask(mask):
    import matplotlib.pyplot as plt

    # Define colors for each class
    cmap = ListedColormap(["black", "green", "blue", "red"])

    plt.imshow(mask, cmap=cmap)
    plt.title("Multiclass Mask")
    plt.colorbar(ticks=[0, 1, 2, 3], format=plt.FuncFormatter(lambda x, _: ["None", "Vegetation", "Water", "Urban"][int(x)]))
    plt.show()
 
def create_multiclass_mask(ndvi, ndwi, ndbi, ndvi_t=NDVI_THRESHOLD, ndwi_t=NDWI_THRESHOLD, ndbi_t=NDBI_THRESHOLD):
    mask = np.zeros_like(ndvi, dtype=np.uint8)  # Initialize with all zeros
    
    mask[ndvi > ndvi_t] = VEGETATION
    mask[ndwi > ndwi_t] = WATER
    mask[ndbi > ndbi_t] = URBAN
    
    # Ensure remaining pixels are set to 0
    mask[(ndvi <= ndvi_t) & (ndwi <= ndwi_t) & (ndbi <= ndbi_t)] = 0
    return mask

# the main processing function
def process_image(image_path, output_dir, ndvi_t, ndwi_t, ndbi_t, save_format="png", image_number=1):
    
    # Open
    with rasterio.open(image_path) as src:
        image = src.read()

    # Calculate NDVI, NDWI, and NDBI
    ndvi = calculate_ndvi(image)
    ndwi = calculate_ndwi(image)
    ndbi = calculate_ndbi(image)

    # Threshold the images
    ndvi_thresholded = threshold_image(ndvi, ndvi_t)
    ndwi_thresholded = threshold_image(ndwi, ndwi_t)
    ndbi_thresholded = threshold_image(ndbi, ndbi_t)

    # convert the images to percentage
    ndvi_thresholded = percentage_calculate(ndvi_thresholded)
    ndwi_thresholded = percentage_calculate(ndwi_thresholded)
    ndbi_thresholded = percentage_calculate(ndbi_thresholded)

    # create the multiclass mask
    multiclass_mask = create_multiclass_mask(ndvi_thresholded, ndwi_thresholded, ndbi_thresholded, ndvi_t, ndwi_t, ndbi_t)
    # Extract the base name of the input image and append "_mm"
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    output_filename = f"{output_dir}/{base_name}_mm.{save_format}"

    # Save the multiclass mask as a PNG or TIF file
    if save_format == "png":
        save_image_png(multiclass_mask, output_filename)
    else:
        save_image_tif(multiclass_mask, output_filename, src=src)

    print(f"✅ Processed image {image_number}.")
    return multiclass_mask


# args and main function
if __name__ == "__main__":
    print("✨ Auto Labeling Landsat 8 Images ✨")
    # print with warnining emoji
    print("⚠️ use with radiances images only ⚠️")
    parser = argparse.ArgumentParser(description="Convert Landsat 8 DN values to radiance and save as a multi-band GeoTIFF.")
    parser.add_argument("-i", type=str, help="Path to the multi-band TIFF image or directory containing images.")
    parser.add_argument("-o", type=str, help="Path to save the output radiance GeoTIFF.")
    parser.add_argument("-show", action="store_true", help="Visualize the multiclass mask.")
    # Add an argument for thresholds (ndvi, ndwi, ndbi)
    parser.add_argument("--ndvi", type=float, default=NDVI_THRESHOLD , help="NDVI threshold.")
    parser.add_argument("--ndwi", type=float, default=NDWI_THRESHOLD, help="NDWI threshold.")
    parser.add_argument("--ndbi", type=float, default=NDBI_THRESHOLD, help="NDBI threshold.")
    parser.add_argument("--format", type=str, choices=["tif", "png"], default="tif", help="Output format: 'tif' or 'png'.")
    args = parser.parse_args()

    input_path = args.i

    # Check if the input path is valid
    if not os.path.exists(input_path):
        print("Invalid input path:", input_path)
        exit()
    
    os.makedirs(args.o, exist_ok=True)

    # Process a single image or a directory of images
    if os.path.isfile(input_path):
        mm = process_image(input_path, args.o, args.ndvi, args.ndwi, args.ndbi, save_format=args.format)

        if args.show:
            visualize_multiclass_mask(mm)
            
    elif os.path.isdir(input_path):
        image_files = [f for f in os.listdir(input_path) if f.endswith('.tif')]
        for i, image_file in enumerate(image_files, start=1):
            image_path = os.path.join(input_path, image_file)
            process_image(image_path, args.o, args.ndvi, args.ndwi, args.ndbi, save_format=args.format, image_number=i)
    else:
        print("Invalid input path:", input_path)
        exit()

    # generate a csv file with the calsses constants
    with open('classes.csv', mode='w') as file:
        writer = csv.writer(file)
        writer.writerow(["Class", "Value"])
        writer.writerow(["Vegetation", VEGETATION])
        writer.writerow(["Water", WATER])
        writer.writerow(["Urban", URBAN])

    print("✅ Saved classes to classes.csv")