@auth.requires_membership('Manager')
def billing():
    query = (db.v_billing_per_os.nb!=0)
    billing_per_os = db(query).select(orderby=~db.v_billing_per_os.nb)
    query = (db.v_billing_per_app.nb!=0)
    billing_per_app = db(query).select(orderby=~db.v_billing_per_app.nb)
    return dict(billing_per_os=billing_per_os, billing_per_app=billing_per_app)

@auth.requires_membership('Manager')
def billing2():
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
    rows = db(q).select(db.svcmon.mon_svcname, db.nodes.os_name, groupby=db.services.svc_name)
    svc_nonprd = {}
    for row in rows:
        if row.nodes.os_name not in svc_nonprd:
            svc_nonprd[row.nodes.os_name] = [row.svcmon.mon_svcname]
        else:
            svc_nonprd[row.nodes.os_name] += [row.svcmon.mon_svcname]
    data['svc_nonprd'] = svc_nonprd

    # fill the blanks
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
        billing['svc_prd'][os] = val
        b = db(q & (db.billing.bill_env=="nonprd")).select().first()
        val = 0 if b is None else b.bill_cost
        billing['svc_nonprd'][os] = val

    # billing agt
    qb = db.billing_agent.bill_min_agt <= data['total']['agents_without_svc']
    qb &= db.billing_agent.bill_max_agt > data['total']['agents_without_svc']
    billing['agents_without_svc_prd'] = {}
    billing['agents_without_svc_nonprd'] = {}
    for os in data['os']:
        q = qb & (db.billing_agent.bill_os_name == os)
        b = db(q & (db.billing_agent.bill_env=="prd")).select().first()
        val = 0 if b is None else b.bill_cost
        billing['agents_without_svc_prd'][os] = val
        b = db(q & (db.billing_agent.bill_env=="nonprd")).select().first()
        val = 0 if b is None else b.bill_cost
        billing['agents_without_svc_nonprd'][os] = val

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

    return dict(data=data, billing=billing, token=token)
