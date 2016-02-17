function table_uids(divid, options) {
	var defaults = {
		'divid': divid,
		'caller': "view_nodes",
		'id': "uids",
		'name': "uids",
		'ajax_url': '/init/nodes/ajax_uids',
		'span': ['user_id'],
		'columns': ['user_id', 'user_id_count', 'user_name'],
		'default_columns': ['user_id', 'user_id_count', 'user_name'],
		'parent_tables': ["nodes"]
	}
	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}

function table_gids(divid, options) {
	var defaults = {
		'divid': divid,
		'id': "gids",
		'caller': "view_nodes",
		'name': "gids",
		'ajax_url': '/init/nodes/ajax_gids',
		'span': ['group_id'],
		'columns': ['group_id', 'group_id_count', 'group_name'],
		'default_columns': ['group_id', 'group_id_count', 'group_name'],
		'parent_tables': ["nodes"]
	}
	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}

function table_nodes(divid, options) {
	var defaults = {
		'divid': divid,
		'caller': "view_nodes",
		'id': "nodes",
		'name': "nodes",
		'ajax_url': '/init/nodes/ajax_nodes',
		'span': ['nodename'],
		'force_cols': ['os_name'],
		'columns': [].concat(['id', 'nodename'], objcols.node, ["updated"]),
		'default_columns': [
			"cpu_cores",
			"cpu_dies",
			"cpu_model",
			"host_mode",
			"loc_building",
			"loc_floor",
			"loc_rack",
			"mem_bytes",
			"nodename",
			"serial",
			"status",
			"team_responsible"
		],
		'child_tables': ['obs_agg', 'uids', 'gids'],
		'wsable': true,
		'events': ['nodes_change']
	}
	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}

function view_nodes(divid, options) {
	var o = {}
	$("#"+divid).load("/init/static/views/nodes.html", function() {
		$(this).i18n()
		table_nodes("nodes", options)
		$("#uids_a").bind("click", function() {
			if (!$("#uids").is(":visible")) {
				$(this).addClass("down16")
				$(this).removeClass("right16")
				$("#uids").show()
				table_uids("uids", options)
			} else {
				$(this).addClass("right16")
				$(this).removeClass("down16")
				$("#uids").hide()
			}
		})
		$("#gids_a").bind("click", function() {
			if (!$("#gids").is(":visible")) {
				$(this).addClass("down16")
				$(this).removeClass("right16")
				$("#gids").show()
				table_gids("gids", options)
			} else {
				$(this).addClass("right16")
				$(this).removeClass("down16")
				$("#gids").hide()
			}
		})
	})
}

