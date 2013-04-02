def notify_action_queue(nodename):
    pass

def purge_action_queue():
    now = datetime.datetime.now()
    limit = now - datetime.timedelta(minutes=120)
    q = db.action_queue.date_dequeued < limit
    q &= db.action_queue.status == 'T'
    return db(q).delete()

def queued_actions():
    q = db.action_queue.status == 'W'
    w = db(q).count()
    q = db.action_queue.status == 'R'
    r = db(q).count()
    return (r, w)

def queued_action_widget():
    d = DIV(
          IMG(_src=URL(r=request, c='static', f='action16.png')),
          SCRIPT(
            """ ajax("%(url_queue)s", [], "action_queue");
               (function refresh_actions(){
                  setTimeout(function(){
                    if ($("#action_queue").is(":visible")) {
                      ajax("%(url_queue)s", [], "action_queue");
                    }
                    refresh_actions();
                  }, 15000);
               })();
            """%dict(
                  url_queue=URL(r=request, c='action_queue', f='ajax_actions'),
                ),
          ),
          _id='action_count',
          _onclick='click_action_queue("%s");'%URL(r=request, c='action_queue',
                                                   f='ajax_actions'),
          _class='search',
        )
    return d
