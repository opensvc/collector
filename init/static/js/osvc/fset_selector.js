function fset_selector(divid, callback) {
  var o = {}
  o.divid = divid
  o.div = $("#"+divid)
  o.div.empty()
  o.callback = callback

  o.load_span = function() {
    return fset_selector_load_span(o)
  }
  o.load_area = function() {
    return fset_selector_load_area(o)
  }
  o.set_fset = function(new_fset_id, new_fset_name) {
    return fset_selector_set_fset(o, new_fset_id, new_fset_name)
  }
  o.unset_fset = function() {
    return fset_selector_unset_fset(o)
  }
  o.container = function() {
    return fset_selector_container(o)
  }
  o.callbacks = function() {
    return fset_selector_callbacks(o)
  }
  o.add_fset = function(id, name) {
    return fset_selector_add_fset(o, id, name)
  }

  o.container()
  return o
}

function fset_selector_container(o) {
  var e = $("<span class='filter16' name='fset_selector'></span>")
  e.text(i18n.t('table.filter'))

  var span_selector = $("<span class='clickable'></span>")
  span_selector.uniqueId()
  e.append(span_selector)
  o.span = span_selector

  e.i18n()
  o.div.append(e)

  o.load_span()
}

function fset_selector_callbacks(o) {
  // refresh tables
  for (tid in osvc.tables) {
    osvc.tables[tid].refresh()
  }
  if (o.callback) {
    o.callback()
  }
}

function fset_selector_unset_fset(o) {
  services_osvcdeleterest("R_USERS_SELF_FILTERSET", [], "", "", function(jd) {
    o.span.empty()
    o.span.text(i18n.t("table.none"))
    o.span.attr("fset_id", "-1")
    $(".flash").hide()
    o.callbacks()
  },
  function(xhr, stat, error) {
    o.span.html(services_ajax_error_fmt(xhr, stat, error))
    o.span.show()
  })
}

function fset_selector_set_fset(o, new_fset_id, new_fset_name) {
  services_osvcpostrest("R_USERS_SELF_FILTERSET_ONE", [new_fset_id], "", "", function(jd) {
    o.span.empty()
    o.span.text(new_fset_name)
    o.span.attr("fset_id", new_fset_id)
    $(".flash").hide()
    o.callbacks()
  },
  function(xhr, stat, error) {
      o.span.html(services_ajax_error_fmt(xhr, stat, error))
      o.span.show()
  })
}

function fset_selector_add_fset(o, id, name) {
  var e = $("<div class='menu_entry menu_box' fset_id='"+id+"'></div>")
  var icon = $("<div class='menu_icon filter16'></div>")
  e.append(icon)

  var text = $("<div></div>")
  var title = $("<div name='title'></div>")
  title.text(name)
  text.append(title)
  var subtitle = $("<div></div>")
  text.append(subtitle)
  e.append(text)

  e.bind("click", function() {
    var new_fset_id = $(this).attr("fset_id")
    var new_fset_name = $(this).find("[name=title]").text()
    if (new_fset_id < 0) {
      o.unset_fset()
    } else {
      o.set_fset(new_fset_id, new_fset_name)
    }
  })

  o.area.append(e)
}

function fset_selector_load_area(o) {
  if (o.area) {
    o.area.remove()
  }
  o.area = $("<div name='fset_selector_entries'></div>")
  var current_fset_id = o.span.attr("fset_id")

  // add the "none" option
  o.add_fset(-1, i18n.t("fset_selector.none"))

  services_osvcgetrest("R_FILTERSETS", "", {"limit": "0", "props": "id,fset_name", "meta": "0"}, function(jd) {
    for (var i=0; i<jd.data.length; i++) {
      var data = jd.data[i]
      o.add_fset(data.id, data.fset_name)
    }

    o.area.find("[fset_id="+current_fset_id+"]").addClass("menu_selected")
    $(".flash").html(o.area)
  })
}

function fset_selector_load_span(o) {
  spinner_add(o.div)
  services_osvcgetrest("R_USERS_SELF_FILTERSET", "", "", function(jd) {
    spinner_del(o.div)
    if (jd.data.length == 1) {
      var fset_name = jd.data[0].fset_name
      var fset_id = jd.data[0].id
    } else {
      var fset_name = i18n.t("fset_selector.none")
      var fset_id = -1
    }
    o.span.text(fset_name)
    o.span.attr("fset_id", fset_id)
    o.span.bind("click", function() {
      if (!$(".flash").is(":visible")) {
        $(".flash").show("fold")
        $("#search_input").focus()
        o.load_area()
      }
    })
  })

  return o
}
