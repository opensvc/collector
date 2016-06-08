//
// service
//
function service_tabs(divid, options) {
	var o = tabs(divid)
	o.options = options
	o.options.bgcolor = osvc.colors.svc

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

		// tab env
		i = o.register_tab({
			"title": "service_tabs.env",
			"title_class": "icon file16"
		})
		o.tabs[i].callback = function(divid) {
			service_env(divid, {"svc_id": o.options.svc_id})
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
			sync_ajax("/init/ajax_node/ajax_svc_stor/"+divid.replace("-", "_")+"/"+encodeURIComponent(o.options.svc_id), [], divid, function(){})
		}

		// tab stats
		i = o.register_tab({
			"title": "service_tabs.container_stats",
			"title_class": "icon spark16"
		})
		o.tabs[i].callback = function(divid) {
			services_osvcgetrest("R_SERVICE_NODES", [o.options.svc_id], {"limit": "0", "props": "node_id,mon_vmname", "meta": "0"}, function(jd) {
				if (jd.error) {
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
				sync_ajax("/init/stats/ajax_containerperf_plot?node="+encodeURIComponent(nodes), [], divid, function(){})
			},
			function(xhr, stat, error) {
				$("#"+divid).html(services_ajax_error_fmt(xhr, stat, error))
			})
		}

		// tab stats
		i = o.register_tab({
			"title": "service_tabs.stats",
			"title_class": "icon spark16"
		})
		o.tabs[i].callback = function(divid) {
			services_osvcgetrest("R_SERVICE_NODES", [o.options.svc_id], {"limit": "0", "props": "node_id", "meta": "0"}, function(jd) {
				if (jd.error) {
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

		// tab compliance
		i = o.register_tab({
			"title": "service_tabs.compliance",
			"title_class": "icon comp16"
		})
		o.tabs[i].callback = function(divid) {
			sync_ajax("/init/compliance/ajax_compliance_svc/"+encodeURIComponent(o.options.svc_id), [], divid, function(){})
		}

		o.set_tab(o.options.tab)
	})
	return o
}


function service_env(divid, options)
{
	var o = {}

	// store parameters
	o.options = options

	o.div = $("#"+divid)

	o.init = function() {
		o.div.load('/init/static/views/service_env.html?v='+osvc.code_rev, function() {
			o._init()
		})
	}

	o._init = function() {
		o.header = o.div.find("p")
		o.body = o.div.find("code")

		spinner_add(o.div)
		services_osvcgetrest("R_SERVICE", [o.options.svc_id], {"meta": "false", "props": "updated,svc_envfile"}, function(jd) {
			spinner_del(o.div)
			if (!jd.data) {
				o.div.html(services_error_fmt(jd))
			}
			var data = jd.data[0]
			o.header.text(i18n.t("service_env.header", {"updated": data.updated}))
			o.load(data)
		},
		function() {
			o.div.html(services_ajax_error_fmt(xhr, stat, error))
		})
	}

	o.load = function(data) {
		if (data.svc_envfile && (data.svc_envfile.length > 0)) {
			var text = data.svc_envfile.replace(/\\n\[/g, "\n\n[").replace(/\\n/g, "\n").replace(/\\t/g, "\t")
		} else {
			var text = ""
		}
		o.editor = osvc_editor(o.body, {
			"text": text,
			"mode": "ini",
			"obj_type": "services",
			"obj_id": o.options.svc_id,
			"save": o.save
		})
	}

	o.save = function(text) {
		var data = { 
			"svc_envfile": text
		}
		services_osvcpostrest("/services/%1", [o.options.svc_id], "", data, function(jd) {
			if (jd.error && (jd.error.length > 0)) {
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

	o.init = function(){
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


