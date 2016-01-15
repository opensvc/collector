//
table_comp_module_status_defaults = {
     'pager': {'page': 1},
     'extrarow': false,
     'extrarow_class': "",
     'flash': "",
     'checkboxes': false,
     'ajax_url': '/init/compliance/ajax_comp_mod_status',
     'span': ['mod_name'],
     'columns': ['mod_name', 'total', 'ok', 'nok', 'na', 'obs', 'pct', 'mod_log'],
     'colprops': {'ok': {'field': 'ok', 'filter_redirect': '', 'force_filter': '', 'img': 'compstatus', '_dataclass': '', 'title': 'Ok', '_class': 'numeric', 'table': 'comp_mod_status', 'display': 1, 'default_filter': ''}, 'nok': {'field': 'nok', 'filter_redirect': '', 'force_filter': '', 'img': 'compstatus', '_dataclass': '', 'title': 'Not Ok', '_class': 'numeric', 'table': 'comp_mod_status', 'display': 1, 'default_filter': ''}, 'na': {'field': 'na', 'filter_redirect': '', 'force_filter': '', 'img': 'compstatus', '_dataclass': '', 'title': 'N/A', '_class': 'numeric', 'table': 'comp_mod_status', 'display': 1, 'default_filter': ''}, 'pct': {'field': 'pct', 'filter_redirect': '', 'force_filter': '', 'img': 'compstatus', '_dataclass': '', 'title': 'Percent', '_class': 'comp_pct', 'table': 'comp_mod_status', 'display': 1, 'default_filter': ''}, 'mod_name': {'field': 'mod_name', 'filter_redirect': '', 'force_filter': '', 'img': 'mod16', '_dataclass': '', 'title': 'Module', '_class': '', 'table': 'comp_mod_status', 'display': 1, 'default_filter': ''}, 'mod_log': {'field': 'mod_log', 'filter_redirect': '', 'force_filter': '', 'img': 'complog', '_dataclass': '', 'title': 'History', '_class': 'comp_plot', 'table': '', 'display': 1, 'default_filter': ''}, 'total': {'field': 'total', 'filter_redirect': '', 'force_filter': '', 'img': 'compstatus', '_dataclass': '', 'title': 'Total', '_class': 'numeric', 'table': 'comp_mod_status', 'display': 1, 'default_filter': ''}, 'obs': {'field': 'obs', 'filter_redirect': '', 'force_filter': '', 'img': 'compstatus', '_dataclass': '', 'title': 'Obsolete', '_class': 'numeric', 'table': 'comp_mod_status', 'display': 1, 'default_filter': ''}},
     'volatile_filters': false,
     'child_tables': [],
     'parent_tables': ['cs0'],
     'dataable': false,
     'linkable': true,
     'dbfilterable': false,
     'filterable': true,
     'refreshable': true,
     'bookmarkable': true,
     'exportable': true,
     'columnable': true,
     'commonalityable': true,
     'headers': true,
     'wsable': false,
     'pageable': true,
     'on_change': false,
     'events': [],
     'request_vars': {}
}

function table_comp_module_status(divid, options) {
	var _options = {"id": "cms"}
	$.extend(true, _options, table_comp_module_status_defaults, options)
	_options.divid = divid
	_options.caller = "table_comp_module_status"
	table_init(_options)
}

//
table_comp_node_status_defaults = {
     'pager': {'page': 1},
     'extrarow': false,
     'extrarow_class': "",
     'flash': "",
     'checkboxes': false,
     'ajax_url': '/init/compliance/ajax_comp_node_status',
     'span': ['node_name'],
     'columns': ['node_name', 'total', 'ok', 'nok', 'na', 'obs', 'pct', 'node_log'],
     'colprops': {'ok': {'field': 'ok', 'filter_redirect': '', 'force_filter': '', 'img': 'compstatus', '_dataclass': '', 'title': 'Ok', '_class': 'numeric', 'table': 'comp_node_status', 'display': 1, 'default_filter': ''}, 'nok': {'field': 'nok', 'filter_redirect': '', 'force_filter': '', 'img': 'compstatus', '_dataclass': '', 'title': 'Not Ok', '_class': 'numeric', 'table': 'comp_node_status', 'display': 1, 'default_filter': ''}, 'na': {'field': 'na', 'filter_redirect': '', 'force_filter': '', 'img': 'compstatus', '_dataclass': '', 'title': 'N/A', '_class': 'numeric', 'table': 'comp_node_status', 'display': 1, 'default_filter': ''}, 'pct': {'field': 'pct', 'filter_redirect': '', 'force_filter': '', 'img': 'compstatus', '_dataclass': '', 'title': 'Percent', '_class': 'comp_pct', 'table': 'comp_node_status', 'display': 1, 'default_filter': ''}, 'node_name': {'field': 'node_name', 'filter_redirect': '', 'force_filter': '', 'img': 'node16', '_dataclass': '', 'title': 'Node', '_class': 'nodename', 'table': 'comp_node_status', 'display': 1, 'default_filter': ''}, 'total': {'field': 'total', 'filter_redirect': '', 'force_filter': '', 'img': 'compstatus', '_dataclass': '', 'title': 'Total', '_class': 'numeric', 'table': 'comp_node_status', 'display': 1, 'default_filter': ''}, 'obs': {'field': 'obs', 'filter_redirect': '', 'force_filter': '', 'img': 'compstatus', '_dataclass': '', 'title': 'Obsolete', '_class': 'numeric', 'table': 'comp_node_status', 'display': 1, 'default_filter': ''}, 'node_log': {'field': 'node_log', 'filter_redirect': '', 'force_filter': '', 'img': 'complog', '_dataclass': '', 'title': 'History', '_class': 'comp_plot', 'table': '', 'display': 1, 'default_filter': ''}},
     'volatile_filters': false,
     'child_tables': [],
     'parent_tables': ['cs0'],
     'dataable': false,
     'linkable': true,
     'dbfilterable': false,
     'filterable': true,
     'refreshable': true,
     'bookmarkable': true,
     'exportable': true,
     'columnable': true,
     'commonalityable': true,
     'headers': true,
     'wsable': false,
     'pageable': true,
     'on_change': false,
     'events': [],
     'request_vars': {}
}

function table_comp_node_status(divid, options) {
	var _options = {"id": "cns"}
	$.extend(true, _options, table_comp_node_status_defaults, options)
	_options.divid = divid
	_options.caller = "table_comp_node_status"
	table_init(_options)
}

//
table_comp_service_status_defaults = {
     'pager': {'page': 1},
     'extrarow': false,
     'extrarow_class': "",
     'flash': "",
     'checkboxes': false,
     'ajax_url': '/init/compliance/ajax_comp_svc_status',
     'span': ['svc_name'],
     'columns': ['svc_name', 'total', 'ok', 'nok', 'na', 'obs', 'pct', 'svc_log'],
     'colprops': {'svc_log': {'field': 'svc_log', 'filter_redirect': '', 'force_filter': '', 'img': 'complog', '_dataclass': '', 'title': 'History', '_class': 'comp_plot', 'table': '', 'display': 1, 'default_filter': ''}, 'ok': {'field': 'ok', 'filter_redirect': '', 'force_filter': '', 'img': 'compstatus', '_dataclass': '', 'title': 'Ok', '_class': 'numeric', 'table': 'comp_svc_status', 'display': 1, 'default_filter': ''}, 'nok': {'field': 'nok', 'filter_redirect': '', 'force_filter': '', 'img': 'compstatus', '_dataclass': '', 'title': 'Not Ok', '_class': 'numeric', 'table': 'comp_svc_status', 'display': 1, 'default_filter': ''}, 'na': {'field': 'na', 'filter_redirect': '', 'force_filter': '', 'img': 'compstatus', '_dataclass': '', 'title': 'N/A', '_class': 'numeric', 'table': 'comp_svc_status', 'display': 1, 'default_filter': ''}, 'pct': {'field': 'pct', 'filter_redirect': '', 'force_filter': '', 'img': 'compstatus', '_dataclass': '', 'title': 'Percent', '_class': 'comp_pct', 'table': 'comp_svc_status', 'display': 1, 'default_filter': ''}, 'total': {'field': 'total', 'filter_redirect': '', 'force_filter': '', 'img': 'compstatus', '_dataclass': '', 'title': 'Total', '_class': 'numeric', 'table': 'comp_svc_status', 'display': 1, 'default_filter': ''}, 'svc_name': {'field': 'svc_name', 'filter_redirect': '', 'force_filter': '', 'img': 'svc', '_dataclass': '', 'title': 'Service', '_class': 'svcname', 'table': 'comp_svc_status', 'display': 1, 'default_filter': ''}, 'obs': {'field': 'obs', 'filter_redirect': '', 'force_filter': '', 'img': 'compstatus', '_dataclass': '', 'title': 'Obsolete', '_class': 'numeric', 'table': 'comp_svc_status', 'display': 1, 'default_filter': ''}},
     'volatile_filters': false,
     'child_tables': [],
     'parent_tables': ['cs0'],
     'dataable': false,
     'linkable': true,
     'dbfilterable': false,
     'filterable': true,
     'refreshable': true,
     'bookmarkable': true,
     'exportable': true,
     'columnable': true,
     'commonalityable': true,
     'headers': true,
     'wsable': false,
     'pageable': true,
     'on_change': false,
     'events': [],
     'request_vars': {}
}

function table_comp_service_status(divid, options) {
	var _options = {"id": "css"}
	$.extend(true, _options, table_comp_service_status_defaults, options)
	_options.divid = divid
	_options.caller = "table_comp_service_status"
	table_init(_options)
}

//
table_comp_status_defaults = {
     'pager': {'page': 1},
     'extrarow': false,
     'extrarow_class': "",
     'flash': "",
     'checkboxes': true,
     'ajax_url': '/init/compliance/ajax_comp_status',
     'span': ['run_nodename', 'run_svcname', 'run_module'],
     'force_cols': ['id', 'os_name'],
     'columns': ['id', 'run_date', 'run_nodename', 'run_svcname', 'run_module', 'run_status', 'run_status_log', 'rset_md5', 'run_log', 'assetname', 'fqdn', 'serial', 'model', 'environnement', 'role', 'status', 'type', 'sec_zone', 'loc_country', 'loc_zip', 'loc_city', 'loc_addr', 'loc_building', 'loc_floor', 'loc_room', 'loc_rack', 'enclosure', 'enclosureslot', 'hvvdc', 'hvpool', 'hv', 'os_name', 'os_release', 'os_vendor', 'os_arch', 'os_kernel', 'cpu_dies', 'cpu_cores', 'cpu_threads', 'cpu_model', 'cpu_freq', 'mem_banks', 'mem_slots', 'mem_bytes', 'listener_port', 'version', 'action_type', 'host_mode', 'team_responsible', 'team_integ', 'team_support', 'project', 'last_boot', 'power_supply_nb', 'power_cabinet1', 'power_cabinet2', 'power_protect', 'power_protect_breaker', 'power_breaker1', 'power_breaker2', 'warranty_end', 'maintenance_end', 'os_obs_warn_date', 'os_obs_alert_date', 'hw_obs_warn_date', 'hw_obs_alert_date', 'updated'],
     'colprops': {'id': {'field': 'id', 'filter_redirect': '', 'force_filter': '', 'img': 'key', '_dataclass': '', 'title': 'Id', '_class': '', 'table': 'comp_status', 'display': 0, 'default_filter': ''}, 'enclosure': {'field': 'enclosure', 'filter_redirect': '', 'force_filter': '', 'img': 'loc', '_dataclass': '', 'title': 'Enclosure', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'status': {'field': 'status', 'filter_redirect': '', 'force_filter': '', 'img': 'node16', '_dataclass': '', 'title': 'Status', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'loc_city': {'field': 'loc_city', 'filter_redirect': '', 'force_filter': '', 'img': 'loc', '_dataclass': '', 'title': 'City', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'mem_banks': {'field': 'mem_banks', 'filter_redirect': '', 'force_filter': '', 'img': 'mem16', '_dataclass': '', 'title': 'Memory banks', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'sec_zone': {'field': 'sec_zone', 'filter_redirect': '', 'force_filter': '', 'img': 'fw16', '_dataclass': '', 'title': 'Security zone', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'os_release': {'field': 'os_release', 'filter_redirect': '', 'force_filter': '', 'img': 'os16', '_dataclass': '', 'title': 'OS release', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'mem_bytes': {'field': 'mem_bytes', 'filter_redirect': '', 'force_filter': '', 'img': 'mem16', '_dataclass': '', 'title': 'Memory', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'os_kernel': {'field': 'os_kernel', 'filter_redirect': '', 'force_filter': '', 'img': 'os16', '_dataclass': '', 'title': 'OS kernel', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'cpu_dies': {'field': 'cpu_dies', 'filter_redirect': '', 'force_filter': '', 'img': 'cpu16', '_dataclass': '', 'title': 'CPU dies', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'power_cabinet1': {'field': 'power_cabinet1', 'filter_redirect': '', 'force_filter': '', 'img': 'pwr', '_dataclass': '', 'title': 'Power cabinet #1', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'power_cabinet2': {'field': 'power_cabinet2', 'filter_redirect': '', 'force_filter': '', 'img': 'pwr', '_dataclass': '', 'title': 'Power cabinet #2', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'fqdn': {'field': 'fqdn', 'filter_redirect': '', 'force_filter': '', 'img': 'node16', '_dataclass': '', 'title': 'Fqdn', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'os_name': {'field': 'os_name', 'filter_redirect': '', 'force_filter': '', 'img': 'os16', '_dataclass': '', 'title': 'OS name', '_class': 'os_name', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'os_arch': {'field': 'os_arch', 'filter_redirect': '', 'force_filter': '', 'img': 'os16', '_dataclass': '', 'title': 'OS arch', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'rset_md5': {'field': 'rset_md5', 'filter_redirect': '', 'force_filter': '', 'img': 'comp16', '_dataclass': '', 'title': 'Ruleset md5', '_class': 'nowrap pre rset_md5', 'table': 'comp_status', 'display': 0, 'default_filter': ''}, 'assetname': {'field': 'assetname', 'filter_redirect': '', 'force_filter': '', 'img': 'node16', '_dataclass': '', 'title': 'Asset name', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'host_mode': {'field': 'host_mode', 'filter_redirect': '', 'force_filter': '', 'img': 'svc', '_dataclass': '', 'title': 'Host Mode', '_class': 'env', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'run_svcname': {'field': 'run_svcname', 'filter_redirect': '', 'force_filter': '', 'img': 'svc', '_dataclass': '', 'title': 'Service', '_class': 'svcname', 'table': 'comp_status', 'display': 1, 'default_filter': ''}, 'cpu_vendor': {'field': 'cpu_vendor', 'filter_redirect': '', 'force_filter': '', 'img': 'cpu16', '_dataclass': '', 'title': 'CPU vendor', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'os_vendor': {'field': 'os_vendor', 'filter_redirect': '', 'force_filter': '', 'img': 'os16', '_dataclass': '', 'title': 'OS vendor', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'cpu_freq': {'field': 'cpu_freq', 'filter_redirect': '', 'force_filter': '', 'img': 'cpu16', '_dataclass': '', 'title': 'CPU freq', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'run_module': {'field': 'run_module', 'filter_redirect': '', 'force_filter': '', 'img': 'mod16', '_dataclass': '', 'title': 'Module', '_class': '', 'table': 'comp_status', 'display': 1, 'default_filter': ''}, 'run_date': {'field': 'run_date', 'filter_redirect': '', 'force_filter': '', 'img': 'time16', '_dataclass': '', 'title': 'Run date', '_class': 'datetime_weekly', 'table': 'comp_status', 'display': 1, 'default_filter': ''}, 'loc_building': {'field': 'loc_building', 'filter_redirect': '', 'force_filter': '', 'img': 'loc', '_dataclass': '', 'title': 'Building', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'team_responsible': {'field': 'team_responsible', 'filter_redirect': '', 'force_filter': '', 'img': 'guys16', '_dataclass': '', 'title': 'Team responsible', '_class': 'groups', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'cpu_cores': {'field': 'cpu_cores', 'filter_redirect': '', 'force_filter': '', 'img': 'cpu16', '_dataclass': '', 'title': 'CPU cores', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'id': {'field': 'id', 'filter_redirect': '', 'force_filter': '', 'img': 'columns', '_dataclass': '', 'title': 'Id', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'node_updated': {'field': 'node_updated', 'filter_redirect': '', 'force_filter': '', 'img': 'time16', '_dataclass': '', 'title': 'Last node update', '_class': 'datetime_daily', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'power_supply_nb': {'field': 'power_supply_nb', 'filter_redirect': '', 'force_filter': '', 'img': 'pwr', '_dataclass': '', 'title': 'Power supply number', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'version': {'field': 'version', 'filter_redirect': '', 'force_filter': '', 'img': 'svc', '_dataclass': '', 'title': 'Agent version', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'loc_rack': {'field': 'loc_rack', 'filter_redirect': '', 'force_filter': '', 'img': 'loc', '_dataclass': '', 'title': 'Rack', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'team_integ': {'field': 'team_integ', 'filter_redirect': '', 'force_filter': '', 'img': 'guys16', '_dataclass': '', 'title': 'Integrator', '_class': 'groups', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'role': {'field': 'role', 'filter_redirect': '', 'force_filter': '', 'img': 'node16', '_dataclass': '', 'title': 'Role', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'run_status': {'field': 'run_status', 'filter_redirect': '', 'force_filter': '', 'img': 'compstatus', '_dataclass': '', 'title': 'Status', '_class': 'run_status', 'table': 'comp_status', 'display': 1, 'default_filter': ''}, 'type': {'field': 'type', 'filter_redirect': '', 'force_filter': '', 'img': 'node16', '_dataclass': '', 'title': 'Type', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'enclosureslot': {'field': 'enclosureslot', 'filter_redirect': '', 'force_filter': '', 'img': 'loc', '_dataclass': '', 'title': 'Enclosure Slot', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'maintenance_end': {'field': 'maintenance_end', 'filter_redirect': '', 'force_filter': '', 'img': 'time16', '_dataclass': '', 'title': 'Maintenance end', '_class': 'date_future', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'loc_zip': {'field': 'loc_zip', 'filter_redirect': '', 'force_filter': '', 'img': 'loc', '_dataclass': '', 'title': 'ZIP', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'updated': {'field': 'updated', 'filter_redirect': '', 'force_filter': '', 'img': 'time16', '_dataclass': '', 'title': 'Last node update', '_class': 'datetime_daily', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'power_protect_breaker': {'field': 'power_protect_breaker', 'filter_redirect': '', 'force_filter': '', 'img': 'pwr', '_dataclass': '', 'title': 'Power protector breaker', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'mem_slots': {'field': 'mem_slots', 'filter_redirect': '', 'force_filter': '', 'img': 'mem16', '_dataclass': '', 'title': 'Memory slots', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'nodename': {'field': 'nodename', 'filter_redirect': '', 'force_filter': '', 'img': 'node16', '_dataclass': '', 'title': 'Node name', '_class': 'nodename', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'power_protect': {'field': 'power_protect', 'filter_redirect': '', 'force_filter': '', 'img': 'pwr', '_dataclass': '', 'title': 'Power protector', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'os_obs_alert_date': {'field': 'os_obs_alert_date', 'filter_redirect': '', 'force_filter': '', 'img': 'time16', '_dataclass': '', 'title': 'OS obsolescence alert date', '_class': 'date_future', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'run_nodename': {'field': 'run_nodename', 'filter_redirect': '', 'force_filter': '', 'img': 'node16', '_dataclass': '', 'title': 'Node', '_class': 'nodename', 'table': 'comp_status', 'display': 1, 'default_filter': ''}, 'hv': {'field': 'hv', 'filter_redirect': '', 'force_filter': '', 'img': 'hv16', '_dataclass': '', 'title': 'Hypervisor', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'run_status_log': {'field': 'un_status_log', 'filter_redirect': '', 'force_filter': '', 'img': 'complog', '_dataclass': '', 'title': 'History', '_class': 'run_status_log', 'table': 'comp_status', 'display': 0, 'default_filter': ''}, 'run_log': {'field': 'run_log', 'filter_redirect': '', 'force_filter': '', 'img': 'complog', '_dataclass': '', 'title': 'Log', '_class': 'run_log', 'table': 'comp_status', 'display': 0, 'default_filter': ''}, 'cpu_model': {'field': 'cpu_model', 'filter_redirect': '', 'force_filter': '', 'img': 'cpu16', '_dataclass': '', 'title': 'CPU model', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'hvvdc': {'field': 'hvvdc', 'filter_redirect': '', 'force_filter': '', 'img': 'hv16', '_dataclass': '', 'title': 'Virtual datacenter', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'loc_country': {'field': 'loc_country', 'filter_redirect': '', 'force_filter': '', 'img': 'loc', '_dataclass': '', 'title': 'Country', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'hvpool': {'field': 'hvpool', 'filter_redirect': '', 'force_filter': '', 'img': 'hv16', '_dataclass': '', 'title': 'Hypervisor pool', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'last_boot': {'field': 'last_boot', 'filter_redirect': '', 'force_filter': '', 'img': 'time16', '_dataclass': '', 'title': 'Last boot', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'cpu_threads': {'field': 'cpu_threads', 'filter_redirect': '', 'force_filter': '', 'img': 'cpu16', '_dataclass': '', 'title': 'CPU threads', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'os_concat': {'field': 'os_concat', 'filter_redirect': '', 'force_filter': '', 'img': 'os16', '_dataclass': '', 'title': 'OS full name', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'serial': {'field': 'serial', 'filter_redirect': '', 'force_filter': '', 'img': 'node16', '_dataclass': '', 'title': 'Serial', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'listener_port': {'field': 'listener_port', 'filter_redirect': '', 'force_filter': '', 'img': 'svc', '_dataclass': '', 'title': 'Listener port', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'environnement': {'field': 'environnement', 'filter_redirect': '', 'force_filter': '', 'img': 'node16', '_dataclass': '', 'title': 'Env', '_class': 'env', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'team_support': {'field': 'team_support', 'filter_redirect': '', 'force_filter': '', 'img': 'guys16', '_dataclass': '', 'title': 'Support', '_class': 'groups', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'hw_obs_alert_date': {'field': 'hw_obs_alert_date', 'filter_redirect': '', 'force_filter': '', 'img': 'time16', '_dataclass': '', 'title': 'Hardware obsolescence alert date', '_class': 'date_future', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'loc_addr': {'field': 'loc_addr', 'filter_redirect': '', 'force_filter': '', 'img': 'loc', '_dataclass': '', 'title': 'Address', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'os_obs_warn_date': {'field': 'os_obs_warn_date', 'filter_redirect': '', 'force_filter': '', 'img': 'time16', '_dataclass': '', 'title': 'OS obsolescence warning date', '_class': 'date_future', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'hw_obs_warn_date': {'field': 'hw_obs_warn_date', 'filter_redirect': '', 'force_filter': '', 'img': 'time16', '_dataclass': '', 'title': 'Hardware obsolescence warning date', '_class': 'date_future', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'loc_room': {'field': 'loc_room', 'filter_redirect': '', 'force_filter': '', 'img': 'loc', '_dataclass': '', 'title': 'Room', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'warranty_end': {'field': 'warranty_end', 'filter_redirect': '', 'force_filter': '', 'img': 'time16', '_dataclass': '', 'title': 'Warranty end', '_class': 'date_future', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'project': {'field': 'project', 'filter_redirect': '', 'force_filter': '', 'img': 'svc', '_dataclass': '', 'title': 'Project', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'loc_floor': {'field': 'loc_floor', 'filter_redirect': '', 'force_filter': '', 'img': 'loc', '_dataclass': '', 'title': 'Floor', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'action_type': {'field': 'action_type', 'filter_redirect': '', 'force_filter': '', 'img': 'svc', '_dataclass': '', 'title': 'Action type', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'run_action': {'field': 'run_action', 'filter_redirect': '', 'force_filter': '', 'img': 'mod16', '_dataclass': '', 'title': 'Action', '_class': '', 'table': 'comp_status', 'display': 1, 'default_filter': ''}, 'model': {'field': 'model', 'filter_redirect': '', 'force_filter': '', 'img': 'node16', '_dataclass': '', 'title': 'Model', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'power_breaker1': {'field': 'power_breaker1', 'filter_redirect': '', 'force_filter': '', 'img': 'pwr', '_dataclass': '', 'title': 'Power breaker #1', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'power_breaker2': {'field': 'power_breaker2', 'filter_redirect': '', 'force_filter': '', 'img': 'pwr', '_dataclass': '', 'title': 'Power breaker #2', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}},
     'volatile_filters': false,
     'child_tables': ['cms', 'cns', 'css'],
     'parent_tables': [],
     'dataable': true,
     'linkable': true,
     'dbfilterable': true,
     'filterable': true,
     'refreshable': true,
     'bookmarkable': true,
     'exportable': true,
     'columnable': true,
     'commonalityable': true,
     'headers': true,
     'wsable': true,
     'pageable': true,
     'on_change': false,
     'events': ['comp_status_change'],
     'request_vars': {}
}

function table_comp_status(divid, options) {
	var _options = {"id": "cs0"}
	$.extend(true, _options, table_comp_status_defaults, options)
	_options.divid = divid
	_options.caller = "table_comp_status"
	return table_init(_options)
}

function comp_status_agg(divid, options) {
	var t = options.table
	var data = {
	  "table_id": t.id
	}
	for (c in t.colprops) {
		var current = $("#"+t.id+"_f_"+c).val()
		if ((current != "") && (typeof current !== 'undefined')) {
			data[t.id+"_f_"+c] = current
		} else if (t.colprops[c].force_filter != "") {
			data[t.id+"_f_"+c] = t.colprops[c].force_filter
		}
	}
	$.getJSON("/init/compliance/call/json/json_comp_status_agg", data, function(data) {
			var total = data.ok + data.nok + data.obs + data.na
			if (total == 0) {
				var p_ok = 0
				var p_nok = 0
				var p_obs = 0
				var p_na = 0
				var fp_ok = "0%"
				var fp_nok = "0%"
				var fp_obs = "0%"
				var fp_na = "0%"
			} else {
				var fp_ok = 100 * data.ok / total
				var fp_nok = 100 * data.nok / total
				var fp_obs = 100 * data.obs / total
				var fp_na = 100 * data.na / total
				var p_ok = fp_ok.toFixed(0) + "%"
				var p_nok = fp_nok.toFixed(0) + "%"
				var p_obs = fp_obs.toFixed(0) + "%"
				var p_na = fp_na.toFixed(0) + "%"
				var fp_ok = fp_ok.toFixed(1) + "%"
				var fp_nok = fp_nok.toFixed(1) + "%"
				var fp_obs = fp_obs.toFixed(1) + "%"
				var fp_na = fp_na.toFixed(1) + "%"
			}
			var d1 = $("<div style='margin:auto;text-align:center;width:100%'></div>")
			var d2 = $("<div style='text-align:left;margin:2px auto;background:#FF7863;overflow:hidden'></div>")
			var d3 = $("<div></div>")

			var div_obs = $("<div style='font-size:0;line-height:0;height:8px;float:left;min-width:0%;background:#15367A'></div>")
			div_obs.css({"max-width": p_obs, "width": p_obs})
			var div_ok = $("<div style='font-size:0;line-height:0;height:8px;float:left;min-width:0%;background:#3aaa50'></div>")
			div_ok.css({"max-width": p_ok, "width": p_ok})
			var div_na = $("<div style='font-size:0;line-height:0;height:8px;float:left;min-width:0%;background:#acacac'></div>")
			div_na.css({"max-width": p_na, "width": p_na})

			var span_obs = $("<span style='color:#15367A;padding:3px'></span>")
			span_obs.text(data.obs + " (" + fp_obs + ") " + i18n.t("views.comp_status.obs"))
			var span_ok = $("<span style='color:#3aaa50;padding:3px'></span>")
			span_ok.text(data.ok + " (" + fp_ok + ") " + i18n.t("views.comp_status.ok"))
			var span_na = $("<span style='color:#acacac;padding:3px'></span>")
			span_na.text(data.na + " (" + fp_na + ") " + i18n.t("views.comp_status.na"))
			var span_nok = $("<span style='color:#FF7863;padding:3px'></span>")
			span_nok.text(data.nok + " (" + fp_nok + ") " + i18n.t("views.comp_status.nok"))

			d1.append(d2)
			d1.append(d3)
                        d2.append(div_obs)
                        d2.append(div_ok)
                        d2.append(div_na)
                        d3.append(span_obs)
                        d3.append(span_ok)
                        d3.append(span_na)
                        d3.append(span_nok)
			$("#"+divid).html(d1)
	})
}

function view_comp_status(divid, options) {
	var o = {}
	$("#"+divid).load("/init/static/views/comp_status.html", function() {
		$(this).i18n()
		var t = table_comp_status("cs0", options)
		t.options.on_change = function() {
			comp_status_agg("agg", {"table": t})
		}
		$("#cms_a").bind("click", function() {
			if (!$("#cms").is(":visible")) {
				$(this).addClass("down16")
				$(this).removeClass("right16")
				$("#cms").show()
				table_comp_module_status("cms", options)
			} else {
				$(this).addClass("right16")
				$(this).removeClass("down16")
				$("#cms").hide()
			}
		})
		$("#cns_a").bind("click", function() {
			if (!$("#cns").is(":visible")) {
				$(this).addClass("down16")
				$(this).removeClass("right16")
				$("#cns").show()
				table_comp_node_status("cns", options)
			} else {
				$(this).addClass("right16")
				$(this).removeClass("down16")
				$("#cns").hide()
			}
		})
		$("#css_a").bind("click", function() {
			if (!$("#css").is(":visible")) {
				$(this).addClass("down16")
				$(this).removeClass("right16")
				$("#css").show()
				table_comp_service_status("css", options)
			} else {
				$(this).addClass("right16")
				$(this).removeClass("down16")
				$("#css").hide()
			}
		})
	})

}

function comp_status_log_on_hover(t) {
	t.div.find("[name$=_c_run_status]").hover(
	function() {
		line = $(this).parents("tr")
		var s = line.children("[name$=_c_run_status]")
		var e = line.children("[name$=_c_run_log]")
		var pos = s.position()
		e.width($(window).width()*0.8)
		e.css({"left": pos.left - e.width() - 10 + "px", "top": pos.top+s.parent().height() + "px"})
		e.addClass("white_float")
		cell_decorator_run_log(e)
		e.show()
	},
	function() {
		$(this).parents("tr").children("[name$=_c_run_log]").hide()
	})
}

function table_comp_status_node(divid, nodename) {
	var id = "cs_node_" + nodename.replace(/[\.-]/g, "_")
	var f = id+"_f_run_nodename"
	var request_vars = {}
	request_vars[f] = nodename

	t = table_comp_status(divid, {
		"id": id,
		"caller": "table_comp_status_node",
		"request_vars": request_vars,
		"volatile_filters": true,
		"bookmarkable": false,
		"refreshable": false,
		"linkable": false,
		"exportable": false,
		"pageable": false,
		"columnable": false,
		"commonalityable": false,
		"filterable": false,
		"wsable": false,
		"force_cols": ['id', 'os_name', 'run_log'],
		"visible_columns": ['run_date', 'run_svcname', 'run_module', 'run_status']
	})
	t.on_change = function() {
		comp_status_log_on_hover(t)
	}
	return t
}

function table_comp_status_svc(divid, svcname) {
	var id = "cs_svc_" + svcname.replace(/[\.-]/g, "_")
	var f = id+"_f_run_svcname"
	var request_vars = {}
	request_vars[f] = svcname

	t = table_comp_status(divid, {
		"id": id,
		"caller": "table_comp_status_svc",
		"request_vars": request_vars,
		"volatile_filters": true,
		"bookmarkable": false,
		"refreshable": false,
		"linkable": false,
		"exportable": false,
		"pageable": false,
		"columnable": false,
		"commonalityable": false,
		"filterable": false,
		"wsable": false,
		"force_cols": ['id', 'os_name', 'run_log'],
		"visible_columns": ['run_date', 'run_nodename', 'run_module', 'run_status']
	})
	t.on_change = function() {
		comp_status_log_on_hover(t)
	}
	return t
}


