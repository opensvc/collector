//
// Action queue stats
//
function action_queue_stats(data) {
    if (typeof data !== 'undefined') {
      _action_queue_stats(data)
      return
    }
    url = services_get_url() + "/init/rest/api/actions/stats"
    $.getJSON(url, function(data){_action_queue_stats(data)})
}

function _action_queue_stats(data) {
    var s = ''
    if ("data" in data)
      data = data.data
    if (!("queued" in data)) {
      return
    }
    if (data["queued"] > 0) {
      s += "<span class='boxed_small bgorange'>"+data["queued"]+'</span>'
    }
    if (data["ok"] > 0) {
      s += "<span class='boxed_small bggreen'>"+data['ok']+'</span>'
    }
    if (data["ko"] > 0) {
      s += "<span class='boxed_small bgred'>"+data['ko']+'</span>'
    }
    $(".header").find("[href$=action_queue]").html(s)
}

function action_queue_stats_wsh(data) {
    if (data["event"] == "action_q_change") {
        action_queue_stats(data['data'])
    }
}

wsh["action_queue_stats_wsh"] = action_queue_stats_wsh

// init on page load
action_queue_stats()


