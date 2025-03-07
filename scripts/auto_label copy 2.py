import rasterio
import numpy as np
import cv2
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import argparse


# Constants for the classes
VEGETATION = 1
WATER = 2
URBAN = 3

# thresholds for the classes
NDVI_THRESHOLD = 0.5
NDWI_THRESHOLD = 0.99
NDBI_THRESHOLD = 0.9


image_path = "../tile_3_2_r.tif"
with rasterio.open(image_path) as src:
    image = src.read()  # Read all bands


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


def save_image_tif(image, filename):
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


ndvi = calculate_ndvi(image)
ndwi = calculate_ndwi(image)
ndbi = calculate_ndbi(image)


# Threshold the images
ndvi_thresholded = threshold_image(ndvi, NDVI_THRESHOLD)
ndwi_thresholded = threshold_image(ndwi, NDWI_THRESHOLD)
ndbi_thresholded = threshold_image(ndbi, NDBI_THRESHOLD)

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
 
def create_multiclass_mask(ndvi, ndwi, ndbi):
    mask = np.zeros_like(ndvi, dtype=np.uint8)  # Initialize with all zeros
    
    mask[ndvi > NDVI_THRESHOLD] = VEGETATION  # Vegetation
    mask[ndwi > 0] = WATER  # Water
    mask[ndbi > 0] = URBAN  # Urban/Built-up
    
    return mask

# the percintages of each pixel being in the class
ndvi_thresholded = percentage_calculate(ndvi_thresholded)
ndwi_thresholded = percentage_calculate(ndwi_thresholded)
ndbi_thresholded = percentage_calculate(ndbi_thresholded)

# Create the multiclass mask
multiclass_mask = create_multiclass_mask(ndvi_thresholded, ndwi_thresholded, ndbi_thresholded)

# visualize_multiclass_mask(multiclass_mask)

# Save the multiclass mask as a tif file
# save_image_tif(multiclass_mask, "../multiclass_mask.tif")

# the main processing function
def process_image(image_path, output_dir):
    with rasterio.open(image_path) as src:
        image = src.read()

    # Calculate NDVI, NDWI, and NDBI
    ndvi = calculate_ndvi(image)
    ndwi = calculate_ndwi(image)
    ndbi = calculate_ndbi(image)

    # Threshold the images
    ndvi_thresholded = threshold_image(ndvi, NDVI_THRESHOLD)
    ndwi_thresholded = threshold_image(ndwi, NDWI_THRESHOLD)
    ndbi_thresholded = threshold_image(ndbi, NDBI_THRESHOLD)

    # create the multiclass mask
    multiclass_mask = create_multiclass_mask(ndvi_thresholded, ndwi_thresholded, ndbi_thresholded)

    # Save the multiclass mask as a tif file
    save_image_tif(multiclass_mask, output_dir)