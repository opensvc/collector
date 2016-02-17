function table_replication(divid, options) {
	var defaults = {
	     'caller': "table_replication",
	     'divid': divid,
	     'id': "replication",
	     'name': "replication",
	     'ajax_url': '/init/replication/ajax_replication_status',
	     'span': [],
	     'force_cols': [],
	     'columns': ['mode', 'remote', 'table_schema', 'table_name', 'need_resync', 'current_cksum', 'last_cksum', 'table_updated'],
	     'default_columns': ['mode', 'remote', 'table_schema', 'table_name', 'need_resync', 'current_cksum', 'last_cksum', 'table_updated']
	}

	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}

