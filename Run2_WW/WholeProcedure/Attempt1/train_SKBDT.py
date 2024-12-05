# %%
from utils.constants import myoutput_path
from utils.constants import sig_GMH5pp_dsids, sig_dsid_mass_map, sig_mass_dsid_map
from utils.constants import region_labels
from utils.processing import (
    get_merged_mc_df,
    get_individual_sig_df,
    logging_setup,
    check_inputpath,
    check_outputpath,
)

import pandas as pd
import joblib
import numpy as np
import matplotlib.pyplot as plt
import logging

from sklearn.ensemble import GradientBoostingClassifier
from utils.ml import plot_overtraining, plot_roc, save_fig


def train_SKBDT(wp_mass, ml_output_folder):
    region = "SR"
    logging_setup(verbosity=3, if_write_log=False, output_path=None)
    logging.info(f"Training BDT for m{wp_mass} ...")
    training_features = [
        "jet0_m",
        "jet0_pt",
        "jet1_m",
        "jet1_pt",
        "MT",
        "DYjj",
        "Mll",
        "DPhillMET",
        "DEtall",
        "DYll",
    ]

    if ml_output_folder is None:
        ml_output_folder = myoutput_path / "ml_output" / "dev" / f"m{wp_mass}"

    print("check path")
    ml_output_folder = check_outputpath(ml_output_folder)
    print("get data frames")
    df_region = myoutput_path / "merged_gz_new"# / region
    bkg_df = get_merged_mc_df(df_region)
    bkg_df["target"] = 0

    wp_dsid = sig_mass_dsid_map[wp_mass]
    sig_df = get_individual_sig_df(df_region, wp_dsid)
    sig_df["target"] = 1

    # Combine the two dataframes and split into X and y using sklearn
    combined_df = pd.concat([bkg_df, sig_df], ignore_index=True)
    combined_df["ml_score"] = np.nan
    combined_df = combined_df.sample(frac=1).reset_index(drop=True)

    # k-fold cross validation by index and modulos
    n_kfold = 5

    combined_df["kfold"] = combined_df.index % n_kfold
    print("train")
    # %%
    # split into X and y based on kfold
    for idx_k in range(n_kfold):
        logging.info(f"Training fold {idx_k} ...")
        X_train = combined_df[combined_df["kfold"] != idx_k]
        X_test = combined_df[combined_df["kfold"] == idx_k]
        y_train = X_train["target"]
        y_test = X_test["target"]

        # ignore the negative weights in the training set
        idx_positive_weights = X_train["weight"] > 0
        X_train = X_train.loc[idx_positive_weights]
        y_train = y_train.loc[idx_positive_weights]

        # adjust the weights in the training set
        sig_class_weight = X_train.loc[X_train["target"] == 1, "weight"].sum()
        bkg_class_weight = X_train.loc[X_train["target"] == 0, "weight"].sum()

        X_train.loc[X_train["target"] == 1, "training_weight"] = (
            X_train.loc[X_train["target"] == 1, "weight"] / sig_class_weight
        )
        X_train.loc[X_train["target"] == 0, "training_weight"] = (
            X_train.loc[X_train["target"] == 0, "weight"] / bkg_class_weight
        )

        bdt = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=3,
            validation_fraction=0.1,
            n_iter_no_change=10,
            tol=0.01,
            random_state=0,
            verbose=1,
        )

        bdt.fit(X_train[training_features], y_train, sample_weight=X_train["training_weight"])

        fig_ot, ax_ot = plot_overtraining(
            clf=bdt, X_dev=X_train, y_dev=y_train, X_test=X_test, y_test=y_test, features=training_features
        )

        fig_roc, ax_roc = plot_roc(bdt, X_test, y_test, training_features)

        # store the clf scores for the test set based on the kfold
        combined_df.loc[combined_df["kfold"] == idx_k, "ml_score"] = bdt.predict_proba(
            X_test[training_features]
        )[:, 1]

        # save the model
        joblib.dump(bdt, ml_output_folder / f"bdt_m{wp_mass}_k{idx_k}.gz")

        # save the plots
        save_fig(fig_ot, ml_output_folder, f"ot_m{wp_mass}_k{idx_k}.png")
        save_fig(fig_roc, ml_output_folder, f"roc_m{wp_mass}_k{idx_k}.png")

        plt.close("all")

    # save the combined dataframe for later use, e.g. histograms
    joblib.dump(combined_df, ml_output_folder / f"df_m{wp_mass}_combined.gz")

    logging.info("Done training!")
    return combined_df


if __name__ == "__main__":
    print("start program")
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "wp_mass", help="mass of the H5pp", type=int, default=200, choices=list(sig_mass_dsid_map.keys())
    )
    parser.add_argument("--identifier", help="identifier of the attempt", type=str, default="dev_attempt")
    args = parser.parse_args()

    wp_mass = args.wp_mass
    identifier = args.identifier
    ml_output_folder = myoutput_path / f"{identifier}/ml_output" / f"m{wp_mass}"
    print("run training")
    combined_df = train_SKBDT(wp_mass, ml_output_folder)
