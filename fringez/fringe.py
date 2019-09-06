#!/usr/bin/env python
"""fringe.py"""
from joblib import load as joblib_load
from astropy.io import fits
from numpy import median as np_median
from numpy import abs as np_abs
from numpy import zeros_like as np_zeros_like
from glob import glob
from sys import exit as sys_exit
from os import path as os_path
from fringez.utils import create_fits
from fringez.utils import flatten_images


def generate_fringe_map(image):
    """ Create a fringe image from a science image."""
    median = np_median(image)
    median_absdev = np_median(np_abs(image - median))
    pixel_5sigma_plus = median + (median_absdev * 1.48 * 5)
    pixel_5sigma_minus = median - (median_absdev * 1.48 * 5)

    fringe_map = np_zeros_like(image)
    fringe_map[:] = image[:]
    cond1 = fringe_map >= pixel_5sigma_plus
    cond2 = fringe_map <= pixel_5sigma_minus
    cond = cond1 + cond2
    fringe_map[cond] = median

    fringe_map -= median
    fringe_map /= median_absdev

    return fringe_map, median_absdev


def gather_flat_fringes():
    """Gathers all of the fringe images in the directory,
    flattened for 1D analysis"""
    fname_arr, fringes, rcid = gather_fringes()
    fringes_flattened, image_shape = flatten_images(fringes)
    return fname_arr, fringes_flattened, image_shape, rcid


def gather_fringes():
    """Gathers all of the science images in the directory and returns a list
    of the fringe images, as well as the rcid of the science images."""

    fname_arr = glob('ztf*sciimg.fits')
    fname_arr.sort()

    with fits.open(fname_arr[0]) as f:
        header = f[0].header

    if 'RCID' in header:
        rcid = int(header['RCID'])
    else:
        rcid = 0

    image_shape = None
    fringes = []
    for i, fname in enumerate(fname_arr):
        if i % 10 == 0:
            print('Generating fringe image %i/%i' % (i, len(fname_arr)))
        with fits.open(fname) as f:
            image = f[0].data
        fringe, _ = generate_fringe_map(image)

        if i == 0:
            image_shape = fringe.shape
        else:
            if fringe.shape != image_shape:
                print('%s != %s' % (str(fringe.shape), str(image_shape)))
                print('** ALL FRINGE IMAGES MUST BE THE SAME SIZE **')
                print('** EXITING **')
                sys_exit(0)

        fringes.append(fringe)

    return fname_arr, fringes, rcid


def append_eigenvalues_to_header(header, fringe_ica):
    for i, eigenvalue in enumerate(fringe_ica.T):
        header['PCAEIG%02d' % i] = eigenvalue[0]

    return header


def remove_fringe(image_name,
                  fringe_model_name,
                  debugFlag=False):
    """ Generates fringe bias image for the provided science image and
    and subtracts that fringe bias image from the science image, resulting in
    a clean image with extension *sciimg.clean.fits.

    Models are loaded from disk as
    fringe_{MODEL_NAME}_comp{N_COMPONENTS}.c{CID}_q{QID}.{DATE}.model """

    if not os_path.exists(image_name):
        print('Image missing! Exiting...')
        sys_exit(0)

    if not os_path.exists(fringe_model_name):
        print('Fringe model missing! Exiting...')
        sys_exit(0)

    print('Generating clean image for %s' % image_name)

    with fits.open(image_name) as f:
        image = f[0].data
        header = f[0].header
        image_shape = image.shape

    fringe_map, median_absdev = generate_fringe_map(image)

    estimator = joblib_load(fringe_model_name)

    fringe_map = fringe_map.flatten()
    fringe_map_transposed = fringe_map.reshape(1, len(fringe_map))
    fringe_ica = estimator.transform(fringe_map_transposed)

    fringe_bias = estimator.inverse_transform(fringe_ica)
    fringe_bias = fringe_bias.reshape(image_shape)

    fringe_bias *= median_absdev

    header = append_eigenvalues_to_header(header, fringe_ica)

    image_clean = image - fringe_bias
    image_clean_fname = image_name.replace('.fits', '.clean.fits')
    create_fits(image_clean_fname, image_clean, header)
    print('-- %s saved to disk' % image_clean_fname)

    if debugFlag:
        extension = os.path.basename(fringe_model_name).replace('.model',
                                                                '.bias')
        fname = image_name.replace('.fits', '.%s.fits' % extension)
        create_fits(fname, fringe_bias, header)

        print('-- %s saved to disk' % fname)
