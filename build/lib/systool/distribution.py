# -*- coding: utf-8 -*-


# -------------------------------------------------------------------------------------------------------------------- #
# Name:       CalcDistribution
# Purpose:    Utilities for various calculations of different types of trip distribution models.
#             a) calc_fratar : Calculates a Fratar/IPF on a seed matrix given row and column (P and A) totals
#             b) calc_singly_constrained : Calculates a singly constrained trip distribution for given P/A vectors and a
#                friction factor matrix
#             c) calc_doubly_constrained : Calculates a doubly constrained trip distribution for given P/A vectors and a
#                friction factor matrix (P and A should be balanced before usage, if not then A is scaled to P)
#             d) calc_multi_fratar : Applies fratar model to given set of trip matrices with multiple target production
#                vectors and one attr_action vector
#             e) calc_multi_distribute : Applies gravity model to a given set of frication matrices with multiple
#                production vectors and one target attr_action vector
#
#              **All input vectors are expected to be numpy arrays
#
# Author:      Chetan Joshi, Portland OR
# Dependencies:numpy [www.numpy.org]
# Created:     5/14/2015
#
# Copyright:   (c) Chetan Joshi 2015
# Licence:     Permission is hereby granted, free of charge, to any person obtaining a copy
#              of this software and associated documentation files (the "Software"), to deal
#              in the Software without restriction, including without limitation the rights
#              to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#              copies of the Software, and to permit persons to whom the Software is
#              furnished to do so, subject to the following conditions:
#
#              The above copyright notice and this permission notice shall be included in all
#              copies or substantial portions of the Software.
#
#              THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#              IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#              FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#              AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#              LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#              OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#              SOFTWARE.
# -------------------------------------------------------------------------------------------------------------------- #
import numpy


def calc_fratar(prod_a, attr_a, trips_1, max_iter=10, print_balance=False):
    """
    Calculates fratar trip distribution
       prod_a = Production target as array
       attr_a = attr_action target as array
       trips_1 = Seed trip table for fratar
       max_iter (optional) = maximum iterations, default is 10
       Returns fratared trip table
    """
    # print('Checking production, attr_action balancing:')
    sum_p = sum(prod_a)
    sum_a = sum(attr_a)
    # print('Production: ', sum_p)
    # print('attr_action: ', sum_a)
    if sum_p != sum_a:
        if print_balance:
            print('Productions and attr_actions do not balance, attr_actions will be scaled to productions!')
        attr_a = attr_a*(sum_p/sum_a)
    else:
        if print_balance:
            print('Production, attr_action balancing OK.')
    # Run 2D balancing --->
    for balIter in range(0, max_iter):
        computed_productions = trips_1.sum(1)
        computed_productions[computed_productions == 0] = 1
        orig_fac = (prod_a/computed_productions)
        trips_1 = trips_1*orig_fac[:, numpy.newaxis]

        computedattr_actions = trips_1.sum(0)
        computedattr_actions[computedattr_actions == 0] = 1
        dest_fac = (attr_a/computedattr_actions)
        trips_1 = trips_1*dest_fac
    return trips_1


def calc_singly_constrained(prod_a, attr_a, f):
    """
    Calculates singly constrained trip distribution for a given friction factor matrix
    prod_a = Production array
    attr_a = attr_action array
    f = Friction factor matrix
    Resutrns trip table
    """
    sum_ajfij = (attr_a*f).sum(1)
    sum_ajfij[sum_ajfij == 0] = 0.0001
    return prod_a*(attr_a*f).transpose()/sum_ajfij


def calc_doubly_constrained(prod_a, attr_a, f, max_iter=10, verbose=False):
    """
    Calculates doubly constrained trip distribution for a given friction factor matrix
    prod_a = Production array
    attr_a = attr_action array
    f = Friction factor matrix
    max_iter (optional) = maximum iterations, default is 10
    Returns trip table
    """
    worse = f.min()
    f = f / worse

    trips_1 = numpy.zeros((len(prod_a), len(prod_a)))
    if verbose:
        print('Checking production, attr_action balancing:')
    sum_p = sum(prod_a)
    sum_a = sum(attr_a)
    if verbose:
        print('Production: ', sum_p)
        print('attr_action: ', sum_a)
    if sum_p != sum_a:
        if verbose:
            print('Productions and attr_actions do not balance, attr_actions will be scaled to productions!')
        attr_a = attr_a*(sum_p/sum_a)
        attr_t = attr_a.copy()
        prod_t = prod_a.copy()
    else:
        if verbose:
            print('Production, attr_action balancing OK.')
        attr_t = attr_a.copy()
        prod_t = prod_a.copy()

    for balIter in range(0, max_iter):
        for i in range(0, len(prod_a)):
            trips_1[i, :] = prod_a[i]*attr_a*f[i, :]/max(0.000001, sum(attr_a * f[i, :]))

        # Run 2D balancing --->
        computedattr_actions = trips_1.sum(0)
        computedattr_actions[computedattr_actions == 0] = 1
        attr_a = attr_a*(attr_t/computedattr_actions)

        computed_productions = trips_1.sum(1)
        computed_productions[computed_productions == 0] = 1
        prod_a = prod_a*(prod_t/computed_productions)

    for i in range(0, len(prod_a)):
        trips_1[i, :] = prod_a[i]*attr_a*f[i, :]/max(0.000001, sum(attr_a * f[i, :]))

    return trips_1


def calc_multi_fratar(prods, attr, trip_matrices, max_iter=10):
    """
    Applies fratar model to given set of trip matrices with target productions and one attr_action vector
    prods = Array of Productions (n production segments)
    attr_att = Array of attr_action ( 1 attr_action segment)
    trip_matrices = N-Dim array of seed trip matrices corresponding to prod_atts
     --> (num_trip_mats, num_zones, num_zones)
    max_iter = Maximum number of iterations
    version 1.0
    """
    num_zones = len(attr)
    num_trip_mats = len(trip_matrices)
    trip_matrices = numpy.zeros((num_trip_mats, num_zones, num_zones))

    # Run 2D balancing --->
    for Iter in range(0, max_iter):
        # computedattr_actions = numpy.ones(num_zones)
        computedattr_actions = trip_matrices.sum(1).sum(0)
        computedattr_actions[computedattr_actions == 0] = 1
        dest_fac = attr/computedattr_actions

        for k in range(0, len(num_trip_mats)):
            trip_matrices[k] = trip_matrices[k]*dest_fac
            computed_productions = trip_matrices[k].sum(1)
            computed_productions[computed_productions == 0] = 1
            orig_fac = prods[:, k]/computed_productions  # P[i, k1, k2, k3]...
            trip_matrices[k] = trip_matrices[k]*orig_fac[:, numpy.newaxis]

    return trip_matrices


def calc_multi_distribute(prods, attr, fric_matrices, max_iter=10):
    """
    prods = List of Production attributes
    attr  = attr_action attribute
    fric_matrices = N-Dim array of friction matrices corresponding to prod_atts --> 
    (numFrictionMats, num_zones, num_zones)
    max_iter (optional) = Maximum number of balancing iterations, default is 10
    Returns N-Dim array of trip matrices corresponding to each production segment
    """
    num_zones = len(attr)
    trip_matrices = numpy.zeros(fric_matrices.shape)
    num_fric_mats = len(fric_matrices)

    prod_op = prods.copy()
    attr_op = attr.copy()

    for Iter in range(0, max_iter):
        # Distribution --->
        for k in range(0, num_fric_mats):
            for i in range(0, num_zones):
                if prod_op[i, k] > 0:
                    trip_matrices[k, i, :] = prod_op[i, k] * attr_op * fric_matrices[k, i, :] / \
                                            max(0.000001, sum(attr_op * fric_matrices[k, i, :]))
        # Balancing --->
        computedattr_actions = trip_matrices.sum(1).sum(0)
        computedattr_actions[computedattr_actions == 0] = 1
        attr_op = attr_op*(attr/computedattr_actions)
        for k in range(0, len(fric_matrices)):
            computed_productions = trip_matrices[k].sum(1)
            computed_productions[computed_productions == 0] = 1
            orig_fac = prods[:, k]/computed_productions
            prod_op[:, k] = orig_fac*prod_op[:, k]
    # Final Distribution --->
    for k in range(0, num_fric_mats):
        for i in range(0, num_zones):
            if prod_op[i, k] > 0:
                trip_matrices[k, i, :] = prod_op[i, k] * attr_op * fric_matrices[k, i, :] / \
                                        max(0.000001, sum(attr_op * fric_matrices[k, i, :]))

    return trip_matrices
