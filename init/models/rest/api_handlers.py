deprecated_columns = {
    "services.svc_cluster_type": "services.svc_topology",
    "services.svc_envfile": "services.svc_config",
    "services.svc_envdate": "services.svc_config_updated",
    "services.svc_type": "services.svc_env",
    "nodes.host_mode": "nodes.node_env",
    "nodes.environnement": "nodes.asset_env",
}

def get_get_handlers(prefix=None):
    _handlers = {
       "api": [
             "rest_get_api",
       ],
       "actions": [
             "rest_get_action_queue",
             "rest_get_action_queue_stats",
             "rest_get_action_queue_one",
       ],
       "alerts": [
             "rest_get_alerts",
             "rest_get_alert",
       ],
       "alert_event": [
             "rest_get_alert_event",
       ],
       "apps": [
             "rest_get_apps",
             "rest_get_app",
             "rest_get_app_am_i_responsible",
             "rest_get_app_nodes",
             "rest_get_app_quotas",
             "rest_get_app_services",
             "rest_get_app_responsibles",
             "rest_get_app_publications",
       ],
       "arrays": [
             "rest_get_arrays",
             "rest_get_array",
             "rest_get_array_disks",
             "rest_get_array_diskgroups",
             "rest_get_array_diskgroup",
             "rest_get_array_diskgroup_quota",
             "rest_get_array_diskgroup_quotas",
             "rest_get_array_proxies",
             "rest_get_array_targets",
       ],
       "checks": [
             "rest_get_checks_defaults",
             "rest_get_checks_default",
             "rest_get_checks_settings",
             "rest_get_checks_setting",
             "rest_get_checks_contextual_settings",
             "rest_get_checks_contextual_setting",
             "rest_get_checks",
             "rest_get_check",
       ],
       "compliance": [
             "rest_get_compliance_log",
             "rest_get_compliance_logs",
             "rest_get_compliance_modulesets_export",
             "rest_get_compliance_modulesets",
             "rest_get_compliance_moduleset_am_i_responsible",
             "rest_get_compliance_moduleset_usage",
             "rest_get_compliance_moduleset_export",
             "rest_get_compliance_moduleset_module",
             "rest_get_compliance_moduleset_modules",
             "rest_get_compliance_moduleset_candidate_nodes",
             "rest_get_compliance_moduleset_nodes",
             "rest_get_compliance_moduleset_candidate_services",
             "rest_get_compliance_moduleset_services",
             "rest_get_compliance_moduleset_publications",
             "rest_get_compliance_moduleset_responsibles",
             "rest_get_compliance_moduleset",
             "rest_get_compliance_rulesets_export",
             "rest_get_compliance_rulesets",
             "rest_get_compliance_ruleset_am_i_responsible",
             "rest_get_compliance_ruleset_variables",
             "rest_get_compliance_ruleset_variable",
             "rest_get_compliance_ruleset_candidate_nodes",
             "rest_get_compliance_ruleset_nodes",
             "rest_get_compliance_ruleset_candidate_services",
             "rest_get_compliance_ruleset_services",
             "rest_get_compliance_ruleset_publications",
             "rest_get_compliance_ruleset_responsibles",
             "rest_get_compliance_ruleset_variable",
             "rest_get_compliance_ruleset_export",
             "rest_get_compliance_ruleset_usage",
             "rest_get_compliance_ruleset",
             "rest_get_compliance_status",
             "rest_get_compliance_status_one",
       ],
       "docker": [
             "rest_get_docker_registries",
             "rest_get_docker_registry",
             "rest_get_docker_registry_publications",
             "rest_get_docker_registry_responsibles",
             "rest_get_docker_registry_am_i_responsible",
             "rest_get_docker_repositories",
             "rest_get_docker_repository",
             "rest_get_docker_repository_pullers",
             "rest_get_docker_repository_pullers_apps",
             "rest_get_docker_repository_pullers_groups",
             "rest_get_docker_repository_pullers_services",
             "rest_get_docker_repository_pullers_users",
             "rest_get_docker_repository_pushers",
             "rest_get_docker_repository_pushers_apps",
             "rest_get_docker_repository_pushers_groups",
             "rest_get_docker_repository_pushers_users",
             "rest_get_docker_tag",
       ],
       "disks": [
             "rest_get_disk",
             "rest_get_disks",
       ],
       "dns": [
             "rest_get_dns_domains",
             "rest_get_dns_domain",
             "rest_get_dns_domain_records",
             "rest_get_dns_records",
             "rest_get_dns_record",
       ],
       "filters": [
             "rest_get_filters",
             "rest_get_filter",
       ],
       "filtersets": [
             "rest_get_filtersets",
             "rest_get_filterset",
             "rest_get_filterset_usage",
             "rest_get_filterset_export",
             "rest_get_filterset_filtersets",
             "rest_get_filterset_filters",
             "rest_get_filterset_nodes",
             "rest_get_filterset_services",
       ],
       "form_output_results": [
             "rest_get_form_output_result",
       ],
       "forms_revisions": [
             "rest_get_forms_revisions",
             "rest_get_forms_revision",
       ],
       "forms": [
             "rest_get_forms",
             "rest_get_form",
             "rest_get_form_publications",
             "rest_get_form_responsibles",
             "rest_get_form_am_i_responsible",
             "rest_get_form_revision",
             "rest_get_form_revisions",
             "rest_get_form_diff",
       ],
       "frontend": [
             "rest_get_frontend_hidden_menu_entries",
       ],
       "groups": [
             "rest_get_groups",
             "rest_get_group",
             "rest_get_group_apps",
             "rest_get_group_hidden_menu_entries",
             "rest_get_group_modulesets",
             "rest_get_group_nodes",
             "rest_get_group_rulesets",
             "rest_get_group_services",
             "rest_get_group_users",
       ],
       "ips": [
             "rest_get_ips",
             "rest_get_ip",
       ],
       "links": [
             "rest_get_link",
             "rest_get_links",
       ],
       "logs": [
             "rest_get_log",
             "rest_get_logs",
       ],
       "networks": [
             "rest_get_networks",
             "rest_get_network",
             "rest_get_network_ips",
             "rest_get_network_segments",
             "rest_get_network_segment",
             "rest_get_network_segment_responsibles",
             "rest_get_network_nodes",
       ],
       "nodes_hardware": [
             "rest_get_nodes_hardwares",
       ],
       "nodes": [
             "rest_get_node_hardwares",
             "rest_get_nodes",
             "rest_get_node",
             "rest_get_node_alerts",
             "rest_get_node_am_i_responsible",
             "rest_get_node_disks",
             "rest_get_node_checks",
             "rest_get_node_candidate_tags",
             "rest_get_node_compliance_candidate_modulesets",
             "rest_get_node_compliance_modulesets",
             "rest_get_node_compliance_candidate_rulesets",
             "rest_get_node_compliance_rulesets",
             "rest_get_node_compliance_status",
             "rest_get_node_compliance_logs",
             "rest_get_node_hbas",
             "rest_get_node_targets",
             "rest_get_node_interfaces",
             "rest_get_node_ips",
             "rest_get_node_root_password",
             "rest_get_node_services",
             "rest_get_node_service",
             "rest_get_node_sysreport",
             "rest_get_node_sysreport_timediff", # keep before sysreport_commit
             "rest_get_node_sysreport_commit",
             "rest_get_node_sysreport_commit_tree",
             "rest_get_node_sysreport_commit_tree_file",
             "rest_get_node_tags",
             "rest_get_node_uuid",
       ],
       "obsolescence": [
             "rest_get_obsolescence_settings",
             "rest_get_obsolescence_setting",
       ],
       "packages": [
             "rest_get_packages_diff",
       ],
       "provisioning_templates": [
             "rest_get_provisioning_templates",
             "rest_get_provisioning_template",
             "rest_get_provisioning_template_am_i_responsible",
             "rest_get_provisioning_template_responsibles",
             "rest_get_provisioning_template_publications",
             "rest_get_provisioning_template_revision",
             "rest_get_provisioning_template_revisions",
             "rest_get_provisioning_template_diff",
       ],
       "resources": [
             "rest_get_resource",
             "rest_get_resources",
       ],
       "resources_logs": [
             "rest_get_resources_logs",
       ],
       "search": [
             "rest_get_search",
       ],
       "services": [
             "rest_get_services",
             "rest_get_service",
             "rest_get_service_actions",
             "rest_get_service_actions_unacknowledged_errors",
             "rest_get_service_resinfos",
             "rest_get_service_alerts",
             "rest_get_service_am_i_responsible",
             "rest_get_service_candidate_tags",
             "rest_get_service_checks",
             "rest_get_service_compliance_candidate_modulesets",
             "rest_get_service_compliance_modulesets",
             "rest_get_service_compliance_candidate_rulesets",
             "rest_get_service_compliance_rulesets",
             "rest_get_service_compliance_status",
             "rest_get_service_compliance_logs",
             "rest_get_service_disks",
             "rest_get_service_hbas",
             "rest_get_service_nodes",
             "rest_get_service_node",
             "rest_get_service_node_resources",
             "rest_get_service_node_resources_logs",
             "rest_get_service_resources",
             "rest_get_service_resources_logs",
             "rest_get_service_tags",
             "rest_get_service_targets",
       ],
       "services_instances": [
             "rest_get_services_instances",
             "rest_get_service_instance",
       ],
       "services_actions": [
             "rest_get_services_actions",
       ],
       "services_instances_status_log": [
             "rest_get_services_instances_status_log",
       ],
       "services_status_log": [
             "rest_get_services_status_log",
       ],
       "scheduler": [
             "rest_get_scheduler_stats",
             "rest_get_scheduler_tasks",
             "rest_get_scheduler_task",
             "rest_get_scheduler_runs",
             "rest_get_scheduler_run",
             "rest_get_scheduler_workers",
             "rest_get_scheduler_worker",
       ],
       "forms_store": [
             "rest_get_store_form_dump",
             "rest_get_store_forms",
             "rest_get_store_form",
       ],
       "tags": [
             "rest_get_tags_nodes",
             "rest_get_tags_services",
             "rest_get_tags",
             "rest_get_tag",
             "rest_get_tag_nodes",
             "rest_get_tag_services",
       ],
       "users": [
             "rest_get_users",
             "rest_get_user",
             "rest_get_user_prefs",
             "rest_get_user_dump",
             "rest_get_user_apps_publication",
             "rest_get_user_apps_responsible",
             "rest_get_user_nodes",
             "rest_get_user_services",
             "rest_get_user_groups",
             "rest_get_user_hidden_menu_entries",
             "rest_get_user_primary_group",
             "rest_get_user_filterset",
       ],
       "reports": [
             "rest_get_reports_charts",
             "rest_get_reports_chart",
             "rest_get_reports_chart_am_i_responsible",
             "rest_get_reports_chart_publications",
             "rest_get_reports_chart_responsibles",
             "rest_get_reports_chart_revision",
             "rest_get_reports_chart_revisions",
             "rest_get_reports_chart_diff",
             "rest_get_reports_chart_samples",
             "rest_get_reports_metrics",
             "rest_get_reports_metric",
             "rest_get_reports_metric_am_i_responsible",
             "rest_get_reports_metric_publications",
             "rest_get_reports_metric_samples",
             "rest_get_reports_metric_revision",
             "rest_get_reports_metric_revisions",
             "rest_get_reports_metric_diff",
             "rest_get_report_definition",
             "rest_get_report_export",
             "rest_get_reports",
             "rest_get_report",
             "rest_get_report_am_i_responsible",
             "rest_get_report_publications",
             "rest_get_report_responsibles",
             "rest_get_report_revision",
             "rest_get_report_revisions",
             "rest_get_report_diff",
       ],
       "safe": [
             "rest_get_safe",
             "rest_get_safe_file_history",
             "rest_get_safe_file",
             "rest_get_safe_file_am_i_responsible",
             "rest_get_safe_file_download",
             "rest_get_safe_file_preview",
             "rest_get_safe_file_publications",
             "rest_get_safe_file_responsibles",
             "rest_get_safe_file_usage",
       ],
       "sysreport": [
             "rest_get_sysreport_timeline",
             "rest_get_sysreport_nodediff",
             "rest_get_sysreport_secure_patterns",
             "rest_get_sysreport_secure_pattern",
             "rest_get_sysreport_authorizations",
             "rest_get_sysreport_authorization",
       ],
       "wiki": [
             "rest_get_wiki",
             "rest_get_wikis",
       ],
       "workflows": [
             "rest_get_workflow",
             "rest_get_workflows",
             "rest_get_workflow_dump",
       ]
    }
    if prefix:
        return [globals()[h]() for h in _handlers[prefix]]
    data = []
    for l in _handlers.values():
        data += [globals()[h]() for h in l]
    return data


def get_delete_handlers(prefix=None):
    _handlers = {
        "actions": [
             "rest_delete_action_queue_one",
        ],
        "alerts": [
             "rest_delete_alert",
             "rest_delete_alerts",
        ],
        "apps": [
             "rest_delete_apps",
             "rest_delete_app",
             "rest_delete_app_responsible",
             "rest_delete_app_publication",
        ],
        "apps_responsibles": [
             "rest_delete_apps_responsibles",
        ],
        "apps_publications": [
             "rest_delete_apps_publications",
        ],
        "arrays": [
             "rest_delete_array_diskgroup_quotas",
             "rest_delete_array_diskgroup_quota",
             "rest_delete_array_proxies",
             "rest_delete_array_proxy",
        ],
        "checks": [
             "rest_delete_checks_settings",
             "rest_delete_checks_setting",
             "rest_delete_checks_contextual_settings",
             "rest_delete_checks_contextual_setting",
             "rest_delete_checks_defaults",
             "rest_delete_checks_default",
             "rest_delete_checks",
             "rest_delete_check",
        ],
        "compliance": [
             "rest_delete_compliance_moduleset_moduleset",
             "rest_delete_compliance_moduleset_module",
             "rest_delete_compliance_moduleset_publication",
             "rest_delete_compliance_modulesets_publications",
             "rest_delete_compliance_moduleset_responsible",
             "rest_delete_compliance_modulesets_responsibles",
             "rest_delete_compliance_moduleset_ruleset",
             "rest_delete_compliance_moduleset",
             "rest_delete_compliance_modulesets",
             "rest_delete_compliance_modulesets_nodes",
             "rest_delete_compliance_modulesets_services",
             "rest_delete_compliance_ruleset_filterset",
             "rest_delete_compliance_ruleset_publication",
             "rest_delete_compliance_rulesets_publications",
             "rest_delete_compliance_ruleset_responsible",
             "rest_delete_compliance_rulesets_responsibles",
             "rest_delete_compliance_ruleset_ruleset",
             "rest_delete_compliance_ruleset_variable",
             "rest_delete_compliance_ruleset",
             "rest_delete_compliance_rulesets",
             "rest_delete_compliance_rulesets_nodes",
             "rest_delete_compliance_rulesets_services",
             "rest_delete_compliance_status_run",
             "rest_delete_compliance_status_runs",
        ],
        "disks": [
             "rest_delete_disk",
             "rest_delete_disks",
        ],
        "docker": [
             "rest_delete_docker_tags",
             "rest_delete_docker_tag",
             "rest_delete_docker_registries",
             "rest_delete_docker_registry",
             "rest_delete_docker_repositories",
             "rest_delete_docker_repository",
             "rest_delete_docker_registries_publications",
             "rest_delete_docker_registries_responsibles",
             "rest_delete_docker_registry_publication",
             "rest_delete_docker_registry_responsible",
        ],
        "dns": [
             "rest_delete_dns_domain",
             "rest_delete_dns_domains",
             "rest_delete_dns_record",
             "rest_delete_dns_records",
        ],
        "filters": [
             "rest_delete_filter",
             "rest_delete_filters",
        ],
        "filtersets": [
             "rest_delete_filterset",
             "rest_delete_filtersets",
             "rest_delete_filterset_filterset",
             "rest_delete_filterset_filter",
        ],
        "filtersets_filtersets": [
             "rest_delete_filtersets_filtersets",
        ],
        "filtersets_filters": [
             "rest_delete_filtersets_filters",
        ],
        "forms": [
             "rest_delete_form",
             "rest_delete_forms",
             "rest_delete_form_publication",
             "rest_delete_form_responsible",
        ],
        "forms_publications": [
             "rest_delete_forms_publications",
        ],
        "forms_responsibles": [
             "rest_delete_forms_responsibles",
        ],
        "groups": [
             "rest_delete_group",
             "rest_delete_groups",
             "rest_delete_group_hidden_menu_entries",
        ],
        "ips": [
             "rest_delete_ips",
             "rest_delete_ip",
        ],
        "networks": [
             "rest_delete_networks_segments",
             "rest_delete_networks_segments_responsibles",
             "rest_delete_network",
             "rest_delete_networks",
             "rest_delete_network_segment",
             "rest_delete_network_segment_responsible",
        ],
        "nodes": [
             "rest_delete_nodes",
             "rest_delete_node",
             "rest_delete_node_compliance_moduleset",
             "rest_delete_node_compliance_ruleset",
        ],
        "obsolescence": [
             "rest_delete_obsolescence_settings",
             "rest_delete_obsolescence_setting",
        ],
        "provisioning_templates": [
             "rest_delete_provisioning_templates",
             "rest_delete_provisioning_template",
             "rest_delete_provisioning_template_responsible",
             "rest_delete_provisioning_template_publication",
        ],
        "provisioning_templates_publications": [
             "rest_delete_provisioning_templates_publications",
        ],
        "provisioning_templates_responsibles": [
             "rest_delete_provisioning_templates_responsibles",
        ],
        "reports": [
             "rest_delete_reports_chart",
             "rest_delete_reports_chart_publication",
             "rest_delete_reports_chart_responsible",
             "rest_delete_reports_charts",
             "rest_delete_reports_charts_publications",
             "rest_delete_reports_charts_responsibles",
             "rest_delete_reports_metric",
             "rest_delete_reports_metric_publication",
             "rest_delete_reports_metrics",
             "rest_delete_reports_metrics_publications",
             "rest_delete_reports",
             "rest_delete_report",
             "rest_delete_report_publication",
             "rest_delete_report_responsible",
        ],
        "reports_publications": [
             "rest_delete_reports_publications",
        ],
        "reports_publications": [
             "rest_delete_reports_responsibles",
        ],
        "resources": [
             "rest_delete_resource",
             "rest_delete_resources",
        ],
        "services_instances": [
             "rest_delete_service_instance",
             "rest_delete_services_instances",
        ],
        "services": [
             "rest_delete_service",
             "rest_delete_services",
             "rest_delete_service_compliance_moduleset",
             "rest_delete_service_compliance_ruleset",
        ],
        "scheduler": [
             "rest_delete_scheduler_task",
             "rest_delete_scheduler_run",
        ],
        "safe": [
             "rest_delete_safe_files_publications",
             "rest_delete_safe_files_responsibles",
             "rest_delete_safe_files",
             "rest_delete_safe_file_publication",
             "rest_delete_safe_file_responsible",
             "rest_delete_safe_file",
        ],
        "sysreport": [
             "rest_delete_sysreport_secure_pattern",
             "rest_delete_sysreport_authorization",
        ],
        "tags": [
             "rest_delete_tags_nodes",
             "rest_delete_tags_services",
             "rest_delete_tags",
             "rest_delete_tag",
             "rest_delete_tag_node",
             "rest_delete_tag_service",
        ],
        "users_groups": [
             "rest_delete_users_groups",
        ],
        "users": [
             "rest_delete_users",
             "rest_delete_user",
             "rest_delete_user_group",
             "rest_delete_user_primary_group",
             "rest_delete_user_filterset",
        ]
    }
    if prefix:
        return [globals()[h]() for h in _handlers[prefix]]
    data = []
    for l in _handlers.values():
        data += [globals()[h]() for h in l]
    return data


def get_post_handlers(prefix=None):
    _handlers = {
        "actions": [
             "rest_post_action_queue",
             "rest_post_action_queue_one",
        ],
        "alerts": [
             "rest_post_alert",
             "rest_post_alerts",
        ],
        "apps": [
             "rest_post_apps",
             "rest_post_app",
             "rest_post_app_responsible",
             "rest_post_app_publication",
        ],
        "apps_responsibles": [
             "rest_post_apps_responsibles",
        ],
        "apps_publications": [
             "rest_post_apps_publications",
        ],
        "arrays": [
             "rest_post_array",
             "rest_post_array_diskgroup_quotas",
             "rest_post_array_diskgroup_quota",
             "rest_post_array_proxies",
             "rest_post_array_proxy",
        ],
        "checks": [
             "rest_post_checks_contextual_settings",
             "rest_post_checks_contextual_setting",
             "rest_post_checks_defaults",
             "rest_post_checks_default",
             "rest_post_checks_settings",
             "rest_post_checks_setting",
        ],
        "compliance": [
             "rest_post_compliance_import",
             "rest_post_compliance_moduleset_moduleset",
             "rest_post_compliance_moduleset_module",
             "rest_post_compliance_moduleset_modules",
             "rest_post_compliance_moduleset_publication",
             "rest_post_compliance_modulesets_publications",
             "rest_post_compliance_moduleset_responsible",
             "rest_post_compliance_modulesets_responsibles",
             "rest_post_compliance_moduleset_ruleset",
             "rest_post_compliance_modulesets_nodes",
             "rest_post_compliance_modulesets_services",
             "rest_post_compliance_modulesets",
             "rest_post_compliance_moduleset",
             "rest_post_compliance_ruleset_filterset",
             "rest_post_compliance_ruleset_publication",
             "rest_post_compliance_rulesets_publications",
             "rest_post_compliance_ruleset_responsible",
             "rest_post_compliance_rulesets_responsibles",
             "rest_post_compliance_ruleset_ruleset",
             "rest_post_compliance_ruleset_variable",
             "rest_post_compliance_ruleset_variables",
             "rest_post_compliance_rulesets_variables",
             "rest_post_compliance_rulesets_nodes",
             "rest_post_compliance_rulesets_services",
             "rest_post_compliance_rulesets",
             "rest_post_compliance_ruleset",
        ],
        "disks": [
             "rest_post_disks",
        ],
        "docker": [
             "rest_post_docker_registries",
             "rest_post_docker_registry",
             "rest_post_docker_repository",
             "rest_post_docker_registries_publications",
             "rest_post_docker_registries_responsibles",
             "rest_post_docker_registry_publication",
             "rest_post_docker_registry_responsible",
        ],
        "dns": [
             "rest_post_dns_domains",
             "rest_post_dns_domain",
             "rest_post_dns_records",
             "rest_post_dns_record",
             "rest_post_dns_services_records",
        ],
        "filters": [
             "rest_post_filters",
             "rest_post_filter",
        ],
        "filtersets_filtersets": [
             "rest_post_filtersets_filtersets",
        ],
        "filtersets_filters": [
             "rest_post_filtersets_filters",
        ],
        "filtersets": [
             "rest_post_filtersets",
             "rest_post_filterset",
             "rest_post_filterset_filterset",
             "rest_post_filterset_filter",
        ],
        "forms": [
             "rest_post_forms",
             "rest_post_form",
             "rest_post_form_publication",
             "rest_post_form_responsible",
             "rest_post_form_rollback",
        ],
        "forms_publications": [
             "rest_post_forms_publications",
        ],
        "forms_responsibles": [
             "rest_post_forms_responsibles",
        ],
        "groups": [
             "rest_post_groups",
             "rest_post_group_hidden_menu_entries",
             "rest_post_group",
        ],
        "links": [
             "rest_post_link",
        ],
        "logs": [
             "rest_post_logs",
        ],
        "networks": [
             "rest_post_networks_segments_responsibles",
             "rest_post_networks",
             "rest_post_network",
             "rest_post_network_allocate",
             "rest_post_network_release",
             "rest_post_network_segment",
             "rest_post_network_segments",
             "rest_post_network_segment_responsible",
        ],
        "nodes": [
             "rest_post_nodes",
             "rest_post_node_snooze",
             "rest_post_node",
             "rest_post_node_compliance_moduleset",
             "rest_post_node_compliance_ruleset",
        ],
        "obsolescence": [
             "rest_post_obsolescence_settings",
             "rest_post_obsolescence_setting",
        ],
        "provisioning_templates": [
             "rest_post_provisioning_templates",
             "rest_post_provisioning_template",
             "rest_post_provisioning_template_responsible",
             "rest_post_provisioning_template_publication",
             "rest_post_provisioning_template_rollback",
        ],
        "provisioning_templates_publications": [
             "rest_post_provisioning_templates_publications",
        ],
        "provisioning_templates_responsibles": [
             "rest_post_provisioning_templates_responsibles",
        ],
        "register": [
             "rest_post_register",
        ],
        "reports": [
             "rest_post_reports_chart",
             "rest_post_reports_chart_responsible",
             "rest_post_reports_chart_publication",
             "rest_post_reports_charts",
             "rest_post_reports_charts_responsibles",
             "rest_post_reports_charts_publications",
             "rest_post_reports_metric",
             "rest_post_reports_metric_publication",
             "rest_post_reports_metrics",
             "rest_post_reports_metrics_publications",
             "rest_post_reports_import",
             "rest_post_reports",
             "rest_post_report",
             "rest_post_report_responsible",
             "rest_post_report_publication",
             "rest_post_report_rollback",
        ],
        "reports_publications": [
             "rest_post_reports_publications",
        ],
        "reports_responsibles": [
             "rest_post_reports_responsibles",
        ],
        "safe": [
             "rest_post_safe_files_publications",
             "rest_post_safe_files_responsibles",
             "rest_post_safe_file_upload",
             "rest_post_safe_upload",
             "rest_post_safe_file",
             "rest_post_safe_file_publication",
             "rest_post_safe_file_responsible",
             "rest_post_safe",
        ],
        "scheduler": [
             "rest_post_scheduler_task",
             "rest_post_scheduler_run",
        ],
        "services": [
             "rest_post_services",
             "rest_post_service_snooze",
             "rest_post_service",
             "rest_post_service_compliance_moduleset",
             "rest_post_service_compliance_ruleset",
        ],
        "services_actions": [
             "rest_post_services_action",
             "rest_post_services_actions",
        ],
        "sysreport": [
             "rest_post_sysreport_secure_patterns",
             "rest_post_sysreport_authorizations",
        ],
        "tags": [
             "rest_post_tags_nodes",
             "rest_post_tags_services",
             "rest_post_tag",
             "rest_post_tags",
             "rest_post_tag_node",
             "rest_post_tag_service",
        ],
        "users": [
             "rest_post_users",
             "rest_post_user",
             "rest_post_user_group",
             "rest_post_user_prefs",
             "rest_post_user_primary_group",
             "rest_post_user_filterset",
        ],
        "users_groups": [
             "rest_post_users_groups",
        ],
        "wiki": [
             "rest_post_wikis",
        ]
    }
    if prefix:
        return [globals()[h]() for h in _handlers[prefix]]
    data = []
    for l in _handlers.values():
        data += [globals()[h]() for h in l]
    return data


def get_put_handlers(prefix=None):
    _handlers = {
        "actions": [
             "rest_put_action_queue",
        ],
        "dns": [
             "rest_put_dns_domain_sync",
        ],
        "compliance": [
             "rest_put_compliance_moduleset",
             "rest_put_compliance_ruleset",
             "rest_put_compliance_ruleset_variable",
        ],
        "form_output_results": [
             "rest_put_form_output_result",
        ],
        "forms": [
             "rest_put_form",
        ],
        "obsolescence": [
             "rest_put_obsolescence_refresh",
        ],
        "provisioning_templates": [
             "rest_put_provisioning_template",
        ],
        "services": [
             "rest_put_service_action_queue",
             "rest_put_service_disks",
        ]
    }
    if prefix:
        return [globals()[h]() for h in _handlers[prefix]]
    data = []
    for l in _handlers.values():
        data += [globals()[h]() for h in l]
    return data



