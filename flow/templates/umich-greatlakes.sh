{# Templated in accordance with: https://arc-ts.umich.edu/greatlakes/user-guide/ #}
{% extends "slurm.sh" %}
{% block tasks %}
{% set cpu_tasks = operations|calc_tasks('np', parallel, force) %}
{% set threads_per_cpu = operations|calc_tasks('omp_num_threads', false, force) %}
{% set threads_per_cpu = threads_per_cpu if threads_per_cpu else 1 %}
{% if partition == 'standard' %}
{% set nn_cpu = (cpu_tasks * threads_per_cpu)|calc_num_nodes(36, 0, 'CPU') %}
#SBATCH --nodes={{ nn_cpu }}
{% set ppn = cpu_tasks // nn_cpu %}
{% set ppn = ppn + 1 if cpu_tasks % nn_cpu else ppn %}
#SBATCH --ntasks-per-node={{ ppn }}
#SBATCH --cpus-per-task={{ threads_per_cpu }}
{% endif %}
{% if cpumemory %}
#SBATCH --memory-per-cpu={{ cpumemory }}
{% endif %}
{% endblock %}

{% block header %}
{{ super() -}}
{% set account = account|default(environment|get_account_name, true) %}
{% if account %}
#SBATCH --account {{ account }}
{% endif %}
{% endblock %}
