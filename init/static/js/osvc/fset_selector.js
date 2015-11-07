function fset_selector(divid, callback) {
  var o = {}
  o.divid = divid
  o.div = $("#"+divid)
  o.div.empty()
  o.callback = callback

  o.load_span = function() {
    return fset_selector_load_span(this)
  }
  o.load_input = function(current_fset_name) {
    return fset_selector_load_input(this, current_fset_name)
  }
  o.load_bindings = function() {
    return fset_selector_load_bindings(this)
  }
  o.set_fset = function(new_fset) {
    return fset_selector_set_fset(this, new_fset)
  }
  o.unset_fset = function() {
    return fset_selector_unset_fset(this)
  }

  o.span = $("<span class='clickable'></span>")
  o.input = $("<select class='editable hidden'></select>")
  o.div.append(o.span)
  o.div.append(o.input)

  o.load_span()
  return o
}

function fset_selector_unset_fset(o) {
  services_osvcdeleterest("R_USERS_SELF_FILTERSET", [], "", "", function(jd) {
      o.span.empty()
      o.span.text(o.input.val())
      o.span.show()
      o.input.hide()
      o.callback()
  },
  function(xhr, stat, error) {
      o.span.html(services_ajax_error_fmt(xhr, stat, error))
      o.span.show()
  })
}

function fset_selector_set_fset(o, new_fset) {
  services_osvcpostrest("R_USERS_SELF_FILTERSET_ONE", [new_fset], "", "", function(jd) {
      o.span.empty()
      o.span.text(o.input.val())
      o.span.show()
      o.input.hide()
      o.callback()
  },
  function(xhr, stat, error) {
      o.span.html(services_ajax_error_fmt(xhr, stat, error))
      o.span.show()
  })
}

function fset_selector_load_bindings(o) {
  o.span.bind("click", function() {
    o.span.hide()
    o.input.show().focus()
  })
  o.input.bind("change", function() {
    var new_fset = o.input.find(":selected").attr("id")
    if (new_fset < 0) {
      o.unset_fset()
    } else {
      o.set_fset(new_fset)
    }
  })
}

function fset_selector_load_input(o, current_fset_name) {
  o.input.empty()

  // add the "none" option
  var option = $("<option></option)")
  option.text(i18n.t("fset_selector.none"))
  option.attr("id", -1)
  if (option.text() == current_fset_name) {
    option.attr("selected", "")
  }
  o.input.append(option)

  services_osvcgetrest("R_FILTERSETS", "", {"limit": "0", "props": "id,fset_name", "meta": "0"}, function(jd) {
    for (var i=0; i<jd.data.length; i++) {
      var data = jd.data[i]
      var option = $("<option></option)")
      option.text(data.fset_name)
      option.attr("id", data.id)
      if (data.fset_name == current_fset_name) {
        option.attr("selected", "")
      }
      o.input.append(option)
    }

    // all is loaded, we can bind events
    o.load_bindings()
  })
}

function fset_selector_load_span(o) {
  spinner_add(o.div)
  services_osvcgetrest("R_USERS_SELF_FILTERSET", "", "", function(jd) {
    spinner_del(o.div)
    if (jd.data.length == 1) {
      fset_name = jd.data[0].fset_name
    } else {
      fset_name = i18n.t("fset_selector.none")
    }
    o.span.text(fset_name)
    o.load_input(fset_name)
  })

  return o
}
