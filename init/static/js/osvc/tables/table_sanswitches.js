table_sanswitches_defaults = {
     'pager': {'page': 1},
     'extrarow': false,
     'extrarow_class': "",
     'flash': "",
     'checkboxes': false,
     'ajax_url': '/init/sanswitches/ajax_sanswitches',
     'span': ['sw_name', 'sw_index'],
     'columns': ['sw_fabric', 'sw_name', 'sw_index', 'sw_slot', 'sw_port', 'sw_portspeed', 'sw_portnego', 'sw_porttype', 'sw_portstate', 'sw_portname', 'sw_rportname', 'sw_rname', 'sw_updated'],
     'colprops': {'sw_updated': {'field': 'sw_updated', 'filter_redirect': '', 'force_filter': '', 'img': 'time16', '_dataclass': '', 'title': 'Updated', '_class': 'datetime_no_age', 'table': 'v_switches', 'display': 1, 'default_filter': ''}, 'sw_portname': {'field': 'sw_portname', 'filter_redirect': '', 'force_filter': '', 'img': 'net16', '_dataclass': '', 'title': 'Port Name', '_class': '', 'table': 'v_switches', 'display': 1, 'default_filter': ''}, 'sw_portstate': {'field': 'sw_portstate', 'filter_redirect': '', 'force_filter': '', 'img': 'net16', '_dataclass': '', 'title': 'Port State', '_class': '', 'table': 'v_switches', 'display': 1, 'default_filter': ''}, 'sw_rname': {'field': 'sw_rname', 'filter_redirect': '', 'force_filter': '', 'img': 'net16', '_dataclass': '', 'title': 'Remote Name', '_class': '', 'table': 'v_switches', 'display': 1, 'default_filter': ''}, 'sw_portspeed': {'field': 'sw_portspeed', 'filter_redirect': '', 'force_filter': '', 'img': 'net16', '_dataclass': '', 'title': 'Port Speed', '_class': '', 'table': 'v_switches', 'display': 1, 'default_filter': ''}, 'sw_porttype': {'field': 'sw_porttype', 'filter_redirect': '', 'force_filter': '', 'img': 'net16', '_dataclass': '', 'title': 'Port Type', '_class': '', 'table': 'v_switches', 'display': 1, 'default_filter': ''}, 'sw_port': {'field': 'sw_port', 'filter_redirect': '', 'force_filter': '', 'img': 'net16', '_dataclass': '', 'title': 'Port', '_class': '', 'table': 'v_switches', 'display': 1, 'default_filter': ''}, 'sw_portnego': {'field': 'sw_portnego', 'filter_redirect': '', 'force_filter': '', 'img': 'net16', '_dataclass': '', 'title': 'Port Nego', '_class': 'boolean', 'table': 'v_switches', 'display': 1, 'default_filter': ''}, 'sw_name': {'field': 'sw_name', 'filter_redirect': '', 'force_filter': '', 'img': 'net16', '_dataclass': '', 'title': 'Switch Name', '_class': '', 'table': 'v_switches', 'display': 1, 'default_filter': ''}, 'sw_slot': {'field': 'sw_slot', 'filter_redirect': '', 'force_filter': '', 'img': 'net16', '_dataclass': '', 'title': 'Slot', '_class': '', 'table': 'v_switches', 'display': 1, 'default_filter': ''}, 'sw_fabric': {'field': 'sw_fabric', 'filter_redirect': '', 'force_filter': '', 'img': 'net16', '_dataclass': '', 'title': 'Switch Fabric', '_class': '', 'table': 'v_switches', 'display': 0, 'default_filter': ''}, 'sw_rportname': {'field': 'sw_rportname', 'filter_redirect': '', 'force_filter': '', 'img': 'net16', '_dataclass': '', 'title': 'Remote Port Name', '_class': '', 'table': 'v_switches', 'display': 1, 'default_filter': ''}, 'sw_index': {'field': 'sw_index', 'filter_redirect': '', 'force_filter': '', 'img': 'net16', '_dataclass': '', 'title': 'Port Index', '_class': '', 'table': 'v_switches', 'display': 1, 'default_filter': ''}},
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
     'wsable': false,
     'pageable': true,
     'on_change': false,
     'events': [],
     'request_vars': {}
}

function table_sanswitches(divid, options) {
  var _options = {"id": "sanswitches"}
  $.extend(true, _options, table_sanswitches_defaults, options)
  _options.divid = divid
  _options.caller = "table_sanswitches"
  table_init(_options)
}

