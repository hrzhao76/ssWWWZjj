import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc


def plot_overtraining(bdt, X_test, X_dev, features, y_test, y_dev, output_folder, wp_mass, kfold):
    y_test_proba = bdt.predict_proba(X_test[features])[:, 1]
    y_train_proba = bdt.predict_proba(X_dev[features])[:, 1]

    bin_edges_proba = np.linspace(0, 1, 51)
    bin_centers_proba = (bin_edges_proba[1:] + bin_edges_proba[:-1]) / 2

    fig, ax = plt.subplots()
    ax.hist(
        y_test_proba[y_test == 1],
        bins=bin_edges_proba,
        density=True,
        label="signal, test",
        alpha=0.5,
        weights=X_test["weight"][y_test == 1],
    )
    ax.hist(
        y_test_proba[y_test == 0],
        bins=bin_edges_proba,
        density=True,
        label="bkg, test",
        alpha=0.5,
        weights=X_test["weight"][y_test == 0],
    )

    # ax.hist(y_train_proba[y_train==1], bins=bin_edges_proba, density=True, label="train, signal", alpha=0.5)
    # ax.hist(y_train_proba[y_train==0], bins=bin_edges_proba, density=True, label="train, bkg", alpha=0.5)

    y_train_sig_bin_contents, _ = np.histogram(
        y_train_proba[y_dev == 1], bins=bin_edges_proba, density=True, weights=X_dev["weight"][y_dev == 1]
    )
    y_train_bkg_bin_contents, _ = np.histogram(
        y_train_proba[y_dev == 0], bins=bin_edges_proba, density=True, weights=X_dev["weight"][y_dev == 0]
    )

    ax.scatter(bin_centers_proba, y_train_sig_bin_contents, label="signal, train")
    ax.scatter(bin_centers_proba, y_train_bkg_bin_contents, label="bkg, train")

    ax.legend()
    ax.set_xlabel("BDT proba")
    ax.set_ylabel("Density")
    ax.set_title("Overtraining test w/ event weights")
    plt.show()

    plt.savefig(
        output_folder / f"Overtraining_test_m{wp_mass}_w_weights_kfold{kfold}.png", bbox_inches="tight"
    )


def plot_roc(bdt, X_test, y_test, features, output_folder, wp_mass, kfold, use_weights=True):
    # fpr, tpr, _ = roc_curve(y_test, y_test_proba, sample_weight=X_test['weight'])
    y_test_proba = bdt.predict_proba(X_test[features])[:, 1]

    fig, ax = plt.subplots()
    if use_weights:
        fpr, tpr, thresholds = roc_curve(y_test, y_test_proba, sample_weight=X_test["weight"])
        # sort the fpr and tpr so that the thresholds are increasing
        # and we don't get weird lines in the ROC curve
        sort_idx = np.argsort(fpr)
        fpr = fpr[sort_idx]
        tpr = tpr[sort_idx]
    else:
        fpr, tpr, thresholds = roc_curve(y_test, y_test_proba)

    ax.plot(fpr, tpr, label=f"ROC curve (area = {auc(fpr, tpr):.3f})")
    ax.plot([0, 1], [0, 1], "k--", label="Randomly guess")
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, 1.0)
    ax.legend(loc="best")
    if use_weights:
        ax.set_title("ROC w/ event weights")
    else:
        ax.set_title("ROC w/o event weights")

    plt.show()
    if use_weights:
        plt.savefig(output_folder / f"ROC_m{wp_mass}_w_weights_kfold{kfold}.png", bbox_inches="tight")
    else:
        plt.savefig(output_folder / f"ROC_m{wp_mass}_wo_weights_kfold{kfold}.png", bbox_inches="tight")
