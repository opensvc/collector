function report_tabs(divid, options) {
	var o = tabs(divid)
	o.options = options
	o.options.bgcolor = osvc.colors.stats
	o.options.icon = osvc.icons.report
	o.link = {
		"fn": arguments.callee.name,
		"title": "link."+arguments.callee.name,
		"title": "format_title",
		"title_args": {
			"id": o.options.report_id,
			"type": "report"
		}
	}

	o.load(function() {
		if (o.options.report_name && o.options.report_id) {
			o._load()
		} else if (o.options.report_id) {
			services_osvcgetrest("/reports/%1", [o.options.report_id], "", function(jd) {
				o.options.report_data = jd.data[0]
				o.options.report_name = o.options.report_data.report_name
				o._load(jd.data[0])
			})
		} else if (o.options.report_name) {
			services_osvcgetrest("/reports", "", {"filters": ["report_name "+o.options.report_name]}, function(jd) {
				o.options.report_data = jd.data[0]
				o.options.report_id = o.options.report_data.id
				o._load(jd.data[0])
			})
		}
	})

	o._load = function() {
		o.link.title_args.name = o.options.report_name
		o.closetab.text(o.options.report_name)

		// tab properties
		i = o.register_tab({
			"title": "report_tabs.properties",
			"title_class": "icon fa-list-ul"
		})
		o.tabs[i].callback = function(divid) {
			report_properties(divid, o.options)
		}

		// tab display
		i = o.register_tab({
			"title": "report_tabs.rendering",
			"title_class": "icon report16"
		})
		o.tabs[i].callback = function(divid) {
			var options = $.extend({}, o.options, {"pad": true})
			report(divid, options)
		}

		// tab definition
		i = o.register_tab({
			"title": "report_tabs.definition",
			"title_class": "icon edit16"
		})
		o.tabs[i].callback = function(divid) {
			report_definition(divid, o.options)
		}

		// tab revision
		i = o.register_tab({
			"title": "form_tabs.revisions",
			"title_class": "icon time16"
		})
		o.tabs[i].callback = function(divid) {
			generic_revisions(divid, {
				"id": o.options.report_id,
				"base_url": "/reports"
			})
		}

		// tab export
		i = o.register_tab({
			"title": "report_tabs.export",
			"title_class": "icon csv"
		})
		o.tabs[i].callback = function(divid) {
			report_export(divid, o.options)
		}

		o.set_tab(o.options.tab)
	}
	return o
}

function report_properties(divid, options) {
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
			"id": o.options.report_id,
			"type": "report"
		}
	}

	o.init = function() {
		o.info_id = o.div.find("#id")
		o.info_report_name = o.div.find("#report_name")
		o.info_publications = o.div.find("#publications")
		o.info_publications_title = o.div.find("#publications_title")
		o.info_responsibles = o.div.find("#responsibles")
		o.info_responsibles_title = o.div.find("#responsibles_title")
		o.load()
	}

	o.load= function() {
		if (o.options.report_data) {
			o._load(o.options.report_data)
		} else {
			services_osvcgetrest("/reports/%1", [o.options.report_id], "", function(jd) {
				o._load(jd.data[0])
			})
		}
	}

	o._load= function(data) {
		o.link.title_args.name = data.report_name
		osvc_tools(o.div, {
			"link": o.link
		})

		o.info_id.html(data.id)
		o.info_report_name.html(data.report_name)

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
								"fn": "data_action_del_reports",
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
				services_osvcpostrest("/reports/%1", [o.options.report_id], "", data, callback, error_callback)
			}
		})
		report_publications({
			"tid": o.info_publications,
			"report_id": data.id
		})
		report_responsibles({
			"tid": o.info_responsibles,
			"report_id": data.id
		})
	}

	o.div.load("/init/static/views/report_properties.html?v="+osvc.code_rev, function() {
		o.div.i18n()
		o.init()
	})

	return o
}


function report_definition(divid, options) {
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
			"id": o.options.report_id,
			"type": "report"
		}
	}

	o.init = function() {
		o.div.empty()
		services_osvcgetrest("/reports/%1", [o.options.report_id], {"props": "report_yaml"}, function(jd) {
			o.load(jd.data[0])
		})
	}

	o.load = function(data) {
		o.editor_div = $("<div style='padding:1em'></div>")
		o.div.append(o.editor_div)
		if (data.report_yaml && (data.report_yaml.length > 0)) {
			var text = data.report_yaml
		} else {
			var text = ""
		}
		o.editor = osvc_editor(o.editor_div, {
			"text": text,
			"privileges": ["Manager", "ReportsManager"],
			"save": o.save,
			"callback": o.resize
		})
		osvc_tools(o.div, {
			"resize": o.resize,
			"link": o.link
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

	o.save = function(text) {
		var data = {
			"report_yaml": text
		}
		services_osvcpostrest("/reports/%1", [o.options.report_id], "", data, function(jd) {
			if (rest_error(jd)) {
				osvc.flash.error(services_error_fmt(jd))
				return
			}
			o.init()

			// force a new render in the rendering tab
			o.div.parents(".tab_display").first().find(".reports_div").parent().empty()
		},
		function(xhr, stat, error) {
			osvc.flash.error(services_ajax_error_fmt(xhr, stat, error))
		})
	}

	o.init()

	return o
}

function report_export(divid, options) {
	var o = {}

	// store parameters
	o.options = options
	o.div = $("#"+divid)
	o.link = {
		"fn": arguments.callee.name,
		"parameters": o.options,
		"title": "format_title",
		"title_args": {
			"id": o.options.report_id,
			"type": "report"
		}
	}

	o.resize = function() {
		var max_height = max_child_height(o.div)
		o.textarea.outerHeight(max_height)
	}

	o.init = function() {
		o.textarea = $("<textarea class='export_data'>")
		o.textarea.prop("disabled", true)
		o.div.css({"padding": "4px"})

		spinner_add(o.div)
		services_osvcgetrest("/reports/%1/export", [o.options.report_id], "", function(jd) {
			if (rest_error(jd)) {
				o.div.html(services_error_fmt(jd))
			}
			o.textarea.text(JSON.stringify(jd, null, 4))
			o.div.html(o.textarea)
			o.resize()
			osvc_tools(o.div, {
				"resize": o.resize,
				"link": o.link
			})
		},
		function() {
			o.div.html(services_ajax_error_fmt(xhr, stat, error))
		})
	}

	o.init()
	return o
}
