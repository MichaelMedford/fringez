#!/usr/bin/env python
"""convert.py"""
from astropy.io import fits
import numpy as np
from fringez.utils import create_fits


def lcogt_calculate_maglim(cat):
    background = cat['background']
    flux = cat['flux']
    flux_less_background = flux - background
    mask = flux_less_background > 0
    mag = -2.5 * np.log10(flux_less_background[mask])

    num_bins = int(len(mag) / 100)
    counts, edges = np.histogram(mag, bins=num_bins)
    bins = (edges[1:] + edges[:-1]) / 2
    max_mag = bins[np.argmax(counts)]

    num_bins = int(np.sum(mag >= max_mag) / 100)
    bins = np.linspace(max_mag, np.max(mag), num_bins)
    counts, edges = np.histogram(mag, bins=bins)
    bins = (edges[1:] + edges[:-1]) / 2
    maglim = np.min(bins[counts < (np.max(counts) * 0.75)])

    return maglim


def lcogt_convert_image(image_name):
    # Format specified in https://lco.global/documentation/data/BANZAIpipeline/
    with fits.open(image_name) as f:
        cat_data = f[2].data
        maglim = lcogt_calculate_maglim(cat_data)

        sci_header = f[1].header
        sci_header['MAGLIM'] = maglim
        sci_data = f[1].data
        sci_name = image_name.replace('.fits.fz', '-sciimg.fits')
        create_fits(sci_name, sci_data, sci_header)

        mask_data = f[3].data  # zero for background pixel, non-zero for everything else
        mask_name = image_name.replace('.fits.fz', '-mskimg.fits')
        create_fits(mask_name, mask_data)
