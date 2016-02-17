function table_metrics(divid, options) {
	var defaults = {
		'id': "table_metrics",
		'divid': divid,
		'id': "metrics",
		'name': "metrics",
		'ajax_url': '/init/charts/ajax_metrics_admin',
		'span': ['id'],
		'force_cols': ['id'],
		'columns': ['id', 'metric_name', 'metric_sql', 'metric_col_value_index', 'metric_col_instance_index', 'metric_col_instance_label', 'metric_created', 'metric_author'],
		'default_columns': ['metric_name', 'metric_sql', 'metric_col_value_index', 'metric_col_instance_index', 'metric_col_instance_label'],
		'wsable': true,
		'events': ['metrics_change']
	}

	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}

function table_charts(divid, options) {
	var defaults = {
		'id': "table_charts",
		'divid': divid,
		'id': "charts",
		'name': "charts",
		'ajax_url': '/init/charts/ajax_charts_admin',
		'span': ['id'],
		'force_cols': ['id'],
		'columns': ['id', 'chart_name', 'chart_yaml'],
		'default_columns': ['chart_name', 'chart_yaml'],
		'wsable': true,
		'events': ['charts_change']
	}

	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}

function table_reports(divid, options) {
	var defaults = {
		'caller': "table_reports",
		'divid': divid,
		'id': "reports",
		'name': "reports",
		'ajax_url': '/init/charts/ajax_reports_admin',
		'span': ['id'],
		'force_cols': ['id'],
		'columns': ['id', 'report_name', 'report_yaml'],
		'default_columns': ['report_name', 'report_yaml'],
		'wsable': true,
		'events': ['reports_change']
	}

	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}


