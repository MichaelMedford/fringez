#!/usr/bin/env python
"""plot.py"""
import matplotlib.pyplot as plt
import numpy as np
import os


def plot_gallery(title, images, image_shape):
    """Plots a panel of images"""

    n_images, _ = images.shape
    n_col = n_row = np.ceil(np.sqrt(n_images)).astype(int)

    fig, ax = plt.subplots(n_row, n_col)
    ax = ax.flatten()
    fig.suptitle(title, size=10)
    for i, comp in enumerate(images):
        vmax = max(comp.max(), -comp.min())
        ax[i].imshow(comp.reshape(image_shape),
                     cmap='gray',
                     interpolation='None',
                     vmin=-vmax, vmax=vmax,
                     origin='lower')
        ax[i].set_xticks(())
        ax[i].set_yticks(())
        ax[i].set_title('Comp %i' % i)

    model_folder = os.path.dirname(os.path.realpath(__file__)) + '/models'
    fname = '%s/%s.png' % (model_folder, title.replace(' ', '_'))
    fig.savefig(fname)
    print('%s saved to disk' % fname)
    plt.close()


def plot_before_and_after(title, image, image_model):
    """Plots the difference between an image and its model."""

    vmax = max(image.max(), -image.min())
    residual = image - image_model

    fig, ax = plt.subplots(2, 2, figsize=(8, 6))
    ax = ax.flatten()

    fig.suptitle(title, size=10)
    ax[0].imshow(image,
                 cmap='gray',
                 interpolation='None',
                 vmin=-vmax, vmax=vmax,
                 origin='lower')
    ax[0].set_title('Fringe Original')

    ax[1].imshow(image_model,
                 cmap='gray',
                 interpolation='None',
                 vmin=-vmax, vmax=vmax,
                 origin='lower')
    ax[1].set_title('Fringe Model')

    ax[2].imshow(residual,
                 cmap='gray',
                 interpolation='None',
                 vmin=-vmax, vmax=vmax,
                 origin='lower')
    ax[2].set_title('Residual')

    std_image = float(np.std(image))
    std_residual = float(np.std(residual))
    bins = np.linspace(-std_image, std_image, 200)
    ax[3].hist(image.flatten(), bins=bins,
               color='g', alpha=0.3,
               label='Original +- %.2f' % std_image)
    ax[3].hist(residual.flatten(), bins=bins,
               color='b', alpha=0.3,
               label='Residual +- %.2f' % std_residual)
    ax[3].set_title('Pixel Histogram')
    ax[3].legend(loc=3)

    model_folder = os.path.dirname(os.path.realpath(__file__)) + '/models'
    fname = '%s/%s.png' % (model_folder, title.replace(' ', '_'))
    fig.savefig(fname)
    print('%s saved to disk' % fname)
    plt.close()
