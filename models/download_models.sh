#!/bin/bash

read -p "MODEL_DATE: " MODEL_DATE

filename=ztf_iband_fringe_models_${MODEL_DATE}.tar.gz

echo Downloading ${filename}...
wget https://portal.nersc.gov/project/ptf/iband/$filename

echo Extracting ${filename}...
gunzip $filename
tar -xvf ${filename%.gz}

echo ${MODEL_DATE} Models Downloaded