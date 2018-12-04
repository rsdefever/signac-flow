{# Templated in accordance with: http://www.sdsc.edu/support/user_guides/comet.html#running #}
{# This template can only be used with P100 GPUs! #}
{# Last updated on 2018-06-22 by csadorf@umich.edu #}
{% set mpiexec = "ibrun" %}
{% extends "slurm.sh" %}
{% block tasks %}
{% set threshold = 0 if force else 0.9 %}
{% if ngpu_global and 'gpu' not in partition %}
{% raise "Requesting GPUs requires a gpu partition!" %}
{% endif %}
{% if partition == 'gpu' %}
{% set nn_cpu = np_global|calc_num_nodes(24) %}
{% set nn_gpu = ngpu_global|calc_num_nodes(4) %}
{% set nn = nn|default((nn_cpu, nn_gpu)|max, true) %}
#SBATCH --nodes={{ nn|check_utilization(ngpu_global, 4, threshold) }}
#SBATCH --gres=gpu:p100:{{ (ngpu_global, 4)|min }}
{% elif partition == 'gpu-shared' %}
#SBATCH --nodes={{ nn|default(1, true)|check_utilization(ngpu_global, 1, threshold) }}
#SBATCH --ntasks-per-node={{ (ngpu_global * 7, np_global)|max }}
#SBATCH --gres=gpu:p100:{{ ngpu_global }}
{% elif 'shared' in partition %}{# standard shared partition #}
#SBATCH --nodes={{ nn|default(1, true) }}
#SBATCH --ntasks-per-node={{ np_global }}
{% else %}{# standard compute partition #}
#SBATCH --nodes={{ nn|check_utilization(np_global, 24, threshold) }}
#SBATCH --ntasks-per-node={{ (24, np_global)|min }}
{% endif %}
{% endblock tasks %}
{% block header %}
{{ super () -}}
{% set account = account|default('account'|get_config_value(ns=environment), true) %}
{% if account %}
#SBATCH -A {{ account }}
{% endif %}
{% if memory %}
#SBATCH --mem={{ memory }}G
{% endif %}
{% endblock %}
