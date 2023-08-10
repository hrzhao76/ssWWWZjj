#!/bin/bash

source /data/hrzhao/sw/TRExFitter/setup.sh

wp_mass=$1
fit_type="${2:-full_systs}"
config_dirpath="${3:-/home/hrzhao/Projects/ssWWWZjj/Run2_WW/Paper_Fit/mod_fit_configs}"

additional_options=""
output_dir="/data/hrzhao/Samples/ssWWWZ_run3/MyOutputs/Paper_Fit/fitoutput_types/${fit_type}"
full_additional_options="${additional_options}OutputDir=${output_dir}"

# One should be able to combine `hdbwpflsri` but this fails from time to time with Segmentation Fault
# So I split it into multiple commands
for fit_option in h d b w p f l s r i; do
    trex-fitter $fit_option $config_dirpath/Anal_ssWW_interpretation_m${wp_mass}.config \
    "$full_additional_options"
done
# trex-fitter hdbwpflsri $config_dirpath/Anal_ssWW_interpretation_m${wp_mass}.config \
# "Systematics=NONE:OutputDir=/data/hrzhao/Samples/ssWWWZ_run3/MyOutputs/Paper_Fit/fitoutput_types/${fit_type}"
