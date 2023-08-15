import hist
from ROOT import TH1, TH1F
import numpy as np
from typing import Union, Literal
import array


def TH1tohist(_TH1: TH1) -> hist.Hist:
    """convert ROOT TH1 to hist.Hist

    Args:
        _TH1 (TH1): ROOT TH1

    Returns:
        hist.Hist: return hist
    """

    bin_conents = np.array([_TH1.GetBinContent(i) for i in range(0, _TH1.GetNbinsX() + 2)])
    bin_errors = np.array([_TH1.GetBinError(i) for i in range(0, _TH1.GetNbinsX() + 2)])

    bin_edges = np.array([_TH1.GetBinLowEdge(i) for i in range(1, _TH1.GetNbinsX() + 2)])

    _hist = hist.Hist(
        hist.axis.Variable(bin_edges, flow=True, name=_TH1.GetName(), label=_TH1.GetTitle()),
        storage=hist.storage.Weight(),
    )
    _hist[:] = list(zip(bin_conents[1:-1], bin_errors[1:-1]))

    _hist[hist.underflow] = (bin_conents[0], bin_errors[0])
    _hist[hist.overflow] = (bin_conents[-1], bin_errors[-1])

    return _hist


def histtoTH1(_hist: hist.Hist) -> TH1:
    _TH1 = TH1F(_hist.axes[0].name, _hist.axes[0].label, _hist.axes[0].size, _hist.axes[0].edges)
    bin_contents = _hist.values()
    # when seeting the bin error, the TH1.SetBinError() function will take the std dev
    bin_errors = np.sqrt(_hist.variances())
    for i in range(1, _hist.axes[0].size + 1):
        _TH1.SetBinContent(i, bin_contents[i - 1])
        _TH1.SetBinError(i, bin_errors[i - 1])
    return _TH1


def RebinTH1(_TH1: TH1, new_axis: Union[list, np.array, array.array]) -> TH1:
    """This function essentially calls the TH1.Rebin() function to rebin a TH1 histogram

    Args:
        _TH1 (TH1): The original TH1 histogram to be rebinned
        new_axis (Union[list, np.array, array.array]): The new bin edges

    Raises:
        ValueError: if new_axis[-1] > _TH1.GetBinLowEdge(_TH1.GetNbinsX()+1)

    Returns:
        TH1: The rebinned TH1 histogram
    """
    if new_axis[-1] > _TH1.GetBinLowEdge(_TH1.GetNbinsX() + 1):
        raise ValueError(f"Cannot rebin! {new_axis[-1]} > {_TH1.GetBinLowEdge(_TH1.GetNbinsX()+1)}")

    if not isinstance(new_axis, array.array):
        if not isinstance(new_axis, list):
            new_axis = new_axis.tolist()

        new_axis = array.array("d", new_axis)

    _TH1_rebinned = _TH1.Rebin(len(new_axis) - 1, _TH1.GetName(), new_axis)

    return _TH1_rebinned


def Rebinhist(_hist: hist.Hist, new_axis: Union[list, np.array, array.array]) -> hist.Hist:
    """Rebin a hist histogram via ROOT TH1.Rebin() function

    Args:
        _hist (hist.Hist): the original hist histogram to be rebinned
        new_axis (Union[list, np.array, array.array]): the new bin edges

    Raises:
        ValueError: if _hist.axes[0].edges[-1]

    Returns:
        hist.Hist: the rebinned hist histogram
    """

    if new_axis[-1] > _hist.axes[0].edges[-1]:
        raise ValueError(f"Cannot rebin! {new_axis[-1]} > {_hist.axes[0].edges[-1]}")

    _TH1 = histtoTH1(_hist)
    _TH1_rebinned = RebinTH1(_TH1, new_axis)
    _hist_rebinned = TH1tohist(_TH1_rebinned)

    return _hist_rebinned
