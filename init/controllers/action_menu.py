def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    session.forget()
    return service()

@service.json
def json_action():
    data = json.loads(request.vars.data)
    n = 0 # accepted actions count
    n_raw = len(data)

    data = factorize_actions(data)
    n_factorized = len(data)

    for d in data:
        n += json_action_one(d)
        if n % 10 == 0:
            action_q_event()

    start_actiond()

    if n > 0:
        action_q_event()

    return {
      "accepted": n,
      "rejected": n_factorized-n,
      "factorized": n_raw-n_factorized,
    }

