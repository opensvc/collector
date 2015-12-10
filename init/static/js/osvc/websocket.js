//
// websockets
//
var wsh = {}
var ws_scheduled = {}

function ws_switch(e) {
    try {
        var data = $.parseJSON(e.data)
    } catch(e) {
        return
    }
    if (data.uuid in ws_scheduled) {
        return
    }
    var _data = data.data
    ws_scheduled[data.uuid] = setTimeout(function() {
        delete(ws_scheduled[data.uuid])
        for (i=0; i<_data.length; i++) {
            ws_switch_one(_data[i])
        }
    }, 1000)
}

function ws_switch_one(data) {
    if (!("event" in data)) {
        return
    }
    for (key in wsh) {
        if (osvc && osvc.tables && (key in osvc.tables) && osvc.tables[key].e_wsswitch && !osvc.tables[key].e_wsswitch.find("input").prop('checked')) {
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


