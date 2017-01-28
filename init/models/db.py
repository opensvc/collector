# coding: utf8

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
#########################################################################

import datetime
import os

dbopensvc_host = config_get('dbopensvc_host', '127.0.0.1')
dbopensvc_user = config_get('dbopensvc_user', 'opensvc')
dbopensvc_password = config_get('dbopensvc_password', 'opensvc')
redis_host = config_get('redis_host', dbopensvc_host)
ldap_mode = config_get("ldap_mode", None)

from gluon.contrib.redis_cache import RedisCache
from gluon.contrib.redis_utils import RConn
rconn = RConn(redis_host, 6379)
cache.redis = RedisCache(rconn, debug=False)

from gluon.contrib.redis_session import RedisSession
sessiondb = RedisSession(redis_conn=rconn, session_expiry=False)
session.connect(request, response, db=sessiondb)

def db_error_handler(exc):
    body = """
<div style="text-align:left:margin:1em">
        <h1>Database connexion error</h1>
        <pre>%(error)s</pre>
        <br>
        <a href="%(url)s">Edit collector's configuration file</a>
</div>
"""
    lines = str(exc).splitlines()
    try:
        error = lines[0]+"\n"+lines[-1]
    except IndexError:
        error = str(exc)
    data = dict(
        error=error,
        url=URL(a="admin", c="default", f="edit",
                args=["init/modules/config.py"],
                vars={"id": "modules__config__py"}),
    )
    raise HTTP(512, body=body%data)

#if request.env.web2py_runtime_gae:            # if running on Google App Engine
#    db = DAL('gae')                           # connect to Google BigTable
#    session.connect(request, response, db=db) # and store sessions and tickets there
    ### or use the following lines to store sessions in Memcache
    # from gluon.contrib.memdb import MEMDB
    # from google.appengine.api.memcache import Client
    # session.connect(request, response, db=MEMDB(Client())
#else:                                         # else use a normal relational database
try:
    db = DAL('mysql://%s:%s@%s/opensvc' % (dbopensvc_user, dbopensvc_password, dbopensvc_host),
             driver_args={'connect_timeout': 20},
             pool_size=0,
             lazy_tables=True)
except Exception as exc:
    db_error_handler(exc)


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
auth=MyAuth(globals(), db)
auth.settings.hmac_key='sha512:7755f108-1b83-45dc-8302-54be8f3616a1'
auth.settings.expiration=config_get("session_expire", 36000000)
auth.settings.allow_basic_login = True
auth.settings.remember_me_form = False
auth.settings.login_methods = [auth]
auth.settings.register_onaccept = [lambda form: auth_register_callback(form)]
login_form_username = False

if config_get("allow_register", False):
    auth.settings.actions_disabled.append('register')

#request.requires_https()
#response.optimize_css="concat,minify"
#response.optimize_js="concat,minify"


def table_modified(name):
    sql = """insert into table_modified values (null, "%s", now()) on duplicate key update table_modified=now()"""%name
    db.executesql(sql)
    db.commit()


#
# custom auth_user table. new field: email_notifications
#
auth.settings.extra_fields['auth_group'] = [
    Field('privilege','boolean'),
]

db.define_table('im_types',
    Field('im_type','string'),
    migrate=False)

auth.settings.extra_fields['auth_membership']= [
    Field('primary_group', 'boolean', default=False,
          label=T("The user's primary group, used for task assignation and message routing")),
]

auth.settings.extra_fields['auth_user']= [
    Field('quota_docker_registries', 'integer', default=1,
          requires=IS_INT_IN_RANGE(minimum=0), writable=False,
          label=T('Maximum number of docker registries the user can be responsible of')),
    Field('quota_org_group', 'integer', default=1,
          requires=IS_INT_IN_RANGE(minimum=0), writable=False,
          label=T('Maximum number of organizational groups the user can be member of')),
    Field('quota_app', 'integer', default=1, writable=False,
          requires=IS_INT_IN_RANGE(minimum=0),
          label=T('Maximum number of applications the user can be responsible of')),
    Field('phone_work', 'string', label=T("Work desk phone number"), length=15),
    Field('email_notifications', 'boolean', default=False,
          label=T('Email notifications')),
    Field('im_notifications', 'boolean', default=False,
          label=T('Instant messaging notifications')),
    Field('perpage', 'integer', default=20,
          label=T('Preferred lines per page')),
    Field('im_type', 'integer',
          label=T('Instant messaging protocol'), default=1,
          requires=IS_IN_DB(db, db.im_types.id, "%(im_type)s", zero=T('choose one'))),
    Field('im_username', 'string', label=T("Instant messaging user name")),
    Field('im_log_level', 'string', default="critical", label=T("Instant messaging log level"),
          requires=IS_IN_SET(["debug", "info", "warning", "error", "critical"])),
    Field('email_log_level', 'string', default="critical", label=T("Email messaging log level"),
          requires=IS_IN_SET(["debug", "info", "warning", "error", "critical"])),
    Field('lock_filter', 'boolean', default=False,
          label=T("Lock user's session filter"),
          writable=False, readable=False),
]

if ldap_mode:
    login_form_username = True

auth.define_tables(migrate=False, username=login_form_username)

if ldap_mode:
    from applications.init.modules.ldap_auth import ldap_auth
    auth.settings.actions_disabled=['register','change_password','request_reset_password','retrieve_username','profile']
    kwargs = {}
    kwargs["mode"] = ldap_mode
    kwargs["db"] = db
    kwargs["manage_user"] = True
    kwargs["user_firstname_attrib"]='givenName'
    kwargs["user_lastname_attrib"]='sn'
    kwargs["server"] = config_get("ldap_server", None)
    kwargs["base_dn"] = config_get("ldap_base_dn", None)
    allowed_groups = config_get("ldap_allowed_groups", None)
    group_dn = config_get("ldap_group_dn", None)
    if allowed_groups and group_dn:
        kwargs["allowed_groups"] = allowed_groups
        kwargs["group_dn"] = group_dn
	kwargs["group_name_attrib"] = config_get("ldap_group_name_attrib", "cn")
	kwargs["group_member_attrib"] = config_get("ldap_group_member_attrib", "memberUid")
	kwargs["group_filterstr"] = config_get("ldap_group_filterstr", "objectClass=*")
	kwargs["manage_groups"] = config_get("ldap_manage_groups", False)
	kwargs["group_mapping"] = config_get("ldap_group_mapping", {})
	kwargs["manage_groups_callback"] = [
          lambda: table_modified("auth_membership"),
          lambda: table_modified("auth_group"),
        ]

    bind_dn = config_get("ldap_bind_dn", None)
    if bind_dn:
        kwargs["bind_dn"] = bind_dn
    bind_pw = config_get("ldap_bind_pw", None)
    if bind_pw:
        kwargs["bind_pw"] = bind_pw
    filterstr = config_get("ldap_filter", None)
    if filterstr:
        kwargs["filterstr"] = filterstr
    kwargs["logging_level"] = "debug"
    auth.settings.login_methods.append(ldap_auth(**kwargs))

auth.settings.login_methods.append(node_auth())
auth.messages.logged_in = ''

#crud=Crud(globals(),db)                      # for CRUD helpers using auth
service=Service(globals())                   # for json, xml, jsonrpc, xmlrpc, amfrpc
# crud.settings.auth=auth                      # enforces authorization on crud
# mail.settings.login='username:password'      # your credentials or None
# auth.settings.registration_requires_verification = True
# auth.settings.registration_requires_approval = True
# auth.messages.verify_email = \
#  'Click on the link http://.../user/verify_email/%(key)s to verify your email'
mail_server = config_get("mail_server", "localhost:25")
mail_sender = config_get("mail_sender", "admin@opensvc.com")
mail_login = config_get("mail_login", None)
mail_tls = config_get("mail_tls", False)

mail=Mail()
mail.settings.server = mail_server
mail.settings.sender = mail_sender
mail.settings.login = mail_login
mail.settings.tls = mail_tls
auth.settings.mailer = mail

default_max_lines = 1000
default_limitby = (0, default_max_lines)

db.define_table('svcmon',
    Field('svc_id', 'string', length=36),
    Field('node_id', 'string', length=36),
    Field('mon_svctype'),
    Field('mon_ipstatus'),
    Field('mon_fsstatus'),
    Field('mon_containerstatus'),
    Field('mon_diskstatus'),
    Field('mon_sharestatus'),
    Field('mon_syncstatus'),
    Field('mon_hbstatus'),
    Field('mon_appstatus'),
    Field('mon_availstatus'),
    Field('mon_overallstatus'),
    Field('mon_updated', 'datetime'),
    Field('mon_changed'),
    Field('mon_frozen'),
    Field('mon_vmname'),
    Field('mon_vmtype'),
    Field('mon_guestos'),
    Field('mon_vmem'),
    Field('mon_vcpus'),
    Field('mon_containerpath'),
    migrate=False)

db.define_table('svcactions',
    Field('version'),
    Field('action'),
    Field('status'),
    Field('time'),
    Field('begin','datetime'),
    Field('end','datetime'),
    Field('svc_id', 'string', length=36),
    Field('node_id', 'string', length=36),
    Field('hostid'),
    Field('status_log'),
    Field('ack'),
    Field('acked_by'),
    Field('acked_comment'),
    Field('acked_date'),
    Field('pid'),
    Field('cron'),
    migrate=False)

db.define_table('services',
    Field('svcname', 'string'),
    Field('svc_ha'),
    Field('svc_status'),
    Field('svc_availstatus'),
    Field('svc_cluster_type'),
    Field('svc_flex_min_nodes'),
    Field('svc_flex_max_nodes'),
    Field('svc_flex_cpu_low_threshold'),
    Field('svc_flex_cpu_high_threshold'),
    Field('svc_hostid'),
    Field('svc_id', 'string', length=36),
    Field('svc_nodes'),
    Field('svc_drpnode'),
    Field('svc_autostart'),
    Field('svc_env'),
    Field('svc_drpnodes'),
    Field('svc_comment'),
    Field('svc_app'),
    Field('svc_wave'),
    Field('svc_created', 'datetime'),
    Field('updated', 'datetime'),
    Field('svc_status_updated', 'datetime'),
    Field('svc_config_updated'),
    Field('svc_containertype'),
    Field('svc_config'),
    migrate=False)

db.define_table('v_svcmon',
    Field('err'),
    Field('svc_ha'),
    Field('svc_cluster_type'),
    Field('svc_status'),
    Field('svc_availstatus'),
    Field('svc_flex_min_nodes'),
    Field('svc_flex_max_nodes'),
    Field('svc_flex_cpu_low_threshold'),
    Field('svc_flex_cpu_high_threshold'),
    Field('svc_id', 'string', length=36),
    Field('svc_nodes'),
    Field('svc_drpnode'),
    Field('svc_drptype'),
    Field('svc_autostart'),
    Field('svc_env'),
    Field('svc_drpnodes'),
    Field('svc_comment'),
    Field('svc_app'),
    Field('app_domain'),
    Field('app_team_ops'),
    Field('svc_created', 'datetime'),
    Field('svc_updated', 'datetime'),
    Field('svc_config_updated'),
    Field('svc_containertype'),
    Field('svc_id', 'string', length=36),
    Field('svcname', 'string'),
    Field('mon_ipstatus'),
    Field('mon_fsstatus'),
    Field('mon_containerstatus'),
    Field('mon_diskstatus'),
    Field('mon_sharestatus'),
    Field('mon_syncstatus'),
    Field('mon_hbstatus'),
    Field('mon_appstatus'),
    Field('mon_availstatus'),
    Field('mon_overallstatus'),
    Field('mon_updated', 'datetime'),
    Field('mon_changed'),
    Field('mon_frozen'),
    Field('node_updated', 'datetime'),
    Field('warranty_end'),
    Field('maintenance_end'),
    Field('status'),
    Field('role'),
    Field('listener_port'),
    Field('collector'),
    Field('connect_to'),
    Field('version'),
    Field('asset_env'),
    Field('node_env'),
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
    Field('node_id', 'string', length=36),
    Field('nodename'),
    Field('team_responsible'),
    Field('team_integ'),
    Field('team_support'),
    Field('serial'),
    Field('sp_version'),
    Field('bios_version'),
    Field('sp_version'),
    Field('bios_version'),
    Field('model'),
    Field('tz'),
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
    Field('mon_vmname'),
    Field('mon_vmtype'),
    Field('mon_guestos'),
    Field('mon_vmem'),
    Field('mon_vcpus'),
    Field('enclosure'),
    Field('enclosureslot'),
    Field('assetname'),
    Field('cpu_threads'),
    Field('sec_zone'),
    Field('last_boot', 'date'),
    Field('action_type', 'string',
          requires=IS_IN_SET(['push', 'pull']),
    ),
    migrate=False)

db.define_table('drpservices',
    Field('svc_id', 'string', length=36),
    Field('drp_wave'),
    Field('drp_project_id', 'integer'),
    migrate=False)

db.define_table('drpprojects',
    Field('drp_project'),
    Field('drp_project_id', 'integer'),
    primarykey=['drp_project_id'],
    migrate=False)

db.define_table('apps',
    Field('id', 'integer'),
    Field('app', required=True),
    Field('description', 'text'),
    Field('app_domain', 'string'),
    Field('app_team_ops', 'string'),
    Field('updated', 'datetime',
          default=request.now,
          update=request.now),
    migrate=False)

db.define_table('v_apps',
    Field('id', 'integer'),
    Field('app'),
    Field('app_domain', 'string'),
    Field('app_team_ops', 'string'),
    Field('publications'),
    Field('responsibles'),
    migrate=False)

db.define_table('apps_publications',
    Field('id', 'integer'),
    Field('app_id', 'integer'),
    Field('group_id', 'integer'),
    migrate=False)

db.define_table('apps_responsibles',
    Field('id', 'integer'),
    Field('app_id', 'integer'),
    Field('group_id', 'integer'),
    migrate=False)

db.define_table('nodes',
    Field('node_id', 'string', length=36),
    Field('warranty_end', 'datetime', default=request.now),
    Field('maintenance_end', 'datetime', default=request.now),
    Field('status'),
    Field('role'),
    Field('listener_port'),
    Field('version'),
    Field('collector'),
    Field('connect_to'),
    Field('tz'),
    Field('asset_env'),
    Field('node_env', writable=False),
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
    Field('nodename', 'string', length=30, requires=IS_NOT_EMPTY(), unique=True),
    Field('fqdn', 'string'),
    Field('team_responsible'),
    Field('team_integ'),
    Field('team_support'),
    Field('app'),
    Field('serial', writable=False),
    Field('sp_version', writable=False),
    Field('bios_version', writable=False),
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
    Field('updated', 'datetime'),
    Field('enclosure'),
    Field('enclosureslot'),
    Field('assetname'),
    Field('cpu_threads', writable=False),
    Field('sec_zone'),
    Field('last_boot', 'date', writable=False),
    Field('action_type', 'string',
          requires=IS_IN_SET(['push', 'pull']),
    ),
    Field('hvpool'),
    Field('hvvdc'),
    Field('hv'),
    Field('hw_obs_warn_date'),
    Field('hw_obs_alert_date'),
    Field('os_obs_warn_date'),
    Field('os_obs_alert_date'),
    migrate=False)

db.define_table('v_users',
    Field('fullname'),
    Field('manager', 'integer'),
    Field('email'),
    Field('phone_work'),
    Field('last'),
    Field('primary_group'),
    Field('groups'),
    Field('lock_filter'),
    Field('fset_name'),
    Field('quota_app'),
    Field('quota_org_group'),
    migrate=False)

db.define_table('disk_blacklist',
    Field('disk_id', 'string'),
    migrate=False)

db.define_table('diskinfo',
    Field('disk_id', 'string'),
    Field('disk_devid', 'string'),
    Field('disk_name', 'string'),
    Field('disk_alloc', 'integer'),
    Field('disk_arrayid', 'string'),
    Field('disk_size', 'integer'),
    Field('disk_group', 'string'),
    Field('disk_raid', 'string'),
    Field('disk_updated', 'datetime'),
    Field('disk_created', 'datetime'),
    Field('disk_level', 'integer'),
    Field('disk_controller', 'string'),
    migrate=False)

db.define_table('svcdisks',
    Field('disk_id', 'string'),
    Field('svc_id', 'string', length=36),
    Field('node_id', 'string', length=36),
    Field('app_id', 'integer'),
    Field('disk_size', 'integer'),
    Field('disk_used', 'integer'),
    Field('disk_vendor', 'string'),
    Field('disk_model', 'string'),
    Field('disk_dg', 'string'),
    Field('disk_updated', 'datetime'),
    Field('disk_local', 'boolean'),
    Field('disk_region', 'string'),
    migrate=False)

db.define_table('resmon',
    Field('svc_id', 'string', length=36),
    Field('node_id', 'string', length=36),
    Field('vmname'),
    Field('rid'),
    Field('res_type'),
    Field('res_desc'),
    Field('res_status', 'string'),
    Field('res_log'),
    Field('res_optional'),
    Field('res_disable'),
    Field('res_monitor'),
    Field('changed', 'datetime'),
    Field('updated', 'datetime'),
    migrate=False)

db.define_table('svcmon_log',
    Field('id', 'integer'),
    Field('mon_begin','datetime'),
    Field('mon_end','datetime'),
    Field('svc_id', 'string', length=36),
    Field('node_id', 'string', length=36),
    Field('mon_availstatus'),
    Field('mon_overallstatus'),
    Field('mon_ipstatus'),
    Field('mon_fsstatus'),
    Field('mon_diskstatus'),
    Field('mon_sharestatus'),
    Field('mon_containerstatus'),
    Field('mon_syncstatus'),
    Field('mon_hbstatus'),
    Field('mon_appstatus'),
    migrate=False)

db.define_table('svcmon_log_last',
    db.svcmon_log,
    migrate=False)

db.define_table('v_svcmon_log',
    db.svcmon_log,
    migrate=False)

db.define_table('v_obsolescence',
    Field('id', 'integer'),
    Field('obs_type', 'string', length=30),
    Field('obs_name', 'string', length=100),
    Field('obs_warn_date', 'datetime'),
    Field('obs_alert_date', 'datetime'),
    Field('obs_warn_date_updated_by', 'string', length=100),
    Field('obs_alert_date_updated_by', 'string', length=100),
    Field('obs_warn_date_updated', 'datetime'),
    Field('obs_alert_date_updated', 'datetime'),
    Field('obs_count', 'integer'),
    migrate=False)

db.define_table('obsolescence',
    Field('id', 'integer'),
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
    Field('svc_id', 'string', length=36),
    Field('mon_begin', 'datetime'),
    Field('mon_end', 'datetime'),
    Field('mon_comment', 'string'),
    Field('mon_account', 'integer'),
    Field('mon_acked_by', 'string'),
    Field('mon_acked_on', 'datetime'),
    migrate=False)

db.define_table('auth_filters',
    Field('id', 'integer'),
    Field('fil_uid', 'integer'),
    Field('fil_id', 'integer'),
    Field('fil_value', 'string', length=200),
    Field('fil_active', 'tinyint'),
    migrate=False)

db.define_table('filters',
    Field('id', 'integer'),
    Field('fil_name', 'string', length=30),
    Field('fil_column', 'string', length=30),
    Field('fil_need_value', 'boolean'),
    Field('fil_pos', 'integer'),
    Field('fil_table', 'string', length=30),
    Field('fil_search_table', 'string', length=30),
    Field('fil_img', 'string', length=30),
    migrate=False)

db.define_table('stats_fs_u',
    Field('id', 'integer'),
    Field('date', 'datetime'),
    Field('node_id', 'string', length=36),
    Field('mntpt', 'string'),
    Field('size', 'integer'),
    Field('used', 'integer'),
    migrate=False)

db.define_table('stats_cpu',
    Field('id', 'integer'),
    Field('node_id', 'string', length=36),
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
    Field('id', 'integer'),
    Field('date', 'datetime'),
    Field('node_id', 'string', length=36),
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
    Field('id', 'integer'),
    Field('date', 'datetime'),
    Field('node_id', 'string', length=36),
    Field('runq_sz', 'integer'),
    Field('plist_sz', 'integer'),
    Field('ldavg_1', 'float'),
    Field('ldavg_5', 'float'),
    Field('ldavg_15', 'float'),
    migrate=False)

db.define_table('stats_swap',
    Field('id', 'integer'),
    Field('date', 'datetime'),
    Field('node_id', 'string', length=36),
    Field('kbswpfree', 'integer'),
    Field('kbswpused', 'integer'),
    Field('pct_swpused', 'float'),
    Field('pct_swpcad', 'float'),
    Field('kbswpcad', 'integer'),
    migrate=False)

db.define_table('stats_block',
    Field('id', 'integer'),
    Field('date', 'datetime'),
    Field('node_id', 'string', length=36),
    Field('tps', 'float'),
    Field('rtps', 'float'),
    Field('wtps', 'float'),
    Field('rbps', 'float'),
    Field('wbps', 'float'),
    migrate=False)

db.define_table('stats_blockdev',
    Field('id', 'integer'),
    Field('date', 'datetime'),
    Field('node_id', 'string', length=36),
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
    Field('id', 'integer'),
    Field('date', 'datetime'),
    Field('node_id', 'string', length=36),
    Field('dev', 'string', length=8),
    Field('rxerrps', 'float'),
    Field('txerrps', 'float'),
    Field('collps', 'float'),
    Field('rxdropps', 'float'),
    Field('txdropps', 'float'),
    migrate=False)

db.define_table('stats_netdev',
    Field('id', 'integer'),
    Field('date', 'datetime'),
    Field('node_id', 'string', length=36),
    Field('dev', 'string', length=8),
    Field('rxkBps', 'float'),
    Field('txkBps', 'float'),
    Field('rxpckps', 'float'),
    Field('txpckps', 'float'),
    migrate=False)

db.define_table('pkg_sig_provider',
    Field('id', 'integer'),
    Field('sig_id', 'string', length=16),
    Field('sig_provider', 'string', length=32),
    migrate=False)

db.define_table('packages',
    Field('id', 'integer'),
    Field('node_id', 'string', length=36),
    Field('pkg_name', 'string', length=100),
    Field('pkg_version', 'string', length=16),
    Field('pkg_arch', 'string', length=8),
    Field('pkg_type', 'string', length=6),
    Field('pkg_updated', 'datetime'),
    Field('pkg_install_date', 'datetime'),
    Field('pkg_sig', 'string', length=16),
    migrate=False)

db.define_table('patches',
    Field('id', 'integer'),
    Field('node_id', 'string', length=36),
    Field('patch_num', 'string', length=100),
    Field('patch_rev', 'string', length=16),
    Field('patch_updated', 'datetime'),
    Field('patch_install_date', 'datetime'),
    migrate=False)

db.define_table('checks_live',
    Field('id', 'integer'),
    Field('node_id', 'string', length=36),
    Field('svc_id', 'string', length=36),
    Field('chk_instance', 'string', length=60),
    Field('chk_type', 'string', length=10),
    Field('chk_updated', 'datetime'),
    Field('chk_created', 'datetime'),
    Field('chk_value', 'integer'),
    Field('chk_low', 'integer'),
    Field('chk_high', 'integer'),
    Field('chk_err', 'integer'),
    Field('chk_threshold_provider', 'string', length=60),
    migrate=False)

db.define_table('checks_defaults',
    Field('chk_type', 'string', length=10, writable=False),
    Field('chk_inst', 'string', length=128),
    Field('chk_low', 'integer'),
    Field('chk_high', 'integer'),
    Field('chk_prio', 'integer'),
    migrate=False)

db.define_table('checks_settings',
    Field('node_id', 'string', length=36),
    Field('svc_id', 'string', length=36),
    Field('chk_instance', 'string', length=60, writable=False),
    Field('chk_type', 'string', length=10, writable=False),
    Field('chk_changed', 'datetime', writable=False),
    Field('chk_changed_by', 'string', length=60, writable=False),
    Field('chk_low', 'integer'),
    Field('chk_high', 'integer'),
    migrate=False)

db.define_table('billing',
    Field('bill_os_name', 'string'),
    Field('bill_min_svc', 'integer'),
    Field('bill_max_svc', 'integer'),
    Field('bill_env', 'string'),
    Field('bill_cost', 'integer'),
    migrate=False)

db.define_table('billing_agent',
    Field('bill_os_name', 'string'),
    Field('bill_min_agt', 'integer'),
    Field('bill_max_agt', 'integer'),
    Field('bill_env', 'string'),
    Field('bill_cost', 'integer'),
    migrate=False)

db.define_table('lifecycle_os',
    Field('id', 'integer'),
    Field('fset_id', 'integer'),
    Field('lc_os_concat', 'string'),
    Field('lc_os_vendor', 'string'),
    Field('lc_os_name', 'string'),
    Field('lc_count', 'integer'),
    Field('lc_date', 'date'),
    migrate=False)

db.define_table('v_lifecycle_os_name',
    Field('id', 'integer'),
    Field('fset_id', 'integer'),
    Field('lc_os_name', 'string'),
    Field('lc_count', 'integer'),
    Field('lc_date', 'date'),
    migrate=False)

db.define_table('user_prefs_columns',
    Field('id', 'integer'),
    Field('upc_user_id', 'integer'),
    Field('upc_table', 'string'),
    Field('upc_field', 'string'),
    Field('upc_visible', 'integer'),
    migrate=False)

db.define_table('upc_dashboard',
    Field('id', 'integer'),
    Field('upc_user_id', 'integer'),
    Field('upc_dashboard', 'string'),
    migrate=False)

db.define_table('sym_upload',
    Field('archive','upload', requires=IS_NOT_EMPTY()),
    Field('batched','integer', writable=False),
    migrate=False)

db.define_table('v_comp_modulesets',
    Field('modset_id','integer'),
    Field('modset_name','string'),
    Field('modset_author','string'),
    Field('modset_updated','datetime'),
    Field('id','integer'),
    Field('modset_mod_name','string'),
    Field('modset_mod_author','string'),
    Field('modset_mod_updated','datetime'),
    Field('autofix','boolean', default=False),
    Field('teams_responsible','string'),
    Field('teams_publication','string'),
    migrate=False)

db.define_table('comp_moduleset',
    Field('modset_name','string'),
    Field('modset_author','string'),
    Field('modset_updated','datetime'),
    migrate=False)

db.define_table('comp_moduleset_modules',
    Field('modset_id','integer'),
    Field('modset_mod_name','string'),
    Field('modset_mod_author','string'),
    Field('modset_mod_updated','datetime'),
    Field('autofix','boolean', default=False),
    migrate=False)

db.define_table('comp_log',
    Field('run_module','string'),
    Field('node_id', 'string', length=36),
    Field('svc_id', 'string', length=36),
    Field('run_status','integer'),
    Field('run_log','string'),
    Field('run_date','datetime'),
    Field('run_action','string'),
    Field('rset_md5','string'),
    migrate=False)

db.define_table('comp_log_daily',
    Field('run_module','string'),
    Field('node_id', 'string', length=36),
    Field('svc_id', 'string', length=36),
    Field('run_status','integer'),
    Field('run_date','date'),
    migrate=False)

db.define_table('comp_status',
    Field('run_module','string'),
    Field('node_id', 'string', length=36),
    Field('svc_id', 'string', length=36),
    Field('run_status','integer'),
    Field('run_log','string'),
    Field('run_date','datetime'),
    Field('run_action','string'),
    Field('rset_md5','string'),
    migrate=False)

db.define_table('comp_svc_status',
    Field('svc_id', 'string', length=36),
    Field('total','integer'),
    Field('ok','integer'),
    Field('nok','integer'),
    Field('na','integer'),
    Field('obs','integer'),
    Field('pct','integer'),
    migrate=False)

db.define_table('comp_node_status',
    Field('node_name','string'),
    Field('total','integer'),
    Field('ok','integer'),
    Field('nok','integer'),
    Field('na','integer'),
    Field('obs','integer'),
    Field('pct','integer'),
    migrate=False)

db.define_table('comp_mod_status',
    Field('mod_name','string'),
    Field('total','integer'),
    Field('ok','integer'),
    Field('nok','integer'),
    Field('na','integer'),
    Field('obs','integer'),
    Field('pct','integer'),
    migrate=False)

db.define_table('gen_filtersets',
    Field('fset_name','string', requires=IS_NOT_EMPTY()),
    Field('fset_author','string'),
    Field('fset_updated','datetime'),
    Field('fset_stats','boolean', default=False),
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
    Field('f_label','string', readable=False, writable=False),
    migrate=False)

db.define_table('v_gen_filtersets',
    db.gen_filtersets,
    db.gen_filtersets_filters,
    db.gen_filters,
    Field('encap_fset_name','string'),
    Field('join_id','integer'),
    Field('fset_id','integer'),
    Field('fset_stats','boolean', default=False),
    migrate=False)

db.define_table('comp_rulesets',
    Field('ruleset_name','string', requires=IS_NOT_EMPTY()),
    Field('ruleset_type','string', requires=IS_IN_SET(['contextual','explicit'])),
    Field('ruleset_public','boolean', default=True),
    migrate=False)

db.define_table('comp_rulesets_rulesets',
    Field('parent_rset_id','integer'),
    Field('child_rset_id','integer'),
    migrate=False)

db.define_table('comp_moduleset_moduleset',
    Field('parent_modset_id','integer'),
    Field('child_modset_id','integer'),
    migrate=False)

db.define_table('comp_moduleset_ruleset',
    Field('modset_id','integer'),
    Field('ruleset_id','integer'),
    migrate=False)

db.define_table('comp_rulesets_filtersets',
    Field('ruleset_id','integer', requires=IS_NOT_EMPTY()),
    Field('fset_id','integer', requires=IS_NOT_EMPTY()),
    migrate=False)

db.define_table('comp_rulesets_nodes',
    Field('ruleset_id','integer', requires=IS_NOT_EMPTY()),
    Field('node_id', 'string', length=36, requires=IS_NOT_EMPTY()),
    migrate=False)

db.define_table('comp_rulesets_services',
    Field('ruleset_id','integer', requires=IS_NOT_EMPTY()),
    Field('svc_id', 'string', length=36),
    Field('slave','boolean'),
    migrate=False)

db.define_table('v_comp_rulesets',
    Field('ruleset_id','integer'),
    Field('fset_id','integer'),
    Field('encap_rset','string'),
    Field('encap_rset_id','integer'),
    Field('chain_len','integer'),
    Field('chain','text'),
    Field('ruleset_name','string', requires=IS_NOT_EMPTY()),
    Field('ruleset_type','string', requires=IS_IN_SET(['contextual','explicit'])),
    Field('ruleset_public','boolean', default=True),
    Field('teams_responsible','string'),
    Field('teams_publication','string'),
    Field('fset_name','string'),
    Field('var_class','string'),
    Field('var_name','string'),
    Field('var_value','text'),
    Field('var_author','string', readable=False, writable=False),
    Field('var_updated','datetime', readable=False, writable=False),
    migrate=False)

db.define_table('comp_ruleset_team_responsible',
    Field('ruleset_id','integer'),
    Field('group_id','integer'),
    migrate=False)

db.define_table('comp_ruleset_team_publication',
    Field('ruleset_id','integer'),
    Field('group_id','integer'),
    migrate=False)

db.define_table('comp_node_moduleset',
    Field('node_id', 'string', length=36),
    Field('modset_id','integer'),
    Field('modset_updated','datetime'),
    Field('modset_mod_author','string'),
    migrate=False)

db.define_table('comp_modulesets_services',
    Field('svc_id', 'string', length=36),
    Field('modset_id','integer'),
    Field('modset_updated','datetime'),
    Field('modset_mod_author','string'),
    Field('slave','boolean'),
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
    Field('ruleset_id','integer'),
    Field('ruleset_name','string'),
    Field('modset_id','integer'),
    Field('modset_name','string'),
    migrate=False)

db.define_table('v_comp_services',
    db.services,
    Field('encap','boolean'),
    Field('ruleset_id','integer'),
    Field('ruleset_name','string'),
    Field('modset_id','integer'),
    Field('modset_name','string'),
    migrate=False)

db.define_table('v_comp_explicit_rulesets',
    Field('ruleset_name','string'),
    Field('variables','string'),
    migrate=False)

db.define_table('log',
    Field('log_action','string'),
    Field('log_user','string'),
    Field('svc_id', 'string', length=36),
    Field('node_id', 'string', length=36),
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
    Field('bookmark','string'),
    migrate=False)

db.define_table('wiki_pages',
    Field('name', writable=False, requires=IS_NOT_IN_DB(db,'wiki_pages.name')),
    Field('author', db.auth_user, readable=False, writable=False),
    Field('saved_on', 'datetime', readable=False, writable=False),
    Field('title'),
    Field('body', 'text'),
    Field('change_note', length=200),
    migrate=False)

db.define_table('v_action_queue',
    Field('status', 'string'),
    Field('ret', 'integer'),
    Field('user_id', 'integer'),
    Field('form_id', 'integer'),
    Field('command', 'text'),
    Field('stdout', 'text'),
    Field('stderr', 'text'),
    Field('date_queued', 'datetime'),
    Field('date_dequeued', 'datetime'),
    Field('nodename', 'string'),
    Field('svcname', 'string'),
    Field('node_id', 'string', length=36),
    Field('svc_id', 'string', length=36),
    Field('username', 'string'),
    Field('action_type', 'string'),
    Field('connect_to', 'string'),
    migrate=False)

db.define_table('action_queue',
    Field('status', 'string'),
    Field('ret', 'integer'),
    Field('user_id', 'integer'),
    Field('command', 'text'),
    Field('stdout', 'text'),
    Field('stderr', 'text'),
    Field('date_queued', 'datetime'),
    Field('date_dequeued', 'datetime'),
    Field('node_id', 'string', length=36),
    Field('svc_id', 'string', length=36),
    Field('action_type', 'string'),
    Field('form_id', 'integer'),
    Field('connect_to', 'string'),
    migrate=False)

db.define_table('v_outdated_services',
    Field('svc_id', 'string', length=36),
    Field('uptodate', 'integer'),
    migrate=False)

db.define_table('services_log',
    Field('svc_id', 'string', length=36),
    Field('svc_availstatus', 'string'),
    Field('svc_begin', 'datetime'),
    Field('svc_end', 'datetime'),
    migrate=False)

db.define_table('services_log_last',
    db.services_log,
    migrate=False)

db.define_table('v_services_log',
    db.services_log,
    migrate=False)

db.define_table('resmon_log',
    Field('node_id', 'string', length=36),
    Field('svc_id', 'string', length=36),
    Field('rid', 'string'),
    Field('res_status', 'string'),
    Field('res_begin', 'datetime'),
    Field('res_end', 'datetime'),
    migrate=False)

db.define_table('resmon_log_last',
    db.resmon_log,
    migrate=False)

db.define_table('v_resmon_log',
    db.resmon_log,
    migrate=False)

db.define_table('auth_node',
    Field('nodename', 'string'),
    Field('uuid', 'string'),
    Field('updated', 'datetime'),
    Field('node_id', 'string', length=36),
    migrate=False)

db.define_table('v_gen_filterset_teams_responsible',
    Field('fset_id', 'integer'),
    Field('teams_responsible', 'string'),
    migrate=False)

db.define_table('comp_moduleset_team_publication',
    Field('modset_id','integer'),
    Field('group_id','integer'),
    migrate=False)

db.define_table('comp_moduleset_team_responsible',
    Field('modset_id','integer'),
    Field('group_id','integer'),
    migrate=False)

db.define_table('gen_filterset_team_responsible',
    Field('fset_id','integer'),
    Field('group_id','integer'),
    migrate=False)

db.define_table('gen_filterset_check_threshold',
    Field('fset_id','integer'),
    Field('chk_type','string'),
    Field('chk_instance','string'),
    Field('chk_low','integer'),
    Field('chk_high','integer'),
    migrate=False)

db.define_table('v_gen_filterset_check_threshold',
    Field('fset_id','integer'),
    Field('chk_type','string'),
    Field('chk_instance','string'),
    Field('chk_low','integer'),
    Field('chk_high','integer'),
    Field('name','string'),
    migrate=False)

db.define_table('forms_team_responsible',
    Field('form_id','integer'),
    Field('group_id','integer'),
    migrate=False)

db.define_table('forms_team_publication',
    Field('form_id','integer'),
    Field('group_id','integer'),
    migrate=False)

db.define_table('v_forms',
    Field('form_name','string'),
    Field('form_team_responsible','string'),
    Field('form_team_publication','string'),
    Field('form_type','string', requires=IS_IN_SET(("generic", "custo", "folder", "obj")), default="custo"),
    Field('form_yaml','text'),
    Field('form_folder','string'),
    Field('form_author','string'),
    Field('form_created','datetime'),
    migrate=False)

db.define_table('forms',
    Field('form_name','string'),
    Field('form_type','string', requires=IS_IN_SET(("generic", "custo", "folder", "obj")), default="custo"),
    Field('form_yaml','text'),
    Field('form_folder','string'),
    Field('form_author','string'),
    Field('form_created','datetime'),
    migrate=False)

db.define_table('comp_rulesets_variables',
    Field('ruleset_id','integer', requires=IS_NOT_EMPTY()),
    Field('var_class','string', default="raw"),
    Field('var_name','string', requires=IS_NOT_EMPTY()),
    Field('var_value','text'),
    Field('var_author','string', readable=False, writable=False),
    Field('var_updated','datetime', readable=False, writable=False),
    migrate=False)

db.define_table('prov_templates',
    Field('tpl_name','string'),
    Field('tpl_definition','text'),
    Field('tpl_comment','text'),
    Field('tpl_author','string'),
    Field('tpl_created','datetime'),
    migrate=False)

db.define_table('v_prov_templates',
    Field('tpl_name','string'),
    Field('tpl_definition','text'),
    Field('tpl_comment','text'),
    Field('tpl_author','string'),
    Field('tpl_created','datetime'),
    Field('tpl_team_responsible','string'),
    Field('tpl_team_publication','string'),
    migrate=False)

db.define_table('prov_template_team_responsible',
    Field('tpl_id','integer'),
    Field('group_id','integer'),
    migrate=False)

db.define_table('prov_template_team_publication',
    Field('tpl_id','integer'),
    Field('group_id','integer'),
    migrate=False)

db.define_table('networks',
    Field('name','string'),
    Field('network','string', requires=IS_NOT_EMPTY()),
    Field('broadcast','string', writable=False),
    Field('comment','text'),
    Field('gateway','string'),
    Field('begin','string', writable=False),
    Field('end','string', writable=False),
    Field('pvid','integer'),
    Field('updated','datetime'),
    Field('netmask','integer',
          requires=IS_INT_IN_RANGE(0, 33)),
    Field('prio','integer', default=0, requires=IS_NULL_OR(IS_INT_IN_RANGE(0,100))),
    Field('team_responsible','string',
          requires=IS_IN_DB(db((db.auth_group.privilege=="F")&(~db.auth_group.role.like("user_%"))), db.auth_group.role, "%(role)s", zero=T('choose team'))),
    migrate=False)

db.networks.name.requires = IS_NULL_OR(IS_NOT_IN_DB(db, db.networks.name))

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

db.define_table('resinfo',
    Field('svc_id', 'string', length=36),
    Field('node_id', 'string', length=36),
    Field('rid','string'),
    Field('res_key','string'),
    Field('res_value','string'),
    Field('updated','datetime'),
    migrate=False)

db.define_table('resinfo_log',
    db.resinfo,
    migrate=False)

db.define_table('dashboard',
    Field('dash_type','string'),
    Field('svc_id', 'string', length=36),
    Field('node_id', 'string', length=36),
    Field('dash_severity','integer'),
    Field('dash_fmt','string'),
    Field('dash_dict','string'),
    Field('dash_created','datetime'),
    Field('dash_updated','datetime'),
    Field('dash_env','string'),
    Field('dash_md5','string'),
    migrate=False)

db.define_table('dashboard_events',
    Field('svc_id', 'string', length=36),
    Field('node_id', 'string', length=36),
    Field('dash_begin','datetime'),
    Field('dash_end','datetime'),
    Field('dash_md5','string'),
    migrate=False)

db.define_table('dashboard_ref',
    Field('dash_type','string'),
    Field('dash_fmt','string'),
    Field('dash_dict','string'),
    Field('dash_md5','string'),
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
    Field('node_id', 'string', length=36),
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
    Field('array_level','integer'),
    migrate=False)

db.define_table('stor_array_dg',
    Field('array_id','integer'),
    Field('dg_name','string'),
    Field('dg_free','integer'),
    Field('dg_used','integer'),
    Field('dg_size','integer'),
    Field('dg_reserved','integer'),
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
    Field('node_id', 'string', length=36),
    Field('updated','datetime'),
    migrate=False)

db.define_table('stor_array_proxy',
    Field('array_id','integer'),
    Field('node_id', 'string', length=36),
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
    Field('dg_reserved','integer'),
    Field('dg_reservable','integer'),
    Field('app','string'),
    Field('quota','integer'),
    Field('quota_used','integer'),
    Field('dg_id','integer'),
    Field('array_id','integer'),
    Field('app_id','integer'),
    migrate=False)

db.define_table('stat_day_disk_app_dg',
    Field('app','string'),
    Field('dg_id','integer'),
    Field('day','datetime'),
    Field('disk_used','integer'),
    Field('quota','integer'),
    migrate=False)

db.define_table('stat_day_disk_app',
    Field('app','string'),
    Field('day','datetime'),
    Field('disk_used','integer'),
    Field('quota','integer'),
    migrate=False)

db.define_table('stat_day_disk_array',
    Field('array_name','string'),
    Field('day','datetime'),
    Field('disk_used','integer'),
    Field('disk_size','integer'),
    Field('reserved','integer'),
    Field('reservable','integer'),
    migrate=False)

db.define_table('stat_day_disk_array_dg',
    Field('array_name','string'),
    Field('array_dg','string'),
    Field('day','datetime'),
    Field('disk_used','integer'),
    Field('disk_size','integer'),
    Field('reserved','integer'),
    Field('reservable','integer'),
    migrate=False)

db.define_table('v_switches',
    Field('node_id', 'string', length=36),
    Field('sw_name', 'string'),
    Field('sw_fabric', 'string'),
    Field('sw_index', 'integer'),
    Field('sw_slot', 'integer'),
    Field('sw_port', 'integer'),
    Field('sw_portspeed', 'integer'),
    Field('sw_portnego', 'boolean'),
    Field('sw_portstate', 'string'),
    Field('sw_porttype', 'string'),
    Field('sw_portname', 'string'),
    Field('sw_rportname', 'string'),
    Field('sw_updated', 'datetime'),
    Field('sw_rname', 'string'),
    migrate=False)

db.define_table('switches',
    Field('sw_name', 'string'),
    Field('sw_fabric', 'string'),
    Field('sw_index', 'integer'),
    Field('sw_slot', 'integer'),
    Field('sw_port', 'integer'),
    Field('sw_portspeed', 'integer'),
    Field('sw_portnego', 'boolean'),
    Field('sw_portstate', 'string'),
    Field('sw_porttype', 'string'),
    Field('sw_portname', 'string'),
    Field('sw_rportname', 'string'),
    Field('sw_updated', 'datetime'),
    migrate=False)

db.define_table('node_ip',
    Field('node_id', 'string', length=36),
    Field('mac', 'string'),
    Field('intf', 'string'),
    Field('type', 'string'),
    Field('addr', 'string'),
    Field('mask', 'string'),
    Field('updated', 'datetime'),
    Field('flag_deprecated', 'boolean'),
    migrate=False)

db.define_table('san_zone',
    Field('cfg', 'string'),
    Field('zone', 'string'),
    Field('port', 'string'),
    Field('updated', 'datetime'),
    migrate=False)

db.define_table('san_zone_alias',
    Field('cfg', 'string'),
    Field('alias', 'string'),
    Field('port', 'string'),
    Field('updated', 'datetime'),
    migrate=False)

db.define_table('stat_day_billing',
    Field('day', 'datetime'),
    Field('fset_id', 'integer'),
    Field('os_name', 'string'),
    Field('nb_svc_prd', 'integer'),
    Field('nb_svc_nonprd', 'integer'),
    Field('nb_agents_without_svc_prd', 'integer'),
    Field('nb_agents_without_svc_nonprd', 'integer'),
    migrate=False)

db.define_table('saves',
    Field('save_date', 'datetime'),
    Field('save_retention', 'datetime'),
    Field('save_size', 'integer'),
    Field('node_id', 'string', length=36),
    Field('svc_id', 'string', length=36),
    Field('save_name', 'string'),
    Field('save_group', 'string'),
    Field('save_volume', 'string'),
    Field('save_level', 'string'),
    Field('save_server', 'string'),
    Field('save_app', 'string'),
    Field('save_id', 'string'),
    migrate=False)

db.define_table('v_forms_store',
    Field('id', 'integer'),
    Field('form_submit_date', 'datetime'),
    Field('form_next_id', 'integer'),
    Field('form_prev_id', 'integer'),
    Field('form_head_id', 'integer'),
    Field('form_var_id', 'integer'),
    Field('form_submitter', 'string'),
    Field('form_assignee', 'string'),
    Field('form_md5', 'string'),
    Field('form_data', 'text'),
    Field('form_scripts', 'text'),
    Field('form_id', 'integer'),
    Field('form_yaml', 'text'),
    Field('form_name', 'string'),
    Field('form_folder', 'string'),
    Field('form_date', 'datetime'),
    migrate=False)

db.define_table('forms_store',
    Field('id', 'integer'),
    Field('form_submit_date', 'datetime'),
    Field('form_next_id', 'integer'),
    Field('form_prev_id', 'integer'),
    Field('form_head_id', 'integer'),
    Field('form_var_id', 'integer'),
    Field('form_submitter', 'string'),
    Field('form_assignee', 'string'),
    Field('form_md5', 'string'),
    Field('form_data', 'text'),
    Field('form_scripts', 'text'),
    migrate=False)

db.define_table('forms_store_archive',
    db.forms_store,
    migrate=False)

db.define_table('forms_revisions',
    Field('id', 'integer'),
    Field('form_id', 'integer'),
    Field('form_md5', 'string'),
    Field('form_yaml', 'text'),
    Field('form_name', 'string'),
    Field('form_folder', 'string'),
    migrate=False)

db.define_table('workflows',
    Field('id', 'integer'),
    Field('form_head_id', 'integer'),
    Field('form_md5', 'string'),
    Field('status', 'string'),
    Field('steps', 'integer'),
    Field('creator', 'string'),
    Field('create_date', 'datetime'),
    Field('last_assignee', 'string'),
    Field('last_update', 'datetime'),
    Field('last_form_id', 'integer'),
    Field('last_form_name', 'string'),
    migrate=False)

db.define_table('metrics',
    Field('id', 'integer'),
    Field('metric_name', 'string'),
    Field('metric_sql', 'text'),
    Field('metric_created', 'datetime'),
    Field('metric_author', 'string'),
    Field('metric_col_value_index', 'integer'),
    Field('metric_col_instance_index', 'integer'),
    Field('metric_col_instance_label', 'string'),
    Field('metric_historize', 'boolean'),
    migrate=False)

db.define_table('metrics_log',
    Field('metric_id', 'integer'),
    Field('fset_id', 'integer'),
    Field('value', 'float'),
    Field('date', 'date'),
    Field('instance', 'string'),
    migrate=False)

db.define_table('charts',
    Field('id', 'integer'),
    Field('chart_name', 'string'),
    Field('chart_yaml', 'text'),
    migrate=False)

db.define_table('reports',
    Field('id', 'integer'),
    Field('report_name', 'string'),
    Field('report_yaml', 'text'),
    migrate=False)

db.define_table('reports_user',
    Field('report_id','integer'),
    Field('user_id','integer'),
    migrate=False)

db.define_table('comp_rulesets_chains',
    Field('head_rset_id','integer'),
    Field('tail_rset_id','integer'),
    Field('chain_len','integer'),
    Field('chain','text'),
    migrate=False)

db.define_table('v_nodenetworks',
    Field('warranty_end', 'datetime', default=request.now),
    Field('maintenance_end', 'datetime', default=request.now),
    Field('status'),
    Field('role'),
    Field('node_id', 'string', length=36),
    Field('asset_env'),
    Field('listener_port'),
    Field('version'),
    Field('node_env', writable=False),
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
    Field('fqdn', 'string'),
    Field('team_responsible'),
    Field('team_integ'),
    Field('team_support'),
    Field('app'),
    Field('serial', writable=False),
    Field('sp_version', writable=False),
    Field('bios_version', writable=False),
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
    Field('updated', 'datetime'),
    Field('enclosure'),
    Field('enclosureslot'),
    Field('assetname'),
    Field('cpu_threads'),
    Field('sec_zone'),
    Field('last_boot', 'date'),
    Field('action_type', 'string',
          requires=IS_IN_SET(['push', 'pull']),
    ),
    Field('hvpool'),
    Field('hvvdc'),
    Field('hv'),
    Field('hw_obs_warn_date'),
    Field('hw_obs_alert_date'),
    Field('os_obs_warn_date'),
    Field('os_obs_alert_date'),
    Field('mac', 'string'),
    Field('intf', 'string'),
    Field('addr_type', 'string'),
    Field('addr', 'string'),
    Field('mask', 'string'),
    Field('flag_deprecated', 'boolean'),
    Field('addr_updated', 'datetime'),
    Field('net_id','integer'),
    Field('prio','integer'),
    Field('net_name','string'),
    Field('net_network','string'),
    Field('net_broadcast','string'),
    Field('net_comment','text'),
    Field('net_gateway','string'),
    Field('net_begin','string'),
    Field('net_end','string'),
    Field('net_pvid','integer'),
    Field('net_netmask','integer'),
    Field('net_team_responsible','string'),
    migrate=False)

db.define_table('v_nodesan',
    Field('warranty_end', 'datetime', default=request.now),
    Field('maintenance_end', 'datetime', default=request.now),
    Field('status'),
    Field('role'),
    Field('asset_env'),
    Field('listener_port'),
    Field('version'),
    Field('node_env', writable=False),
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
    Field('node_id'),
    Field('nodename', writable=False),
    Field('fqdn', 'string'),
    Field('team_responsible'),
    Field('team_integ'),
    Field('team_support'),
    Field('app'),
    Field('serial', writable=False),
    Field('sp_version', writable=False),
    Field('bios_version', writable=False),
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
    Field('node_updated', 'datetime'),
    Field('enclosure'),
    Field('enclosureslot'),
    Field('assetname'),
    Field('cpu_threads'),
    Field('sec_zone'),
    Field('last_boot', 'date'),
    Field('action_type', 'string',
          requires=IS_IN_SET(['push', 'pull']),
    ),
    Field('hvpool'),
    Field('hvvdc'),
    Field('hv'),
    Field('hw_obs_warn_date'),
    Field('hw_obs_alert_date'),
    Field('os_obs_warn_date'),
    Field('os_obs_alert_date'),
    Field('tgt_id', 'string'),
    Field('hba_id', 'string'),
    Field('array_name', 'string'),
    Field('array_model', 'string'),
    Field('array_cache', 'integer'),
    Field('array_level', 'integer'),
    Field('array_firmware', 'string'),
    Field('array_updated', 'datetime'),
    migrate=False)

db.define_table('node_users',
    Field('user_id','integer'),
    Field('user_name','string'),
    Field('node_id', 'string', length=36),
    Field('updated', 'datetime'),
    migrate=False)

db.define_table('node_groups',
    Field('group_id','integer'),
    Field('group_name','string'),
    Field('node_id', 'integer'),
    Field('updated', 'datetime'),
    migrate=False)

db.define_table('v_uids',
    Field('user_id','integer'),
    Field('user_id_count','integer'),
    Field('user_name','string'),
    migrate=False)

db.define_table('v_gids',
    Field('group_id','integer'),
    Field('group_id_count','integer'),
    Field('group_name','string'),
    migrate=False)

db.define_table('group_hidden_menu_entries',
    Field('group_id','integer'),
    Field('menu_entry','string'),
    migrate=False)

db.define_table('sysrep_changing',
    Field('pattern','string'),
    migrate=False)

db.define_table('sysrep_secure',
    Field('pattern','string'),
    migrate=False)

db.define_table('v_sysrep_allow',
    Field('pattern','string'),
    Field('fset_id','integer'),
    Field('group_id','integer'),
    Field('fset_name','string'),
    Field('group_name','string'),
    migrate=False)

db.define_table('sysrep_allow',
    Field('pattern','string'),
    Field('fset_id','integer'),
    Field('group_id','integer'),
    migrate=False)

db.define_table('v_comp_moduleset_attachments',
    Field('node_id','string', length=36),
    Field('svc_id', 'string', length=36),
    Field('modset_name','string'),
    migrate=False)

db.define_table('tags',
    Field('tag_name','string',
          requires=[IS_NOT_EMPTY(), IS_NOT_IN_DB(db, 'tags.tag_name')],
          unique=True),
    Field('tag_id','string'),
    Field('tag_exclude','string'),
    Field('tag_created','datetime', default=request.now, writable=False),
    migrate=False)

db.define_table('node_tags',
    Field('node_id', 'string', length=36),
    Field('tag_id','string'),
    Field('created','datetime'),
    migrate=False)

db.define_table('svc_tags',
    Field('svc_id', 'string', length=36),
    Field('tag_id','string'),
    Field('created','datetime'),
    migrate=False)

db.define_table('v_tags',
    Field('ckid','string'),
    Field('node_id', 'string', length=36),
    Field('svc_id', 'string', length=36),
    Field('tag_id','string'),
    Field('tag_name','string'),
    Field('created','datetime'),
    migrate=False)

db.define_table('v_tags_full',
    db.v_tags,
    Field('nodename','string'),
    Field('svcname','string'),
    migrate=False)

db.define_table('safe',
    Field('uploader','integer'),
    Field('uploaded_from','string'),
    Field('uploaded_date','datetime'),
    Field('name','string'),
    Field('md5','string'),
    Field('size','integer'),
    Field('uuid','upload',
           uploadfolder=os.path.join(request.folder,"uploads/safe"),
           uploadseparate=True),
    migrate=False)

db.define_table('v_safe',
    Field('uploader','integer'),
    Field('uploaded_from','string'),
    Field('uploaded_date','datetime'),
    Field('safe_name','string'),
    Field('md5','string'),
    Field('size','integer'),
    Field('uuid','upload',
           uploadfolder=os.path.join(request.folder,"uploads/safe"),
           uploadseparate=True),
    Field('uploader_name','string'),
    Field('safe_team_responsible','string'),
    Field('safe_team_publication','string'),
    migrate=False)

db.define_table('safe_team_publication',
    Field('file_id','integer', IS_IN_DB(db, db.safe.id)),
    Field('group_id','integer', IS_IN_DB(db, db.auth_group.id)),
    migrate=False)

db.define_table('safe_team_responsible',
    Field('file_id','integer', IS_IN_DB(db, db.safe.id)),
    Field('group_id','integer', IS_IN_DB(db, db.auth_group.id)),
    migrate=False)

db.define_table('v_wiki_events',
    Field('id','integer'),
    Field('name','string'),
    Field('title','string'),
    Field('body','string'),
    Field('change_note','string'),
    Field('saved_on','datetime'),
    Field('email','string'),
    migrate=False)

db.define_table('links',
    Field('id','integer'),
    Field('link_title','string'),
    Field('link_title_args','string'),
    Field('link_function','string'),
    Field('link_parameters','string'),
    Field('link_creation_user_id','integer'),
    Field('link_creation_date','datetime'),
    Field('link_last_consultation_date','datetime'),
    Field('link_md5','string'),
    Field('link_access_counter','integer'),
    migrate=False)

db.define_table('v_scheduler_run',
    Field('id','integer'),
    Field('task_id','integer'),
    Field('duration','integer'),
    Field('timeout','integer'),
    Field('retry_failed','integer'),
    Field('times_run','integer'),
    Field('times_failed','integer'),
    Field('start_time','datetime'),
    Field('stop_time','datetime'),
    Field('run_output','text'),
    Field('run_result','text'),
    Field('traceback','text'),
    Field('args','text'),
    Field('vars','text'),
    Field('function_name','string'),
    Field('application_name','string'),
    Field('status','string'),
    Field('group_name','string'),
    Field('worker_name','string'),
    migrate=False)

db.define_table('docker_registries',
    Field('service', 'string', length=128),
    Field('url', 'string', length=256),
    Field('insecure', 'boolean'),
    Field('restricted', 'boolean'),
    Field('updated', "datetime"),
    Field('created', "datetime"),
    migrate=False)

db.define_table('docker_repositories',
    Field('registry_id', 'integer'),
    Field('repository', 'string', length=255),
    Field('updated', "datetime"),
    Field('created', "datetime"),
    Field('automated', 'boolean'),
    Field('official', 'boolean'),
    Field('stars', 'integer'),
    Field('description', 'string', length=255),
    migrate=False)

db.define_table('docker_tags',
    Field('registry_id', 'integer'),
    Field('repository_id', 'integer'),
    Field('name', 'string', length=255),
    Field('updated', "datetime"),
    Field('created', "datetime"),
    Field('config_digest', 'string', length=72),
    Field('config_size', 'integer'),
    migrate=False)

db.define_table('docker_registries_publications',
    Field('group_id', 'integer'),
    Field('registry_id', 'integer'),
    migrate=False)

db.define_table('docker_registries_responsibles',
    Field('group_id', 'integer'),
    Field('registry_id', 'integer'),
    migrate=False)

db.define_table('form_output_results',
    Field('user_id', 'integer'),
    Field('node_id', 'string'),
    Field('results', 'text'),
    migrate=False)


