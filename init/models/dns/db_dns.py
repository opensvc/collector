from applications.init.modules import config

if hasattr(config, 'dbdns'):
    dbdns = config.dbdns
else:
    dbdns = 'pdns'

if hasattr(config, 'dbdns_host'):
    dbdns_host = config.dbdns_host
else:
    dbdns_host = dbopensvc

if hasattr(config, 'dbdns_user'):
    dbdns_user = config.dbdns_user
else:
    dbdns_user = 'pdns'

if hasattr(config, 'dbdns_password'):
    dbdns_password = config.dbdns_password
else:
    dbdns_password = 'pdns'

try:
    dbdns = DAL('mysql://%s:%s@%s/%s' % (dbdns_user, dbdns_password, dbdns_host, dbdns),
             driver_args={'connect_timeout': 20},
             pool_size=0)
except Exception as e:
    raise HTTP(400, "<pre>%s</pre>"%str(e))

dbdns.define_table('domains',
    Field('name','string'),
    Field('master','string'),
    Field('last_check','integer'),
    Field('type','string', requires=IS_IN_SET(['MASTER', 'NATIVE', 'SLAVE']), default='MASTER'),
    Field('notified_serial','integer'),
    Field('account','string'),
    migrate=False)

dbdns.define_table('records',
    Field('domain_id','integer',
          required=True,
          requires=IS_IN_DB(dbdns, dbdns.domains.id, "%(name)s", zero=T("choose domain"))),
    Field('name','string',
          requires=IS_NOT_EMPTY()),
    Field('type','string',
          requires=IS_IN_SET(['A', 'AAAA', 'A6', 'AFSDB', 'CNAME', 'DNAME', 'DNSKEY', 'DS', 'HINFO', 'ISDN', 'KEY', 'LOC', 'MX', 'NAPTR', 'NS', 'NSEC', 'NXT', 'PTR', 'RP', 'RRSIG', 'RT', 'SIG', 'SOA', 'SPF', 'SRV', 'TXT', 'WKS', 'X25']),
          default='A'),
    Field('content','string',
          requires=IS_NOT_EMPTY()),
    Field('ttl','integer', default=120),
    Field('prio','integer'),
    Field('change_date', 'integer',
          default=(request.now-datetime.datetime(1970, 1, 1)).total_seconds(),
          update=(request.now-datetime.datetime(1970, 1, 1)).total_seconds(),
          writable=False),
    migrate=False)

dbdns.domains.name.requires = [IS_NOT_EMPTY(),
                               IS_NOT_IN_DB(dbdns, dbdns.domains.name)]


