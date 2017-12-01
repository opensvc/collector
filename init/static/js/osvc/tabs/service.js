//
// service
//
function service_tabs(divid, options) {
	var o = tabs(divid)
	o.options = options
	o.options.bgcolor = osvc.colors.svc
	o.link = {
		"fn": arguments.callee.name,
		"title": "format_title",
		"title_args": {
			"type": "service",
			"id": o.options.svc_id
		}
	}

	o.load(function(){
		var i = 0
		var e_title = $("<span svc_id="+o.options.svc_id+"></span>")
		o.closetab.append(e_title)
		e_title.osvc_svcname()

		// tab properties
		i = o.register_tab({
			"title": "node_tabs.properties",
			"title_class": "icon svc"
		})
		o.tabs[i].callback = function(divid) {
			service_properties(divid, {"svc_id": o.options.svc_id})
		}

		// tab alerts
		i = o.register_tab({
			"title": "node_tabs.alerts",
			"title_class": "icon alert16"
		})
		o.tabs[i].callback = function(divid) {
			table_dashboard_svc(divid, o.options.svc_id)
		}

		// tab status
		i = o.register_tab({
			"title": "service_tabs.status",
			"title_class": "icon svc"
		})
		o.tabs[i].callback = function(divid) {
			table_service_instances_svc(divid, o.options.svc_id)
		}

		// tab resources
		i = o.register_tab({
			"title": "service_tabs.resources",
			"title_class": "icon resource"
		})
		o.tabs[i].callback = function(divid) {
			table_resources_svc(divid, o.options.svc_id)
		}

		// tab resources info
		i = o.register_tab({
			"title": "service_tabs.resinfo",
			"title_class": "icon resource"
		})
		o.tabs[i].callback = function(divid) {
			table_resinfo_svc(divid, o.options.svc_id)
		}

		// tab actions
		i = o.register_tab({
			"title": "service_tabs.actions",
			"title_class": "icon action16"
		})
		o.tabs[i].callback = function(divid) {
			table_actions_svc(divid, o.options.svc_id)
		}

		// tab log
		i = o.register_tab({
			"title": "service_tabs.log",
			"title_class": "icon log16"
		})
		o.tabs[i].callback = function(divid) {
			table_log_svc(divid, o.options.svc_id)
		}

		// tab config
		i = o.register_tab({
			"title": "service_tabs.config",
			"title_class": "icon file16"
		})
		o.tabs[i].callback = function(divid) {
			service_config(divid, {"svc_id": o.options.svc_id})
		}

		// tab topology
		i = o.register_tab({
			"title": "service_tabs.topology",
			"title_class": "icon dia16"
		})
		o.tabs[i].callback = function(divid) {
			topology(divid, {
				"svc_ids": [
					o.options.svc_id
				],
				"display": [
					"nodes",
					"services",
					"countries",
					"cities",
					"buildings",
					"rooms",
					"racks",
					"enclosures",
					"hvs",
					"hvpools",
					"hvvdcs",
					"disks"]
			})
		}

		// tab startup
		i = o.register_tab({
			"title": "service_tabs.startup",
			"title_class": "icon startup"
		})
		o.tabs[i].callback = function(divid) {
			startup(divid, {"svc_ids": [o.options.svc_id]})
		}

		// tab storage
		i = o.register_tab({
			"title": "service_tabs.storage",
			"title_class": "icon hd16"
		})
		o.tabs[i].callback = function(divid) {
			sync_ajax("/init/ajax_node/ajax_svc_stor/"+divid.replace("-", "_")+"/"+encodeURIComponent(o.options.svc_id), [], divid, function(){
				osvc_tools($("#"+divid), {
					"link": {
						"fn": "/init/ajax_node/ajax_svc_stor",
						"parameters": divid.replace("-", "_")+"/"+encodeURIComponent(o.options.svc_id),
						"title": "format_title",
						"title_args": {
							"fn": "service_storage",
							"id": o.options.svc_id,
							"type": "service"
						}
					}
				})
			})
		}

		// tab stats
		i = o.register_tab({
			"title": "service_tabs.container_stats",
			"title_class": "icon chart16"
		})
		o.tabs[i].callback = function(divid) {
			services_osvcgetrest("R_SERVICE_NODES", [o.options.svc_id], {"filters": ["mon_vmname !empty"], "limit": "0", "props": "node_id,mon_vmname", "meta": "0"}, function(jd) {
				if (rest_error(jd)) {
					$("#"+divid).html(services_error_fmt(jd))
					return
				}
				var nodes = []
				for (i=0; i<jd.data.length; i++) {
					d = jd.data[i]
					if ((d.node_id != "") && (d.mon_vmname != "")) {
						nodes.push(d.mon_vmname+"@"+d.node_id)
					}
				}
				sync_ajax("/init/stats/ajax_containerperf_plot?node="+encodeURIComponent(nodes), [], divid, function(){
					osvc_tools($("#"+divid), {
						"link": {
							"fn": "/init/stats/ajax_containerperf_plot",
							"parameters": "nodes="+encodeURIComponent(nodes),
							"title": "format_title",
							"title_args": {
								"fn": "service_containerperf",
								"id": o.options.svc_id,
								"type": "service"
							}
						}
					})
				})
			},
			function(xhr, stat, error) {
				$("#"+divid).html(services_ajax_error_fmt(xhr, stat, error))
			})
		}

		// tab stats
		i = o.register_tab({
			"title": "service_tabs.stats",
			"title_class": "icon chart16"
		})
		o.tabs[i].callback = function(divid) {
			services_osvcgetrest("R_SERVICE_NODES", [o.options.svc_id], {"limit": "0", "props": "node_id", "meta": "0"}, function(jd) {
				if (rest_error(jd)) {
					$("#"+divid).html(services_error_fmt(jd))
					return
				}
				var nodenames = []
				for (i=0; i<jd.data.length; i++) {
					nodenames.push(jd.data[i].node_id)
				}
				node_stats(divid, {
					"node_id": nodenames.join(","), 
					"view": "/init/static/views/nodes_stats.html",
					"controller": "/init/stats"
				})
			},
			function(xhr, stat, error) {
				$("#"+divid).html(services_ajax_error_fmt(xhr, stat, error))
			})
		}

		// tab wiki
		i = o.register_tab({
			"title": "node_tabs.wiki",
			"title_class": "icon edit"
		})
		o.tabs[i].callback = function(divid) {
			wiki(divid, {"nodes": o.options.svc_id})
		}

		// tab avail
		i = o.register_tab({
			"title": "service_tabs.avail",
			"title_class": "icon avail16"
		})
		o.tabs[i].callback = function(divid) {
			services_status_log(divid, {"services": [o.options.svc_id], "instances": true})
		}

		// tab pkgdiff
		i = o.register_tab({
			"title": "service_tabs.pkgdiff",
			"title_class": "icon pkg16"
		})
		o.tabs[i].callback = function(divid) {
			svc_pkgdiff(divid, {"svc_ids": o.options.svc_id})
		}

		// tab nodediff
		i = o.register_tab({
			"title": "action_menu.node_diff",
			"title_class": "icon common16"
		})
		o.tabs[i].callback = function(divid) {
			svc_nodediff(divid, {"svc_id": o.options.svc_id})
		}

		// tab sysrepdiff
		i = o.register_tab({
			"title": "action_menu.node_sysrep_diff",
			"title_class": "icon common16"
		})
		o.tabs[i].callback = function(divid) {
			svc_sysrepdiff(divid, {"svc_id": o.options.svc_id})
		}

		// tab compliance
		i = o.register_tab({
			"title": "service_tabs.compliance",
			"title_class": "icon comp16"
		})
		o.tabs[i].callback = function(divid) {
			service_compliance(divid, options)
		}

		o.set_tab(o.options.tab)
	})
	return o
}


function service_config(divid, options)
{
	var o = {}

	// store parameters
	o.options = options

	o.div = $("#"+divid)
	o.link = {
		"fn": arguments.callee.name,
		"parameters": o.options,
		"title": "format_title",
		"title_args": {
			"type": "service",
			"id": o.options.svc_id
		}
	}

	o.init = function() {
		o.div.load('/init/static/views/service_config.html?v='+osvc.code_rev, function() {
			o._init()
		})
	}

	o.resize = function() {
		var div = o.body.children().first()
		var button = o.body.find("button")
		var max_height = max_child_height(o.div)
			- o.body.css("padding-top").replace(/px/,"")
			- o.body.css("padding-bottom").replace(/px/,"")
			- o.header.outerHeight()
		if (button.length > 0) {
			max_height = max_height
				 - button.height()
				 - button.css("margin-top").replace(/px/,"")
				 - button.css("margin-bottom").replace(/px/,"")
		}
		div.outerHeight(max_height)
		o.editor.editor.resize()
	}

	o._init = function() {
		osvc_tools(o.div, {
			"resize": o.resize,
			"link": o.link
		})
		o.header = o.div.find("p")
		o.body = o.div.find("[name=content]")

		spinner_add(o.div)
		services_osvcgetrest("R_SERVICE", [o.options.svc_id], {"meta": "false", "props": "updated,svc_config"}, function(jd) {
			spinner_del(o.div)
			if (!jd.data) {
				o.div.html(services_error_fmt(jd))
			}
			var data = jd.data[0]
			o.header.text(i18n.t("service_config.header", {"updated": data.updated}))
			o.load(data)
		},
		function() {
			o.div.html(services_ajax_error_fmt(xhr, stat, error))
		})
	}

	o.load = function(data) {
		if (data.svc_config && (data.svc_config.length > 0)) {
			var text = data.svc_config.replace(/\\n\[/g, "\n\n[").replace(/\\n/g, "\n").replace(/\\t/g, "\t")
		} else {
			var text = ""
		}
		o.editor = osvc_editor(o.body, {
			"text": text,
			"mode": "ini",
			"obj_type": "services",
			"obj_id": o.options.svc_id,
			"save": o.save,
			"callback": o.resize
		})
	}

	o.save = function(text) {
		var data = { 
			"svc_config": text
		}
		services_osvcpostrest("/services/%1", [o.options.svc_id], "", data, function(jd) {
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


function service_properties(divid, options)
{
	var o = {}

	// store parameters
	o.options = options

	o.div = $("#"+divid)
	o.link = {
		"fn": arguments.callee.name,
		"parameters": o.options,
		"title": "format_title",
		"title_args": {
			"type": "service",
			"id": o.options.svc_id
		}
	}

	o.init = function(){
		osvc_tools(o.div, {
			"link": o.link
		})
		o.div.i18n();
		o.e_tags = o.div.find(".tags")
		o.e_tags.uniqueId()


		// unack errors
		o.unack_errs = o.div.find("#err")
		spinner_add(o.unack_errs)
		services_osvcgetrest("R_SERVICE_ACTIONS_UNACKNOWLEDGED_ERRORS", [o.options.svc_id], {"meta": "true", "limit": "1"}, function(jd) {
			spinner_del(o.unack_errs)
			if (!jd.meta) {
				o.unack_errs.html(services_error_fmt(jd))
			}
			o.unack_errs.html(jd.meta.total)
			if (jd.meta.total > 0) {
				o.unack_errs.addClass("highlight")
			}
		})

		services_osvcgetrest("R_SERVICE", [o.options.svc_id], {"meta": "false"}, function(jd) {
			if (!jd.data) {
				o.div.html(services_error_fmt(jd))
			}
			var data = jd.data[0];
			var key;
			for (key in data) {
				if (!(key in data)) {
					continue
				}
				o.div.find("#"+key).text(data[key])
			}

			// HA formatter
			if (data.svc_ha) {
				o.div.find("#svc_ha").text(i18n.t("service_properties.yes"))
			} else {
				o.div.find("#svc_ha").text(i18n.t("service_properties.no"))
			}
			o.div.find("#svc_created").text(osvc_date_from_collector(data.svc_created))
			o.div.find("#updated").text(osvc_date_from_collector(data.updated))

			// tools
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
									"fn": "data_action_delete_svcs"
								}
							]
						}
					]
				}
			]
			tab_tools({
				"div": o.div.find("#tools"),
				"data": {"svc_id": data.svc_id},
				"am_data": am_data
			})

			// status
			o.decorator_status(o.div.find("#svc_status"), data.svc_status_updated)
			o.decorator_status(o.div.find("#svc_availstatus"), data.svc_status_updated)

			// responsibles
			o.responsibles = o.div.find("#responsibles")
			o.responsibles_title = o.div.find("#responsibles_title")
			tab_properties_generic_list({
				"request_service": "R_APP_RESPONSIBLES",
				"request_parameters": function(){return [o.div.find("#svc_app").text()]},
				"limit": "0",
				"key": "role",
				"item_class": "icon guys16",
				"id": "id",
				"flash_id_prefix": "group",
				"bgcolor": osvc.colors.org,
				"depends": ["svc_app"],
				"e_title": o.responsibles_title,
				"e_list": o.responsibles,
				"ondblclick": function(divid, data) {
					group_tabs(divid, {"group_id": data.id, "group_name": data.name})
				}

			})

			tab_properties_generic_updater({
				"div": o.div,
				"post": function(data, callback, error_callback) {
					services_osvcpostrest("R_SERVICE", [o.options.svc_id], "", data, callback, error_callback)
				}
			})
		},
		function() {
			o.div.html(services_ajax_error_fmt(xhr, stat, error))
		})

		// init tags
		service_tags({
			"bgcolor": osvc.colors.tag,
			"tid": o.e_tags.attr("id"),
			"svc_id": o.options.svc_id,
		})
	}

	o.decorator_status = function(e, updated) {
		var v = e.text()
		if ((v=="") || (v=="empty")) {
			v = "undef"
		}
		var c = v
		if (_outdated(updated, 15)) {
			c = "undef"
		}
		t = {
			"warn": "orange",
			"up": "green",
			"stdby up": "green",
			"down": "red",
			"stdby down": "red",
			"undef": "gray",
			"n/a": "gray",
		}
		e.html("<div class='status_icon icon nowrap icon-"+t[c]+"'>"+v+"</div>")
	}

	o.div.load('/init/static/views/service_properties.html?v='+osvc.code_rev, function() {
		o.div = o.div.children()
		o.div.uniqueId()
		o.init()
	})
	return o
}

function service_compliance(divid, options) {
        var o = {}
        o.options = options
        o.link = {
                "fn": arguments.callee.name,
                "parameters": o.options,
                "title": "format_title",
                "title_args": {
                        "type": "service",
                        "id": o.options.svc_id
                }
        }

        // store parameters
        o.divid = divid
        o.div = $("#"+divid)

        o.init = function() {
                osvc_tools(o.div, {
                        "link": o.link
                })

                o.e_status = o.div.find("[name=status]")
                o.e_status.uniqueId()
                table_comp_status_svc(o.e_status.attr("id"), o.options.svc_id)

                service_modulesets({
                        "tid": o.div.find("#modulesets"),
                        "svc_id": o.options.svc_id,
                        "title": "node_compliance.modulesets",
                        "e_title": o.div.find("#modulesets_title")
                })

                service_rulesets({
                        "tid": o.div.find("#rulesets"),
                        "svc_id": o.options.svc_id,
                        "title": "node_compliance.rulesets",
                        "e_title": o.div.find("#rulesets_title")
                })

		services_osvcgetrest("/services/%1/resinfo", [o.options.svc_id], {
			"limit": "1",
			"meta": "0",
			"filters": ["res_key tags", "res_value %encap%"]
		}, function(jd) {
			if (jd.data.length == 0) {
				return
			}

			o.div.find("#encap_modulesets").show()
			service_modulesets({
				"tid": o.div.find("#encap_modulesets"),
				"svc_id": o.options.svc_id,
				"slave": true,
				"title": "service_compliance.encap_modulesets",
				"e_title": o.div.find("#encap_modulesets_title")
			})

			o.div.find("#encap_rulesets").show()
			service_rulesets({
				"tid": o.div.find("#encap_rulesets"),
				"svc_id": o.options.svc_id,
				"slave": true,
				"title": "service_compliance.encap_rulesets",
				"e_title": o.div.find("#encap_rulesets_title")
			})
		})

                o.e_svcdiff = o.div.find("[name=svcdiff]")
                o.e_svcdiff.uniqueId()
		sync_ajax('/init/compliance/ajax_compliance_svcdiff?node='+o.options.svc_id, [], o.e_svcdiff.attr("id"), function(){})
        }

        o.div.load('/init/static/views/service_compliance.html?v='+osvc.code_rev, function() {
                o.div.i18n()
                o.init()
        })
}

function svc_nodediff(divid, options) {
	var o = {}
	o.div = $("#"+divid)
	o.options = options
	o.link = {
		"fn": arguments.callee.name,
		"parameters": o.options,
		"title": "link."+arguments.callee.name
	}

	var t
	var d

	o.div.empty()
	o.div.addClass("p-3")
	services_osvcgetrest("R_SERVICE_NODES", [o.options.svc_id], {"limit": "0", "props": "node_id", "meta": "0", "groupby": "node_id"}, function(jd) {
		if (rest_error(jd)) {
			$("#"+divid).html(services_error_fmt(jd))
			return
		}
		var nodes = []
		for (i=0; i<jd.data.length; i++) {
			d = jd.data[i]
			if (d.node_id != "") {
				nodes.push(d.node_id)
			}
		}
		nodediff(divid, {"node_ids": nodes})
	})
	osvc_tools(o.div, {
		"link": o.link
	})

	o.div.i18n()
	return o
}

function svc_sysrepdiff(divid, options) {
	var o = {}
	o.div = $("#"+divid)
	o.options = options
	o.link = {
		"fn": arguments.callee.name,
		"parameters": o.options,
		"title": "link."+arguments.callee.name
	}

	var t
	var d

	o.div.empty()
	o.div.addClass("p-3")
	services_osvcgetrest("R_SERVICE_NODES", [o.options.svc_id], {"limit": "0", "props": "node_id", "meta": "0", "groupby": "node_id"}, function(jd) {
		if (rest_error(jd)) {
			$("#"+divid).html(services_error_fmt(jd))
			return
		}
		var nodes = []
		for (i=0; i<jd.data.length; i++) {
			d = jd.data[i]
			if (d.node_id != "") {
				nodes.push(d.node_id)
			}
		}
		sysrepdiff(divid, {"nodes": nodes})
	})
	osvc_tools(o.div, {
		"link": o.link
	})

	o.div.i18n()
	return o
}

