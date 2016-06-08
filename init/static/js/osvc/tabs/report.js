function report_tabs(divid, options) {
	var o = tabs(divid)
	o.options = options
	o.options.bgcolor = osvc.colors.stats
	o.options.icon = "spark16"

	o.load(function() {
		if (o.options.report_name) {
			var title = o.options.report_name
		} else {
			var title = o.options.report_id
		}
		o.closetab.text(title)

		// tab properties
		i = o.register_tab({
			"title": "report_tabs.properties",
			"title_class": "icon wf16"
		})
		o.tabs[i].callback = function(divid) {
			report_properties(divid, o.options)
		}

		// tab display
		i = o.register_tab({
			"title": "report_tabs.rendering",
			"title_class": "icon wf16"
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

		// tab export
		i = o.register_tab({
			"title": "report_tabs.export",
			"title_class": "icon csv"
		})
		o.tabs[i].callback = function(divid) {
			report_export(divid, o.options)
		}

		o.set_tab(o.options.tab)
	})
	return o
}

function report_properties(divid, options) {
	var o = {}

	// store parameters
	o.divid = divid
	o.div = $("#"+divid)
	o.options = options

	o.init = function() {
		o.info_id = o.div.find("#id")
		o.info_report_name = o.div.find("#report_name")
		o.load()
	}

	o.load= function() {
		services_osvcgetrest("/reports/%1", [o.options.report_id], "", function(jd) {
			o._load(jd.data[0])
		})
	}

	o._load= function(data) {
		o.info_id.html(data.id)
		o.info_report_name.html(data.report_name)

		var am_data = [
			{
				"title": "action_menu.data_actions",
				"class": "hd16",
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

	o.init = function() {
		o.div.empty()
		services_osvcgetrest("/reports/%1", [o.options.report_id], {"props": "report_yaml"}, function(jd) {
			o.load(jd.data[0])
		})
	}

	o.load = function(data) {
		var div = $("<div style='padding:1em'></div>")
		o.div.append(div)
		if (data.report_yaml && (data.report_yaml.length > 0)) {
			var text = data.report_yaml
		} else {
			var text = ""
		}
		o.editor = osvc_editor(div, {
			"text": text,
			"privileges": ["Manager", "ReportsManager"],
			"save": o.save
		})
	}

	o.save = function(text) {
		var data = {
			"report_yaml": text
		}
		services_osvcpostrest("/reports/%1", [o.options.report_id], "", data, function(jd) {
			if (jd.error && (jd.error.length > 0)) {
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

	o.init = function() {
		div = $("<textarea class='export_data'>")
		div.prop("disabled", true)

		spinner_add(o.div)
		services_osvcgetrest("/reports/%1/export", [o.options.report_id], "", function(jd) {
			if (jd.error) {
				o.div.html(services_error_fmt(jd))
			}
			div.text(JSON.stringify(jd, null, 4))
			o.div.html(div)
		},
		function() {
			o.div.html(services_ajax_error_fmt(xhr, stat, error))
		})
	}

	o.init()
	return o
}
