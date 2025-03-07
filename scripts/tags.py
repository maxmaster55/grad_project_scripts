import rasterio
import rasterio.plot

data = "./sentinel2_image_30m_.tif"

tiff  = rasterio.open(data)

print(tiff.tags())

