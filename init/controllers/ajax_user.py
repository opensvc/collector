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
def ajax_user():
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

    user = db(db.v_users.fullname==request.vars.username).select(cacheable=True).first()
    if user is None:
        return TABLE(
                 TR(
                   TD(
                     T("No user information for %(user)s",
                       dict(user=request.vars.username)),
                   ),
                 ),
               )

    ug = user_groups()
    manager = "Manager" in ug

    info = TABLE(
      TR(TD(T('Email'), _style='font-style:italic'), TD(user['email'])),
      TR(TD(T('Phone'), _style='font-style:italic'), TD(user['phone_work'])),
      TR(TD(T('Domains'), _style='font-style:italic'), TD(user['domains'])),
      TR(TD(T('Manager'), _style='font-style:italic'), TD(user['manager'])),
      TR(TD(T('Primary Group'), _style='font-style:italic'), TD(user['primary_group'])),
      TR(TD(T('Groups'), _style='font-style:italic'), TD(user['groups'])),
      TR(TD(T('Lock Filter'), _style='font-style:italic'), TD(user['lock_filter'])),
      TR(TD(T('Filterset Name'), _style='font-style:italic'), TD(user['fset_name'])),
    )

    t = TABLE(
      TR(
        TD(
          UL(
            LI(
              P(
                T("%(n)s", dict(n=request.vars.username)),
                _class='nok',
                _onclick="""$('#%(id)s').remove()"""%dict(id=rowid),
              ),
              _class="closetab",
            ),
            LI(
              P(
                T("info"),
                _class='guy16',
                _onclick=js('tab1', rowid),
              ),
              _class="tab_active",
              _id="litab1_"+str(rowid),
            ),
            LI(P(T("groups"), _class='guys16', _onclick=js('tab2', rowid)), _id="litab2_"+str(rowid)),
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
            "function n%(rid)s_load_user_groups(){sync_ajax('%(url)s', [], '%(id)s', function(){})}"%dict(
               id='tab2_'+str(rowid),
               rid=str(rowid),
               url=URL(r=request, c='ajax_user', f='ajax_user_groups',
                       args=['tab2_'+str(rowid)], vars={'username': request.vars.username})
            ),
            """callbacks = {"tab2": %(id)s_load_user_groups,
                           }"""%dict(id='n'+str(rowid)),
            js(tab, rowid),
            _name='%s_to_eval'%rowid,
          ),
        ),
      ),
    )
    return t

priv_groups = [
  "CheckExec",
  "CheckManager",
  "CheckRefresh",
  "CompExec",
  "CompManager",
  "DnsManager",
  "FormsManager",
  "Manager",
  "NetworkManager",
  "NodeManager",
  "ObsManager",
  "ProvisioningManager",
  "StorageExec",
  "StorageManager",
  "TagManager",
  "UserManager",
]

blist_groups = [
  "UnaffectedProjects",
]

@auth.requires_login()
def ajax_user_groups():
    id = request.args[0]
    username = request.vars.username

    q = db.v_users.fullname == username
    user = db(q).select(db.v_users.id).first()
    if user is None:
        return ""

    # group info cache
    o = db.auth_group.role
    q = ~db.auth_group.role.like("user_%")
    groups = db(q).select(orderby=o)

    ug = user_group_ids(user.id)

    manager = 'Manager' in user_groups()

    _org_groups = [g for g in groups if g.role not in blist_groups and g.role not in priv_groups]
    _priv_groups = [g for g in groups if g.role in priv_groups]

    def html_user_groups(groups):
        d = []
        for group in groups:
            if group.id in ug:
                memberof = True
            else:
                memberof = False
            attrs = dict(
              _type="checkbox",
              _disabled=not manager,
              _checked=memberof,
              _group_id=group.id,
              _user_id=user.id,
              _name='user_group_check',
            )
            _d = DIV(
                   INPUT(
                     **attrs
                   ),
                   DIV(
                     group.role,
                   ),
                   _class="user_group",
                 )
            d.append(_d)
        return DIV(d)

    d = DIV(
          H2(T("Organizational groups")),
          html_user_groups(_org_groups),
          DIV(_class="spacer"),
          H2(T("Privilege groups")),
          html_user_groups(_priv_groups),
        )
    return DIV(d, SCRIPT("bind_user_groups()"))

@service.json
def set_user_group():
    user_id = request.vars.user_id
    group_id = request.vars.group_id
    membership = request.vars.membership

    if 'Manager' not in user_groups():
        return {"err": "Not allowed"}
    if user_id is None:
        return {"err": "user id not specified"}
    if group_id is None:
        return {"err": "group id not specified"}

    q = db.auth_group.id == group_id
    g = db(q).select().first()
    if g is None:
        return {"err": "group id does not exist"}
    g = g.role

    q = db.v_users.id == user_id
    u = db(q).select(db.v_users.fullname).first()
    if u is None:
        return {"err": "user id does not exist"}
    u = u.fullname

    if membership == "true":
        db.auth_membership.insert(
          user_id=user_id,
          group_id=group_id
        )
        _log('users.group.attach',
             'attached group %(g)s to user %(u)s',
             dict(g=g, u=u))
    elif membership == "false":
        q = db.auth_membership.user_id == user_id
        q &= db.auth_membership.group_id == group_id
        db(q).delete()
        _log('users.group.detach',
             'detached group %(g)s from user %(u)s',
             dict(g=g, u=u))
    else:
        return {"err": "Unsupported membership target value"}

    return {}
