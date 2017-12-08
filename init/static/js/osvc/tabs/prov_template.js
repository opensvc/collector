function prov_template_tabs(divid, options) {
	var o = tabs(divid)
	o.options = options
	o.options.bgcolor = osvc.colors.svc
	o.options.icon = "prov"
	o.link = {
		"fn": arguments.callee.name,
		"title": "link."+arguments.callee.name
	}

	o.load(function() {
		if (o.options.tpl_name) {
			var title = o.options.tpl_name
		} else {
			var title = o.options.tpl_id
		}
		o.closetab.text(title)

		// tab properties
		i = o.register_tab({
			"title": "form_tabs.properties",
			"title_class": "icon prov"
		})
		o.tabs[i].callback = function(divid) {
			prov_template_properties(divid, o.options)
		}

		// tab definition
		i = o.register_tab({
			"title": "form_tabs.definition",
			"title_class": "icon edit16"
		})
		o.tabs[i].callback = function(divid) {
			prov_template_definition(divid, o.options)
		}

		// tab revision
		i = o.register_tab({
			"title": "form_tabs.revisions",
			"title_class": "icon time16"
		})
		o.tabs[i].callback = function(divid) {
			generic_revisions(divid, {
				"id": o.options.tpl_id,
				"base_url": "/provisioning_templates"
			})
		}

		// tab wiki
		i = o.register_tab({
			"title": "node_tabs.wiki",
			"title_class": "icon edit"
		})
		o.tabs[i].callback = function(divid) {
			wiki(divid, {"nodes": o.options.tpl_id, "type": "tpl"})
		}

		o.set_tab(o.options.tab)
	})
	return o
}

function prov_template_properties(divid, options) {
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
		o.info_id = o.div.find("#id")
		o.info_tpl_name = o.div.find("#tpl_name")
		o.info_tpl_comment = o.div.find("#tpl_comment")
		o.info_tpl_author = o.div.find("#tpl_author")
		o.info_tpl_created = o.div.find("#tpl_created")
		o.info_publications = o.div.find("#publications")
		o.info_publications_title = o.div.find("#publications_title")
		o.info_responsibles = o.div.find("#responsibles")
		o.info_responsibles_title = o.div.find("#responsibles_title")
		o.load_form()
	}

	o.load_form = function() {
		services_osvcgetrest("/provisioning_templates/%1", [o.options.tpl_id], "", function(jd) {
			o._load_form(jd.data[0])
		})
	}

	o._load_form = function(data) {
		o.info_id.html(data.id)
		o.info_tpl_name.html(data.tpl_name)
		o.info_tpl_comment.html(data.tpl_comment)
		o.info_tpl_author.html(data.tpl_author)
		o.info_tpl_created.html(osvc_date_from_collector(data.tpl_created))

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
								"fn": "data_action_del_prov_templates",
								"privileges": ["Manager", "ProvisioningManager"]
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
			"privileges": ["ProvisioningManager", "Manager"],
			"post": function(data, callback, error_callback) {
				services_osvcpostrest("/provisioning_templates/%1", [o.options.tpl_id], "", data, callback, error_callback)
			}
		})
		prov_template_publications({
			"tid": o.info_publications,
			"tpl_id": data.id
		})
		prov_template_responsibles({
			"tid": o.info_responsibles,
			"tpl_id": data.id
		})
	}

	o.div.load("/init/static/views/prov_template_properties.html?v="+osvc.code_rev, function() {
		o.div.i18n()
		o.init()
	})

	return o
}


function prov_template_definition(divid, options) {
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
		o.div.empty()
		services_osvcgetrest("/provisioning_templates/%1", [o.options.tpl_id], {"props": "tpl_definition"}, function(jd) {
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
		if (data.tpl_definition && (data.tpl_definition.length > 0)) {
			var text = data.tpl_definition
		} else {
			var text = ""
		}
		o.editor = osvc_editor(o.editor_div, {
			"text": text,
			"mode": "ini",
			"obj_type": "provisioning_templates",
			"obj_id": o.options.tpl_id,
			"save": o.save,
			"callback": o.resize
		})
		osvc_tools(o.div, {
			"resize": o.resize,
			"link": o.link
		})
	}

	o.save = function(text) {
		var data = {
			"tpl_definition": text
		}
		services_osvcpostrest("/provisioning_templates/%1", [o.options.tpl_id], "", data, function(jd) {
			if (rest_error(jd)) {
				osvc.flash.error(services_error_fmt(jd))
				return
			}
			o.init()
		},
		function(xhr, stat, error) {
			osvc.flash.error(services_ajax_error_fmt(xhr, stat, error))
		})
	}

	o.init()

	return o
}

