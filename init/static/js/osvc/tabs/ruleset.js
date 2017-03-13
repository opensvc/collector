function ruleset_tabs(divid, options) {
	var o = tabs(divid)
	o.options = options
	o.options.bgcolor = osvc.colors.comp
	o.options.icon = "rset16"
	o.link = {
		"fn": arguments.callee.name,
                "parameters": o.options,
                "title": "format_title",
                "title_args": {
                        "type": "ruleset",
                        "name": o.options.ruleset_name
                }

	}

	o.load(function() {
		if (!("ruleset_id" in o.options)) {
			services_osvcgetrest("/compliance/rulesets", "", {"meta": "0", "filters": ["ruleset_name "+o.options.ruleset_name]}, function(jd) {
				o.options.ruleset_id = jd.data[0].id
				o.link.title_args.id = jd.data[0].id
				o._load()
			})
		} else {
			o._load()
		}
	})

	o._load = function() {
		if (o.options.ruleset_name) {
			var title = o.options.ruleset_name
		} else {
			var title = o.options.ruleset_id
		}
		o.closetab.text(title)

		// tab properties
		i = o.register_tab({
			"title": "ruleset_properties.base",
			"title_class": "icon rset16"
		})
		o.tabs[i].callback = function(divid) {
			ruleset_properties(divid, o.options)
		}

		// tab content
		i = o.register_tab({
			"title": "ruleset_tabs.content",
			"title_class": "icon rset16"
		})
		o.tabs[i].callback = function(divid) {
			ruleset_content(divid, o.options)
		}

		// tab export
		i = o.register_tab({
			"title": "ruleset_tabs.export",
			"title_class": "icon log16"
		})
		o.tabs[i].callback = function(divid) {
			ruleset_export(divid, o.options)
		}

		o.set_tab(o.options.tab)
	}

	return o
}

function ruleset_export(divid, options) {
	var o = {}
	o.options = options
	o.div = $("#"+divid)
	o.link = {
		"fn": arguments.callee.name,
		"parameters": o.options,
		"title": "format_title",
                "title_args": {
                        "type": "ruleset",
                        "id": o.options.ruleset_id,
                        "name": o.options.ruleset_name
                }
	}

	o.resize = function() {
		var max_height = max_child_height(o.div)
		o.textarea.outerHeight(max_height)
	}

	spinner_add(o.div)
	services_osvcgetrest("R_COMPLIANCE_RULESET_EXPORT", [o.options.ruleset_id], "", function(jd) {
		if (!jd && jd.error) {
			o.div.html(services_error_fmt(jd))
			return
		}
		o.textarea = $("<textarea class='export_data'>")
		o.textarea.prop("disabled", true)
		o.textarea.text(JSON.stringify(jd, null, 4))
		o.div.css({"padding": "4px"})
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

function ruleset_content(divid, options) {
	var o = {}
	o.options = options
	o.div = $("#"+divid)
	o.link = {
		"fn": arguments.callee.name,
		"parameters": o.options,
		"title": "format_title",
                "title_args": {
                        "type": "ruleset",
                        "id": o.options.ruleset_id,
                        "name": o.options.ruleset_name
                }
	}
	o.rulesets = {}
	var head = {}
	services_osvcgetrest("R_COMPLIANCE_RULESET_EXPORT", [o.options.ruleset_id], "", function(jd) {
		if (!jd && jd.error) {
			o.div.html(services_error_fmt(jd))
			return
		}
		for (var i=0; i<jd.rulesets.length; i++) {
			var rset = jd.rulesets[i]
			o.rulesets[rset.ruleset_name] = rset
			if (o.options.ruleset_name && (o.options.ruleset_name == rset.ruleset_name)) {
				head = rset
				continue
			}
			if (o.options.ruleset_id && (o.options.ruleset_id == rset.id)) {
				head = rset
				continue
			}
		}
		var div = $("<div style='padding:1em'></div>")
		o.area = div
		o.div.append(div)
		o.render(head)
		osvc_tools(o.div, {
			"link": o.link
		})
	},
	function() {
		o.div.html(services_ajax_error_fmt(xhr, stat, error))
	})

	o.render_title = function(chain) {
		var div = $("<div></div>")
		for (var i=0; i<chain.length; i++) {
			var rset = chain[i]
			if (i>0) {
				div.append("<br>")
				div.append("<span class='icon fa-arrow-right'></span>")
			}
			var e = $("<span style='opacity:0.5;font-size:1.2em'></span>")
			e.text(rset.ruleset_name)
			e.osvc_ruleset()
			if (i == chain.length-1) {
				e.css({"opacity": 1})
			}
			div.append(e)
		}
		return div
	}

	o.render = function(rset, chain) {
		var p1 = $("<p></p>")
		var p2 = $("<p></p>")
		var p3 = $("<p></p>")

		if (!chain) {
			var chain = []
		}
		o.area.append(o.render_title([].concat(chain, [rset])))

		p1.text(i18n.t("ruleset_tab.type", {"type": rset.ruleset_type}))
		p2.text(i18n.t("ruleset_tab.public", {"public": rset.ruleset_public}))
		o.area.append(p1)
		o.area.append(p2)

		if (rset.ruleset_type == "contextual") {
			p3.text(i18n.t("ruleset_tab.filterset"))
			var e_fset = $("<span>"+rset.fset_name+"</span>")
			p3.append(e_fset)
			e_fset.osvc_filterset()
			o.area.append(p3)
		}

		for (var i=0; i<rset.variables.length; i++) {
			var variable = rset.variables[i]
			try {
				var data = $.parseJSON(variable.var_value)
			} catch(e) {
				var data = variable.var_value
			}
			var variable_name = $("<h3 class='b'></h3>")
			variable_name.text(variable.var_name)
			o.area.append(variable_name)

			var p1 = $("<p></p>")
			p1.text(i18n.t("designer.var_class", {"name": variable.var_class}))
			o.area.append(p1)

			var p2 = $("<p></p>")
			var last_mod = $("<span>"+i18n.t("variable_tabs.var_last_mod")+"</span>")
			var fullname = $("<span fullname='"+variable.var_author+"'>"+variable.var_author+"</span>")
			var mod_date = $("<span>"+i18n.t("variable_tabs.var_mod_on")+" "+variable.var_updated+"</span>")
			p2.append([last_mod, " " ,fullname, " ", mod_date])
			fullname.osvc_fullname()
			o.area.append(p2)

			o.area.append("<br>")

			var form_div = $("<div></div>")
			form_div.uniqueId()
			o.area.append(form_div)

			
			form(form_div.attr("id"), {
				"data": data,
				"var_id": variable.id,
				"rset_id": rset.id,
				"display_mode": true,
				"digest": true,
				"form_name": variable.var_class,
				"disable_edit": false
			})
			o.area.append("<br>")
		}
		o.area.append("<br>")

		if (!rset.rulesets) {
			return
		}
		for (var i=0; i<rset.rulesets.length; i++) {
			o.render(o.rulesets[rset.rulesets[i]], [].concat(chain, [rset]))
		}
	}
}

function ruleset_properties(divid, options) {
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
                        "type": "ruleset",
                        "id": o.options.ruleset_id,
                        "name": o.options.ruleset_name
                }
	}

	o.init = function() {
		osvc_tools(o.div, {
			"link": o.link
		})
		o.info_id = o.div.find("#id")
		o.info_ruleset_name = o.div.find("#ruleset_name")
		o.info_ruleset_type = o.div.find("#ruleset_type")
		o.info_ruleset_public = o.div.find("#ruleset_public")
		o.info_publications = o.div.find("#publications")
		o.info_responsibles = o.div.find("#responsibles")
		o.info_publications_title = o.div.find("#publications_title")
		o.info_responsibles_title = o.div.find("#responsibles_title")
		o.info_modulesets = o.div.find("#modulesets")
		o.info_modulesets_title = o.div.find("#modulesets_title")
		o.info_rulesets = o.div.find("#rulesets")
		o.info_rulesets_title = o.div.find("#rulesets_title")
		o.load_ruleset()
	}

	o.load_ruleset = function() {
		services_osvcgetrest("/compliance/rulesets/%1", [o.options.ruleset_id], "", function(jd) {
			o._load_ruleset(jd.data[0])
		})
	}

	o._load_ruleset = function(data) {
		o.info_id.html(data.id)
		o.info_ruleset_name.html(data.ruleset_name)
		o.info_ruleset_type.html(data.ruleset_type)
		o.info_ruleset_public.html(data.ruleset_public)

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
								"fn": "data_action_del_rulesets",
								"privileges": ["Manager", "CompManager"]
							}
						]
					}
				]
			}
		]
		tab_tools({
			"div": o.div.find("#tools"),
			"data": {"ruleset_id": data.id},
			"am_data": am_data
		})

		tab_properties_generic_updater({
			"div": o.div,
			"privileges": ["FormsManager", "Manager"],
			"post": function(data, callback, error_callback) {
				services_osvcpostrest("/compliance/rulesets/%1", [o.options.ruleset_id], "", data, callback, error_callback)
			}
		})
		tab_properties_generic_autocomplete({
			"div": o.info_ruleset_type,
			"privileges": ["CompManager", "Manager"],
			"post": function(_data, callback, error_callback) {
				services_osvcpostrest("/compliance/rulesets/%1", [data.id], "", _data, callback, error_callback)
			},
			"get": function(callback) {
				var data = ["contextual", "explicit"]
				callback(data)
			}
		})
		ruleset_publications({
			"tid": o.info_publications,
			"ruleset_id": data.id
		})
		ruleset_responsibles({
			"tid": o.info_responsibles,
			"ruleset_id": data.id
		})

                ruleset_nodes({
                        "tid": o.div.find("#nodes"),
                        "ruleset_id": data.id,
                        "title": "ruleset_properties.nodes",
                        "e_title": o.div.find("#nodes_title")
                })

                ruleset_services({
                        "tid": o.div.find("#services"),
                        "ruleset_id": data.id,
                        "title": "ruleset_properties.services",
                        "e_title": o.div.find("#services_title")
                })

                ruleset_services({
                        "tid": o.div.find("#encap_services"),
                        "ruleset_id": data.id,
                        "slave": true,
                        "title": "ruleset_properties.encap_services",
                        "e_title": o.div.find("#encap_services_title")
                })

                services_osvcgetrest("/compliance/rulesets/%1/usage", [data.id], "", function(jd) {
                        tab_properties_generic_list({
                                "data": jd.data.modulesets,
                                "key": "modset_name",
                                "item_class": "icon modset16",
                                "id": "id",
                                "flash_id_prefix": "modset",
                                "bgcolor": osvc.colors.comp,
                                "e_title": o.info_modulesets_title,
                                "e_list": o.info_modulesets,
                                "ondblclick": function(divid, data) {
                                        moduleset_tabs(divid, {"modset_id": data.id, "modset_name": data.name})
                                }
                        })
                        tab_properties_generic_list({
                                "data": jd.data.rulesets,
                                "key": "ruleset_name",
                                "item_class": "icon rset16",
                                "id": "id",
                                "flash_id_prefix": "rset",
                                "bgcolor": osvc.colors.comp,
                                "e_title": o.info_rulesets_title,
                                "e_list": o.info_rulesets,
                                "ondblclick": function(divid, data) {
                                        ruleset_tabs(divid, {"ruleset_id": data.id, "ruleset_name": data.name})
                                }
                        })
                })
        }

	o.div.load("/init/static/views/ruleset_properties.html?v="+osvc.code_rev, function() {
		o.div.i18n()
		o.init()
	})

	return o
}


