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

def prov_admin_load():
    return prov_admin()["table"]

