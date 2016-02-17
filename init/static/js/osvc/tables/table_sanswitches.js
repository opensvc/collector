function table_sanswitches(divid, options) {
	var defaults = {
		'id': "sanswitches",
		'divid': divid,
		'caller': "table_sanswitches",
		'name': "sanswitches",
		'checkboxes': false,
		'ajax_url': '/init/sanswitches/ajax_sanswitches',
		'span': ['sw_name', 'sw_index'],
		'columns': ['sw_fabric', 'sw_name', 'sw_index', 'sw_slot', 'sw_port', 'sw_portspeed', 'sw_portnego', 'sw_porttype', 'sw_portstate', 'sw_portname', 'sw_rportname', 'sw_rname', 'sw_updated'],
		'default_columns': ['sw_fabric', 'sw_name', 'sw_index', 'sw_slot', 'sw_port', 'sw_portspeed', 'sw_portnego', 'sw_porttype', 'sw_portstate', 'sw_portname', 'sw_rportname', 'sw_rname', 'sw_updated']
	}

	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}

