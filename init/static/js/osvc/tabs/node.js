//
// node
//
function node_tabs(divid, options) {
  var o = tabs(divid)
  o.options = options
  o.load(function(){
    var i = 0

    // tab properties
    o.closetab.children("p").text(o.options.nodename)
    i = o.register_tab({
      "title": "node_tabs.properties",
      "title_class": "icon node16"
    })
    o.tabs[i].callback = function(divid) {
      node_properties(divid, {"nodename": o.options.nodename})
    }

    // tab alerts
    i = o.register_tab({
      "title": "node_tabs.alerts",
      "title_class": "icon alert16"
    })
    o.tabs[i].callback = function(divid) {
      table_dashboard_node(divid, o.options.nodename)
    }

    // tab services
    i = o.register_tab({
      "title": "node_tabs.services",
      "title_class": "icon svc"
    })
    o.tabs[i].callback = function(divid) {
      table_service_instances_node(divid, o.options.nodename)
    }

    // tab actions
    i = o.register_tab({
      "title": "node_tabs.actions",
      "title_class": "icon action16"
    })
    o.tabs[i].callback = function(divid) {
      table_actions_node(divid, o.options.nodename)
    }

    // tab log
    i = o.register_tab({
      "title": "node_tabs.log",
      "title_class": "icon log16"
    })
    o.tabs[i].callback = function(divid) {
      table_log_node(divid, o.options.nodename)
    }

    // tab topology
    i = o.register_tab({
      "title": "node_tabs.topology",
      "title_class": "icon dia16"
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
      "title_class": "icon hd16"
    })
    o.tabs[i].callback = function(divid) {
      sync_ajax("/init/ajax_node/ajax_node_stor/"+divid.replace("-", "_")+"/"+encodeURIComponent(o.options.nodename), [], divid, function(){})
    }

    // tab network
    i = o.register_tab({
      "title": "node_tabs.network",
      "title_class": "icon net16"
    })
    o.tabs[i].callback = function(divid) {
      ips(divid, {"nodes": o.options.nodename})
    }

    // tab stats
    i = o.register_tab({
      "title": "node_tabs.stats",
      "title_class": "icon spark16"
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
      "title_class": "icon edit"
    })
    o.tabs[i].callback = function(divid) {
      wiki(divid, {"nodes": o.options.nodename})
    }

    // tab checks
    i = o.register_tab({
      "title": "node_tabs.checks",
      "title_class": "icon check16"
    })
    o.tabs[i].callback = function(divid) {
      table_checks_node(divid, o.options.nodename)
    }

    // tab packages
    i = o.register_tab({
      "title": "node_tabs.packages",
      "title_class": "icon pkg16"
    })
    o.tabs[i].callback = function(divid) {
	table_packages_node(divid, o.options.nodename)
    }

    // tab compliance
    i = o.register_tab({
      "title": "node_tabs.compliance",
      "title_class": "icon comp16"
    })
    o.tabs[i].callback = function(divid) {
      sync_ajax("/init/compliance/ajax_compliance_node/"+encodeURIComponent(o.options.nodename), [], divid, function(){})
    }

    // tab sysreport
    i = o.register_tab({
      "title": "node_tabs.sysreport",
      "title_class": "icon log16"
    })
    o.tabs[i].callback = function(divid) {
      sysrep(divid, {"nodes": o.options.nodename})
    }

    o.set_tab(o.options.tab)
  })
  return o
}


function node_properties(divid, options)
{
    var o = {}

    // store parameters
    o.options = options

    o.div = $("#"+divid)

    o.init = function(){
      return node_props_init(this)
    }
    o.responsible_init = function(){
      return node_props_responsible_init(this)
    }

    o.div.load('/init/static/views/node_properties.html', "", function() {
      o.div = o.div.children()
      o.div.uniqueId()
      o.init()
    })
    return o
}

function node_props_init(o)
{
	o.div.i18n();
	o.e_tags = o.div.find(".tags")
	o.e_tags.uniqueId()

	o.e_team_responsible = o.div.find("#team_responsible")
	o.e_team_integ = o.div.find("#team_integ")
	o.e_team_support = o.div.find("#team_support")
	o.e_app = o.div.find("#app")
	o.e_uuid = o.div.find("#uuid")
	o.e_root_pwd = o.div.find("#root_pwd")
	o.e_action_type = o.div.find("#action_type")

	// fill the view with values from /nodes/<nodename>
	services_osvcgetrest("R_NODE", [o.options.nodename], {"meta": "false"}, function(jd) {
		if (!jd.data) {
			o.div.html(services_error_fmt(jd))
		}
		var data = jd.data[0];
		var key;
		for (key in data) {
			if (!data[key]) {
				continue
			}
			if (key == "mem_bytes") {
				o.div.find("#"+key).text(fancy_size_mb(data[key]))
			} else {
				o.div.find("#"+key).text(data[key])
			}
		}

		// init sys responsible tools
		if (o.options.nodename) {
			services_osvcgetrest("R_NODE_AM_I_RESPONSIBLE", [o.options.nodename], "", function(jd) {
				o.options.responsible = jd.data
				if (!o.options.responsible) {
					return
				}
				o.responsible_init()
			})
		}
	},
	function(xhr, stat, error) {
		o.div.html(services_ajax_error_fmt(xhr, stat, error))
	})

	// init tags
	tags({
		"tid": o.e_tags.attr("id"),
		"nodename": o.options.nodename,
		"responsible": o.options.responsible
	})
}

function node_props_responsible_init(o)
{
	// has this node an opensvc agent ?
	if (o.div.find("#version").text() != "") {
		o.has_agent = true
	} else {
		o.has_agent = false
	}

	// init uuid
	o.e_uuid.parent().show()
	services_osvcgetrest("R_NODE_UUID", [o.options.nodename], {"meta": "false"}, function(jd) {
		if (!jd.data) {
			o.e_uuid.html(services_error_fmt(jd))
		}
		if (jd.data.length == 0) {
			o.e_uuid.text(i18n.t("node_properties.no_uuid"))
			return
		}
		var data = jd.data[0];
		o.e_uuid.text(data.uuid)
	},
	function(xhr, stat, error) {
		o.e_uuid.html(services_ajax_error_fmt(xhr, stat, error))
	})

	// init passwd
	o.e_root_pwd.parent().show()
	e = $("<span></span>")
	e.text(i18n.t("node_properties.retrieve_root_password"))
	e.addClass("clickable")
	e.bind("click", function(){
		o.e_root_pwd.empty()
		spinner_add(o.e_root_pwd)
		services_osvcgetrest("R_NODE_ROOT_PASSWORD", [o.options.nodename], "", function(jd) {
			spinner_del(o.e_root_pwd)
			if (!jd.data) {
				o.e_root_pwd.html(services_error_fmt(jd))
			}
			o.e_root_pwd.text(jd.data)
			o.e_root_pwd.removeClass("lock")
		})
	})
	o.e_root_pwd.html(e).addClass("icon lock")

	// init updaters
	tab_properties_generic_updater({
		"condition": function(e) {
			if (o.has_agent && (e.attr("agent") == 1)) {
				return false
			}
			return true
		},
		"div": o.div,
		"privileges": ["NodeManager", "Manager"],
		"post": function(_data, callback, error_callback) {
			services_osvcpostrest("R_NODE", [o.options.nodename], "", _data, callback, error_callback)
		}
	})
	tab_properties_generic_autocomplete({
		"div": o.e_action_type,
		"privileges": ["NodeManager", "Manager"],
		"post": function(_data, callback, error_callback) {
			services_osvcpostrest("R_NODE", [o.options.nodename], "", _data, callback, error_callback)
		},
		"get": function(callback) {
			var opts = ["push", "pull"]
			callback(opts)
		}
	})
}

function node_stats(divid, options) {
  var o = {}
  o.divid = divid
  o.div = $("#"+divid)
  o.options = options

  o.init = function() {
    return node_stats_init(o)
  }
  o.dates_set_now = function() {
    return node_stats_dates_set_now(o)
  }
  o.dates_set_last_day = function() {
    return node_stats_dates_set_last_day(o)
  }
  o.dates_set_last_week = function() {
    return node_stats_dates_set_last_week(o)
  }
  o.dates_set_last_month = function() {
    return node_stats_dates_set_last_month(o)
  }
  o.dates_set_last_year = function() {
    return node_stats_dates_set_last_year(o)
  }
  o.init_container = function(container) {
    return node_stats_init_container(o, container)
  }
  o.refresh_container_group = function(group) {
    return node_stats_refresh_container_group(o, group)
  }
  o.refresh_container_groups = function() {
    return node_stats_refresh_container_groups(o)
  }

  o.div.load(o.options.view, "", function() {
    o.init()
  })
  return o
}

function node_stats_init(o) {
  o.div.i18n();

  // init date inputs
  o.begin = o.div.find("input[name=begin]")
  o.end = o.div.find("input[name=end]")

  o.begin.datetimepicker({dateFormat:'yy-mm-dd'});
  o.end.datetimepicker({dateFormat:'yy-mm-dd'});
  o.begin.prev().attr("title", i18n.t("node_stats.begin"))
  o.end.next().attr("title", i18n.t("node_stats.end"))

  o.dates_set_now()

  // init buttons
  o.btn_now = o.div.find("input[name=now]")
  o.btn_last_day = o.div.find("input[name=last_day]")
  o.btn_last_week = o.div.find("input[name=last_week]")
  o.btn_last_month = o.div.find("input[name=last_month]")
  o.btn_last_year = o.div.find("input[name=last_year]")

  o.btn_now.attr("value", i18n.t("node_stats.now"))
  o.btn_last_day.attr("value", i18n.t("node_stats.last_day"))
  o.btn_last_week.attr("value", i18n.t("node_stats.last_week"))
  o.btn_last_month.attr("value", i18n.t("node_stats.last_month"))
  o.btn_last_year.attr("value", i18n.t("node_stats.last_year"))

  o.btn_now.bind("click", function() {
    o.dates_set_now()
    o.refresh_container_groups()
  })
  o.btn_last_day.bind("click", function() {
    o.dates_set_last_day()
    o.refresh_container_groups()
  })
  o.btn_last_week.bind("click", function() {
    o.dates_set_last_week()
    o.refresh_container_groups()
  })
  o.btn_last_month.bind("click", function() {
    o.dates_set_last_month()
    o.refresh_container_groups()
  })
  o.btn_last_year.bind("click", function() {
    o.dates_set_last_year()
    o.refresh_container_groups()
  })

  // init containers
  o.div.find(".container").each(function() {
    o.init_container($(this))
  })
}

function node_stats_dates_set_now(o) {
  var d = new Date()
  o.end.val(print_date(d))
  d.setDate(d.getDate()-1)
  o.begin.val(print_date(d))
  o.begin.effect("highlight")
  o.end.effect("highlight")
}

function node_stats_dates_set_last_day(o) {
  var d = new Date()
  d.setMinutes(0)
  d.setHours(0)
  d.setSeconds(0)
  o.end.val(print_date(d))
  d.setDate(d.getDate()-1)
  o.begin.val(print_date(d))
  o.begin.effect("highlight")
  o.end.effect("highlight")
}

function node_stats_dates_set_last_week(o) {
  var d = new Date()
  d.setMinutes(0)
  d.setHours(0)
  d.setSeconds(0)
  o.end.val(print_date(d))
  d.setDate(d.getDate()-7)
  o.begin.val(print_date(d))
  o.begin.effect("highlight")
  o.end.effect("highlight")
}

function node_stats_dates_set_last_month(o) {
  var d = new Date()
  d.setMinutes(0)
  d.setHours(0)
  d.setSeconds(0)
  o.end.val(print_date(d))
  d.setDate(d.getDate()-31)
  o.begin.val(print_date(d))
  o.begin.effect("highlight")
  o.end.effect("highlight")
}

function node_stats_dates_set_last_year(o) {
  var d = new Date()
  d.setMinutes(0)
  d.setHours(0)
  d.setSeconds(0)
  o.end.val(print_date(d))
  d.setDate(d.getDate()-365)
  o.begin.val(print_date(d))
  o.begin.effect("highlight")
  o.end.effect("highlight")
}

function node_stats_init_container(o, container) {
  container.children(".refresh16").bind("click", function() {
    $(this).parent().children("[name=plots]").each(function() {
      o.refresh_container_group($(this))
    })
  })
  container.children(".nok").bind("click", function() {
    $(this).hide()
    $(this).siblings(".refresh16").hide()
    $(this).parent().children("[name=plots]").each(function() {
      if ($(this).is(":visible")) {
        $(this).slideToggle()
      }
    })
  })
  container.children("a").first().bind("click", function() {
    $(this).siblings(".jqplot-image-container-close").toggle()
    var plots = $(this).parent().children("[name=plots]")
    plots.each(function() {
      if ($(this).is(":visible")) {
        $(this).slideToggle()
        return
      }
      $(this).show()
      o.refresh_container_group($(this))
    })
  })
  if (container.hasClass("open_on_load")) {
    container.children("a").first().trigger("click")
  }
}

function node_stats_refresh_container_groups(o) {
  o.div.find(".container").each(function() {
    if (!$(this).is(":visible")) {
      return
    }
    $(this).children("[name=plots]").each(function() {
      o.refresh_container_group($(this))
    })
  })
}

function node_stats_refresh_container_group(o, group) {
  if (group.hasClass("jqplot-target")) {
    group.empty()
  }
  group.find(".jqplot-target").empty()
  group.siblings(".jqplot-image-container").remove()

  // jqplot needs per graph id
  // generate a main one, and suffix in the per-plot div
  group.uniqueId()
  var uid = group.attr("id")

  group.children("div.perf_plot").each(function() {
    e = $("<div></div>")
    e.attr("id", uid+$(this).attr("name"))
    $(this).append(e)
  })

  var groupname = group.attr("group")
  var url = o.options.controller+"/call/json/json_"+groupname
  url += "?node=" + o.options.nodename
  url += "&b=" + o.begin.val()
  url += "&e=" + o.end.val()

  fn = window["stats_"+groupname]
  fn(url, uid)
}

function ips(divid, options)
{
    var o = {}

    // store parameters
    o.divid = divid
    o.direct_access_url = "R_IPS";
    o.div = $("#"+divid);
    o.nodes = options.nodes;

    o.ips_load = function()
    {
    	return ips_load(o);
    }

    o.div.load('/init/static/views/network.html', "", function() {
      ips_init(o);
    });
    
}

function ips_init(o)
{
	o.ips_ipv4_u = o.div.find("#ips_ipv4_u");
    o.ips_ipv6_u = o.div.find("#ips_ipv6_u");
    o.ips_ipv4_m = o.div.find("#ips_ipv4_m");
    o.ips_ipv6_m = o.div.find("#ips_ipv6_m");

    o.div.i18n();

 	o.ips_load();
}

function ips_build_table(o, resultset)
{
    
}

function ips_load(o)
{
    var th = "<tr><th>mac</th><th style='width:7em'>interface</th><th>type</th><th style='width:20em'>addr</th><th style='width:7em'>mask</th><th style='width:10em'>net name</th><th style='width:10em'>net comment</th><th style='width:4em'>net pvid</th><th>net base</th><th style='width:7em'>net gateway</th><th style='width:5em'>net prio</th><th style='width:7em'>net begin</th><th style='width:7em'>net end</th></tr>";

    services_osvcgetrest("R_IPS", [o.nodes],"", function(jd) {
      if (jd.data === undefined) {
        return;
      }

      o.ips_ipv4_u.html(th);
      o.ips_ipv6_u.html(th);
      o.ips_ipv4_m.html(th);
      o.ips_ipv6_m.html(th);

      var result = jd.data;
      // count
      var ipv4ucount=ipv6ucount=ipv4mcount=ipv6mcount=0;
      for(i=0;i<result.length;i++)
      {
        var resultset = result[i];
        if (!is_empty_or_null(resultset.net_name)) resultset.net_name = '-';
        if (!is_empty_or_null(resultset.net_comment)) resultset.net_comment = '-';
        if (!is_empty_or_null(resultset.net_pvid)) resultset.net_pvid = '-';
        if (!is_empty_or_null(resultset.net_network)) resultset.net_network = '-';
        if (!is_empty_or_null(resultset.net_gateway)) resultset.net_gateway = '-';
        if (!is_empty_or_null(resultset.prio)) resultset.prio = '-';
        if (!is_empty_or_null(resultset.net_begin)) resultset.net_begin = '-';
        if (!is_empty_or_null(resultset.net_end)) resultset.net_end = '-';
        var td ="<tr><td>";
        td += resultset.mac + "</td><td>";
        td += resultset.intf + "</td><td>";
        td += resultset.addr_type + "</td><td>";
        td += resultset.addr + "</td><td>";
        td += resultset.mask + "</td><td class='bluer'>";
        td += resultset.net_name + "</td><td class='bluer'>";
        td += resultset.net_comment + "</td><td class='bluer'>";
        td += resultset.net_pvid + "</td><td class='bluer'>";
        td += resultset.net_network + "</td><td class='bluer'>";
        td += resultset.net_gateway + "</td><td class='bluer'>";
        td += resultset.prio + "</td><td class='bluer'>";
        td += resultset.net_begin + "</td><td class='bluer'>";
        td += resultset.net_end;
        td += "</td></tr>";

        // Handle dispatch in array
        if (resultset.addr_type == "ipv4")
        {
            if (resultset.mask == "")
            {
                o.ips_ipv4_m.append(td);
                ipv4mcount+=1;
            }
            else
            {
                o.ips_ipv4_u.append(td);
                ipv4ucount+=1;
            }
        }
        else 
        {
            if (resultset.mask == "")
            {
                o.ips_ipv6_m.append(td);
                ipv6mcount+=1;
            }
            else
            {
                o.ips_ipv6_u.append(td);
                ipv6ucount+=1;
            }
        }
      }
        var emtpyline="<tr><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td></tr>";
        if (ipv4mcount==0) o.ips_ipv4_m.append(emtpyline);
        if (ipv4ucount==0) o.ips_ipv4_u.append(emtpyline);
        if (ipv6mcount==0) o.ips_ipv6_m.append(emtpyline);
        if (ipv6ucount==0) o.ips_ipv6_u.append(emtpyline);

    });
}
