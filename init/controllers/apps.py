def refresh_b_apps():
    try:
        sql = "drop table if exists b_apps_new"
        db.executesql(sql)
        sql = "create table b_apps_new like b_apps"
        db.executesql(sql)
        sql = "insert into b_apps_new select * from v_apps"
        db.executesql(sql)
        sql = "drop table if exists b_apps_old"
        db.executesql(sql)
        sql = "rename table b_apps to b_apps_old, b_apps_new to b_apps"
        db.executesql(sql)
    except:
        sql = "drop table if exists b_apps"
        db.executesql(sql)
        sql = """CREATE TABLE `b_apps` (
  `id` int(11) NOT NULL DEFAULT '0',
  `app` varchar(64) CHARACTER SET latin1 NOT NULL,
  `roles` varchar(342) DEFAULT NULL,
  `responsibles` varchar(342) DEFAULT NULL,
  `mailto` varchar(342) DEFAULT NULL,
  KEY `i_app` (`app`)
)
"""
        db.executesql(sql)
        sql = "insert into b_apps select * from v_apps"
        db.executesql(sql)
    db.commit()


class table_apps(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['app',
                     'app_domain',
                     'app_team_ops',
                     'roles',
                     'responsibles',
                     'mailto']
        self.keys = ['app']
        self.span = ['app']
        self.colprops = {
            'app': HtmlTableColumn(
                     title='Application code',
                     table='v_apps',
                     field='app',
                     img='svc',
                     display=True,
                    ),
            'app_domain': HtmlTableColumn(
                     title='App domain',
                     table='v_apps',
                     field='app_domain',
                     img='svc',
                     display=True,
                    ),
            'app_team_ops': HtmlTableColumn(
                     title='Ops team',
                     table='v_apps',
                     field='app_team_ops',
                     img='guys16',
                     display=True,
                    ),
            'roles': HtmlTableColumn(
                     title='Sysresp teams',
                     table='v_apps',
                     field='roles',
                     img='guys16',
                     display=True,
                     _class="groups",
                    ),
            'responsibles': HtmlTableColumn(
                     title='System Responsibles',
                     table='v_apps',
                     field='responsibles',
                     img='guys16',
                     display=True,
                    ),
            'mailto': HtmlTableColumn(
                     title='Mailing list',
                     table='v_apps',
                     field='mailto',
                     img='guys16',
                     display=False,
                    ),
        }
        self.ajax_col_values = 'ajax_apps_col_values'
        #self.dbfilterable = True
        self.checkboxes = True
        self.checkbox_id_table = 'v_apps'
        self.checkbox_id_col = 'id'
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
        q = _where(q, 'v_apps', t.filter_parse(f), f)
    t.object_list = db(q).select(o, orderby=o)
    return t.col_values_cloud_ungrouped(col)

@auth.requires_membership('Manager')
def group_attach(ids=[]):
    if len(ids) == 0:
        raise ToolError("attach group failed: no app selected")
    gid = request.vars.group_attach_s

    attach_group_to_app(gid, ids)

@auth.requires_membership('Manager')
def group_detach(ids=[]):
    if len(ids) == 0:
        raise ToolError("detach group failed: no app selected")
    gid = request.vars.group_detach_s
    detach_group_from_app(gid, ids)

@auth.requires_membership('Manager')
def app_add():
    app = request.vars.app_add_i
    if len(app) == 0:
        raise ToolError("add application failed: application name is empty")
    q = db.apps.app==app
    if db(q).count() > 0:
        raise ToolError("add application failed: application already exists")
    db.apps.insert(app=app)
    table_modified("apps")
    db.commit()
    refresh_b_apps()
    _log('apps.app.add',
         'added app %(a)s',
         dict(a=app))

@auth.requires_membership('Manager')
def app_del(ids):
    q = db.apps.id.belongs(ids)
    u = ', '.join([r.app for r in db(q).select(db.apps.app) if r.app is not None])
    g = db(q).select(db.apps.app)[0].app
    db(db.apps_responsibles.app_id.belongs(ids)).delete()
    table_modified("apps_responsibles")
    db(q).delete()
    table_modified("apps")
    db.commit()
    refresh_b_apps()
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

    if len(request.args) == 1 and request.args[0] == 'line':
        if request.vars.volatile_filters is None:
            n = db(q).count()
            limitby = (t.pager_start,t.pager_end)
        else:
            n = 0
            limitby = (0, 500)
        t.object_list = db(q).select(orderby=o, groupby=o, limitby=limitby)
        return t.table_lines_data(n)

    n = db(q).count()
    t.setup_pager(n)
    t.object_list = db(q).select(limitby=(t.pager_start,t.pager_end),
                                 orderby=o, groupby=o)
    return t.html()

@auth.requires_login()
def apps():
    t = DIV(
          ajax_apps(),
          _id='apps',
        )
    return dict(table=t)


