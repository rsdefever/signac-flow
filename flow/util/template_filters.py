# Copyright (c) 2018 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
"""Provide jinja2 template environment filter functions."""
from __future__ import division
from math import ceil


def identical(iterable):
    """Check that all elements of an iterator are identical"""
    return len(set(iterable)) <= 1


def format_timedelta(delta, style='HH:MM:SS'):
    "Format a time delta for interpretation by schedulers."
    if isinstance(delta, int) or isinstance(delta, float):
        import datetime
        delta = datetime.timedelta(hours=delta)
    hours, r = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(r, 60)
    hours += delta.days * 24
    if style == 'HH:MM:SS':
        return "{:0>2}:{:0>2}:{:0>2}".format(hours, minutes, seconds)
    elif style == 'HH:MM':
        return "{:0>2}:{:0>2}".format(hours, minutes)
    else:
        raise ValueError('Unsupported style in format_timedelta.')


def with_np_offset(operations):
    """Add the np_offset variable to the operations' directives."""
    offset = 0
    for operation in operations:
        operation.directives.setdefault('np_offset', offset)
        offset += operation.directives['np']
    return operations


def check_utilization(nn, np, cpn, threshold=0.9):
    """Check whether the calculated node utilization is below threshold.

    This function raises a :class:`RuntimeError` if the calculated
    node utilization is below the given threshold or if the number
    of calculated required nodes is zero.

    :param nn:
        number of nodes
    :param np:
        number of processing units (CPU/GPU etc.)
    :param cpn:
        number of available processing units per node
    :param threshold:
        The required node utilization.
    :raises RuntimeError:
        If the number of nodes is zero or if the utilization
        is below the given threshold.
    :returns:
        The number of calculated nodes.
    """
    assert 0 <= threshold <= 1.0
    if nn == 0:
        raise RuntimeError("The number of required nodes is zero!")
    utilization = np / (nn * cpn)
    if utilization < threshold:
        raise RuntimeError(
            "Bad utilization: {:.0%} [#nodes={} #(cpu|#gpu)={}, #(cpu|gpu)/node={}]!".format(
                utilization, nn, np, cpn))
    else:
        return nn


def calc_num_nodes(np, cpn=1, threshold=0):
    """Calculate the number of required nodes.

    :param np:
        number of processing units (CPU/GPU etc.)
    :param cpn:
        number of available processing units per node
    :param threshold:
        (optional) The required node utilization.
        The default is 0, meaning no check.
    :returns:
        The number of required nodes.
    :raises RuntimeError:
        If the calculated node utilization is below the given threshold.
    """
    nn = int(ceil(np / cpn))
    return check_utilization(nn, np, cpn, threshold)
