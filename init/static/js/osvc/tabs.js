//
// tabs
//
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

function tabs(divid) {
  var o = {}
  o.divid = divid
  o.div = $("#"+divid)

  o.tabs = []

  o.load = function(callback) {
    return tabs_load(o, callback)
  }
  o.init = function() {
    return tabs_init(o)
  }
  o.register_tab = function(data) {
    return tabs_register_tab(o, data)
  }
  o.add_tab = function(index) {
    return tabs_add_tab(o, index)
  }

  return o
}

function tabs_load(o, callback) {
  o.div.load('/init/static/views/tabs.html', "", function() {
    o.init()
    callback(o)
  })
}

function tabs_init(o) {
  o.closetab = o.div.find(".closetab")
  o.tabs_ul = o.closetab.parent()
  o.display = o.div.find(".tab_display")

  // empty tabs on click closetab
  o.closetab.bind("click", function() {
  o.div.parent().remove(); // Remove extraline
  o.div.remove();
  })
}

function tabs_register_tab(o, data) {
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

function tabs_add_tab(o, index) {
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
      sync_ajax("/init/default/svcmon_node/"+encodeURIComponent(o.options.nodename), [], divid, function(){})
    }

    // tab actions
    i = o.register_tab({
      "title": "node_tabs.actions",
      "title_class": "action16"
    })
    o.tabs[i].callback = function(divid) {
      sync_ajax("/init/svcactions/actions_node/"+encodeURIComponent(o.options.nodename), [], divid, function(){})
    }

    // tab log
    i = o.register_tab({
      "title": "node_tabs.log",
      "title_class": "log16"
    })
    o.tabs[i].callback = function(divid) {
      sync_ajax("/init/log/log_node/"+encodeURIComponent(o.options.nodename), [], divid, function(){})
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
      sync_ajax("/init/checks/checks_node/"+encodeURIComponent(o.options.nodename), [], divid, function(){})
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

    if (!o.options.tab) {
      o.closetab.next("li").trigger("click")
    } else {
      for (var i=0; i<o.tabs.length; i++) {
        if (o.tabs[i].title != o.options.tab) {
          continue
        }
        o.tabs[i].tab.trigger("click")
        break
      }
    }
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
      sync_ajax("/init/default/svcmon_svc/"+encodeURIComponent(o.options.svcname), [], divid, function(){})
    }

    // tab resources
    i = o.register_tab({
      "title": "service_tabs.resources",
      "title_class": "svc"
    })
    o.tabs[i].callback = function(divid) {
      sync_ajax("/init/resmon/resmon_svc/"+encodeURIComponent(o.options.svcname), [], divid, function(){})
    }

    // tab actions
    i = o.register_tab({
      "title": "service_tabs.actions",
      "title_class": "action16"
    })
    o.tabs[i].callback = function(divid) {
      sync_ajax("/init/svcactions/actions_svc/"+encodeURIComponent(o.options.svcname), [], divid, function(){})
    }

    // tab log
    i = o.register_tab({
      "title": "service_tabs.log",
      "title_class": "log16"
    })
    o.tabs[i].callback = function(divid) {
      sync_ajax("/init/log/log_svc/"+encodeURIComponent(o.options.svcname), [], divid, function(){})
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

    if (!o.options.tab) {
      o.closetab.next("li").trigger("click")
    } else {
      for (var i=0; i<o.tabs.length; i++) {
        if (o.tabs[i].title != o.options.tab) {
          continue
        }
        o.tabs[i].tab.trigger("click")
        break
      }
    }
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

    if (!o.options.tab) {
      o.closetab.next("li").trigger("click")
    } else {
      for (var i=0; i<o.tabs.length; i++) {
        if (o.tabs[i].title != o.options.tab) {
          continue
        }
        o.tabs[i].tab.trigger("click")
        break
      }
    }
  }
  return o
}


