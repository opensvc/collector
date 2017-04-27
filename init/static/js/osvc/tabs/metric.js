//
// prov template
//
function metric_tabs(divid, options) {
	var o = tabs(divid)
	o.options = options
	o.options.bgcolor = osvc.colors.stats
	o.options.icon = osvc.icons.metric
	o.link = {
		"fn": arguments.callee.name,
		"title": "format_title",
		"title_args": {
			"type": "metric",
			"id": o.options.metric_id
		}
	}

	o.load(function() {
		if (o.options.metric_name && o.options.metric_id) {
			o._load()
		} else if (o.options.report_id) {
			services_osvcgetrest("/reports/metrics/%1", [o.options.report_id], "", function(jd) {
				o.options.metric_data = jd.data[0]
				o.options.metric_name = o.options.metric_data.metric_name
				o._load(jd.data[0])
			})
		} else if (o.options.report_name) {
			services_osvcgetrest("/reports/metrics", "", {"filters": ["metric_name "+o.options.metric_name]}, function(jd) {
				o.options.metric_data = jd.data[0]
				o.options.metric_id = o.options.metric_data.id
				o._load(jd.data[0])
			})
		}
	})

	o._load = function() {
		var title = o.options.metric_name
		o.closetab.text(title)
		o.link.title_args.name = o.options.metric_name

		// tab properties
		i = o.register_tab({
			"title": "metric_tabs.properties",
			"title_class": "icon metric16"
		})
		o.tabs[i].callback = function(divid) {
			metric_properties(divid, o.options)
		}

		// tab request
		i = o.register_tab({
			"title": "metric_tabs.request",
			"title_class": "icon edit16"
		})
		o.tabs[i].callback = function(divid) {
			metric_request(divid, o.options)
		}

		o.set_tab(o.options.tab)

		// tab revision
		i = o.register_tab({
			"title": "form_tabs.revisions",
			"title_class": "icon time16"
		})
		o.tabs[i].callback = function(divid) {
			generic_revisions(divid, {
				"id": o.options.metric_id,
				"base_url": "/reports/metrics"
			})
		}

	}
	return o
}

function metric_properties(divid, options) {
	var o = {}

	// store parameters
	o.divid = divid
	o.div = $("#"+divid)
	o.options = options
	o.link = {
		"fn": arguments.callee.name,
		"parameters": o.options,
		"title": "format_title",
		"title_args": {
			"type": "metric",
			"id": o.options.metric_id
		}
	}

	o.init = function() {
		o.info_id = o.div.find("#id")
		o.info_metric_name = o.div.find("#metric_name")
		o.info_metric_author = o.div.find("#metric_author")
		o.info_metric_created = o.div.find("#metric_created")
		o.info_metric_col_instance_label = o.div.find("#metric_col_instance_label")
		o.info_metric_col_value_index = o.div.find("#metric_col_value_index")
		o.info_metric_col_instance_index = o.div.find("#metric_col_instance_index")
		o.info_metric_historize = o.div.find("#metric_historize")
		o.load()
	}

	o.load = function() {
		services_osvcgetrest("/reports/metrics/%1", [o.options.metric_id], "", function(jd) {
			o._load(jd.data[0])
		})
	}

	o._load = function(data) {
		o.link.title_args.name = data.metric_name
		osvc_tools(o.div, {
			"link": o.link
		})
		o.info_id.html(data.id)
		o.info_metric_name.html(data.metric_name)
		o.info_metric_author.html(data.metric_author)
		o.info_metric_created.html(osvc_date_from_collector(data.metric_created))
		o.info_metric_col_instance_label.html(data.metric_col_instance_label)
		o.info_metric_col_value_index.html(data.metric_col_value_index)
		o.info_metric_col_instance_index.html(data.metric_col_instance_index)
		o.info_metric_historize.html(data.metric_historize)
		o.info_publications = o.div.find("#publications")
		o.info_publications_title = o.div.find("#publications_title")

		var am_data = [
			{
				"title": "action_menu.data_actions",
				"children": [
					{
						"selector": ["tab"],
						"foldable": false,
						"cols": [],
						"children": [
							{
								"title": "action_menu.del",
								"class": "del16",
								"fn": "data_action_del_metrics",
								"privileges": ["Manager", "ReportsManager"]
							}
						]
					}
				]
			}
		]
		tab_tools({
			"div": o.div.find("#tools"),
			"data": {"id": data.id},
			"am_data": am_data
		})

		tab_properties_generic_updater({
			"div": o.div,
			//"privileges": ["ReportsManager", "Manager"],
			"post": function(data, callback, error_callback) {
				services_osvcpostrest("/reports/metrics/%1", [o.options.metric_id], "", data, callback, error_callback)
			}
		})
		metric_publications({
			"tid": o.info_publications,
			"metric_id": data.id
		})
	}

	o.div.load("/init/static/views/metric_properties.html?v="+osvc.code_rev, function() {
		o.div.i18n()
		o.init()
	})

	return o
}


function metric_request(divid, options) {
	var o = {}

	// store parameters
	o.divid = divid
	o.div = $("#"+divid)
	o.options = options
	o.link = {
		"fn": arguments.callee.name,
		"parameters": o.options,
		"title": "format_title",
		"title_args": {
			"type": "metric",
			"id": o.options.metric_id
		}
	}

	o.init = function() {
		o.div.empty()
		services_osvcgetrest("/reports/metrics/%1", [o.options.metric_id], {"props": "metric_sql"}, function(jd) {
			o.load(jd.data[0])
			o.test(jd.data[0])
		})
	}

	o.load = function(data) {
		osvc_tools(o.div, {
			"resize": o.resize,
			"link": o.link
		})
		o.editor_div = $("<div style='padding:1em'></div>")
		o.div.append(o.editor_div)
		if (data.metric_sql && (data.metric_sql.length > 0)) {
			var text = data.metric_sql
		} else {
			var text = ""
		}
		o.editor = osvc_editor(o.editor_div, {
			"text": text,
			"privileges": ["Manager", "ReportsManager"],
			"save": o.save,
			"callback": o.resize
		})
	}

	o.resize = function() {
		var div = o.editor_div.children().first()
		var button = o.editor_div.find("button")
		var max_height = max_child_height(o.div)
			 - o.div.css("padding-top").replace(/px/,"")
			 - o.div.css("padding-bottom").replace(/px/,"")
		o.div.outerHeight(max_height)
		if (button.length > 0) {
			max_height = max_height
				 - button.height()
				 - button.css("margin-top").replace(/px/,"")
				 - button.css("margin-bottom").replace(/px/,"")
		}

		// leave half the space for the request result
		max_height /= 2
		div.outerHeight(max_height)

		o.editor.editor.resize()
	}

	o.save = function(text) {
		var data = {
			"metric_sql": text
		}
		services_osvcpostrest("/reports/metrics/%1", [o.options.metric_id], "", data, function(jd) {
			if (jd.error && (jd.error.length > 0)) {
				osvc.flash.error(services_error_fmt(jd))
				return
			}
			o.init()
		},
		function(xhr, stat, error) {
			osvc.flash.error(services_ajax_error_fmt(xhr, stat, error))
		})
	}

	o.test = function(data) {
		var div = $("<div style='padding:1em'></div>")
		div.uniqueId()
		o.div.append(div)
		if (!data.metric_sql || (data.metric_sql.length == 0)) {
			return
		}
		var options = {"metric_id" : o.options.metric_id}
		metric(div.attr("id"), options)
	}

	o.init()

	return o
}

