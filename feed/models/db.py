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
    #db = DAL('mysql://opensvc:opensvc@dbopensvc/opensvc')       # if not, use SQLite or other DB
    db = DAL('mysql://opensvc:opensvc@dbopensvc/opensvc',
             driver_args={'connect_timeout': 20},
             pool_size=30)

## if no need for session
session.forget()

#########################################################################
## Here is sample code if you need for 
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - crud actions
## comment/uncomment as needed

from gluon.tools import *
#auth=Auth(globals(),db)                      # authentication/authorization
#auth.settings.hmac_key='sha512:7755f108-1b83-45dc-8302-54be8f3616a1'
#auth.settings.expiration=36000

#auth.define_tables(migrate=False)                         # creates all needed tables
#crud=Crud(globals(),db)                      # for CRUD helpers using auth
service=Service(globals())                   # for json, xml, jsonrpc, xmlrpc, amfrpc
#auth.messages.logged_in = ''
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
#mail=Mail()
#mail.settings.server='localhost:25'
#mail.settings.sender='admin@opensvc.com'
#auth.settings.mailer=mail

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
    Field('mon_sharestatus'),
    Field('mon_syncstatus'),
    Field('mon_hbstatus'),
    Field('mon_appstatus'),
    Field('mon_overallstatus'),
    Field('mon_availstatus'),
    Field('mon_prinodes'),
    Field('mon_updated'),
    Field('mon_changed'),
    Field('mon_frozen'),
    Field('mon_vmname'),
    Field('mon_vmtype'),
    migrate=False)

db.define_table('SVCactions',
    Field('version'),
    Field('action'),
    Field('status'),
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

db.define_table('services',
    Field('svc_vmname'),
    Field('svc_ha'),
    Field('svc_status'),
    Field('svc_availstatus'),
    Field('svc_guestos'),
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
    Field('svc_drnoaction', 'boolean'),
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

db.define_table('nodes',
    Field('warranty_end', 'datetime', default=request.now),
    Field('maintenance_end', 'datetime', default=request.now),
    Field('status'),
    Field('role'),
    Field('fqdn'),
    Field('assetname'),
    Field('enclosureslot'),
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
    Field('cpu_threads', writable=False),
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
    Field('enclosure'),
    Field('hv'),
    Field('hvpool'),
    Field('hvvdc'),
    Field('version'),
    Field('listener_port'),
    Field('os_obs_warn_date'),
    Field('os_obs_alert_date'),
    Field('hw_obs_warn_date'),
    Field('hw_obs_alert_date'),
    migrate=False)

db.define_table('disk_blacklist',
    Field('disk_id', 'string'),
    migrate=False)

db.define_table('diskinfo',
    Field('disk_id', 'string'),
    Field('disk_devid', 'string'),
    Field('disk_alloc', 'integer'),
    Field('disk_name', 'string'),
    Field('disk_arrayid', 'string'),
    Field('disk_size', 'integer'),
    Field('disk_group', 'string'),
    Field('disk_raid', 'string'),
    Field('disk_updated', 'datetime'),
    Field('disk_level', 'integer'),
    migrate=False)

db.define_table('svcdisks',
    Field('id'),
    Field('disk_id'),
    Field('disk_svcname'),
    Field('disk_nodename'),
    Field('disk_size'),
    Field('disk_used'),
    Field('disk_vendor'),
    Field('disk_model'),
    Field('disk_dg'),
    Field('disk_updated'),
    Field('disk_region', 'integer'),
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
    Field('vmname'),
    Field('rid'),
    Field('res_desc'),
    Field('res_status'),
    Field('res_log'),
    Field('changed'),
    Field('updated'),
    migrate=False)

db.define_table('svcmon_log_ack',
    Field('mon_begin'),
    Field('mon_end'),
    Field('mon_svcname'),
    Field('mon_acked_by'),
    Field('mon_acked_on'),
    Field('mon_account'),
    Field('mon_comment'),
    migrate=False)

db.define_table('svcmon_log',
    Field('id'),
    Field('mon_begin'),
    Field('mon_end'),
    Field('mon_svcname'),
    Field('mon_nodname'),
    Field('mon_overallstatus'),
    Field('mon_availstatus'),
    Field('mon_ipstatus'),
    Field('mon_fsstatus'),
    Field('mon_diskstatus'),
    Field('mon_sharestatus'),
    Field('mon_containerstatus'),
    Field('mon_syncstatus'),
    Field('mon_hbstatus'),
    Field('mon_appstatus'),
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

db.define_table('packages',
    Field('id'),
    Field('pkg_nodename', 'string', length=60),
    Field('pkg_name', 'string', length=100),
    Field('pkg_version', 'string', length=16),
    Field('pkg_arch', 'string', length=8),
    Field('pkg_updated', 'datetime'),
    migrate=False)

db.define_table('patches',
    Field('id'),
    Field('patch_nodename', 'string', length=60),
    Field('patch_num', 'string', length=100),
    Field('patch_rev', 'string', length=16),
    Field('patch_updated', 'datetime'),
    migrate=False)

db.define_table('checks_live',
    Field('id'),
    Field('chk_nodename', 'string', length=60),
    Field('chk_svcname', 'string', length=60),
    Field('chk_instance', 'string', length=60),
    Field('chk_type', 'string', length=10),
    Field('chk_updated', 'datetime'),
    Field('chk_created', 'datetime'),
    Field('chk_value', 'integer'),
    Field('chk_low', 'integer'),
    Field('chk_high', 'integer'),
    Field('chk_threshold_provider', 'string', length=60),
    migrate=False)

db.define_table('checks_defaults',
    Field('chk_type', 'string', length=10, writable=False),
    Field('chk_inst', 'string', length=10),
    Field('chk_low', 'integer'),
    Field('chk_high', 'integer'),
    Field('chk_prio', 'integer'),
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
    Field('run_date','datetime'),
    Field('run_action','string'),
    migrate=False)

db.define_table('comp_status',
    Field('run_module','string'),
    Field('run_nodename','string'),
    Field('run_svcname','string'),
    Field('run_status','integer'),
    Field('run_log','string'),
    Field('run_date','datetime'),
    Field('run_action','string'),
    migrate=False)

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

db.define_table('comp_rulesets_variables',
    Field('ruleset_id','integer', requires=IS_NOT_EMPTY()),
    Field('var_name','string', requires=IS_NOT_EMPTY()),
    Field('var_value','string', requires=IS_NOT_EMPTY()),
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

db.define_table('comp_modulesets_services',
    Field('modset_svcname','string'),
    Field('modset_id','integer'),
    Field('modset_updated','string'),
    Field('modset_mod_author','string'),
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

db.define_table('gen_filterset_check_threshold',
    Field('fset_id','string'),
    Field('chk_type','string'),
    Field('chk_instance','string'),
    Field('chk_low','integer'),
    Field('chk_high','integer'),
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
    Field('log_level','string'),
    migrate=False)

db.define_table('auth_user',
    Field('im_notifications', 'boolean'),
    Field('im_type', 'integer'),
    Field('im_username', 'string'),
    migrate=False)

db.define_table('auth_group',
    Field('role', 'string'),
    migrate=False)

db.define_table('auth_membership',
    Field('user_id', 'integer'),
    Field('group_id', 'integer'),
    migrate=False)

db.define_table('apps',
    Field('app', 'string'),
    Field('app_domain', 'string'),
    Field('app_team_ops', 'string'),
    migrate=False)

db.define_table('apps_responsibles',
    Field('app_id', 'integer'),
    Field('group_id', 'integer'),
    migrate=False)

db.define_table('feed_queue',
    Field('q_fn', 'string'),
    Field('q_args', 'blob'),
    Field('created', 'datetime'),
    migrate=False)

db.define_table('dashboard',
    Field('dash_type','string'),
    Field('dash_svcname','string'),
    Field('dash_nodename','string'),
    Field('dash_severity','integer'),
    Field('dash_fmt','string'),
    Field('dash_dict','string'),
    Field('dash_created','datetime'),
    Field('dash_updated','datetime'),
    Field('dash_md5','string'),
    migrate=False)

db.define_table('v_disk_app',
    Field('disk_id', 'string'),
    Field('disk_region', 'string'),
    Field('app', 'string'),
    Field('disk_used', 'string'),
    Field('disk_size', 'integer'),
    Field('disk_arrayid', 'string'),
    Field('disk_group', 'string'),
    Field('disk_devid', 'string'),
    Field('disk_name', 'string'),
    Field('disk_alloc', 'integer'),
    Field('disk_updated', 'datetime'),
    Field('disk_level', 'string'),
    Field('disk_raid', 'string'),
    Field('disk_svcname', 'string'),
    Field('disk_nodename', 'string'),
    Field('disk_vendor', 'string'),
    Field('disk_model', 'string'),
    Field('disk_dg', 'string'),
    Field('svcdisk_updated', 'datetime'),
    Field('svcdisk_id', 'integer'),
    Field('disk_local', 'boolean'),
    migrate=False)

db.define_table('b_disk_app',
    db.v_disk_app,
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

db.define_table('action_queue',
    Field('status', 'string'),
    Field('ret', 'integer'),
    Field('command', 'text'),
    Field('stdout', 'text'),
    Field('stderr', 'text'),
    Field('date_queued', 'datetime'),
    Field('date_dequeued', 'datetime'),
    Field('nodename', 'string'),
    Field('svcname', 'string'),
    Field('action_type', 'string'),
    migrate=False)

