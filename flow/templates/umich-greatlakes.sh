{# Templated in accordance with: https://arc-ts.umich.edu/greatlakes/user-guide/ #}
{% extends "slurm.sh" %}
{% block tasks %}
{% set cpu_tasks = operations|calc_tasks('np', parallel, force) %}
#SBATCH --ntasks={{ cpu_tasks }}
{% if partition == 'standard' %}
{% set nodes = cpu_tasks|calc_num_nodes(1, 0, 'CPU') %}
#SBATCH --nodes={{ nodes }}
{% set cpus_per_task = cpu_tasks // len(operations) %}
#SBATCH --cpus-per-task={{ cpus_per_task }}
{% endif %}
{% if memory %}
#SBATCH --memory-per-cpu={{ cpumemory }}
{% endblock %}

{% block header %}
{{ super() -}}
{% set account = account|default(environment|get_account_name, true) %}
{% if account %}
#SBATCH --account {{ account }}
{% endif %}
{% endblock %}
