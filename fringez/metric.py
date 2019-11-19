#! /usr/bin/env python
"""
metric.py
"""

from photutils import Background2D
from photutils import StdBackgroundRMS, MedianBackground
from astropy.io import fits
import numpy as np


def return_backgrounds(image):
    bkg = Background2D(image, (10, 10), filter_size=1,
                       bkg_estimator=MedianBackground(sigma_clip=None),
                       bkgrms_estimator=StdBackgroundRMS(sigma_clip=None))
    return bkg.background, bkg.background_rms


def return_fom(filename):
    image = fits.open(filename)[0].data

    median_bkg, rms_bkg = return_backgrounds(image)

    term0 = np.abs(median_bkg - np.median(image))
    term1 = rms_bkg
    fom = np.sum(term0 < term1) / len(image.flatten())
    return fom
