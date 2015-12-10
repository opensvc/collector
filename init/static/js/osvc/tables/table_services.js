table_services_defaults = {
     'id': 'services',
     'pager': {'page': 1},
     'extrarow': false,
     'extrarow_class': "",
     'flash': "",
     'checkboxes': true,
     'ajax_url': '/init/services/ajax_services',
     'span': ['svc_name'],
     'columns': ['svc_name', 'svc_status', 'svc_availstatus', 'svc_app', 'svc_type', 'svc_ha', 'svc_cluster_type', 'svc_flex_min_nodes', 'svc_flex_max_nodes', 'svc_flex_cpu_low_threshold', 'svc_flex_cpu_high_threshold', 'svc_drptype', 'svc_containertype', 'svc_autostart', 'svc_nodes', 'svc_drpnode', 'svc_drpnodes', 'svc_comment', 'svc_created', 'updated', 'svc_status_updated'],
     'colprops': {'svc_updated': {'field': 'updated', 'filter_redirect': '', 'force_filter': '', 'img': 'time16', '_dataclass': '', 'title': 'Last service update', '_class': 'datetime_daily', 'table': 'services', 'display': 0, 'default_filter': ''}, 'svc_app': {'field': 'svc_app', 'filter_redirect': '', 'force_filter': '', 'img': 'svc', '_dataclass': '', 'title': 'App', '_class': '', 'table': 'services', 'display': 0, 'default_filter': ''}, 'svc_drpnode': {'field': 'svc_drpnode', 'filter_redirect': '', 'force_filter': '', 'img': 'svc', '_dataclass': '', 'title': 'DRP node', '_class': 'nodename_no_os', 'table': 'services', 'display': 0, 'default_filter': ''}, 'svc_flex_cpu_high_threshold': {'field': 'svc_flex_cpu_high_threshold', 'filter_redirect': '', 'force_filter': '', 'img': 'spark16', '_dataclass': '', 'title': 'Flex cpu high threshold', '_class': '', 'table': 'services', 'display': 0, 'default_filter': ''}, 'svc_status': {'field': 'svc_status', 'filter_redirect': '', 'force_filter': '', 'img': 'svc', '_dataclass': '', 'title': 'Service overall status', '_class': 'status', 'table': 'services', 'display': 1, 'default_filter': ''}, 'id': {'field': 'id', 'filter_redirect': '', 'force_filter': '', 'img': 'pkg16', '_dataclass': '', 'title': 'Id', '_class': '', 'table': 'services', 'display': 0, 'default_filter': ''}, 'svc_hostid': {'field': 'svc_hostid', 'filter_redirect': '', 'force_filter': '', 'img': 'svc', '_dataclass': '', 'title': 'Host id', '_class': '', 'table': 'services', 'display': 0, 'default_filter': ''}, 'svc_flex_max_nodes': {'field': 'svc_flex_max_nodes', 'filter_redirect': '', 'force_filter': '', 'img': 'svc', '_dataclass': '', 'title': 'Flex max nodes', '_class': '', 'table': 'services', 'display': 0, 'default_filter': ''}, 'mailto': {'field': 'mailto', 'filter_redirect': '', 'force_filter': '', 'img': 'guy16', '_dataclass': '', 'title': 'Responsibles emails', '_class': '', 'table': 'services', 'display': 0, 'default_filter': ''}, 'svc_flex_cpu_low_threshold': {'field': 'svc_flex_cpu_low_threshold', 'filter_redirect': '', 'force_filter': '', 'img': 'spark16', '_dataclass': '', 'title': 'Flex cpu low threshold', '_class': '', 'table': 'services', 'display': 0, 'default_filter': ''}, 'svc_cluster_type': {'field': 'svc_cluster_type', 'filter_redirect': '', 'force_filter': '', 'img': 'svc', '_dataclass': '', 'title': 'Cluster type', '_class': '', 'table': 'services', 'display': 1, 'default_filter': ''}, 'svc_autostart': {'field': 'svc_autostart', 'filter_redirect': '', 'force_filter': '', 'img': 'svc', '_dataclass': '', 'title': 'Primary node', '_class': 'svc_autostart', 'table': 'services', 'display': 0, 'default_filter': ''}, 'svc_comment': {'field': 'svc_comment', 'filter_redirect': '', 'force_filter': '', 'img': 'svc', '_dataclass': '', 'title': 'Comment', '_class': '', 'table': 'services', 'display': 0, 'default_filter': ''}, 'svc_envdate': {'field': 'svc_envdate', 'filter_redirect': '', 'force_filter': '', 'img': 'time16', '_dataclass': '', 'title': 'Env file date', '_class': '', 'table': 'services', 'display': 0, 'default_filter': ''}, 'svc_wave': {'field': 'svc_wave', 'filter_redirect': '', 'force_filter': '', 'img': 'svc', '_dataclass': '', 'title': 'Drp wave', '_class': '', 'table': 'services', 'display': 0, 'default_filter': ''}, 'responsibles': {'field': 'responsibles', 'filter_redirect': '', 'force_filter': '', 'img': 'guy16', '_dataclass': '', 'title': 'Responsibles', '_class': '', 'table': 'services', 'display': 0, 'default_filter': ''}, 'svc_name': {'field': 'svc_name', 'filter_redirect': '', 'force_filter': '', 'img': 'svc', '_dataclass': '', 'title': 'Service', '_class': 'svcname', 'table': 'services', 'display': 1, 'default_filter': ''}, 'updated': {'field': 'updated', 'filter_redirect': '', 'force_filter': '', 'img': 'time16', '_dataclass': '', 'title': 'Last service update', '_class': 'datetime_daily', 'table': 'services', 'display': 0, 'default_filter': ''}, 'svc_type': {'field': 'svc_type', 'filter_redirect': '', 'force_filter': '', 'img': 'svc', '_dataclass': '', 'title': 'Service type', '_class': 'env', 'table': 'services', 'display': 0, 'default_filter': ''}, 'svc_envfile': {'field': 'svc_envfile', 'filter_redirect': '', 'force_filter': '', 'img': 'svc', '_dataclass': '', 'title': 'Env file', '_class': '', 'table': 'services', 'display': 0, 'default_filter': ''}, 'svc_availstatus': {'field': 'svc_availstatus', 'filter_redirect': '', 'force_filter': '', 'img': 'svc', '_dataclass': '', 'title': 'Service availability status', '_class': 'status', 'table': 'services', 'display': 1, 'default_filter': ''}, 'svc_flex_min_nodes': {'field': 'svc_flex_min_nodes', 'filter_redirect': '', 'force_filter': '', 'img': 'svc', '_dataclass': '', 'title': 'Flex min nodes', '_class': '', 'table': 'services', 'display': 0, 'default_filter': ''}, 'svc_drptype': {'field': 'svc_drptype', 'filter_redirect': '', 'force_filter': '', 'img': 'svc', '_dataclass': '', 'title': 'DRP type', '_class': '', 'table': 'services', 'display': 0, 'default_filter': ''}, 'svc_status_updated': {'field': 'svc_status_updated', 'filter_redirect': '', 'force_filter': '', 'img': 'time16', '_dataclass': '', 'title': 'Status updated', '_class': 'datetime_status', 'table': 'services', 'display': 1, 'default_filter': ''}, 'svc_containertype': {'field': 'svc_containertype', 'filter_redirect': '', 'force_filter': '', 'img': 'svc', '_dataclass': '', 'title': 'Service mode', '_class': '', 'table': 'services', 'display': 0, 'default_filter': ''}, 'svc_ha': {'field': 'svc_ha', 'filter_redirect': '', 'force_filter': '', 'img': 'svc', '_dataclass': '', 'title': 'HA', '_class': 'svc_ha', 'table': 'services', 'display': 1, 'default_filter': ''}, 'svc_drpnodes': {'field': 'svc_drpnodes', 'filter_redirect': '', 'force_filter': '', 'img': 'svc', '_dataclass': '', 'title': 'DRP nodes', '_class': '', 'table': 'services', 'display': 0, 'default_filter': ''}, 'svc_nodes': {'field': 'svc_nodes', 'filter_redirect': '', 'force_filter': '', 'img': 'svc', '_dataclass': '', 'title': 'Nodes', '_class': '', 'table': 'services', 'display': 0, 'default_filter': ''}, 'svc_created': {'field': 'svc_created', 'filter_redirect': '', 'force_filter': '', 'img': 'time16', '_dataclass': '', 'title': 'Service creation date', '_class': '', 'table': 'services', 'display': 0, 'default_filter': ''}},
     'volatile_filters': false,
     'child_tables': [],
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
     'events': ['services_change'],
     'request_vars': {}
}

function table_services(divid, options) {
  var _options = {"id": "services"}
  $.extend(true, _options, table_services_defaults, options)
  _options.divid = divid
  _options.caller = "table_services"
  table_init(_options)
}

