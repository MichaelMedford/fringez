#!/usr/bin/env python
"""generate_fringe_model.py"""
import argparse
from model import generate_models
from model import test_models
from fringe import gather_flat_fringes


# from utils import generate_random_ds9_list


def main():
    """Generates the fringe model for all science images (and fringe images) in
    the directory. The model is saved to disk."""

    # Get arguments
    parser = argparse.ArgumentParser(description=__doc__)

    arguments = parser.add_argument_group('arguments')
    arguments.add_argument('--n-components', type=int,
                           default=6,
                           help='Number of components in the PCA model. '
                                'DEFAULT 6.')
    arguments.add_argument('--fringe-model-name', type=str,
                           default=None,
                           help='If selected, forces the generated fringe '
                                'models to include this name.')

    plotgroup = parser.add_mutually_exclusive_group()
    plotgroup.add_argument('--plots', dest='plotFlag',
                           action='store_true',
                           help='Turn ON plotting for debugging.')
    plotgroup.add_argument('--plots-off', dest='plotFlag',
                           action='store_false',
                           help='Turn OFF plotting for debugging. DEFAULT.')
    parser.set_defaults(plotFlag=False)

    curdirgroup = parser.add_mutually_exclusive_group()
    curdirgroup.add_argument('--current-dir', dest='curdirFlag',
                             action='store_true',
                             help='Turn ON to export models '
                                  'to current directory.')
    curdirgroup.add_argument('--current-dir-off', dest='curdirFlag',
                             action='store_false',
                             help='Turn OFF to export models '
                                  'to ztf-fringe-model/models directory. '
                                  'DEFAULT')
    parser.set_defaults(curdirFlag=False)

    args = parser.parse_args()

    # Generate the fringe model from the fringe images in the directory
    fname_arr, fringes_flattened, image_shape, rcid = gather_flat_fringes()

    generate_models(fname_arr,
                    fringes_flattened,
                    image_shape,
                    rcid,
                    fringe_model_name=args.fringe_model_name,
                    n_components=args.n_components,
                    plotFlag=args.plotFlag,
                    curdirFlag=args.curdirFlag)

    if args.plotFlag:
        # Apply the fringe model to a random image for testing
        test_models(fringes_flattened,
                    image_shape,
                    rcid,
                    fringe_model_name=args.fringe_model_name,
                    n_components=args.n_components,
                    curdirFlag=args.curdirFlag)


if __name__ == '__main__':
    main()
