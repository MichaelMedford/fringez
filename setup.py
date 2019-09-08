#! /usr/bin/env python
"""
__setup__.py
Inspired by: https://github.com/pypa/sampleproject
"""

DESCRIPTION = "Removing atmospheric fringes from ZTF i-band images"

DISTNAME = 'fringez'
AUTHOR = 'Michael Medford'
AUTHOR_EMAIL = 'michaelmedford@berkeley.edu'
URL = 'https://github.com/MichaelMedford/fringez'
LICENSE = 'MIT'
VERSION = open('VERSION').readline().strip()
DOWNLOAD_URL = 'https://github.com/MichaelMedford/fringez/tarball/%s' % VERSION

from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    LONG_DESCRIPTION = f.read()
LONG_DESCRIPTION_CONTENT_TYPE = 'text/markdown'

setup(name=DISTNAME,
      author=AUTHOR,
      author_email=AUTHOR_EMAIL,
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      long_description_content_type=LONG_DESCRIPTION_CONTENT_TYPE,
      license=LICENSE,
      url=URL,
      version=VERSION,
      download_url=DOWNLOAD_URL,
      packages=find_packages(exclude=['contrib', 'docs', 'tests']),
      python_requires='>=3.5',
      install_requires=['astropy',
                        'joblib',
                        'numpy',
                        'matplotlib',
                        'scikit-learn',
                        'requests',
                        'wget',
                        'beautifulsoup4'],
      scripts=['bin/fringez-generate',
               'bin/fringez-clean',
               'bin/fringez-download'],
      classifiers=['Intended Audience :: Science/Research',
                   'Programming Language :: Python :: 3.5',
                   'License :: OSI Approved :: MIT License',
                   'Topic :: Scientific/Engineering :: Astronomy',
                   'Operating System :: POSIX',
                   'Operating System :: Unix',
                   'Operating System :: MacOS'],
      project_urls={'Models': 'https://portal.nersc.gov/project/ptf/iband'}
      )
