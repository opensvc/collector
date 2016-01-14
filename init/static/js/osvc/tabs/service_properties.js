function service_properties(divid, options)
{
    var o = {}

    // store parameters
    o.options = options

    o.div = $("#"+divid)

    o.init = function(){
      return service_props_init(this)
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

function service_props_init(o)
{
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
    spinner_add(o.responsibles)
    services_osvcgetrest("R_APP_RESPONSIBLES", [data.svc_app], {"meta": "0", "limit": "0"}, function(jd) {
      spinner_del(o.responsibles)
      if (!jd.data) {
        o.responsibles.html(services_error_fmt(jd))
      }
      o.responsibles.addClass("group_list_small")
      for (var i=0; i<jd.data.length; i++) {
        var li = $("<li></li>")
        li.text(jd.data[i].role)
        o.responsibles.append(li)
      }
    })


  },
  function() {
    o.div.html(services_ajax_error_fmt(xhr, stat, error))
  });

  // init tags
  tags({
    "tid": o.e_tags.attr("id"),
    "svcname": o.options.svcname,
  })
}

