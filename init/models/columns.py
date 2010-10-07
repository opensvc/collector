def __update_columns(d, table):
    q = db.user_prefs_columns.upc_user_id==session.auth.user.id
    q &= db.user_prefs_columns.upc_table==table
    rows = db(q).select()
    for row in rows:
        d[row.upc_field]['display'] = row.upc_visible

def v_services_columns():
    d = dict(
        svc_name = dict(
            pos = 1,
            title = T('Service'),
            display = True,
            img = 'svc',
            size = 10
        ),
        svc_app = dict(
            pos = 2,
            title = T('App'),
            display = True,
            img = 'svc',
            size = 3
        ),
        svc_containertype = dict(
            pos = 3,
            title = T('Container type'),
            display = True,
            img = 'svc',
            size = 3
        ),
        svc_type = dict(
            pos = 4,
            title = T('Service type'),
            display = True,
            img = 'svc',
            size = 3
        ),
        svc_vmname = dict(
            pos = 6,
            title = T('Container name'),
            display = False,
            img = 'svc',
            size = 10
        ),
        svc_vcpus = dict(
            pos = 7,
            title = T('Vcpus'),
            display = False,
            img = 'svc',
            size = 3
        ),
        svc_vmem = dict(
            pos = 8,
            title = T('Vmem'),
            display = False,
            img = 'svc',
            size = 3
        ),
        svc_guestos = dict(
            pos = 9,
            title = T('Guest OS'),
            display = False,
            img = 'svc',
            size = 6
        ),
        svc_autostart = dict(
            pos = 11,
            title = T('Primary node'),
            display = False,
            img = 'svc',
            size = 10
        ),
        svc_nodes = dict(
            pos = 12,
            title = T('Nodes'),
            display = False,
            img = 'svc',
            size = 10
        ),
        svc_drpnode = dict(
            pos = 13,
            title = T('DRP node'),
            display = False,
            img = 'svc',
            size = 10
        ),
        svc_drpnodes = dict(
            pos = 14,
            title = T('DRP nodes'),
            display = False,
            img = 'svc',
            size = 10
        ),
        svc_drptype = dict(
            pos = 15,
            title = T('DRP type'),
            display = False,
            img = 'svc',
            size = 6
        ),
        svc_comment = dict(
            pos = 17,
            title = T('Comment'),
            display = False,
            img = 'svc',
            size = 10
        ),
        svc_updated = dict(
            pos = 18,
            title = T('Updated'),
            display = False,
            img = 'svc',
            size = 6
        ),
        responsibles = dict(
            pos = 19,
            title = T('Responsibles'),
            display = False,
            img = 'guy16',
            size = 6
        ),
        mailto = dict(
            pos = 20,
            title = T('Responsibles emails'),
            display = False,
            img = 'guy16',
            size = 6
        ),
    )
    return d

def v_nodes_columns():
    d = dict(
        nodename = dict(
            pos = 1,
            title = T('Node name'),
            display = True,
            img = 'node16',
            size = 10
        ),
        loc_country = dict(
            pos = 2,
            title = T('Country'),
            display = False,
            img = 'loc',
            size = 10
        ),
        loc_zip = dict(
            pos = 3,
            title = T('ZIP'),
            display = False,
            img = 'loc',
            size = 10
        ),
        loc_city = dict(
            pos = 4,
            title = T('City'),
            display = False,
            img = 'loc',
            size = 10
        ),
        loc_addr = dict(
            pos = 5,
            title = T('Address'),
            display = False,
            img = 'loc',
            size = 10
        ),
        loc_building = dict(
            pos = 6,
            title = T('Building'),
            display = True,
            img = 'loc',
            size = 10
        ),
        loc_floor = dict(
            pos = 7,
            title = T('Floor'),
            display = True,
            img = 'loc',
            size = 3
        ),
        loc_room = dict(
            pos = 8,
            title = T('Room'),
            display = False,
            img = 'loc',
            size = 10
        ),
        loc_rack = dict(
            pos = 9,
            title = T('Rack'),
            display = True,
            img = 'loc',
            size = 10
        ),
        os_name = dict(
            pos = 10,
            title = T('OS name'),
            display = False,
            img = 'os16',
            size = 10
        ),
        os_release = dict(
            pos = 11,
            title = T('OS release'),
            display = False,
            img = 'os16',
            size = 10
        ),
        os_vendor = dict(
            pos = 11,
            title = T('OS vendor'),
            display = False,
            img = 'os16',
            size = 6
        ),
        os_arch = dict(
            pos = 11,
            title = T('OS arch'),
            display = False,
            img = 'os16',
            size = 6
        ),
        os_kernel = dict(
            pos = 12,
            title = T('OS kernel'),
            display = False,
            img = 'os16',
            size = 10
        ),
        cpu_dies = dict(
            pos = 13,
            title = T('CPU dies'),
            display = True,
            img = 'cpu16',
            size = 10
        ),
        cpu_cores = dict(
            pos = 13,
            title = T('CPU cores'),
            display = True,
            img = 'cpu16',
            size = 10
        ),
        cpu_model = dict(
            pos = 14,
            title = T('CPU model'),
            display = True,
            img = 'cpu16',
            size = 10
        ),
        cpu_freq = dict(
            pos = 15,
            title = T('CPU freq'),
            display = False,
            img = 'cpu16',
            size = 10
        ),
        mem_banks = dict(
            pos = 16,
            title = T('Memory banks'),
            display = True,
            img = 'mem16',
            size = 10
        ),
        mem_slots = dict(
            pos = 16,
            title = T('Memory slots'),
            display = True,
            img = 'mem16',
            size = 10
        ),
        mem_bytes = dict(
            pos = 16,
            title = T('Memory'),
            display = True,
            img = 'mem16',
            size = 10
        ),
        serial = dict(
            pos = 17,
            title = T('Serial'),
            display = True,
            img = 'node16',
            size = 10
        ),
        model = dict(
            pos = 18,
            title = T('Model'),
            display = False,
            img = 'node16',
            size = 10
        ),
        team_responsible = dict(
            pos = 19,
            title = T('Team responsible'),
            display = True,
            img = 'node16',
            size = 10
        ),
        role = dict(
            pos = 20,
            title = T('Role'),
            display = False,
            img = 'node16',
            size = 10
        ),
        environnement = dict(
            pos = 21,
            title = T('Env'),
            display = True,
            img = 'node16',
            size = 10
        ),
        warranty_end = dict(
            pos = 22,
            title = T('Warranty end'),
            display = False,
            img = 'node16',
            size = 10
        ),
        status = dict(
            pos = 23,
            title = T('Status'),
            display = True,
            img = 'node16',
            size = 10
        ),
        type = dict(
            pos = 24,
            title = T('Type'),
            display = False,
            img = 'node16',
            size = 10
        ),
        power_supply_nb = dict(
            pos = 25,
            title = T('Power supply number'),
            display = False,
            img = 'pwr',
            size = 10
        ),
        power_cabinet1 = dict(
            pos = 26,
            title = T('Power cabinet #1'),
            display = False,
            img = 'pwr',
            size = 10
        ),
        power_cabinet2 = dict(
            pos = 27,
            title = T('Power cabinet #2'),
            display = False,
            img = 'pwr',
            size = 10
        ),
        power_protect = dict(
            pos = 28,
            title = T('Power protector'),
            display = False,
            img = 'pwr',
            size = 10
        ),
        power_protect_breaker = dict(
            pos = 29,
            title = T('Power protector breaker'),
            img = 'pwr',
            display = False,
            size = 10
        ),
        power_breaker1 = dict(
            pos = 30,
            title = T('Power breaker #1'),
            display = False,
            img = 'pwr',
            size = 10
        ),
        power_breaker2 = dict(
            pos = 31,
            title = T('Power breaker #2'),
            display = False,
            img = 'pwr',
            size = 10
        ),
    )
    return d

def status_columns():
    d = dict(
        mon_overallstatus = dict(
            pos = 7,
            title = T('Status'),
            display = True,
            img = 'svc',
            size = 4
        ),
        mon_updated = dict(
            pos = 8,
            title = T('Last status update'),
            display = False,
            img = 'svc',
            size = 6
        ),
        mon_frozen = dict(
            pos = 9,
            title = T('Frozen'),
            display = False,
            img = 'svc',
            size = 3
        ),
        mon_containerstatus = dict(
            pos = 12,
            title = T('Container status'),
            display = False,
            img = 'svc',
            size = 3
        ),
        mon_ipstatus = dict(
            pos = 13,
            title = T('Ip status'),
            display = False,
            img = 'svc',
            size = 3
        ),
        mon_fsstatus = dict(
            pos = 14,
            title = T('Fs status'),
            display = False,
            img = 'svc',
            size = 3
        ),
        mon_diskstatus = dict(
            pos = 15,
            title = T('Disk status'),
            display = False,
            img = 'svc',
            size = 3
        ),
        mon_syncstatus = dict(
            pos = 16,
            title = T('Sync status'),
            display = False,
            img = 'svc',
            size = 3
        ),
        mon_appstatus = dict(
            pos = 17,
            title = T('App status'),
            display = False,
            img = 'svc',
            size = 3
        ),
    )
    return d

def v_svcmon_columns():
    d = dict(
        mon_svcname = dict(
            pos = 1,
            title = T('Service'),
            display = True,
            img = 'svc',
            size = 10
        ),
        svc_containertype = dict(
            pos = 2,
            title = T('Container type'),
            display = True,
            img = 'svc',
            size = 3
        ),
        svc_app = dict(
            pos = 3,
            title = T('App'),
            display = True,
            img = 'svc',
            size = 3
        ),
        mon_svctype = dict(
            pos = 4,
            title = T('Service type'),
            display = True,
            img = 'svc',
            size = 3
        ),
        responsibles = dict(
            pos = 4,
            title = T('Responsibles'),
            display = False,
            img = 'guy16',
            size = 5
        ),
        mon_nodtype = dict(
            pos = 5,
            title = T('Node type'),
            display = True,
            img = 'svc',
            size = 3
        ),
        mon_nodname = dict(
            pos = 6,
            title = T('Node name'),
            display = True,
            img = 'node16',
            size = 6
        ),
        mon_frozen = dict(
            pos = 9,
            title = T('Frozen'),
            display = False,
            img = 'svc',
            size = 3
        ),
        svc_vcpus = dict(
            pos = 10,
            title = T('Vcpus'),
            display = False,
            img = 'svc',
            size = 3
        ),
        svc_vmem = dict(
            pos = 11,
            title = T('Vmem'),
            display = False,
            img = 'svc',
            size = 3
        ),
    )
    d.update(status_columns())
    return d

def v_drpservices_columns():
    d = dict(
        drp_wave = dict(
            pos = 1,
            title = T('Wave'),
            display = True,
            img = 'flag16',
            size = 4
        ),
    )
    return d

