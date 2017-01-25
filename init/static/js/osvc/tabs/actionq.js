function actionq_tabs(divid, options) {
	var o = tabs(divid)
	o.options = options
	o.options.bgcolor = osvc.colors.action
	o.options.icon = "action16"
	o.link = {
		"fn": arguments.callee.name,
		"title": "link."+arguments.callee.name
	}

	o.load(function() {
		var title = o.options.actionq_id
		o.closetab.text(title)

		// tab outputs
		i = o.register_tab({
			"title": "actionq_tabs.outputs",
			"title_class": "icon action16"
		})
		o.tabs[i].callback = function(divid) {
			actionq_outputs(divid, o.options)
		}

		o.set_tab(o.options.tab)
	})

	return o
}

function actionq_outputs(divid, options) {
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
		o.output_command = o.div.find("#command")
		o.output_stderr = o.div.find("#stderr")
		o.output_stdout = o.div.find("#stdout")
		o.load_actionq()
	}

	o.load_actionq = function() {
		services_osvcgetrest("/actions/%1", [o.options.actionq_id], "", function(jd) {
			o.data = jd.data[0]
			o._load_actionq()
		})
	}

	o._load_actionq = function() {
		o.output_command.html(o.data.command)
		o.output_stderr.html(o.data.stderr)
		o.output_stdout.html(o.data.stdout)
	}

	o.div.load("/init/static/views/actionq_outputs.html?v="+osvc.code_rev, function() {
		o.div.i18n()
		o.init()
	})

	return o
}

