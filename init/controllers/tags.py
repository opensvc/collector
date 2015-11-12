def call():
    session.forget()
    return service()

@auth.requires_login()
@service.json
def tag_exclude():
    tag_exclude = request.vars.tag_exclude
    tag_id = request.vars.tag_id
    q = db.tags.id == tag_id
    db(q).update(tag_exclude=tag_exclude)
    _log("tag",
         "tag id '%(tag_id)d' exclude updated to %(tag_exclude)s",
         dict(tag_id=tag_id, tag_exclude=tag_exclude),
    )
    return {"ret": 0, "tag_id": tag_id, "msg": "tag exclude successfully updated"}

#
# adm-tags view code
#

class table_tags(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)

        # from models/colprops/
        self.cols = tags_cols
        self.colprops = tags_colprops

        self.dataable = True
        #self.extraline = True
        self.checkboxes = True
        self.checkbox_id_col = 'id'
        self.checkbox_id_table = 'tags'
        self.ajax_col_values = 'ajax_tags_col_values'
        self.span = ["id"]
        self.keys = ["id"]

        ug = user_groups()
        if 'Manager' in ug or 'TagManager' in ug:
	    self.form_tag_add = self.tag_add_sqlform()
            self += HtmlTableMenu('Tag', 'tag16', [
              't_tag_add',
              't_tag_del'
            ])

    @auth.requires_membership('CompManager')
    def tag_add_sqlform(self):
        f = SQLFORM(
                 db.tags,
                 labels={
                  'tag_name': T('Tag name'),
                  'tag_exclude': T('Tag exclusions')
                 },
                 _name='form_tag_add',
            )
        return f

    def t_tag_add(self):
        d = DIV(
              A(
                T("Add tag"),
                _class='add16',
                _onclick="""
                  click_toggle_vis(event,'%(div)s', 'block');
                """%dict(div='tag_add'),
              ),
              DIV(
                self.form_tag_add,
                _style='display:none',
                _class='white_float',
                _name='tag_add',
                _id='tag_add',
              ),
            )
        return d

    def t_tag_del(self):
        d = DIV(
              A(
                T("Delete tags"),
                _class='del16',
                _onclick="""if (confirm("%(text)s")){%(s)s};
                         """%dict(s=self.ajax_submit(args=['t_tag_del']),
                                  text=T("Deleting tags also deletes their attachments to nodes and services. Please confirm tags deletion"),
                                 ),
              ),
            )
        return d

@auth.requires(auth.has_membership('Manager') or auth.has_membership('TagManager'))
def t_tag_del(ids):
    q = db.tags.id.belongs(ids)
    u = ', '.join([r.tag_name for r in db(q).select(db.tags.tag_name) if r.tag_name is not None])
    db(db.node_tags.tag_id.belongs(ids)).delete()
    db(db.svc_tags.tag_id.belongs(ids)).delete()
    table_modified("node_tags")
    table_modified("svc_tags")
    db(q).delete()
    table_modified("tags")
    db.commit()
    _log('tag.delete',
         'deleted tags %(u)s',
         dict(u=u))

@auth.requires_login()
def ajax_tags_col_values():
    t = table_tags('tags', 'ajax_tags')
    col = request.args[0]
    o = db[t.colprops[col].table][col]
    q = db.tags.id > 0
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    t.object_list = db(q).select(o, orderby=o)
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_tags():
    t = table_tags('tags', 'ajax_tags')
    o = db.tags.tag_name

    if len(request.args) == 1:
        action = request.args[0]
        try:
            if action == 't_tag_del':
                t_tag_del(t.get_checked())
        except ToolError, e:
            t.flash = str(e)

    q = db.tags.id>0
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)

    if len(request.args) == 1 and request.args[0] == 'csv':
        t.csv_q = q
        t.csv_orderby = o
        return t.csv()
    if len(request.args) == 1 and request.args[0] == 'commonality':
        t.csv_q = q
        return t.do_commonality()
    if len(request.args) == 1 and request.args[0] == 'data':
        n = db(q).select(db.tags.id.count()).first()(db.tags.id.count())
        t.setup_pager(n)
        limitby = (t.pager_start,t.pager_end)
        cols = t.get_visible_columns()
        t.object_list = db(q).select(*cols, orderby=o, limitby=limitby, cacheable=False)
        return t.table_lines_data(n, html=False)

@auth.requires_login()
def tags():
    t = table_tags('tags', 'ajax_tags')

    try:
        if t.form_tag_add.accepts(request.vars, formname='add_tag'):
            _log("tag",
                 "tag '%(tag_name)s' created",
                 dict(tag_name=request.vars.tag_name)
            )
            table_modified("tags")
            redirect(URL(r=request))
        elif t.form_ruleset_add.errors:
            response.flash = T("errors in form")
    except AttributeError:
        pass
    except ToolError as e:
        t.flash = str(e)

    t = DIV(
          t.html(),
          _id='tags',
        )
    return dict(table=t)

def tags_load():
    return tags()["table"]

#
# view-tagattach view code
#

class table_tagattach(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['tag_id',
                     'tag_name',
                     'nodename',
                     'svcname',
                     'created']
        self.colprops = {
            'tag_id': HtmlTableColumn(
                     title='Tag id',
                     table='v_tags_full',
                     field='tag_id',
                     img='tag16',
                     display=False,
                    ),
            'tag_name': HtmlTableColumn(
                     title='Tag name',
                     table='v_tags_full',
                     field='tag_name',
                     img='tag16',
                     display=True,
                    ),
            'created': HtmlTableColumn(
                     title='Attach date',
                     table='v_tags_full',
                     field='created',
                     img='time16',
                     display=True,
                     _class='datetime_no_age',
                    ),
            'nodename': HtmlTableColumn(
                     title='Node',
                     table='v_tags_full',
                     field='nodename',
                     img='node16',
                     display=True,
                     _class='nodename',
                    ),
            'svcname': HtmlTableColumn(
                     title='Service',
                     table='v_tags_full',
                     field='svcname',
                     img='svc',
                     display=True,
                     _class='svcname',
                    ),
        }
        self.dataable = True
        #self.extraline = True
        self.checkboxes = True
        self.checkbox_id_col = 'ckid'
        self.checkbox_id_table = 'v_tags_full'
        self.ajax_col_values = 'ajax_tagattach_col_values'
        self.force_cols = ["ckid"]
        self.span = ["tag_id"]
        self.keys = ["tag_id", "nodename", "svcname"]
        if 'Manager' in ug or 'TagManager' in ug:
            self += HtmlTableMenu('Tags', 'tag16', [
              't_tag_attach',
              't_tag_detach'
            ])

    def t_tag_attach(self):
        label = 'Attach'
        action = 'tag_attach'
        divid = 'tag_attach'
        sid = 'tag_attach_s'
        o = db.tags.tag_name
        q = db.tags.id > 0
        options = [OPTION(g.tag_name, _value=g.id) for g in db(q).select(orderby=o, cacheable=True)]

        d = DIV(
              A(
                T(label),
                _class='attach16',
                _onclick="""
                  click_toggle_vis(event,'%(div)s', 'block');
                """%dict(div=divid),
              ),
              DIV(
                TABLE(
                  TR(
                    TH(T('Tag')),
                    TD(
                      SELECT(
                        *options,
                        **dict(_id=sid,
                               _requires=IS_IN_DB(db, 'tags.id'))
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
              ),
            )
        return d

    def t_tag_detach(self):
        d = DIV(
              A(
                T("Detach"),
                _class='detach16',
                _onclick=self.ajax_submit(args=['tag_detach']),
              ),
            )
        return d


@auth.requires_login()
def ajax_tagattach_col_values():
    t = table_tagattach('tagattach', 'ajax_tagattach')
    col = request.args[0]
    o = db[t.colprops[col].table][col]
    q = db.v_tags_full.id >= 0
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    t.object_list = db(q).select(o, orderby=o)
    return t.col_values_cloud_ungrouped(col)

@auth.requires(auth.has_membership('Manager') or auth.has_membership('TagManager'))
def tag_detach(ids):
    for id in ids:
        nodename, svcname, tag_id = id.split("_")
        tag_id = int(tag_id)
	try:
            if nodename == "null":
                lib_tag_detach_service(tag_id, svcname)
            if svcname == "null":
                lib_tag_detach_node(tag_id, nodename)
        except Exception as e:
	    response.flash = str(e)

@auth.requires(auth.has_membership('Manager') or auth.has_membership('TagManager'))
def tag_attach(tag_id, ids):
    for id in ids:
        nodename, svcname, dummy = id.split("_")
	try:
            if nodename == "null":
                lib_tag_attach_service(tag_id, svcname)
            if svcname == "null":
                lib_tag_attach_node(tag_id, nodename)
        except Exception as e:
	    response.flash = str(e)

@auth.requires_login()
def ajax_tagattach():
    t = table_tagattach('tagattach', 'ajax_tagattach')
    o = db.v_tags_full.tag_name | db.v_tags_full.nodename | db.v_tags_full.svcname

    q = db.v_tags_full.id >= 0
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)

    if len(request.args) == 1:
        action = request.args[0]
        try:
            if action == 'tag_attach':
                tag_attach(request.vars.tag_attach_s, t.get_checked())
            elif action == 'tag_detach':
                tag_detach(t.get_checked())
        except ToolError as e:
            t.flash = str(e)

    if len(request.args) == 1 and request.args[0] == 'csv':
        t.csv_q = q
        t.csv_orderby = o
        return t.csv()
    if len(request.args) == 1 and request.args[0] == 'commonality':
        t.csv_q = q
        return t.do_commonality()
    if len(request.args) == 1 and request.args[0] == 'data':
        n = db(q).select(db.v_tags_full.id.count()).first()(db.v_tags_full.id.count())
        t.setup_pager(n)
        limitby = (t.pager_start,t.pager_end)
        cols = t.get_visible_columns()
        t.object_list = db(q).select(*cols, orderby=o, limitby=limitby, cacheable=False)
        return t.table_lines_data(n, html=False)

@auth.requires_login()
def tagattach():
    t = table_tagattach('tagattach', 'ajax_tagattach')
    t = DIV(
          t.html(),
          _id='tagattach',
        )
    return dict(table=t)

def tagattach_load():
    return tagattach()["table"]

