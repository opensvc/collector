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
			"title": "actionq_tabs.properties",
			"title_class": "icon fa-list-ul"
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
		osvc_tools(o.div, {
			"link": o.link
		})
		o.output_id = o.div.find("#id")
		o.output_ret = o.div.find("#ret")
		o.output_action_type = o.div.find("#action_type")
		o.output_node_id = o.div.find("#node_id")
		o.output_svc_id = o.div.find("#svc_id")
		o.output_status = o.div.find("#status")
		o.output_date_queued = o.div.find("#date_queued")
		o.output_date_dequeued = o.div.find("#date_dequeued")
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
		o.output_id.html(o.data.id)
		o.output_ret.html(o.data.ret)
		o.output_action_type.html(o.data.action_type)
		o.output_node_id.html(o.data.node_id).osvc_nodename({tag: true})
		o.output_svc_id.html(o.data.svc_id).osvc_svcname({tag: true})
		o.output_status.html(o.data.status)
		$.data(o.output_status[0], "v", o.data.status)
		cell_decorator_action_q_status(o.output_status)
		o.output_date_queued.html(o.data.date_queued)
		o.output_date_dequeued.html(o.data.date_dequeued)
		o.output_command.html(o.data.command)
		o.output_stderr.html(o.data.stderr)
		o.output_stdout.html(o.data.stdout)
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
									"title": "action_menu.cancel",
									"class": "del16",
									"fn": "data_action_action_queue_cancel",
									"privileges": ["Manager", "NodeExec", "CompExec"]
								},
								{
									"title": "action_menu.redo",
									"class": "refresh16",
									"fn": "data_action_action_queue_redo",
									"privileges": ["Manager", "NodeExec", "CompExec"]
								}
							]
						}
					]
				}
		]
		tab_tools({
			"div": o.div.find("#tools"),
			"data": {"id": o.data.id},
			"am_data": am_data
		})
	}

	o.div.load("/init/static/views/actionq_properties.html?v="+osvc.code_rev, function() {
		o.div.i18n()
		o.init()
	})

	return o
}

