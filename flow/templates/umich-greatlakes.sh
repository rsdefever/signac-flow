{# Templated in accordance with: https://arc-ts.umich.edu/greatlakes/user-guide/ #}
{% extends "slurm.sh" %}
{% block tasks %}
{% set cpu_tasks = operations|calc_tasks('np', parallel, force) %}
{% set tpp = operations|calc_tasks('omp_num_threads', false, force) %}
{% set tpp = tpp if tpp else 1 %}
{% if partition == 'standard' %}
{% set nn_cpu = cpu_tasks|calc_num_nodes(36, 0, 'CPU') %}
{% set cpuproc = cpu_tasks // tpp %}
{% set cpuproc = cpuproc + 1 if cpu_tasks % tpp else cpuproc %}
{% set ppn = cpuproc // nn_cpu %}
{% set ppn = ppn + 1 if cpu_tasks % tpp else ppn %}
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
