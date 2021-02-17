#! /usr/bin/env python
"""
metric.py
"""

from astropy.io import fits
from photutils import MedianBackground, StdBackgroundRMS
from photutils import aperture_photometry, CircularAperture
from photutils.background import Background2D
import numpy as np
import os
from fringez.utils import create_fits, update_fits


def return_backgrounds(image, mask, mskimg_fname, saveBackground=True):
    rms_fname = mskimg_fname.replace('mskimg', 'rmsimg')
    if os.path.exists(rms_fname):
        with fits.open(rms_fname) as f:
            rms = f[0].data
    else:
        bkg = Background2D(image, (10, 10), mask=mask, filter_size=1,
                           bkg_estimator=MedianBackground(sigma_clip=None),
                           bkgrms_estimator=StdBackgroundRMS(sigma_clip=None))
        rms = bkg.background_rms.astype(np.float32)
        if saveBackground:
            create_fits(rms_fname, rms)
    return rms

  
def load_image_and_mask(sciimg_fname, mskimg_fname):
    with fits.open(sciimg_fname) as f:
        image = f[0].data
        image_header = f[0].header

    with fits.open(mskimg_fname) as f:
        mask = f[0].data
    mask = mask.astype(bool)


def return_aperture_locations(mask, N_apertures=50000, aperture_size=2,
                              edge_buffer=10, aperture_buffer_multiple=3):
    aperture_locations = []
    x_size, y_size = mask.shape
    xarr = np.random.randint(low=edge_buffer, high=x_size - edge_buffer,
                             size=N_apertures)
    yarr = np.random.randint(low=edge_buffer, high=x_size - edge_buffer,
                             size=N_apertures)
    aperture_edge = int(aperture_size * aperture_buffer_multiple)
    for x, y in zip(xarr, yarr):
        ymin = int(y - aperture_edge)
        ymax = int(y + aperture_edge)
        xmin = int(x - aperture_edge)
        xmax = int(x + aperture_edge)
        mask_cutout = mask[ymin:ymax, xmin:xmax]
        if np.all(mask_cutout == False):
            aperture_locations.append((x, y))

    return aperture_locations


def calculate_UBI(sciimg_fname, mskimg_fname=None,
                  N_apertures=20000, N_samples=3, aperture_size=2,
                  updateHeader=True):
    if mskimg_fname is None:
        mskimg_fname = sciimg_fname.replace('sciimg', 'mskimg')
    image, image_header, mask = load_image_and_mask(sciimg_fname, mskimg_fname)
    bkg_rms = return_backgrounds(image, mask, mskimg_fname)

    UBI_arr = []
    for i in range(N_samples):
        aperture_locations = return_aperture_locations(mask,
                                                       N_apertures=N_apertures,
                                                       aperture_size=aperture_size)
        aperture = CircularAperture(aperture_locations, r=aperture_size)
        phot_table = aperture_photometry(image, aperture,
                                         error=bkg_rms, mask=mask)
        flux = phot_table['aperture_sum']
        fluxerr = phot_table['aperture_sum_err']
        fluxerr_pixel = fluxerr / aperture.area
        UBI = (np.std(flux) + np.median(fluxerr_pixel)) / np.median(fluxerr)
        UBI_arr.append(UBI)

    if updateHeader:
        image_header[f'UBI{aperture_size:0.0f}'] = np.median(UBI_arr)
        image_header[f'UBIERR{aperture_size:0.0f}'] = np.std(UBI_arr)
        update_fits(sciimg_fname, image, image_header)

    return np.median(UBI_arr), np.std(UBI_arr)
