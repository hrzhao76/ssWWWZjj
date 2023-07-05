#!/bin/sh
# Author : Haoran Zhao

source /data/hrzhao/sw/miniconda3/bin/activate ssWWWZjj
# mamba activate ssWWWZjj
bdt_out_folder=BDT1

python /home/hrzhao/Projects/ssWWWZjj/Run2_WW/ML/BDT/train_SKBDT.py $1 --ml-output-folder $bdt_out_folder
python /home/hrzhao/Projects/ssWWWZjj/Run2_WW/ML/BDT/makehist_SKBDT.py $1 --ml-output-folder $bdt_out_folder
