from pathlib import Path
import numpy as np

work_path = Path("/home/hrzhao/Projects/ssWWWZjj/")
ntuple_path = Path("/data/hrzhao/Samples/ssWWWZ_run3/Ntuples/")
myoutput_path = Path("/data/hrzhao/Samples/ssWWWZ_run3/MyOutputs/")

### Run 2 Fit Bin Definitions ###
Mjj_bin_edges = np.array([500.0, 850.0, 1450.0, 2100.0, 2550.0, 3000.0], dtype=float)
Mjj_bin_centers = (Mjj_bin_edges[1:] + Mjj_bin_edges[:-1]) / 2
MT_bin_edges = np.array([0, 100, 180, 230, 280, 350, 500, 800, 1500], dtype=float)
MT_bin_centers = (MT_bin_edges[1:] + MT_bin_edges[:-1]) / 2

### Run 2 MC Samples ###
ttree_prefix = "HWWTree_"
ttree_channels = ["em", "me", "ee", "mm"]
period_labels = np.array(["a", "d", "e"])
region_labels = np.array(["SR", "CRlowMjj", "CRWZ"])

### Run 2 signal samples ###
sig_mass_points1 = np.linspace(200, 550, int((550 - 200) / 25 + 1), dtype=int)
sig_mass_points2 = np.linspace(600, 1000, int((1000 - 600) / 100 + 1), dtype=int)
sig_mass_points3 = np.array([1500, 2000, 3000], dtype=int)
sig_mass_points = np.concatenate([sig_mass_points1, sig_mass_points2, sig_mass_points3])

sig_mass_dsid_map = dict.fromkeys(sig_mass_points)
sig_mass_dsid_start = 511727
for mass_idx, masss_point in enumerate(sig_mass_points):
    sig_mass_dsid_map[masss_point] = sig_mass_dsid_start + mass_idx
dsid_sig_mass_map = dict(zip(sig_mass_dsid_map.values(), sig_mass_dsid_map.keys()))

sig_GMH5pp_dsids = np.array(list(sig_mass_dsid_map.values()), dtype=int)

bkg_EWKWW_dsids = np.array([500986], dtype=int)
bkg_QCDWW_dsids = np.array([500987], dtype=int)
bkg_INTWW_dsids = np.array([500988], dtype=int)

bkg_QCDWZ_dsids = np.array([364253], dtype=int)
bkg_EWKWZ_dsids = np.array([364739, 364740, 364741, 364742], dtype=int)


bkg_ddFakes_dsid = np.array([-1], dtype=int)
### Run 2 background samples ###
