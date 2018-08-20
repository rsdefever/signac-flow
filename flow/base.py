# Copyright (c) 2018 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
import warnings
from hashlib import sha1

from signac.common import six
from signac.contrib.hashing import calc_id

from .scheduling.base import JobStatus


class FlowCondition(object):
    """A FlowCondition represents a condition as a function of a signac job.

    The __call__() function of a FlowCondition object may return either True
    or False, representing whether the condition is met or not.
    This can be used to build a graph of conditions and operations.

    :param callback:
        A function with one positional argument (the job)
    :type callback:
        :py:class:`~signac.contrib.job.Job`
    """

    def __init__(self, callback):
        self._callback = callback

    def __call__(self, job):
        if self._callback is None:
            return True
        return self._callback(job)

    def __hash__(self):
        return hash(self._callback)

    def __eq__(self, other):
        return self._callback == other._callback


class FlowOperation(object):
    """A FlowOperation represents a data space operation, operating on any job.

    Any FlowOperation is associated with a specific command, which should be
    a function of :py:class:`~signac.contrib.job.Job`. The command (cmd) can
    be stated as function, either by using str-substitution based on a job's
    attributes, or by providing a unary callable, which expects an instance
    of job as its first and only positional argument.

    For example, if we wanted to define a command for a program called 'hello',
    which expects a job id as its first argument, we could contruct the following
    two equivalent operations:

    .. code-block:: python

        op = FlowOperation('hello', cmd='hello {job._id}')
        op = FlowOperation('hello', cmd=lambda 'hello {}'.format(job._id))

    Here is another example for possible str-substitutions:

    .. code-block:: python

        # Substitute job state point parameters:
        op = FlowOperation('hello', cmd='cd {job.ws}; hello {job.sp.a}')

    Pre-requirements (pre) and post-conditions (post) can be used to
    trigger an operation only when certain conditions are met. Conditions are unary
    callables, which expect an instance of job as their first and only positional
    argument and return either True or False.

    An operation is considered "eligible" for execution when all pre-requirements
    are met and when at least one of the post-conditions is not met.
    Requirements are always met when the list of requirements is empty and
    post-conditions are never met when the list of post-conditions is empty.

    :param cmd:
        The command to execute operation; should be a function of job.
    :type cmd:
        str or callable
    :param pre:
        required conditions
    :type pre:
        sequence of callables
    :param post:
        post-conditions to determine completion
    :type pre:
        sequence of callables
    :param directives:
        A dictionary of additional parameters that provide instructions on how
        to execute this operation, e.g., specifically required resources.
    :type directives:
        :class:`dict`
    """

    def __init__(self, cmd, pre=None, post=None, directives=None, np=None):
        if pre is None:
            pre = []
        if post is None:
            post = []
        self._cmd = cmd
        self.directives = directives

        # Handle deprecated np argument.
        if np is not None:
            warnings.warn(
                "The np argument for the FlowOperation() constructor is deprecated.",
                DeprecationWarning)
            if self.directives is None:
                self.directives = dict(np=np)
            else:
                assert self.directives.setdefault('np', np) == np

        self._prereqs = [FlowCondition(cond) for cond in pre]
        self._postconds = [FlowCondition(cond) for cond in post]

    def __str__(self):
        return "{type}(cmd='{cmd}')".format(type=type(self).__name__, cmd=self._cmd)

    def eligible(self, job):
        "Eligible, when all pre-conditions are true and at least one post-condition is false."
        pre = all(cond(job) for cond in self._prereqs)
        if len(self._postconds):
            post = any(not cond(job) for cond in self._postconds)
        else:
            post = True
        return pre and post

    def complete(self, job):
        "True when all post-conditions are met."
        if len(self._postconds):
            return all(cond(job) for cond in self._postconds)
        else:
            return False

    def __call__(self, job=None):
        if callable(self._cmd):
            return self._cmd(job).format(job=job)
        else:
            return self._cmd.format(job=job)

    def np(self, job):
        "(deprecated) Return the number of processors this operation requires."
        if callable(self._np):
            return self._np(job)
        else:
            return self._np


class JobOperation(object):
    """This class represents the information needed to execute one operation for one job.

    An operation function in this context is a shell command, which should be a function
    of one and only one signac job.

    .. note::

        This class is used by the :class:`~.FlowProject` class for the execution and
        submission process and should not be instantiated by users themselves.

    .. versionchanged:: 0.6

    :param name:
        The name of this JobOperation instance. The name is arbitrary,
        but helps to concisely identify the operation in various contexts.
    :type name:
        str
    :param job:
        The job instance associated with this operation.
    :type job:
        :py:class:`signac.Job`.
    :param cmd:
        The command that executes this operation.
    :type cmd:
        str
    :param directives:
        A dictionary of additional parameters that provide instructions on how
        to execute this operation, e.g., specifically required resources.
    :type directives:
        :class:`dict`
    """
    MAX_LEN_ID = 100

    def __init__(self, name, job, cmd, directives=None, np=None):
        if directives is None:
            directives = dict()
        self.name = name
        self.job = job
        self.cmd = cmd

        # Handle deprecated np argument:
        if np is not None:
            warnings.warn(
                "The np argument for the JobOperation constructor is deprecated.",
                DeprecationWarning)
            assert directives.setdefault('np', np) == np
        else:
            directives.setdefault(
                'np', directives.get('nranks', 1) * directives.get('omp_num_threads', 1))
        directives.setdefault('ngpu', 0)
        # Future: directives.setdefault('np', 1)

        # Evaluate strings and callables for job:
        def evaluate(value):
            if value and callable(value):
                return value(job)
            elif isinstance(value, six.string_types):
                return value.format(job=job)
            else:
                return value

        self.directives = {key: evaluate(value) for key, value in directives.items()}

    def __str__(self):
        return "{}({})".format(self.name, self.job)

    def __repr__(self):
        return "{type}(name='{name}', job='{job}', cmd={cmd}, directives={directives})".format(
            type=type(self).__name__,
            name=self.name,
            job=str(self.job),
            cmd=repr(self.cmd),
            directives=self.directives)

    def _get_legacy_id(self):
        "Return a name, which identifies this job-operation."
        return '{}-{}'.format(self.job, self.name)

    def get_id(self, index=0):
        "Return a name, which identifies this job-operation."
        project = self.job._project

        # The full name is designed to be truly unique for each job-operation.
        full_name = '{}%{}%{}%{}'.format(
            project.root_directory(), self.job.get_id(), self.name, index)

        # The job_op_id is a hash computed from the unique full name.
        job_op_id = calc_id(full_name)

        # The actual job id is then constructed from a readable part and the job_op_id,
        # ensuring that the job-op is still somewhat identifiable, but guarantueed to
        # be unique. The readable name is based on the project id, job id, operation name,
        # and the index number. All names and the id itself are restricted in length
        # to guarantuee that the id does not get too long.
        max_len = self.MAX_LEN_ID - len(job_op_id)
        if max_len < len(job_op_id):
            raise ValueError("Value for MAX_LEN_ID is too small ({}).".format(self.MAX_LEN_ID))

        readable_name = '{}/{}/{}/{:04d}/'.format(
            str(project)[:12], str(self.job)[:8], self.name[:12], index)[:max_len]

        # By appending the unique job_op_id, we ensure that each id is truly unique.
        return readable_name + job_op_id

    @classmethod
    def expand_id(self, _id):
        # TODO: Remove beginning version 0.7.
        raise RuntimeError("The expand_id() method has been removed as of version 0.6.")

    def __hash__(self):
        return int(sha1(self.get_id().encode('utf-8')).hexdigest(), 16)

    def __eq__(self, other):
        return self.get_id() == other.get_id()

    def set_status(self, value):
        "Store the operation's status."
        status_doc = self.job.document.get('_status', dict())
        status_doc[self.get_id()] = int(value)
        self.job.document['_status'] = status_doc

    def get_status(self):
        "Retrieve the operation's last known status."
        try:
            status_cache = self.job.document['_status']
            return JobStatus(status_cache[self.get_id()])
        except KeyError:
            return JobStatus.unknown
