import re
import pydal

deprecated_columns = {
  "services.svc_envfile": "services.svc_config",
  "services.svc_envdate": "services.svc_config_updated",
  "services.svc_type": "services.svc_env",
  "nodes.host_mode": "nodes.node_env",
  "nodes.environnement": "nodes.asset_env",
}

def convert_bool(v):
    if v in ("True", "true", True, "y", "Y", "yes", "Yes", "1"):
        return True
    else:
        return False

def markup_result(result, markup):
    for p in ("info", "error"):
        if p in result:
            if type(result[p]) == list:
                for i, s in enumerate(result[p]):
                    result[p][i] = "%s: %s" % (markup, s)
            else:
                result[p] = "%s: %s" % (markup, result[p])
    return result

def merge_results(result, _result):
    if "ret" not in result:
        if "ret" not in _result:
            pass
        else:
            result["ret"] = _result["ret"]
    else:
        if "ret" not in _result:
            pass
        else:
            result["ret"] += _result["ret"]
    for p in ("info", "error"):
        if p not in result:
            if p not in _result:
                continue
            else:
                result[p] = _result[p]
        else:
            if p not in _result:
                continue
            else:
                if result[p] != list:
                    result[p] = [result[p]]
                if _result[p] != list:
                    _result[p] = [_result[p]]
                result[p] += _result[p]
    for p in _result:
        if p in ("info", "error", "ret"):
            continue
        if p not in result:
            result[p] = _result[p]
    return result

def get_handlers(action=None, prefix=None):
    if action == "GET":
        return get_get_handlers(prefix=prefix)
    elif action == "POST":
        return get_post_handlers(prefix=prefix)
    elif action == "DELETE":
        return get_delete_handlers(prefix=prefix)
    elif action == "PUT":
        return get_put_handlers(prefix=prefix)
    else:
        return {
            "GET": get_get_handlers(),
            "POST": get_post_handlers(),
            "DELETE": get_delete_handlers(),
            "PUT": get_put_handlers(),
        }

def get_handler(action, url):
    """ Support url with or without the leading /
    """
    url = url.lstrip("/")
    prefix = url.split("/")[0]
    for handler in get_handlers(action, prefix):
        if handler.match("/"+url):
            return handler

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
             "rest_get_array_diskgroups",
             "rest_get_array_diskgroup",
             "rest_get_array_diskgroup_quota",
             "rest_get_array_diskgroup_quotas",
             "rest_get_array_proxies",
             "rest_get_array_targets",
       ],
       "checks": [
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
       "nodes": [
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
       ],
       "resources": [
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
             "rest_get_service_nodes",
             "rest_get_service_node",
             "rest_get_service_node_resources",
             "rest_get_service_node_resources_logs",
             "rest_get_service_resources",
             "rest_get_service_resources_logs",
             "rest_get_service_tags",
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
             "rest_get_user_dump",
             "rest_get_user_apps_publication",
             "rest_get_user_apps_responsible",
             "rest_get_user_nodes",
             "rest_get_user_services",
             "rest_get_user_groups",
             "rest_get_user_hidden_menu_entries",
             "rest_get_user_primary_group",
             "rest_get_user_filterset",
             "rest_get_user_table_settings",
             "rest_get_user_table_filters",
       ],
       "reports": [
             "rest_get_reports_charts",
             "rest_get_reports_chart",
             "rest_get_reports_metrics",
             "rest_get_reports_metric",
             "rest_get_reports_metric_samples",
             "rest_get_reports_chart_samples",
             "rest_get_report_definition",
             "rest_get_report_export",
             "rest_get_reports",
             "rest_get_report",
       ],
       "safe": [
             "rest_get_safe",
             "rest_get_safe_file",
             "rest_get_safe_file_am_i_responsible",
             "rest_get_safe_file_download",
             "rest_get_safe_file_preview",
             "rest_get_safe_file_publications",
             "rest_get_safe_file_responsibles",
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
        ],
        "checks": [
             "rest_delete_checks_settings",
             "rest_delete_checks_setting",
             "rest_delete_checks_contextual_settings",
             "rest_delete_checks_contextual_setting",
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
             "rest_delete_reports_charts",
             "rest_delete_reports_metric",
             "rest_delete_reports_metrics",
             "rest_delete_reports",
             "rest_delete_report",
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
             "rest_delete_safe_file_publication",
             "rest_delete_safe_file_responsible",
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
             "rest_delete_user_table_filters",
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
             "rest_post_array_diskgroup_quotas",
             "rest_post_array_diskgroup_quota",
        ],
        "checks": [
             "rest_post_checks_contextual_settings",
             "rest_post_checks_contextual_setting",
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
             "rest_post_network_segment",
             "rest_post_network_segments",
             "rest_post_network_segment_responsible",
        ],
        "nodes": [
             "rest_post_nodes",
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
             "rest_post_reports_charts",
             "rest_post_reports_metric",
             "rest_post_reports_metrics",
             "rest_post_reports_import",
             "rest_post_reports",
             "rest_post_report",
        ],
        "safe": [
             "rest_post_safe_files_publications",
             "rest_post_safe_files_responsibles",
             "rest_post_safe_upload",
             "rest_post_safe_file",
             "rest_post_safe_file_publication",
             "rest_post_safe_file_responsible",
        ],
        "scheduler": [
             "rest_post_scheduler_task",
             "rest_post_scheduler_run",
        ],
        "services": [
             "rest_post_services",
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
             "rest_post_user_primary_group",
             "rest_post_user_filterset",
             "rest_post_user_table_settings",
             "rest_post_user_table_filters",
             "rest_post_user_table_filters_load_bookmark",
             "rest_post_user_table_filters_save_bookmark",
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
        ]
    }
    if prefix:
        return [globals()[h]() for h in _handlers[prefix]]
    data = []
    for l in _handlers.values():
        data += [globals()[h]() for h in l]
    return data


class rest_handler(object):
    def __init__(self,
                 action="GET",
                 path=None,
                 tables=[],
                 dbo=None,
                 props_blacklist=[],
                 vprops={},
                 vprops_fn=None,
                 count_prop="id",
                 q=None,
                 left=None,
                 groupby=None,
                 orderby=None,
                 replication=["local"],
                 allow_fset_id=False,
                 _cache=None,
                 desc=[], params={}, examples=[], data={}):
        self._cache = _cache
        self.action = action
        self.path = path
        self.tables = tables
        self.props_blacklist = props_blacklist
        self.desc = desc
        self.examples = examples
        self.init_params = params
        self.init_data = data
        self.count_prop = count_prop
        self.vprops = vprops
        self.vprops_fn = vprops_fn
        self.q = q
        self.left = left
        self.groupby = groupby
        self.orderby = orderby
        self.replication = replication
        self.allow_fset_id = allow_fset_id
        if dbo:
            self.db = dbo
        else:
            self.db = db


    def update_parameters(self):
        self.params = copy.copy(self.init_params)

    def set_q(self, q):
        self.q = q

    def get_pattern(self):
        return "^"+re.sub("\<[-\w]+\>", "[\#\:=% ><@\.\-\w\(\){slash,percent}*]+", self.path)+"$"

    def match(self, args):
        pattern = self.get_pattern()
        regexp = re.compile(pattern)
        return regexp.match(args)

    def replication_relay(self, collector, data):
        p = get_proxy(collector, controller="rest")
        try:
            ret = p.relay_rest_request(auth.user_id, self.action, self.path, data)
            ret = markup_result(ret, collector)
            return ret
        except Exception as e:
            return {"ret": 1, "error": "remote collector %s raised %s" % (collector, str(e))}

    def replication_pull(self, collectors):
        for collector in collectors:
            pull_all_table_from_remote(collector)

    def get_svc_collectors(self, svc_id):
        q = db.svcmon.svc_id == svc_id
        q &= db.svcmon.node_id == db.nodes.node_id
        rows = db(q).select(db.nodes.collector, groupby=db.nodes.collector)
        return [r.collector for r in rows if r.collector is not None]

    def get_node_collectors(self, node_id):
        q = db.nodes.node_id == node_id
        node = db(q).select(db.nodes.collector).first()
        if node is None:
            return []
        if node.collector is None:
            return []
        return [node.collector]

    def get_collectors(self, *args, **vars):
        try:
            if "node_id" in vars:
                return self.get_node_collectors(get_node_id(vars["node_id"]))
            if "nodes" in args:
                idx = args.index("nodes")
                if len(args) > idx+1:
                    return self.get_node_collectors(get_node_id(args[idx+1]))
            if "svc_id" in vars:
                return self.get_svc_collectors(get_svc_id(vars["svc_id"]))
            if "services" in args:
                idx = args.index("services")
                if len(args) > idx+1:
                    return self.get_svc_collectors(get_svc_id(args[idx+1]))
        except:
            # object not found
            return []
        return []

    def handle(self, *args, **vars):
        if "local" not in self.replication and "relay" not in self.replication:
            return {"ret": 1, "error": "both local and remote handler skipped"}

        result = {}

        if "pull" in self.replication or "relay" in self.replication:
            collectors = self.get_collectors(*args, **vars)

        for repl_action in self.replication:
            if repl_action == "relay":
                for collector in collectors:
                    _result = self.replication_relay(collector, [args, vars])
                    result = merge_results(result, _result)
            elif repl_action == "pull":
                self.replication_pull(collectors)
            elif repl_action == "local":
                _result = self.handle_local(*args, **vars)
                result = merge_results(result, _result)

        return result

    def handle_local(self, *args, **vars):
        response.headers["Content-Type"] = "application/json"
        # extract args from the path
        # /a/<b>/c/<d> => [b, d]
        nargs = []
        for i, a in enumerate(self.path.rstrip("/").split("/")):
            if a.startswith("<") and a.endswith(">"):
                nargs.append(args[i-1])
        if "filters[]" in vars:
            if "filters" in vars:
                vars["filters"] += vars["filters[]"]
            else:
                vars["filters"] = vars["filters[]"]
            del(vars["filters[]"])

        if self._cache is None:
            return self.handler(*nargs, **vars)
        if self._cache is True:
            time_expire = 14400
        elif type(self._cache) == int:
            time_expire = self._cache
        key = self.get_cache_key(*nargs, **vars)
        return cache.redis(key, lambda: self.handler(*nargs, **vars), time_expire=time_expire)

    def cache_clear(self, keys):
        for key in keys:
            cache.redis.clear(regex="rest:.*:"+key+":.*")

    def get_cache_key(self, *nargs, **vars):
        import json
        from hashlib import md5
        sign = md5(json.dumps({"args": nargs, "vars": vars})).hexdigest()
        key = "rest:%s:%s:%s" % (auth.user_id, type(self).__name__, sign)
        return key

    def prepare_data(self, **vars):
        add_to_vars = [
          "q",
          "orderby",
          "groupby",
          "left",
          "vprops",
          "vprops_fn",
          "count_prop",
          "props_blacklist",
          "tables",
          "db"
        ]

        if "fset-id" in vars:
            del(vars["fset-id"])

        if "orderby" in vars:
            cols, translations = props_to_cols(vars["orderby"], tables=self.tables, blacklist=self.props_blacklist, db=self.db)
            if len(cols) == 0:
                pass
            else:
                add_to_vars.remove("orderby")
                o = cols[0]
                if len(cols) > 1:
                   for col in cols[1:]:
                       o |= col
                vars["orderby"] = o

        for v in add_to_vars:
            if hasattr(self, v) and vars.get(v) is None:
                vars[v] = getattr(self, v)
        return prepare_data(**vars)

    def handler(self, **vars):
        return self.prepare_data(**vars)

    def update_data(self):
        self.data = {}
        if type(self.init_data) in (str, unicode):
            for i in re.findall("\*\*(\w+)\*\*", self.init_data):
                self.data[i] = {"desc": ""}
        elif type(self.init_data) == dict:
                self.data.update(self.init_data)
        if len(self.tables) == 0 or self.action not in ("POST", "PUT"):
            return
        for prop in all_props(tables=self.tables, vprops=self.vprops, blacklist=self.props_blacklist, db=self.db):
            if prop in self.data:
                # init data takes precedence
                continue

            v = prop.split(".")
            if len(v) == 2:
                _table, _prop = v
            else:
                _table = self.tables[0]
                _prop = prop
            if _prop == "id":
                continue
            colprops = globals().get(_table+"_colprops", {}).get(_prop, {})
            if colprops is None:
                colprops = globals().get("v_"+_table+"_colprops", {}).get(_prop, {})

            self.data[prop] = {
              "desc":  getattr(colprops, "title") if hasattr(colprops, "title") else "",
              "img":  getattr(colprops, "img") if hasattr(colprops, "img") else "",
              "type": self.db[_table][_prop].type,
              "table": _table,
              #"requires": self.db[_table][_prop].requires,
              #"default": self.db[_table][_prop].default,
              "unique": self.db[_table][_prop].unique,
              "writable": self.db[_table][_prop].writable,
            }

    def fmt_props_props_desc(self):
        cols, translations = props_to_cols(None, tables=self.tables, blacklist=self.props_blacklist, db=self.db)
        props = cols_to_props(cols, self.tables)
        s = """
A list of properties to include in each data dictionnary.

If omitted, all properties are included.

The separator is ','.

Available properties are: ``%(props)s``:green.

""" % dict(props=", ".join(sorted(props)))
        return s

    def handle_list(self, data, args, vars):
        rdata = {
          "info": [],
          "error": [],
          "data": [],
        }
        for entry in data:
            if type(entry) != dict:
                rdata["error"].append("skip '%s': not a dict" % str(entry))
                continue
            try:
                r = rest_handler.handle(self, *args, **entry)
            except Exception as e:
                r = dict(error=str(e))
            for key in ("info", "error", "data"):
               if key in r:
                   d = r[key]
                   if type(d) == list:
                       rdata[key] += d
                   else:
                       rdata[key] += [d]
        return rdata

class rest_post_handler(rest_handler):
    def __init__(self, **vars):
        vars["action"] = "POST"
        rest_handler.__init__(self, **vars)

    def handle(self, *args, **vars):
        response.headers["Content-Type"] = "application/json"
        if request.env.http_content_type and "application/json" in request.env.http_content_type:
            try:
                data = json.loads(request.body.read())
            except:
                return rest_handler.handle(self, *args, **vars)
            if type(data) == list:
                return self.handle_list(data, args, vars)
            elif type(data) == dict:
                return rest_handler.handle(self, *args, **data)
        if "filters" in vars and hasattr(self, "get_handler"):
            return self.handle_multi_update(*args, **vars)
        if "query" in vars and hasattr(self, "get_handler"):
            return self.handle_multi_update(*args, **vars)
        return rest_handler.handle(self, *args, **vars)

    def handle_multi_update(self, *args, **vars):
        _vars = {
          "limit": 0,
          "props": self.update_one_param,
        }
        if "query" in vars:
            _vars["query"] = vars["query"]
            del(vars["query"])
        if "filters" in vars:
            _vars["filters"] = vars["filters"]
            del(vars["filters"])
        l = self.get_handler.handler(**vars)["data"]
        result = {"data": []}
        for e in l:
            try:
                r = self.update_one_handler.handler(e.get(self.update_one_param), **vars)
                result["data"] += r["data"] if "data" in r else r
            except Exception as ex:
                d = {"error": str(ex)}
                d[self.update_one_param] = e[self.update_one_param]
                result["data"] += [d]
        return result

    def update_parameters(self):
        self.params = copy.copy(self.init_params)
        if len(self.tables) == 0:
            return
        self.params.update({
          "filters": {
            "desc": """
An opensvc property values filter.

""",
          },
          "query": {
            "desc": """
A web2py smart query.

""",
          },
        })


class rest_put_handler(rest_handler):
    def __init__(self, **vars):
        vars["action"] = "PUT"
        rest_handler.__init__(self, **vars)

    def handle(self, *args, **vars):
        response.headers["Content-Type"] = "application/json"
        if request.env.http_content_type and "application/json" in request.env.http_content_type:
            try:
                data = json.loads(request.body.read())
            except:
                return rest_handler.handle(self, *args, **vars)
            if type(data) == list:
                return self.handle_list(data, args, vars)
            elif type(data) == dict:
                return rest_handler.handle(self, *args, **data)
        if "filters" in vars and hasattr(self, "get_handler"):
            return self.handle_multi_update(*args, **vars)
        if "query" in vars and hasattr(self, "get_handler"):
            return self.handle_multi_update(*args, **vars)
        return rest_handler.handle(self, *args, **vars)


class rest_delete_handler(rest_handler):
    def __init__(self, **vars):
        vars["action"] = "DELETE"
        rest_handler.__init__(self, **vars)

    def handle(self, *args, **vars):
        response.headers["Content-Type"] = "application/json"
        if request.env.http_content_type and "application/json" in request.env.http_content_type:
            try:
                data = json.loads(request.body.read())
            except:
                return rest_handler.handle(self, *args, **vars)
            if type(data) == list:
                return self.handle_list(data, args, vars)
            elif type(data) == dict:
                return rest_handler.handle(self, *args, **data)
        return rest_handler.handle(self, *args, **vars)

    def update_parameters(self):
        self.params = copy.copy(self.init_params)

    def update_data(self):
        self.data = copy.copy(self.init_data)

class rest_get_handler(rest_handler):
    def __init__(self, **vars):
        vars["action"] = "GET"
        rest_handler.__init__(self, **vars)

    def update_data(self):
        self.data = copy.copy(self.init_data)

class rest_get_table_handler(rest_handler):
    def __init__(self, **vars):
        vars["action"] = "GET"
        rest_handler.__init__(self, **vars)

    def update_parameters(self):
        self.params = copy.copy(self.init_params)
        self.params.update({
          "commonality": {
            "desc": """
Controls the inclusion in the returned dictionnary of a "commonality" key, containing the selected properties most frequent value with its occurence percentile.
* true: include.
* false: do not include.
""",
          },
          "stats": {
            "desc": """
Controls the inclusion in the returned dictionnary of a "stats" key, containing the selected properties distinct values counts.
* true: include.
* false: do not include.
""",
          },
          "meta": {
            "desc": """
Controls the inclusion in the returned dictionnary of a "meta" key, whose parameter is a dictionnary containing the following properties: displayed entry count, total entry count, displayed properties, available properties, offset and limit.
* true: include.
* false: do not include.

""",
          },
          "limit": {
            "desc": """
The maximum number of entries to return. 0 means no limit.

""",
          },
          "offset": {
            "desc": """
Skip the first <offset> entries of the data cursor.

""",
          },
          "query": {
            "desc": """
A web2py smart query

""",
          },
          "filters": {
            "type": "list",
            "desc": """
An opensvc property values filter. Example: "updated>-2d".

""",
          },
          "orderby": {
            "desc": """
A comma-separated list of properties.

Sort the resultset using the specified properties.

Property sorting priority decreases from left to right.

The order is descending by default.

A property can be prefixed by '~' to activate the ascending order.

""",
          },
          "props": {
            "desc": self.fmt_props_props_desc(),
          },
        })
        if self.allow_fset_id:
            self.params.update({
              "fset-id": {
                "desc": "Filter the list using the filterset identified by fset-id."
              }
            })

    def update_data(self):
        self.data = copy.copy(self.init_data)


class rest_get_line_handler(rest_handler):
    def __init__(self, **vars):
        vars["action"] = "GET"
        rest_handler.__init__(self, **vars)

    def update_parameters(self):
        self.params = copy.copy(self.init_params)
        self.params.update({
          "props": {
            "desc": self.fmt_props_props_desc(),
          },
        })

    def update_data(self):
        self.data = copy.copy(self.init_data)

    def prepare_data(self, **vars):
        vars["meta"] = False
        vars["stats"] = False
        vars["commonality"] = False
        if "filters" in vars:
            del(vars["filters"])
        if "query" in vars:
            del(vars["query"])
        return rest_handler.prepare_data(self, **vars)

def data_commonality(cols, data):
    total = len(data)
    data = data_stats(cols, data)["data"]
    top = []
    for col in data:
        l = data[col].items()
        if len(l) == 0:
            continue
        l.sort(lambda x, y: cmp(x[1], y[1]), reverse=True)
        v, n = l[0]
        pct = 100*n//total
        if pct == 0 or n == 1:
            continue
        top.append({
          "prop": col,
          "value": v,
          "percent": pct,
        })
    top.sort(lambda x, y: cmp(x["percent"], y["percent"]), reverse=True)
    return dict(data=top)

def data_stats(cols, data):
    h = {}
    if len(data) == 0:
        return dict(data=h)
    for c in cols:
        _col = ".".join((c.table._tablename, c.name))
        if _col not in data[0]:
            _col = c.name
        h[_col] = {}
        for d in data:
            val = d[_col]
            if val is None or val == "":
                val = 'empty'
            elif type(val) == datetime.datetime:
                val = val.strftime("%Y-%m-%d %H:%M:%S")
            elif type(val) == datetime.date:
                val = val.strftime("%Y-%m-%d")
            if val not in h[_col]:
                h[_col][val] = 1
            else:
                h[_col][val] += 1
    return dict(data=h)

def prepare_data(
     meta=True,
     count_prop=None,
     query=None,
     stats=False,
     commonality=False,
     filters=[],
     props=None,
     vprops={},
     vprops_fn=None,
     props_blacklist=[],
     tables=[],
     data=None,
     q=None,
     db=db,
     groupby=None,
     orderby=None,
     left=None,
     cols=[],
     offset=0,
     limit=20,
     total=None):

    validated_props = []
    if left is None:
        left = []
    elif type(left) == pydal.objects.Expression:
        left = [left]
    elif type(left) == tuple:
        left = list(left)
    elif type(left) == list:
        pass
    else:
        raise Exception("invalid 'left' parameter type: %s" % type(left))

    if props is not None:
        for i, prop in enumerate(props.split(",")):
            if "." in prop:
                t, c = prop.split(".")
            elif prop in vprops:
                validated_props.append(prop)
                continue
            else:
                validated_props.append(tables[0]+"."+prop)
                continue
            if t in tables:
                validated_props.append(prop)
                continue
            if t == "nodes":
                for table in tables:
                    if "node_id" in db[table].fields:
                        left.append(db.nodes.on(db.nodes.node_id==db[table].node_id))
                        tables.append("nodes")
                        validated_props.append(prop)
                        break
            elif t == "services":
                for table in tables:
                    if "svc_id" in db[table].fields:
                        left.append(db.services.on(db.services.svc_id==db[table].svc_id))
                        tables.append("services")
                        validated_props.append(prop)
                        break
        props = ",".join(validated_props)

    all_cols, translations = props_to_cols(None, tables=tables, blacklist=props_blacklist, db=db)
    cols, translations = props_to_cols(props, tables=tables, vprops=vprops, blacklist=props_blacklist, db=db)
    false_values = ("0", "f", "F", "False", "false", False)

    if meta in false_values:
        meta = False
    else:
        meta = True
    if stats in false_values:
        stats = False
    else:
        stats = True
        limit = 0
    if commonality in false_values:
        commonality = False
    else:
        commonality = True
        limit = 0
    if not data and q:
        if type(filters) in (str, unicode):
            filters = [filters]
        for f in filters:
            f_prop = re.findall(r'\w+', f)[0]
            f_val = f[len(f_prop):].strip()
            if '.' in f_prop:
                t, f_col = f_prop.split(".")
            else:
                t = tables[0]
                f_col = f_prop
            q = _where(q, t, f_val, f_col, db=db)
        if query:
            try:
                q &= pydal.helpers.methods.smart_query(all_cols, query)
            except Exception as e:
                raise Exception(T("smart query error for '%(s)s': %(err)s", dict(s=str(query), err=str(e))))
        if meta:
            if count_prop:
                try:
                    table, prop = count_prop.split(".")
                except:
                    table = tables[0]
                    prop = count_prop
                count_col = db[table][prop].count()
            else:
                count_col = cols[0].count()
            if groupby:
                total = len(db(q).select(count_col, groupby=groupby, left=left))
            else:
                total = db(q).select(count_col, left=left).first()._extra[count_col]

        limit = int(limit)
        offset = int(offset)

        if limit == 0:
            # no limit. should we limit this to a priv group ?
            limitby = (offset, 2**20)
        else:
            limitby = (offset, offset + limit)

        data = db(q).select(
                       *cols,
                       cacheable=True,
                       left=left,
                       groupby=groupby,
                       orderby=orderby,
                       limitby=limitby
                     ).as_list()
    else:
        return dict(error="failed to prepare data: missing parameter")

    data = mangle_data(data, props=props, vprops=vprops, vprops_fn=vprops_fn)

    # reverve to deprecated column name
    if len(translations) > 0:
        for orig, translated in translations:
            short_orig = orig.split(".")[-1]
            short_translated = translated.split(".")[-1]
            for i, d in enumerate(data):
                if short_translated in data[i]:
                    data[i][short_orig] = data[i][short_translated]
                    del(data[i][short_translated])
                else:
                    data[i][orig] = data[i][translated]
                    del(data[i][translated])

    if stats:
        return data_stats(cols, data)
    if commonality:
        return data_commonality(cols, data)
    if meta:
        _cols = [".".join((c.table._tablename, c.name)) for c in cols]
        if props is None:
            _cols += vprops.keys()
        else:
            _cols += list(set(props.split(",")) & set(vprops.keys()))
            for _vprops in vprops.values():
                for prop in _vprops:
                    if prop in _cols and prop not in props.split(","):
                        _cols.remove(prop)
                    if len(tables) == 1:
                        prop = tables[0] + "." + prop
                        if prop in _cols and prop not in props.split(","):
                            _cols.remove(prop)
        _all_cols = [".".join((c.table._tablename, c.name)) for c in all_cols] + vprops.keys()
        meta = dict(
                 included_props=_cols,
                 available_props=_all_cols,
                 offset=offset,
                 limit=limit,
                 total=total,
                 count=len(data),
                 server_timezone=config_get("server_timezone", "Europe/Paris"),
               )
        d = dict(data=data, meta=meta)
    else:
        d = dict(data=data)

    return d

def mangle_data(data, props=None, vprops={}, vprops_fn=None):
    if vprops_fn is None:
        return data
    if props and len(set(vprops) & set(props.split(","))) == 0:
        return data
    data = vprops_fn(data)

    # purge props used to produce vprops
    props_to_purge = set([])
    for _vprops in vprops.values():
        props_to_purge |= set(_vprops)
    if props is not None:
        # unless the user expressly requested them
        props_to_purge -= set(props.split(","))
    for i, d in enumerate(data):
        for prop in props_to_purge:
            del(data[i][prop])
    return data

def all_props(tables=[], blacklist=[], vprops={}, db=db):
    cols, translations = props_to_cols(None, tables=tables, blacklist=blacklist, db=db)
    return cols_to_props(cols, tables=tables) + vprops.values()

def props_to_cols(props, tables=[], vprops={}, blacklist=[], db=db):
    if props is None:
        cols = []
        for table in tables:
            bl = [f.split(".")[-1] for f in blacklist if f.startswith(table+".") or "." not in f]
            for p in set(db[table].fields) - set(bl):
                cols.append(db[table][p])
        return cols, []
    cols = []
    props = set(props.split(",")) - set(vprops.keys())
    for _vprops in vprops.values():
        props |= set(_vprops)
    translations = []
    for p in props:
        if p[0] == "~":
            desc = True
            p = p[1:]
        else:
            desc = False
        v = p.split(".")
        if len(v) == 1 and len(tables) == 1:
            v = [tables[0], p]

        # deprecated columns translation
        fullp = '.'.join(v)
        translated = False
        while fullp in deprecated_columns:
            fullp = deprecated_columns[fullp]
            translated = True
        if translated:
            translations.append(('.'.join(v), fullp))
            v = fullp.split(".")

        try:
            col = db[v[0]][v[1]]
        except Exception as e:
            raise Exception("prop %s does not exist for %s" % (v[1], v[0]))

        if desc:
            col = ~col
        cols.append(col)
    return cols, translations

def cols_to_props(cols, tables):
    if len(tables) > 1:
        multi = True
    else:
        multi = False
    props = [".".join((c.table._tablename, c.name)) if multi else c.name for c in cols]
    return props



