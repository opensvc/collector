# coding: utf8

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
#########################################################################

if request.env.web2py_runtime_gae:            # if running on Google App Engine
    db = DAL('gae')                           # connect to Google BigTable
    session.connect(request, response, db=db) # and store sessions and tickets there
    ### or use the following lines to store sessions in Memcache
    # from gluon.contrib.memdb import MEMDB
    # from google.appengine.api.memcache import Client
    # session.connect(request, response, db=MEMDB(Client())
else:                                         # else use a normal relational database
    db = DAL('mysql://opensvc:opensvc@dbopensvc/opensvc')       # if not, use SQLite or other DB
## if no need for session
# session.forget()

#########################################################################
## Here is sample code if you need for 
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - crud actions
## comment/uncomment as needed

from gluon.tools import *
auth=Auth(globals(),db)                      # authentication/authorization
auth.settings.hmac_key='sha512:7755f108-1b83-45dc-8302-54be8f3616a1'
auth.settings.expiration=36000
auth.define_tables(migrate=False)                         # creates all needed tables
crud=Crud(globals(),db)                      # for CRUD helpers using auth
service=Service(globals())                   # for json, xml, jsonrpc, xmlrpc, amfrpc
auth.messages.logged_in = ''
# crud.settings.auth=auth                      # enforces authorization on crud
# mail=Mail()                                  # mailer
# mail.settings.server='smtp.gmail.com:587'    # your SMTP server
# mail.settings.sender='you@gmail.com'         # your email
# mail.settings.login='username:password'      # your credentials or None
# auth.settings.mailer=mail                    # for user email verification
# auth.settings.registration_requires_verification = True
# auth.settings.registration_requires_approval = True
# auth.messages.verify_email = \
#  'Click on the link http://.../user/verify_email/%(key)s to verify your email'
## more options discussed in gluon/tools.py
#########################################################################
mail=Mail()
mail.settings.server='localhost:25'
mail.settings.sender='admin@opensvc.com'
auth.settings.mailer=mail

#########################################################################
## Define your tables below, for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################
db.define_table('svcmon',
    Field('mon_svcname'),
    Field('mon_svctype'),
    Field('mon_drptype'),
    Field('mon_nodname'),
    Field('mon_ipstatus'),
    Field('mon_fsstatus'),
    Field('mon_containerstatus'),
    Field('mon_diskstatus'),
    Field('mon_syncstatus'),
    Field('mon_appstatus'),
    Field('mon_overallstatus'),
    Field('mon_prinodes'),
    Field('mon_updated'),
    Field('mon_changed'),
    Field('mon_frozen'),
    migrate=False)

db.define_table('SVCactions',
    Field('version'),
    Field('action'),
    Field('status'),
    Field('time'),
    Field('begin'),
    Field('end'),
    Field('hostname'),
    Field('hostid'),
    Field('status_log'),
    Field('ack'),
    Field('acked_by'),
    Field('acked_comment'),
    Field('acked_date'),
    Field('svcname'),
    Field('pid'),
    Field('status_log'),
    migrate=False)

db.define_table('v_svcactions',
    Field('version'),
    Field('action'),
    Field('status'),
    Field('time'),
    Field('begin'),
    Field('end'),
    Field('hostname'),
    Field('hostid'),
    Field('status_log'),
    Field('ack'),
    Field('acked_by'),
    Field('acked_comment'),
    Field('acked_date'),
    Field('svcname'),
    Field('pid'),
    Field('status_log'),
    Field('app'),
    Field('responsibles'),
    Field('mailto'),
    Field('warranty_end'),
    Field('asset_status'),
    Field('role'),
    Field('environnement'),
    Field('cpu_freq'),
    Field('cpu_cores'),
    Field('cpu_dies'),
    Field('cpu_model'),
    Field('cpu_vendor'),
    Field('mem_bytes'),
    Field('mem_banks'),
    Field('mem_slots'),
    Field('os_vendor'),
    Field('os_name'),
    Field('os_kernel'),
    Field('os_release'),
    Field('os_arch'),
    Field('type'),
    Field('nodename'),
    Field('team_responsible'),
    Field('serial'),
    Field('model'),
    Field('loc_addr'),
    Field('loc_floor'),
    Field('loc_city'),
    Field('loc_zip'),
    Field('loc_rack'),
    Field('loc_country'),
    Field('loc_building'),
    Field('loc_room'),
    migrate=False)

db.define_table('v_services',
    Field('svc_vmname'),
    Field('svc_guestos'),
    Field('svc_version'),
    Field('svc_hostid'),
    Field('svc_name'),
    Field('svc_nodes'),
    Field('svc_drpnode'),
    Field('svc_ipname'),
    Field('svc_ipdev'),
    Field('svc_drpipname'),
    Field('svc_drpipdev'),
    Field('svc_drptype'),
    Field('svc_fs'),
    Field('svc_dev'),
    Field('svc_autostart'),
    Field('svc_mntopt'),
    Field('svc_scsi'),
    Field('svc_type'),
    Field('svc_drpnodes'),
    Field('svc_comment'),
    Field('svc_app'),
    Field('svc_wave'),
    Field('svc_drnoaction'),
    Field('svc_vcpus'),
    Field('svc_vmem'),
    Field('updated'),
    Field('cksum'),
    Field('svc_hapri'),
    Field('svc_hasec'),
    Field('svc_hastonith'),
    Field('svc_hastartup'),
    Field('svc_envdate'),
    Field('svc_containertype'),
    Field('svc_metrocluster'),
    Field('responsibles'),
    Field('mailto'),
    migrate=False)

db.define_table('services',
    Field('svc_vmname'),
    Field('svc_guestos'),
    Field('svc_version'),
    Field('svc_hostid'),
    Field('svc_name'),
    Field('svc_nodes'),
    Field('svc_drpnode'),
    Field('svc_ipname'),
    Field('svc_ipdev'),
    Field('svc_drpipname'),
    Field('svc_drpipdev'),
    Field('svc_drptype'),
    Field('svc_fs'),
    Field('svc_dev'),
    Field('svc_autostart'),
    Field('svc_mntopt'),
    Field('svc_scsi'),
    Field('svc_type'),
    Field('svc_drpnodes'),
    Field('svc_comment'),
    Field('svc_app'),
    Field('svc_wave'),
    Field('svc_drnoaction'),
    Field('updated'),
    Field('cksum'),
    Field('svc_hapri'),
    Field('svc_hasec'),
    Field('svc_hastonith'),
    Field('svc_hastartup'),
    Field('svc_envdate'),
    Field('svc_containertype'),
    Field('svc_metrocluster'),
    Field('svc_envfile'),
    Field('svc_vcpus'),
    Field('svc_vmem'),
    migrate=False)

db.define_table('v_svcmon',
    Field('err'),
    Field('svc_vmname'),
    Field('svc_guestos'),
    Field('svc_version'),
    Field('svc_name'),
    Field('svc_nodes'),
    Field('svc_drpnode'),
    Field('svc_drptype'),
    Field('svc_autostart'),
    Field('svc_type'),
    Field('svc_drpnodes'),
    Field('svc_comment'),
    Field('svc_app'),
    Field('svc_drnoaction'),
    Field('svc_updated'),
    Field('svc_envdate'),
    Field('svc_containertype'),
    Field('svc_metrocluster'),
    Field('svc_vcpus'),
    Field('svc_vmem'),
    Field('responsibles'),
    Field('mailto'),
    Field('mon_svcname'),
    Field('mon_svctype'),
    Field('mon_drptype'),
    Field('mon_nodname'),
    Field('mon_nodtype'),
    Field('mon_ipstatus'),
    Field('mon_fsstatus'),
    Field('mon_containerstatus'),
    Field('mon_diskstatus'),
    Field('mon_syncstatus'),
    Field('mon_appstatus'),
    Field('mon_overallstatus'),
    Field('mon_prinodes'),
    Field('mon_updated'),
    Field('mon_changed'),
    Field('mon_frozen'),
    Field('warranty_end'),
    Field('status'),
    Field('role'),
    Field('environnement'),
    Field('mem_bytes'),
    Field('mem_banks'),
    Field('mem_slots'),
    Field('os_vendor'),
    Field('os_name'),
    Field('os_kernel'),
    Field('os_release'),
    Field('os_arch'),
    Field('cpu_freq'),
    Field('cpu_dies'),
    Field('cpu_cores'),
    Field('cpu_model'),
    Field('cpu_vendor'),
    Field('type'),
    Field('nodename'),
    Field('team_responsible'),
    Field('serial'),
    Field('model'),
    Field('loc_addr'),
    Field('loc_floor'),
    Field('loc_city'),
    Field('loc_zip'),
    Field('loc_rack'),
    Field('loc_country'),
    Field('loc_building'),
    Field('loc_room'),
    migrate=False)

db.define_table('v_svcmon_clusters',
    db.v_svcmon,
    Field('nodes'),
    migrate=False)

db.define_table('drpservices',
    Field('drp_svcname'),
    Field('drp_wave'),
    Field('drp_project_id'),
    migrate=False)

db.define_table('drpprojects',
    Field('drp_project'),
    Field('drp_project_id'),
    migrate=False)

db.define_table('apps',
    Field('id'),
    Field('app'),
    migrate=False)

db.define_table('v_apps',
    Field('id'),
    Field('app'),
    Field('roles'),
    Field('responsibles'),
    Field('mailto'),
    migrate=False)

db.define_table('apps_responsibles',
    Field('id'),
    Field('app_id'),
    Field('group_id'),
    migrate=False)

os_names = [
    "Linux",
    "HP-UX",
    "AIX",
    "Solaris",
    "OpenSolaris",
    "Windows",
    "Irix",
    "FreeBSD",
    "OSX",
    "Tru64"
]

os_vendors = [
    "Apple",
    "FreeBSD",
    "Red Hat",
    "Ubuntu",
    "Debian",
    "CentOS",
    "HP",
    "IBM",
    "Microsoft",
    "Suse",
    "Oracle"
]

db.define_table('nodes',
    Field('warranty_end', 'datetime', default=request.now),
    Field('status'),
    Field('role'),
    Field('environnement', writable=False),
    Field('mem_bytes', writable=False),
    Field('mem_banks', writable=False),
    Field('mem_slots', writable=False),
    Field('os_vendor', writable=False),
    Field('os_name', writable=False),
    Field('os_kernel', writable=False),
    Field('os_release', writable=False),
    Field('os_arch', writable=False),
    Field('cpu_freq', writable=False),
    Field('cpu_dies', writable=False),
    Field('cpu_cores', writable=False),
    Field('cpu_model', writable=False),
    Field('cpu_vendor', writable=False),
    Field('type'),
    Field('nodename', 'string', length=30, requires=IS_NOT_EMPTY(), unique=True),
    Field('team_responsible'),
    Field('serial', writable=False),
    Field('model', writable=False),
    Field('loc_addr'),
    Field('loc_city'),
    Field('loc_zip'),
    Field('loc_rack'),
    Field('loc_floor'),
    Field('loc_country'),
    Field('loc_building'),
    Field('loc_room'),
    Field('power_supply_nb', 'integer', default=0),
    Field('power_cabinet1'),
    Field('power_cabinet2'),
    Field('power_protect'),
    Field('power_protect_breaker'),
    Field('power_breaker1'),
    Field('power_breaker2'),
    migrate=False)

db.define_table('v_nodes',
    Field('warranty_end', 'datetime', default=request.now),
    Field('status'),
    Field('role'),
    Field('environnement', writable=False),
    Field('mem_bytes', writable=False),
    Field('mem_banks', writable=False),
    Field('mem_slots', writable=False),
    Field('os_vendor', writable=False),
    Field('os_name', writable=False),
    Field('os_kernel', writable=False),
    Field('os_release', writable=False),
    Field('os_arch', writable=False),
    Field('os_concat', writable=False),
    Field('cpu_freq', writable=False),
    Field('cpu_dies', writable=False),
    Field('cpu_cores', writable=False),
    Field('cpu_model', writable=False),
    Field('cpu_vendor', writable=False),
    Field('type'),
    Field('nodename', writable=False),
    Field('team_responsible'),
    Field('serial', writable=False),
    Field('model', writable=False),
    Field('loc_addr'),
    Field('loc_city'),
    Field('loc_zip'),
    Field('loc_rack'),
    Field('loc_floor'),
    Field('loc_country'),
    Field('loc_building'),
    Field('loc_room'),
    Field('power_supply_nb', 'integer', default=0),
    Field('power_cabinet1'),
    Field('power_cabinet2'),
    Field('power_protect'),
    Field('power_protect_breaker'),
    Field('power_breaker1'),
    Field('power_breaker2'),
    migrate=False)

db.define_table('alerts',
    Field('id'),
    Field('created_at'),
    Field('send_at'),
    Field('sent_at'),
    Field('sent_to'),
    Field('subject'),
    Field('body'),
    Field('action_id'),
    Field('action_ids'),
    Field('app_id'),
    Field('domain'),
    migrate=False)

db.define_table('v_users',
    Field('fullname'),
    Field('domains'),
    Field('manager'),
    Field('email'),
    Field('last'),
    Field('groups'),
    migrate=False)

db.define_table('svcdisks',
    Field('id'),
    Field('disk_id'),
    Field('disk_svcname'),
    Field('disk_nodename'),
    Field('disk_size'),
    Field('disk_vendor'),
    Field('disk_model'),
    Field('disk_dg'),
    Field('disk_target_port_id'),
    migrate=False)

db.define_table('v_svcdisks',
    Field('id'),
    Field('disk_id'),
    Field('disk_svcname'),
    Field('disk_nodename'),
    Field('disk_size'),
    Field('disk_vendor'),
    Field('disk_model'),
    Field('disk_dg'),
    Field('disk_target_port_id'),
    Field('disk_devid'),
    Field('disk_arrayid'),
    migrate=False)

db.define_table('svc_res_sync',
    Field('id'),
    Field('sync_svcname'),
    Field('sync_src'),
    Field('sync_dst'),
    Field('sync_dstfs'),
    Field('sync_snap'),
    Field('sync_bwlimit'),
    Field('sync_exclude'),
    Field('sync_prdtarget'),
    Field('sync_drptarget'),
    migrate=False)

db.define_table('svc_res_ip',
    Field('id'),
    Field('ip_svcname'),
    Field('ip_name'),
    Field('ip_dev'),
    Field('ip_netmask'),
    Field('ip_node'),
    migrate=False)

db.define_table('svc_res_fs',
    Field('id'),
    Field('fs_svcname'),
    Field('fs_dev'),
    Field('fs_mnt'),
    Field('fs_mntopt'),
    Field('fs_type'),
    migrate=False)

db.define_table('domain_permissions',
    Field('id'),
    Field('group_id'),
    Field('domains'),
    migrate=False)

db.define_table('stat_day',
    Field('id'),
    Field('day'),
    Field('nb_svc'),
    Field('nb_svc_prd'),
    Field('nb_svc_cluster'),
    Field('nb_action'),
    Field('nb_action_err'),
    Field('nb_action_warn'),
    Field('nb_action_ok'),
    Field('disk_size'),
    Field('ram_size'),
    Field('nb_cpu_core'),
    Field('nb_cpu_die'),
    Field('watt'),
    Field('rackunit'),
    Field('nb_apps'),
    Field('nb_accounts'),
    Field('nb_svc_with_drp'),
    Field('nb_nodes'),
    Field('nb_nodes_prd'),
    migrate=False)

db.define_table('resmon',
    Field('id'),
    Field('svcname'),
    Field('nodename'),
    Field('rid'),
    Field('res_desc'),
    Field('res_status'),
    Field('res_log'),
    Field('changed'),
    Field('updated'),
    migrate=False)

db.define_table('svcmessages',
    Field('id'),
    Field('msg_svcname'),
    Field('msg_last_editor'),
    Field('msg_last_edit_date'),
    Field('msg_body'),
    migrate=False)

db.define_table('svcmon_log',
    Field('id'),
    Field('mon_begin'),
    Field('mon_end'),
    Field('mon_svcname'),
    Field('mon_nodname'),
    Field('mon_overallstatus'),
    Field('mon_ipstatus'),
    Field('mon_fsstatus'),
    Field('mon_diskstatus'),
    Field('mon_containerstatus'),
    Field('mon_syncstatus'),
    Field('mon_appstatus'),
    migrate=False)

db.define_table('v_svc_group_status',
    Field('id'),
    Field('svcname'),
    Field('svctype'),
    Field('groupstatus'),
    Field('nodes'),
    migrate=False)

db.define_table('obsolescence',
    Field('id'),
    Field('obs_type', 'string', length=30),
    Field('obs_name', 'string', length=100),
    Field('obs_warn_date', 'datetime'),
    Field('obs_alert_date', 'datetime'),
    Field('obs_warn_date_updated_by', 'string', length=100),
    Field('obs_alert_date_updated_by', 'string', length=100),
    Field('obs_warn_date_updated', 'datetime'),
    Field('obs_alert_date_updated', 'datetime'),
    migrate=False)

db.define_table('svcmon_log_ack',
    Field('mon_svcname', 'string', length=100),
    Field('mon_begin', 'datetime'),
    Field('mon_end', 'datetime'),
    Field('mon_comment', 'string'),
    Field('mon_account', 'integer'),
    Field('mon_acked_by', 'string'),
    Field('mon_acked_on', 'datetime'),
    migrate=False)

db.define_table('auth_filters',
    Field('id'),
    Field('fil_uid', 'integer'),
    Field('fil_id', 'integer'),
    Field('fil_value', 'string', length=200),
    Field('fil_active', 'tinyint'),
    migrate=False)

db.define_table('filters',
    Field('id'),
    Field('fil_name', 'string', length=30),
    Field('fil_column', 'string', length=30),
    Field('fil_need_value', 'boolean'),
    Field('fil_pos', 'integer'),
    Field('fil_table', 'string', length=30),
    Field('fil_search_table', 'string', length=30),
    Field('fil_img', 'string', length=30),
    migrate=False)

db.define_table('stats_cpu',
    Field('id'),
    Field('nodename', 'string', length=60),
    Field('cpu', 'string', length=5),
    Field('date', 'datetime'),
    Field('usr', 'float'),
    Field('nice', 'float'),
    Field('sys', 'float'),
    Field('iowait', 'float'),
    Field('steal', 'float'),
    Field('irq', 'float'),
    Field('soft', 'float'),
    Field('guest', 'float'),
    Field('idle', 'float'),
    migrate=False)

db.define_table('stats_mem_u',
    Field('id'),
    Field('date', 'datetime'),
    Field('nodename', 'string', length=60),
    Field('kbmemfree', 'integer'),
    Field('kbmemused', 'integer'),
    Field('pct_memused', 'float'),
    Field('kbbuffers', 'integer'),
    Field('kbcached', 'integer'),
    Field('kbcommit', 'integer'),
    Field('pct_commit', 'float'),
    Field('kbmemsys', 'integer'),
    migrate=False)

db.define_table('stats_proc',
    Field('id'),
    Field('date', 'datetime'),
    Field('nodename', 'string', length=60),
    Field('runq_sz', 'integer'),
    Field('plist_sz', 'integer'),
    Field('ldavg_1', 'float'),
    Field('ldavg_5', 'float'),
    Field('ldavg_15', 'float'),
    migrate=False)

db.define_table('stats_swap',
    Field('id'),
    Field('date', 'datetime'),
    Field('nodename', 'string', length=60),
    Field('kbswpfree', 'integer'),
    Field('kbswpused', 'integer'),
    Field('pct_swpused', 'float'),
    Field('pct_swpcad', 'float'),
    Field('kbswpcad', 'integer'),
    migrate=False)

db.define_table('stats_block',
    Field('id'),
    Field('date', 'datetime'),
    Field('nodename', 'string', length=60),
    Field('tps', 'float'),
    Field('rtps', 'float'),
    Field('wtps', 'float'),
    Field('rbps', 'float'),
    Field('wbps', 'float'),
    migrate=False)

db.define_table('stats_blockdev',
    Field('id'),
    Field('date', 'datetime'),
    Field('nodename', 'string', length=60),
    Field('dev', 'string', length=20),
    Field('tps', 'float'),
    Field('rsecps', 'float'),
    Field('wsecps', 'float'),
    Field('avgrq_sz', 'float'),
    Field('avgqu_sz', 'float'),
    Field('await', 'float'),
    Field('svctm', 'float'),
    Field('pct_util', 'float'),
    migrate=False)

db.define_table('stats_netdev_err',
    Field('id'),
    Field('date', 'datetime'),
    Field('nodename', 'string', length=60),
    Field('dev', 'string', length=8),
    Field('rxerrps', 'float'),
    Field('txerrps', 'float'),
    Field('collps', 'float'),
    Field('rxdropps', 'float'),
    Field('txdropps', 'float'),
    migrate=False)

db.define_table('stats_netdev',
    Field('id'),
    Field('date', 'datetime'),
    Field('nodename', 'string', length=60),
    Field('dev', 'string', length=8),
    Field('rxkBps', 'float'),
    Field('txkBps', 'float'),
    Field('rxpckps', 'float'),
    Field('txpckps', 'float'),
    migrate=False)

db.define_table('v_stats_netdev_err_avg_last_day',
    Field('id'),
    Field('nodename', 'string', length=60),
    Field('dev', 'string', length=8),
    Field('avgrxerrps', 'float'),
    Field('avgtxerrps', 'float'),
    Field('avgcollps', 'float'),
    Field('avgrxdropps', 'float'),
    Field('avgtxdropps', 'float'),
    migrate=False)

db.define_table('packages',
    Field('id'),
    Field('pkg_nodename', 'string', length=60),
    Field('pkg_name', 'string', length=100),
    Field('pkg_version', 'string', length=16),
    Field('pkg_arch', 'string', length=8),
    Field('pkg_updated', 'timestamp'),
    migrate=False)

db.define_table('checks_live',
    Field('id'),
    Field('chk_nodename', 'string', length=60),
    Field('chk_svcname', 'string', length=60),
    Field('chk_instance', 'string', length=60),
    Field('chk_type', 'string', length=10),
    Field('chk_updated', 'timestamp'),
    Field('chk_created', 'timestamp'),
    Field('chk_value', 'integer'),
    migrate=False)

db.define_table('checks_defaults',
    Field('id'),
    Field('chk_type', 'string', length=10, writable=False),
    Field('chk_low', 'integer'),
    Field('chk_high', 'integer'),
    migrate=False)

db.define_table('checks_settings',
    Field('id'),
    Field('chk_nodename', 'string', length=60, writable=False),
    Field('chk_svcname', 'string', length=60, writable=False),
    Field('chk_instance', 'string', length=60, writable=False),
    Field('chk_type', 'string', length=10, writable=False),
    Field('chk_changed', 'datetime', writable=False),
    Field('chk_changed_by', 'string', length=60, writable=False),
    Field('chk_low', 'integer'),
    Field('chk_high', 'integer'),
    migrate=False)

db.define_table('v_checks',
    Field('id'),
    Field('chk_nodename', 'string', length=60),
    Field('chk_svcname', 'string', length=60),
    Field('chk_instance', 'string', length=60),
    Field('chk_type', 'string', length=10),
    Field('chk_updated', 'timestamp'),
    Field('chk_created', 'timestamp'),
    Field('chk_value', 'integer'),
    Field('chk_low', 'integer'),
    Field('chk_high', 'integer'),
    migrate=False)

db.define_table('v_billing_per_os',
    Field('id'),
    Field('svc_list', 'string'),
    Field('os_name', 'string'),
    Field('nb', 'integer'),
    Field('app_list', 'string'),
    Field('cost', 'integer'),
    migrate=False)

db.define_table('v_billing_per_app',
    Field('id'),
    Field('svc_list', 'string'),
    Field('svc_app', 'string'),
    Field('nb', 'integer'),
    Field('os_list', 'string'),
    Field('cost', 'integer'),
    migrate=False)

db.define_table('lifecycle_os',
    Field('id'),
    Field('lc_os_concat', 'string'),
    Field('lc_os_vendor', 'string'),
    Field('lc_os_name', 'string'),
    Field('lc_count', 'integer'),
    Field('lc_date', 'date'),
    migrate=False)

