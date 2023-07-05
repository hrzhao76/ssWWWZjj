from utils.constants import (
    sig_GMH5pp_dsids,
    bkg_EWKWW_dsids,
    bkg_QCDWW_dsids,
    bkg_INTWW_dsids,
    bkg_QCDWZ_dsids,
    bkg_EWKWZ_dsids,
)
from utils.processing import merge_samples, merge_ddFakes_samples

# TODO: Change the naming convention of the SM WW samples
for dsid in [sig_GMH5pp_dsids, bkg_EWKWW_dsids, bkg_QCDWW_dsids, bkg_INTWW_dsids]:
    merge_samples(dsid, "sig", logging_verbosity=3)

for dsid in [bkg_QCDWZ_dsids]:
    merge_samples(dsid, "bkg", logging_verbosity=3)

merge_samples(bkg_EWKWZ_dsids, "bkg", is_multiple=True, logging_verbosity=3)

merge_ddFakes_samples()
