"""Environments for XSEDE supercomputers."""
from __future__ import print_function
import sys
import logging

from xsede import Stampede2Environment
from ..errors import SubmitError
from jinja2 import Template

logger = logging.getLogger(__name__)

class Stampede2Launcher(Stampede2Environment):
    """Environment profile for the Stampede2 supercomputer using launcher.
    https://www.tacc.utexas.edu/systems/stampede2
    """
    template = 'stampede2launcher.sh'

    @classmethod
    def submit(cls, _id, script, flags=None, *args, **kwargs):
        """Submit a job submission script to the environment's scheduler.

        Scripts should be submitted to the environment, instead of directly
        to the scheduler to allow for environment specific post-processing.
        """
        if flags is None:
            flags = []
        env_flags = getattr(cls, 'submit_flags', [])
        if env_flags:
            flags.extend(env_flags)

        # Hand off the actual submission to the scheduler
        if isinstance(script, JobScript):  # api version < 6
            script = str(script)

        submission_name=_id.split('/')[-1]
        dir='launcher/'
        launcher_part='''
export LAUNCHER_PLUGIN_DIR=$LAUNCHER_DIR/plugins
export LAUNCHER_RMI=SLURM
export LAUNCHER_JOB_FILE=%s

$LAUNCHER_DIR/paramrun
''' %(dir+submission_name)
        script=script+launcher_part

        # create list of commands file for launcher
        launcher_file  = open('%s' %(dir+submission_name), 'w')
        for operation in operations:
            file_object.write(operation.cmd)
        launcher_file.close()

        if cls.get_scheduler().submit(script, flags=flags, *args, **kwargs):
            return JobStatus.submitted
