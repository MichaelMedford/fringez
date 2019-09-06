#!/usr/bin/env python
"""model.py"""
import numpy as np
from sklearn import decomposition
import joblib
from time import time
import datetime
import os
from plot import plot_before_and_after
from plot import plot_gallery


def return_estimators(n_components):
    """Returns all of the estimators that can be used to generate models.
    A larger selection of possible estimators have been commented out, but
    could be uncommented."""

    estimators = [
        ('PCArandom',
         decomposition.PCA(n_components=n_components, svd_solver='randomized',
                           whiten=True))
    ]

    # estimators = [
    #     ('PCArandom',
    #      decomposition.PCA(n_components=n_components,
    #                        svd_solver='randomized',
    #                        whiten=True)),
    #     ('PCAfull',
    #      decomposition.PCA(n_components=n_components,
    #                        svd_solver='full',
    #                        whiten=True)),
    #     ('PCAarpack',
    #      decomposition.PCA(n_components=n_components,
    #                        svd_solver='arpack',
    #                        whiten=True)),
    #     ('PCAauto',
    #      decomposition.PCA(n_components=n_components,
    #                        svd_solver='auto',
    #                        whiten=True))
    # ]

    return estimators


def return_estimator_names():
    """Returns the names of all of the estimators being currently used."""

    estimators = return_estimators(1)
    estimator_names = [e[0] for e in estimators]

    return estimator_names


def generate_models(fname_arr,
                    fringe_maps_flattened,
                    image_shape,
                    rcid,
                    fringe_model_name=None,
                    n_components=6,
                    plotFlag=False):
    """Generates fringe models by applying an estimator method to a collection
    of fringe maps.

    Models are saved to disk as
    fringe_{MODEL_NAME}_comp{N_COMPONENTS}.c{CID}_q{QID}.{DATE}.model
    """

    estimators = return_estimators(n_components=n_components)

    for name, estimator in estimators:
        timestamp = datetime.datetime.now().strftime('%Y%m%d')

        cid = int(rcid / 4) + 1
        qid = int(rcid % 4) + 1

        if fringe_model_name is None:
            model_name = 'fringe_%s_comp%02d.' \
                         'c%02d_q%i.%s.model' % (name,
                                                 n_components,
                                                 cid,
                                                 qid,
                                                 timestamp)
        else:
            model_name = 'fringe_%s_comp%02d.' \
                         'c%02d_q%i.%s.%s.model' % (name,
                                                    n_components,
                                                    cid,
                                                    qid,
                                                    fringe_model_name,
                                                    timestamp)
        print("Extracting the "
              "top %d components "
              "in %s " % (n_components,
                          name))

        t0 = time()
        estimator.fit(fringe_maps_flattened)  # subtracts mean and whitens
        train_time = (time() - t0)
        print("Fitting Model: done in %0.3fs" % train_time)

        joblib.dump(estimator, model_name)
        print('Fringe Model saved as: %s' % model_name)

        log_name = model_name.replace('.model', '.model_list')
        with open(log_name, 'w') as f:
            for fname in fname_arr:
                f.write('%s\n' % fname)
        print('Log saved as: %s' % log_name)

        if plotFlag:
            model_name = os.path.basename(model_name)
            model_name = model_name.replace('.model', '')
            title = '%s components' % model_name
            plot_gallery(title,
                         estimator.components_[:n_components],
                         image_shape)


def test_models(fringe_maps_flattened,
                image_shape,
                rcid,
                fringe_model_name=None,
                n_components=6,
                idx=None,
                curdirFlag=False):
    """Builds a fringe bias for a random science image and subtracts the
    fringe bias from the fringe map. Generates a plot showing the
    difference.

    'idx=None' tests a random image from the list of images_flattened.
    'idx=0' tests the first image from the list of images_flattened, and so on.
    """

    n_samples, n_features = fringe_maps_flattened.shape

    if idx is None:
        idx = np.random.choice(np.arange(n_samples), 1).astype(int)[0]
    fringe_map = fringe_maps_flattened[idx]

    estimator_names = return_estimator_names()

    for name in estimator_names:
        timestamp = datetime.datetime.now().strftime('%Y%m%d')
        if curdirFlag:
            model_folder = '.'
        else:
            model_folder = os.path.dirname(
                os.path.realpath(__file__)) + '/models'

        cid = int(rcid / 4) + 1
        qid = int(rcid % 4) + 1

        if fringe_model_name is None:
            model_name = '%s/fringe_%s_comp%02d.' \
                         'c%02d_q%i.%s.model' % (model_folder,
                                                 name,
                                                 n_components,
                                                 cid,
                                                 qid,
                                                 timestamp)
        else:
            model_name = '%s/fringe_%s_comp%02d.' \
                         'c%02d_q%i.%s.%s.model' % (model_folder,
                                                    name,
                                                    n_components,
                                                    cid,
                                                    qid,
                                                    fringe_model_name,
                                                    timestamp)
        print('Working on %s...' % name)

        estimator = joblib.load(model_name)

        t0 = time()
        fringe_transposed = fringe_map.reshape(1, len(fringe_map))
        fringe_ica = estimator.transform(fringe_transposed)
        fringe_bias = estimator.inverse_transform(fringe_ica)
        fringe_bias = fringe_bias.reshape(image_shape)
        model_time = (time() - t0)
        print("Building fringe bias from %s: done in %0.3fs" % (name,
                                                                model_time))

        model_name = os.path.basename(model_name)
        model_name = model_name.replace('.model', '')
        title = '%s idx%i fringe map vs fringe bias' % (model_name, idx)
        plot_before_and_after(title,
                              fringe_map.reshape(image_shape),
                              fringe_bias)
