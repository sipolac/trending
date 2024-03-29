#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Author: Chris Sipola
Created: 2019-08-03

Tests for trending functions.
"""
from trending import trending


def test_weight_summations():
    n = 10
    p = 0.9
    actual = sum(trending._decaying_weights(n, p))
    expected = trending._geom_sum(p, n - 1)
    assert abs(actual - expected) < 1e-6


def test_find_r():
    n = 10
    frac = 0.5
    error_bound = 1e-6
    p = trending.find_r(frac, n, error_bound=error_bound)
    actual_frac = trending.compute_weight_frac(p, n)
    assert abs(actual_frac - frac) < 1e-3

    assert trending.find_r(0.5, 5, 10) == 1
    assert trending.find_r(0.5, 5, 10) == 1
    assert trending.find_r(0.5, 5, 11) < 1
    assert trending.find_r(0.7, 7, 10) == 1
    assert trending.find_r(0.7, 7, 11) < 1
