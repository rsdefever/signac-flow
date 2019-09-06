# Copyright (c) 2018 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
"""Environments for the University of Michigan HPC environment."""
from ..environment import DefaultTorqueEnvironment
from ..environment import DefaultSlurmEnvironment


class FluxEnvironment(DefaultTorqueEnvironment):
    """Environment profile for the flux supercomputing environment.

    http://arc-ts.umich.edu/systems-and-services/flux/
    """
    hostname_pattern = '(nyx|flux)((?!-hadoop).).*.umich.edu'
    template = 'umich-flux.sh'
    cores_per_node = 1

    @classmethod
    def add_args(cls, parser):
        super(FluxEnvironment, cls).add_args(parser)
        parser.add_argument(
            '--mode',
            choices=('cpu', 'gpu'),
            default='cpu',
            help="Specify whether to submit to the CPU or the GPU queue. "
                 "(default=cpu)")
        parser.add_argument(
            '--memory',
            default='4g',
            help="Specify how much memory to reserve per node. (default=4g)")


class GreatLakesEnvironement(DefaultSlurmEnvironment):
    """Environment profile for the GreatLakes supercomputing environment.

    https://arc-ts.umich.edu/greatlakes/
    """
    hostname_pattern = r'^(gl)\w*(\.arc-ts\.\.umich\.edu)$'
    template = 'umich-greatlakes.sh'
    cores_per_node = 36

    @classmethod
    def add_args(cls, parser):
        super(GreatLakesEnvironement, cls).add_args(parser)
        parser.add_argument(
                '--partition',
                choices=('standard', 'gpu', 'largemem'),
                default='standard',
                help="Specify the partition to submit jobs under.")
        parser.add_argument(
                '--cpumemory',
                default='768m',
                help='Specify the memory per cpu. (default=768m')


__all__ = ['FluxEnvironment', 'GreatLakesEnvironement']
