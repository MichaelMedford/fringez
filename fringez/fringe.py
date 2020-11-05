#!/usr/bin/env python
"""fringe.py"""
from astropy.io import fits
import numpy as np
import sys
import os
from fringez.utils import create_fits
from fringez.utils import flatten_images


def generate_fringe_map(image, mask_image=None):
    """
    Create a fringe map from a science image.
    If a mask is provided, it is used to zeroed out outlier pixels.
    Else, pixels +-5 sigma are zeroed out.
    """
    fringe_map = np.zeros_like(image)
    fringe_map[:] = image[:]
    median = np.median(image)
    median_absdev = np.median(np.abs(image - median))

    if mask_image is None:
        pixel_5sigma_plus = median + (median_absdev * 1.48 * 5)
        pixel_5sigma_minus = median - (median_absdev * 1.48 * 5)

        cond1 = fringe_map >= pixel_5sigma_plus
        cond2 = fringe_map <= pixel_5sigma_minus
        mask = cond1 + cond2
        fringe_map[mask] = median
    else:
        mask = mask_image != 0
        fringe_map[mask] = median

    fringe_map -= median
    fringe_map /= median_absdev

    return fringe_map, median_absdev


def gather_flat_fringe_maps(N_samples, parallelFlag):
    """Gathers all of the fringe images in the directory,
    flattened for 1D analysis"""
    fname_arr, fringes, rcid = gather_fringe_maps(N_samples, parallelFlag)
    fringe_maps_flattened, image_shape = flatten_images(fringes)
    return fname_arr, fringe_maps_flattened, image_shape, rcid


def gather_fringe_maps(N_samples, parallelFlag):
    if parallelFlag:
        from mpi4py import MPI
        comm = MPI.COMM_WORLD
        rank = comm.Get_rank()
        size = comm.Get_size()
    else:
        rank, size = 0, 1

    if rank == 0:
        # Only select images currently on disk
        data = np.genfromtxt('fringe_maglimits.txt', delimiter=',', names=True,
                             dtype=None, encoding='utf-8')
        fringe_filename_arr = []
        maglimit_arr = []
        for fringe_filename, maglimit in data:
            if os.path.exists(fringe_filename):
                fringe_filename_arr.append(fringe_filename)
                maglimit_arr.append(maglimit)
        fringe_filename_arr = np.array(fringe_filename_arr)
        maglimit_arr = np.array(maglimit_arr)
        N_images = len(fringe_filename_arr)

        # Sort in ascending maglim order
        maglimit_idxs = np.argsort(maglimit_arr)
        fringe_filename_arr = fringe_filename_arr[maglimit_idxs]

        # Determine the rcid of the folder
        ccdid = int(fringe_filename_arr[0].split('_')[-4].replace('c', ''))
        qid = int(fringe_filename_arr[0].split('_')[-2].replace('q', ''))
        rcid = (ccdid - 1) * 4 + (qid - 1)
        print('rcid = %i' % rcid)

        # Determine the image_shape
        with fits.open(fringe_filename_arr[0]) as f:
            image_shape = f[0].data.shape

        # Calculate the size of the samples
        N_images_per_sample = int(N_images / N_samples)
        print('%i image on disk | %i samples -> ~%i images per sample' % (N_images,
                                                                          N_samples,
                                                                          N_images_per_sample))

        fringe_maps = []
    else:
        fringe_filename_arr = None
        image_shape = None
        fringe_maps = None
        rcid = None

    if parallelFlag:
        fringe_filename_arr = comm.bcast(fringe_filename_arr, root=0)
        image_shape = comm.bcast(image_shape, root=0)
        N_images = len(fringe_filename_arr)

    for id_sample in range(N_samples):
        if rank == 0 and id_sample % 10 == 0:
            print('Generating fringe sample %i/%i' % (id_sample, N_samples))

        idx_sample = np.arange(id_sample, N_images, N_samples).astype(int)
        my_idx_sample = np.array_split(idx_sample, size)[rank]

        my_sample = np.zeros((len(my_idx_sample), image_shape[0], image_shape[1]))

        for i, idx in enumerate(my_idx_sample):
            fringe_filename = fringe_filename_arr[idx]
            with fits.open(fringe_filename) as f:
                data_fringe = f[0].data
            if data_fringe.shape != image_shape:
                print('%s != %s' % (str(fringe_map.shape), str(image_shape)))
                print('** ALL FRINGE MAPS MUST BE THE SAME SIZE **')
                print('** EXITING **')
                sys.exit(0)

            mskimg_filepath = fringe_filename.replace('sciimg', 'mskimg')
            if os.path.exists(mskimg_filepath):
                with fits.open(mskimg_filepath) as f:
                    data_mskimg = f[0].data
            else:
                data_mskimg = None

            fringe_map, _ = generate_fringe_map(data_fringe, mask_image=data_mskimg)
            my_sample[i] = fringe_map
            del data_fringe, fringe_map

        if parallelFlag:
            sizes = [len(a) * image_shape[0] * image_shape[1] for a in np.array_split(idx_sample, size)]
            displacements_input = np.insert(np.cumsum(sizes), 0, 0)[0:-1]

            if rank == 0:
                sample = np.zeros((len(idx_sample), image_shape[0], image_shape[1]))
            else:
                sample = None
            comm.Gatherv(my_sample, [sample, sizes, displacements_input, MPI.DOUBLE], root=0)
        else:
            sample = my_sample

        if rank == 0:
            sample_median = np.median(sample, axis=0)
            fringe_maps.append(sample_median)

    return fringe_filename_arr, fringe_maps, rcid


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
    fringe_ica = np.dot(fringe_map_transposed, components.T)
    fringe_ica /= np.sqrt(explained_variance)

    fringe_bias = np.dot(fringe_ica, np.sqrt(
        explained_variance[:, np.newaxis]) * components) + mean

    return fringe_bias, fringe_ica


def remove_fringe(image_name,
                  fringe_model_name,
                  debugFlag=False):
    """ Subtracts the fringe bias image from the science image, resulting in
    a clean image with extension *sciimg.clean.fits.

    Models are loaded from disk as
    fringe_{MODEL_NAME}_comp{N_COMPONENTS}.c{CID}_q{QID}.{DATE}.model """

    if not os.path.exists(image_name):
        print('Image missing! Exiting...')
        sys.exit(0)

    if not os.path.exists(fringe_model_name):
        print('Fringe model missing! Exiting...')
        sys.exit(0)

    print('Generating clean image for %s' % image_name)

    with fits.open(image_name) as f:
        image = f[0].data
        header = f[0].header
        image_shape = image.shape

    fringe_map, median_absdev = generate_fringe_map(image)

    fringe_model = np.load(fringe_model_name)

    fringe_bias, fringe_ica = calculate_fringe_bias(fringe_map, fringe_model)
    fringe_bias = fringe_bias.reshape(image_shape)
    fringe_bias *= median_absdev

    header = append_eigenvalues_to_header(header, fringe_ica)
    header['FRNGMDL'] = os.path.basename(fringe_model_name)

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
