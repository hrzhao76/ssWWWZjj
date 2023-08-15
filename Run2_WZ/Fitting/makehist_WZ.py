import uproot
from pathlib import Path
from typing import Union
import logging
import numpy as np
import hist

import mplhep as hep

hep.style.use(hep.style.ATLAS)

from utils.histograms import (
    TH1tohist,
    histtoTH1,
    RebinTH1,
    Rebinhist,
)
from utils.constants import myoutput_path
from utils.processing import (
    logging_setup,
    check_inputpath,
    check_outputpath,
)


sig_mass_WZ = [
    200,
    225,
    250,
    275,
    300,
    325,
    350,
    375,
    400,
    425,
    450,
    475,
    500,
    525,
    550,
    600,
    700,
    800,
    900,
    1000,
]
m_WZ_bin_edges = np.array([150, 200, 230, 270, 310, 350, 390, 480, 660, 1200])
m_WZ_bin_widths = np.diff(m_WZ_bin_edges)

hist_identifiers = ["WZEW", "WZQCD", "FakeRenorm", "VVV", "ZZ", "data"]
region_labels = ["GMMVASR", "GMMVACR", "ZZCRJJ"]
# WZEW_M_WZ_GMMVASR


def makehist_WZ(
    wp_mass: int,
    hist_output_folder: Union[str, Path],
):
    hist_output_folder = check_outputpath(hist_output_folder)
    output_file = hist_output_folder / f"hist_m{wp_mass}.root"

    logging_setup(verbosity=3, if_write_log=False, output_path=None)
    logging.info(f"Making hist for m{wp_mass} for WZ ... ")

    histogram_input = check_inputpath("/data/hrzhao/Samples/Run2_WZ/Finebin/ExportHistograms.root")
    histograms = uproot.open(histogram_input)

    hist_identifiers.insert(0, f"GMvbf{wp_mass}")
    with uproot.recreate(output_file) as f:
        logging.info(f"Writing rebined histograms to {output_file} ...")
        for region_label in region_labels:
            for hist_identifier in hist_identifiers:
                hist_name = f"{hist_identifier}_M_WZ_{region_label}"  # WZEW_M_WZ_GMMVASR
                unbined_hist = histograms[hist_name].to_hist()
                rebined_hist = Rebinhist(unbined_hist, m_WZ_bin_edges)

                # Merge the overflow bin to the last bin
                rebined_hist[-1] += rebined_hist[hist.overflow]
                rebined_hist[0] += rebined_hist[hist.underflow]
                rebined_hist[hist.overflow] = (0.0, 0.0)
                rebined_hist[hist.underflow] = (0.0, 0.0)

                # TODO: Events/ 50 GeV
                rebined_hist = rebined_hist / m_WZ_bin_widths * 50.0

                f[f"{region_label}_{hist_identifier}"] = rebined_hist


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("wp_mass", help="mass of the H5p", type=int, default=200, choices=sig_mass_WZ)
    parser.add_argument(
        "--identifier", help="identifier of the attempt", type=str, default="dev_attempt_WZ"
    )
    args = parser.parse_args()

    wp_mass = args.wp_mass
    identifier = args.identifier
    hist_output_folder = myoutput_path / f"{identifier}/hist_output" / f"m{wp_mass}"

    makehist_WZ(wp_mass, hist_output_folder)
