//
// service
//
function service_tabs(divid, options) {
	var o = tabs(divid)
	o.options = options
	o.load(function(){
		var i = 0

		o.closetab.children("p").text(o.options.svcname)

		// tab properties
		i = o.register_tab({
			"title": "node_tabs.properties",
			"title_class": "svc"
		})
		o.tabs[i].callback = function(divid) {
			service_properties(divid, {"svcname": o.options.svcname})
		}

		// tab alerts
		i = o.register_tab({
		"title": "node_tabs.alerts",
		"title_class": "alert16"
		})
		o.tabs[i].callback = function(divid) {
			table_dashboard_svc(divid, o.options.svcname)
		}

		// tab status
		i = o.register_tab({
		"title": "service_tabs.status",
		"title_class": "svc"
		})
		o.tabs[i].callback = function(divid) {
			table_service_instances_svc(divid, o.options.svcname)
		}

		// tab resources
		i = o.register_tab({
		"title": "service_tabs.resources",
		"title_class": "svc"
		})
		o.tabs[i].callback = function(divid) {
			table_resources_svc(divid, o.options.svcname)
		}

		// tab actions
		i = o.register_tab({
		"title": "service_tabs.actions",
		"title_class": "action16"
		})
		o.tabs[i].callback = function(divid) {
			table_actions_svc(divid, o.options.svcname)
		}

		// tab log
		i = o.register_tab({
		"title": "service_tabs.log",
		"title_class": "log16"
		})
		o.tabs[i].callback = function(divid) {
			table_log_svc(divid, o.options.svcname)
		}

		// tab env
		i = o.register_tab({
		"title": "service_tabs.env",
		"title_class": "file16"
		})
		o.tabs[i].callback = function(divid) {
			service_env(divid, {"svcname": o.options.svcname})
		}

		// tab topology
		i = o.register_tab({
		"title": "service_tabs.topology",
		"title_class": "dia16"
		})
		o.tabs[i].callback = function(divid) {
			topology(divid, {
				"svcnames": [
					o.options.svcname
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
			"title_class": "startup"
		})
		o.tabs[i].callback = function(divid) {
			startup(divid, {"svcnames": [o.options.svcname]})
		}

		// tab storage
		i = o.register_tab({
			"title": "service_tabs.storage",
			"title_class": "hd16"
		})
		o.tabs[i].callback = function(divid) {
			sync_ajax("/init/ajax_node/ajax_svc_stor/"+divid.replace("-", "_")+"/"+encodeURIComponent(o.options.svcname), [], divid, function(){})
		}

		// tab stats
		i = o.register_tab({
			"title": "service_tabs.container_stats",
			"title_class": "spark16"
		})
		o.tabs[i].callback = function(divid) {
			services_osvcgetrest("R_SERVICE_NODES", [o.options.svcname], {"limit": "0", "props": "mon_nodname,mon_vmname", "meta": "0"}, function(jd) {
				if (jd.error) {
					$("#"+divid).html(services_error_fmt(jd))
					return
				}
				var nodes = []
				for (i=0; i<jd.data.length; i++) {
					d = jd.data[i]
					if (d.mon_vmname && (d.mon_vmname != "")) {
						nodes.push(d.mon_vmname+"@"+d.mon_nodname)
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
			"title_class": "spark16"
		})
		o.tabs[i].callback = function(divid) {
			services_osvcgetrest("R_SERVICE_NODES", [o.options.svcname], {"limit": "0", "props": "mon_nodname", "meta": "0"}, function(jd) {
				if (jd.error) {
					$("#"+divid).html(services_error_fmt(jd))
					return
				}
				var nodenames = []
				for (i=0; i<jd.data.length; i++) {
					nodenames.push(jd.data[i].mon_nodname)
				}
				node_stats(divid, {
					"nodename": nodenames.join(","), 
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
			"title_class": "edit"
		})
		o.tabs[i].callback = function(divid) {
			wiki(divid, {"nodes": o.options.svcname})
		}

		// tab avail
		i = o.register_tab({
			"title": "service_tabs.avail",
			"title_class": "svc"
		})
		o.tabs[i].callback = function(divid) {
			sync_ajax("/init/svcmon_log/ajax_svcmon_log_1?svcname="+encodeURIComponent(o.options.svcname), [], divid, function(){})
		}

		// tab pkgdiff
		i = o.register_tab({
			"title": "service_tabs.pkgdiff",
			"title_class": "pkg16"
		})
		o.tabs[i].callback = function(divid) {
			svc_pkgdiff(divid, {"svcnames": o.options.svcname})
		}

		// tab compliance
		i = o.register_tab({
			"title": "service_tabs.compliance",
			"title_class": "comp16"
		})
		o.tabs[i].callback = function(divid) {
			sync_ajax("/init/compliance/ajax_compliance_svc/"+encodeURIComponent(o.options.svcname), [], divid, function(){})
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

	o.div.load('/init/static/views/service_env.html', "", function() {
		o.init()
	})

	o.init = function(o) {
		o.header = o.div.find("p")
		o.body = o.div.find("code")

		spinner_add(o.div)
		services_osvcgetrest("R_SERVICE", [o.options.svcname], {"meta": "false", "props": "updated,svc_envfile"}, function(jd) {
			spinner_del(o.div)
			if (!jd.data) {
				o.div.html(services_error_fmt(jd))
			}
			var data = jd.data[0]
			o.header.text(i18n.t("service_env.header", {"updated": data.updated}))
			text = data.svc_envfile.replace(/\\n\[/g, "\n\n[").replace(/\\n/g, "\n").replace(/\\t/g, "\t")
			o.body.html(text)
			hljs.highlightBlock(o.body[0])
			o.body.find(".hljs-setting").css({"color": "green"}).children().css({"color": "initial"})
		},
		function() {
			o.div.html(services_ajax_error_fmt(xhr, stat, error))
		})
	}

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
		services_osvcgetrest("R_SERVICE_ACTIONS_UNACKNOWLEDGED_ERRORS", [o.options.svcname], {"meta": "true", "limit": "1"}, function(jd) {
			spinner_del(o.unack_errs)
			if (!jd.meta) {
				o.unack_errs.html(services_error_fmt(jd))
			}
			o.unack_errs.html(jd.meta.total)
			if (jd.meta.total > 0) {
				o.unack_errs.addClass("highlight")
			}
		})

		services_osvcgetrest("R_SERVICE", [o.options.svcname], {"meta": "false"}, function(jd) {
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
				"item_class": "guys16",
				"depends": ["svc_app"],
				"e_title": o.responsibles_title,
				"e_list": o.responsibles
			})

			tab_properties_generic_updater({
				"div": o.div,
				"post": function(data, callback, error_callback) {
					services_osvcpostrest("R_SERVICE", [o.options.svcname], "", data, callback, error_callback)
				}
			})
		},
		function() {
			o.div.html(services_ajax_error_fmt(xhr, stat, error))
		})

		// init tags
		tags({
			"tid": o.e_tags.attr("id"),
			"svcname": o.options.svcname,
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
		e.html("<div class='status_icon nowrap icon-"+t[c]+"'>"+v+"</div>")
	}

	o.div.load('/init/static/views/service_properties.html', "", function() {
		o.div = o.div.children()
		o.div.uniqueId()
		o.init()
	})
	return o
}


