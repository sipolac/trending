#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Author: Chris Sipola
Created: 2019-08-02

Methods for determining trending-ness.

Some notes on "notation":
> `a` is used to represent a series/list/array of interest, in the style of
  numpy. However, within the project, `a` treated as a list since I didn't
  want a numpy dependency. In practice there should be no issue using a numpy
  array or a pandas series.
> `growth` (or `g` if shortened) represents proportional growth. E.g., from
  2 to 3, growth is 3 / 2 = 1.5.
> `rate` (or `r` if shortened) represents rate in the sense of a geometric
  series: http://mathworld.wolfram.com/GeometricSeries.html
> `n` means the number of observations. Adjustments may need to be made based
  on how `n` is used. For example, the typical index for the sum of a finite
  geometric series goes from 0 to n, meaning there are actually n + 1
  observations. So 1 must be subtracted before using this formula.
"""
from functools import reduce
from operator import mul


def _compute_growth(a):
    """Computes proportional growth between consecutive values in input list.

    >>> _compute_growth([1, 2, 3, 4, 5])
    [2.0, 1.5, 1.3333333333333333, 1.25]
    """
    growth_list = [a[i] / a[i - 1] for i in range(1, len(a))]
    return growth_list


def _geom_mean(growth_list, weights):
    """Computes weighted geometric mean."""
    weighted = [g**w for g, w in zip(growth_list, weights)]
    gmean = reduce(mul, weighted)**(1 / sum(weights))
    return gmean


def _decaying_weights(n, r):
    """Computes weights that decay geometrically at rate r."""
    weights = [r**(n - i - 1) for i in range(n)]
    return weights


def recent_growth(a, r):
    """Computes geometric mean of growth rates, with more weight on recent obs.

    Args:
        a: List of floats for which to compute recent growth
        r: Float for decay rate. 0 gives all weight to most recent observation
          and 1 gives equal weight to all observations

    Returns:
        Float for weighted geometric mean of growth rates

    >>> recent_growth([5, 5, 5], r=0.8)  # no trend
    1.0
    >>> recent_growth([4, 5, 6], r=0.8)  # upward trend
    1.2219704337257924
    """
    if len(a) < 2:
        raise Exception('input list `a` must have more than 1 value')
    growth_list = _compute_growth(a)
    weights = _decaying_weights(len(growth_list), r)
    gmean = _geom_mean(growth_list, weights)
    return gmean


def _geom_sum(r, n):
    """Computes sum of geometric series.

    Use n=float('inf') for infinite series.
    """
    return (1 - r**(n + 1)) / (1 - r)


def compute_weight_frac(r, n, total_n=None):
    """Computes fraction of total weight represented by last n obs.

    That is, it computes:
      [sum of weights of most recent n observations] divided by [sum of
      weights of *all* observations], where *all* is either all actual
      observations in the time series, or a theoretically infinite number
      of observations.

    Args:
        r: Float for decay rate
        n: Int for number of most recent observations
        total_n: Float for total number of observations. If None, will use
          inifite geometric sum instead

    Returns:
        Float for fraction
    """
    # n is inclusive in finite sum function so need to subtract 1.
    if total_n is None:
        total_n = float('inf')
    frac = _geom_sum(r, n - 1) / _geom_sum(r, total_n - 1)
    return frac


def find_r(frac, n, total_n=None, error_bound=1e-6):
    """Finds r s.t. the last n obs make up specified fraction of total weight.

    Args:
        frac: Float for fraction of total weight represented by last n
          observations
        n: Int for number of most recent observations
        total_n: Float for total number of observations. If None, will use
          inifite geometric sum instead
        error_bound: Error bound of r

    Returns:
        Float for decay rate

    >>> find_p(0.5, 10)  # r such that last 10 obs make up 50% of total weight
    0.9330339431762695
    """
    low, high = 0, 1
    r = (low + high) / 2
    test_frac = compute_weight_frac(r, n, total_n)
    while high - low > error_bound:
        test_frac = compute_weight_frac(r, n, total_n)
        if test_frac > frac:
            low = r
        elif test_frac < frac:
            high = r
        else:
            break
        r = (low + high) / 2
    return r
