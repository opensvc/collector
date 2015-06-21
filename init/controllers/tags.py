def call():
    session.forget()
    return service()

@auth.requires_login()
@service.json
def create_and_add_tag():
    data = create_tag()
    if data["ret"] != 0:
        return data
    return add_tag()

@auth.requires_login()
@service.json
def create_tag():
    tag_name = request.vars.tag_name
    if tag_name is None:
        return {"ret": 1, "msg": "misformatted data (tag_name)"}
    q = db.tags.tag_name == tag_name
    rows = db(q).select()
    if len(rows) != 0:
        return {"ret": 0, "msg": "tag already exists"}

    db.tags.insert(
       tag_name=tag_name
    )
    _log("tag",
         "tag '%(tag_name)s' created",
         dict(tag_name=tag_name)
    )
    return {"ret": 0, "msg": "tag successfully created"}


@auth.requires_login()
@service.json
def add_tag():
    nodename = request.vars.nodename
    svcname = request.vars.svcname
    tag_name = request.vars.tag_name
    if nodename is None and svcname is None:
        return {"ret": 1, "msg": "misformatted data (nodename)"}
    if tag_name is None:
        return {"ret": 1, "msg": "misformatted data (tag_name)"}
    q = db.tags.tag_name == tag_name
    rows = db(q).select()
    if len(rows) == 0:
        return {"ret": 2, "msg": "This tag does not exist yet. Press enter again to create it."}
    tag_id = rows.first().id

    if svcname is not None:
        q = db.svc_tags.svcname == svcname
        q &= db.svc_tags.tag_id == tag_id
        rows = db(q).select()
        if len(rows) > 0:
            return {"ret": 3, "msg": "tag is already attached"}
        db.svc_tags.insert(
           svcname=svcname,
           tag_id=tag_id
        )
        _log("service.tag",
             "tag '%(tag_name)s' attached",
             dict(tag_name=tag_name),
             svcname=svcname)
    if nodename is not None:
        q = db.node_tags.nodename == nodename
        q &= db.node_tags.tag_id == tag_id
        rows = db(q).select()
        if len(rows) > 0:
            return {"ret": 3, "msg": "tag is already attached"}
        db.node_tags.insert(
           nodename=nodename,
           tag_id=tag_id
        )
        _log("node.tag",
             "tag '%(tag_name)s' attached",
             dict(tag_name=tag_name),
             nodename=nodename)
    return {"ret": 0, "tag_id": tag_id, "msg": "tag successfully attached"}

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


@auth.requires_login()
@auth.requires(auth.has_membership('Manager') or auth.has_membership('TagManager'))
@service.json
def del_tag():
    nodename = request.vars.nodename
    svcname = request.vars.svcname
    tag_id = request.vars.tag_id
    if nodename is None and svcname is None:
        return {"ret": 1, "msg": "misformatted data (nodename)"}
    if tag_id is None:
        return {"ret": 1, "msg": "misformatted data (tag_id)"}

    q = db.tags.id == tag_id
    rows = db(q).select()
    tag = rows.first()
    if tag is None:
        return {"ret": 1, "msg": "tag not found"}

    if svcname is not None:
        q = db.svc_tags.tag_id == tag_id
        q &= db.svc_tags.svcname == svcname
        rows = db(q).select()
        if len(rows) == 0:
            return {"ret": 0, "msg": "tag is already detached"}

        db(q).delete()
        _log("service.tag",
             "tag '%(tag_name)s' detached",
             dict(tag_name=tag.tag_name),
             svcname=svcname)
    if nodename is not None:
        q = db.node_tags.tag_id == tag_id
        q &= db.node_tags.nodename == nodename
        rows = db(q).select()
        if len(rows) == 0:
            return {"ret": 0, "msg": "tag is already detached"}

        db(q).delete()
        _log("node.tag",
             "tag '%(tag_name)s' detached",
             dict(tag_name=tag.tag_name),
             nodename=nodename)
    return {"ret": 0, "msg": "tag successfully detached"}

@auth.requires_login()
@service.json
def json_svc_tags(svcname):
    q = db.svc_tags.svcname == svcname
    q &= db.svc_tags.tag_id == db.tags.id
    rows = db(q).select(db.tags.id, db.tags.tag_name, db.tags.tag_exclude, orderby=db.tags.tag_name, cacheable=True)
    l = []
    for row in rows:
        l.append({"tag_name": row.tag_name.lower(), "tag_exclude": row.tag_exclude, "tag_id": row.id})
    return l

@auth.requires_login()
@service.json
def json_node_tags(nodename):
    q = db.node_tags.nodename == nodename
    q &= db.node_tags.tag_id == db.tags.id
    rows = db(q).select(db.tags.id, db.tags.tag_name, db.tags.tag_exclude, orderby=db.tags.tag_name, cacheable=True)
    l = []
    for row in rows:
        l.append({"tag_name": row.tag_name.lower(), "tag_exclude": row.tag_exclude, "tag_id": row.id})
    return l

@auth.requires_login()
@service.json
def list_svc_avail_tags(svcname, prefix):
    d = {}
    l = json_svc_tags(svcname)
    tag_ids = [r["tag_id"] for r in l]
    pattern = '|'.join([r["tag_exclude"] for r in l if r["tag_exclude"] is not None])

    q = ~db.tags.id.belongs(tag_ids)
    q &= db.tags.tag_name.like(prefix+"%")
    qx = _where(q, "tags", pattern, "tag_name")
    q &= ~qx
    rows = db(q).select(orderby=db.tags.tag_name)
    if len(rows) == 0:
        return []
    tags = [{"tag_name": r.tag_name.lower(), "tag_id": r.id} for r in rows]
    return tags

@auth.requires_login()
@service.json
def list_node_avail_tags(nodename, prefix):
    d = {}
    l = json_node_tags(nodename)
    tag_ids = [r["tag_id"] for r in l]
    pattern = '|'.join([r["tag_exclude"] for r in l if r["tag_exclude"] is not None])

    q = ~db.tags.id.belongs(tag_ids)
    q &= db.tags.tag_name.like(prefix+"%")
    qx = _where(q, "tags", pattern, "tag_name")
    q &= ~qx
    rows = db(q).select(orderby=db.tags.tag_name)
    if len(rows) == 0:
        return []
    tags = [{"tag_name": r.tag_name.lower(), "tag_id": r.id} for r in rows]
    return tags


#
# adm-tags view code
#

class table_tags(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['id',
                     'tag_name',
                     'tag_exclude',
                     'tag_created']
        self.colprops = {
            'tag_name': HtmlTableColumn(
                     title='Tag name',
                     table='tags',
                     field='tag_name',
                     img='tag16',
                     display=True,
                    ),
            'tag_created': HtmlTableColumn(
                     title='Tag created',
                     table='tags',
                     field='tag_created',
                     img='time16',
                     display=True,
                     _class='datetime',
                    ),
            'tag_exclude': HtmlTableColumn(
                     title='Tag exclude',
                     table='tags',
                     field='tag_exclude',
                     img='tag16',
                     display=True,
                     _class='tag_exclude',
                    ),
            'id': HtmlTableColumn(
                     title='Id',
                     table='tags',
                     field='id',
                     img='tag16',
                     display=False,
                    ),
        }
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
            self.additional_tools.append('t_tag_del')

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
              _class='floatw',
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
    t = DIV(
          t.html(),
          _id='tags',
        )
    return dict(table=t)

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
                     _class='datetime',
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
        self.checkbox_id_col = 'id'
        self.checkbox_id_table = 'v_tags_full'
        self.ajax_col_values = 'ajax_tagattach_col_values'
        self.span = ["tag_id"]
        self.keys = ["tag_id", "nodename", "svcname"]

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

@auth.requires_login()
def ajax_tagattach():
    t = table_tagattach('tagattach', 'ajax_tagattach')
    o = db.v_tags_full.tag_name | db.v_tags_full.nodename | db.v_tags_full.svcname

    q = db.v_tags_full.id >= 0
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)

    if len(request.args) == 1 and request.args[0] == 'csv':
        t.csv_q = q
        t.csv_orderby = o
        return t.csv()
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


