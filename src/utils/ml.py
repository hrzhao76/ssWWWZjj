import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import mplhep as hep

from sklearn.metrics import roc_curve, auc
from sklearn.ensemble import GradientBoostingClassifier

from utils.constants import bin_edges_proba, bin_centers_proba


def plot_overtraining(clf, X_test, X_dev, features, y_test, y_dev, use_weights=True, clf_name="BDT"):
    hep.style.use("ATLAS")

    y_test_proba = clf.predict_proba(X_test[features])[:, 1]
    y_train_proba = clf.predict_proba(X_dev[features])[:, 1]

    if use_weights:
        X_dev_weight = X_dev["weight"]
        X_test_weight = X_test["weight"]
        title = "Overtraining test w/ event weights"
    else:
        X_dev_weight = np.ones(len(X_dev))
        X_test_weight = np.ones(len(X_test))
        title = "Overtraining test w/o event weights"

    fig, ax = plt.subplots()
    ax.hist(
        y_test_proba[y_test == 1],
        bins=bin_edges_proba,
        density=True,
        label="signal, test",
        alpha=0.5,
        weights=X_test_weight[y_test == 1],
    )
    ax.hist(
        y_test_proba[y_test == 0],
        bins=bin_edges_proba,
        density=True,
        label="bkg, test",
        alpha=0.5,
        weights=X_test_weight[y_test == 0],
    )

    y_train_sig_bin_contents, _ = np.histogram(
        y_train_proba[y_dev == 1], bins=bin_edges_proba, density=True, weights=X_dev_weight[y_dev == 1]
    )
    y_train_bkg_bin_contents, _ = np.histogram(
        y_train_proba[y_dev == 0], bins=bin_edges_proba, density=True, weights=X_dev_weight[y_dev == 0]
    )

    ax.scatter(bin_centers_proba, y_train_sig_bin_contents, label="signal, train")
    ax.scatter(bin_centers_proba, y_train_bkg_bin_contents, label="bkg, train")

    ax.legend()
    ax.set_xlabel(f"{clf_name} score")
    ax.set_ylabel("Density")
    ax.set_title(title)

    return fig, ax


def plot_roc(clf, X_test, y_test, features, use_weights=True):
    y_test_proba = clf.predict_proba(X_test[features])[:, 1]

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

    return fig, ax


def save_fig(fig, output_folder, output_name):
    fig.savefig(output_folder / output_name, bbox_inches="tight")
