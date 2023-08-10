#!/bin/sh
# Author: Haoran Zhao

source /data/hrzhao/sw/miniconda3/bin/activate ssWWWZjj

fit_output=$1
do_bdtfit="${2:-1}"
do_Asimov="${3:-1}"

echo "fit_output: ${fit_output}"
echo "do_bdtfit: ${do_bdtfit}"
echo "do_Asimov: ${do_Asimov}"

# Helper function for displaying help
display_help() {
    echo "Usage: ./script_name.sh fit_output [do_bdtfit] [do_Asimov]"
    echo ""
    echo "fit_output: Path to the fit output"
    echo "do_bdtfit: Flag indicating whether to plot on BDT fit results (default: 1)"
    echo "do_Asimov: Flag indicating whether to plot on Asimov fitting (default: 1)"
    echo ""
    echo "Example: ./script_name.sh /path/to/fit_output.root 1 0"
    echo ""
    echo "Note: Square brackets indicate optional parameters"
}

# Check if the script was invoked with a help flag
if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    display_help
    exit 0
fi

for dosin in 0 1; do
    echo "Running with dosin=$dosin"
    root -q "/home/hrzhao/Projects/ssWWWZjj/Run2_WW/scripts/plotWWlimits.C(\"${fit_output}\", ${dosin}, ${do_bdtfit}, ${do_Asimov})"
done
