//
// workflow
//
function workflow_tabs(divid, options) {
	var o = tabs(divid)
	o.options = options
	o.options.bgcolor = osvc.colors.form
	o.options.icon = "wf16"
	o.link = {
		"fn": arguments.callee.name,
		"parameters": o.options,
		"title": "format_title",
		"title_args": {
			"type": "form",
			"id": o.options.workflow_id
		}
	}

	o.load(function() {
		if (o.options.form_id && !o.options.workflow_id) {
			o.load_from_form_id()
		} else {
			o.load_from_workflow_id()
		}
	})

	o.load_from_form_id = function() {
		services_osvcgetrest("/forms_store/%1/dump", [o.options.form_id], "", function(jd) {
			o.data = jd.data[0]["workflow"]
			console.log(jd.data[0])
			o.options.workflow_id = o.data.id
			o.link.title_args.name = o.data.id+"/"+o.data.head.form_name
			o.link.title_args.id = o.data.id
			o._load()
		})
	}

	o.load_from_workflow_id = function() {
		services_osvcgetrest("/workflows/%1/dump", [o.options.workflow_id], "", function(jd) {
			o.data = jd.data[0]
			o.link.title_args.name = o.data.id+"/"+o.data.head.form_name
			if (!o.options.form_id) {
				o.options.form_id = o.data.form_head_id
			}
			o._load()
		})
	}

	o._load = function() {
		o.closetab.text(o.data.id+"/"+o.data.head.form_name)

		// tab properties
		i = o.register_tab({
			"title": "node_tabs.properties",
			"title_class": "icon fa-list-ul"
		})
		o.tabs[i].callback = function(divid) {
			workflow_properties(divid, o.options)
		}
		i = o.register_tab({
			"title": "workflow_tabs.steps",
			"title_class": "icon wf16"
		})
		o.tabs[i].callback = function(divid) {
			workflow(divid, {
				workflow_id: o.options.workflow_id,
				form_id: o.options.form_id
			})
		}
		i = o.register_tab({
			"title": "workflow_tabs.derive",
			"title_class": "icon wf16"
		})
		o.tabs[i].callback = function(divid) {
			workflow_derive(divid, o.options)
		}

		o.set_tab(o.options.tab)
	}
	return o
}

function workflow_properties(divid, options) {
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
			"type": "form",
			"id": o.options.workflow_id
		}
	}

	o.init = function() {
		osvc_tools(o.div, {
			"link": o.link
		})
		// non updateable
		o.info_id = o.div.find("#id")
		o.info_status = o.div.find("#status")
		o.info_steps = o.div.find("#steps")
		o.info_form_head_id = o.div.find("#form_head_id")
		o.info_creator = o.div.find("#creator")
		o.info_create_date = o.div.find("#create_date")
		o.info_last_form_id = o.div.find("#last_form_id")
		o.info_last_assignee = o.div.find("#last_assignee")
		o.info_last_update = o.div.find("#last_update")

		o.load_workflow()
	}

	o.load_workflow = function() {
		if (o.options.data) {
			o._load_workflow(o.options.data)
		} else {
			services_osvcgetrest("/workflows/%1/dump", [o.options.workflow_id], "", function(jd) {
				o._load_workflow(jd.data[0])
			})
		}
	}

	o._load_workflow = function(data) {
		o.link.title_args.name = data.id+"/"+data.head.form_name
		o.info_id.html(data.id)
		o.info_status.html(data.status)
		o.info_steps.html(data.steps)
		o.info_form_head_id.html(data.form_head_id)
		o.info_creator.html(data.creator)
		o.info_create_date.html(data.create_date)
		o.info_last_form_id.html(data.last_form_id)
		o.info_last_assignee.html(data.last_assignee)
		o.info_last_update.html(data.last_update)
	}

	o.div.load("/init/static/views/workflow_properties.html?v="+osvc.code_rev, function() {
		o.div.i18n()
		o.init()
	})

	return o
}

function workflow_derive(divid, options) {
	var o = {}
	o.options = options
	o.div = $("#"+divid)
	o.link = {
		"fn": arguments.callee.name,
		"parameters": o.options,
		"title": "format_title",
		"title_args": {
			"type": "form",
			"id": o.options.workflow_id
		}
	}

	o.init = function(data) {
		var div = $("<div style='padding:1em'></div>")
		var p1 = $("<div style='padding-bottom:1em;font-size:1.25em;font-style:italic'></div>")
		var p2 = $("<div></div>")
		div.append([p1, p2])
		p1.text(i18n.t("workflow_tabs.derive_text"))
		p2.uniqueId()
		o.div.append(div)
		o.link.title_args.name = o.data.id+"/"+o.data.head.form_name
		osvc_tools(o.div, {
			"link": o.link
		})
		o.form = form(p2.attr("id"), {
			form_name: o.data.head.form_name,
			data: $.parseJSON(o.data.head.form_data)
		})
	}

	o.load = function() {
		if (o.options.data) {
			o.workflow_data = o.options.data
			o.init()
		} else {
			services_osvcgetrest("/workflows/%1/dump", [o.options.workflow_id], "", function(jd) {
				o.data = jd.data[0]
				o.init()
			})
		}
	}

	o.load()

	return o
}
