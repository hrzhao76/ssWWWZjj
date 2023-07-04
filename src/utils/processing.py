from typing import Union, Literal
import subprocess
from pathlib import Path
import uproot
import pandas as pd
import numpy as np
import awkward as ak
import joblib
import logging

from utils.utils import check_inputpath, check_outputpath, logging_setup
from utils.constants import ttree_prefix, ttree_channels, sig_GMH5pp_dsids, region_labels, bkg_ddFakes_dsid
from utils.constants import ntuple_path, myoutput_path


def call_hadd(file_list: list, output_path: Path, output_name: str) -> tuple:
    """This function calls the hadd command to merge the root files in the file_list.

    Args:
        file_list (list): the list of root files to be merged
        output_path (Path): the path to the output file
        output_name (str): the name of the output file

    Returns:
        tuple: the return code and the path to the merged file, return code 0 if successful
    """
    # Build the hadd command
    command = ["hadd", "-f", output_path / output_name] + file_list

    # Execute the hadd command and capture the output and return code
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()

    return_code = process.returncode
    return_merged_file = None

    # Check the return code and output
    if return_code == 0:
        logging.info("Merging completed successfully.")
        return_merged_file = output_path / output_name

    else:
        logging.critical("Error occurred during merging.")
        logging.critical("Error message:", error.decode("utf-8"))

    return return_code, return_merged_file


def flatten_root(
    input_filepath: Union[str, Path],
    library: Literal["pd", "np", "ak"] = "pd",
) -> Union[pd.DataFrame, np.ndarray, ak.Array]:
    # Check the input path
    check_inputpath(input_filepath)

    # dsid = input_filepath.name.split("_")[0]

    root = uproot.open(input_filepath)

    try:
        root_keys = root.keys()
        root_keys = [string.rstrip(";1") for string in root_keys]
        assert sorted(root_keys) == sorted([ttree_prefix + channel for channel in ttree_channels])
    except AssertionError:
        print(root_keys)
        return root.keys()

    if library == "pd":
        merged_channels = []
        try:
            for ttree_channel in ttree_channels:
                ttree_name = ttree_prefix + ttree_channel
                df = root[ttree_name].arrays(library=library)
                # the following only works for the pattern `HWWTree_{channel};{digits}`
                # df['channel'] = ttree_name.split(";")[0].split("_")[-1]

                # here we directly specify the ttree name
                df["channel"] = ttree_channel
                # df['dsid'] = dsid
                merged_channels.append(df)

            merged_channels = pd.concat(merged_channels)

        except KeyError:
            raise Exception(f"KeyError: {ttree_name} not found in {input_filepath}. ")

        return merged_channels


def MC_is_signal(dsid):
    return dsid in sig_GMH5pp_dsids


def get_ntuple_pattern(dsid_list, mc_type, is_multiple=False):
    dsid_ntuple_map = dict.fromkeys(region_labels)
    for region in region_labels:
        dsid_ntuple_map[region] = dict.fromkeys(dsid_list)

        if not is_multiple:
            for dsid in dsid_list:
                dsid_ntuple_map[region][dsid] = f"{dsid}_full_run2_{mc_type}_X_mc16?_*_{region}.root"
        else:
            if isinstance(dsid_list, np.ndarray):
                dsid_list = list(map(str, dsid_list.tolist()))
            joined_dsids = "{" + ",".join(dsid_list) + "}"
            dsid_ntuple_map[region] = joined_dsids + f"_s_full_run2_{mc_type}_X_mc16?_*_{region}.root"

    return dsid_ntuple_map


def _merge_samples(file_list, dsid, mc_type, region, is_multiple=False):
    merged_root_output_path = myoutput_path / "merged_root" / region
    merged_root_output_path = check_outputpath(merged_root_output_path)
    if not is_multiple:
        return_code, return_merged_file = call_hadd(
            file_list=file_list,
            output_path=merged_root_output_path,
            output_name=f"{dsid}_{mc_type}_merged_{region}.root",
        )
    else:
        return_code, return_merged_file = call_hadd(
            file_list=file_list,
            output_path=merged_root_output_path,
            output_name=f"{dsid}_sub_{mc_type}_merged_{region}.root",
        )

    merged_gz_output_path = myoutput_path / "merged_gz" / region
    merged_gz_output_path = check_outputpath(merged_gz_output_path)

    if return_code == 0:
        # Open the merged file
        merged_channel_pd = flatten_root(input_filepath=return_merged_file)
        merged_channel_pd["dsid"] = dsid

        if not is_multiple:
            joblib.dump(
                merged_channel_pd,
                merged_gz_output_path / f"{dsid}_{mc_type}_merged_{region}.gz",
                compress=("gzip", 3),
            )
        else:
            joblib.dump(
                merged_channel_pd,
                merged_gz_output_path / f"{dsid}_sub_{mc_type}_merged_{region}.gz",
                compress=("gzip", 3),
            )

        return merged_channel_pd


def merge_samples(dsid_list, mc_type, is_multiple=False, logging_verbosity=0):
    logging_setup(verbosity=logging_verbosity, if_write_log=False, output_path=None)

    if not is_multiple:
        ntuples_pattern = get_ntuple_pattern(dsid_list, mc_type)

        for region, dsid_pattern_map in ntuples_pattern.items():
            for dsid, pattern in dsid_pattern_map.items():
                logging.info(dsid, pattern)
                if not MC_is_signal(dsid):
                    mc_type = "bkg"
                file_list = sorted(ntuple_path.glob(pattern))

                _merge_samples(file_list, dsid, mc_type, region)

    else:
        # e.g. EWK WZ samples, four dsids are corresponding to one merged root file [364739, 364740, 364741, 364742]
        for region in region_labels:
            glob_pattern = f"_s_full_run2_{mc_type}_X_mc16?_*_{region}.root"

            # create a single gz file merging all the dsids
            # i.e. according to the bkg type and region
            merged_gz = []
            for dsid in dsid_list:
                file_list = sorted(ntuple_path.glob(str(dsid) + glob_pattern))
                if not MC_is_signal(dsid):
                    mc_type = "bkg"
                merged_gz.append(_merge_samples(file_list, dsid, mc_type, region, is_multiple=True))

            merged_gz = pd.concat(merged_gz)
            joblib.dump(
                merged_gz,
                myoutput_path / "merged_gz" / region / f"{dsid_list[0]}_{mc_type}_merged_{region}.gz",
                compress=("gzip", 3),
            )


def merge_ddFakes_samples():
    for region in region_labels:
        glob_pattern = f"data_fakes_full_run2_bkg_X_mc16?_ddFakes_X_data_X*{region}.root"
        file_list = sorted(ntuple_path.glob(glob_pattern))
        _merge_samples(file_list, bkg_ddFakes_dsid[0], "bkg", region)
