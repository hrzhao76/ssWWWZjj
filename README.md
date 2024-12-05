# ssWWWZjj
This repo records the code development for Run2 + Run3 ssWW/WZ+jj analysis in ATLAS.

``` bash
# The following is path-dependent.
mamba env export > environment.yml
mamba env create -f environment.yml

# add the ssWWWZjj package for some utils func
pip install -e .
```

scikit-hep's hist package is also a required dependancy and can be installed with `pip install hist`. This package is not included in the enviornment file because the installation of hist sometimes fails. Further testing is required before including it with the rest of the dependencies.

## Using MC20/23

In order to run with mc20/23 ntuples, they must first be processed with the run 3 development code, found at https://github.com/Alive7/charged-higgs-ML, and the `myoutput_path` variable in `src/utils/constants.py` must be adjusted to point to the output directoies of the run 3 code.
