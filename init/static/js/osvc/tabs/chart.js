//
// chart
//
function chart_tabs(divid, options) {
	var o = tabs(divid)
	o.options = options
	o.options.bgcolor = osvc.colors.stats
	o.options.icon = osvc.icons.chart
	o.link = {
		"fn": arguments.callee.name,
		"title": "format_title",
		"title_args": {
			"type": "chart",
			"id": o.options.chart_id
		}
	}

	o.load(function() {
		if (o.options.chart_name && o.options.chart_id) {
			o._load()
		} else if (o.options.report_id) {
			services_osvcgetrest("/reports/charts/%1", [o.options.report_id], "", function(jd) {
				o.options.chart_data = jd.data[0]
				o.options.chart_name = o.options.chart_data.chart_name
				o._load(jd.data[0])
			})
		} else if (o.options.report_name) {
			services_osvcgetrest("/reports/charts", "", {"filters": ["chart_name "+o.options.chart_name]}, function(jd) {
				o.options.chart_data = jd.data[0]
				o.options.chart_id = o.options.chart_data.id
				o._load(jd.data[0])
			})
		}
	})

	o._load = function(data) {
		var title = o.options.chart_name
		o.link.title_args.name = o.options.chart_name
		o.closetab.text(title)

		// tab properties
		i = o.register_tab({
			"title": "chart_tabs.properties",
			"title_class": "icon fa-list-ul"
		})
		o.tabs[i].callback = function(divid) {
			chart_properties(divid, o.options)
		}

		// rendering properties
		i = o.register_tab({
			"title": "chart_tabs.rendering",
			"title_class": "icon chart16"
		})
		o.tabs[i].callback = function(divid) {
			chart(divid, o.options)
		}

		// tab definition
		i = o.register_tab({
			"title": "chart_tabs.definition",
			"title_class": "icon edit16"
		})
		o.tabs[i].callback = function(divid) {
			chart_definition(divid, o.options)
		}

		o.set_tab(o.options.tab)

		// tab revision
		i = o.register_tab({
			"title": "form_tabs.revisions",
			"title_class": "icon time16"
		})
		o.tabs[i].callback = function(divid) {
			generic_revisions(divid, {
				"id": o.options.chart_id,
				"base_url": "/reports/charts"
			})
		}

	}
	return o
}

function chart_properties(divid, options) {
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
			"id": o.options.chart_id,
			"type": "chart"
		}
	}

	o.init = function() {
		o.info_id = o.div.find("#id")
		o.info_chart_name = o.div.find("#chart_name")
		o.info_publications = o.div.find("#publications")
		o.info_publications_title = o.div.find("#publications_title")
		o.info_responsibles = o.div.find("#responsibles")
		o.info_responsibles_title = o.div.find("#responsibles_title")
		o.load()
	}

	o.load= function() {
                if (o.options.chart_data) {
                        o._load(o.options.chart_data)
                } else {
			services_osvcgetrest("/reports/charts/%1", [o.options.chart_id], "", function(jd) {
				o._load(jd.data[0])
			})
		}
	}

	o._load= function(data) {
		o.link.title_args.name = data.chart_name
		osvc_tools(o.div, {
			"link": o.link
		})
		o.info_id.html(data.id)
		o.info_chart_name.html(data.chart_name)

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
								"fn": "data_action_del_charts",
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
			"privileges": ["FormsManager", "Manager"],
			"post": function(data, callback, error_callback) {
				services_osvcpostrest("/reports/charts/%1", [o.options.chart_id], "", data, callback, error_callback)
			}
		})
		chart_publications({
			"tid": o.info_publications,
			"chart_id": data.id
		})
		chart_responsibles({
			"tid": o.info_responsibles,
			"chart_id": data.id
		})
	}

	o.div.load("/init/static/views/chart_properties.html?v="+osvc.code_rev, function() {
		o.div.i18n()
		o.init()
	})

	return o
}


function chart_definition(divid, options) {
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
			"id": o.options.chart_id,
			"type": "chart"
		}
	}

	o.init = function() {
		o.div.empty()
		osvc_tools(o.div, {
			"resize": o.resize,
			"link": o.link
		})
		services_osvcgetrest("/reports/charts/%1", [o.options.chart_id], {"props": "chart_yaml"}, function(jd) {
			o.load(jd.data[0])
		})
	}

	o.resize = function() {
		var div = o.editor_div.children().first()
		var button = o.editor_div.find("button")
		var max_height = max_child_height(o.div)
			 - o.editor_div.css("padding-top").replace(/px/,"")
			 - o.editor_div.css("padding-bottom").replace(/px/,"")
		if (button.length > 0) {
			max_height = max_height
				 - button.height()
				 - button.css("margin-top").replace(/px/,"")
				 - button.css("margin-bottom").replace(/px/,"")
		}
		div.outerHeight(max_height)
		o.editor.editor.resize()
	}

	o.load = function(data) {
		o.editor_div = $("<div style='padding:1em'></div>")
		o.div.append(o.editor_div)
		if (data.chart_yaml && (data.chart_yaml.length > 0)) {
			var text = data.chart_yaml
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

	o.save = function(text) {
		var data = {
			"chart_yaml": text
		}
		services_osvcpostrest("/reports/charts/%1", [o.options.chart_id], "", data, function(jd) {
			if (rest_error(jd)) {
				osvc.flash.error(services_error_fmt(jd))
				return
			}
			o.init()

			// force a new render in the rendering tab
			o.div.parents(".tab_display").first().find(".reports_section").parent().empty()

		},
		function(xhr, stat, error) {
			osvc.flash.error(services_ajax_error_fmt(xhr, stat, error))
		})
	}

	o.init()

	return o
}

