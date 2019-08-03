#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Author: Chris Sipola
Created: 2019-08-02
"""
from functools import reduce
from math import ceil, exp, sqrt
from operator import mul
from statistics import mean
import random


# -----------------------------------------------------------------------------
# Main functions
# -----------------------------------------------------------------------------


def rbf(x, x2, sigma):
    """Radial basis function. Sigma is the width parameter."""
    return exp(-(x - x2)**2 / (2 * sigma**2))


# def smooth(a, sigma, window=None):
#     """Smooths list of values using RBF.

#     Args:
#         a: List of floats representing time series
#         sigma: Float for width parameter for RBF

#     Returns:
#         List of smoothed values

#     >>> smooth([1, 3, 2], 1)
#     [1.7741104349160406, 2.1777941428164094, 2.2705118487351643]
#     """
#     if window is None:
#         window = ceil(3 * sigma) * 2 + 1
#     smoothed = list()
#     for i in range(window, len(a) - window):
#     # for i, x in enumerate(a):
#         low, high = i - window, i + window + 1
#         print(low, high)
#         weights = [rbf(i, j, sigma) for j in range(low, high)]
#         print(weights)
#         weighted = [w * x2 for w, x2 in zip(weights, a[high:low])]
#         print(weighted)
#         # weights = [rbf(i, j, sigma) for j in range(len(a))]
#         # weighted = [w * x2 for w, x2 in zip(weights, a)]
#         x_smooth = sum(weighted) / sum(weights)
#         smoothed.append(x_smooth)
#     return smoothed


def smooth(a, window, sigma=None):
    """Moving average."""
    return [mean(a[i:i+window]) for i in range(len(a)-window+1)]


def compute_rates(a):
    """Computes rates between consecutive values in input list.

    In the output list, 1 represents no change, 2 doubling, 0.5 halving, etc.
    Returns one fewer element than the input list.

    >>> compute_rates([1, 2, 3, 4, 5])
    [2.0, 1.5, 1.3333333333333333, 1.25]
    """
    rates = [a[i] / a[i - 1] for i in range(1, len(a))]
    return rates


def geom_mean(rates, weights):
    """Computes weighted geometric mean."""
    weighted = [r**w for r, w in zip(rates, weights)]
    gmean = reduce(mul, weighted)**(1 / sum(weights))
    return gmean


def compute_decaying_weights(n, p):
    """Computes weights that decay exponentially at the rate of p."""
    weights = [p**(n - i - 1) for i in range(n)]
    return weights


def trending_score(a, p, window=None, pseudo_count=0):
    """Computes geometric mean of growth rates, with more weight on recent obs.

    Args:
        a: List of floats for which to compute trending score
        p: Float for p parameter in decaying weights. 0 gives all weight
          to most recent observation and 1 gives equal weight to all
          observations
        sigma: Float for width parameter for RBF function used in smoothing
        pseudo_count: Float for how may values to add to each value in input
          list

    Returns:
        Float for weighted geometric mean of growth rates, where 1 represents
        no change, 2 doubling, 0.5 halving, etc.

    >>> trending_score([5, 5, 5], p=0.8)  # no trend
    1.0
    >>> trending_score([4, 5, 6], p=0.8)  # upward trend
    1.2219704337257924
    """
    if len(a) < 2:
        raise Exception('input list `a` must have more than 1 value')
    # if sigma is not None:
    #     a = smooth(a, sigma)
    if window is not None:
        a = smooth(a, window)
    if pseudo_count > 0:
        a = [x + pseudo_count for x in a]
    rates = compute_rates(a)
    weights = compute_decaying_weights(len(rates), p)
    gmean = geom_mean(rates, weights)
    return gmean


# -----------------------------------------------------------------------------
# Helper functions
# -----------------------------------------------------------------------------


def sum_of_finite_geom(r, n):
    return (1 - r**(n + 1)) / (1 - r)


def sum_of_infinite_geom(r):
    return 1 / (1 - r)


def compute_weight_frac(p, n, total_n=None):
    """Computes fraction of total weight represented by first n obs."""
    # n is inclusive in finite sum function so need to subtract 1.
    if total_n is None:
        total_weight = sum_of_infinite_geom(p)
    else:
        total_weight = sum_of_finite_geom(p, total_n - 1)
    frac = sum_of_finite_geom(p, n - 1) / total_weight
    return frac


def find_p(frac, n, total_n=None, error_bound=1e-6):
    """Finds p s.t. the first n obs make up specified fraction of total weight.

    Args:
        n: Int for number of observations to have specified fraction of weight
        frac: Float for fraction of weight of first n observations
        error_bound: Error bound of p

    Returns:
        Float p

    >>> find_p(0.5, 10)  # p such that first 10 obs make up 50% of total weight
    0.9330339431762695
    """
    low, high = 0, 1
    p = (low + high) / 2
    test_frac = compute_weight_frac(p, n, total_n)
    while high - low > error_bound:
        test_frac = compute_weight_frac(p, n, total_n)
        if test_frac > frac:
            low = p
        elif test_frac < frac:
            high = p
        else:
            break
        p = (low + high) / 2
    return p


# -----------------------------------------------------------------------------
# Sumulation
# -----------------------------------------------------------------------------


def random_walk(n):
    step_set = [-1, 0, 1]
    vals = [random.randint(0, int(2 * sqrt(n)))]
    for _ in range(1, n):
        val = vals[-1] + random.choice(step_set)
        val = max(0, val)
        vals.append(val)
    return vals


def generate_series(num_series, n):
    series = [random_walk(n) for _ in range(num_series)]
    return series


# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------


def test_weight_summations():
    n = 10
    p = 0.9
    actual = sum(compute_decaying_weights(n, p))
    expected = sum_of_finite_geom(p, n - 1)
    assert abs(actual - expected) < 1e-6


def test_find_p():
    n = 10
    frac = 0.5
    error_bound = 1e-6
    p = find_p(frac, n, error_bound=error_bound)
    actual_frac = compute_weight_frac(p, n)
    assert abs(actual_frac - frac) < 1e-3
