# fringez

## Getting Started

ZTF i-band images are contaminated with atmospheric fringes that significantly 
effect the photometric solution of sources within the image. ```fringez``` uses 
principal component analysis to generate a fringe model from these i-band 
images. Each ZTF readout channel generates similar atmospheric fringe patterns 
and therefore requires its own fringe model. That fringe model can then be 
used to generate a fringe bias image for each contaminated i-band image which, 
when subtraction from the i-band image, removes the atmospheric fringes. 
This results in a clean i-band image.  

**Diagram of fringez Scripts**
![](https://github.com/MichaelMedford/fringez/raw/master/figures/fringez_diagram.jpeg)

```fringez``` installs three executables.

- ```fringez-download```: Downloads pre-generated fringe models from the NERSC 
web portal
- ```fringez-clean```: Cleans contaminated i-band images using fringe models
- ```fringez-generate```: Generates new fringe models using contaminated i-band 
images

### Installation

Preferred method is through pip:

```
pip install fringez
```

Latest version can also be installed from github:
```
git clone https://github.com/MichaelMedford/fringez.git
cd fringez
python setup.py install
```

### Downloading Fringe Models
Users must have fringe models on disk in order to clean i-band images with 
atmospheric fringes. These fringe models are what generate a fringe bias 
image for each contaminated i-band image which, when subtraction from the 
i-band image, removes the atmospheric fringes. This results in a clean i-band 
image.  

Pre-generated fringe models can be downloaded from the NERSC web portal 
with the ```fringez-download``` executable. Select a ```-fringe-model-date``` 
from the below list to download a version of the pre-generated fringe models. 
The script will also download the model lists, containing the list of images 
used to create the fringe model. 

Current model versions:
* 20200723 (32 GB)

Fringe models can either be downloaded for all 64 readout channels with the 
```-all``` argument, or only a single fringe model can be downloaded with 
the ```-single``` argument. If the ```-single``` argument is selected, then 
only the model with the ```-fringe-model-id``` argument is downloaded. The 
```-fringe-model-id``` is the cid and the qid of the fringe model combined 
in the following syntax: c01_q1

By default the fringe models and fringe model lists will be downloaded to the 
current directoy, but can also be sent a specific directory with the 
```-fringe-model-folder``` argument.

### Generating Clean Images
Contaminated images can be cleaned with the ```fringez-clean``` executable.

Contaminated images can either be cleaned one at a time with the 
```-single-image``` argument, or all images in a folder can be cleaned with the 
```-all-images-in-folder``` argument. All clean images will have the same 
filename as the science images, but with the extension ```sciimg.clean.fits```. 
To save the fringe bias images to disk for debugging, select the ```-debug``` 
argument.

#### Cleaning all contaminated images in a folder

Cleaning a folder of contaminated images requires specifying the folder where 
fringe models are located. ```fringez-clean``` will automatically pair the 
correct fringe model with each contaminated image.

From within the directory where all of the science images are located, 
execute ```fringez-clean -all-images-in-folder 
-fringe-model-folder={FRINGE_MODEL_FOLDER}```. The ```-fringe-model-folder``` 
argument must be set when ```-all-images-in-folder``` is selected.

When cleaning all images, ```fringez-clean``` can either clean one image at a 
time with the ```-serial``` argument, or clean images in parallel with the 
```-parallel``` argument. Images are cleaned in ```-serial``` by default. 
Parallelization is executed with the mpi4py package and simply splits the list 
of images in the folder across the processes used to launch the 
```fringez-clean``` executable.

#### Cleaning a single contaminated image

Cleaning a single contaminated image requires specifying a fringe model. This 
fringe model should match the readout channel ID of the contaminated image. 
The image and the model will both be labelled with the same quadrant ID and 
ccd ID. For example, if ```ztf_20190703184838_000481_zi_c02_o_q1_sciimg.fits```
is the contaminated image, then 
```fringe_PCArandom_comp06.c02_q1.20190618.model``` would be the correct model 
because of the matching ``c02`` and ```q1``` parameters. 

From within the directory where the contaminated science image is located, 
execute ```fringez-clean -single-image -image-name={IMAGE_NAME} 
-fringe-model-name={FRINGE_MODEL_NAME}```. The ```-image-name``` and 
```-fringe-model-name``` arguments must be set when ```-single-image``` is 
selected.  

### Measuring the Uniform Background Indicator (UBI)
The presence of correlated background noise can be determined by measuring 
the Uniform Background Indicator, or UBI, or an image. The measurement is made 
by performing aperture photometry on random background locations and measuring 
how well the scatter in background flux measurements is captured by locally 
determined estimates of the flux error. 

An ideal `UBI = 1` indicates no correlated background noise, with larger values 
indicating more correlated noise. Here are the results of calculating UBI on 
an image of random noise for various aperture sizes, as well as three example 
images to qualitatively show how UBI scales with the presence of 
atmospheric fringes.

**Ideal UBI and Example Images**
![](https://github.com/MichaelMedford/fringez/raw/master/figures/UBI_apertures_and_examples.png)

To measure the UBI on an image:

```python
from fringez.metric import calculate_UBI
UBI, UBI_err = calculate_UBI(sciimg_fname, mskimg_fname, updateHeader=True)
```

The science image header will be updated with the value of the image's UBI.

### Generating Fringe Models
*Note: Downloading pre-generated models using the fringez-download executable 
is recommended. Most users will not need to generate new fringe models. New 
models must be generated from images that have not already been cleaned.*

Fringe models are generated with the ```fringez-generate``` executable.

The models which will be generated are listed in 
```$PATH_TO_FRINGEZ_DIR/model.py:return_estimators```. 
The number of components in each model fit are set with the 
```-n-components``` argument. Plots of the eigenimages can be generated for 
debugging with the ```-plots``` argument.
 
To generate fringe models:

1) Place images containing fringes into a directory. **All images within the 
directory must have the same RCID. Models are made separately for each ZTF 
RCID.** Image names are expected to begin with **ztf** and end with 
```sciimg.fits```. 
2) From within this folder, execute ```fringez-generate```. By default the 
script will choose six components and will not generate debugging plots. 
3) The current directory will now contain a model or models of the fringes, 
named **fringe\_{MODEL_NAME}\_comp{N_COMPONENTS}.c{CID}\_q{QID}.{DATE}.model**. 
By default the script will only generate **PCArandom** models, but more models 
can be tested by editing the 
```$PATH_TO_FRINGEZ_DIR/model.py:return_estimators``` function. The current 
directory will also contain a ```*.model_list``` file for each model listing 
the images that went into the creation of the model.

## Requirements
* Python 3.6

## Authors

* Michael Medford <MichaelMedford@berkeley.edu>
* Peter Nugent <penugent@lbl.gov>

## Citation
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.4247698.svg)](https://doi.org/10.5281/zenodo.4247698)