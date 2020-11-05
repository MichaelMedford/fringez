#!/usr/bin/env python
"""utils.py"""
import numpy as np
import glob
import os
from astropy.io import fits


def flatten_images(images):
    """Flattens images for use in 1D analysis"""

    # If parallelFlag and non-root rank is passing in None
    if images is None:
        return None, None

    image_shape = images[0].shape
    images_flattened = []
    for i, image in enumerate(images):
        if i % 10 == 0:
            print('Flattening image %i/%i' % (i, len(images)))
        images_flattened.append(image.flatten())
    images_flattened = np.array(images_flattened)

    return images_flattened, image_shape


def create_fits(image_name,
                data,
                header=None):
    """Creates a fits image with an optional header

    Uses the astropy.io.fits pacakge to create a fits image.
    WARNING : THIS WILL OVERWRITE ANY FILE ALREADY NAMED 'image_name'.
    """
    # Creates the Header Data Unit
    hdu = fits.PrimaryHDU(data)

    # Adds the 'header' if None is not selected
    if header is not None:
        hdu.header = header

    # Remove the image if it currently exists
    if os.path.exists(image_name):
        os.remove(image_name)

    # Write the fits image to disk
    hdu.writeto(image_name)


def generate_random_ds9_list(n_random=6):
    """ Generates a random list of images to be viewed in ds9
    Viewed with: ds9 -zscale $(<ds9.list) """

    fname_arr = glob.glob('ztf*sciimg.clean.fits')
    fname_arr.sort()

    n_images = min(n_random, len(fname_arr))

    idx_arr = np.random.choice(np.arange(len(fname_arr)), n_images,
                               replace=False)
    with open('ds9.list', 'w') as f:
        for idx in idx_arr:
            f.write('%s\n' % fname_arr[idx])
            f.write('%s\n' % fname_arr[idx].replace('.clean', ''))
