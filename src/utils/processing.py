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
from utils.constants import (
    ttree_prefix,
    ttree_channels,
    sig_GMH5pp_dsids,
    sig_dsid_mass_map,
    region_labels,
    bkg_ddFakes_dsid,
    Mjj_bin_edges_map,
)
from utils.constants import bkg_flattened_categories_map, bkg_flattened_subcategories_map
from utils.constants import ntuple_path, myoutput_path

import hist
from hist import Hist
from utils.constants import fit_bin_edges_proba
from ROOT import TH1, TH1F
import array


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
                logging.info(f"{dsid}, {pattern}")
                if not MC_is_signal(dsid):
                    mc_type = "bkg"
                file_list = sorted(ntuple_path.glob(pattern))

                _merge_samples(file_list, dsid, mc_type, region)

    else:
        # e.g. EWK WZ samples, four dsids are corresponding to one merged root file [364739, 364740, 364741, 364742]
        for region in region_labels:
            pattern = f"_s_full_run2_{mc_type}_X_mc16?_*_{region}.root"

            # create a single gz file merging all the dsids
            # i.e. according to the bkg type and region
            merged_gz = []
            for dsid in dsid_list:
                sub_pattern = str(dsid) + pattern
                file_list = sorted(ntuple_path.glob(sub_pattern))
                logging.info(f"{dsid}, {sub_pattern}")
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
        pattern = f"data_fakes_full_run2_bkg_X_mc16?_ddFakes_X_data_X*_{region}.root"
        logging.info(f"-1, {pattern}")
        file_list = sorted(ntuple_path.glob(pattern))

        _merge_samples(file_list, bkg_ddFakes_dsid[0], "bkg", region)


def get_merged_mc_df(mc_df_path: Path, mc_type: Literal["sig", "bkg"] = "bkg") -> pd.DataFrame:
    """load all the mc(bkg/sig) samples into a single dataframe given a folder path

    Args:
        mc_df_path (Path): path to the df folder
        mc_type (Literal[&quot;sig&quot;, &quot;bkg&quot;], optional): mc_type to load. Defaults to "bkg".

    Raises:
        ValueError: if mc_type is not "sig" or "bkg"

    Returns:
        pd.DataFrame: merged mc dataframe
    """

    logging.info(f"Loading {mc_type} dataframe from {mc_df_path} ...")
    mc_df_path = check_inputpath(mc_df_path)

    merged_df = []
    if mc_type == "sig":
        mc_files = sorted(mc_df_path.glob("*_sig_merged_*.gz"))
    elif mc_type == "bkg":
        mc_files = sorted(mc_df_path.glob("*_bkg_merged_*.gz"))

        # remove sub samples with sub_bkg in name
        mc_files = [file for file in mc_files if "_sub_bkg_" not in file.name]

    else:
        raise ValueError(f"mc_type {mc_type} not supported")

    for file in mc_files:
        logging.info(f"Loading {file.stem} ...")
        merged_df.append(joblib.load(file))

    return pd.concat(merged_df)


def get_individual_sig_df(mc_df_path: Path, dsid: int) -> pd.DataFrame:
    logging.info(f"Loading dsid:{dsid} dataframe from {mc_df_path} ...")
    mc_df_path = check_inputpath(mc_df_path)

    mc_files = sorted(mc_df_path.glob(f"{dsid}_sig_merged_*.gz"))
    if len(mc_files) == 0:
        raise ValueError(f"dsid {dsid} not found in {mc_df_path}")
    return joblib.load(mc_files[0])


def get_hist_proba(x, w, if_multibin=False, name="ml_score", label="ML score"):
    if if_multibin:
        _bin_edges = fit_bin_edges_proba
    else:
        _bin_edges = np.linspace(0, 1, 2)

    _hist = Hist(
        hist.axis.Variable(_bin_edges, name=name, label=label, overflow=True, underflow=True),
        storage=hist.storage.Weight(),
    )

    _hist.fill(x, weight=w)

    return _hist


def get_hist_Mjj(
    x, w, region="SR", if_multibin=False, low_edge=500, high_edge=3000, name="mjj", label="Mjj [GeV]"
):
    if if_multibin:
        _mjj_bin_edges = Mjj_bin_edges_map[region]
    else:
        _mjj_bin_edges = np.linspace(low_edge, high_edge, 2)

    _mjj_hist = Hist(
        hist.axis.Variable(_mjj_bin_edges, name=name, label=label, overflow=True, underflow=True),
        storage=hist.storage.Weight(),
    )

    _mjj_hist.fill(x, weight=w)

    return _mjj_hist


def get_hist_2D(
    x,
    y,
    w,
    x_axis_edges,
    y_axis_edges,
    x_axis_name="MT",
    y_axis_name="Mjj",
    x_axis_label="MT [GeV]",
    y_axis_label="Mjj [GeV]",
):
    _hist2d = hist.Hist(
        hist.axis.Variable(
            x_axis_edges, name=x_axis_name, label=x_axis_label, overflow=True, underflow=True
        ),
        hist.axis.Variable(
            y_axis_edges, name=y_axis_name, label=y_axis_label, overflow=True, underflow=True
        ),
        storage=hist.storage.Weight(),
    )

    _hist2d.fill(MT=x, Mjj=y, weight=w)

    return _hist2d


def get_hist_1D(x, w, x_axis_edges, x_axis_name="Mjj", x_axis_label="Mjj [GeV]"):
    _hist1d = hist.Hist(
        hist.axis.Variable(
            x_axis_edges, name=x_axis_name, label=x_axis_label, overflow=True, underflow=True
        ),
        storage=hist.storage.Weight(),
    )

    _hist1d.fill(x, weight=w)

    return _hist1d


def TH1tohist(_TH1: TH1) -> hist.Hist:
    """convert ROOT TH1 to hist.Hist

    Args:
        _TH1 (TH1): ROOT TH1

    Returns:
        hist.Hist: return hist
    """

    bin_conents = np.array([_TH1.GetBinContent(i) for i in range(0, _TH1.GetNbinsX() + 2)])
    bin_errors = np.array([_TH1.GetBinError(i) for i in range(0, _TH1.GetNbinsX() + 2)])

    bin_edges = np.array([_TH1.GetBinLowEdge(i) for i in range(1, _TH1.GetNbinsX() + 2)])

    _hist = hist.Hist(
        hist.axis.Variable(bin_edges, flow=True, name=_TH1.GetName(), label=_TH1.GetTitle()),
        storage=hist.storage.Weight(),
    )
    _hist[:] = list(zip(bin_conents[1:-1], bin_errors[1:-1]))

    _hist[hist.underflow] = (bin_conents[0], bin_errors[0])
    _hist[hist.overflow] = (bin_conents[-1], bin_errors[-1])

    return _hist


def histtoTH1(_hist: hist.Hist) -> TH1:
    _TH1 = TH1F(_hist.axes[0].name, _hist.axes[0].label, _hist.axes[0].size, _hist.axes[0].edges)
    bin_contents = _hist.values()
    # when seeting the bin error, the TH1.SetBinError() function will take the std dev
    bin_errors = np.sqrt(_hist.variances())
    for i in range(1, _hist.axes[0].size + 1):
        _TH1.SetBinContent(i, bin_contents[i - 1])
        _TH1.SetBinError(i, bin_errors[i - 1])
    return _TH1


def RebinTH1(_TH1: TH1, new_axis: Union[list, np.array, array.array]) -> TH1:
    """This function essentially calls the TH1.Rebin() function to rebin a TH1 histogram

    Args:
        _TH1 (TH1): The original TH1 histogram to be rebinned
        new_axis (Union[list, np.array, array.array]): The new bin edges

    Raises:
        ValueError: if new_axis[-1] > _TH1.GetBinLowEdge(_TH1.GetNbinsX()+1)

    Returns:
        TH1: The rebinned TH1 histogram
    """
    if new_axis[-1] > _TH1.GetBinLowEdge(_TH1.GetNbinsX() + 1):
        raise ValueError(f"Cannot rebin! {new_axis[-1]} > {_TH1.GetBinLowEdge(_TH1.GetNbinsX()+1)}")

    if not isinstance(new_axis, array.array):
        if not isinstance(new_axis, list):
            new_axis = new_axis.tolist()

        new_axis = array.array("d", new_axis)

    _TH1_rebinned = _TH1.Rebin(len(new_axis) - 1, _TH1.GetName(), new_axis)

    return _TH1_rebinned


def Rebinhist(_hist: hist.Hist, new_axis: Union[list, np.array, array.array]) -> hist.Hist:
    """Rebin a hist histogram via ROOT TH1.Rebin() function

    Args:
        _hist (hist.Hist): the original hist histogram to be rebinned
        new_axis (Union[list, np.array, array.array]): the new bin edges

    Raises:
        ValueError: if _hist.axes[0].edges[-1]

    Returns:
        hist.Hist: the rebinned hist histogram
    """

    if new_axis[-1] > _hist.axes[0].edges[-1]:
        raise ValueError(f"Cannot rebin! {new_axis[-1]} > {_hist.axes[0].edges[-1]}")

    _TH1 = histtoTH1(_hist)
    _TH1_rebinned = RebinTH1(_TH1, new_axis)
    _hist_rebinned = TH1tohist(_TH1_rebinned)

    return _hist_rebinned


def attach_MCtypes(df_decorated):
    for k, v in bkg_flattened_categories_map.items():
        df_decorated.loc[df_decorated.dsid.isin(v), "mc_type"] = k.split("_")[1]

    for k, v in bkg_flattened_subcategories_map.items():
        df_decorated.loc[df_decorated.dsid.isin(v), "mc_subtype"] = k.split("_")[1]

    for v in sig_GMH5pp_dsids:
        df_decorated.loc[df_decorated.dsid == v, "mc_type"] = "GMH5pp"
        df_decorated.loc[df_decorated.dsid == v, "mc_subtype"] = f"m{sig_dsid_mass_map[v]}"

    return df_decorated
