function comp_status_tabs(divid, options) {
	options.url = "/compliance/status/%1"
	return run_status_tabs(divid, options)
}

function comp_log_tabs(divid, options) {
	options.url = "/compliance/logs/%1"
	return run_status_tabs(divid, options)
}

function run_status_tabs(divid, options) {
	var o = tabs(divid)
	o.options = options
	o.options.bgcolor = osvc.colors.comp
	o.options.icon = "log16"
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

		// tab history
		i = o.register_tab({
			"title": "run_status_tabs.history",
			"title_class": "icon complog"
		})
		o.tabs[i].callback = function(divid) {
			$("#"+divid).addClass("p-3")
			run_status_history(divid, o.options)
		}

		// tab ruleset
		i = o.register_tab({
			"title": "col.Ruleset",
			"title_class": "icon comp16"
		})
		o.tabs[i].callback = function(divid) {
			$("#"+divid).addClass("p-3")
			run_status_ruleset(divid, o.options)
		}

		o.set_tab(o.options.tab)
	})

	return o
}

function run_status_history(divid, options) {
	var o = {}

	o.divid = divid
	o.div = $("#"+divid)
	o.div.css("background", "white")
	o.options = options

	o.init = function() {
		o.load_history()
	}

	o.load_history = function() {
		services_osvcgetrest(o.options.url, [o.options.id], "", function(jd) {
			o.data = jd.data[0]
			o._load_history()
		})
	}

	o._load_history = function() {
		comp_log(o.divid, {"module": o.data.run_module, "svc_id": o.data.svc_id, "node_id": o.data.node_id})
	}

	o.init()

	return o
}

function run_status_outputs(divid, options) {
	var o = {}

	// store parameters
	o.divid = divid
	o.div = $("#"+divid)
	o.div.css("background", "white")
	o.options = options
	o.link = {
		"fn": arguments.callee.name,
		"parameters": o.options,
		"title": "link."+arguments.callee.name
	}

	o.init = function() {
		osvc_tools(o.div, {
			"link": o.link
		})
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
		services_osvcgetrest(o.options.url, [o.options.id], "", function(jd) {
			o.data = jd.data[0]
			o._load_run_status()
                })
	}

	o._load_run_status = function() {
		o.run_status_node_id.html(o.data.node_id).osvc_nodename({tag: true})
		o.run_status_svc_id.html(o.data.svc_id).osvc_svcname({tag: true})
		o.run_status_run_module.html(o.data.run_module)
		o.run_status_run_action.html(o.data.run_action)
		o.run_status_run_status.html(o.data.run_status)
		$.data(o.run_status_run_status[0], "v", o.data.run_status)
		cell_decorator_run_status(o.run_status_run_status)
		o.run_status_run_date.html(o.data.run_date)
		o.run_status_run_log.html(o.data.run_log)
		$.data(o.run_status_run_log[0], "v", o.data.run_log)
		cell_decorator_run_log(o.run_status_run_log)
	}

	o.div.load("/init/static/views/run_status_properties.html?v="+osvc.code_rev, function() {
		o.div.i18n()
		o.init()
	})

	return o
}

function run_status_ruleset(divid, options) {
	var o = {}
	o.divid = divid
	o.options = options
	o.div = $("#"+divid)
	o.div.addClass("spinner")
	services_osvcgetrest(o.options.url, [o.options.id], "", function(jd) {
		var url = services_get_url() + "/init/compliance/ajax_rset_md5?rset_md5="+jd.data[0].rset_md5
		sync_ajax(url, [], divid, function(){
			o.div.removeClass("spinner")
		})
	})
	return o
}
