import os

#
# Domains
#
@auth.requires_membership('DnsManager')
def _domain_form(record=None):
    if record is not None:
        deletable = True
    else:
        deletable = False
    return SQLFORM(db.pdns_domains,
                 record=record,
                 deletable=deletable,
                 hidden_fields=['id'],
                 fields=[
                     'name',
                     'type'],
                 labels={
                     'name': 'Name',
                     'type': 'Type',
                 })

class table_dns_domains(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['id',
                     'name',
                     'master',
                     'last_check',
                     'type',
                     'notified_serial',
                     'account']
        self.colprops = {
            'id': HtmlTableColumn(
                     title='Domain Id',
                     field='id',
                     img='dns16',
                     display=True,
                    ),
            'name': HtmlTableColumn(
                     title='Name',
                     field='name',
                     img='dns16',
                     display=True,
                    ),
            'master': HtmlTableColumn(
                     title='Master',
                     field='master',
                     img='dns16',
                     display=False,
                    ),
            'last_check': HtmlTableColumn(
                     title='Last Check',
                     field='last_check',
                     img='time16',
                     display=False,
                    ),
            'type': HtmlTableColumn(
                     title='Type',
                     field='type',
                     img='dns16',
                     display=True,
                    ),
            'notified_serial': HtmlTableColumn(
                     title='Notified Serial',
                     field='notified_serial',
                     img='dns16',
                     display=True,
                    ),
            'account': HtmlTableColumn(
                     title='Account',
                     field='account',
                     img='guy16',
                     display=False,
                    ),
        }
        self.keys = ["id"]
        self.span = ["id"]
        self.dbfilterable = False
        self.ajax_col_values = 'ajax_dns_domains_col_values'
        self.extrarow = True
        self.checkboxes = True
        if 'DnsManager' in user_groups():
            self.additional_tools.append('domain_add')
            self.additional_tools.append('domain_del')

    def format_extrarow(self, o):
        id = self.extra_line_key(o)
        s = self.colprops['id'].get(o)
        d = DIV(
              A(
                IMG(
                  _src=URL(r=request, c='static', f='edit.png'),
                  _style='vertical-align:middle',
                ),
                _href=URL(r=request, c='dns', f='domain_edit',
                          vars={'domain_id':s,
                                '_next': URL(r=request)}
                      ),
              ),
              A(
                IMG(
                  _src=URL(r=request, c='static', f='action_sync_16.png'),
                  _style='vertical-align:middle',
                ),
                _href=URL(r=request, c='dns', f='domain_sync',
                          vars={'domain_id':s,
                                '_next': URL(r=request)}
                      ),
              ),
            )
        return d

    def domain_del(self):
        d = DIV(
              A(
                T("Delete domain"),
                _class='del16',
                _onclick="""if (confirm("%(text)s")){%(s)s};"""%dict(
                   s=self.ajax_submit(args=['domain_del']),
                   text=T("Deleting a domain also deletes all contained records. Please confirm domain deletion"),
                ),
              ),
              _class='floatw',
            )
        return d

    def domain_add(self):
        d = DIV(
              A(
                T("Add domain"),
                _class='add16',
                _onclick="""location.href='domain_add?_next=%s'"""%URL(r=request),
              ),
              _class='floatw',
            )
        return d

@auth.requires_login()
def domain_add():
    form = _domain_form()
    if form.accepts(request.vars):
        response.flash = T("edition recorded")
        _log('dns.domains.add',
             'added domain %(u)s',
             dict(u=request.vars.name))
        redirect(URL(r=request, f='dns'))
    elif form.errors:
        response.flash = T("errors in form")
    return dict(form=form)

@auth.requires_membership('DnsManager')
def domain_del(ids):
    q = db.pdns_domains.id.belongs(ids)
    #groups = user_groups()
    #if 'Manager' not in groups:
        # Manager+DnsManager can delete any domain
        # DnsManager can delete the domains they are responsible of
    #    q &= db.pdns_domains.team_responsible.belongs(groups)
    u = ', '.join([r.name for r in db(q).select(db.pdns_domains.name)])
    db(q).delete()
    _log('dns.domains.delete',
         'deleted domains %(u)s',
         dict(u=u))

@auth.requires_login()
def domain_sync():
    q = (db.pdns_domains.id>0)
    q &= _where(None, 'pdns_domains', request.vars.domain_id, 'id')
    rows = db(q).select()
    dname = rows[0].name

    q = db.pdns_records.name == dname
    q &= db.pdns_records.type == "SOA"
    rows = db(q).select()

    if len(rows) != 1:
        response.flash = "no single SOA found for domain %s"%dname
        redirect(URL(r=request, f='dns'))

    l = rows[0].content.split()

    if len(l) < 3:
        response.flash = "SOA has less than 3 fields found for domain %s"%dname
        redirect(URL(r=request, f='dns'))

    new = int(l[2]) + 1
    l[2] = str(new)
    db(q).update(content=' '.join(l))
    response.flash = "SOA incremented to %d for domain %s"%(new, dname)
    redirect(URL(r=request, f='dns'))

@auth.requires_login()
def domain_edit():
    query = (db.pdns_domains.id>0)
    query &= _where(None, 'pdns_domains', request.vars.domain_id, 'id')
    #groups = user_groups()
    #if 'Manager' not in groups:
        # Manager+DnsManager can edit any domain
        # DnsManager can edit the domains they are responsible of
    #    query &= db.pdns_domains.team_responsible.belongs(groups)
    rows = db(query).select()
    if len(rows) != 1:
        response.flash = "domain %d not found or insufficient privileges"%request.vars.domain_id
        return dict(form=None)
    record = rows[0]
    form = _domain_form(record)
    if form.accepts(request.vars):
        response.flash = T("edition recorded")
        _log('dns.domains.change',
             'edited domain %(u)s',
             dict(u=request.vars.name))
        redirect(URL(r=request, f='dns'))
    elif form.errors:
        response.flash = T("errors in form")
    return dict(form=form)


@auth.requires_login()
def ajax_dns_domains_col_values():
    t = table_dns_domains('dnsd', 'ajax_dns_domains')
    col = request.args[0]
    o = db.pdns_domains[col]
    q = db.pdns_domains.id > 0
    for f in set(t.cols):
        q = _where(q, 'pdns_domains', t.filter_parse(f), f)
    t.object_list = db(q).select(o, orderby=o)
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_dns_domains():
    t = table_dns_domains('dnsd', 'ajax_dns_domains')

    if len(request.args) >= 1:
        action = request.args[0]
        try:
            if action == 'domain_del':
                domain_del(t.get_checked())
        except ToolError, e:
            t.flash = str(e)

    o = ~db.pdns_domains.name
    q = db.pdns_domains.id > 0
    for f in set(t.cols):
        q = _where(q, 'pdns_domains', t.filter_parse(f), f)

    if len(request.args) == 1 and request.args[0] == 'line':
        if request.vars.volatile_filters is None:
            n = db(q).count()
            limitby = (t.pager_start,t.pager_end)
        else:
            n = 0
            limitby = (0, 500)
        t.object_list = db(q).select(orderby=o, limitby=limitby, cacheable=False)
        return t.table_lines_data(n)

    n = db(q).count()
    t.setup_pager(n)
    t.object_list = db(q).select(limitby=(t.pager_start,t.pager_end), orderby=o)

    return t.html()

#
# Records
#
class col_type(HtmlTableColumn):
    def html(self, o):
       d = self.get(o)
       if d in ["A", "PTR"]:
           return DIV(d, _class="boxed_small bgblack")
       elif d == "CNAME":
           return DIV(d, _class="boxed_small bggreen")
       else:
           return DIV(d, _class="boxed_small bgred")

@auth.requires_membership('DnsManager')
def _record_form(record=None):
    if record is not None:
        deletable = True
    else:
        deletable = False
    js = """if ($("#pdns_records_content").is(":visible")) {
            $("#pdns_records_content").hide();
            $("#pdns_records_content").parent().append("<div id=pdns_records_content_1>loading...</div>");
            $("#pdns_records_content").parent().append("<div id=pdns_records_content_2></div>");
            $("#pdns_records_content").parent().append("<div id=pdns_records_content_3></div>");
            function g() {
                $("#pdns_records_content_2 > select").change(function(){
                    $("#pdns_records_content").val($(this).val());
                    $("#pdns_records_content_3").text("%(pingmsg)s");
                    ajax("%(url3)s"+"/"+$(this).val(), [], "pdns_records_content_3");
                });
            };
            function f() {
                $("#pdns_records_content_1 > select").click(function(){
                    sync_ajax("%(url2)s"+"/"+$(this).val(), [], "pdns_records_content_2", g);
                });
            };
            sync_ajax("%(url1)s", [], "pdns_records_content_1", f);
            } else {
                $("#pdns_records_content").show();
                $("#pdns_records_content_1").remove();
                $("#pdns_records_content_2").remove();
            }
         """%dict(url1=URL(r=request, f="networks"),
                  url2=URL(r=request, f="ips"),
                  url3=URL(r=request, f="ping"),
                  pingmsg=T("testing ip ..."))
    return SQLFORM(db.pdns_records,
                 record=record,
                 deletable=deletable,
                 hidden_fields=['id'],
                 fields=[
                     'domain_id',
                     'name',
                     'type',
                     'content',
                     'ttl',
                     'prio'],
                 labels={
                     'domain_id': 'Domain Id',
                     'name': 'Name',
                     'type': 'Type',
                     'content': 'Content',
                     'ttl': 'Time to Live',
                     'prio': 'Priority',
                 },
                 col3={
                     'content': IMG(_src=URL(r=request, c='static', f='wizard16.png'), _onclick=js)
                 })

class table_dns_records(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['id',
                     'domain_id',
                     'name',
                     'type',
                     'content',
                     'ttl',
                     'prio',
                     'change_date']
        self.keys = ["id"]
        self.span = ["id"]
        self.colprops = {
            'id': HtmlTableColumn(
                     title='Record Id',
                     field='id',
                     img='dns16',
                     display=False,
                    ),
            'domain_id': HtmlTableColumn(
                     title='Domain Id',
                     field='domain_id',
                     img='dns16',
                     display=True,
                    ),
            'name': HtmlTableColumn(
                     title='Name',
                     field='name',
                     img='dns16',
                     display=True,
                    ),
            'type': col_type(
                     title='Type',
                     field='type',
                     img='dns16',
                     display=True,
                    ),
            'content': HtmlTableColumn(
                     title='Content',
                     field='content',
                     img='dns16',
                     display=True,
                    ),
            'ttl': HtmlTableColumn(
                     title='Time to Live',
                     field='ttl',
                     img='dns16',
                     display=True,
                    ),
            'prio': HtmlTableColumn(
                     title='Priority',
                     field='prio',
                     img='dns16',
                     display=True,
                    ),
            'change_date': HtmlTableColumn(
                     title='Last change',
                     field='change_date',
                     img='time16',
                     display=False,
                    ),
        }
        self.dbfilterable = False
        self.ajax_col_values = 'ajax_dns_records_col_values'
        self.extrarow = True
        self.checkboxes = True
        if 'DnsManager' in user_groups():
            self.additional_tools.append('record_add')
            self.additional_tools.append('record_del')

    def format_extrarow(self, o):
        id = self.extra_line_key(o)
        s = o['id']
        d = DIV(
              A(
                IMG(
                  _src=URL(r=request, c='static', f='edit.png'),
                  _style='vertical-align:middle',
                ),
                _href=URL(r=request, c='dns', f='record_edit',
                          vars={'record_id':s,
                                '_next': URL(r=request)}
                      ),
              ),
            )
        return d

    def record_del(self):
        d = DIV(
              A(
                T("Delete record"),
                _class='del16',
                _onclick="""if (confirm("%(text)s")){%(s)s};"""%dict(
                   s=self.ajax_submit(args=['record_del']),
                   text=T("Please confirm record deletion"),
                ),
              ),
              _class='floatw',
            )
        return d

    def record_add(self):
        d = DIV(
              A(
                T("Add record"),
                _class='add16',
                _onclick="""location.href='record_add?_next=%s'"""%URL(r=request),
              ),
              _class='floatw',
            )
        return d

def ptr_add():
    if request.vars.type != 'A':
        return
    request.vars.type = 'PTR'
    tmp = request.vars.content
    l = tmp.split('.')
    l.reverse()
    tmp = '.'.join(l)
    tmp += ".in-addr.arpa"
    request.vars.content = request.vars.name
    request.vars.name = tmp
    form = _record_form()
    if form.accepts(request.vars):
        response.flash = T("a and ptr recorded")
        _log('dns.records.add',
             'added record %(u)s',
             dict(u=request.vars.name))
    elif form.errors:
        response.flash = T("errors in ptr form")

@auth.requires_login()
def record_add():
    form = _record_form()
    if form.accepts(request.vars):
        response.flash = T("edition recorded")
        _log('dns.records.add',
             'added record %(u)s',
             dict(u=request.vars.name))
        ptr_add()
        redirect(URL(r=request, f='dns'))
    elif form.errors:
        response.flash = T("errors in form")
    return dict(form=form)

@auth.requires_membership('DnsManager')
def record_del(ids):
    q = db.pdns_records.id.belongs(ids)
    #groups = user_groups()
    #if 'Manager' not in groups:
        # Manager+DnsManager can delete any record
        # DnsManager can delete the records they are responsible of
    #    q &= db.pdns_records.team_responsible.belongs(groups)
    u = ', '.join([r.name for r in db(q).select(db.pdns_records.name)])
    db(q).delete()
    _log('dns.records.delete',
         'deleted records %(u)s',
         dict(u=u))

@auth.requires_login()
def record_edit():
    query = (db.pdns_records.id>0)
    query &= _where(None, 'pdns_records', request.vars.record_id, 'id')
    #groups = user_groups()
    #if 'Manager' not in groups:
        # Manager+DnsManager can edit any record
        # DnsManager can edit the records they are responsible of
    #    query &= db.pdns_records.team_responsible.belongs(groups)
    rows = db(query).select()
    if len(rows) != 1:
        response.flash = "record %d not found or insufficient privileges"%request.vars.record_id
        return dict(form=None)
    record = rows[0]
    form = _record_form(record)
    if form.accepts(request.vars):
        response.flash = T("edition recorded")
        _log('dns.records.change',
             'edited record %(u)s',
             dict(u=request.vars.name))
        redirect(URL(r=request, f='dns'))
    elif form.errors:
        response.flash = T("errors in form")
    return dict(form=form)


@auth.requires_login()
def ajax_dns_records_col_values():
    t = table_dns_records('dnsr', 'ajax_dns_records')
    col = request.args[0]
    o = db.pdns_records[col]
    q = db.pdns_records.id > 0
    for f in set(t.cols):
        q = _where(q, 'pdns_records', t.filter_parse(f), f)
    t.object_list = db(q).select(o, orderby=o)
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_dns_records():
    t = table_dns_records('dnsr', 'ajax_dns_records')

    if len(request.args) >= 1:
        action = request.args[0]
        try:
            if action == 'record_del':
                record_del(t.get_checked())
        except ToolError, e:
            t.flash = str(e)

    o = ~db.pdns_records.name
    q = db.pdns_records.id > 0
    for f in set(t.cols):
        q = _where(q, 'pdns_records', t.filter_parse(f), f)

    if len(request.args) == 1 and request.args[0] == 'line':
        if request.vars.volatile_filters is None:
            n = db(q).count()
            limitby = (t.pager_start,t.pager_end)
        else:
            n = 0
            limitby = (0, 500)
        t.object_list = db(q).select(orderby=o, limitby=limitby, cacheable=False)
        return t.table_lines_data(n)

    n = db(q).count()
    t.setup_pager(n)
    t.object_list = db(q).select(limitby=(t.pager_start,t.pager_end), orderby=o)

    return t.html()

@auth.requires_login()
def networks():
    rows = db(db.networks.id>0).select()
    l = map(lambda r: OPTION(r.name, " - ", "/".join((r.network, str(r.netmask))), _value=r.id), rows)
    return SELECT(l)

@auth.requires_login()
def ips():
    from socket import inet_ntoa
    from struct import pack
    network_id = request.args[0]
    sql = """select count(id) from network_segments where net_id=%s"""%network_id
    n_segs = db.executesql(sql)[0][0]

    sql = """select
               inet_aton(s.seg_begin),
               inet_aton(s.seg_end),
               s.seg_type
             from
               network_segments s,
               network_segment_responsibles sr,
               auth_group g
             where
               s.net_id = %s and
               s.id = sr.seg_id and
               sr.group_id = g.id and
               g.role in (%s)
             group by s.id
             order by inet_aton(seg_begin)
          """%(network_id, ','.join(map(lambda x: "'"+x+"'", user_groups())))
    rows = db.executesql(sql)
    ipl = []

    if n_segs > 0:
        if len(rows) == 0:
            return T("you are owner of no segment of this network")
        for row in rows:
            if row[2] == "dhcp":
                ipl += map(lambda x: [inet_ntoa(pack('>L', x)), T("dhcp")], range(row[0], row[1]))
            else:
                ipl += map(lambda x: [inet_ntoa(pack('>L', x)), ""], range(row[0], row[1]))
    else:
        sql = """select inet_aton(network), inet_aton(broadcast) from networks where id=%s"""%network_id
        rows = db.executesql(sql)
        if len(rows) == 0:
            return T("you are not owner of this network")
        ipl = map(lambda x: [inet_ntoa(pack('>l', x)), ""], range(rows[0][0], rows[0][1]))
    if len(ipl) == 0:
        return SPAN()
    sql = """select content from pdns_records where content in (%s)"""%','.join(map(lambda x: repr(x[0]), ipl))
    rows = db.executesql(sql)
    alloc_ips = map(lambda r: r[0], rows)
    for i, (ip, ip_type) in enumerate(ipl):
        if ip in alloc_ips:
           ipl[i][1] = T("allocated")
    l = map(lambda r: OPTION("%16s %s"%(r[0], r[1]), _value=r[0]), ipl)
    return SELECT(l, _id="pdns_records_content_select")

def is_exe(fpath):
    """Returns True if file path is executable, False otherwize
    does not follow symlink
    """
    return os.path.exists(fpath) and os.access(fpath, os.X_OK)

def which(program):
    def ext_candidates(fpath):
        yield fpath
        for ext in os.environ.get("PATHEXT", "").split(os.pathsep):
            yield fpath + ext

    fpath, fname = os.path.split(program)
    if fpath:
        if os.path.isfile(program) and is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            for candidate in ext_candidates(exe_file):
                if is_exe(candidate):
                    return candidate

    return None

@auth.requires_login()
def ping():
    if not which("fping"):
        return SPAN(T("fping not found. disable ip testing"))
    ip = request.args[0]
    import subprocess
    cmd = ['fping', ip]
    p = subprocess.Popen(cmd)
    out, err = p.communicate()
    if p.returncode == 0:
        return DIV(
                 T("ip is alive"),
                 _style="font-weight:bold;color:darkred",
               )
    return SPAN(T("ip is not alive"))

#
# Common
#
@auth.requires_login()
def dns():
    t = DIV(
          DIV(
            ajax_dns_domains(),
            _id='dnsd',
          ),
          DIV(
            ajax_dns_records(),
            _id='dnsr',
          ),
        )
    return dict(table=t)


