function table_nodenetworks(divid, options) {
	var defaults = {
		'divid': divid,
		'caller': "table_nodenetworks",
		'id': "nodenetworks",
		'name': "nodenetworks",
		'ajax_url': '/init/nodenetworks/ajax_nodenetworks',
		'span': ['nodename'],
		'force_cols': ['id', 'os_name'],
		'columns': [].concat(
			['id', 'nodename'],
			objcols.node,
			['updated', 'mac', 'intf', 'addr_type', 'addr', 'mask', 'flag_deprecated', 'addr_updated', 'net_name', 'net_network', 'net_broadcast', 'net_comment', 'net_gateway', 'net_begin', 'net_end', 'prio', 'net_pvid', 'net_netmask', 'net_team_responsible']
		),
		'default_columns': ["addr_type", "addr", "addr_updated", "intf", "mac", "mask", "net_begin", "net_end", "net_broadcast", "net_comment", "net_gateway", "net_name", "net_netmask", "net_network", "net_pvid", "net_team_responsible", "nodename"],
		'wsable': true,
		'events': ['node_ip_change', 'nodes_change', 'networks_change']
	}
	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}

function table_nodenetworks_addr(divid, addr) {
	var id = "nodenetworks_" + addr.replace(/[\.-]/g, "_")
	var f = id+"_f_addr"
	var request_vars = {}
	request_vars[f] = addr
	table_nodenetworks(divid, {
		"id": id,
		"caller": "table_table_nodenetworks_addr",
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
		"visible_columns": [
			'nodename',
			'fqdn',
			'loc_city',
			'team_responsible',
			'project',
			'host_mode',
			'environnement',
			'status',
			'mac',
			'intf',
			'addr',
			'mask',
			'flag_deprecated',
			'addr_updated',
			'net_name',
			'net_network',
			'net_gateway',
			'net_pvid',
			'net_netmask'
		]
	})
}

