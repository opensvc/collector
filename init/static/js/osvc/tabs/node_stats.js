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

  o.div.load("/init/static/views/node_stats.html", "", function() {
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
      o.refresh_container_group($(this))
      $(this).slideToggle()
    })
  })
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
  group.children(".perf_plot").empty()
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
  var url = "/init/ajax_perf/call/json/json_"+groupname
  url += "?node=" + o.options.nodename
  url += "&b=" + o.begin.val()
  url += "&e=" + o.end.val()

  fn = window["stats_"+groupname]
  fn(url, uid)
}

