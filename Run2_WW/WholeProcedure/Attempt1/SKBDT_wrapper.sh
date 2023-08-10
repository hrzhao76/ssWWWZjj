#!/bin/sh
# Author : Haoran Zhao

source /data/hrzhao/sw/miniconda3/bin/activate ssWWWZjj
# mamba activate ssWWWZjj
identifier=Attempt1
mass=$1

python /home/hrzhao/Projects/ssWWWZjj/Run2_WW/WholeProcedure/$identifier/train_SKBDT.py $mass --identifier $identifier
python /home/hrzhao/Projects/ssWWWZjj/Run2_WW/WholeProcedure/$identifier/makehist_SKBDT.py $mass --identifier $identifier

# mamba don't work with CERN LCG yet
# setuptrex
# trex-fitter hdbwpflsri /home/hrzhao/Projects/ssWWWZjj/Run2_WW/WholeProcedure/${identifier}/fit_configs/ssWW_bdt_m${mass}.config
