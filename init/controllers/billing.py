class table_billing(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = []
        self.colprops = {}
        self.dbfilterable = True
        self.headers = False
        self.filterable = False
        self.refreshable = False
        self.pageable = False
        self.exportable = True
        self.columnable = False
        self.object_list = []
        self.nodatabanner = False

@auth.requires_login()
def ajax_billing():
    t = table_billing('billing', 'ajax_billing')

    fset_id = user_fset_id()

    q = db.stat_day_billing.id > 0
    q &= db.stat_day_billing.fset_id == fset_id
    t.csv_q = q
    if len(request.args) == 1 and request.args[0] == 'csv':
        return t.csv()

    rows = db(q).select()

    table = DIV(
     t.html(),
     billing_fmt(t.html()),
     _id="billing",
    )
    return table

def name_fmt(a, b):
    a = a.replace('-','_')
    b = b.replace('-','_')
    return '_'.join((a, b))

def num_fmt(n, k, os, token, _class=""):
    return A(
             n if token[k][os]>0 else '',
             _href="#%s"%name_fmt(k,os),
             _onclick="""
              $("#%s").effect("highlight", {}, 3000)
             """%name_fmt(k,os),
             _class=_class,
           )

def billing_fmt(table):
    data, billing, token = billing_data()

    lines = []
    for os in data['os']:
        if data['ostotal'][os]['svc'] == 0 and data['ostotal'][os]['agents_without_svc'] == 0:
            continue
        line = [TD(os)]
        for k in ('svc_prd', 'agents_without_svc_prd', 'svc_nonprd', 'agents_without_svc_nonprd'):
            line.append(TD(num_fmt(len(data[k][os]), k, os, token), _class="numeric"))
            line.append(TD(num_fmt(billing[k][os], k, os, token, "lighter"), _class="numeric"))
            line.append(TD(num_fmt(token[k][os], k, os, token), _class="numeric"))
        line.append(TD(data['ostotal'][os]['svc'] if data['ostotal'][os]['svc']>0 else '', _class="numeric"))
        line.append(TD(token['ostotal'][os]['svc'] if token['ostotal'][os]['svc']>0 else '', _class="numeric"))
        line.append(TD(data['ostotal'][os]['agents_without_svc'] if data['ostotal'][os]['agents_without_svc']>0 else '', _class="numeric"))
        line.append(TD(token['ostotal'][os]['agents_without_svc'] if token['ostotal'][os]['agents_without_svc']>0 else '', _class="numeric"))
        lines.append(TR(line))

    lines.append(TR(
      TH("Total"),
      TD(data['total']['svc_prd'] if data['total']['svc_prd']>0 else '', _class="numeric"),
      TD(),
      TD(token['total']['svc_prd'] if token['total']['svc_prd']>0 else '', _class="numeric"),
      TD(data['total']['agents_without_svc_prd'] if data['total']['agents_without_svc_prd']>0 else '', _class="numeric"),
      TD(),
      TD(token['total']['agents_without_svc_prd'] if token['total']['agents_without_svc_prd']>0 else '', _class="numeric"),
      TD(data['total']['svc_nonprd'] if data['total']['svc_nonprd']>0 else '', _class="numeric"),
      TD(),
      TD(token['total']['svc_nonprd'] if token['total']['svc_nonprd']>0 else '', _class="numeric"),
      TD(data['total']['agents_without_svc_nonprd'] if data['total']['agents_without_svc_nonprd']>0 else '', _class="numeric"),
      TD(),
      TD(token['total']['agents_without_svc_nonprd'] if token['total']['agents_without_svc_nonprd']>0 else '', _class="numeric"),
      TD(data['total']['svc'], _class="numeric"),
      TD(token['total']['svc'], _class="numeric"),
      TD(data['total']['agents_without_svc'], _class="numeric"),
      TD(token['total']['agents_without_svc'], _class="numeric"),
    ))

    t = TABLE(
          TR(
            TH("OS Name", _rowspan=3, _class="head1"),
            TH("PRD", _colspan=6, _class="head1"),
            TH("Non PRD", _colspan=6, _class="head1"),
            TH("Total", _colspan=4, _class="head1"),
          ),
          TR(
            TH("Services", _colspan=3, _class="head2"),
            TH("Agents without services", _colspan=3, _class="head2"),
            TH("Services", _colspan=3, _class="head2"),
            TH("Agents without services", _colspan=3, _class="head2"),
            TH("Services", _colspan=2, _class="head2"),
            TH("Agents without services", _colspan=2, _class="head2"),
          ),
          TR(
            TH("Count", _class="head3"),
            TH("Tokens/Unit", _class="head3"),
            TH("Tokens", _class="head3"),
            TH("Count", _class="head3"),
            TH("Tokens/Unit", _class="head3"),
            TH("Tokens", _class="head3"),
            TH("Count", _class="head3"),
            TH("Tokens/Unit", _class="head3"),
            TH("Tokens", _class="head3"),
            TH("Count", _class="head3"),
            TH("Tokens/Unit", _class="head3"),
            TH("Tokens", _class="head3"),
            TH("Count", _class="head3"),
            TH("Tokens", _class="head3"),
            TH("Count", _class="head3"),
            TH("Tokens", _class="head3"),
          ),
          lines,
          _class="billing",
        )

    headings = {
      'svc_prd': 'PRD Services',
      'svc_nonprd': 'Non PRD Services',
      'agents_without_svc_prd': 'PRD Agents without services',
      'agents_without_svc_nonprd': 'Non PRD Agents without services',
    }
    details = []

    for k in ('svc_prd', 'agents_without_svc_prd', 'svc_nonprd', 'agents_without_svc_nonprd'):
        for os in data[k]:
            if len(data[k][os]) == 0:
                continue
            l = []
            for o in data[k][os]:
                l.append(SPAN(o.lower()+" "))
            details.append(SPAN(
              A(_name=name_fmt(k,os)),
              H2(headings[k]+" : "+os),
              SPAN(l),
              _id=name_fmt(k,os),
            ))

    summary = DIV(
      H2(T("Accounting")),
      SPAN(T("%(n)d tokens", dict(n=token['total']['svc']+token['total']['agents_without_svc']))),
      _style="text-align:left", _class="billing"
    )

    d = DIV(
      summary,
      BR(),
      DIV(H2(T("Detailled Accounting")), _style="text-align:left", _class="billing"),
      t,
      BR(),
      DIV(details, _style="text-align:left", _class="billing")
    )
    return d


@auth.requires_membership('Manager')
def billing_data():
    data = {}
    billing = {}
    token = {}

    # get effective os list
    q = db.nodes.os_name != ""
    rows = db(q).select(db.nodes.os_name, groupby=db.nodes.os_name, orderby=db.nodes.os_name)
    data['os'] = [r.os_name for r in rows]

    # nodes with services
    q = db.svcmon.id > 0
    rows = db(q).select(db.svcmon.mon_nodname, groupby=db.svcmon.mon_nodname)
    data['agents_with_svc'] = [r.mon_nodname for r in rows]


    # nodes with opensvc and no services
    q = db.packages.id > 0
    rows = db(q).select(db.packages.pkg_nodename, groupby=db.packages.pkg_nodename)
    data['agents_with_agent'] = [r.pkg_nodename for r in rows]
    data['agents_without_svc'] = set(data['agents_with_agent']) - set(data['agents_with_svc'])

    #
    q = db.nodes.nodename.belongs(data['agents_without_svc'])
    q &= db.nodes.host_mode == 'PRD'
    q = apply_filters(q, db.nodes.nodename, None)
    rows = db(q).select(db.nodes.nodename, db.nodes.os_name)
    agents_without_svc_prd = {}
    for row in rows:
        if row.os_name not in agents_without_svc_prd:
            agents_without_svc_prd[row.os_name] = [row.nodename]
        else:
            agents_without_svc_prd[row.os_name] += [row.nodename]
    data['agents_without_svc_prd'] = agents_without_svc_prd

    #
    q = db.nodes.nodename.belongs(data['agents_without_svc'])
    q &= db.nodes.host_mode != 'PRD'
    q = apply_filters(q, db.nodes.nodename, None)
    rows = db(q).select(db.nodes.nodename, db.nodes.os_name)
    agents_without_svc_nonprd = {}
    for row in rows:
        if row.os_name not in agents_without_svc_nonprd:
            agents_without_svc_nonprd[row.os_name] = [row.nodename]
        else:
            agents_without_svc_nonprd[row.os_name] += [row.nodename]
    data['agents_without_svc_nonprd'] = agents_without_svc_nonprd


    # prd svc
    q = db.services.svc_type == 'PRD'
    q &= db.svcmon.mon_svcname == db.services.svc_name
    q &= db.svcmon.mon_nodname == db.nodes.nodename
    q = apply_filters(q, db.svcmon.mon_nodname, db.svcmon.mon_svcname)
    rows = db(q).select(db.svcmon.mon_svcname, db.nodes.os_name, groupby=db.services.svc_name)
    svc_prd = {}
    for row in rows:
        if row.nodes.os_name not in svc_prd:
            svc_prd[row.nodes.os_name] = [row.svcmon.mon_svcname]
        else:
            svc_prd[row.nodes.os_name] += [row.svcmon.mon_svcname]
    data['svc_prd'] = svc_prd

    # !prd svc
    q = db.services.svc_type != 'PRD'
    q &= db.svcmon.mon_svcname == db.services.svc_name
    q &= db.svcmon.mon_nodname == db.nodes.nodename
    q = apply_filters(q, db.svcmon.mon_nodname, db.svcmon.mon_svcname)
    rows = db(q).select(db.svcmon.mon_svcname, db.nodes.os_name, groupby=db.services.svc_name)
    svc_nonprd = {}
    for row in rows:
        if row.nodes.os_name not in svc_nonprd:
            svc_nonprd[row.nodes.os_name] = [row.svcmon.mon_svcname]
        else:
            svc_nonprd[row.nodes.os_name] += [row.svcmon.mon_svcname]
    data['svc_nonprd'] = svc_nonprd

    # fill the blanks and compute total counts
    data['ostotal'] = {}
    data['total'] = {'svc_prd': 0, 'agents_without_svc_prd': 0, 'svc_nonprd': 0, 'agents_without_svc_nonprd': 0, 'svc': 0, 'agents_without_svc': 0}
    for os in data['os']:
        data['ostotal'][os] = {}
        for k in ('svc_prd', 'agents_without_svc_prd', 'svc_nonprd', 'agents_without_svc_nonprd'):
            if os not in data[k]:
                data[k][os] = []
            data['total'][k] += len(data[k][os])
        data['ostotal'][os]['svc'] = len(data['svc_prd'][os]) + len(data['svc_nonprd'][os])
        data['ostotal'][os]['agents_without_svc'] = len(data['agents_without_svc_prd'][os]) + len(data['agents_without_svc_nonprd'][os])
    data['total']['agents_without_svc'] = data['total']['agents_without_svc_prd'] + data['total']['agents_without_svc_nonprd']
    data['total']['svc'] = data['total']['svc_prd'] + data['total']['svc_nonprd']

    # billing svc
    qb = db.billing.bill_min_svc <= data['total']['svc']
    qb &= db.billing.bill_max_svc > data['total']['svc']
    billing['svc_prd'] = {}
    billing['svc_nonprd'] = {}
    for os in data['os']:
        q = qb & (db.billing.bill_os_name == os)
        b = db(q & (db.billing.bill_env=="prd")).select().first()
        val = 0 if b is None else b.bill_cost
        billing['svc_prd'][os] = int(val)
        b = db(q & (db.billing.bill_env=="nonprd")).select().first()
        val = 0 if b is None else b.bill_cost
        billing['svc_nonprd'][os] = int(val)

    # billing agt
    qb = db.billing_agent.bill_min_agt <= data['total']['agents_without_svc']
    qb &= db.billing_agent.bill_max_agt > data['total']['agents_without_svc']
    billing['agents_without_svc_prd'] = {}
    billing['agents_without_svc_nonprd'] = {}
    for os in data['os']:
        q = qb & (db.billing_agent.bill_os_name == os)
        b = db(q & (db.billing_agent.bill_env=="prd")).select().first()
        val = 0 if b is None else b.bill_cost
        billing['agents_without_svc_prd'][os] = int(val)
        b = db(q & (db.billing_agent.bill_env=="nonprd")).select().first()
        val = 0 if b is None else b.bill_cost
        billing['agents_without_svc_nonprd'][os] = int(val)

    # token svc
    token = {
      'svc_prd': {},
      'agents_without_svc_prd': {},
      'svc_nonprd': {},
      'agents_without_svc_nonprd': {},
      'ostotal': {},
      'total': {
        'svc': 0,
        'agents_without_svc': 0,
        'svc_prd': 0,
        'svc_nonprd': 0,
        'agents_without_svc_prd': 0,
        'agents_without_svc_nonprd': 0,
      }
    }
    for os in data['os']:
        token['ostotal'][os] = {'svc': 0, 'agents_without_svc': 0}
        for k in ('svc_prd', 'agents_without_svc_prd', 'svc_nonprd', 'agents_without_svc_nonprd'):
            token[k][os] = billing[k][os] * len(data[k][os])
        token['ostotal'][os]['svc'] += token['svc_prd'][os]
        token['ostotal'][os]['svc'] += token['svc_nonprd'][os]
        token['total']['svc_prd'] += token['svc_prd'][os]
        token['total']['svc_nonprd'] += token['svc_nonprd'][os]
        token['total']['svc'] += token['svc_prd'][os]
        token['total']['svc'] += token['svc_nonprd'][os]
        token['ostotal'][os]['agents_without_svc'] += token['agents_without_svc_prd'][os]
        token['ostotal'][os]['agents_without_svc'] += token['agents_without_svc_nonprd'][os]
        token['total']['agents_without_svc_prd'] += token['agents_without_svc_prd'][os]
        token['total']['agents_without_svc_nonprd'] += token['agents_without_svc_nonprd'][os]
        token['total']['agents_without_svc'] += token['agents_without_svc_prd'][os]
        token['total']['agents_without_svc'] += token['agents_without_svc_nonprd'][os]
    return data, billing, token

@auth.requires_login()
def billing():
    return dict(table=ajax_billing())

