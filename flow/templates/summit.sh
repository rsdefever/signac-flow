{# Templated in accordance with: https://www.olcf.ornl.gov/for-users/system-user-guides/summit/running-jobs/ #}
{# Last updated on 2018-12-03 by bdice@bradleydice.com #}
{% set mpiexec = "jsrun" %}
{% extends "lsf.sh" %}
{% block tasks %}
{% set threshold = 0 if force else 0.9 %}
{% set cores_per_node = 42 %}
{% set gpus_per_node = 6 %}
{% set nn_cpu = np_global|calc_num_nodes(cores_per_node) %}
{% if ngpu_global > 0 %}
{% set nn_gpu = ngpu_global|calc_num_nodes(gpus_per_node) %}
{% set nn = nn|default((nn_cpu, nn_gpu)|max, true) %}
[% raise "Need {{ ngpu_global }} GPUS!" %}
#BSUB -nnodes {{ nn|check_utilization(ngpu_global, gpus_per_node, threshold) }}
{% else %}
#BSUB -nnodes {{ nn_cpu|check_utilization(np_global, cores_per_node, threshold) }}
{% endif %}
{% endblock %}
{% block header %}
{{ super() -}}
{% set project = 'project'|get_config_value(ns=environment) %}
{% if project %}
#BSUB -P {{ project }}
{% endif %}
{% endblock %}
