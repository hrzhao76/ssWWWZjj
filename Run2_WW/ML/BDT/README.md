This folder contains the high level scripts to train a BDT with `scikit-learn` framework.

This is a baseline BDT, which is trained on the following features:
``` python
training_features = ['jet0_m', 'jet0_pt', 'jet1_m', 'jet1_pt', 'MT', 'DYjj', 'Mll', 'DPhillMET', 'DEtall', 'DYll']
```
Further features can be added in `train_SKBDT.py` file.

TODO: Hyperparameters tuning.

# How to run
``` bash
./SKBDT_wrapper.sh <H5pp_mass_point>

# e.g. ./SKBDT_wrapper.sh 450

```
