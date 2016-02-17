function table_saves(divid, options) {
	var defaults = {
		'id': "saves",
		'divid': divid,
		'caller': "view_saves",
		'name': "saves",
		'ajax_url': '/init/saves/ajax_saves',
		'span': ['save_nodename', 'save_svcname'],
		'force_cols': ['id', 'os_name'],
		'columns': [].concat(['id', 'save_server', 'save_id', 'save_app', 'save_nodename', 'save_svcname', 'save_name', 'save_group', 'save_level', 'save_size', 'save_volume', 'save_date', 'save_retention'], objcols.node),
		'default_columns': ['save_server', 'save_app', 'save_nodename', 'save_svcname', 'save_name', 'save_group', 'save_level', 'save_size', 'save_volume', 'save_date', 'save_retention'],
		'child_tables': ['charts'],
		'wsable': true,
		'events': ['saves_change']
	}

	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}

function table_saves_charts(divid, options) {
	var defaults = {
		'id': "charts",
		'divid': divid,
		'caller': "view_saves",
		'name': "saves_charts",
		'checkboxes': false,
		'ajax_url': '/init/saves/ajax_saves_charts',
		'span': ['chart'],
		'force_cols': [],
		'columns': ['chart'],
		'default_columns': ['chart'],
		'colprops': {
			'chart': {
				'img': 'spark16',
				'_dataclass': '',
				'title': 'Chart',
				'_class': 'saves_charts',
			}
		},
		'parent_tables': ['saves'],
		'linkable': false,
		'filterable': false,
		'refreshable': false,
		'bookmarkable': false,
		'exportable': false,
		'columnable': false,
		'commonalityable': false,
		'headers': false,
		'pageable': false
	}

	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}

function view_saves(divid, options) {
	o = {}
	o.divid = divid
	o.div = $("#"+divid)

	o.div.load("/init/static/views/saves.html", function() {
		o.div.i18n()
		table_saves("saves_div", options)
		table_saves_charts("stats_div", options)
		$("#stats_a").bind("click", function() {
			if (!$("#stats_div").is(":visible")) {
				$(this).addClass("down16")
				$(this).removeClass("right16")
				$("#stats_div").show()
				table_saves_charts("stats_div", options)
			} else {
				$(this).addClass("right16")
				$(this).removeClass("down16")
				$("#stats_div").hide()
			}
		})

	})
}

