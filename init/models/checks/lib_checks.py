def update_thresholds_batch(rows=None, one_source=False):
    if rows is None:
        q = db.checks_live.id > 0
        rows = db(q).select(cacheable=True)
    if one_source:
        update_thresholds_rows_one_source(rows)
    else:
        update_thresholds_rows(rows)
    l = {
      'event': 'checks_change',
      'data': {'a': 'b'},
    }
    _websocket_send(event_msg(l))

def update_thresholds_batch_type(chk_type):
    q = db.checks_live.chk_type == chk_type
    rows = db(q).select(
      db.checks_live.id,
      db.checks_live.chk_nodename,
      db.checks_live.chk_svcname,
      db.checks_live.chk_type,
      db.checks_live.chk_instance,
      db.checks_live.chk_value,
      cacheable=True
    )
    update_thresholds_rows(rows)

def update_thresholds_rows(rows):
    rest = update_thresholds_from_settings(rows)
    rest = update_thresholds_from_filters(rest)
    rest = update_thresholds_from_defaults(rest)

def update_thresholds_rows_one_source(rows):
    rest = update_thresholds_from_settings(rows)
    rest = update_thresholds_from_filters_one_source(rest)
    rest = update_thresholds_from_defaults(rest)

def update_thresholds_from_defaults(rows):
    if len(rows) == 0:
        return
    ids = map(lambda x: str(x['id']), rows)
    ids = ','.join(ids)

    sql = """insert into checks_live
             select * from
             (select
               NULL as id,
               t.chk_nodename as chk_nodename,
               t.chk_svcname as chk_svcname,
               t.chk_type as chk_type,
               t.chk_updated as chk_updated,
               t.chk_value as chk_value,
               t.chk_created as chk_created,
               t.chk_instance as chk_instance,
               cd2.chk_low as chk_low,
               cd2.chk_high as chk_high,
               "defaults" as chk_threshold_provider,
               NULL as chk_err
              from (
                select
                  cl.chk_nodename,
                  cl.chk_svcname,
                  cl.chk_type,
                  cl.chk_updated,
                  cl.chk_value,
                  cl.chk_created,
                  cl.chk_instance,
                  (select id
                   from checks_defaults cd
                   where
                    cl.chk_type=cd.chk_type and
                    (cl.chk_instance rlike concat("^",cd.chk_inst,"$") or
                     cl.chk_instance=cd.chk_inst or
                     cd.chk_inst="" or
                     cd.chk_inst is null)
                   order by cd.chk_prio desc, length(cd.chk_inst) desc
                   limit 1
                  ) as cdid
                from checks_live cl
                where cl.id in (%(ids)s)
             ) t left join checks_defaults cd2 on t.cdid=cd2.id
             ) u
             on duplicate key update
                chk_low=u.chk_low,
                chk_high=u.chk_high,
                chk_threshold_provider=u.chk_threshold_provider
           """%dict(ids=ids)
    db.executesql(sql)
    db.commit()
    return []

def update_thresholds_from_filters(rows):
    if len(rows) == 0:
        return rows

    # get all relevent filterset ids
    sql = """select
              f.id as fset_id,
              f.fset_name as fset_name,
              cf.chk_type as chk_type,
              cf.chk_instance as chk_instance,
              cf.chk_low as chk_low,
              cf.chk_high as chk_high
             from
              checks_live cl,
              gen_filterset_check_threshold cf,
              gen_filtersets f
             where
              cl.chk_type=cf.chk_type and
              (cl.chk_instance=cf.chk_instance or
               cl.chk_instance='' or
               cl.chk_instance is null) and
              cf.fset_id=f.id
             group by cf.id"""
    _rows = db.executesql(sql, as_dict=True)
    fset_ids = set(map(lambda x: (x['fset_id'], x['fset_name']), _rows))

    data = {}
    for row in rows:
        source = (row['chk_nodename'], row['chk_svcname'])
        if source in data:
            data[source].append(row)
        else:
            data[source] = [row]

    fset_names = {}
    q = db.gen_filtersets.id > 0
    __rows = db(q).select(db.gen_filtersets.id, db.gen_filtersets.fset_name)
    for row in __rows:
        fset_names[row.id] = row.fset_name

    rest = []
    vals = []
    vars = ['chk_nodename', 'chk_svcname', 'chk_type', 'chk_instance', 'chk_value', 'chk_high', 'chk_low', 'chk_threshold_provider']
    for source in data:
        _rest, _vals = update_thresholds_from_filters_source(data[source], source, fset_ids, _rows, fset_names=fset_names, get_vals=True)
        rest += _rest
        vals += _vals
    generic_insert('checks_live', vars, vals)
    db.commit()
    return rest

def update_thresholds_from_filters_one_source(rows):
    if len(rows) == 0:
        return rows
    nodename = rows[0]['chk_nodename']
    svcname = rows[0]['chk_svcname']

    ids = map(lambda x: str(x['id']), rows)
    ids = ','.join(ids)

    # get all relevent filterset ids
    sql = """select
              f.id as fset_id,
              f.fset_name as fset_name,
              cf.chk_type as chk_type,
              cf.chk_instance as chk_instance,
              cf.chk_low as chk_low,
              cf.chk_high as chk_high
             from
              checks_live cl,
              gen_filterset_check_threshold cf,
              gen_filtersets f
             where
              cl.id in (%(ids)s) and
              cl.chk_type=cf.chk_type and
              (cl.chk_instance=cf.chk_instance or
               cl.chk_instance='' or
               cl.chk_instance is null) and
              cf.fset_id=f.id
             group by cf.id"""%dict(ids=ids)
    _rows = db.executesql(sql, as_dict=True)
    fset_ids = set(map(lambda x: (x['fset_id'], x['fset_name']), _rows))
    rest = update_thresholds_from_filters_source(rows, (nodename, svcname), fset_ids, _rows)
    return rest

def update_thresholds_from_filters_source(rows, source, fset_ids, _rows, fset_names=None, get_vals=False):
    nodename, svcname = source

    # filter out those not matching the nodename/svcname
    matching_fset_ids = comp_get_matching_fset_ids(fset_ids, nodename=nodename, svcname=svcname)

    if len(matching_fset_ids) == 0:
        if get_vals:
            return rows, []
        return rows

    # index fset info by row.chk_type, row.chk_instance
    fsets = {}
    for row in _rows:
         if row['fset_id'] not in matching_fset_ids:
             continue
         fsets[row['chk_type'], row['chk_instance']] = row

    # load filterset names cache
    if fset_names is None:
        fset_names = {}
        q = db.gen_filtersets.id.belongs(matching_fset_ids)
        _rows = db(q).select(db.gen_filtersets.id, db.gen_filtersets.fset_name)
        for row in _rows:
            fset_names[row.id] = row.fset_name

    # prepare thresholds insert/update request
    rest = []
    vars = ['chk_nodename', 'chk_svcname', 'chk_type', 'chk_instance', 'chk_value', 'chk_high', 'chk_low', 'chk_threshold_provider']
    vals = []
    for row in rows:
        i = row['chk_type'], row['chk_instance']
        if i not in fsets:
            rest.append(row)
            continue
        vals.append([row['chk_nodename'],
                     row['chk_svcname'],
                     row['chk_type'],
                     row['chk_instance'],
                     str(row['chk_value']),
                     str(fsets[i]['chk_high']),
                     str(fsets[i]['chk_low']),
                     'fset:%s'%fset_names[fsets[i]['fset_id']]])
    if get_vals:
        return rest, vals
    generic_insert('checks_live', vars, vals)
    db.commit()
    return rest


def update_thresholds_from_settings(rows):
    ids = map(lambda x: str(x.id), rows)
    ids = ','.join(ids)
    sql = """
             select * from (
               select
                id,
                chk_nodename,
                chk_svcname,
                chk_type,
                chk_value,
                chk_instance,
                (select chk_low from checks_settings cs where cs.chk_nodename=cl.chk_nodename and cs.chk_type=cl.chk_type and cs.chk_instance=cl.chk_instance limit 1) as chk_low
               from checks_live cl
               where
                id in (%(ids)s)
             ) t
             where
              t.chk_low is null"""%dict(ids=ids)
    rest = db.executesql(sql, as_dict=True)

    sql = """insert into checks_live  (
               chk_nodename,
               chk_svcname,
               chk_type,
               chk_updated,
               chk_value,
               chk_created,
               chk_instance,
               chk_low,
               chk_high,
               chk_threshold_provider
             )
             select * from (
               select
                chk_nodename,
                chk_svcname,
                chk_type,
                chk_updated,
                chk_value,
                chk_created,
                chk_instance,
                (select chk_low from checks_settings cs where cs.chk_nodename=cl.chk_nodename and cs.chk_type=cl.chk_type and cs.chk_instance=cl.chk_instance limit 1) as chk_low,
                (select chk_high from checks_settings cs where cs.chk_nodename=cl.chk_nodename and cs.chk_type=cl.chk_type and cs.chk_instance=cl.chk_instance limit 1) as chk_high,
                "settings" as chk_threshold_provider
               from checks_live cl
               where
                id in (%(ids)s)
             ) t
             where
              t.chk_low is not null
             on duplicate key update
              chk_low=t.chk_low,
              chk_high=t.chk_high,
              chk_threshold_provider=t.chk_threshold_provider"""%dict(ids=ids)
    db.executesql(sql)
    db.commit()
    return rest

def b_update_thresholds_batch():
    update_thresholds_batch()

def update_dash_checks_nodes(nodenames):
    for nodename in nodenames:
        update_dash_checks(nodename)

def update_dash_checks(nodename):
    nodename = nodename.strip("'")
    now = datetime.datetime.now()
    now = now - datetime.timedelta(microseconds=now.microsecond)
    sql = """select host_mode from nodes
             where
               nodename="%(nodename)s"
          """%dict(nodename=nodename)
    rows = db.executesql(sql)

    env = rows[0][0]
    if len(rows) == 1 and env == 'PRD':
        sev = 3
    else:
        sev = 2

    sql = """insert into dashboard
               select
                 NULL,
                 "check out of bounds",
                 t.svcname,
                 t.nodename,
                 %(sev)d,
                 "%%(ctype)s:%%(inst)s check value %%(val)d. %%(ttype)s thresholds: %%(min)d - %%(max)d",
                 concat('{"ctype": "', t.ctype,
                        '", "inst": "', t.inst,
                        '", "ttype": "', t.ttype,
                        '", "val": ', t.val,
                        ', "min": ', t.min,
                        ', "max": ', t.max,
                        '}'),
                 "%(now)s",
                 md5(concat('{"ctype": "', t.ctype,
                        '", "inst": "', t.inst,
                        '", "ttype": "', t.ttype,
                        '", "val": ', t.val,
                        ', "min": ', t.min,
                        ', "max": ', t.max,
                        '}')),
                 "%(env)s",
                 "",
                 "%(now)s"
               from (
                 select
                   chk_svcname as svcname,
                   chk_nodename as nodename,
                   chk_type as ctype,
                   chk_instance as inst,
                   chk_threshold_provider as ttype,
                   chk_value as val,
                   chk_low as min,
                   chk_high as max
                 from checks_live
                 where
                   chk_nodename = "%(nodename)s" and
                   chk_updated >= date_sub(now(), interval 1 day) and
                   (
                     chk_value < chk_low or
                     chk_value > chk_high
                   )
               ) t
               on duplicate key update
                 dash_updated="%(now)s"
          """%dict(nodename=nodename,
                   sev=sev,
                   env=env,
                   now=str(now),
                  )
    db.executesql(sql)
    db.commit()

    sql = """delete from dashboard
               where
                 dash_nodename = "%(nodename)s" and
                 dash_type = "check out of bounds" and
                 dash_updated < "%(now)s"
          """%dict(nodename=nodename, now=str(now))
    n = db.executesql(sql)
    if n > 0:
        table_modified("dashboard")
    db.commit()


