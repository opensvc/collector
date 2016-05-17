//
// prov template
//
function metric_tabs(divid, options) {
	var o = tabs(divid)
	o.options = options

	o.load(function() {
		if (o.options.metric_name) {
			var title = o.options.metric_name
		} else {
			var title = o.options.metric_id
		}
		o.closetab.children("p").text(title)

		// tab properties
		i = o.register_tab({
			"title": "metric_tabs.properties",
			"title_class": "icon spark16"
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
	})
	return o
}

function metric_properties(divid, options) {
	var o = {}

	// store parameters
	o.divid = divid
	o.div = $("#"+divid)
	o.options = options

	o.init = function() {
		o.info_id = o.div.find("#id")
		o.info_metric_name = o.div.find("#metric_name")
		o.info_metric_author = o.div.find("#metric_author")
		o.info_metric_created = o.div.find("#metric_created")
		o.info_metric_col_instance_label = o.div.find("#metric_col_instance_label")
		o.info_metric_col_value_index = o.div.find("#metric_col_value_index")
		o.info_metric_col_instance_index = o.div.find("#metric_col_instance_index")
		o.load()
	}

	o.load = function() {
		services_osvcgetrest("/reports/metrics/%1", [o.options.metric_id], "", function(jd) {
			o._load(jd.data[0])
		})
	}

	o._load = function(data) {
		o.info_id.html(data.id)
		o.info_metric_name.html(data.metric_name)
		o.info_metric_author.html(data.metric_author)
		o.info_metric_created.html(osvc_date_from_collector(data.metric_created))
		o.info_metric_col_instance_label.html(data.metric_col_instance_label)
		o.info_metric_col_value_index.html(data.metric_col_value_index)
		o.info_metric_col_instance_index.html(data.metric_col_instance_index)

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
	}

	o.div.load("/init/static/views/metric_properties.html", function() {
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

	o.init = function() {
		o.div.empty()
		services_osvcgetrest("/reports/metrics/%1", [o.options.metric_id], {"props": "metric_sql"}, function(jd) {
			o.load(jd.data[0])
			o.test(jd.data[0])
		})
	}

	o.load = function(data) {
		var div = $("<div style='padding:1em'></div>")
		o.div.append(div)
		if (data.metric_sql && (data.metric_sql.length > 0)) {
			var text = data.metric_sql
		} else {
			var text = i18n.t("metric_properties.no_request")
		}
		$.data(div, "v", text)
		cell_decorator_sql(div)

		div.bind("click", function() {
			div.hide()
			var edit = $("<div name='edit'></div>")
			var textarea = $("<textarea class='oi oidefinition'></textarea>")
			var button = $("<input type='button' style='margin:0.5em 0 0.5em 0'>")
			button.attr("value", i18n.t("metric_properties.save"))
			if (data.metric_sql && (data.metric_sql.length > 0)) {
				textarea.val(div.text())
			}
			edit.append(textarea)
			edit.append(button)
			o.div.append(edit)
			button.bind("click", function() {
				var data = {
					"metric_sql": textarea.val()
				}
				services_osvcpostrest("/reports/metrics/%1", [o.options.metric_id], "", data, function(jd) {
					if (jd.error && (jd.error.length > 0)) {
						$(".flash").show("blind").html(services_error_fmt(jd))
						return
					}
					o.init()
				},
				function(xhr, stat, error) {
					$(".flash").show("blind").html(services_ajax_error_fmt(xhr, stat, error))
				})
			})
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

