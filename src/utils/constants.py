from pathlib import Path
import numpy as np
import itertools

work_path = Path("/home/hrzhao/Projects/ssWWWZjj/")
ntuple_path = Path("/data/hrzhao/Samples/ssWWWZ_run3/Ntuples/")
myoutput_path = Path("/afs/cern.ch/user/o/owyoung/eos/charged_higgs_analysis/MyOutputs/")

### Run 2 Fit Bin Definitions ###
Mjj_bin_edges_SR = np.array([500.0, 850.0, 1450.0, 2100.0, 2550.0, 3000.0], dtype=float)
Mjj_bin_centers_SR = (Mjj_bin_edges_SR[1:] + Mjj_bin_edges_SR[:-1]) / 2
Mjj_bin_edges_CRlowMjj = np.array([200.0, 500.0], dtype=float)
Mjj_bin_centers_CRlowMjj = (Mjj_bin_edges_CRlowMjj[1:] + Mjj_bin_edges_CRlowMjj[:-1]) / 2

MT_bin_edges = np.array([0, 100, 180, 230, 280, 350, 500, 800, 1500], dtype=float)
MT_bin_centers = (MT_bin_edges[1:] + MT_bin_edges[:-1]) / 2

### Run 2 MC Samples ###
ttree_prefix = "HWWTree_"
ttree_channels = ["em", "me", "ee", "mm"]
period_labels = np.array(["a", "d", "e"])
region_labels = np.array(["SR", "CRlowMjj", "CRWZ"])

Mjj_bin_edges_map = dict.fromkeys(region_labels)
Mjj_bin_edges_map["SR"] = Mjj_bin_edges_SR
Mjj_bin_edges_map["CRlowMjj"] = Mjj_bin_edges_CRlowMjj
Mjj_bin_edges_map["CRWZ"] = np.linspace(200, 3000, 2)

### Run 2 signal samples ###
sig_mass_points1 = np.linspace(200, 550, int((550 - 200) / 25 + 1), dtype=int)
sig_mass_points2 = np.linspace(600, 1000, int((1000 - 600) / 100 + 1), dtype=int)
sig_mass_points3 = np.array([1500, 2000, 3000], dtype=int)
sig_mass_points = np.concatenate([sig_mass_points1, sig_mass_points2, sig_mass_points3])

sig_mass_dsid_map = dict.fromkeys(sig_mass_points)
sig_mass_dsid_start = 525925 #511727 
for mass_idx, masss_point in enumerate(sig_mass_points):
    sig_mass_dsid_map[masss_point] = sig_mass_dsid_start + mass_idx
sig_dsid_mass_map = dict(zip(sig_mass_dsid_map.values(), sig_mass_dsid_map.keys()))

sig_GMH5pp_dsids = np.array(list(sig_mass_dsid_map.values()), dtype=int)

bkg_EWKWW_dsids = np.array([500989], dtype=int)
bkg_QCDWW_dsids = np.array([500990], dtype=int)
bkg_INTWW_dsids = np.array([500991], dtype=int)

bkg_QCDWZ_dsids = np.array([364253], dtype=int)
bkg_EWKWZ_dsids = np.array([364739, 364740, 364741, 364742], dtype=int)

bkg_ddFakes_dsid = np.array([-1], dtype=int)

bkg_categories_map = {
    "bkg_SMWW_dsids": [bkg_EWKWW_dsids, bkg_QCDWW_dsids, bkg_INTWW_dsids],
    "bkg_SMWZ_dsids": [bkg_EWKWZ_dsids, bkg_QCDWZ_dsids],
    "bkg_NonPrompt_dsid": [bkg_ddFakes_dsid],
}

bkg_flattened_categories_map = {
    key: list(itertools.chain.from_iterable(value)) for key, value in bkg_categories_map.items()
}

bkg_flattened_subcategories_map = {
    "bkg_EWKWW_dsids": bkg_EWKWW_dsids,
    "bkg_QCDWW_dsids": bkg_QCDWW_dsids,
    "bkg_INTWW_dsids": bkg_INTWW_dsids,
    "bkg_EWKWZ_dsids": bkg_EWKWZ_dsids,
    "bkg_QCDWZ_dsids": bkg_QCDWZ_dsids,
    "bkg_ddFakes_dsid": bkg_ddFakes_dsid,
}

# bkg_flattened_subcategories_map = {
#     key: list(itertools.chain.from_iterable(value)) for key, value in bkg_subcategories_map.items()
# }

### Run 2 background samples ###

bin_edges_proba = np.linspace(0, 1, 51)
bin_centers_proba = (bin_edges_proba[1:] + bin_edges_proba[:-1]) / 2

fit_bin_edges_proba = np.linspace(0, 1, 11)
fit_bin_centers_proba = (fit_bin_edges_proba[1:] + fit_bin_edges_proba[:-1]) / 2

fit_bin_edges_mwz = np.array([150, 200, 230, 270, 310, 350, 390, 480, 660, 1200])
fit_bin_centers_mwz = (fit_bin_edges_mwz[1:] + fit_bin_edges_mwz[:-1]) / 2


ordered_mass = np.array(
    [
        "m200",
        "m225",
        "m250",
        "m275",
        "m300",
        "m325",
        "m350",
        "m375",
        "m400",
        "m425",
        "m450",
        "m475",
        "m500",
        "m525",
        "m550",
        "m600",
        "m700",
        "m800",
        "m900",
        "m1000",
        "m1500",
        "m2000",
        "m3000",
    ],
    dtype=object,
)
