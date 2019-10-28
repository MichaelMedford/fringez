#!/usr/bin/env python
"""fringe.py"""
from astropy.io import fits
from numpy import median as np_median
from numpy import abs as np_abs
from numpy import zeros_like as np_zeros_like
from numpy import dot as np_dot
from numpy import sqrt as np_sqrt
from numpy import newaxis as np_newaxis
from numpy import load as np_load
from glob import glob
from sys import exit as sys_exit
from os import path as os_path
from fringez.utils import create_fits
from fringez.utils import flatten_images


def generate_fringe_map(image):
    """ Create a fringe map from a science image."""
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


def gather_flat_fringe_maps():
    """Gathers all of the fringe images in the directory,
    flattened for 1D analysis"""
    fname_arr, fringes, rcid = gather_fringe_maps()
    fringe_maps_flattened, image_shape = flatten_images(fringes)
    return fname_arr, fringe_maps_flattened, image_shape, rcid


def gather_fringe_maps():
    """Gathers all of the science images in the directory and returns a list
    of the fringe maps, as well as the rcid of the science images."""

    fname_arr = glob('ztf*sciimg.fits')
    fname_arr.sort()

    with fits.open(fname_arr[0]) as f:
        header = f[0].header

    if 'RCID' in header:
        rcid = int(header['RCID'])
    else:
        rcid = 0

    image_shape = None
    fringe_maps = []
    for i, fname in enumerate(fname_arr):
        if i % 10 == 0:
            print('Generating fringe image %i/%i' % (i, len(fname_arr)))
        with fits.open(fname) as f:
            image = f[0].data
        fringe_map, _ = generate_fringe_map(image)

        if i == 0:
            image_shape = fringe_map.shape
        else:
            if fringe_map.shape != image_shape:
                print('%s != %s' % (str(fringe_map.shape), str(image_shape)))
                print('** ALL FRINGE MAPS MUST BE THE SAME SIZE **')
                print('** EXITING **')
                sys_exit(0)

        fringe_maps.append(fringe_map)

    return fname_arr, fringe_maps, rcid


def append_eigenvalues_to_header(header, fringe_ica):
    for i, eigenvalue in enumerate(fringe_ica.T):
        header['PCAEIG%02d' % i] = eigenvalue[0]

    return header


def calculate_fringe_bias(fringe_map, fringe_model):
    """ Generates fringe bias image for the provided science image.
    These formulas are taken from the scikit-learn estimator's
    transform and inverse transform methods.

    Models are loaded from disk as
    fringe_{MODEL_NAME}_comp{N_COMPONENTS}.c{CID}_q{QID}.{DATE}.model """

    fringe_map = fringe_map.flatten()
    fringe_map_transposed = fringe_map.reshape(1, len(fringe_map))

    mean = fringe_model['mean']
    components = fringe_model['components']
    explained_variance = fringe_model['explained_variance']

    fringe_map_transposed = fringe_map_transposed - mean
    fringe_ica = np_dot(fringe_map_transposed, components.T)
    fringe_ica /= np_sqrt(explained_variance)

    fringe_bias = np_dot(fringe_ica, np_sqrt(
        explained_variance[:, np_newaxis]) * components) + mean

    return fringe_bias, fringe_ica


def remove_fringe(image_name,
                  fringe_model_name,
                  debugFlag=False):
    """ Subtracts the fringe bias image from the science image, resulting in
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

    fringe_model = np_load(fringe_model_name)

    fringe_bias, fringe_ica = calculate_fringe_bias(fringe_map, fringe_model)
    fringe_bias = fringe_bias.reshape(image_shape)
    fringe_bias *= median_absdev

    header = append_eigenvalues_to_header(header, fringe_ica)
    header['FRNGMDL'] = os_path.basename(fringe_model_name)

    image_clean = image - fringe_bias
    image_clean_fname = image_name.replace('.fits', '.clean.fits')
    create_fits(image_clean_fname, image_clean, header)
    print('-- %s saved to disk' % image_clean_fname)

    if debugFlag:
        extension = os_path.basename(fringe_model_name).replace('.model',
                                                                '.bias')
        fname = image_name.replace('.fits', '.%s.fits' % extension)
        create_fits(fname, fringe_bias, header)

        print('-- %s saved to disk' % fname)
