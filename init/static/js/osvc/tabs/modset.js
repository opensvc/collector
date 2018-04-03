//
// moduleset
//
function moduleset_tabs(divid, options) {
	var o = tabs(divid)
	o.options = options
	o.options.icon = "modset16"
	o.options.bgcolor = osvc.colors.modset
	o.link = {
		"fn": arguments.callee.name,
                "title": "format_title",
                "title_args": {
                        "type": "moduleset",
                        "name": o.options.modset_name
		}
	}

        o.load(function() {
                if (!("modset_id" in o.options)) {
                        services_osvcgetrest("/compliance/modulesets", "", {"meta": "0", "filters": ["modset_name "+o.options.modset_name]}, function(jd) {
                                o.options.modset_id = jd.data[0].id
				o.link.title_args.id = jd.data[0].id
                                o._load()
                        })
                } else {
                        o._load()
                }
        })

	o._load = function() {
		var title = o.options.modset_name
		o.closetab.text(title)

		// tab properties
		i = o.register_tab({
			"title": "node_tabs.properties",
			"title_class": "icon fa-list-ul"
		})
		o.tabs[i].callback = function(divid) {
			modset_properties(divid, o.options)
		}

                // tab content
                i = o.register_tab({
                        "title": "ruleset_tabs.content",
                        "title_class": "icon modset16"
                })
                o.tabs[i].callback = function(divid) {
                        modset_content(divid, o.options)
                }

		// tab export
		i = o.register_tab({
			"title": "modset_tabs.export",
			"title_class": "icon log16"
		})
		o.tabs[i].callback = function(divid) {
			modset_export(divid, o.options)
		}

		// tab wiki
		i = o.register_tab({
			"title": "node_tabs.wiki",
			"title_class": "icon edit"
		})
		o.tabs[i].callback = function(divid) {
			wiki(divid, {"nodes": o.options.modset_id, "type": "modset"})
		}

		o.set_tab(o.options.tab)
	}

	return o
}

function modset_properties(divid, options) {
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
                        "type": "moduleset",
                        "id": o.options.modset_id,
                        "name": o.options.modset_name
		}
	}

	o.init = function() {
		osvc_tools(o.div, {
			"link": o.link
		})
		o.info_id = o.div.find("#id")
		o.info_modset_name = o.div.find("#modset_name")
		o.info_modset_author = o.div.find("#modset_author")
		o.info_modset_updated = o.div.find("#modset_updated")
		o.info_nodes = o.div.find("#nodes")
		o.info_nodes_title = o.div.find("#nodes_title")
		o.info_services = o.div.find("#services")
		o.info_services_title = o.div.find("#services_title")
		o.info_modulesets = o.div.find("#modulesets")
		o.info_modulesets_title = o.div.find("#modulesets_title")
		o.info_publications = o.div.find("#publications")
		o.info_responsibles = o.div.find("#responsibles")
		o.load_form()
	}

	o.load_form = function() {
		services_osvcgetrest("/compliance/modulesets", "", {"meta": "0", "filters": ["modset_name "+o.options.modset_name]}, function(jd) {
			o.data = jd.data[0]
			o._load_form(jd.data[0])
		})
	}

	o._load_form = function(data) {
		o.info_id.html(data.id)
		o.info_modset_name.html(data.modset_name)
		o.info_modset_author.html(data.modset_author).osvc_fullname()
		o.info_modset_updated.html(osvc_date_from_collector(data.modset_updated))

		o.load_usage()

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
								"fn": "data_action_del_modulesets",
								"privileges": ["Manager", "CompManager"]
							}
						]
					}
				]
			}
		]
		tab_tools({
			"div": o.div.find("#tools"),
			"data": {"modset_id": data.id},
			"am_data": am_data
		})
                moduleset_nodes({
                        "tid": o.info_nodes,
                        "modset_id": data.id,
                        "title": "ruleset_properties.nodes",
                        "e_title": o.info_nodes_title
                })
                moduleset_services({
                        "tid": o.info_services,
                        "modset_id": data.id,
                        "title": "ruleset_properties.services",
                        "e_title": o.info_services_title
                })
		tab_properties_generic_updater({
			"div": o.div,
			"post": function(_data, callback, error_callback) {
				services_osvcpostrest("/compliance/modulesets/%1", [data.id], "", _data, callback, error_callback)
			}
		})
		modset_publications({
			"tid": o.info_publications,
			"modset_id": data.id
		})
		modset_responsibles({
			"tid": o.info_responsibles,
			"modset_id": data.id
		})
	}

	o.load_usage = function() {
		services_osvcgetrest("/compliance/modulesets/%1/usage", [o.data.id], "", function(jd) {
			tab_properties_generic_list({
				"data": jd.data.modulesets,
				"key": "modset_name",
				"item_class": "icon modset16",
				"id": "id",
				"flash_id_prefix": "modset",
				"bgcolor": osvc.colors.modset,
				"e_title": o.info_modulesets_title,
				"e_list": o.info_modulesets,
				"ondblclick": function(divid, data) {
					moduleset_tabs(divid, {"modset_id": data.id, "modset_name": data.name})
				}
			})
		})
	}

	o.div.load("/init/static/views/modset_properties.html?v="+osvc.code_rev, function() {
		o.div.i18n()
		o.init()
	})

	return o
}

function modset_content(divid, options) {
	var o = {}
	o.options = options
	o.div = $("#"+divid)
	o.link = {
		"fn": arguments.callee.name,
		"parameters": o.options,
                "title": "format_title",
                "title_args": {
                        "type": "moduleset",
                        "id": o.options.modset_id,
                        "name": o.options.modset_name
		}
	}
	o.modulesets = {}
	o.rulesets = {}
	o.modulesets_done = []
	o.rulesets_done = []
	var head = {}
	services_osvcgetrest("/compliance/modulesets/%1/export", [o.options.modset_id], "", function(jd) {
		if (!jd && jd.error) {
			o.div.html(services_error_fmt(jd))
			return
		}
		o.data = jd
		for (var i=0; i<jd.modulesets.length; i++) {
			var modset = jd.modulesets[i]
			o.modulesets[modset.modset_name] = modset
			if (o.options.modset_name && (o.options.modset_name == modset.modset_name)) {
				head = modset
				continue
			}
			if (o.options.modset_id && (o.options.modset_id == modset.id)) {
				head = modset
				continue
			}
		}
		for (var i=0; i<jd.rulesets.length; i++) {
			var ruleset = jd.rulesets[i]
			o.rulesets[ruleset.ruleset_name] = ruleset
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

	o.render_ruleset = function(ruleset_name, chain) {
		var level = chain.length
		chain = [].concat(chain, [ruleset_name])
		var sig = chain.join(",")
		var div = $("<div></div>")
		if (o.rulesets_done.indexOf(sig) >= 0) {
			console.log("loop detected:", sig)
			return div
		} else {
			o.rulesets_done.push(sig)
		}
		var ruleset= o.rulesets[ruleset_name]
		var indent = $("<span></span>")
		indent.css({"width": 2*level+"em", "display": "inline-block"})
		div.append(indent)
		var e = $("<span style='font-size:1.2em'></span>")
		e.text(ruleset_name)
		e.osvc_ruleset()
		div.append(e)

		for (i=0; i<ruleset["rulesets"].length; i++) {
			div.append(o.render_ruleset(ruleset["rulesets"][i], chain))
		}
		return div
	}

	o.render_moduleset = function(modset, chain) {
		var level = chain.length
		chain = [].concat(chain, [modset.modset_name])
		var sig = chain.join(",")
		var div = $("<div></div>")
		if (o.modulesets_done.indexOf(chain) >= 0) {
			console.log("loop detected:", sig)
			return div
		} else {
			o.modulesets_done.push(sig)
		}
		var indent = $("<span></span>")
		indent.css({"width": 2*level+"em", "display": "inline-block"})
		div.append(indent)
		var e = $("<span style='font-size:1.2em'></span>")
		e.text(modset.modset_name)
		e.osvc_moduleset()
		div.append(e)

		level += 1

		for (var j=0; j<modset.modules.length; j++) {
			var module = modset.modules[j]
			div.append("<br>")
			var indent = $("<span></span>")
			indent.css({"width": 2*level+"em", "display": "inline-block"})
			div.append(indent)
			var e = $("<span style='font-size:1.2em'></span>")
			var text = module.modset_mod_name
			if (module.autofix) {
				text += " ("+i18n.t("designer.autofix")+")"
			}
			e.text(text)
			e.osvc_module()
			div.append(e)
		}
		for (var j=0; j<modset.rulesets.length; j++) {
			div.append(o.render_ruleset(modset.rulesets[j], chain))
		}
		for (var i=0; i<modset.modulesets.length; i++) {
			div.append(o.render_moduleset(o.modulesets[modset.modulesets[i]], chain))
		}
		return div
	}

	o.render = function(modset) {
		o.area.append(o.render_moduleset(modset, []))
	}
}


function modset_export(divid, options) {
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
                        "type": "moduleset",
                        "id": o.options.modset_id,
                        "name": o.options.modset_name
		}
	}

	o.init = function() {
		o.load_export()
	}

	o.resize = function() {
		var max_height = max_child_height(o.div)
		o.textarea.outerHeight(max_height)
	}

	o.load_export = function() {
		o.div.empty()
		spinner_add(o.div)
		services_osvcgetrest("/compliance/modulesets", "", {"filters": ["modset_name "+o.options.modset_name]}, function(jd) {
			services_osvcgetrest("/compliance/modulesets/%1/export", [jd.data[0].id], "", function(jd) {
				o._load_export(jd)
			})
		})
	}

	o._load_export = function(data) {
		o.textarea = $("<textarea class='export_data'>")
		o.textarea.prop("disabled", true)
		o.div.css({"padding": "4px"})
		o.div.html(o.textarea)
		o.textarea.text(JSON.stringify(data, null, 4))
		o.resize()
		osvc_tools(o.div, {
			"resize": o.resize,
			"link": o.link
		})
	}

	o.init()

	return o
}

