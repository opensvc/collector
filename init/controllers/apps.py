class table_apps(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['app',
                     'roles',
                     'responsibles',
                     'mailto']
        self.colprops = {
            'app': HtmlTableColumn(
                     title='Application code',
                     field='app',
                     img='svc',
                     display=True,
                    ),
            'roles': HtmlTableColumn(
                     title='Responsible groups',
                     field='roles',
                     img='guys16',
                     display=True,
                    ),
            'responsibles': HtmlTableColumn(
                     title='Responsibles',
                     field='responsibles',
                     img='guys16',
                     display=True,
                    ),
            'mailto': HtmlTableColumn(
                     title='Mailing list',
                     field='mailto',
                     img='guys16',
                     display=True,
                    ),
        }
        self.ajax_col_values = 'ajax_apps_col_values'
        self.dbfilterable = True
        self.checkboxes = True
        if 'Manager' in user_groups():
            self.additional_tools.append('app_del')
            self.additional_tools.append('app_add')
            self.additional_tools.append('group_detach')
            self.additional_tools.append('group_attach')

    def app_add(self):
        label = 'Add application'
        action = 'app_add'
        divid = 'app_add_div'
        sid = 'app_add_i'
        o = db.v_apps.id > 0
        d = DIV(
              A(
                T(label),
                _class='add16',
                _onclick="""
                  click_toggle_vis(event,'%(div)s', 'block');
                """%dict(div=divid),
              ),
              DIV(
                TABLE(
                  TR(
                    TH(T('App')),
                    TD(
                      INPUT(
                        **dict(_id=sid,
                               _requires=IS_NOT_IN_DB(db, 'v_apps.app'))
                      ),
                    ),
                  ),
                  TR(
                    TH(),
                    TD(
                      INPUT(
                        _type='submit',
                        _onclick=self.ajax_submit(additional_inputs=[sid],
                                                  args=action),
                      ),
                    ),
                  ),
                ),
                _style='display:none',
                _class='white_float',
                _name=divid,
                _id=divid,
              ),
              _class='floatw',
            )
        return d

    def group_select_tool(self, label, action, divid, sid, _class=''):
        q = ~db.auth_group.role.like('user_%')
        o = db.auth_group.role
        options = [OPTION(g.role,_value=g.id) for g in db(q).select(orderby=o)]
        d = DIV(
              A(
                T(label),
                _class=_class,
                _onclick="""
                  click_toggle_vis(event,'%(div)s', 'block');
                """%dict(div=divid),
              ),
              DIV(
                TABLE(
                  TR(
                    TH(T('Group')),
                    TD(
                      SELECT(
                        *options,
                        **dict(_id=sid,
                               _requires=IS_IN_DB(db, 'auth_group.id'))
                      ),
                    ),
                  ),
                  TR(
                    TH(),
                    TD(
                      INPUT(
                        _type='submit',
                        _onclick=self.ajax_submit(additional_inputs=[sid],
                                                  args=action),
                      ),
                    ),
                  ),
                ),
                _style='display:none',
                _class='white_float',
                _name=divid,
                _id=divid,
              ),
              _class='floatw',
            )
        return d

    def group_detach(self):
        d = self.group_select_tool(label="Detach group",
                                   action="group_detach",
                                   divid="group_detach",
                                   sid="group_detach_s",
                                   _class="detach16")
        return d

    def group_attach(self):
        d = self.group_select_tool(label="Attach group",
                                   action="group_attach",
                                   divid="group_attach",
                                   sid="group_attach_s",
                                   _class="attach16")
        return d

    def app_del(self):
        d = DIV(
              A(
                T("Delete application"),
                _class='del16',
                _onclick="""if (confirm("%(text)s")){%(s)s};
                         """%dict(s=self.ajax_submit(args=['app_del']),
                                  text=T("Deleting an application code also deletes its group membership. Please confirm application deletion"),
                                 ),
              ),
              _class='floatw',
            )
        return d

@auth.requires_login()
def ajax_apps_col_values():
    t = table_apps('apps', 'ajax_apps')
    col = request.args[0]
    o = db.v_apps[col]
    q = db.v_apps.id > 0
    t.object_list = db(q).select(orderby=o, groupby=o)
    for f in t.cols:
        q = _where(q, 'v_users', t.filter_parse(f), f)
    q = apply_db_filters(q, 'v_apps')
    t.object_list = db(q).select(orderby=o, groupby=o)
    return t.col_values_cloud(col)

@auth.requires_membership('Manager')
def group_attach(ids=[]):
    if len(ids) == 0:
        raise ToolError("attach group failed: no app selected")
    gid = request.vars.group_attach_s

    done = []
    for id in ids:
        q = db.apps_responsibles.app_id == id
        q &= db.apps_responsibles.group_id==gid
        if db(q).count() != 0:
            continue
        done.append(id)
        db.apps_responsibles.insert(app_id=id, group_id=gid)
    rows = db(db.apps_responsibles.id.belongs(done)).select(db.v_apps.app)
    u = ', '.join([r.app for r in rows])
    g = db(db.auth_group.id==gid).select(db.auth_group.role)[0].role
    _log('apps.group.attach',
         'attached group %(g)s to apps %(u)s',
         dict(g=g, u=u))

@auth.requires_membership('Manager')
def group_detach(ids=[]):
    if len(ids) == 0:
        raise ToolError("detach group failed: no app selected")
    gid = request.vars.group_detach_s
    rows = db(db.v_apps.id.belongs(ids)).select(db.v_apps.app)
    u = ', '.join([r.app for r in rows])
    g = db(db.auth_group.id==gid).select(db.auth_group.role)[0].role

    q = db.apps_responsibles.app_id.belongs(ids)
    q &= db.apps_responsibles.group_id==gid
    db(q).delete()
    _log('apps.group.detach',
         'detached group %(g)s from app %(u)s',
         dict(g=g, u=u))

@auth.requires_membership('Manager')
def app_add():
    app = request.vars.app_add_i
    if len(app) == 0:
        raise ToolError("add application failed: application name is empty")
    q = db.apps.app==app
    if db(q).count() > 0:
        raise ToolError("add application failed: application already exists")
    db.apps.insert(app=app)
    _log('apps.app.add',
         'added app %(a)s',
         dict(a=app))

@auth.requires_membership('Manager')
def app_del(ids):
    q = db.apps.id.belongs(ids)
    u = ', '.join([r.app for r in db(q).select(db.apps.app)])
    g = db(q).select(db.apps.app)[0].app
    db(db.apps_responsibles.app_id.belongs(ids)).delete()
    db(q).delete()
    _log('apps.app.delete',
         'deleted apps %(u)s',
         dict(u=u))

@auth.requires_login()
def ajax_apps():
    t = table_apps('apps', 'ajax_apps')

    if len(request.args) == 1:
        action = request.args[0]
        try:
            if action == 'app_del':
                app_del(t.get_checked())
            elif action == 'app_add':
                app_add()
            elif action == 'group_attach':
                group_attach(t.get_checked())
            elif action == 'group_detach':
                group_detach(t.get_checked())
        except ToolError, e:
            t.flash = str(e)

    o = ~db.v_apps.app
    q = db.v_apps.id > 0
    for f in t.cols:
        q = _where(q, 'v_apps', t.filter_parse(f), f)
    n = db(q).count()
    t.setup_pager(n)
    t.object_list = db(q).select(limitby=(t.pager_start,t.pager_end), orderby=o)
    return t.html()

@auth.requires_login()
def apps():
    t = DIV(
          ajax_apps(),
          _id='apps',
        )
    return dict(table=t)


