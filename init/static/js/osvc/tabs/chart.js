//
// chart
//
function chart_tabs(divid, options) {
	var o = tabs(divid)
	o.options = options
	o.options.bgcolor = osvc.colors.stats
	o.options.icon = "spark16"

	o.load(function() {
		if (o.options.chart_name) {
			var title = o.options.chart_name
		} else {
			var title = o.options.chart_id
		}
		o.closetab.text(title)

		// tab properties
		i = o.register_tab({
			"title": "chart_tabs.properties",
			"title_class": "icon wf16"
		})
		o.tabs[i].callback = function(divid) {
			chart_properties(divid, o.options)
		}

		// rendering properties
		i = o.register_tab({
			"title": "chart_tabs.rendering",
			"title_class": "icon wf16"
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
	})
	return o
}

function chart_properties(divid, options) {
	var o = {}

	// store parameters
	o.divid = divid
	o.div = $("#"+divid)
	o.options = options

	o.init = function() {
		o.info_id = o.div.find("#id")
		o.info_chart_name = o.div.find("#chart_name")
		o.load()
	}

	o.load= function() {
		services_osvcgetrest("/reports/charts/%1", [o.options.chart_id], "", function(jd) {
			o._load(jd.data[0])
		})
	}

	o._load= function(data) {
		o.info_id.html(data.id)
		o.info_chart_name.html(data.chart_name)

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

	o.init = function() {
		o.div.empty()
		services_osvcgetrest("/reports/charts/%1", [o.options.chart_id], {"props": "chart_yaml"}, function(jd) {
			o.load(jd.data[0])
		})
	}

	o.load = function(data) {
		var div = $("<div style='padding:1em'></div>")
		o.div.append(div)
		if (data.chart_yaml && (data.chart_yaml.length > 0)) {
			var text = data.chart_yaml
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
			"chart_yaml": text
		}
		services_osvcpostrest("/reports/charts/%1", [o.options.chart_id], "", data, function(jd) {
			if (jd.error && (jd.error.length > 0)) {
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

