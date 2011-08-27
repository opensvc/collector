#
# create and populate utility table
#
create table digit (i integer primary key);

insert into digit values (0), (1), (2), (3), (4), (5), (6), (7), (8), (9);

#
# load 100000 nodes
#
insert into nodes (nodename, loc_country, os_name, os_arch, team_responsible, environnement) select concat('node', e.i, d.i, c.i, b.i, a.i), "France", "Linux", "x86_64", "Workers", "TST" from digit a join digit b join digit c join digit d join digit e;

#
# load 100000 services and status
#
insert into services (svc_name, svc_type, svc_app, svc_cluster_type) select concat('svc', e.i, d.i, c.i, b.i, a.i), "TST", "OSVCLAB", "failover" from digit a join digit b join digit c join digit d join digit e;

insert into svcmon (mon_svcname, mon_nodname, mon_updated, mon_svctype, mon_ipstatus, mon_fsstatus, mon_diskstatus, mon_containerstatus, mon_overallstatus, mon_syncstatus, mon_appstatus, mon_hbstatus, mon_availstatus) select concat('svc', e.i, d.i, c.i, b.i, a.i), concat('node', e.i, d.i, c.i, b.i, a.i), NOW(), "TST", "up", "up", "up", "n/a", "up", "up", "up", "n/a", "up"  from digit a join digit b join digit c join digit d join digit e;

#
# load 100 modules status over 100 weeks on 10000 nodes
#
insert into comp_status (run_nodename, run_module, run_status, run_date, run_action) select n.nodename, m.module, ROUND(RAND()), NOW(), "check" from (select concat('node', "0", d.i, c.i, b.i, a.i) as nodename from digit a join digit b join digit c join digit d) as n, (select concat('mod', b.i, a.i) as module from digit a join digit b) as m;

#
# load 100 modules log lines over 10 weeks on 10000 nodes
#
insert into comp_log (run_nodename, run_module, run_status, run_date, run_action) select n.nodename, m.module, ROUND(RAND()), d.date, "check" from (select concat('node', "0", d.i, c.i, b.i, a.i) as nodename from digit a join digit b join digit c join digit d) as n, (select concat('mod', b.i, a.i) as module from digit a join digit b) as m, (select DATE_SUB(NOW(), INTERVAL a.i week) as date from digit a) as d;
