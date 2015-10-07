import re

class col_tpl_command(HtmlTableColumn):
    def html(self, o):
        val = self.get(o)
        val = val.replace('--resource', '<br>&nbsp;&nbsp;<span class=syntax_blue>--resource</span>')
        val = re.sub(r'(%\(\w+\)s)', r'<span class=syntax_red>\1</span>', val)
        val = re.sub(r'("\w+":)', r'<span class=syntax_green>\1</span>', val)
        return TT(XML(val))

class table_templates(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['tpl_name',
                     'tpl_command',
                     'tpl_comment',
                     'tpl_created',
                     'tpl_author']
        self.keys = ['tpl_name']
        self.span = ['tpl_name']
        self.colprops = {
            'tpl_name': HtmlTableColumn(
                title = 'Name',
                field = 'tpl_name',
                display = True,
                table = 'prov_templates',
                img = 'prov'
            ),
            'tpl_command': col_tpl_command(
                title = 'Command',
                field = 'tpl_command',
                display = True,
                table = 'prov_templates',
                img = 'action16'
            ),
            'tpl_comment': HtmlTableColumn(
                title = 'Comment',
                field = 'tpl_comment',
                display = True,
                table = 'prov_templates',
                img = 'edit16'
            ),
            'tpl_created': HtmlTableColumn(
                title = 'Created on',
                field = 'tpl_created',
                display = False,
                table = 'prov_templates',
                img = 'time16'
            ),
            'tpl_author': HtmlTableColumn(
                title = 'Author',
                field = 'tpl_author',
                display = False,
                table = 'prov_templates',
                img = 'guy16'
            ),
        }
        self.ajax_col_values = 'ajax_prov_admin_col_values'
        self.dbfilterable = False
        self.checkboxes = False
        self.extrarow = True

        if 'ProvisioningManager' in user_groups():
            self.additional_tools.append('add_template')

    def format_extrarow(self, o):
        d = DIV(
              A(
                '',
                _href=URL(r=request, c='provisioning', f='prov_editor', vars={'tpl_id': o.id}),
                _class="edit16",
              ),
            )
        return d

    def add_template(self):
        d = DIV(
              A(
                T("Add template"),
                _href=URL(r=request, f='prov_editor'),
                _class='add16',
              ),
              _class='floatw',
            )
        return d

@auth.requires_login()
def prov_editor():
    q = (db.prov_templates.id==request.vars.tpl_id)
    rows = db(q).select()
    if len(rows) == 1:
        record = rows[0]
    else:
        record = None

    db.prov_templates.tpl_author.default = user_name()
    form = SQLFORM(db.prov_templates,
                 record=record,
                 fields=['tpl_name',
                         'tpl_command',
                         'tpl_comment'],
                 labels={'tpl_name': T('Template name'),
                         'tpl_command': T('Provisioning command'),
                         'tpl_comment': T('Template comment')},
                )
    if form.accepts(request.vars):
        session.flash = T("template recorded")
        redirect(URL(r=request, c='provisioning', f='prov_admin'))
    elif form.errors:
        response.flash = T("errors in form")
    return dict(form=form)

@auth.requires_login()
def ajax_prov_admin():
    t = table_templates('templates', 'ajax_prov_admin')

    o = db.prov_templates.tpl_name > 0
    q = db.prov_templates.id > 0
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)

    if len(request.args) == 1 and request.args[0] == 'line':
        n = db(q).count()
        limitby = (t.pager_start,t.pager_end)
        t.object_list = db(q).select(orderby=o, limitby=limitby)
        return t.table_lines_data(n)

    n = db(q).count()
    t.setup_pager(n)
    t.object_list = db(q).select(limitby=(t.pager_start,t.pager_end), orderby=o)
    return t.html()

@auth.requires_login()
def prov_admin():
    t = DIV(
          ajax_prov_admin(),
          _id='templates',
        )
    return dict(table=t)

@auth.requires_login()
def prov_list():
    q = db.prov_templates.id > 0
    rows = db(q).select()
    l = []
    for row in rows:
        l.append(TR(
          TD(
            INPUT(
              _value=False,
              _type='radio',
              _id=row.id,
              _onclick="""$(this).parents("table").find("[type=radio]:checked").each(function(){$(this).prop("checked", false)});$(this).prop("checked", true);ajax('%(url)s', [], '%(id)s')"""%dict(
                id="prov_inputs",
                url=URL(r=request, c='provisioning', f='ajax_prov_inputs', args=[row.id]),
              ),
            ),
          ),
          TD(
            row.tpl_name,
          ),
          TD(
            row.tpl_comment,
          ),
        ))
    d = DIV(
          TABLE(l),
          DIV(
            _id="prov_inputs",
          ),
        )
    return d

def ajax_prov_inputs():
    tpl_id = request.args[0]
    q = db.prov_templates.id == tpl_id
    tpl = db(q).select().first()
    keys = set(re.findall("%\(\w+\)s", tpl.tpl_command))-set(['%(node)s'])
    keys = map(lambda x: x.replace('%(','').replace(')s',''), keys)
    keys = ['node'] + sorted(list(keys))
    ids = ','.join(map(lambda x: "'prov_"+x+"'", keys))
    l = []
    for key in keys:
        l.append(TR(
                   TD(key),
                   TD(
                     INPUT(
                       _id='prov_'+key,
                       _name='prov_input',
                     ),
                   ),
                 ))
    return TABLE(
             l,
             TR(
               TD(
                 INPUT(
                   _type="submit",
                   _onclick="sync_ajax('%(url)s', [%(ids)s], 'prov_container', function(){})"%dict(
                     ids=ids,
                     url=URL(r=request, c='provisioning', f='ajax_provision', args=[tpl_id]),
                   ),
                 ),
               ),
               TD(
                 INPUT(
                   _type="submit",
                   _value=T("Show command"),
                   _onclick="sync_ajax('%(url)s', [%(ids)s], 'prov_container', function(){})"%dict(
                     ids=ids,
                     url=URL(r=request, c='provisioning', f='ajax_provision', args=[tpl_id, "showcommand"]),
                   ),
                 ),
               ),
             ),
           )

def ajax_provision():
    tpl_id = request.args[0]
    if len(request.args) == 2 and request.args[1] == "showcommand":
        showcommand = True
    else:
        showcommand = False
    q = db.prov_templates.id == tpl_id
    tpl = db(q).select().first()
    import re
    command = tpl.tpl_command

    for k,v in request.vars.items():
        if not k.startswith('prov_'):
            continue
        key = k.replace('prov_', '')
        command = re.sub('%\('+key+'\)s', v, command)

    if 'prov_node' not in request.vars:
        return T("node is mandatory")

    if showcommand:
        return command

    prov_enqueue(request.vars.prov_node, command)
    request.flash = T("Provisioning queued")
    return prov_list()

def prov_enqueue(node, command):
    #command = command.replace("'", "\\'").replace('"', '\\"')
    cmd = 'ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 -o ForwardX11=no -o PasswordAuthentication=no opensvc@'+node+' -- sudo '+command
    purge_action_queue()
    db.action_queue.insert(
      nodename=node,
      command=cmd,
      user_id=auth.user_id
    )
    from subprocess import Popen
    import sys
    actiond = 'applications'+str(URL(r=request,c='actiond',f='actiond.py'))
    process = Popen([sys.executable, actiond])
    process.communicate()
    _log('service.provision', 'provision service on node %(node)s with command %(command)s', dict(
          node=node,
          command=command))
    action_q_event()


