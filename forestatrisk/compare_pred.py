#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ==============================================================================
# author          :Ghislain Vieilledent
# email           :ghislain.vieilledent@cirad.fr, ghislainv@gmail.com
# web             :https://ecology.ghislainv.fr
# python_version  :>=2.7
# license         :GPLv3
# ==============================================================================

# Import
from __future__ import division, print_function  # Python 3 compatibility
import os
import sys
import numpy as np
from osgeo import gdal
from .miscellaneous import progress_bar, makeblock


# compare_pred
def compare_pred(inputA, inputB,
                 output_file="predictions.tif",
                 blk_rows=128):
    """Compute a raster of differences.

    This function compute a raster of differences between two rasters
    of future forest cover. Rasters must have the same extent and resolution.

    :param inputA: path to first raster of predictions.
    :param inputB: path to second raster of predictions.
    :param output_file: name of the output raster file for differences.
    :param blk_rows: if > 0, number of rows for computation by block.

    :return: a raster of differences.

    """

    # Inputs
    ds_A = gdal.Open(inputA)
    band_A = ds_A.GetRasterBand(1)
    ds_B = gdal.Open(inputB)
    band_B = ds_B.GetRasterBand(1)

    # Landscape variables from forest raster
    gt = ds_A.GetGeoTransform()
    ncol = ds_A.RasterXSize
    nrow = ds_A.RasterYSize
    proj = ds_A.GetProjection()

    # Make blocks
    blockinfo = makeblock(inputA, blk_rows=blk_rows)
    nblock = blockinfo[0]
    nblock_x = blockinfo[1]
    x = blockinfo[3]
    y = blockinfo[4]
    nx = blockinfo[5]
    ny = blockinfo[6]
    print("Divide region in {} blocks".format(nblock))

    # Raster of predictions
    print("Create a raster file on disk for projections")
    driver = gdal.GetDriverByName("GTiff")
    ds_out = driver.Create(output_file, ncol, nrow, 1,
                           gdal.GDT_Byte,
                           ["COMPRESS=LZW", "PREDICTOR=2", "BIGTIFF=YES"])
    ds_out.SetGeoTransform(gt)
    ds_out.SetProjection(proj)
    band_out = ds_out.GetRasterBand(1)
    band_out.SetNoDataValue(255)

    # Predict by block
    # Message
    print("Predict deforestation probability by block")
    # Loop on blocks of data
    for b in range(nblock):
        # Progress bar
        progress_bar(nblock, b + 1)
        # Position in 1D-arrays
        px = b % nblock_x
        py = b // nblock_x
        # Data for one block of the stack (shape = (nband,nrow,ncol))
        data_A = band_A.ReadAsArray(x[px], y[py], nx[px], ny[py])
        data_B = band_B.ReadAsArray(x[px], y[py], nx[px], ny[py])

        band_out.WriteArray(pred, x[px], y[py])

    # Compute statistics
    print("Compute statistics")
    band_out.FlushCache()  # Write cache data to disk
    band_out.ComputeStatistics(False)

    # Build overviews
    print("Build overviews")
    band_out.BuildOverviews("nearest", [4, 8, 16, 32])

    # Dereference driver
    band_out = None
    del(ds_out)

# End