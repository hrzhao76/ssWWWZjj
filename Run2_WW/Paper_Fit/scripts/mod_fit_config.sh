#!/bin/bash

show_help() {
  echo "Usage: $0 [new_config_dirpath] [new_debuglevel] [dir_path] [histopath]"
  echo "  new_config_dirpath:     New directory path to store modified config files."
  echo "  new_debuglevel:         New DebugLevel value. (default: 1)"
  echo "  dir_path:               Directory path containing the config files. (default: /data/hrzhao/Samples/ssWWWZ_run3/information_Run2_ssWWHpp/fit_configs/TRExFitter_configfiles_unblinded)"
  echo "  histopath:              New HistoPath value. (default: /data/hrzhao/Samples/ssWWWZ_run3/information_Run2_ssWWHpp/fit_inputs/histograms_th1_step2)"
}

# Check if help option is provided
if [[ "$1" == "-h" || "$1" == "--help" ]]; then
  show_help
  exit 0
fi

# Set new directory path for modified config files
new_config_dirpath="${1:-./mod_fit_config}"

# Set new DebugLevel value
new_debuglevel="${2:-1}"

# Set default directory path if not provided as a command-line argument
dir_path="${3:-/data/hrzhao/Samples/ssWWWZ_run3/information_Run2_ssWWHpp/fit_configs/TRExFitter_configfiles_unblinded}"

# Set default HistoPath value if not provided as a command-line argument
histopath="${4:-/data/hrzhao/Samples/ssWWWZ_run3/information_Run2_ssWWHpp/fit_inputs/histograms_th1_step2}"

mkdir -p "$new_config_dirpath"

# Find and sort the config files in the directory
IFS=$'\n' config_files=($(find "$dir_path" -name "*.config" -type f | sort))

# Iterate over each sorted config file
for file_path in "${config_files[@]}"; do
  # Extract the wp_mass following "m" in the filename
  config_file=$(basename "$file_path")
  wp_mass=$(echo "$config_file" | grep -oP "(?<=m)\d+")

  # Create a copy of the config file in the new directory
  cp "$file_path" "$new_config_dirpath/${config_file}"

  # Replace the HistoPath value in the copied config file
  sed -i "s#HistoPath: \".*\"#HistoPath: \"$histopath\"#" "$new_config_dirpath/${config_file}"

  # Add the OutputDir line with two blank spaces before it, after the HistoPath line in the copied config file
  # sed -i "/HistoPath:.*$/a \  OutputDir: \"/data/hrzhao/Samples/ssWWWZ_run3/MyOutputs/Paper_Fit/fit_output/\"" "$new_config_dirpath/${config_file}"

  # Replace the DebugLevel value in the copied config file
  sed -i "s/DebugLevel: [0-9]/DebugLevel: $new_debuglevel/" "$new_config_dirpath/${config_file}"

  echo "Config file $config_file updated successfully for mass point: $wp_mass"
done
