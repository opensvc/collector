#!/usr/bin/env python
# coding: utf8

# title to display in the browser tab
title = "Collector TST"

# server timezone
server_timezone = "Europe/Madrid"

# connection to the database
dbopensvc_host = "127.0.0.1"
dbopensvc_user = "opensvc"
dbopensvc_password = "opensvc"

# readonly db access
dbro_host = "127.0.0.1"
dbopensvc_user = "readonly"
dbopensvc_password = "readonly"

# pdns database
dbdns = "pdns"
dbdns_host = "127.0.0.1"
dbdns_user = "opensvc"
dbdns_password = "opensvc"

# the dns zone whose records the collector manages
dns_managed_zone = "opensvc.dom.net"
dns_default_ttl = 120

# connection to the redis
redis_host = "dbopensvc"

# google auth
google_client_id = "0123456789-abcdefghijklmnopqrstuvwxyz012345.apps.googleusercontent.com"
google_client_secret = "TRuz_acPKuiKApq-OsmOTIqC"

# ldap / ad
ldap_mode = "ad"
ldap_server = "ad.my.corp"
ldap_port = 636
ldap_tls = False
ldap_base_dn = ""
ldap_allowed_groups = []
ldap_group_dn = ""
ldap_group_name_attrib= "cn"
ldap_group_member_attrib = "memberUid"
ldap_group_filterstr = "objectClass=*"
ldap_manage_groups = False
ldap_group_mapping = {
  "adgrp": ["CheckExec", "CompExec"]
}
ldap_bind_dn = ""
ldap_bind_pw = ""
ldap_filter = ""
ldap_secure = False
ldap_cacert_file = "/tmp/foo"
ldap_user_firstname_attrib = "cn:1"
ldap_user_lastname_attrib = "cn:2"
ldap_user_mail_attrib = "mail"


http_host = "opensvc.mydomain.com"

# websocket
websocket_url = "http://dbopensvc:8889"
websocket_key = "magix123"

# time between relogin, in seconds
session_expire = 36000000

# refuse node register without a collector user credentials
# default: False
refuse_anon_register = True

# groups to attach to a newly registered user
membership_on_register = [
 "AppManager",
 "GroupManager",
 "SelfManager",
 "NodeManager",
 "NodeExec",
 "CompExec",
 "CheckExec",
 "CheckRefresh",
 "CheckManager",
]

# set to True if newly registered users should have a private app code
# created, for them to register nodes and add services
create_app_on_register = True

# allow users to create their own account
# default: True
allow_register = False

# max billing tokens
# default: unset, meaning unlimited
token_quota = 150000

# default user quota
default_quota_app = 1
default_quota_org_group = 3

# billing tunables
billing_method = "agents"

# callouts
nodejs = "/usr/bin/nodejs"
vm2 = "/usr/local/bin/vm2"

#
# DataCore SAN symphony config
#
sansymphony_v_pool = {
  'local': {
    'sds1_pool1': 'sds1:sds1_pool1',
    'sds2_pool2': 'sds2:sds2_pool2',
  },
  'dcspra2': {
  },
  'dcslmw1': {
  },
}
sansymphony_v_mirrored_pool = {
  'local': {
    'sds1_pool1': 'sds1:sds1_pool1,sds2:sds2_pool2',
    'sds2_pool2': 'sds1:sds1_pool1,sds2:sds2_pool2',
  },
  'dcspra2': {
    'sdsert01_sas_optima3': 'sdsert01:sdsert01_sas_optima3,sdsert02:sdsert02_sas_optima3',
    'sdsert02_sas_optima3': 'sdsert01:sdsert01_sas_optima3,sdsert02:sdsert02_sas_optima3',
  },
  'dcslmw1': {
    'sdslmw01_miroir_n2_argent': 'sdslmw01:sdslmw01_miroir_n2_argent,sdslmw03:sdslmw03_miroir_n3_argent',
    'sdslmw03_miroir_n3_argent': 'sdslmw01:sdslmw01_miroir_n2_argent,sdslmw03:sdslmw03_miroir_n3_argent',
    'sdslmw01_miroir_n2_or': 'sdslmw01:sdslmw01_miroir_n2_or,sdslmw03:sdslmw03_miroir_n3_or',
    'sdslmw03_miroir_n3_or': 'sdslmw01:sdslmw01_miroir_n2_or,sdslmw03:sdslmw03_miroir_n3_or',
    'sdslmw01_miroir_n2_platine': 'sdslmw01:sdslmw01_miroir_n2_platine,sdslmw03:sdslmw03_miroir_n3_platine',
    'sdslmw03_miroir_n3_platine': 'sdslmw01:sdslmw01_miroir_n2_platine,sdslmw03:sdslmw03_miroir_n3_platine',
  },
}

# default number of days before stats data purge
stats_retention_days = 367

# per table retention. takes precedence over stats_retention_days
retentions = {
 'comp_log': 365,
 'appinfo_log': 365,
 'SVCactions': 365,
 'services_log': 700,
 'dashboard_events': 165,
}

# mail sending configuration (alertd, web2py)
email = True
email_from = "admin@localhost"
email_host = "localhost"
email_port = 465
email_ssl = True
email_tls = False
email_login = me:1234

xmpp = True
xmpp_username = "opensvc"
xmpp_password = "opensvc"
xmpp_host = "talk.google.com"
xmpp_port = 5223

slack = True
slack_webhook_url = "https://hooks.slack.com/services/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"

# actiond
actiond_workers = 5

# a prefix added to the ssh command
remote_command_prepend = []

# only defined to ease the declaration of 'remote_cmd_ssh'
cmd_ssh = ['ssh', '-o', 'StrictHostKeyChecking=no',
                  '-o', 'CheckHostIP=no',
                  '-o', 'ForwardX11=no',
                  '-o', 'ConnectTimeout=5',
                  '-o', 'PasswordAuthentication=no']

# use this command for remote actions via ssh instead of the default one. per-os.
remote_cmd_ssh = {
    "Linux": cmd_ssh,
    "SunOS": cmd_ssh,
}

# JWT server for registries: key/cert to encode the tokens with.
# If self-signed the crt must be trusted by the registry via the container's
# REGISTRY_AUTH_TOKEN_ROOTCERTBUNDLE env var
registry_jwt_key = "/opt/web2py/applications/init/private/ssl/server.key"
registry_jwt_crt = "/opt/web2py/applications/init/private/ssl/server.crt"
registry_jwt_issuer = "opensvc"

custom_get_handlers = {"mycorp": ["rest_get_mycorp_custohandler"]}
custom_delete_handlers = {"mycorp": ["rest_delete_mycorp_custohandler"]}
custom_post_handlers = {"mycorp": ["rest_post_mycorp_custohandler"]}
custom_put_handlers = {"mycorp": ["rest_put_mycorp_custohandler"]}
