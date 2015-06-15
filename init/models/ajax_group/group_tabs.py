def group_tabs(gid=None, role=None):
    tab = request.vars.tab
    if tab is None:
        tab = "tab1"

    rowid = uuid.uuid1().hex
    def js(tab, rowid):
        buff = ""
        for i in range(1, 4):
            buff += """$('#%(tab)s_%(id)s').hide();$('#li%(tab)s_%(id)s').removeClass('tab_active');"""%dict(tab='tab'+str(i), id=rowid)
        buff += """$('#%(tab)s_%(id)s').show();$('#li%(tab)s_%(id)s').addClass('tab_active');
                   if ("%(tab)s" in callbacks) {
                     callbacks["%(tab)s"]();
                     delete callbacks["%(tab)s"];
                   }
                """%dict(tab=tab, id=rowid)
        return buff

    if role is not None:
        group = db(db.auth_group.role==role).select(cacheable=True).first()
    elif gid is not None:
        group = db(db.auth_group.id==gid).select(cacheable=True).first()
    else:
        return ""

    if group is None:
        return TABLE(
                 TR(
                   TD(
                     T("No group information for %(group)s",
                       dict(group=request.vars.groupname)),
                   ),
                 ),
               )

    q = db.auth_membership.group_id == group.id
    group_user_count = db(q).count()

    q = db.nodes.team_responsible == group.role
    group_node_count = db(q).count()

    q = db.apps_responsibles.group_id == group.id
    group_app_count = db(q).count()

    info = TABLE(
      TR(TD(T('Group id'), _style='font-style:italic'), TD(group.id)),
      TR(TD(T('User count'), _style='font-style:italic'), TD(group_user_count)),
      TR(TD(T('Node count'), _style='font-style:italic'), TD(group_node_count)),
      TR(TD(T('App count'), _style='font-style:italic'), TD(group_app_count)),
    )

    q = db.auth_membership.group_id == group.id
    q &= db.auth_user.id == db.auth_membership.user_id
    rows = db(q).select(db.auth_user.first_name, db.auth_user.last_name)
    if len(rows) == 0:
        users = T("None")
    else:
        users = map(lambda x: P(' '.join((x.first_name, x.last_name))), rows)

    t = TABLE(
      TR(
        TD(
          UL(
            LI(
              P(
                group.role,
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
            LI(P(T("users"), _class='guy16', _onclick=js('tab3', rowid)), _id="litab3_"+str(rowid)),
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
            users,
            _id='tab3_'+str(rowid),
            _class='cloud',
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
                       args=['tab2_'+str(rowid)], vars={'groupname': group.role})
            ),
            """callbacks = {
                "tab2": %(id)s_load_group_hidden_menu_entries,
               }"""%dict(id='n'+str(rowid)),
            js(tab, rowid),
            _name='%s_to_eval'%rowid,
          ),
        ),
      ),
      _id=rowid,
    )
    return t


