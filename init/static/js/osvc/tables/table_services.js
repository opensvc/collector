function table_services(divid, options) {
	var defaults = {
		'caller': 'table_services',
		'divid': divid,
		'name': 'services',
		'id': 'services',
		'ajax_url': '/init/services/ajax_services',
		'span': ['svc_name'],
		'force_cols': ['svc_name', 'svc_status_updated'],
		'columns': [].concat(['svc_name'], objcols.service),
		'default_columns': ["svc_status", "svc_name", "svc_cluster_type", "svc_availstatus", "svc_status_updated", "svc_ha", "updated"],
		'colprops': {
			"updated": colprops.svc_updated
		},
		'wsable': true,
		'events': ['services_change']
	}

	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}

