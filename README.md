# ztf-fringe-model

## Getting Started

This repository generates fringe models for ZTF i-band images and subtracts that 
fringe model from science images, resulting in clean images with the fringes 
removed.

There are two main scripts for (1) generating fringe models and (2) removing 
fringes from science images using those models.

#### Generating Fringe Models
Fringe models are generated with the ```generate_fringe_model.py``` script. The 
models which will be generated are listed in ```model.py/return_estimators```. 
The number of components in each model fit are set with the 
```--n-components``` argument. Plots of the eigen-images can be generated for 
debugging with the ```--plots``` argument.
 
To generate fringe models:

1) Place images containing fringes into a directory. **All images within the 
directory must have the same RCID. Models are made separately for each ZTF 
RCID.** Image names are expected to begin with **ztf** and end with 
```sciimg.fits```. 
2) From within this folder, execute ```python 
$PATH_TO_DIR/generate_fringe_model.py```. By default the script will choose six 
components and will not generate debugging plots. 
3) The ```ztf-fringe-model/models``` directory will now contain a model or 
models of the fringes, named 
**fringe\_{MODEL_NAME}\_comp{N_COMPONENTS}.c{CID}\_q{QID}.{DATE}.model**. By 
default the script will only generate **PCArandom** models, but more models can 
be tested by editing the ```return_estimators``` function in ```model.py```. 
The ```ztf-fringe-model/models``` directory will also contain a 
```*.model_list``` file for each model listing the images that went into the 
creation of the model.

#### Downloading Fringe Models
Fringe models have been generated for ZTF i-band images and are stored on 
a NERSC web portal. To download these models, navigate to the ```models``` 
directory and execute the ```download_models.sh``` script. You will be asked 
to input a MODEL_DATE which signifies the version of the saved models. Models 
will be downloaded to disk and extracted from a tar.gz file. Models 
(```*.model```) and the lists of files that created them (```*.model_lists```) 
will end up in a ```models/{MODEL_DATE}``` folder.

Current model versions (and size after extraction):
* 20190618 (16 GB)

#### Generating Clean Images
Once a fringe model has been generated for each RCID, images can be 
cleaned with the ```remove_fringe.py``` script. Images can either be cleaned 
one at a time with the ```--single-image``` argument, or all images in a folder 
can be cleaned with the ```--all-images-in-folder``` argument. The fringe 
images used to create clean images can be saved to disk for debugging with the 
```--debug``` argument.

To clean a single image:

From within the directory where the science image is located, 
execute ```python $PATH_TO_DIR/remove_fringe.py --single-image 
--image-name={IMAGE_NAME} --fringe-model-name={FRINGE_MODEL_NAME}```.
The ```--image-name``` and ```fringe-model-name``` arguments must be set when 
```--single-image``` is selected.  

To clean all images in a folder:

From within the directory where all of the science images are located, 
execute ```python $PATH_TO_DIR/remove_fringe.py --all-images-in-folder 
--fringe-model-folder={FRINGE_MODEL_FOLDER}```. The ```--fringe-model-folder``` 
argument must be set when ```--all-images-in-folder``` is selected. Cleaning 
all images is run in ```--serial``` by default, but the ```--parallel``` 
argument can be selected as well. Parallelization is executed with mpi4py 
package and simply splits the list of images in the folder across the 
processes used to launch the ```remove_fringe.py``` script.

All clean images will have the same filename as the science images, but 
with the extension ```sciimg.clean.fits```. By default the script will not 
save fringe images to disk. To do so, select the ```--debug``` argument.

## Requirements
* Python 3

## Authors

* Michael Medford <MichaelMedford@berkeley.edu>
* Peter Nugent <penugent@lbl.gov>