function app_start() {
  i18n_init(_app_start)
}

function _app_start() {
  $(document).i18n()
  search_init()
  services_feed_self_and_group()
  fset_selector("fset_selector")
  menu_entries_bind_click_to_load()
}

function menu_entries_bind_click_to_load() {
  $(".menu").find("a").bind("click", function(event) {
    var href = $(this).attr("href")
    if (!href) {
      return
    }
    event.preventDefault()
    var _href
    if (href.indexOf("?") >= 0) {
      l = href.split("?")
      _href = l[0] + "_load?" + l[1]
    } else {
      _href = href + "_load"
    }
    console.log("load", _href)
    history.pushState({}, "", href)
    $(".layout").load(_href)
  
    // purge tables not displayed anymore
    for (tid in osvc.tables) {
      if ($('#'+tid).length == 0) {
        delete osvc.tables[tid]
        if (tid in wsh) {
          delete wsh[tid]
        }
      }
    }
  })
}
