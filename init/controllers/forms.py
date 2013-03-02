import re
import os
import yaml

class col_forms_yaml(HtmlTableColumn):
    def html(self, o):
        val = self.get(o)
        val = re.sub(r'(%\(\w+\)s)', r'<span class=syntax_red>\1</span>', val)
        val = re.sub(r'(\w+:)', r'<span class=syntax_green>\1</span>', val)
        return PRE(XML(val))

class table_forms(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['form_name',
                     'form_type',
                     'form_folder',
                     'form_team_responsible',
                     'form_team_publication',
                     'form_yaml',
                     'form_created',
                     'form_author']
        self.colprops = {
            'form_name': HtmlTableColumn(
                title = 'Name',
                field = 'form_name',
                display = True,
                table = 'v_forms',
                img = 'prov'
            ),
            'form_team_publication': HtmlTableColumn(
                title = 'Team publication',
                field = 'form_team_publication',
                display = True,
                table = 'v_forms',
                img = 'guys16'
            ),
            'form_team_responsible': HtmlTableColumn(
                title = 'Team responsible',
                field = 'form_team_responsible',
                display = True,
                table = 'v_forms',
                img = 'guys16'
            ),
            'form_type': col_forms_yaml(
                title = 'Type',
                field = 'form_type',
                display = True,
                table = 'v_forms',
                img = 'edit16'
            ),
            'form_folder': HtmlTableColumn(
                title = 'Folder',
                field = 'form_folder',
                display = True,
                table = 'v_forms',
                img = 'hd16'
            ),
            'form_yaml': col_forms_yaml(
                title = 'Definition',
                field = 'form_yaml',
                display = True,
                table = 'v_forms',
                img = 'action16'
            ),
            'form_created': HtmlTableColumn(
                title = 'Created on',
                field = 'form_created',
                display = False,
                table = 'v_forms',
                img = 'time16'
            ),
            'form_author': HtmlTableColumn(
                title = 'Author',
                field = 'form_author',
                display = False,
                table = 'v_forms',
                img = 'guy16'
            ),
        }
        self.ajax_col_values = 'ajax_forms_admin_col_values'
        self.dbfilterable = False
        self.checkboxes = True
        self.extrarow = True

        if 'FormsManager' in user_groups():
            self.additional_tools.append('add_forms')
            self += HtmlTableMenu('Team responsible', 'guys16', ['team_responsible_attach', 'team_responsible_detach'])
            self += HtmlTableMenu('Team publication', 'guys16', ['team_publication_attach', 'team_publication_detach'])


    def format_extrarow(self, o):
        d = DIV(
              A(
                _href=URL(r=request, c='forms', f='forms_editor', vars={'form_id': o.id}),
                _class="edit16",
              ),
            )
        return d

    def team_responsible_attach(self):
        d = self.team_responsible_select_tool(label="Attach",
                                              action="team_responsible_attach",
                                              divid="team_responsible_attach",
                                              sid="team_responsible_attach_s",
                                              _class="attach16")
        return d

    def team_responsible_detach(self):
        d = self.team_responsible_select_tool(label="Detach",
                                              action="team_responsible_detach",
                                              divid="team_responsible_detach",
                                              sid="team_responsible_detach_s",
                                              _class="detach16")
        return d

    def team_publication_attach(self):
        d = self.team_publication_select_tool(label="Attach",
                                              action="team_publication_attach",
                                              divid="team_publication_attach",
                                              sid="team_publication_attach_s",
                                              _class="attach16")
        return d

    def team_publication_detach(self):
        d = self.team_publication_select_tool(label="Detach",
                                              action="team_publication_detach",
                                              divid="team_publication_detach",
                                              sid="team_publication_detach_s",
                                              _class="detach16")
        return d

    def add_forms(self):
        d = DIV(
              A(
                T("Add forms"),
                _href=URL(r=request, f='forms_editor'),
                _class='add16',
              ),
              _class='floatw',
            )
        return d

    def team_responsible_select_tool(self, label, action, divid, sid, _class=''):
        if 'Manager' not in user_groups():
            s = """and role in (
                     select g.role from
                       auth_group g
                       join auth_membership gm on g.id=gm.group_id
                       join auth_user u on gm.user_id=u.id
                     where
                       u.id=%d
                  )"""%auth.user_id
        else:
            s = ""
        sql = """ select id, role
                  from auth_group
                  where
                    role not like "user_%%" and
                    privilege = 'F'
                    %s
                  group by role order by role
        """%s
        rows = db.executesql(sql)
        options = [OPTION(g[1],_value=g[0]) for g in rows]

        q = db.auth_membership.user_id == auth.user_id
        q &= db.auth_group.id == db.auth_membership.group_id
        q &= db.auth_group.role.like('user_%')
        options += [OPTION(g.auth_group.role,_value=g.auth_group.id) for g in db(q).select()]
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
                    TH(T('Team')),
                    TD(
                      SELECT(
                        *options,
                        **dict(_id=sid)
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

    def team_publication_select_tool(self, label, action, divid, sid, _class=''):
        sql = """ select id, role
                  from auth_group
                  where
                    role not like "user_%%" and
                    privilege = 'F'
                  group by role order by role
        """
        rows = db.executesql(sql)
        options = [OPTION(g[1],_value=g[0]) for g in rows]

        q = db.auth_membership.user_id == auth.user_id
        q &= db.auth_group.id == db.auth_membership.group_id
        q &= db.auth_group.role.like('user_%')
        options += [OPTION(g.auth_group.role,_value=g.auth_group.id) for g in db(q).select()]
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
                    TH(T('Team')),
                    TD(
                      SELECT(
                        *options,
                        **dict(_id=sid)
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

@auth.requires_membership('FormsManager')
def team_responsible_attach(ids=[]):
    if len(ids) == 0:
        raise ToolError("no form selected")
    group_id = request.vars.team_responsible_attach_s

    done = []
    for id in ids:
        if 'Manager' not in user_groups():
            q = db.forms_team_responsible.form_id == id
            q &= db.form_team_responsible.group_id.belongs(user_group_ids())
            if db(q).count() == 0:
                continue
        q = db.forms_team_responsible.form_id == id
        q &= db.forms_team_responsible.group_id == group_id
        if db(q).count() != 0:
            continue
        done.append(id)
        db.forms_team_responsible.insert(form_id=id, group_id=group_id)
    if len(done) == 0:
        return
    rows = db(db.forms.id.belongs(done)).select(db.forms.form_name)
    u = ', '.join([r.form_name for r in rows])
    _log('form.group.attach',
         'attached group %(g)s to forms %(u)s',
         dict(g=group_role(group_id), u=u))

@auth.requires_membership('CompManager')
def team_responsible_detach(ids=[]):
    if len(ids) == 0:
        raise ToolError("no form selected")
    group_id = request.vars.team_responsible_detach_s

    done = []
    for id in ids:
        q = db.forms_team_responsible.form_id == id
        q &= db.forms_team_responsible.group_id == group_id
        if 'Manager' not in user_groups():
            q &= db.forms_team_responsible.group_id.belongs(user_group_ids())
        if db(q).count() == 0:
            continue
        done.append(id)
        db(q).delete()
    if len(done) == 0:
        return
    rows = db(db.forms.id.belongs(done)).select(db.forms.form_name)
    u = ', '.join([r.form_name for r in rows])
    _log('form.group.detach',
         'detached group %(g)s from forms %(u)s',
         dict(g=group_role(group_id), u=u))

@auth.requires_membership('FormsManager')
def team_publication_attach(ids=[]):
    if len(ids) == 0:
        raise ToolError("no form selected")
    group_id = request.vars.team_publication_attach_s

    done = []
    for id in ids:
        if 'Manager' not in user_groups():
            q = db.forms_team_publication.form_id == id
            q &= db.form_team_publication.group_id.belongs(user_group_ids())
            if db(q).count() == 0:
                continue
        q = db.forms_team_publication.form_id == id
        q &= db.forms_team_publication.group_id == group_id
        if db(q).count() != 0:
            continue
        done.append(id)
        db.forms_team_publication.insert(form_id=id, group_id=group_id)
    if len(done) == 0:
        return
    rows = db(db.forms.id.belongs(done)).select(db.forms.form_name)
    u = ', '.join([r.form_name for r in rows])
    _log('form.group.attach',
         'attached group %(g)s to forms %(u)s',
         dict(g=group_role(group_id), u=u))

@auth.requires_membership('CompManager')
def team_publication_detach(ids=[]):
    if len(ids) == 0:
        raise ToolError("no form selected")
    group_id = request.vars.team_publication_detach_s

    done = []
    for id in ids:
        q = db.forms_team_publication.form_id == id
        q &= db.forms_team_publication.group_id == group_id
        if 'Manager' not in user_groups():
            q &= db.forms_team_publication.group_id.belongs(user_group_ids())
        if db(q).count() == 0:
            continue
        done.append(id)
        db(q).delete()
    if len(done) == 0:
        return
    rows = db(db.forms.id.belongs(done)).select(db.forms.form_name)
    u = ', '.join([r.form_name for r in rows])
    _log('form.group.detach',
         'detached group %(g)s from forms %(u)s',
         dict(g=group_role(group_id), u=u))

@auth.requires_membership('FormsManager')
def forms_editor():
    q = db.forms.id == request.vars.form_id
    rows = db(q).select()

    if len(rows) == 1:
        record = rows[0]
        if 'Manager' not in user_groups():
            q &= db.forms.id == db.forms_team_responsible.form_id
            q &= db.forms_team_responsible.group_id.belongs(user_group_ids())
            rows = db(q).select()
            if len(rows) == 0:
                session.flash = T("You are not allowed to edit this form")
                redirect(URL(r=request, c='forms', f='forms_admin'))
    else:
        record = None

    db.forms.form_author.default = user_name()
    form = SQLFORM(db.forms,
                 record=record,
                 deletable=True,
                 fields=['form_name',
                         'form_folder',
                         'form_type',
                         'form_yaml',],
                 labels={'form_name': T('Form name'),
                         'form_folder': T('Form folder'),
                         'form_type': T('Form type'),
                         'form_yaml': T('Form yaml definition')}
                )
    if form.accepts(request.vars):
        if request.vars.form_id is None:
            _log('compliance.form.add',
                 "Created '%(form_type)s' form '%(form_name)s' with definition:\n%(form_yaml)s",
                     dict(form_name=request.vars.form_name,
                          form_type=request.vars.form_type,
                          form_yaml=request.vars.form_yaml))
            add_default_team_responsible(request.vars.form_name)
            add_default_team_publication(request.vars.form_name)
        elif request.vars.delete_this_record == 'on':
            _log('compliance.form.delete',
                 "Deleted '%(form_type)s' form '%(form_name)s' with definition:\n%(form_yaml)s",
                     dict(form_name=request.vars.form_name,
                          form_type=request.vars.form_type,
                          form_yaml=request.vars.form_yaml))
        else:
            _log('compliance.form.change',
                 "Changed '%(form_type)s' form '%(form_name)s' with definition:\n%(form_yaml)s",
                     dict(form_name=request.vars.form_name,
                          form_type=request.vars.form_type,
                          form_yaml=request.vars.form_yaml))

        session.flash = T("Form recorded")
        redirect(URL(r=request, c='forms', f='forms_admin'))
    elif form.errors:
        response.flash = T("errors in form")
    return dict(form=form)

def add_default_team_responsible(form_name):
    q = db.forms.form_name == form_name
    form_id = db(q).select()[0].id
    q = db.auth_membership.user_id == auth.user_id
    q &= db.auth_membership.group_id == db.auth_group.id
    q &= db.auth_group.role.like('user_%')
    try:
        group_id = db(q).select()[0].auth_group.id
    except:
        q = db.auth_group.role == 'Manager'
        group_id = db(q).select()[0].id
    db.forms_team_responsible.insert(form_id=form_id, group_id=group_id)

def add_default_team_publication(form_name):
    q = db.forms.form_name == form_name
    form_id = db(q).select()[0].id
    q = db.auth_membership.user_id == auth.user_id
    q &= db.auth_membership.group_id == db.auth_group.id
    q &= db.auth_group.role.like('user_%')
    try:
        group_id = db(q).select()[0].auth_group.id
    except:
        q = db.auth_group.role == 'Manager'
        group_id = db(q).select()[0].id
    db.forms_team_publication.insert(form_id=form_id, group_id=group_id)

@auth.requires_login()
def ajax_forms_admin_col_values():
    t = table_forms('forms', 'ajax_forms_admin')

    col = request.args[0]
    o = db.v_forms[col]
    q = db.v_forms.id > 0
    for f in t.cols:
        q = _where(q, 'v_forms', t.filter_parse(f), f)
    t.object_list = db(q).select(o, orderby=o, groupby=o)
    return t.col_values_cloud(col)

@auth.requires_login()
def ajax_forms_admin():
    t = table_forms('forms', 'ajax_forms_admin')

    if len(request.args) == 1:
        action = request.args[0]
        try:
            if action == 'team_responsible_attach':
                team_responsible_attach(t.get_checked())
            elif action == 'team_responsible_detach':
                team_responsible_detach(t.get_checked())
            elif action == 'team_publication_attach':
                team_publication_attach(t.get_checked())
            elif action == 'team_publication_detach':
                team_publication_detach(t.get_checked())
        except ToolError, e:
            v.flash = str(e)

    o = db.v_forms.form_name
    q = db.v_forms.id > 0
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    n = db(q).count()
    t.setup_pager(n)
    t.object_list = db(q).select(limitby=(t.pager_start,t.pager_end), orderby=o)
    return t.html()

@auth.requires_login()
def forms_admin():
    t = DIV(
          ajax_forms_admin(),
          _id='forms',
        )
    return dict(table=t)

def get_folders_info():
    h = {}
    for id, form_name, form_folder, data in get_forms("folder"):
        if 'Folder' not in data:
            continue
        if 'FolderCss' not in data:
            data['FolderCss'] = 'folder48'
        if 'FolderDesc' not in data:
            data['FolderCss'] = ''
        h[data['Folder']] = data
    return data

def get_forms(form_type=None, folder="/", form_names=[]):
    if len(form_names) > 0:
        q = db.forms.form_name.belongs(form_names)
    else:
        q = db.forms.form_folder == folder

    if form_type != "folder":
        q &= db.forms.id == db.forms_team_publication.form_id
        q &= db.forms_team_publication.group_id.belongs(user_group_ids())

    if form_type is None:
        pass
    elif type(form_type) == list:
        q &= db.forms.form_type.belongs(form_type)
    else:
        q &= db.forms.form_type == form_type

    rows = db(q).select(db.forms.id,
                        db.forms.form_name,
                        db.forms.form_folder,
                        db.forms.form_yaml,
                        orderby=db.forms.form_type|db.forms.form_name,
                        groupby=db.forms.id)
    l = []
    for row in rows:
        try:
            data = yaml.load(row.form_yaml)
            if data is None:
                data = {}
        except:
            data = {}
        l.append((row.id, row.form_name, row.form_folder, data))
    return l

@auth.requires_login()
def ajax_forms_list():
    return forms_list(request.vars.folder, prev_wfid=request.vars.prev_wfid)

@auth.requires_login()
def folder_list(folder="/"):
    l = []
    folders = get_forms("folder", folder=folder)
    if folder != "/":
        parent_folder = '/'.join(folder.split('/')[:-1])
        if not parent_folder.startswith('/'):
            parent_folder = '/'+parent_folder
        parent_data = {
          'FolderName': '',
          'FolderCss': 'parent48',
          'FolderLabel': 'Parent folder',
          'FolderDesc': parent_folder,
        }
        parent = ('parent', 'parent', parent_folder, parent_data)
        folders = [parent] + folders

    for id, form_name, form_folder, data in folders:
        cl = data.get('FolderCss', 'folder48')
        desc = data.get('FolderDesc', '')
        folderlabel = data.get('FolderLabel', form_name)
        l.append(DIV(
          DIV(
            P(folderlabel),
            P(desc, _style="font-style:italic;padding-left:1em"),
            _style="padding-top:1em;padding-bottom:1em;",
            _class=cl,
          ),
          _onclick="""
sync_ajax('%(url)s', [], '%(id)s', function(){});
"""%dict(
                id="forms_list",
                url=URL(
                  r=request, c='forms', f='ajax_forms_list',
                  vars={
                    "folder": os.path.join(form_folder, data.get('FolderName')),
                  }
                ),
),
          _class="formentry",
        ),
      )
    return l

@auth.requires_login()
def forms_list(folder="/", form_names=[], prev_wfid=None):
    l = []

    folder = os.path.realpath(folder)

    if len(form_names) == 0:
        l += folder_list(folder)

    for id, form_name, form_folder, data in get_forms(["custo", "generic"], folder=folder, form_names=form_names):
        cl = data.get('Css', 'nologo48')
        desc = data.get('Desc', '')
        if desc is None: desc = ''
        if 'Label' in data:
            label = data['Label']
        else:
            label = form_name
        l.append(DIV(
          DIV(
            P(label),
            P(desc, _style="font-style:italic;padding-left:1em"),
            _style="padding-top:1em;padding-bottom:1em;",
            _class=cl,
          ),
          _onclick="""
$(this).siblings().toggle()
$("#forms_inputs").each(function(){
  $(this).text('');
  $(this).slideToggle(400);
})
$('[name=radio_form]').each(function(){
  if ($(this).attr("id")=='%(rid)s'){return};
  $(this).prop('checked', false)
});
$("#%(id)s").html('%(spinner)s');
sync_ajax('%(url)s', [], '%(id)s', function(){});
"""%dict(
                spinner=IMG(_src=URL(r=request,c='static',f='spinner.gif')).xml(),
                id="forms_inputs",
                rid=id,
                url=URL(
                  r=request, c='compliance', f='ajax_forms_inputs',
                  vars={
                    "form_id": id,
                    "hid": "forms_inputs",
                    "prev_wfid": prev_wfid,
                  }
                ),
              ),
          _class="formentry",
        ),
      )
    d = DIV(
          DIV(
            l,
            _style="margin:1em;display:inline-block;vertical-align:top;text-align:left",
          ),
          DIV(
            _id="forms_inputs",
            _style="padding-top:3em;display:none",
          ),
        )
    return d

@auth.requires_login()
def forms():
    d = DIV(
      H1(T("Choose a customization form")),
      DIV(forms_list(), _id="forms_list"),
    )
    return dict(table=d)

def stored_form_show(wfid, _class=""):
    hid = "wf_%s"%wfid
    q = db.forms_store.id == wfid
    q &= db.forms_store.form_md5 == db.forms_revisions.form_md5
    wf = db(q).select().first()
    form = yaml.load(wf.forms_revisions.form_yaml)

    if len(wf.forms_store.form_assignee) > 0:
        assignee = T("Assigned to %(assignee)s", dict(assignee=wf.forms_store.form_assignee))
    else:
        assignee = ""

    return DIV(
      DIV(
        H2(form.get('Label')),
        I(
          T("Submitted by %(submitter)s on %(date)s", dict(submitter=wf.forms_store.form_submitter, date=wf.forms_store.form_submit_date)),
          BR(),
          assignee,
        ),
        _class=form.get('Css', ''),
      ),
      DIV(
        _id=hid,
        _style="padding:0.5em",
      ),
      SCRIPT(
        """sync_ajax("%(url)s", {}, "%(id)s", function(){})"""%dict(
          url=URL(c="compliance", f="ajax_forms_inputs", vars={
            "wfid": wfid,
            "form_xid": hid,
            "hid": hid,
            "mode": "showdetailed",
            "showexpert": True,
          }),
          id=hid,
        ),
      ),
      _class=_class,
    )

@auth.requires_login()
def forms_chain(wfid, folded=False, highlight_step=True):
    l = []
    id = wfid

    if highlight_step:
        cl = "forms highlight_forms"
    else:
        cl = "forms"
    data = stored_form_show(id, _class=cl)
    l.append(data)

    while id is not None:
        q = db.forms_store.form_next_id == id
        wf = db(q).select(db.forms_store.id).first()
        if wf is None:
            break
        id = wf.id
        data = stored_form_show(id, _class="forms")
        l.append(data)

    l.reverse()

    id = wfid
    while id is not None:
        q = db.forms_store.form_prev_id == id
        wf = db(q).select(db.forms_store.id).first()
        if wf is None:
            break
        id = wf.id
        data = stored_form_show(id, _class="forms")
        l.append(data)

    _l = []
    down = DIV(
      XML("&nbsp;"),
      _class="down16",
      _style="width:16px",
    )

    s = """$(this).find(".foldme").toggle(400)"""

    if len(l) > 2:
        fold = True
    else:
        fold = False

    for i, e in enumerate(l):
        cl = ""
        if i > 0 and i < len(l) - 1:
            cl = "foldme"
            if folded:
                cl += " hidden"
        _l.append(DIV(e, _class=cl))
        _l.append(DIV(down))

    if len(_l) > 0:
        _l.pop()

    return DIV(_l, _onclick=s)

@auth.requires_login()
def workflow():
    wfid = request.vars.wfid

    q = db.forms_store.id == wfid
    q &= db.forms_revisions.form_md5 == db.forms_store.form_md5
    wf = db(q).select().first()

    if wf is None:
        return T("Workflow form id %(wfid)s not found", dict(wfid=wfid))

    form_names = None
    form = yaml.load(wf.forms_revisions.form_yaml)

    if wf.forms_store.form_next_id is not None:
        _forms_list = T("This workflow step is already completed")
    elif wf.forms_store.form_assignee != user_name() and \
         wf.forms_store.form_assignee not in user_groups():
        _forms_list = T("This workflow is not assigned to you or your group")
    else:
        for output in form.get("Outputs", []):
            form_names = output.get("NextForms")
            if form_names is not None:
                break

        if form_names is None:
            _forms_list = T("This Workflow step has no successor")
        else:
            _forms_list = forms_list(form_names=form_names, prev_wfid=wfid)

    d = DIV(
      H1(T("Workflow")),
      DIV(forms_chain(wfid)),
      DIV(_class="spacer"),
      H1(T("Next steps")),
      DIV(_forms_list, _id="forms_list"),
    )
    return dict(table=d)


@auth.requires_login()
def ajax_node_list():
    o = db.nodes.project | db.nodes.nodename
    q = db.nodes.id > 0
    if 'Manager' not in user_groups():
        q &= db.apps_responsibles.app_id == db.apps.id
        q &= db.apps_responsibles.group_id == db.auth_membership.group_id
        q &= db.auth_membership.user_id == auth.user_id
        q &= db.auth_membership.group_id == db.auth_group.id
        q &= db.nodes.team_responsible == db.auth_group.role
    nodes = db(q).select(db.nodes.nodename,
                         db.nodes.project,
                         groupby=o,
                         orderby=o)

    l = [OPTION(T("Choose one"))]
    for n in nodes:
        o = OPTION(
                "%s - %s"%(str(n.project).upper(), str(n.nodename).lower()),
                _value=n.nodename
            )
        l.append(o)

    return DIV(
             H3(T("Node")),
             SELECT(
               l,
               _id="nodename",
               _onchange="""
$("#stage2").html('%(spinner)s');
ajax('%(url)s/%(objtype)s/'+this.options[this.selectedIndex].value, [], '%(div)s');
"""%dict(
      url=URL(
            r=request, c='compliance',
            f='ajax_custo',
          ),
      objtype='nodename',
      div="stage2",
      spinner=IMG(_src=URL(r=request,c='static',f='spinner.gif')).xml(),
    ),
             ),
             SCRIPT("""
$("select").combobox();
$("#nodename").siblings("input").focus();
""", _name="stage1_to_eval"),
           )

@auth.requires_login()
def ajax_service_list():
    o = db.services.svc_app | db.services.svc_name
    q = db.services.svc_app == db.apps.app
    q &= db.services.svc_name == db.svcmon.mon_svcname
    if 'Manager' not in user_groups():
        q &= db.apps_responsibles.app_id == db.apps.id
        q &= db.apps_responsibles.group_id == db.auth_membership.group_id
        q &= db.auth_membership.user_id == auth.user_id
    services = db(q).select(db.services.svc_name,
                            db.services.svc_app,
                            groupby=o,
                            orderby=o)

    l = [OPTION(T("Choose one"))]
    for s in services:
        o = OPTION(
                "%s - %s"%(str(s.svc_app).upper(), str(s.svc_name).lower()),
                _value=s.svc_name
            )
        l.append(o)

    return DIV(
             H3(T("Service")),
             SELECT(
               l,
               _id="svcname",
               _onchange="""
$("#stage2").html('%(spinner)s');
ajax('%(url)s/%(objtype)s/'+this.options[this.selectedIndex].value, [], '%(div)s');
"""%dict(
      url=URL(
            r=request, c='compliance',
            f='ajax_custo',
          ),
      objtype='svcname',
      div="stage2",
      spinner=IMG(_src=URL(r=request,c='static',f='spinner.gif')).xml(),
    ),

             ),
             SCRIPT("""
$("select").combobox();
$("#svcname").siblings("input").focus();
""", _name="stage1_to_eval"),
           )


def format_forms_chain(l):
    _l = []
    for wf in l:
        data = forms_chain(wf.id, folded=False, highlight_step=False)
        d = DIV(
          A(
            data,
            _href=URL(c='forms', f='workflow', vars={'wfid': wf.id}),
          ),
          _class="wfentry",
        )
        _l.append(d)
    return _l

@auth.requires_login()
def workflows_assigned_to_me():
    q = db.forms_store.form_next_id == None
    q1 = db.forms_store.form_assignee.belongs(user_groups())
    q1 |= db.forms_store.form_assignee == user_name()
    q &= q1
    rows = db(q).select(orderby=db.forms_store.form_submit_date)

    _l = format_forms_chain(rows)

    if len(_l) == 0:
        return dict(table=DIV(T("You currently have no assigned workflow"), _style="padding:2em"))

    d = DIV(
      H1(T("Workflows assigned to me")),
      SPAN(_l),
    )
    return dict(table=d)

@auth.requires_login()
def workflows_pending_tiers_action():
    # all my workflows
    q = db.forms_store.form_submitter == user_name()
    q &= db.forms_store.form_prev_id == None
    rows = db(q).select(db.forms_store.id)
    ids = map(lambda x: x.id, rows)

    # only those pending tiers action
    q = db.forms_store.form_head_id.belongs(ids)
    q &= db.forms_store.form_next_id == None
    q &= ~db.forms_store.form_assignee.belongs(user_groups())
    q &= db.forms_store.form_assignee != user_name()
    rows = db(q).select(orderby=db.forms_store.form_submit_date)

    _l = format_forms_chain(rows)

    if len(_l) == 0:
        return dict(table=DIV(T("None of your workflow are pending tiers action"), _style="padding:2em"))

    d = DIV(
      H1(T("Workflows pending tiers action")),
      SPAN(_l),
    )
    return dict(table=d)

@auth.requires_login()
def get_node_portnames():
    if len(request.args) != 1:
        return ""
    q = db.nodes.team_responsible.belongs(user_groups())
    q &= db.node_hba.nodename == db.nodes.nodename
    q &= db.node_hba.nodename == request.args[0]
    rows = db(q).select(db.node_hba.hba_id,
                        orderby=db.node_hba.hba_id,
                        groupby=db.node_hba.hba_id)
    return PRE('\n'.join([r.hba_id for r in rows]))

@auth.requires_login()
def get_service_portnames():
    if len(request.args) != 1:
        return ""
    q = db.apps_responsibles.group_id.belongs(user_group_ids())
    q &= db.apps_responsibles.app_id == db.apps.id
    q &= db.apps.app == db.services.svc_app
    q &= db.svcmon.mon_svcname == db.services.svc_name
    q &= db.services.svc_name == request.args[0]
    q &= db.node_hba.nodename == db.svcmon.mon_nodname
    rows = db(q).select(db.node_hba.hba_id,
                        orderby=db.node_hba.hba_id,
                        groupby=db.node_hba.hba_id)
    return PRE('\n'.join([r.hba_id for r in rows]))

@auth.requires_login()
def get_service_nodes():
    if len(request.args) != 1:
        return ""
    q = db.apps_responsibles.group_id.belongs(user_group_ids())
    q &= db.apps_responsibles.app_id == db.apps.id
    q &= db.apps.app == db.services.svc_app
    q &= db.svcmon.mon_svcname == db.services.svc_name
    q &= db.svcmon.mon_svcname == request.args[0]
    rows = db(q).select(db.svcmon.mon_nodname,
                        orderby=db.svcmon.mon_nodname,
                        groupby=db.svcmon.mon_nodname)
    return PRE('\n'.join([r.mon_nodname for r in rows]))

@auth.requires_login()
def get_node_generic(col):
    if len(request.args) != 1:
        return ""
    q = db.v_nodes.team_responsible.belongs(user_groups())
    q &= db.v_nodes.nodename == request.args[0]
    node = db(q).select().first()
    if node is None:
        return T("node not found")
    return node[col]

@auth.requires_login()
def get_node_environnement():
    return get_node_generic("environnement")

@auth.requires_login()
def get_node_os_concat():
    return get_node_generic("os_concat")

@auth.requires_login()
def get_node_loc_city():
    return get_node_generic("loc_city")

