function run_status_tabs(divid, options) {
	var o = tabs(divid)
	o.options = options
	o.options.bgcolor = osvc.colors.comp
	o.options.icon = "comp16"
	o.link = {
		"fn": arguments.callee.name,
		"title": "link."+arguments.callee.name
	}

	o.load(function() {
		var title = o.options.id
		o.closetab.text(title)

		// tab outputs
		i = o.register_tab({
			"title": "run_status_tabs.properties",
			"title_class": "icon comp16"
		})
		o.tabs[i].callback = function(divid) {
			run_status_outputs(divid, o.options)
		}

		o.set_tab(o.options.tab)
	})

	return o
}

function run_status_outputs(divid, options) {
	var o = {}

	// store parameters
	o.divid = divid
	o.div = $("#"+divid)
	o.options = options
	o.link = {
		"fn": arguments.callee.name,
		"parameters": o.options,
		"title": "link."+arguments.callee.name
	}

	o.init = function() {
		o.run_status_node_id = o.div.find("#node_id")
		o.run_status_svc_id = o.div.find("#svc_id")
		o.run_status_run_module = o.div.find("#run_module")
		o.run_status_run_action = o.div.find("#run_action")
		o.run_status_run_status = o.div.find("#run_status")
		o.run_status_run_date = o.div.find("#run_date")
		o.run_status_run_log = o.div.find("#run_log")
		o.load_run_status()
	}

	o.load_run_status = function() {
		services_osvcgetrest("/compliance/logs/%1", [o.options.id], "", function(jd) {
			o.data = jd.data[0]
			o._load_run_status()
                })
	}

	o._load_run_status = function() {
		o.run_status_node_id.html(o.data.node_id)
		o.run_status_svc_id.html(o.data.svc_id)
		o.run_status_run_module.html(o.data.run_module)
		o.run_status_run_action.html(o.data.run_action)
		o.run_status_run_status.html(o.data.run_status)
		o.run_status_run_date.html(o.data.run_date)
		o.run_status_run_log.html(o.data.run_log)
	}

	o.div.load("/init/static/views/run_status_properties.html?v="+osvc.code_rev, function() {
		o.div.i18n()
		o.init()
	})

	return o
}

