# Run2 ssWW

## Ntuple Generation
Use the `caf_wwwz` to generate the ssWW ntuples.
``` bash

prepare.py config/master/ssWWWZ/prepare-ssWWWZ.cfg

submit.py --executable initialize.py config/master/ssWWWZ/initialize-ssWWWZ-UChicago.cfg --jobs config/jobLists/ssWWWZ/jobs-initialize-BNL.txt --allowArgChanges --identifier ini --memory 2000

tqmerge -t initialize -o sampleFolders/initialized/samples-initialized-ssWWWZ.root batchOutput/unmerged_ini/*.root

submit.py config/master/ssWWWZ/analyze-ssWWWZ.cfg --jobs config/jobLists/ssWWWZ/jobs-analyze-BNL.txt --allowArgChanges --identifier full_run2 --queue nemo_vm_atlhei --memory 2000

```

This generates the ntuples in the `output/data/ntup/` folder. Each job task might be splitte to multiple files, e.g.
`1_full_run2_data_X_mc16a_X.part0_SR.root`, the pattern is usually `{dsid}_{identifier}_{data|bkg|sig}_{X(channels)_{mc16a|mc16d|mc16e}_{partX}_{region}.root`.

note:
- `identifier` is the identifier of the job, e.g. `ini` for initialization, `full_run2` for full run2 analysis.

- `X(channels)` means merged `ee`, `em`, `mm` channels.

- `region` is the region of the analysis, e.g. `SR`, `CRlowMjj`, `CRWZ`.

## Ntuple Processing

### Merge Ntuples

``` bash

```

### Plotting

TODO: Add plotting scripts

### Inspection


## ML training

### Data preparation

``` bash

```

### BDT training

``` bash

```

### MLP training

TODO: Add MLP training scripts
