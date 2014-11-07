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
    def js(tab, rowid):
        buff = ""
        for i in range(1, 3):
            buff += """$('#%(tab)s_%(id)s').hide();$('#li%(tab)s_%(id)s').removeClass('tab_active');"""%dict(tab='tab'+str(i), id=rowid)
        buff += """$('#%(tab)s_%(id)s').show();$('#li%(tab)s_%(id)s').addClass('tab_active');
                   if ("%(tab)s" in callbacks) {
                     callbacks["%(tab)s"]();
                     delete callbacks["%(tab)s"];
                   }
                """%dict(tab=tab, id=rowid)
        return buff

    session.forget(response)
    rowid = request.vars.rowid
    tab = request.vars.tab
    if tab is None:
        tab = "tab1"

    group = db(db.auth_group.role==request.vars.groupname).select(cacheable=True).first()
    if group is None:
        return TABLE(
                 TR(
                   TD(
                     T("No group information for %(group)s",
                       dict(group=request.vars.groupname)),
                   ),
                 ),
               )

    q = db.auth_group.role == request.vars.groupname
    q &= db.auth_membership.group_id == db.auth_group.id
    group_user_count = db(q).count()

    q = db.nodes.team_responsible == request.vars.groupname
    group_node_count = db(q).count()

    q = db.auth_group.role == request.vars.groupname
    q &= db.apps_responsibles.group_id == db.auth_group.id
    group_app_count = db(q).count()

    info = TABLE(
      TR(TD(T('User count'), _style='font-style:italic'), TD(group_user_count)),
      TR(TD(T('Node count'), _style='font-style:italic'), TD(group_node_count)),
      TR(TD(T('App count'), _style='font-style:italic'), TD(group_app_count)),
    )

    t = TABLE(
      TR(
        TD(
          UL(
            LI(
              P(
                T("%(n)s", dict(n=request.vars.groupname)),
                _class='nok',
                _onclick="""$('#%(id)s').remove()"""%dict(id=rowid),
              ),
              _class="closetab",
            ),
            LI(
              P(
                T("info"),
                _class='guys16',
                _onclick=js('tab1', rowid),
              ),
              _class="tab_active",
              _id="litab1_"+str(rowid),
            ),
            LI(P(T("menu entries"), _class='menu16', _onclick=js('tab2', rowid)), _id="litab2_"+str(rowid)),
          ),
          _class="tab",
        ),
      ),
      TR(
        TD(
          DIV(
            info,
            _id='tab1_'+str(rowid),
            _class='cloud_shown',
          ),
          DIV(
            IMG(_src=URL(r=request,c='static',f='spinner.gif')),
            _id='tab2_'+str(rowid),
            _class='cloud',
          ),
          SCRIPT(
            "function n%(rid)s_load_group_hidden_menu_entries(){sync_ajax('%(url)s', [], '%(id)s', function(){})}"%dict(
               id='tab2_'+str(rowid),
               rid=str(rowid),
               url=URL(r=request, c='ajax_group', f='ajax_group_hidden_menu_entries',
                       args=['tab2_'+str(rowid)], vars={'groupname': request.vars.groupname})
            ),
            """callbacks = {
                "tab2": %(id)s_load_group_hidden_menu_entries,
               }"""%dict(id='n'+str(rowid)),
            js(tab, rowid),
            _name='%s_to_eval'%rowid,
          ),
        ),
      ),
    )
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
