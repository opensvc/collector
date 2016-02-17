function table_networks(divid, options) {
	var defaults = {
		'divid': divid,
		'caller': "table_networks",
		'id': "networks",
		'name': "networks",
		'ajax_url': '/init/networks/ajax_networks',
		'span': ['id'],
		'force_cols': ['id'],
		'columns': ['id', 'name', 'pvid', 'network', 'broadcast', 'netmask', 'gateway', 'begin', 'end', 'prio', 'team_responsible', 'comment', 'updated'],
		'default_columns': ['name', 'pvid', 'network', 'broadcast', 'netmask', 'gateway', 'begin', 'end', 'prio', 'team_responsible', 'comment', 'updated'],
		'wsable': true,
		'events': ['networks_change']
	}
	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}

