#! /usr/bin/env python
"""
__setup__.py
"""

DESCRIPTION = "Removing atmospheric fringes from ZTF i-band images."
LONG_DESCRIPTION = """Removing atmospheric fringes from ZTF i-band images."""

DISTNAME = 'fringez'
AUTHOR = 'Michael Medford'
MAINTAINER = 'Michael Medford'
MAINTAINER_EMAIL = 'michaelmedford@berkeley.edu'
URL = 'https://github.com/MichaelMedford/fringez'
LICENSE = 'MIT'
VERSION = open('VERSION').readline().strip()
DOWNLOAD_URL = 'https://github.com/MichaelMedford/fringez/tarball/%s' % VERSION

try:
    from setuptools import setup, find_packages
    _has_setuptools = True
except ImportError:
    from distutils.core import setup
_has_setuptools = False

if __name__ == "__main__":

    if _has_setuptools:
        packages = find_packages()
    else:
        # This should be updated if new submodules are added
        packages = ['fringez']

    setup(name=DISTNAME,
          author=AUTHOR,
          author_email=MAINTAINER_EMAIL,
          maintainer=MAINTAINER,
          maintainer_email=MAINTAINER_EMAIL,
          description=DESCRIPTION,
          long_description=LONG_DESCRIPTION,
          license=LICENSE,
          url=URL,
          version=VERSION,
          download_url=DOWNLOAD_URL,
          packages=packages,
          classifiers=[
              'Intended Audience :: Science/Research',
              'Programming Language :: Python :: 3.6',
              'License :: OSI Approved :: MIT License',
              'Topic :: Scientific/Engineering :: Astronomy',
              'Operating System :: POSIX',
              'Operating System :: Unix',
              'Operating System :: MacOS'],
          )
