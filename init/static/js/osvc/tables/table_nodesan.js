function table_nodesan(divid, options) {
	var defaults = {
		'divid': divid,
		'caller': "table_nodesan",
		'id': "nodesan",
		'name': "nodesan",
		'ajax_url': '/init/nodesan/ajax_nodesan',
		'span': ['nodename'],
		'force_cols': ['id', 'os_name'],
		'columns': [].concat(['id', 'nodename'], objcols.node, ['node_updated', 'hba_id', 'tgt_id', 'array_name', 'array_model', 'array_cache', 'array_firmware', 'array_updated', 'array_level']),
		'default_columns': ["array_model", "array_name", "hba_id", "nodename", "tgt_id"],
		'colprops': {
			"array_name": {
				"_dataclass": "bluer",
				"_class": "",
			},
		},
		'wsable': false,
		'events': []
	}
	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}

