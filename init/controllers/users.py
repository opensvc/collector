class col_users_domains(HtmlTableColumn):
    def html(self, o):
        s = self.get(o)
        if s == '':
            ss = '(no permission)'
        else:
            ss = s
        tid = 'd_t_%s'%o.id
        iid = 'd_i_%s'%o.id
        sid = 'd_s_%s'%o.id
        d = SPAN(
              SPAN(
                ss,
                _id=tid,
                _onclick="""hide_eid('%(tid)s');show_eid('%(sid)s');getElementById('%(iid)s').focus()"""%dict(tid=tid, sid=sid, iid=iid),
                _class="clickable",
              ),
              SPAN(
                INPUT(
                  value=s,
                  _id=iid,
                  _onkeypress="if (is_enter(event)) {%s};"%\
                     self.t.ajax_submit(additional_inputs=[iid],
                                        args="domain_set"),
                ),
                _id=sid,
                _style="display:none",
              ),
            )
        return d

class col_users_last(HtmlTableColumn):
    def html(self, o):
        return A(self.get(o),
                 _href=URL(r=request, c='log',f='log',
                           vars={'log_f_log_user':o.fullname}),
               )

class col_users_manager(HtmlTableColumn):
    def html(self, o):
        role = self.get(o)
        if role == 0:
            img = 'oneguy.png'
        else:
            img = 'admin.png'
        return IMG(_src=URL(r=request,c='static',f=img))

class table_users(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['manager',
                     'fullname',
                     'email',
                     'primary_group',
                     'groups',
                     'lock_filter',
                     'fset_name',
                     'domains',
                     'last']
        self.colprops = {
            'fullname': HtmlTableColumn(
                     title='Full name',
                     field='fullname',
                     img='guy16',
                     display=True,
                    ),
            'email': HtmlTableColumn(
                     title='Email',
                     field='email',
                     img='guy16',
                     display=True,
                    ),
            'primary_group': HtmlTableColumn(
                     title='Primary group',
                     field='primary_group',
                     img='guys16',
                     display=True,
                    ),
            'groups': HtmlTableColumn(
                     title='Groups',
                     field='groups',
                     img='guys16',
                     display=True,
                    ),
            'domains': col_users_domains(
                     title='Domains',
                     field='domains',
                     img='filter16',
                     display=True,
                    ),
            'manager': col_users_manager(
                     title='Role',
                     field='manager',
                     img='guy16',
                     display=True,
                    ),
            'lock_filter': HtmlTableColumn(
                     title='Lock filterset',
                     field='lock_filter',
                     img='attach16',
                     display=True,
                    ),
            'fset_name': HtmlTableColumn(
                     title='Filterset',
                     field='fset_name',
                     img='filter16',
                     display=True,
                    ),
            'last': col_users_last(
                     title='Last events',
                     field='last',
                     img='time16',
                     display=True,
                    ),
        }
        self.colprops['domains'].t = self
        self.ajax_col_values = 'ajax_users_col_values'
        self.dbfilterable = False
        self.checkboxes = True
        if 'Manager' in user_groups():
            self += HtmlTableMenu('Group', 'guys16', ['group_add', 'group_del', 'group_attach', 'group_detach', 'group_set_primary'])
            self += HtmlTableMenu('User', 'guy16', ['user_add', 'users_del', 'lock_filter', 'unlock_filter', 'set_filterset'])
            self.form_group_add = self.group_add_sqlform()
            self.form_user_add = self.user_add_sqlform()

    def group_add(self):
        d = DIV(
              A(
                T("Add"),
                _class='add16',
                _onclick="""
                  click_toggle_vis(event,'%(div)s', 'block');
                """%dict(div='group_add'),
              ),
              DIV(
                self.form_group_add,
                _style='display:none',
                _class='white_float',
                _name='group_add',
                _id='group_add',
              ),
            )
        return d

    def user_add(self):
        d = DIV(
              A(
                T("Add"),
                _class='add16',
                _onclick="""
                  click_toggle_vis(event,'%(div)s', 'block');
                """%dict(div='user_add'),
              ),
              DIV(
                self.form_user_add,
                _style='display:none',
                _class='white_float',
                _name='user_add',
                _id='user_add',
              ),
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
            )
        return d

    def set_filterset(self):
        q = db.gen_filtersets.id > 0
        o = db.gen_filtersets.fset_name
        options = [OPTION(T("None"),_value=0)]
        options += [OPTION(g.fset_name,_value=g.id) for g in db(q).select(orderby=o)]
        d = DIV(
              A(
                T("Set filterset"),
                _class='edit16',
                _onclick="""
                  click_toggle_vis(event,'set_filterset_div', 'block');
                """
              ),
              DIV(
                TABLE(
                  TR(
                    TH(T('Filterset')),
                    TD(
                      SELECT(
                        *options,
                        **dict(_id='fset_id')
                      ),
                    ),
                  ),
                  TR(
                    TH(),
                    TD(
                      INPUT(
                        _type='submit',
                        _onclick=self.ajax_submit(additional_inputs=['fset_id'],
                                                  args='set_filterset'),
                      ),
                    ),
                  ),
                ),
                _style='display:none',
                _class='white_float',
                _name='set_filterset_div',
                _id='set_filterset_div',
              ),
            )
        return d

    def group_detach(self):
        d = self.group_select_tool(label="Detach",
                                   action="group_detach",
                                   divid="group_detach",
                                   sid="group_detach_s",
                                   _class="attach16")
        return d

    def group_attach(self):
        d = self.group_select_tool(label="Attach",
                                   action="group_attach",
                                   divid="group_attach",
                                   sid="group_attach_s",
                                   _class="attach16")
        return d

    def group_set_primary(self):
        d = self.group_select_tool(label="Set primary group",
                                   action="group_set_primary",
                                   divid="group_set_primary",
                                   sid="group_set_primary_s",
                                   _class="wf16")
        return d

    def group_del(self):
        d = self.group_select_tool(label="Delete",
                                   action="group_del",
                                   divid="group_del",
                                   sid="group_del_s",
                                   _class="del16")
        return d

    def users_del(self):
        d = DIV(
              A(
                T("Delete"),
                _class='del16',
                _onclick="""if (confirm("%(text)s")){%(s)s};
                         """%dict(s=self.ajax_submit(args=['users_del']),
                                  text=T("Deleting a user also deletes its group membership. Please confirm user deletion"),
                                 ),
              ),
            )
        return d

    def lock_filter(self):
        d = DIV(
              A(
                T("Lock filterset"),
                _class='attach16',
                _onclick=self.ajax_submit(args=['lock_filter']),
              ),
            )
        return d

    def unlock_filter(self):
        d = DIV(
              A(
                T("Unlock filterset"),
                _class='detach16',
                _onclick=self.ajax_submit(args=['unlock_filter']),
              ),
            )
        return d

    @auth.requires_membership('Manager')
    def user_add_sqlform(self):
        f = SQLFORM(
                 db.auth_user,
                 labels={
                         'first_name': T('First name'),
                         'last_name': T('Last name'),
                         'email': T('Email'),
                        },
                 _name='form_user_add',
            )
        return f

    @auth.requires_membership('Manager')
    def group_add_sqlform(self):
        db.auth_group.description.readable = False
        db.auth_group.description.writable = False
        f = SQLFORM(
                 db.auth_group,
                 labels={
                         'role': T('Group name'),
                        },
                 _name='form_group_add',
            )
        return f


@auth.requires_login()
def ajax_users_col_values():
    t = table_users('users', 'ajax_users')
    col = request.args[0]
    o = db.v_users[col]
    q = db.v_users.id > 0
    t.object_list = db(q).select(orderby=o, groupby=o)
    for f in t.cols:
        q = _where(q, 'v_users', t.filter_parse(f), f)
    t.object_list = db(q).select(o, orderby=o, groupby=o)
    return t.col_values_cloud(col)

@auth.requires_membership('Manager')
def lock_filter(ids=[]):
    if len(ids) == 0:
        raise ToolError("no user selected")
    q = db.auth_user.id.belongs(ids)
    q &= db.auth_user.lock_filter == False
    rows = db(q).select()
    u = ', '.join([" ".join((r.first_name, r.last_name)) for r in rows])
    db(q).update(lock_filter=True)
    _log('users.filter.lock',
         'lock filter for users %(u)s',
         dict(u=u))

@auth.requires_membership('Manager')
def unlock_filter(ids=[]):
    if len(ids) == 0:
        raise ToolError("no user selected")
    q = db.auth_user.id.belongs(ids)
    q &= db.auth_user.lock_filter == True
    rows = db(q).select()
    u = ', '.join([" ".join((r.first_name, r.last_name)) for r in rows])
    db(q).update(lock_filter=False)
    _log('users.filter.unlock',
         'unlock filter for users %(u)s',
         dict(u=u))

@auth.requires_membership('Manager')
def set_filterset(ids=[]):
    if len(ids) == 0:
        raise ToolError("no user selected")
    fset_id = request.vars.fset_id

    q = db.auth_user.id.belongs(ids)
    rows = db(q).select()
    u = ', '.join([" ".join((r.first_name, r.last_name)) for r in rows])

    if fset_id == '0':
        q = db.gen_filterset_user.user_id.belongs(ids)
        db(q).delete()
        _log('users.filter.detach',
             'detach filter from users %(u)s',
             dict(u=u))
        return

    q = db.gen_filtersets.id == fset_id
    rows = db(q).select()
    if len(rows) != 1:
        raise ToolError("Filterset not found")
    fset_name = rows.first().fset_name

    for uid in ids:
        q = db.gen_filterset_user.user_id == uid
        if db(q).count() > 0:
            db(q).delete()
        db.gen_filterset_user.insert(user_id=uid, fset_id=fset_id)

    _log('users.filter.attach',
         'attach filter %(f)s to users %(u)s',
         dict(f=fset_name, u=u))

@auth.requires_membership('Manager')
def group_set_primary(ids=[]):
    if len(ids) == 0:
        raise ToolError("no user selected")
    gid = request.vars.group_set_primary_s

    done = []
    for id in ids:
        sql = """update auth_membership
                 set
                   primary_group = 'F'
                 where
                   user_id=%(user_id)s
              """ % dict(user_id=id)
        db.executesql(sql)

        sql = """insert into auth_membership
                 set
                   id=null,
                   user_id=%(user_id)s,
                   group_id=%(group_id)s,
                   primary_group='T'
                 on duplicate key update
                   user_id=%(user_id)s,
                   group_id=%(group_id)s,
                   primary_group='T'
              """ % dict(user_id=id, group_id=gid)
        db.executesql(sql)
        done.append(id)

    rows = db(db.v_users.id.belongs(done)).select(db.v_users.fullname)
    u = ', '.join([r.fullname for r in rows])
    g = db(db.auth_group.id==gid).select(db.auth_group.role)[0].role
    _log('users.group.attach',
         'attached primary group %(g)s to users %(u)s',
         dict(g=g, u=u))

@auth.requires_membership('Manager')
def group_attach(ids=[]):
    if len(ids) == 0:
        raise ToolError("no user selected")
    gid = request.vars.group_attach_s

    done = []
    for id in ids:
        q = db.auth_membership.user_id == id
        q &= db.auth_membership.group_id==gid
        if db(q).count() != 0:
            continue
        done.append(id)
        db.auth_membership.insert(user_id=id, group_id=gid)
    rows = db(db.v_users.id.belongs(done)).select(db.v_users.fullname)
    u = ', '.join([r.fullname for r in rows])
    g = db(db.auth_group.id==gid).select(db.auth_group.role)[0].role
    _log('users.group.attach',
         'attached group %(g)s to users %(u)s',
         dict(g=g, u=u))

@auth.requires_membership('Manager')
def group_detach(ids=[]):
    if len(ids) == 0:
        raise ToolError("no user selected")
    gid = request.vars.group_detach_s
    rows = db(db.v_users.id.belongs(ids)).select(db.v_users.fullname)
    u = ', '.join([r.fullname for r in rows])
    g = db(db.auth_group.id==gid).select(db.auth_group.role)[0].role

    q = db.auth_membership.user_id.belongs(ids)
    q &= db.auth_membership.group_id==gid
    db(q).delete()
    _log('users.group.detach',
         'detached group %(g)s from users %(u)s',
         dict(g=g, u=u))

@auth.requires_membership('Manager')
def group_del():
    gid = request.vars.group_del_s
    q = db.auth_group.id==gid
    g = db(q).select(db.auth_group.role)[0].role
    db(db.auth_membership.group_id==gid).delete()
    db(q).delete()
    _log('users.group.delete',
         'deleted group %(g)s',
         dict(g=g))

@auth.requires_membership('Manager')
def users_del(ids=[]):
    if len(ids) == 0:
        raise ToolError("no user selected")
    rows = db(db.v_users.id.belongs(ids)).select(db.v_users.fullname)
    x = ', '.join([r.fullname for r in rows])
    db(db.auth_user.id.belongs(ids)).delete()
    db(db.auth_membership.user_id.belongs(ids)).delete()
    _log('users.user.delete',
         'deleted users %(x)s',
         dict(x=x))

@auth.requires_membership('Manager')
def domain_set():
    l = [k for k in request.vars if 'd_i_' in k]
    if len(l) != 1:
        raise ToolError("one user must be selected")
    id = int(l[0].replace('d_i_',''))
    new = request.vars[l[0]]
    gid = auth.user_group(id)

    q = db.domain_permissions.group_id == gid
    rows = db(q).select(db.domain_permissions.id)
    n = len(rows)
    if n == 1:
        if new == '':
            db(q).delete()
        else:
            db(q).update(domains=new)
    elif n == 0:
        if new == '':
            raise ToolError("no domain specified")
        db.domain_permissions.insert(domains=new, group_id=gid)

    rows = db(db.v_users.id==id).select(db.v_users.fullname)
    x = ', '.join([r.fullname for r in rows])
    _log('users.user.change',
         'set domain %(d)s for user %(x)s',
         dict(x=x, d=new))

@auth.requires_login()
def ajax_users():
    t = table_users('users', 'ajax_users')

    if len(request.args) == 1:
        action = request.args[0]
        try:
            if action == 'domain_set':
                domain_set()
            elif action == 'group_del':
                group_del()
            elif action == 'users_del':
                users_del(t.get_checked())
            elif action == 'lock_filter':
                lock_filter(t.get_checked())
            elif action == 'unlock_filter':
                unlock_filter(t.get_checked())
            elif action == 'set_filterset':
                set_filterset(t.get_checked())
            elif action == 'group_set_primary':
                group_set_primary(t.get_checked())
            elif action == 'group_attach':
                group_attach(t.get_checked())
            elif action == 'group_detach':
                group_detach(t.get_checked())
        except ToolError, e:
            t.flash = str(e)

    try:
        if t.form_group_add.accepts(request.vars, formname='form_add_group'):
            response.flash = T("group added")
            # refresh forms comboboxes
            t.form_group_attach = t.group_attach_sqlform()
            t.form_group_set_primary = t.group_set_primary_sqlform()
            _log('users.group.add',
                 'added group %(u)s',
                 dict(u=request.vars.role))
        elif t.form_group_add.errors:
            response.flash = T("errors in form")

        if t.form_user_add.accepts(request.vars, formname='form_add_user'):
            response.flash = T("user added")
            # refresh forms comboboxes
            t.form_group_attach = t.group_attach_sqlform()
            t.form_group_set_primary = t.group_set_primary_sqlform()
            _log('users.user.add',
                 'added user %(u)s',
                 dict(u=' '.join((request.vars.first_name,
                                  request.vars.last_name))))
        elif t.form_user_add.errors:
            response.flash = T("errors in form")
    except AttributeError:
        pass

    o = ~db.v_users.last
    q = db.v_users.id > 0
    for f in t.cols:
        q = _where(q, 'v_users', t.filter_parse(f), f)
    n = db(q).count()
    t.setup_pager(n)
    t.object_list = db(q).select(limitby=(t.pager_start,t.pager_end), orderby=o)
    return t.html()

@auth.requires_login()
def users():
    t = DIV(
          ajax_users(),
          _id='users',
        )
    return dict(table=t)


