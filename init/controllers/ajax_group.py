def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    session.forget()
    return service()

@auth.requires_login()
def ajax_group():
    session.forget(response)
    t = group_tabs(role=request.vars.groupname)
    return t

@auth.requires_login()
def ajax_group_hidden_menu_entries():
    id = request.args[0]
    groupname = request.vars.groupname

    q = db.auth_group.role == groupname
    group = db(q).select(db.auth_group.id).first()
    if group is None:
        return T("No information on this group")

    sql = """select id from auth_group where
             role="%s" and privilege="F"
          """ % groupname
    rows = db.executesql(sql)
    if len(rows) == 0:
        return T("No menu entries settings for privilege groups")

    q = db.group_hidden_menu_entries.group_id == group.id
    hidden_menu_entries = [r.menu_entry for r in db(q).select(db.group_hidden_menu_entries.menu_entry)]

    ug = user_groups()
    manager = "Manager" in ug

    def html_group_hidden_menu_entries():
        d = []

        for menu_entry in menu_entries:
            if menu_entry in hidden_menu_entries:
                hidden = True
            else:
                hidden = False
            attrs = dict(
              _type="checkbox",
              _disabled=not manager,
              _checked=hidden,
              _group_id=group.id,
              _menu_entry=menu_entry,
              _name='group_hidden_menu_entry_check',
            )
            _d = DIV(
                   INPUT(
                     **attrs
                   ),
                   DIV(
                     menu_entries_data[menu_entry],
                   ),
                   _class="group_hidden_menu_entry",
                 )
            d.append(_d)
        return DIV(d)

    d = DIV(
          H2(T("Hidden menu entries")),
          html_group_hidden_menu_entries(),
          DIV(_class="spacer"),
        )
    return DIV(d, SCRIPT("bind_group_hidden_menu_entries()"))

@service.json
def set_group_hidden_menu_entry():
    group_id = request.vars.group_id
    menu_entry = request.vars.menu_entry
    hidden = request.vars.hidden

    if 'Manager' not in user_groups():
        return {"err": "Not allowed"}
    if group_id is None:
        return {"err": "group id not specified"}
    if menu_entry is None:
        return {"err": "menu entry not specified"}
    if menu_entry not in menu_entries:
        return {"err": "unknown menu entry"}

    q = db.auth_group.id == group_id
    g = db(q).select().first()
    if g is None:
        return {"err": "group id does not exist"}
    g = g.role

    if hidden == "true":
        db.group_hidden_menu_entries.insert(
          menu_entry=menu_entry,
          group_id=group_id
        )
        _log('group.menu_entries',
             'hide menu entry %(e)s from group %(g)s members',
             dict(g=g, e=menu_entry))
    elif hidden == "false":
        q = db.group_hidden_menu_entries.menu_entry == menu_entry
        q &= db.group_hidden_menu_entries.group_id == group_id
        db(q).delete()
        _log('group.menu_entries',
             'display menu entry %(e)s to group %(g)s members',
             dict(g=g, e=menu_entry))
    else:
        return {"err": "Unsupported hidden target value"}

    return {}
