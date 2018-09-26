def update_thresholds_batch(rows=None, one_source=False):
    if rows is None:
        q = db.checks_live.id > 0
        rows = db(q).select(cacheable=True)
    if one_source:
        update_thresholds_rows_one_source(rows)
    else:
        update_thresholds_rows(rows)
    ws_send('checks_change')

def update_thresholds_batch_type(chk_type):
    q = db.checks_live.chk_type == chk_type
    rows = db(q).select(
      db.checks_live.id,
      db.checks_live.node_id,
      db.checks_live.svc_id,
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
               t.chk_type as chk_type,
               t.chk_updated as chk_updated,
               t.chk_value as chk_value,
               t.chk_created as chk_created,
               t.chk_instance as chk_instance,
               cd2.chk_low as chk_low,
               cd2.chk_high as chk_high,
               "defaults" as chk_threshold_provider,
               NULL as chk_err,
               t.node_id as node_id,
               t.svc_id as svc_id
              from (
                select
                  cl.node_id,
                  cl.svc_id,
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
              (cl.chk_instance regexp cf.chk_instance or
               cl.chk_instance='' or
               cl.chk_instance is null) and
              cf.fset_id=f.id
             group by cf.id"""
    _rows = db.executesql(sql, as_dict=True)
    fset_ids = set(map(lambda x: (x['fset_id'], x['fset_name']), _rows))

    data = {}
    for row in rows:
        source = (row['node_id'], row['svc_id'])
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
    vars = ['node_id', 'svc_id', 'chk_type', 'chk_instance', 'chk_value', 'chk_high', 'chk_low', 'chk_threshold_provider']
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
    node_id = rows[0]['node_id']
    svc_id = rows[0]['svc_id']

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
              (cl.chk_instance regexp cf.chk_instance or
               cl.chk_instance='' or
               cl.chk_instance is null) and
              cf.fset_id=f.id
             group by cf.id"""%dict(ids=ids)
    _rows = db.executesql(sql, as_dict=True)
    fset_ids = set(map(lambda x: (x['fset_id'], x['fset_name']), _rows))
    rest = update_thresholds_from_filters_source(rows, (node_id, svc_id), fset_ids, _rows)
    return rest

def update_thresholds_from_filters_source(rows, source, fset_ids, _rows, fset_names=None, get_vals=False):
    import re
    node_id, svc_id = source

    # filter out those not matching the node_id/svc_id
    matching_fset_ids = comp_get_matching_fset_ids(fset_ids, node_id=node_id, svc_id=svc_id)

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
    vars = ['node_id', 'svc_id', 'chk_type', 'chk_instance', 'chk_value', 'chk_high', 'chk_low', 'chk_threshold_provider']
    vals = []
    for row in rows:
        i = row['chk_type'], row['chk_instance']
        match = [key for key in fsets if key[0]==i[0] and re.search(key[1], i[1])]
        if not match:
            rest.append(row)
            continue
        i = match[-1]
        vals.append([row['node_id'],
                     row['svc_id'],
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
                node_id,
                svc_id,
                chk_type,
                chk_value,
                chk_instance,
                (select chk_low from checks_settings cs where cs.node_id=cl.node_id and cs.chk_type=cl.chk_type and cs.chk_instance=cl.chk_instance limit 1) as chk_low
               from checks_live cl
               where
                id in (%(ids)s)
             ) t
             where
              t.chk_low is null"""%dict(ids=ids)
    rest = db.executesql(sql, as_dict=True)

    sql = """insert into checks_live  (
               node_id,
               svc_id,
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
                node_id,
                svc_id,
                chk_type,
                chk_updated,
                chk_value,
                chk_created,
                chk_instance,
                (select chk_low from checks_settings cs where cs.node_id=cl.node_id and cs.chk_type=cl.chk_type and cs.chk_instance=cl.chk_instance limit 1) as chk_low,
                (select chk_high from checks_settings cs where cs.node_id=cl.node_id and cs.chk_type=cl.chk_type and cs.chk_instance=cl.chk_instance limit 1) as chk_high,
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

def update_dash_checks_nodes(node_ids):
    for node_id in node_ids:
        update_dash_checks(node_id)

def update_dash_checks(node_id):
    now = datetime.datetime.now()
    now = now - datetime.timedelta(microseconds=now.microsecond)
    q = db.nodes.node_id == node_id
    env = db(q).select().first().node_env
    if env == 'PRD':
        sev = 3
    else:
        sev = 2

    sql = """insert into dashboard
               select
                 NULL,
                 "check out of bounds",
                 t.svc_id,
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
                 "%(now)s",
                 t.node_id,
                 NULL,
                 concat(t.ttype, ":", t.inst)
               from (
                 select
                   svc_id as svc_id,
                   node_id as node_id,
                   chk_type as ctype,
                   chk_instance as inst,
                   chk_threshold_provider as ttype,
                   chk_value as val,
                   chk_low as min,
                   chk_high as max
                 from checks_live
                 where
                   node_id = "%(node_id)s" and
                   chk_updated >= date_sub(now(), interval 1 day) and
                   (
                     chk_value < chk_low or
                     chk_value > chk_high
                   )
               ) t
               on duplicate key update
                 dash_updated="%(now)s"
          """%dict(node_id=node_id,
                   sev=sev,
                   env=env,
                   now=str(now),
                  )
    db.executesql(sql)
    db.commit()

    sql = """delete from dashboard
               where
                 node_id = "%(node_id)s" and
                 dash_type = "check out of bounds" and
                 dash_updated < "%(now)s"
          """%dict(node_id=node_id, now=str(now))
    n = db.executesql(sql)
    if n > 0:
        table_modified("dashboard")
    db.commit()

def enqueue_update_thresholds_batch(chk_type=None):
    if chk_type is None:
        q_fn = 'update_thresholds_batch'
        q_args = []
        task = scheduler.task_status(
          (db.scheduler_task.function_name == q_fn) & \
          (db.scheduler_task.status == "QUEUED")
        )
    else:
        q_fn = 'update_thresholds_batch_type'
        q_args = [chk_type]
        task = scheduler.task_status(
          (db.scheduler_task.function_name == q_fn) & \
          (db.scheduler_task.args.like('%'+chk_type+'%')) & \
          (db.scheduler_task.status == "QUEUED")
        )

    if task is not None:
        return
    scheduler.queue_task(q_fn, q_args, group_name="slow")
    db.commit()

