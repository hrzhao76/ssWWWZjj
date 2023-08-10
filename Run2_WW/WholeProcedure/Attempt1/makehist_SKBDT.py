import joblib
import uproot
import logging
from typing import Union
from pathlib import Path
import pandas as pd
import numpy as np

from utils.constants import myoutput_path
from utils.constants import sig_mass_dsid_map, bkg_flattened_categories_map, bkg_flattened_subcategories_map

from utils.constants import region_labels
from utils.processing import (
    get_merged_mc_df,
    get_individual_sig_df,
    get_hist_proba,
    logging_setup,
    check_inputpath,
    check_outputpath,
    attach_MCtypes,
)


def makehist_SKBDT(
    wp_mass: int,
    ml_output_folder: Union[str, Path],
    hist_output_folder: Union[str, Path],
    if_addCR: bool = True,
    CR_count: bool = True,
):
    ml_output_folder = check_inputpath(ml_output_folder)
    hist_output_folder = check_outputpath(hist_output_folder)
    logging_setup(verbosity=3, if_write_log=False, output_path=None)
    logging.info(f"Making hist for m{wp_mass} ... ")

    df_SR_file = ml_output_folder / f"df_m{wp_mass}_combined.gz"
    df_SR_file = check_inputpath(df_SR_file)
    logging.info(f"Loading {df_SR_file} ... ")

    df_SR_combined = joblib.load(df_SR_file)
    df_SR_combined = attach_MCtypes(df_SR_combined)

    groups_mctype = df_SR_combined.groupby(["mc_subtype"])
    output_file = hist_output_folder / f"hist_m{wp_mass}.root"
    bkg_subtypes = [*bkg_flattened_subcategories_map]
    _mc_type_lables = [bkg_subtype.split("_")[1] for bkg_subtype in bkg_subtypes] + [f"m{wp_mass}"]

    with uproot.recreate(output_file) as f:
        for _mc_type_lable in _mc_type_lables:
            if _mc_type_lable in groups_mctype.groups.keys():
                _sub_df = groups_mctype.get_group(_mc_type_lable)
                hist_mctype = get_hist_proba(x=_sub_df["ml_score"], w=_sub_df["weight"], if_multibin=True)

            else:
                logging.warning(f"Cannot find {_mc_type_lable} in the dataframe, saving empty hist ... ")
                f[f"SR_{_mc_type_lable}"] = get_hist_proba(x=np.array([]), w=np.array([]), if_multibin=True)

            f[f"SR_{_mc_type_lable}"] = hist_mctype

    logging.info(f"Saved to {output_file.absolute()}")
    if if_addCR:
        logging.info("Now working on the CR regions ... ")
        # open the CR file
        if CR_count:
            logging.info("Adding the CR count hist ... ")

            for region in ["CRlowMjj", "CRWZ"]:
                df_region = myoutput_path / "merged_gz" / region
                all_bkg_CR_df = get_merged_mc_df(df_region)

                sig_CR_filename = f"{sig_mass_dsid_map[wp_mass]}_sig_merged_{region}.gz"
                sig_CR_df = joblib.load(df_region / sig_CR_filename)
                all_mc_df = pd.concat([all_bkg_CR_df, sig_CR_df])
                all_mc_df = attach_MCtypes(all_mc_df)

                groups_mctype = all_mc_df.groupby(["mc_subtype"])

                with uproot.update(output_file) as f:
                    # same as the SR
                    for _mc_type_lable in _mc_type_lables:
                        if _mc_type_lable in groups_mctype.groups.keys():
                            _sub_df = groups_mctype.get_group(_mc_type_lable)
                            hist_mctype = get_hist_proba(
                                x=0.5 * np.ones(len(_sub_df)), w=_sub_df["weight"], if_multibin=False
                            )
                        else:
                            logging.warning(
                                f"Cannot find {_mc_type_lable} in the dataframe, saving empty hist ... "
                            )

                            hist_mctype = get_hist_proba(x=np.array([]), w=np.array([]), if_multibin=False)
                        f[f"{region}_{_mc_type_lable}"] = hist_mctype

        else:
            logging.info("Adding the CR bdt hist ... ")
            raise NotImplementedError("Not implemented yet ... ")

    logging.info("Done!")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "wp_mass", help="mass of the H5pp", type=int, default=200, choices=list(sig_mass_dsid_map.keys())
    )
    parser.add_argument("--ml-output-folder", help="folder contains the ml output", type=str, default="dev")
    parser.add_argument("--identifier", help="identifier of the attempt", type=str, default="dev_attempt")
    args = parser.parse_args()

    wp_mass = args.wp_mass
    identifier = args.identifier
    ml_output_folder = myoutput_path / f"{identifier}/ml_output" / f"m{wp_mass}"
    hist_output_folder = myoutput_path / f"{identifier}/hist_output" / f"m{wp_mass}"

    makehist_SKBDT(wp_mass, ml_output_folder, hist_output_folder)
