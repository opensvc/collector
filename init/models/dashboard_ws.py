def dashboard_events():
    l = {
      'event': 'dash_change',
      'data': {'foo': 'bar'},
    }
    _websocket_send(event_msg(l))

