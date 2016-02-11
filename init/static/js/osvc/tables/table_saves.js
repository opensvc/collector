table_saves_defaults = {
     'pager': {'page': 1},
     'extrarow': false,
     'extrarow_class': "",
     'flash': "",
     'checkboxes': false,
     'ajax_url': '/init/saves/ajax_saves',
     'span': ['assetname', 'fqdn', 'serial', 'model', 'environnement', 'role', 'status', 'type', 'sec_zone', 'loc_country', 'loc_zip', 'loc_city', 'loc_addr', 'loc_building', 'loc_floor', 'loc_room', 'loc_rack', 'enclosure', 'enclosureslot', 'hvvdc', 'hvpool', 'hv', 'os_name', 'os_release', 'os_vendor', 'os_arch', 'os_kernel', 'os_concat', 'cpu_dies', 'cpu_cores', 'cpu_threads', 'cpu_model', 'cpu_freq', 'mem_banks', 'mem_slots', 'mem_bytes', 'listener_port', 'version', 'action_type', 'host_mode', 'team_responsible', 'team_integ', 'team_support', 'project', 'last_boot', 'power_supply_nb', 'power_cabinet1', 'power_cabinet2', 'power_protect', 'power_protect_breaker', 'power_breaker1', 'power_breaker2', 'warranty_end', 'maintenance_end', 'os_obs_warn_date', 'os_obs_alert_date', 'hw_obs_warn_date', 'hw_obs_alert_date', 'updated', 'save_server', 'save_app', 'save_nodename', 'save_svcname'],
     'force_cols': ['id', 'os_name'],
     'columns': ['id', 'save_server', 'save_id', 'save_app', 'save_nodename', 'save_svcname', 'save_name', 'save_group', 'save_level', 'save_size', 'save_volume', 'save_date', 'save_retention', 'assetname', 'fqdn', 'serial', 'model', 'environnement', 'role', 'status', 'type', 'sec_zone', 'loc_country', 'loc_zip', 'loc_city', 'loc_addr', 'loc_building', 'loc_floor', 'loc_room', 'loc_rack', 'enclosure', 'enclosureslot', 'hvvdc', 'hvpool', 'hv', 'os_name', 'os_release', 'os_vendor', 'os_arch', 'os_kernel', 'os_concat', 'cpu_dies', 'cpu_cores', 'cpu_threads', 'cpu_model', 'cpu_freq', 'mem_banks', 'mem_slots', 'mem_bytes', 'listener_port', 'version', 'action_type', 'host_mode', 'team_responsible', 'team_integ', 'team_support', 'project', 'last_boot', 'power_supply_nb', 'power_cabinet1', 'power_cabinet2', 'power_protect', 'power_protect_breaker', 'power_breaker1', 'power_breaker2', 'warranty_end', 'maintenance_end', 'os_obs_warn_date', 'os_obs_alert_date', 'hw_obs_warn_date', 'hw_obs_alert_date', 'updated'],
     'colprops': {'enclosure': {'field': 'enclosure', 'filter_redirect': '', 'force_filter': '', 'img': 'loc', '_dataclass': '', 'title': 'Enclosure', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'maintenance_end': {'field': 'maintenance_end', 'filter_redirect': '', 'force_filter': '', 'img': 'time16', '_dataclass': '', 'title': 'Maintenance end', '_class': 'date_future', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'loc_city': {'field': 'loc_city', 'filter_redirect': '', 'force_filter': '', 'img': 'loc', '_dataclass': '', 'title': 'City', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'mem_slots': {'field': 'mem_slots', 'filter_redirect': '', 'force_filter': '', 'img': 'mem16', '_dataclass': '', 'title': 'Memory slots', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'mem_banks': {'field': 'mem_banks', 'filter_redirect': '', 'force_filter': '', 'img': 'mem16', '_dataclass': '', 'title': 'Memory banks', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'sec_zone': {'field': 'sec_zone', 'filter_redirect': '', 'force_filter': '', 'img': 'fw16', '_dataclass': '', 'title': 'Security zone', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'mem_bytes': {'field': 'mem_bytes', 'filter_redirect': '', 'force_filter': '', 'img': 'mem16', '_dataclass': '', 'title': 'Memory', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'power_protect_breaker': {'field': 'power_protect_breaker', 'filter_redirect': '', 'force_filter': '', 'img': 'pwr', '_dataclass': '', 'title': 'Power protector breaker', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'cpu_dies': {'field': 'cpu_dies', 'filter_redirect': '', 'force_filter': '', 'img': 'cpu16', '_dataclass': '', 'title': 'CPU dies', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'power_cabinet1': {'field': 'power_cabinet1', 'filter_redirect': '', 'force_filter': '', 'img': 'pwr', '_dataclass': '', 'title': 'Power cabinet #1', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'power_cabinet2': {'field': 'power_cabinet2', 'filter_redirect': '', 'force_filter': '', 'img': 'pwr', '_dataclass': '', 'title': 'Power cabinet #2', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'os_name': {'field': 'os_name', 'filter_redirect': '', 'force_filter': '', 'img': 'os16', '_dataclass': '', 'title': 'OS name', '_class': 'os_name', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'os_arch': {'field': 'os_arch', 'filter_redirect': '', 'force_filter': '', 'img': 'os16', '_dataclass': '', 'title': 'OS arch', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'team_support': {'field': 'team_support', 'filter_redirect': '', 'force_filter': '', 'img': 'guys16', '_dataclass': '', 'title': 'Support', '_class': 'groups', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'assetname': {'field': 'assetname', 'filter_redirect': '', 'force_filter': '', 'img': 'node16', '_dataclass': '', 'title': 'Asset name', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'host_mode': {'field': 'host_mode', 'filter_redirect': '', 'force_filter': '', 'img': 'svc', '_dataclass': '', 'title': 'Host Mode', '_class': 'env', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'loc_country': {'field': 'loc_country', 'filter_redirect': '', 'force_filter': '', 'img': 'loc', '_dataclass': '', 'title': 'Country', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'cpu_vendor': {'field': 'cpu_vendor', 'filter_redirect': '', 'force_filter': '', 'img': 'cpu16', '_dataclass': '', 'title': 'CPU vendor', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'os_vendor': {'field': 'os_vendor', 'filter_redirect': '', 'force_filter': '', 'img': 'os16', '_dataclass': '', 'title': 'OS vendor', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'nodename': {'field': 'nodename', 'filter_redirect': '', 'force_filter': '', 'img': 'node16', '_dataclass': '', 'title': 'Node name', '_class': 'nodename', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'cpu_freq': {'field': 'cpu_freq', 'filter_redirect': '', 'force_filter': '', 'img': 'cpu16', '_dataclass': '', 'title': 'CPU freq', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'loc_building': {'field': 'loc_building', 'filter_redirect': '', 'force_filter': '', 'img': 'loc', '_dataclass': '', 'title': 'Building', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'team_responsible': {'field': 'team_responsible', 'filter_redirect': '', 'force_filter': '', 'img': 'guys16', '_dataclass': '', 'title': 'Team responsible', '_class': 'groups', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'cpu_cores': {'field': 'cpu_cores', 'filter_redirect': '', 'force_filter': '', 'img': 'cpu16', '_dataclass': '', 'title': 'CPU cores', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'save_date': {'field': 'save_date', 'filter_redirect': '', 'force_filter': '', 'img': 'time16', '_dataclass': '', 'title': 'Date', '_class': 'datetime_no_age', 'table': 'saves', 'display': 1, 'default_filter': '>-1d'}, 'node_updated': {'field': 'node_updated', 'filter_redirect': '', 'force_filter': '', 'img': 'time16', '_dataclass': '', 'title': 'Last node update', '_class': 'datetime_daily', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'version': {'field': 'version', 'filter_redirect': '', 'force_filter': '', 'img': 'svc', '_dataclass': '', 'title': 'Agent version', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'loc_rack': {'field': 'loc_rack', 'filter_redirect': '', 'force_filter': '', 'img': 'loc', '_dataclass': '', 'title': 'Rack', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'save_level': {'field': 'save_level', 'filter_redirect': '', 'force_filter': '', 'img': 'save16', '_dataclass': '', 'title': 'Level', '_class': '', 'table': 'saves', 'display': 1, 'default_filter': ''}, 'team_integ': {'field': 'team_integ', 'filter_redirect': '', 'force_filter': '', 'img': 'guys16', '_dataclass': '', 'title': 'Integrator', '_class': 'groups', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'power_supply_nb': {'field': 'power_supply_nb', 'filter_redirect': '', 'force_filter': '', 'img': 'pwr', '_dataclass': '', 'title': 'Power supply number', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'id': {'field': 'id', 'filter_redirect': '', 'force_filter': '', 'img': 'key', '_dataclass': '', 'title': 'Id', '_class': '', 'table': 'saves', 'display': 0, 'default_filter': ''}, 'type': {'field': 'type', 'filter_redirect': '', 'force_filter': '', 'img': 'node16', '_dataclass': '', 'title': 'Type', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'enclosureslot': {'field': 'enclosureslot', 'filter_redirect': '', 'force_filter': '', 'img': 'loc', '_dataclass': '', 'title': 'Enclosure Slot', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'save_name': {'field': 'save_name', 'filter_redirect': '', 'force_filter': '', 'img': 'save16', '_dataclass': '', 'title': 'Name', '_class': '', 'table': 'saves', 'display': 1, 'default_filter': ''}, 'save_svcname': {'field': 'save_svcname', 'filter_redirect': '', 'force_filter': '', 'img': 'save16', '_dataclass': '', 'title': 'Service', '_class': 'svcname', 'table': 'saves', 'display': 1, 'default_filter': ''}, 'status': {'field': 'status', 'filter_redirect': '', 'force_filter': '', 'img': 'node16', '_dataclass': '', 'title': 'Status', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'loc_zip': {'field': 'loc_zip', 'filter_redirect': '', 'force_filter': '', 'img': 'loc', '_dataclass': '', 'title': 'ZIP', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'updated': {'field': 'updated', 'filter_redirect': '', 'force_filter': '', 'img': 'time16', '_dataclass': '', 'title': 'Last node update', '_class': 'datetime_daily', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'os_kernel': {'field': 'os_kernel', 'filter_redirect': '', 'force_filter': '', 'img': 'os16', '_dataclass': '', 'title': 'OS kernel', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'save_size': {'field': 'save_size', 'filter_redirect': '', 'force_filter': '', 'img': 'save16', '_dataclass': '', 'title': 'Size', '_class': 'size_b', 'table': 'saves', 'display': 1, 'default_filter': ''}, 'action_type': {'field': 'action_type', 'filter_redirect': '', 'force_filter': '', 'img': 'svc', '_dataclass': '', 'title': 'Action type', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'power_protect': {'field': 'power_protect', 'filter_redirect': '', 'force_filter': '', 'img': 'pwr', '_dataclass': '', 'title': 'Power protector', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'os_obs_alert_date': {'field': 'os_obs_alert_date', 'filter_redirect': '', 'force_filter': '', 'img': 'time16', '_dataclass': '', 'title': 'OS obsolescence alert date', '_class': 'date_future', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'hv': {'field': 'hv', 'filter_redirect': '', 'force_filter': '', 'img': 'hv16', '_dataclass': '', 'title': 'Hypervisor', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'cpu_model': {'field': 'cpu_model', 'filter_redirect': '', 'force_filter': '', 'img': 'cpu16', '_dataclass': '', 'title': 'CPU model', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'save_app': {'field': 'save_app', 'filter_redirect': '', 'force_filter': '', 'img': 'save16', '_dataclass': '', 'title': 'App', '_class': '', 'table': 'saves', 'display': 1, 'default_filter': ''}, 'save_server': {'field': 'save_server', 'filter_redirect': '', 'force_filter': '', 'img': 'save16', '_dataclass': '', 'title': 'Server', '_class': 'nodename_no_os', 'table': 'saves', 'display': 1, 'default_filter': ''}, 'hvvdc': {'field': 'hvvdc', 'filter_redirect': '', 'force_filter': '', 'img': 'hv16', '_dataclass': '', 'title': 'Virtual datacenter', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'warranty_end': {'field': 'warranty_end', 'filter_redirect': '', 'force_filter': '', 'img': 'time16', '_dataclass': '', 'title': 'Warranty end', '_class': 'date_future', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'save_id': {'field': 'save_id', 'filter_redirect': '', 'force_filter': '', 'img': 'save16', '_dataclass': '', 'title': 'Id', '_class': '', 'table': 'saves', 'display': 0, 'default_filter': ''}, 'last_boot': {'field': 'last_boot', 'filter_redirect': '', 'force_filter': '', 'img': 'time16', '_dataclass': '', 'title': 'Last boot', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'cpu_threads': {'field': 'cpu_threads', 'filter_redirect': '', 'force_filter': '', 'img': 'cpu16', '_dataclass': '', 'title': 'CPU threads', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'role': {'field': 'role', 'filter_redirect': '', 'force_filter': '', 'img': 'node16', '_dataclass': '', 'title': 'Role', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'os_concat': {'field': 'os_concat', 'filter_redirect': '', 'force_filter': '', 'img': 'os16', '_dataclass': '', 'title': 'OS full name', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'model': {'field': 'model', 'filter_redirect': '', 'force_filter': '', 'img': 'node16', '_dataclass': '', 'title': 'Model', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'serial': {'field': 'serial', 'filter_redirect': '', 'force_filter': '', 'img': 'node16', '_dataclass': '', 'title': 'Serial', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'listener_port': {'field': 'listener_port', 'filter_redirect': '', 'force_filter': '', 'img': 'svc', '_dataclass': '', 'title': 'Listener port', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'environnement': {'field': 'environnement', 'filter_redirect': '', 'force_filter': '', 'img': 'node16', '_dataclass': '', 'title': 'Env', '_class': 'env', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'hw_obs_alert_date': {'field': 'hw_obs_alert_date', 'filter_redirect': '', 'force_filter': '', 'img': 'time16', '_dataclass': '', 'title': 'Hardware obsolescence alert date', '_class': 'date_future', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'loc_addr': {'field': 'loc_addr', 'filter_redirect': '', 'force_filter': '', 'img': 'loc', '_dataclass': '', 'title': 'Address', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'os_obs_warn_date': {'field': 'os_obs_warn_date', 'filter_redirect': '', 'force_filter': '', 'img': 'time16', '_dataclass': '', 'title': 'OS obsolescence warning date', '_class': 'date_future', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'hw_obs_warn_date': {'field': 'hw_obs_warn_date', 'filter_redirect': '', 'force_filter': '', 'img': 'time16', '_dataclass': '', 'title': 'Hardware obsolescence warning date', '_class': 'date_future', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'loc_room': {'field': 'loc_room', 'filter_redirect': '', 'force_filter': '', 'img': 'loc', '_dataclass': '', 'title': 'Room', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'fqdn': {'field': 'fqdn', 'filter_redirect': '', 'force_filter': '', 'img': 'node16', '_dataclass': '', 'title': 'Fqdn', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'hvpool': {'field': 'hvpool', 'filter_redirect': '', 'force_filter': '', 'img': 'hv16', '_dataclass': '', 'title': 'Hypervisor pool', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'project': {'field': 'project', 'filter_redirect': '', 'force_filter': '', 'img': 'svc', '_dataclass': '', 'title': 'Project', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'save_volume': {'field': 'save_volume', 'filter_redirect': '', 'force_filter': '', 'img': 'save16', '_dataclass': '', 'title': 'Volume', '_class': '', 'table': 'saves', 'display': 1, 'default_filter': ''}, 'loc_floor': {'field': 'loc_floor', 'filter_redirect': '', 'force_filter': '', 'img': 'loc', '_dataclass': '', 'title': 'Floor', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'save_nodename': {'field': 'save_nodename', 'filter_redirect': '', 'force_filter': '', 'img': 'node16', '_dataclass': '', 'title': 'Nodename', '_class': 'nodename', 'table': 'saves', 'display': 1, 'default_filter': ''}, 'os_release': {'field': 'os_release', 'filter_redirect': '', 'force_filter': '', 'img': 'os16', '_dataclass': '', 'title': 'OS release', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'save_group': {'field': 'save_group', 'filter_redirect': '', 'force_filter': '', 'img': 'save16', '_dataclass': '', 'title': 'Group', '_class': '', 'table': 'saves', 'display': 1, 'default_filter': ''}, 'save_retention': {'field': 'save_retention', 'filter_redirect': '', 'force_filter': '', 'img': 'time16', '_dataclass': '', 'title': 'Retention', '_class': 'datetime_no_age', 'table': 'saves', 'display': 1, 'default_filter': ''}, 'power_breaker1': {'field': 'power_breaker1', 'filter_redirect': '', 'force_filter': '', 'img': 'pwr', '_dataclass': '', 'title': 'Power breaker #1', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}, 'power_breaker2': {'field': 'power_breaker2', 'filter_redirect': '', 'force_filter': '', 'img': 'pwr', '_dataclass': '', 'title': 'Power breaker #2', '_class': '', 'table': 'nodes', 'display': 0, 'default_filter': ''}},
     'volatile_filters': false,
     'child_tables': ['charts'],
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
     'events': ['saves_change'],
     'request_vars': {}
}

function table_saves(divid, options) {
  var _options = {"id": "saves"}
  $.extend(true, _options, table_saves_defaults, options)
  _options.divid = divid
  _options.caller = "view_saves"
  table_init(_options)
}

table_saves_charts_defaults = {
     'pager': {'page': 1},
     'extrarow': false,
     'extrarow_class': "",
     'flash': "",
     'checkboxes': false,
     'ajax_url': '/init/saves/ajax_saves_charts',
     'span': ['chart'],
     'force_cols': [],
     'columns': ['chart'],
     'colprops': {'chart': {'field': 'chart', 'filter_redirect': '', 'force_filter': '', 'img': 'spark16', '_dataclass': '', 'title': 'Chart', '_class': 'saves_charts', 'table': '', 'display': 1, 'default_filter': ''}},
     'volatile_filters': false,
     'child_tables': [],
     'parent_tables': ['saves'],
     'dataable': false,
     'linkable': false,
     'dbfilterable': false,
     'filterable': false,
     'refreshable': false,
     'bookmarkable': false,
     'exportable': false,
     'columnable': false,
     'commonalityable': false,
     'headers': false,
     'wsable': false,
     'pageable': false,
     'events': [],
     'request_vars': {}
}

function table_saves_charts(divid, options) {
  var _options = {"id": "charts"}
  $.extend(true, _options, table_saves_charts_defaults, options)
  _options.divid = divid
  _options.caller = "view_saves"
  table_init(_options)
}

function view_saves(divid, options) {
	o = {}
	o.divid = divid
	o.div = $("#"+divid)

	o.div.load("/init/static/views/saves.html", function() {
		o.div.i18n()
		table_saves("saves_div", options)
		table_saves_charts("stats_div", options)
		$("#stats_a").bind("click", function() {
			if (!$("#stats_div").is(":visible")) {
				$(this).addClass("down16")
				$(this).removeClass("right16")
				$("#stats_div").show()
				table_saves_charts("stats_div", options)
			} else {
				$(this).addClass("right16")
				$(this).removeClass("down16")
				$("#stats_div").hide()
			}
		})

	})
}

