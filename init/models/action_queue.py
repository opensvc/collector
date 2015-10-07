def action_queue_ws_data():
    data = {}
    sql = """select
              (select count(id) from action_queue where status in ('Q', 'W', 'R')) as queued,
              (select count(id) from action_queue where ret!=0) as ko,
              (select count(id) from action_queue where ret=0 and status='T') as ok
          """
    data = db.executesql(sql, as_dict=True)[0]
    return data

def action_q_event():
    l = {
      'event': 'action_q_change',
      'data': action_queue_ws_data(),
    }
    _websocket_send(event_msg(l))

def purge_action_queue():
    now = datetime.datetime.now()
    limit = now - datetime.timedelta(minutes=120)
    q = db.action_queue.date_dequeued < limit
    q &= db.action_queue.status.belongs(['T', 'C'])
    return db(q).delete()

