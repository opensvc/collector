import datetime

dbdns = config_get('dbdns', 'pdns')
dbdns_host = config_get('dbdns_host', dbopensvc_host)
dbdns_user = config_get('dbdns_user', 'pdns')
dbdns_password = config_get('dbdns_password', 'pdns')

try:
    dbdns = DAL('mysql://%s:%s@%s/%s' % (dbdns_user, dbdns_password, dbdns_host, dbdns),
             driver_args={'connect_timeout': 20},
             pool_size=0)
except Exception as exc:
    db_error_handler(exc)

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


