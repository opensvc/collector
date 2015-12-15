table_networks_defaults = {
     'pager': {'page': 1},
     'extrarow': false,
     'extrarow_class': "",
     'flash': "",
     'checkboxes': true,
     'ajax_url': '/init/networks/ajax_networks',
     'span': ['id'],
     'columns': ['id', 'name', 'pvid', 'network', 'broadcast', 'netmask', 'gateway', 'begin', 'end', 'prio', 'team_responsible', 'comment', 'updated'],
     'colprops': {'comment': {'field': 'comment', 'filter_redirect': '', 'force_filter': '', 'img': 'net16', '_dataclass': '', 'title': 'Comment', '_class': '_network', 'table': 'networks', 'display': 1, 'default_filter': ''}, 'begin': {'field': 'begin', 'filter_redirect': '', 'force_filter': '', 'img': 'net16', '_dataclass': '', 'title': 'Ip range begin', '_class': '_network', 'table': 'networks', 'display': 1, 'default_filter': ''}, 'end': {'field': 'end', 'filter_redirect': '', 'force_filter': '', 'img': 'net16', '_dataclass': '', 'title': 'Ip range end', '_class': '_network', 'table': 'networks', 'display': 1, 'default_filter': ''}, 'network': {'field': 'network', 'filter_redirect': '', 'force_filter': '', 'img': 'net16', '_dataclass': '', 'title': 'Network', '_class': '_network', 'table': 'networks', 'display': 1, 'default_filter': ''}, 'prio': {'field': 'prio', 'filter_redirect': '', 'force_filter': '', 'img': 'net16', '_dataclass': '', 'title': 'Priority', '_class': '_network', 'table': 'networks', 'display': 1, 'default_filter': ''}, 'team_responsible': {'field': 'team_responsible', 'filter_redirect': '', 'force_filter': '', 'img': 'guys16', '_dataclass': '', 'title': 'Team Responsible', '_class': '', 'table': 'networks', 'display': 1, 'default_filter': ''}, 'updated': {'field': 'updated', 'filter_redirect': '', 'force_filter': '', 'img': 'time16', '_dataclass': '', 'title': 'Updated', '_class': 'datetime_daily', 'table': 'networks', 'display': 1, 'default_filter': ''}, 'gateway': {'field': 'gateway', 'filter_redirect': '', 'force_filter': '', 'img': 'net16', '_dataclass': '', 'title': 'Gateway', '_class': '_network', 'table': 'networks', 'display': 1, 'default_filter': ''}, 'broadcast': {'field': 'broadcast', 'filter_redirect': '', 'force_filter': '', 'img': 'net16', '_dataclass': '', 'title': 'Broadcast', '_class': '_network', 'table': 'networks', 'display': 1, 'default_filter': ''}, 'pvid': {'field': 'pvid', 'filter_redirect': '', 'force_filter': '', 'img': 'net16', '_dataclass': '', 'title': 'VLAN id', '_class': '_network', 'table': 'networks', 'display': 1, 'default_filter': ''}, 'netmask': {'field': 'netmask', 'filter_redirect': '', 'force_filter': '', 'img': 'net16', '_dataclass': '', 'title': 'Netmask', '_class': '_network', 'table': 'networks', 'display': 1, 'default_filter': ''}, 'id': {'field': 'id', 'filter_redirect': '', 'force_filter': '', 'img': 'net16', '_dataclass': '', 'title': 'Network Id', '_class': '', 'table': 'networks', 'display': 1, 'default_filter': ''}, 'name': {'field': 'name', 'filter_redirect': '', 'force_filter': '', 'img': 'net16', '_dataclass': '', 'title': 'Name', '_class': '_network', 'table': 'networks', 'display': 1, 'default_filter': ''}},
     'volatile_filters': false,
     'child_tables': [],
     'parent_tables': [],
     'dataable': true,
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
     'events': ['networks_change'],
     'request_vars': {}
}

function table_networks(divid, options) {
  var _options = {"id": "networks"}
  $.extend(true, _options, table_networks_defaults, options)
  _options.divid = divid
  _options.caller = "table_networks"
  table_init(_options)
}

