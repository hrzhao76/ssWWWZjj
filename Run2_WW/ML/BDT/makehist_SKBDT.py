import joblib
import uproot
import logging

from utils.constants import myoutput_path
from utils.constants import sig_mass_dsid_map, bkg_flattened_categories_map
from utils.processing import logging_setup, get_hist_proba, check_inputpath, check_outputpath


def makehist_SKBDT(wp_mass, ml_output_folder, hist_output_folder):
    ml_output_folder = check_inputpath(ml_output_folder)
    hist_output_folder = check_outputpath(hist_output_folder)
    logging_setup(verbosity=3, if_write_log=False, output_path=None)
    logging.info(f"Making hist for m{wp_mass} ... ")

    df_file = ml_output_folder / f"df_m{wp_mass}_combined.gz"
    df_file = check_inputpath(df_file)
    logging.info(f"Loading {df_file} ... ")

    df_combined = joblib.load(df_file)
    df_combined["mc_type"] = "-"

    for k, v in sig_mass_dsid_map.items():
        df_combined.loc[df_combined.dsid.isin([v]), "mc_type"] = f"H5pp_m{k}"

    for k, v in bkg_flattened_categories_map.items():
        df_combined.loc[df_combined.dsid.isin(v), "mc_type"] = k.split("_")[1]

    groups_mctype = df_combined.groupby(["mc_type"])
    output_file = hist_output_folder / f"hist_m{wp_mass}.root"
    with uproot.recreate(output_file) as f:
        for k in groups_mctype.groups.keys():
            hist_mctype = get_hist_proba(groups_mctype.get_group(k))
            f[k] = hist_mctype

    logging.info(f"Saved to {output_file.absolute()}")
    logging.info("Done!")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "wp_mass", help="mass of the H5pp", type=int, default=200, choices=list(sig_mass_dsid_map.keys())
    )
    parser.add_argument("--ml-output-folder", help="folder contains the ml output", type=str, default="dev")
    parser.add_argument(
        "--hist-output-folder",
        help="folder to store the hist output. if not specified, will be the same name as {ml-output-folder}",
        type=str,
        default=None,
    )
    args = parser.parse_args()

    wp_mass = args.wp_mass
    ml_output_folder = myoutput_path / "ml_output" / args.ml_output_folder / f"m{wp_mass}"
    if args.hist_output_folder is None:
        hist_output_folder = myoutput_path / "hist_output" / args.ml_output_folder / f"m{wp_mass}"
    else:
        hist_output_folder = myoutput_path / "hist_output" / args.hist_output_folder / f"m{wp_mass}"

    makehist_SKBDT(wp_mass, ml_output_folder, hist_output_folder)
