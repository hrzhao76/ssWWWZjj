#!/bin/sh
# Author : Haoran Zhao

source /data/hrzhao/sw/miniconda3/bin/activate ssWWWZjj
# mamba activate ssWWWZjj

wp_mass=$1
identifier=Benchmark

python /home/hrzhao/Projects/ssWWWZjj/Run2_WW/WholeProcedure/$identifier/makehist_2DFit.py $wp_mass --identifier $identifier

# source /data/hrzhao/sw/miniconda3/bin/deactivate

# source /data/hrzhao/sw/TRExFitter/setup.sh


# config_dirpath="${3:-/home/hrzhao/Projects/ssWWWZjj/Run2_WW/WholeProcedure/Benchmark/fit_configs}"

# additional_options=""
# output_dir="/data/hrzhao/Samples/ssWWWZ_run3/MyOutputs/Paper_Fit/$identifier/fit_output"
# full_additional_options="${additional_options}OutputDir=${output_dir}"

# # One should be able to combine `hdbwpflsri` but this fails from time to time with Segmentation Fault
# # So I split it into multiple commands
# for fit_option in h d b w p f l s r i; do
#     trex-fitter $fit_option $config_dirpath/ssWW_cut_m${wp_mass}.config \
#     "$full_additional_options"
# done
