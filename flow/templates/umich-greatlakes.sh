{# Templated in accordance with: https://arc-ts.umich.edu/greatlakes/user-guide/ #}
{% extends "slurm.sh" %}
{% block tasks %}
{% set cpu_tasks = operations|calc_tasks('np', parallel, force) %}
{% set tpp = operations|calc_tasks('omp_num_threads', false, force) %}
{% set tpp = tpp if tpp else 1 %}
{% set nranks = operations|calc_tasks('nranks', false, force) %}
{% if partition == 'standard' %}
{% if nranks %}
{% set nn_cpu = nranks %}
{% set ppn = 1 %}
{% else %}
{% set nn_cpu = (cpu_tasks * tpp)|calc_num_nodes(36, 0, 'CPU') %}
{% set ppn = cpu_tasks // nn_cpu %}
{% set ppn = ppn + 1 if cpu_tasks % nn_cpu else ppn %}
{% endif %}
#SBATCH --nodes={{ nn_cpu }}
#SBATCH --ntasks-per-node={{ ppn }}
#SBATCH --cpus-per-task={{ tpp }}
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
