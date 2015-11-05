//
// websockets
//
var wsh = {}
var last_events = []

function ws_duplicate_event(uid) {
    if (last_events.indexOf(uid) >= 0) {
        return true
    }
    last_events.push(uid)
    if (last_events.length > 10) {
        last_events = last_events.slice(0, 10)
    }
    return false
}

function ws_switch(e) {
    var data = []
    try {
        data = eval('('+e.data+')')
    } catch(ex) {
        return
    }
    if (ws_duplicate_event(data['uuid'])) {
        return
    }
    data = data['data']
    for (i=0; i<data.length; i++) {
        ws_switch_one(data[i])
    }
}

function ws_switch_one(data) {
    if (!("event" in data)) {
        return
    }
    for (key in wsh) {
        if (osvc && osvc.tables && (key in osvc.tables) && !osvc.tables[key].e_wsswitch.find("input").prop('checked')) {
            // websocket disabled for this table.
            // just remember we have queued change.
            osvc.tables[key].need_refresh = true
            return
        }
        ws_action_switch = wsh[key]
        ws_action_switch(data)
    }
}

web2py_websocket("wss://"+window.location.hostname+"/realtime/generic", ws_switch)


