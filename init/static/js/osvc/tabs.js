//
// tabs
//

// old tabs support function.
// remove me when fset and modset tabs are ported to js
function bind_tabs(id, callbacks, active_id) {
  $("#"+id).find('.closetab').click(function () {
    $("#"+id).parent().remove(); // Remove extraline
    $("#"+id).remove();
  })
  $("#"+id).find('[id^=litab]').click(function () {
    var _id = $(this).attr('id')
    var did = _id.slice(2, _id.length)
    $("#"+id).find('div[id^=tab]').hide()
    $(this).siblings('[id^=litab]').removeClass('tab_active')
    $("#"+id).find('#'+did).show()
    $(this).show().addClass('tab_active')
    if (_id in callbacks) {
      callbacks[_id]()
      delete callbacks[_id]
    }
  })
  $("#"+id).find('#'+active_id).trigger("click")
}

//
// base tabs object
// derive to make object-specific tabs
//
function tabs(divid) {
	var o = {}
	o.divid = divid
	o.div = $("#"+divid)

	o.tabs = []

	o.load = function(callback) {
		o.div.load('/init/static/views/tabs.html', "", function() {
			o.init()
			callback(o)
		})
	}

	o.init = function() {
		o.closetab = o.div.find(".closetab")
		o.tabs_ul = o.closetab.parent()
		o.display = o.div.find(".tab_display")

		// empty tabs on click closetab
		o.closetab.bind("click", function() {
			o.div.parent().remove(); // Remove extraline
			o.div.remove();
		})
	}

	o.register_tab = function(data) {
		// allocate a div to store tab information
		e = $("<div></div>")
		e.addClass("hidden")
		e.css({"width": "100%"})
		e.uniqueId()
		o.display.append(e)
		data.divid = e.attr("id")
		data.div = e

		var index = o.tabs.length
		o.tabs.push(data)

		o.add_tab(index)

		return index
	}

	o.add_tab = function(index) {
		var data = o.tabs[index]
		var e = $("<li></li>")
		var p = $("<p></p>")
		p.addClass(data.title_class)
		p.text(i18n.t(data.title))
		e.append(p)
		o.tabs_ul.append(e)
		data.tab = e

		e.bind("click", function() {
			for (var i=0; i<o.tabs.length; i++) {
				o.tabs[i].tab.removeClass("tab_active")
				o.tabs[i].div.hide()
			}
			data.tab.addClass("tab_active")
			data.div.show()
			if (!data.div.is(":empty")) {
				return
			}
			data.callback(data.divid)
		})
	}

	o.set_tab = function(tab_title) {
		if (!tab_title) {
			// set the first tab active
			o.closetab.next("li").trigger("click")
			return
		}
		for (var i=0; i<o.tabs.length; i++) {
			if (o.tabs[i].title != tab_title) {
				continue
			}
			// found the tab, set active and stop iterating
			o.tabs[i].tab.trigger("click")
			return
		}
	}


	return o
}

tab_properties_generic_updater = function(options) {
	options.div.find("[upd]").each(function(){
		$(this).addClass("clickable")
		$(this).hover(
			function() {
				$(this).addClass("editable")
			},
			function() {
				$(this).removeClass("editable")
			}
		)
		$(this).bind("click", function() {
			//$(this).unbind("mouseenter mouseleave click")
			if ($(this).siblings().find("form").length > 0) {
				$(this).siblings().show()
				$(this).siblings().find("input[type=text]:visible,select").focus()
				$(this).hide()
				return
			}
			var updater = $(this).attr("upd")
			if ((updater == "string") || (updater == "text") || (updater == "integer") || (updater == "date") || (updater == "datetime")) {
				if (updater == "text") {
					var e = $("<td><form><textarea class='oi'></textarea></form></td>")
					var button = $("<input type='submit'>")
					e.find("form").append("<br>").append(button)
					button.attr("value", i18n.t("prov_template_properties.save"))
				} else {
					var e = $("<td><form><input class='oi' type='text'></input></form></td>")
				}
				e.css({"padding-left": "0px"})
				var input = e.find("input,textarea")
				input.uniqueId() // for date picker
				input.attr("pid", $(this).attr("id"))
				input.attr("value", $(this).text())
				input.bind("blur", function(){
					$(this).parents("td").first().siblings("td").show()
					$(this).parents("td").first().hide()
				})
				$(this).parent().append(e)
				$(this).hide()
				input.focus()
				e.find("form").submit(function(event) {
					event.preventDefault()
					var input = $(this).find("textarea,input[type=text],select")
					input.blur()
					var data = {}
					data[input.attr("pid")] = input.val()
					options.post(data, function(jd) {
						if (jd.error && (jd.error.length > 0)) {
							$(".flash").show("blind").html(services_error_fmt(jd))
							return
						}
						e.hide()
						e.prev().text(input.val()).show()
					},
					function(xhr, stat, error) {
						$(".flash").show("blind").html(services_ajax_error_fmt(xhr, stat, error))
					})
				})
			}
		})
	})
}

//
// node
//
function node_tabs(divid, options) {
  o = tabs(divid)
  o.options = options
  o.load(function(){
    var i = 0

    // tab properties
    o.closetab.children("p").text(o.options.nodename)
    i = o.register_tab({
      "title": "node_tabs.properties",
      "title_class": "node16"
    })
    o.tabs[i].callback = function(divid) {
      node_properties(divid, {"nodename": o.options.nodename})
    }

    // tab alerts
    i = o.register_tab({
      "title": "node_tabs.alerts",
      "title_class": "alert16"
    })
    o.tabs[i].callback = function(divid) {
      table_dashboard_node(divid, o.options.nodename)
    }

    // tab services
    i = o.register_tab({
      "title": "node_tabs.services",
      "title_class": "svc"
    })
    o.tabs[i].callback = function(divid) {
      table_service_instances_node(divid, o.options.nodename)
    }

    // tab actions
    i = o.register_tab({
      "title": "node_tabs.actions",
      "title_class": "action16"
    })
    o.tabs[i].callback = function(divid) {
      table_actions_node(divid, o.options.nodename)
    }

    // tab log
    i = o.register_tab({
      "title": "node_tabs.log",
      "title_class": "log16"
    })
    o.tabs[i].callback = function(divid) {
      table_log_node(divid, o.options.nodename)
    }

    // tab topology
    i = o.register_tab({
      "title": "node_tabs.topology",
      "title_class": "dia16"
    })
    o.tabs[i].callback = function(divid) {
      topology(divid, {
        "nodenames": [
          o.options.nodename
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

    // tab storage
    i = o.register_tab({
      "title": "node_tabs.storage",
      "title_class": "hd16"
    })
    o.tabs[i].callback = function(divid) {
      sync_ajax("/init/ajax_node/ajax_node_stor/"+divid.replace("-", "_")+"/"+encodeURIComponent(o.options.nodename), [], divid, function(){})
    }

    // tab network
    i = o.register_tab({
      "title": "node_tabs.network",
      "title_class": "net16"
    })
    o.tabs[i].callback = function(divid) {
      ips(divid, {"nodes": o.options.nodename})
    }

    // tab stats
    i = o.register_tab({
      "title": "node_tabs.stats",
      "title_class": "spark16"
    })
    o.tabs[i].callback = function(divid) {
      node_stats(divid, {
        "nodename": o.options.nodename,
        "view": "/init/static/views/node_stats.html",
        "controller": "/init/ajax_perf"
      })
    }

    // tab wiki
    i = o.register_tab({
      "title": "node_tabs.wiki",
      "title_class": "edit"
    })
    o.tabs[i].callback = function(divid) {
      wiki(divid, {"nodes": o.options.nodename})
    }

    // tab checks
    i = o.register_tab({
      "title": "node_tabs.checks",
      "title_class": "check16"
    })
    o.tabs[i].callback = function(divid) {
      table_checks_node(divid, o.options.nodename)
    }

    // tab compliance
    i = o.register_tab({
      "title": "node_tabs.compliance",
      "title_class": "comp16"
    })
    o.tabs[i].callback = function(divid) {
      sync_ajax("/init/compliance/ajax_compliance_node/"+encodeURIComponent(o.options.nodename), [], divid, function(){})
    }

    // tab sysreport
    i = o.register_tab({
      "title": "node_tabs.sysreport",
      "title_class": "log16"
    })
    o.tabs[i].callback = function(divid) {
      sysrep(divid, {"nodes": o.options.nodename})
    }

    o.set_tab(o.options.tab)
  })
  return o
}

//
// service
//
function service_tabs(divid, options) {
  o = tabs(divid)
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

//
// user
//
function user_tabs(divid, options) {
  o = tabs(divid)
  o.options = options

  o.load(function(){
    var i = 0

    if (!("user_id" in o.options) && ("fullname" in o.options)) {
      services_osvcgetrest("R_SEARCH", "", {"substring": o.options.fullname}, function(jd) {
        var users = jd.data.users.data
        for (var i=0; i<users.length; i++) {
          var user = users[i]
          if (user.fullname == o.options.fullname) {
            o.options.user_id = user.id
            break
          }
        }
        o._load()
      })
    } else {
      o._load()
    }
  })

  o._load = function() {
    o.closetab.children("p").text(o.options.fullname ? o.options.fullname : o.options.user_id)

    // tab properties
    i = o.register_tab({
      "title": "node_tabs.properties",
      "title_class": "guy16"
    })
    o.tabs[i].callback = function(divid) {
      user_properties(divid, o.options)
    }
    i = o.register_tab({
      "title": "user_tabs.groups",
      "title_class": "guys16"
    })
    o.tabs[i].callback = function(divid) {
      user_groups(divid, o.options)
    }

    o.set_tab(o.options.tab)
  }
  return o
}


//
// group
//
function group_tabs(divid, options) {
  o = tabs(divid)
  o.options = options

  o.load(function(){
    var i = 0

    if (!("group_id" in o.options) && ("group_name" in o.options)) {
      services_osvcgetrest("R_GROUPS", "", {"filters": ["role "+o.options.group_name]}, function(jd) {
        var group = jd.data[0]
        o.options.group_id = group.id
        o._load()
      })
    } else {
      o._load()
    }
  })

  o._load = function() {
    o.closetab.children("p").text(o.options.group_name ? o.options.group_name : o.options.group_id)

    // tab properties
    i = o.register_tab({
      "title": "node_tabs.properties",
      "title_class": "guys16"
    })
    o.tabs[i].callback = function(divid) {
      group_properties(divid, o.options)
    }

    // tab hidden menu entries
    i = o.register_tab({
      "title": "group_tabs.hidden_menu_entries",
      "title_class": "menu16"
    })
    o.tabs[i].callback = function(divid) {
      group_hidden_menu_entries(divid, o.options)
    }

    o.set_tab(o.options.tab)
  }
  return o
}

//
// app
//
function app_tabs(divid, options) {
  o = tabs(divid)
  o.options = options

  o.load(function(){
    var i = 0

    if (!("app_id" in o.options) && ("app_name" in o.options)) {
      services_osvcgetrest("R_APPS", "", {"filters": ["app "+o.options.app_name]}, function(jd) {
        var app = jd.data[0]
        o.options.app_id = app.id
        o._load()
      })
    } else {
      o._load()
    }
  })

  o._load = function() {
    o.closetab.children("p").text(o.options.app_name ? o.options.app_name : o.options.app_id)

    // tab properties
    i = o.register_tab({
      "title": "node_tabs.properties",
      "title_class": "svc"
    })
    o.tabs[i].callback = function(divid) {
      app_properties(divid, o.options)
    }

    // tab quotas
    i = o.register_tab({
      "title": "array_tabs.quotas",
      "title_class": "quota16"
    })
    o.tabs[i].callback = function(divid) {
      table_quota_app(divid, o.options.app_name)
    }

    o.set_tab(o.options.tab)
  }
  return o
}


//
// network
//
function network_tabs(divid, options) {
  o = tabs(divid)
  o.options = options

  o.load(function() {
    o.closetab.children("p").text(o.options.network_id)

    // tab properties
    i = o.register_tab({
      "title": "node_tabs.properties",
      "title_class": "net16"
    })
    o.tabs[i].callback = function(divid) {
      network_properties(divid, o.options)
    }
    i = o.register_tab({
      "title": "network_tabs.segments",
      "title_class": "net16"
    })
    o.tabs[i].callback = function(divid) {
      sync_ajax("/init/networks/segments/"+o.options.network_id, [], divid, function(){})
    }

    o.set_tab(o.options.tab)
  })
  return o
}


//
// ruleset
//
function ruleset_tabs(divid, options) {
  o = tabs(divid)
  o.options = options

  o.load(function() {
    if (o.options.ruleset_name) {
      var title = o.options.ruleset_name
    } else {
      var title = o.options.ruleset_id
    }
    o.closetab.children("p").text(title)

    // tab properties
    i = o.register_tab({
      "title": "ruleset_tabs.ruleset",
      "title_class": "pkg16"
    })
    o.tabs[i].callback = function(divid) {
      ruleset_properties(divid, o.options)
    }
    i = o.register_tab({
      "title": "ruleset_tabs.export",
      "title_class": "log16"
    })
    o.tabs[i].callback = function(divid) {
      ruleset_export(divid, o.options)
    }

    o.set_tab(o.options.tab)
  })
  return o
}

//
// form
//
function form_tabs(divid, options) {
  o = tabs(divid)
  o.options = options

  o.load(function() {
    if (o.options.form_name) {
      var title = o.options.form_name
    } else {
      var title = o.options.form_id
    }
    o.closetab.children("p").text(title)

    // tab properties
    i = o.register_tab({
      "title": "form_tabs.properties",
      "title_class": "wf16"
    })
    o.tabs[i].callback = function(divid) {
      form_properties(divid, o.options)
    }

    // tab definition
    i = o.register_tab({
      "title": "form_tabs.definition",
      "title_class": "edit16"
    })
    o.tabs[i].callback = function(divid) {
      form_definition(divid, o.options)
    }

    // tab request
    i = o.register_tab({
      "title": "form_tabs.request",
      "title_class": "wf16"
    })
    o.tabs[i].callback = function(divid) {
      form(divid, options)
    }

    o.set_tab(o.options.tab)
  })
  return o
}

//
// dns records
//
function dns_record_tabs(divid, options) {
  o = tabs(divid)
  o.options = options

  o.load(function() {
    services_osvcgetrest("R_DNS_RECORD", [o.options.record_id], {"meta": "0"}, function(jd) {
      o.data = jd.data[0]
      o._load()
    })
  })

  o._load = function() {
    var title = o.data.name
    o.closetab.children("p").text(title)

    // tab properties
    i = o.register_tab({
      "title": "dns_record_tabs.properties",
      "title_class": "dns16"
    })
    o.tabs[i].callback = function(divid) {
      dns_record_properties(divid, o.options)
    }

    if ((typeof(o.data.type) === "string") && (o.data.type.length > 0) && (o.data.type[0] == "A")) {
      // tab alerts
      i = o.register_tab({
        "title": "dns_record_tabs.nodes",
        "title_class": "node16"
      })
      o.tabs[i].callback = function(divid) {
        table_nodenetworks_addr(divid, o.data.content)
      }
    }

    o.set_tab(o.options.tab)
  }

  return o
}

//
// dns domains
//
function dns_domain_tabs(divid, options) {
  o = tabs(divid)
  o.options = options

  o.load(function() {
    services_osvcgetrest("R_DNS_DOMAIN", [o.options.domain_id], {"meta": "0"}, function(jd) {
      o.data = jd.data[0]
      o._load()
    })
  })

  o._load = function() {
    var title = o.data.name
    o.closetab.children("p").text(title)

    // tab properties
    i = o.register_tab({
      "title": "dns_domain_tabs.properties",
      "title_class": "dns16"
    })
    o.tabs[i].callback = function(divid) {
      dns_domain_properties(divid, o.options)
    }

    // tab records
    i = o.register_tab({
      "title": "dns_domain_tabs.records",
      "title_class": "dns16"
    })
    o.tabs[i].callback = function(divid) {
      table_dns_records_domain_id(divid, o.options.domain_id)
    }

    o.set_tab(o.options.tab)
  }

  return o
}

//
// quotas
//
function quota_tabs(divid, options) {
  o = tabs(divid)
  o.options = options

  o.load(function() {
    var title = o.options.quota_id
    o.closetab.children("p").text(title)

    // tab properties
    i = o.register_tab({
      "title": "node_tabs.properties",
      "title_class": "quota16"
    })
    o.tabs[i].callback = function(divid) {
      quota_properties(divid, o.options)
    }

    // tab usage
    i = o.register_tab({
      "title": "node_tabs.stats",
      "title_class": "spark16"
    })
    o.tabs[i].callback = function(divid) {
      services_osvcgetrest("R_ARRAY_DISKGROUP_QUOTA", [0, 0, o.options.quota_id], {"meta": "0"}, function(jd) {
        $.ajax({
          "url": "/init/disks/ajax_app",
          "type": "POST",
          "success": function(msg) {$("#"+divid).html(msg)},
          "data": {"app_id": jd.data[0].app_id, "dg_id": jd.data[0].dg_id, "rowid": divid}
        })
      })
    }

    o.set_tab(o.options.tab)
  })

  return o
}

//
// array
//
function array_tabs(divid, options) {
  o = tabs(divid)
  o.options = options

  o.load(function() {
    services_osvcgetrest("R_ARRAY", [o.options.array_name], {"meta": "0"}, function(jd) {
      o.data = jd.data[0]
      o._load()
    })
  })

  o._load = function() {
    var title = o.data.array_name
    o.closetab.children("p").text(title)

    // tab properties
    i = o.register_tab({
      "title": "node_tabs.properties",
      "title_class": "hd16"
    })
    o.tabs[i].callback = function(divid) {
      array_properties(divid, {"array_id": o.data.id})
    }

    // tab quotas
    i = o.register_tab({
      "title": "array_tabs.quotas",
      "title_class": "quota16"
    })
    o.tabs[i].callback = function(divid) {
      table_quota_array(divid, o.data.array_name)
    }

    // tab usage
    i = o.register_tab({
      "title": "node_tabs.stats",
      "title_class": "spark16"
    })
    o.tabs[i].callback = function(divid) {
      $.ajax({
        "url": "/init/disks/ajax_array",
        "type": "POST",
        "success": function(msg) {$("#"+divid).html(msg)},
        "data": {"array": o.data.array_name, "rowid": divid}
      })
    }

    o.set_tab(o.options.tab)
  }

  return o
}


//
// disk group
//
function diskgroup_tabs(divid, options) {
  o = tabs(divid)
  o.options = options

  o.load(function() {
    services_osvcgetrest("R_ARRAY_DISKGROUP", [o.options.array_name, o.options.dg_name], {"meta": "0"}, function(jd) {
      o.data = jd.data[0]
      o._load()
    })
  })

  o._load = function() {
    var title = o.data.dg_name
    o.closetab.children("p").text(title)

    // tab properties
    i = o.register_tab({
      "title": "node_tabs.properties",
      "title_class": "hd16"
    })
    o.tabs[i].callback = function(divid) {
      diskgroup_properties(divid, {"dg_id": o.data.id})
    }

    // tab quotas
    i = o.register_tab({
      "title": "array_tabs.quotas",
      "title_class": "quota16"
    })
    o.tabs[i].callback = function(divid) {
      table_quota_array_dg(divid, o.options.array_name, o.options.dg_name)
    }

    // tab usage
    i = o.register_tab({
      "title": "node_tabs.stats",
      "title_class": "spark16"
    })
    o.tabs[i].callback = function(divid) {
      $.ajax({
        "url": "/init/disks/ajax_array_dg",
        "type": "POST",
        "success": function(msg) {$("#"+divid).html(msg)},
        "data": {"array": o.options.array_name, "dg": o.data.dg_name, "rowid": divid}
      })
    }

    o.set_tab(o.options.tab)
  }

  return o
}

//
// prov template
//
function prov_template_tabs(divid, options) {
  o = tabs(divid)
  o.options = options

  o.load(function() {
    if (o.options.tpl_name) {
      var title = o.options.tpl_name
    } else {
      var title = o.options.tpl_id
    }
    o.closetab.children("p").text(title)

    // tab properties
    i = o.register_tab({
      "title": "form_tabs.properties",
      "title_class": "prov"
    })
    o.tabs[i].callback = function(divid) {
      prov_template_properties(divid, o.options)
    }

    // tab definition
    i = o.register_tab({
      "title": "form_tabs.definition",
      "title_class": "edit16"
    })
    o.tabs[i].callback = function(divid) {
      prov_template_definition(divid, o.options)
    }

    o.set_tab(o.options.tab)
  })
  return o
}



