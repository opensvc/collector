function app_start() {
  $(window).on("popstate", function(e) {
    if (e.originalEvent.state !== null) {
      app_load_href(location.href);
    }
  })

  i18n_init(_app_start)
}

function _app_start() {
  $(document).i18n()
  search("layout_search_tool")
  services_feed_self_and_group()
  fset_selector("fset_selector")
  app_menu_entries_bind_click_to_load()
}

function app_load_href(href) {
    // loadable co-functions ends with '_load'
    event.preventDefault()
    var _href

    if (href.match(/:\/\//)) {
      // full url
      var fn_idx = 5
    } else {
      // relative url
      var fn_idx = 3
    }

    // http:, , host:port, app, ctrl, fn, arg0, arg1, ... lastarg?key=val,key=val
    var l = href.split("?")
    var v = l[0].split("/")

    v[fn_idx] += "_load"

    l[0] = v.join("/")
    _href = l.join("?")

    console.log("load", _href)
    $(".layout").load(_href, {}, function (responseText, textStatus, req) {
      if (textStatus == "error") {
        // load error
        console.log("fallback to location", href)
        document.location.replace(href)
      } else {
        // load success, purge tables not displayed anymore
        for (tid in osvc.tables) {
          if ($('#'+tid).length == 0) {
            delete osvc.tables[tid]
            if (tid in wsh) {
              delete wsh[tid]
            }
          }
        }
      }
    })
}

function app_menu_entries_bind_click_to_load() {
  $(".menu .menu_entry").bind("click", function(event) {
    var href = $(this).find("a").attr("href")
    if (!href) {
      return
    }
    app_load_href(href)
    $(".header .menu").hide("fold")

    // update browser url and history
    history.pushState({}, "", href)
  
    // prevent default
    return false
  })
}
