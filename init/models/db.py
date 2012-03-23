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
auth=MyAuth(globals(),db)                      # authentication/authorization
auth.settings.hmac_key='sha512:7755f108-1b83-45dc-8302-54be8f3616a1'
auth.settings.expiration=36000000

#
# custom auth_user table. new field: email_notifications
#
db.define_table('im_types',
    Field('im_type','string'),
    migrate=False)

table = db.define_table(auth.settings.table_user_name,
    Field('first_name', length=128, default='',
          label=auth.messages.label_first_name,
          requires=IS_NOT_EMPTY(error_message=auth.messages.is_empty)),
    Field('last_name', length=128, default='',
          label=auth.messages.label_last_name,
          requires=IS_NOT_EMPTY(error_message=auth.messages.is_empty)),
    Field('email', length=512, default='',
          label=auth.messages.label_email),
    Field('password', 'password', length=512,
          readable=False, label=auth.messages.label_password,
          requires=[CRYPT(key=auth.settings.hmac_key)]),
    Field('registration_key', length=512,
          writable=False, readable=False, default='',
          label=auth.messages.label_registration_key),
    Field('reset_password_key', length=512,
          writable=False, readable=False, default='',
          label=auth.messages.label_reset_password_key),
    Field('email_notifications', 'boolean', default=True,
          label=T('Email notifications')),
    Field('im_notifications', 'boolean', default=True,
          label=T('Instant messaging notifications')),
    Field('perpage', 'integer', default=20,
          label=T('Preferred lines per page')),
    Field('im_type', 'integer',
          label=T('Instant messaging protocol'),
          requires=IS_IN_DB(db, db.im_types.id, "%(im_type)s", zero=T('choose one'))),
    Field('im_username', 'string', label=T("Instant messaging user name")),
    Field('im_log_level', 'string', label=T("Instant messaging log level"),
          requires=IS_IN_SET(["debug", "info", "warning", "error", "critical"])),
    Field('email_log_level', 'string', label=T("Email messaging log level"),
          requires=IS_IN_SET(["debug", "info", "warning", "error", "critical"])),
    Field('lock_filter', 'boolean', default=False,
          label=T("Lock user's session filter"),
          writable=False, readable=False),
    migrate=False)

table.email.requires = [IS_EMAIL(error_message=auth.messages.invalid_email),
                        IS_NOT_IN_DB(db, db.auth_user.email)]

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
mail.settings.tls = False

default_max_lines = 1000
default_limitby = (0, default_max_lines)

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
    Field('mon_nodname'),
    Field('mon_ipstatus'),
    Field('mon_fsstatus'),
    Field('mon_containerstatus'),
    Field('mon_diskstatus'),
    Field('mon_syncstatus'),
    Field('mon_hbstatus'),
    Field('mon_appstatus'),
    Field('mon_availstatus'),
    Field('mon_overallstatus'),
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
    Field('cron'),
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
    Field('cron'),
    Field('app'),
    Field('svc_ha'),
    Field('responsibles'),
    Field('mailto'),
    Field('warranty_end'),
    Field('asset_status'),
    Field('role'),
    Field('environnement'),
    Field('host_mode'),
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
    Field('team_integ'),
    Field('team_support'),
    Field('project'),
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
    Field('svc_ha'),
    Field('svc_cluster_type'),
    Field('svc_status'),
    Field('svc_availstatus'),
    Field('svc_flex_min_nodes'),
    Field('svc_flex_max_nodes'),
    Field('svc_flex_cpu_low_threshold'),
    Field('svc_flex_cpu_high_threshold'),
    Field('svc_guestos'),
    Field('svc_version'),
    Field('svc_hostid'),
    Field('svc_name'),
    Field('svc_nodes'),
    Field('svc_drpnode'),
    Field('svc_autostart'),
    Field('svc_type'),
    Field('svc_drpnodes'),
    Field('svc_comment'),
    Field('svc_app'),
    Field('svc_wave'),
    Field('svc_vcpus'),
    Field('svc_vmem'),
    Field('updated'),
    Field('svc_envdate'),
    Field('svc_containertype'),
    Field('responsibles'),
    Field('mailto'),
    migrate=False)

db.define_table('services',
    Field('svc_vmname'),
    Field('svc_ha'),
    Field('svc_status'),
    Field('svc_availstatus'),
    Field('svc_cluster_type'),
    Field('svc_flex_min_nodes'),
    Field('svc_flex_max_nodes'),
    Field('svc_flex_cpu_low_threshold'),
    Field('svc_flex_cpu_high_threshold'),
    Field('svc_guestos'),
    Field('svc_version'),
    Field('svc_hostid'),
    Field('svc_name'),
    Field('svc_nodes'),
    Field('svc_drpnode'),
    Field('svc_autostart'),
    Field('svc_type'),
    Field('svc_drpnodes'),
    Field('svc_comment'),
    Field('svc_app'),
    Field('svc_wave'),
    Field('svc_created'),
    Field('updated'),
    Field('svc_envdate'),
    Field('svc_containertype'),
    Field('svc_envfile'),
    Field('svc_vcpus'),
    Field('svc_vmem'),
    migrate=False)

db.define_table('v_svcmon',
    Field('err'),
    Field('svc_ha'),
    Field('svc_vmname'),
    Field('svc_cluster_type'),
    Field('svc_status'),
    Field('svc_availstatus'),
    Field('svc_flex_min_nodes'),
    Field('svc_flex_max_nodes'),
    Field('svc_flex_cpu_low_threshold'),
    Field('svc_flex_cpu_high_threshold'),
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
    Field('svc_created'),
    Field('svc_updated'),
    Field('svc_envdate'),
    Field('svc_containertype'),
    Field('svc_vcpus'),
    Field('svc_vmem'),
    Field('responsibles'),
    Field('mailto'),
    Field('mon_svcname'),
    Field('mon_nodname'),
    Field('mon_ipstatus'),
    Field('mon_fsstatus'),
    Field('mon_containerstatus'),
    Field('mon_diskstatus'),
    Field('mon_syncstatus'),
    Field('mon_hbstatus'),
    Field('mon_appstatus'),
    Field('mon_availstatus'),
    Field('mon_overallstatus'),
    Field('mon_updated'),
    Field('mon_changed'),
    Field('mon_frozen'),
    Field('node_updated'),
    Field('warranty_end'),
    Field('status'),
    Field('role'),
    Field('environnement'),
    Field('host_mode'),
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
    Field('team_integ'),
    Field('team_support'),
    Field('project'),
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
    Field('power_supply_nb', 'integer', default=0),
    Field('power_cabinet1'),
    Field('power_cabinet2'),
    Field('power_protect'),
    Field('power_protect_breaker'),
    Field('power_breaker1'),
    Field('power_breaker2'),
    migrate=False)

db.define_table('v_svcmon_clusters',
    db.v_svcmon,
    Field('nodes'),
    migrate=False)

db.define_table('drpservices',
    Field('drp_svcname'),
    Field('drp_wave'),
    Field('drp_project_id'),
    primarykey=['drp_svcname'],
    migrate=False)

db.define_table('drpprojects',
    Field('drp_project'),
    Field('drp_project_id'),
    primarykey=['drp_project_id'],
    migrate=False)

db.define_table('apps',
    Field('id'),
    Field('app'),
    Field('updated'),
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
    Field('environnement'),
    Field('host_mode', writable=False),
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
    Field('team_integ'),
    Field('team_support'),
    Field('project'),
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
    Field('updated'),
    migrate=False)

db.define_table('v_nodes',
    Field('warranty_end', 'datetime', default=request.now),
    Field('status'),
    Field('role'),
    Field('environnement'),
    Field('host_mode', writable=False),
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
    Field('team_integ'),
    Field('team_support'),
    Field('project'),
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
    Field('updated'),
    migrate=False)

db.define_table('v_users',
    Field('fullname'),
    Field('domains'),
    Field('manager'),
    Field('email'),
    Field('last'),
    Field('groups'),
    Field('lock_filter'),
    Field('fset_name'),
    migrate=False)

db.define_table('disk_blacklist',
    Field('disk_id', 'string'),
    migrate=False)

db.define_table('diskinfo',
    Field('disk_id', 'string'),
    Field('disk_devid', 'string'),
    Field('disk_arrayid', 'string'),
    Field('disk_size', 'integer'),
    Field('disk_group', 'string'),
    Field('disk_raid', 'string'),
    Field('disk_updated', 'datetime'),
    migrate=False)

db.define_table('svcdisks',
    Field('disk_id', 'string'),
    Field('disk_svcname', 'string'),
    Field('disk_nodename', 'string'),
    Field('disk_size', 'integer'),
    Field('disk_used', 'integer'),
    Field('disk_vendor', 'string'),
    Field('disk_model', 'string'),
    Field('disk_dg', 'string'),
    Field('disk_updated', 'datetime'),
    Field('disk_local', 'boolean'),
    Field('disk_region', 'integer'),
    migrate=False)

db.define_table('v_svcdisks',
    Field('disk_id', 'string'),
    Field('disk_devid', 'string'),
    Field('disk_arrayid', 'string'),
    Field('disk_size', 'integer'),
    Field('disk_used', 'integer'),
    Field('disk_svcname', 'string'),
    Field('disk_nodename', 'string'),
    Field('disk_vendor', 'string'),
    Field('disk_model', 'string'),
    Field('disk_dg', 'string'),
    Field('disk_updated', 'datetime'),
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
    Field('fset_id'),
    Field('day'),
    Field('nb_svc'),
    Field('nb_svc_prd'),
    Field('nb_svc_cluster'),
    Field('nb_action'),
    Field('nb_action_err'),
    Field('nb_action_warn'),
    Field('nb_action_ok'),
    Field('disk_size'),
    Field('local_disk_size'),
    Field('ram_size'),
    Field('nb_cpu_core'),
    Field('nb_cpu_die'),
    Field('nb_vcpu'),
    Field('nb_vmem'),
    Field('watt'),
    Field('rackunit'),
    Field('nb_apps'),
    Field('nb_accounts'),
    Field('nb_svc_with_drp'),
    Field('nb_nodes'),
    Field('nb_virt_nodes'),
    Field('nb_nodes_prd'),
    Field('nb_resp_accounts'),
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

db.define_table('svcmon_log',
    Field('id'),
    Field('mon_begin'),
    Field('mon_end'),
    Field('mon_svcname'),
    Field('mon_nodname'),
    Field('mon_availstatus'),
    Field('mon_overallstatus'),
    Field('mon_ipstatus'),
    Field('mon_fsstatus'),
    Field('mon_diskstatus'),
    Field('mon_containerstatus'),
    Field('mon_syncstatus'),
    Field('mon_hbstatus'),
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

db.define_table('stats_fs_u',
    Field('id'),
    Field('date', 'datetime'),
    Field('nodename', 'string'),
    Field('mntpt', 'string'),
    Field('size', 'integer'),
    Field('used', 'integer'),
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

db.define_table('patches',
    Field('id'),
    Field('patch_nodename', 'string', length=60),
    Field('patch_num', 'string', length=100),
    Field('patch_rev', 'string', length=16),
    Field('patch_updated', 'timestamp'),
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
    Field('chk_low', 'integer'),
    Field('chk_high', 'integer'),
    Field('chk_threshold_provider', 'string', length=60),
    migrate=False)

db.define_table('checks_defaults',
    Field('chk_type', 'string', length=10, writable=False),
    Field('chk_low', 'integer'),
    Field('chk_high', 'integer'),
    migrate=False)

db.define_table('checks_settings',
    Field('chk_nodename', 'string', length=60, writable=False),
    Field('chk_svcname', 'string', length=60, writable=False),
    Field('chk_instance', 'string', length=60, writable=False),
    Field('chk_type', 'string', length=10, writable=False),
    Field('chk_changed', 'datetime', writable=False),
    Field('chk_changed_by', 'string', length=60, writable=False),
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
    Field('fset_id'),
    Field('lc_os_concat', 'string'),
    Field('lc_os_vendor', 'string'),
    Field('lc_os_name', 'string'),
    Field('lc_count', 'integer'),
    Field('lc_date', 'date'),
    migrate=False)

db.define_table('v_lifecycle_os_name',
    Field('id'),
    Field('fset_id'),
    Field('lc_os_name', 'string'),
    Field('lc_count', 'integer'),
    Field('lc_date', 'date'),
    migrate=False)

db.define_table('user_prefs_columns',
    Field('id'),
    Field('upc_user_id', 'integer'),
    Field('upc_table', 'string'),
    Field('upc_field', 'string'),
    Field('upc_visible', 'boolean'),
    migrate=False)

db.define_table('upc_dashboard',
    Field('id'),
    Field('upc_user_id', 'integer'),
    Field('upc_dashboard', 'string'),
    migrate=False)

db.define_table('sym_upload',
    Field('archive','upload', requires=IS_NOT_EMPTY()),
    Field('batched','integer', writable=False),
    migrate=False)

db.define_table('comp_moduleset',
    Field('modset_name','string'),
    Field('modset_author','string'),
    Field('modset_updated','datetime'),
    migrate=False)

db.define_table('comp_moduleset_modules',
    Field('modset_id','string'),
    Field('modset_mod_name','string'),
    Field('modset_mod_author','string'),
    Field('modset_mod_updated','datetime'),
    migrate=False)

db.define_table('comp_log',
    Field('run_module','string'),
    Field('run_nodename','string'),
    Field('run_svcname','string'),
    Field('run_status','integer'),
    Field('run_log','string'),
    Field('run_ruleset','string'),
    Field('run_date','datetime'),
    Field('run_action','string'),
    Field('rset_md5','string'),
    migrate=False)

db.define_table('comp_status',
    Field('run_module','string'),
    Field('run_nodename','string'),
    Field('run_svcname','string'),
    Field('run_status','integer'),
    Field('run_log','string'),
    Field('run_ruleset','string'),
    Field('run_date','datetime'),
    Field('run_action','string'),
    Field('rset_md5','string'),
    migrate=False)

db.define_table('comp_svc_status',
    Field('svc_name','string'),
    Field('total','integer'),
    Field('ok','integer'),
    Field('nok','integer'),
    Field('na','integer'),
    Field('obs','integer'),
    Field('pct','integer'),
    migrate=True)

db.define_table('comp_node_status',
    Field('node_name','string'),
    Field('total','integer'),
    Field('ok','integer'),
    Field('nok','integer'),
    Field('na','integer'),
    Field('obs','integer'),
    Field('pct','integer'),
    migrate=True)

db.define_table('comp_mod_status',
    Field('mod_name','string'),
    Field('total','integer'),
    Field('ok','integer'),
    Field('nok','integer'),
    Field('na','integer'),
    Field('obs','integer'),
    Field('pct','integer'),
    migrate=True)

db.define_table('gen_filtersets',
    Field('fset_name','string', requires=IS_NOT_EMPTY()),
    Field('fset_author','string'),
    Field('fset_updated','datetime'),
    migrate=False)

db.define_table('gen_filtersets_filters',
    Field('fset_id','integer', requires=IS_NOT_EMPTY()),
    Field('encap_fset_id','integer'),
    Field('f_id','integer'),
    Field('f_order','integer'),
    Field('f_log_op','string',
          requires=IS_IN_SET(['AND', 'AND NOT', 'OR', 'OR NOT']),
          default='AND'),
    migrate=False)

db.define_table('gen_filters',
    Field('f_op','string',
          requires=IS_IN_SET(['=', 'LIKE', 'NOT LIKE', '<', '<=', '>', '>=', 'IN', 'NOT IN']),
          default='='),
    Field('f_table','string', requires=IS_NOT_EMPTY()),
    Field('f_field','string', requires=IS_NOT_EMPTY()),
    Field('f_value','string', requires=IS_NOT_EMPTY()),
    Field('f_author','string', readable=False, writable=False),
    Field('f_updated','datetime', readable=False, writable=False),
    migrate=False)

db.define_table('v_gen_filtersets',
    db.gen_filtersets,
    db.gen_filtersets_filters,
    db.gen_filters,
    Field('encap_fset_name','string'),
    Field('join_id','integer'),
    Field('fset_id','integer'),
    migrate=False)

db.define_table('comp_rulesets',
    Field('ruleset_name','string', requires=IS_NOT_EMPTY()),
    Field('ruleset_type','string', requires=IS_IN_SET(['contextual','explicit'])),
    migrate=False)

db.define_table('comp_rulesets_rulesets',
    Field('parent_rset_id','integer'),
    Field('child_rset_id','integer'),
    migrate=False)

db.define_table('comp_rulesets_variables',
    Field('ruleset_id','integer', requires=IS_NOT_EMPTY()),
    Field('var_class','string', requires=IS_IN_SET(("raw", "authkey", "file",
"fs", "group", "package", "user", "vuln")), default="raw"),
    Field('var_name','string', requires=IS_NOT_EMPTY()),
    Field('var_value','text'),
    Field('var_author','string', readable=False, writable=False),
    Field('var_updated','datetime', readable=False, writable=False),
    migrate=False)

db.define_table('comp_rulesets_filtersets',
    Field('ruleset_id','integer', requires=IS_NOT_EMPTY()),
    Field('fset_id','integer', requires=IS_NOT_EMPTY()),
    migrate=False)

db.define_table('comp_rulesets_nodes',
    Field('ruleset_id','integer', requires=IS_NOT_EMPTY()),
    Field('nodename','string', requires=IS_NOT_EMPTY()),
    migrate=False)

db.define_table('comp_rulesets_services',
    Field('ruleset_id','integer', requires=IS_NOT_EMPTY()),
    Field('svcname','string', requires=IS_NOT_EMPTY()),
    migrate=False)

db.define_table('v_comp_rulesets',
    Field('ruleset_id','integer'),
    Field('fset_id','integer'),
    Field('encap_rset','string'),
    Field('encap_rset_id','integer'),
    Field('ruleset_name','string', requires=IS_NOT_EMPTY()),
    Field('ruleset_type','string', requires=IS_IN_SET(['contextual','explicit'])),
    Field('teams_responsible','string'),
    Field('fset_name','string'),
    Field('var_class','string', requires=IS_IN_SET(("raw", "authkey", "file",
"fs", "group", "package", "user", "cve")), default="raw"),
    Field('var_name','string'),
    Field('var_value','text'),
    Field('var_author','string', readable=False, writable=False),
    Field('var_updated','datetime', readable=False, writable=False),
    migrate=False)

db.define_table('comp_ruleset_team_responsible',
    Field('ruleset_id','string'),
    Field('group_id','string'),
    migrate=False)

db.define_table('comp_node_ruleset',
    Field('ruleset_node','string'),
    Field('ruleset_name','string'),
    Field('ruleset_updated','string'),
    migrate=False)

db.define_table('comp_node_moduleset',
    Field('modset_node','string'),
    Field('modset_id','integer'),
    Field('modset_updated','string'),
    Field('modset_author','string'),
    migrate=False)

db.define_table('comp_modulesets_services',
    Field('modset_svcname','string'),
    Field('modset_id','integer'),
    Field('modset_updated','string'),
    Field('modset_author','string'),
    migrate=False)

db.define_table('v_comp_mod_status',
    Field('mod_name','string'),
    Field('mod_total','integer'),
    Field('mod_ok','integer'),
    Field('mod_percent','integer'),
    Field('mod_nodes','string'),
    migrate=False)

db.define_table('v_comp_nodes',
    db.nodes,
    Field('rulesets','string'),
    Field('modulesets','string'),
    migrate=False)

db.define_table('v_comp_explicit_rulesets',
    Field('ruleset_name','string'),
    Field('variables','string'),
    migrate=False)

db.define_table('log',
    Field('log_action','string'),
    Field('log_user','string'),
    Field('log_svcname','string'),
    Field('log_nodename','string'),
    Field('log_fmt','string'),
    Field('log_dict','string'),
    Field('log_date','datetime'),
    Field('log_gtalk_sent','integer'),
    Field('log_email_sent','integer'),
    Field('log_entry_id','string'),
    Field('log_level','string'),
    migrate=False)

db.define_table('column_filters',
    Field('user_id','integer'),
    Field('col_tableid','string'),
    Field('col_name','string'),
    Field('col_filter','string'),
    migrate=False)

db.define_table('wiki_pages',
    Field('name', writable=False, requires=IS_NOT_IN_DB(db,'wiki_pages.name')),
    Field('author', db.auth_user, readable=False, writable=False),
    Field('saved_on', 'datetime', readable=False, writable=False),
    Field('title'),
    Field('body', 'text'),
    Field('change_note', length=200),
    migrate=False)

db.define_table('action_queue',
    Field('status', 'string'),
    Field('ret', 'integer'),
    Field('command', 'text'),
    Field('date_queued', 'timestamp'),
    Field('date_dequeued', 'timestamp'),
    migrate=False)

db.define_table('v_flex_status',
    Field('svc_name', 'string'),
    Field('svc_flex_min_nodes', 'integer'),
    Field('svc_flex_max_nodes', 'integer'),
    Field('svc_flex_cpu_low_threshold', 'integer'),
    Field('svc_flex_cpu_high_threshold', 'integer'),
    Field('up', 'integer'),
    Field('cpu', 'integer'),
    migrate=False)

db.define_table('v_outdated_services',
    Field('svcname', 'string'),
    Field('uptodate', 'integer'),
    migrate=False)

db.define_table('services_log',
    Field('svc_name', 'string'),
    Field('svc_availstatus', 'string'),
    Field('svc_begin', 'datetime'),
    Field('svc_end', 'datetime'),
    migrate=False)

db.define_table('auth_node',
    Field('nodename', 'string'),
    Field('uuid', 'string'),
    migrate=False)

db.define_table('v_comp_moduleset_teams_responsible',
    Field('modset_id', 'integer'),
    Field('teams_responsible', 'string'),
    migrate=False)

db.define_table('v_gen_filterset_teams_responsible',
    Field('fset_id', 'integer'),
    Field('teams_responsible', 'string'),
    migrate=False)

db.define_table('comp_moduleset_team_responsible',
    Field('modset_id','string'),
    Field('group_id','string'),
    migrate=False)

db.define_table('gen_filterset_team_responsible',
    Field('fset_id','integer'),
    Field('group_id','integer'),
    migrate=False)

db.define_table('gen_filterset_check_threshold',
    Field('fset_id','string'),
    Field('chk_type','string'),
    Field('chk_instance','string'),
    Field('chk_low','integer'),
    Field('chk_high','integer'),
    migrate=False)

db.define_table('prov_templates',
    Field('tpl_name','string'),
    Field('tpl_command','text'),
    Field('tpl_comment','text'),
    Field('tpl_author','string'),
    Field('tpl_created','datetime'),
    migrate=False)

db.define_table('prov_template_team_responsible',
    Field('tpl_id','integer'),
    Field('group_id','integer'),
    migrate=False)

db.define_table('pdns_domains',
    Field('name','string'),
    Field('master','string'),
    Field('last_check','integer'),
    Field('type','string', requires=IS_IN_SET(['MASTER', 'NATIVE', 'SLAVE']), default='MASTER'),
    Field('notified_serial','integer'),
    Field('account','string'),
    migrate=False)

db.define_table('pdns_records',
    Field('domain_id','integer',
          requires=IS_IN_DB(db, db.pdns_domains.id, "%(name)s", zero=T("choose domain"))),
    Field('name','string',
          requires=IS_NOT_EMPTY()),
    Field('type','string',
          requires=IS_IN_SET(['A', 'AAAA', 'A6', 'AFSDB', 'CNAME', 'DNAME', 'DNSKEY', 'DS', 'HINFO', 'ISDN', 'KEY', 'LOC', 'MX', 'NAPTR', 'NS', 'NSEC', 'NXT', 'PTR', 'RP', 'RRSIG', 'RT', 'SIG', 'SOA', 'SPF', 'SRV', 'TXT', 'WKS', 'X25']),
          default='A'),
    Field('content','string',
          requires=IS_NOT_EMPTY()),
    Field('ttl','integer', default=120),
    Field('prio','integer'),
    Field('change_date','integer'),
    migrate=False)

db.pdns_domains.name.requires = [IS_NOT_EMPTY(),
                                 IS_NOT_IN_DB(db, db.pdns_domains.name)]

db.define_table('networks',
    Field('name','string'),
    Field('network','string'),
    Field('broadcast','string'),
    Field('netmask','integer',
          requires=IS_INT_IN_RANGE(0, 33)),
    Field('team_responsible','string',
          requires=IS_IN_DB(db, db.auth_group.role, "%(role)s", zero=T('choose team'))),
    migrate=False)

db.networks.name.requires = [IS_NOT_EMPTY(),
                             IS_NOT_IN_DB(db, db.networks.name)]
db.networks.network.requires = [IS_NOT_EMPTY(),
                                IS_NOT_IN_DB(db, db.networks.network)]
db.networks.broadcast.requires = [IS_NOT_EMPTY(),
                                 IS_NOT_IN_DB(db, db.networks.broadcast)]

db.define_table('network_segments',
    Field('seg_type','string', requires=IS_IN_SET(["static", "dynamic"])),
    Field('seg_begin','string'),
    Field('seg_end','string'),
    Field('net_id','integer', default="static", requires=[IS_NOT_EMPTY(), IS_IN_DB(db, db.networks.id)]),
    migrate=False)

db.define_table('v_network_segments',
    Field('seg_type','string', requires=IS_IN_SET(["static", "dynamic"])),
    Field('seg_begin','string'),
    Field('seg_end','string'),
    Field('net_id','integer', default="static", requires=[IS_NOT_EMPTY(), IS_IN_DB(db, db.networks.id)]),
    Field('teams_responsible','string'),
    migrate=False)

db.define_table('network_segment_responsibles',
    Field('seg_id','integer'),
    Field('group_id','integer'),
    migrate=False)

db.define_table('appinfo',
    Field('app_svcname','string'),
    Field('app_nodename','string'),
    Field('app_launcher','string'),
    Field('app_key','string'),
    Field('app_value','string'),
    Field('app_updated','datetime'),
    migrate=False)

db.define_table('dashboard',
    Field('dash_type','string'),
    Field('dash_svcname','string'),
    Field('dash_nodename','string'),
    Field('dash_severity','integer'),
    Field('dash_fmt','string'),
    Field('dash_dict','string'),
    Field('dash_created','datetime'),
    migrate=False)

db.define_table('dash_agg',
    Field('dash_type','string'),
    Field('dash_alerts','integer'),
    Field('dash_history','string'),
    migrate=False)

db.define_table('dashboard_log',
    Field('dash_type','string'),
    Field('dash_alerts','integer'),
    Field('dash_date','string'),
    Field('dash_filters_md5','string'),
    migrate=False)

db.define_table('gen_filterset_user',
    Field('fset_id','integer'),
    Field('user_id','integer'),
    migrate=False)

db.define_table('stats_compare_user',
    Field('compare_id','integer'),
    Field('user_id','integer'),
    migrate=False)

db.define_table('stats_compare_fset',
    Field('compare_id','integer'),
    Field('fset_id','integer'),
    migrate=False)

db.define_table('stats_compare',
    Field('name','string'),
    migrate=False)

db.define_table('node_hba',
    Field('nodename','string'),
    Field('hba_id','string'),
    Field('hba_type','string'),
    Field('updated','datetime'),
    migrate=False)

db.define_table('stor_array',
    Field('array_name','string'),
    Field('array_model','string'),
    Field('array_firmware','string'),
    Field('array_cache','integer'),
    Field('array_updated','datetime'),
    migrate=False)

db.define_table('stor_array_dg',
    Field('array_id','integer'),
    Field('dg_name','string'),
    Field('dg_free','integer'),
    Field('dg_used','integer'),
    Field('dg_size','integer'),
    Field('dg_updated','datetime'),
    migrate=False)

db.define_table('stor_array_dg_quota',
    Field('dg_id','integer'),
    Field('app_id','integer'),
    Field('quota','integer'),
    migrate=False)

db.define_table('stor_array_tgtid',
    Field('array_id','integer'),
    Field('array_tgtid','string'),
    migrate=False)

db.define_table('stor_zone',
    Field('tgt_id','string'),
    Field('hba_id','string'),
    Field('nodename','string'),
    Field('updated','datetime'),
    migrate=False)

db.define_table('stor_array_proxy',
    Field('array_id','integer'),
    Field('nodename','string'),
    migrate=False)

db.define_table('comp_run_ruleset',
    Field('rset_md5','string'),
    Field('rset','text'),
    migrate=False)

db.define_table('v_disk_quota',
    Field('array_name','string'),
    Field('array_model','string'),
    Field('dg_name','string'),
    Field('dg_free','integer'),
    Field('dg_used','integer'),
    Field('dg_size','integer'),
    Field('app','string'),
    Field('quota','integer'),
    Field('quota_used','integer'),
    Field('dg_id','integer'),
    Field('array_id','integer'),
    Field('app_id','integer'),
    migrate=False)

db.define_table('stat_day_disk_app',
    Field('app','string'),
    Field('day','datetime'),
    Field('disk_used','integer'),
    migrate=False)

db.define_table('stat_day_disk_array',
    Field('array_name','string'),
    Field('day','datetime'),
    Field('disk_used','integer'),
    Field('disk_size','integer'),
    migrate=False)

db.define_table('stat_day_disk_array_dg',
    Field('array_name','string'),
    Field('array_dg','string'),
    Field('day','datetime'),
    Field('disk_used','integer'),
    Field('disk_size','integer'),
    migrate=False)


