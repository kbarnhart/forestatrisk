#!/usr/bin/python

# ==============================================================================
# author          :Ghislain Vieilledent
# email           :ghislain.vieilledent@cirad.fr, ghislainv@gmail.com
# web             :https://ghislainv.github.io
# python_version  :2.7
# license         :GPLv3
# ==============================================================================

# Import
import numpy as np  # For arrays
from osgeo import gdal  # GIS libraries
from miscellaneous import makeblock, progress_bar


# Countpix
def countpix(input_raster, value=1, blk_rows=0):
    """Count the number of pixels having a specific value.

    Count the number of pixels (and the corresponding area in ha) having a
    specific value.

    :param input_raster: Input raster file.
    :param value: Target value.
    :param blk_rows: if > 0, number of lines per block.

    :return: A dictionary with the number of pixels having the
    specified value (npix) and the total area (area, in ha).

    """

    # Read raster
    rasterR = gdal.Open(input_raster)
    rasterB = rasterR.GetRasterBand(1)

    # Make blocks
    blockinfo = makeblock(input_raster, blk_rows=blk_rows)
    nblock = blockinfo[0]
    nblock_x = blockinfo[1]
    x = blockinfo[3]
    y = blockinfo[4]
    nx = blockinfo[5]
    ny = blockinfo[6]
    print("Divide region in " + str(nblock) + " blocks")

    # Number of pixels with a given value
    print("Compute the number of pixels with value=" + str(value))
    npix = 0

    # Loop on blocks of data
    for b in range(nblock):
        # Progress bar
        progress_bar(nblock, b + 1)
        # Position in 1D-arrays
        px = b % nblock_x
        py = b / nblock_x
        # Read the data
        rasterA = rasterB.ReadAsArray(x[px], y[py], nx[px], ny[py])
        # Identify pixels (x/y coordinates) which are deforested
        pix = np.nonzero(rasterA == value)
        npix += len(pix[0])

    # Compute area
    print("Compute the corresponding area in ha")
    gt = rasterR.GetGeoTransform()
    pix_area = gt[1] * (-gt[5])
    area = pix_area * npix / 10000

    # Results
    return({'npix': npix, 'area': area})

# End
