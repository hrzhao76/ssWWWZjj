import joblib
import uproot
import logging
from typing import Union
from pathlib import Path
import pandas as pd
import numpy as np

from utils.constants import myoutput_path
from utils.constants import sig_mass_dsid_map, bkg_flattened_categories_map, bkg_flattened_subcategories_map
from utils.constants import MT_bin_edges, Mjj_bin_edges_map
from utils.processing import get_hist_1D, get_hist_2D

from utils.constants import region_labels
from utils.processing import (
    get_merged_mc_df,
    get_individual_sig_df,
    logging_setup,
    check_inputpath,
    check_outputpath,
    attach_MCtypes,
)


def makehist_2DFit(
    wp_mass: int,
    mergedgz_output_folder: Union[str, Path],
    hist_output_folder: Union[str, Path],
    if_addCR: bool = True,
    CR_count: bool = True,
):
    mergedgz_output_folder = check_inputpath(mergedgz_output_folder)
    hist_output_folder = check_outputpath(hist_output_folder)
    output_file = hist_output_folder / f"hist_m{wp_mass}.root"

    logging_setup(verbosity=3, if_write_log=False, output_path=None)
    logging.info(f"Making hist for m{wp_mass} for 2D Fit ... ")

    # Do the SR first
    wp_dsid = sig_mass_dsid_map[wp_mass]
    region = "SR"
    df_sig_SR_file = mergedgz_output_folder / region / f"{wp_dsid}_sig_merged_{region}.gz"
    df_sig_SR_file = check_inputpath(df_sig_SR_file)
    logging.info(f"Loading {df_sig_SR_file} ... ")

    df_sig_SR = joblib.load(df_sig_SR_file)
    df_bkg_SR = get_merged_mc_df(mc_df_path=mergedgz_output_folder / region, mc_type="bkg")

    df_SR_combined = pd.concat([df_sig_SR, df_bkg_SR])
    df_SR_combined = attach_MCtypes(df_SR_combined)
    groups_mctype = df_SR_combined.groupby(["mc_subtype"])

    bkg_subtypes = [*bkg_flattened_subcategories_map]
    _mc_type_labels = [bkg_subtype.split("_")[1] for bkg_subtype in bkg_subtypes] + [f"m{wp_mass}"]

    with uproot.recreate(output_file) as f:
        logging.info(f"Writing SR hist to {output_file} ...")
        _mc_type_avail_keys = [*groups_mctype.groups.keys()]
        for _mc_type_label in _mc_type_labels:
            if _mc_type_label in _mc_type_avail_keys:
                _sub_df = groups_mctype.get_group(_mc_type_label)
                data_x, data_y, data_w = _sub_df["MT"] / 1000, _sub_df["Mjj"] / 1000, _sub_df["weight"]
            else:
                logging.warning(
                    f"Cannot find {_mc_type_label} in the dataframe for {region}, saving empty hist ... "
                )
                data_x, data_y, data_w = np.array([]), np.array([]), np.array([])

            _hist2d = get_hist_2D(
                x=data_x,
                y=data_y,
                w=data_w,
                x_axis_edges=MT_bin_edges,
                y_axis_edges=Mjj_bin_edges_map[region],
            )

            num_hists_MT = _hist2d.shape[0]
            for idx_hist_MT in range(num_hists_MT):
                f[f"SR_MTBin{idx_hist_MT+1}_Mjj_{_mc_type_label}"] = _hist2d[idx_hist_MT, :]

    # Do the CRs
    if if_addCR:
        logging.info("Now working on the CR regions ... ")
        logging.info("Adding the CR count hist ... ")

        for region in ["CRlowMjj", "CRWZ"]:
            df_sig_SR_file = mergedgz_output_folder / region / f"{wp_dsid}_sig_merged_{region}.gz"
            df_sig_SR_file = check_inputpath(df_sig_SR_file)
            logging.info(f"Loading {df_sig_SR_file} ... ")

            df_sig_SR = joblib.load(df_sig_SR_file)
            df_bkg_SR = get_merged_mc_df(mc_df_path=mergedgz_output_folder / region, mc_type="bkg")

            df_SR_combined = pd.concat([df_sig_SR, df_bkg_SR])
            df_SR_combined = attach_MCtypes(df_SR_combined)

            groups_mctype = df_SR_combined.groupby(["mc_subtype"])
            _mc_type_avail_keys = [*groups_mctype.groups.keys()]

            with uproot.update(output_file) as f:
                logging.info(f"Writing {region} hist to {output_file} ...")

                # different regions have different binning
                # CRlowMjj(2D, 8 * 1): MT_bin_edges, Mjj_bin_edges_map[region]
                # CRWZ(1D, 1 bin): Mjj_bin_edges_map["CRWZ"]
                if region == "CRlowMjj":
                    for _mc_type_label in _mc_type_labels:
                        if _mc_type_label in _mc_type_avail_keys:
                            _sub_df = groups_mctype.get_group(_mc_type_label)
                            data_x, data_y, data_w = (
                                _sub_df["MT"] / 1000,
                                _sub_df["Mjj"] / 1000,
                                _sub_df["weight"],
                            )
                        else:
                            logging.warning(
                                f"Cannot find {_mc_type_label} in the dataframe for {region}, saving empty hist ... "
                            )
                            data_x, data_y, data_w = np.array([]), np.array([]), np.array([])

                        _hist2d = get_hist_2D(
                            x=data_x,
                            y=data_y,
                            w=data_w,
                            x_axis_edges=MT_bin_edges,
                            y_axis_edges=Mjj_bin_edges_map[region],
                        )

                        num_hists_MT = _hist2d.shape[0]
                        for idx_hist_MT in range(num_hists_MT):
                            f[f"{region}_MTBin{idx_hist_MT+1}_Mjj_{_mc_type_label}"] = _hist2d[
                                idx_hist_MT, :
                            ]

                elif region == "CRWZ":
                    for _mc_type_label in _mc_type_labels:
                        if _mc_type_label in _mc_type_avail_keys:
                            _sub_df = groups_mctype.get_group(_mc_type_label)
                            data_x, data_w = _sub_df["Mjj"] / 1000, _sub_df["weight"]
                        else:
                            logging.warning(
                                f"Cannot find {_mc_type_label} in the dataframe for {region}, saving empty hist ... "
                            )
                            data_x, data_w = np.array([]), np.array([])

                        _hist1d = get_hist_1D(
                            x=data_x / 1000,
                            w=data_w,
                            x_axis_edges=Mjj_bin_edges_map[region],
                            x_axis_name="Mjj",
                            x_axis_label="Mjj [GeV]",
                        )
                        f[f"{region}_Mjj_{_mc_type_label}"] = _hist1d

    logging.info("Done!")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "wp_mass", help="mass of the H5pp", type=int, default=200, choices=list(sig_mass_dsid_map.keys())
    )
    parser.add_argument("--identifier", help="identifier of the attempt", type=str, default="dev_attempt")
    args = parser.parse_args()

    wp_mass = args.wp_mass
    identifier = args.identifier
    mergedgz_output_folder = myoutput_path / "merged_gz"
    hist_output_folder = myoutput_path / f"{identifier}/hist_output" / f"m{wp_mass}"

    makehist_2DFit(wp_mass, mergedgz_output_folder, hist_output_folder)
