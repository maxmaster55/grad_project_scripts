import rasterio
import numpy as np
import json
import argparse
from pathlib import Path

def read_from_mtl(mtl_file):
    """Reads radiance scaling factors from the MTL JSON file."""
    with open(mtl_file, "r") as f:
        mtl_data = json.load(f)

    radiance_mult = {}
    radiance_add = {}

    rescaling_data = mtl_data["LANDSAT_METADATA_FILE"]["LEVEL1_RADIOMETRIC_RESCALING"]

    if isinstance(rescaling_data, dict):  # Expected format
        for key, value in rescaling_data.items():
            if key.startswith("RADIANCE_MULT_BAND"):
                band_num = int(key.split("_")[-1])  # Extract band number
                radiance_mult[band_num] = float(value)
            elif key.startswith("RADIANCE_ADD_BAND"):
                band_num = int(key.split("_")[-1])
                radiance_add[band_num] = float(value)
    else:
        print("Unexpected format:", rescaling_data)

    return radiance_mult, radiance_add

def process_tiff(mtl_file, input_tiff, output_tiff):
    """Converts a multi-band Landsat 8 TIFF to radiance and saves all bands in a single TIFF."""
    # Read radiance scaling factors
    radiance_mult, radiance_add = read_from_mtl(mtl_file)

    input_tiff = Path(input_tiff)
    output_tiff = Path(output_tiff)

    # Open the multi-band TIFF
    with rasterio.open(input_tiff) as src:
        num_bands = src.count  # Get number of bands
        print(f"Processing {num_bands} bands from {input_tiff}...")

        # Initialize an empty array to store all radiance bands
        radiance_bands = np.zeros((num_bands, src.height, src.width), dtype=np.float32)

        for band_num in range(1, num_bands + 1):  # Bands are 1-based in rasterio
            if band_num not in radiance_mult:
                print(f"Skipping Band {band_num} (no radiance coefficients in MTL).")
                continue

            print(f"Processing Band {band_num}...")

            # Read DN values
            DN = src.read(band_num)

            # Convert DN to radiance
            radiance = radiance_mult[band_num] * DN + radiance_add[band_num]

            # Store the radiance values in the array
            radiance_bands[band_num - 1] = radiance

        # Save all bands in a single multi-band GeoTIFF
        with rasterio.open(
            output_tiff, "w",
            driver="GTiff",
            height=src.height,
            width=src.width,
            count=num_bands,
            dtype=radiance_bands.dtype,
            crs=src.crs,
            transform=src.transform
        ) as dst:
            for band_num in range(1, num_bands + 1):
                dst.write(radiance_bands[band_num - 1], band_num)

        print(f"Saved multi-band radiance image: {output_tiff}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert Landsat 8 DN values to radiance and save as a multi-band GeoTIFF.")
    parser.add_argument("mtl_file", type=str, help="Path to the MTL JSON file.")
    parser.add_argument("input_tiff", type=str, help="Path to the multi-band TIFF image.")
    parser.add_argument("output_tiff", type=str, help="Path to save the output radiance GeoTIFF.")

    args = parser.parse_args()

    process_tiff(args.mtl_file, args.input_tiff, args.output_tiff)
