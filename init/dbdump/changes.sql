ALTER TABLE `opensvc`.`nodes_import` ADD COLUMN `power_cabinet1` varchar(20)  AFTER `environnement`,
 ADD COLUMN `power_cabinet2` varchar(20)  AFTER `power_cabinet1`,
 ADD COLUMN `power_supply_nb` integer  AFTER `power_cabinet2`,
 ADD COLUMN `power_protect` varchar(20)  AFTER `power_supply_nb`,
 ADD COLUMN `power_protect_breaker` varchar(20)  AFTER `power_protect`,
 ADD COLUMN `power_breaker1` varchar(20)  AFTER `power_protect_breaker`,
 ADD COLUMN `power_breaker2` varchar(20)  AFTER `power_breaker1`;

ALTER TABLE `opensvc`.`nodes` ADD COLUMN `power_cabinet1` varchar(20)  AFTER `environnement`,
 ADD COLUMN `power_cabinet2` varchar(20)  AFTER `power_cabinet1`,
 ADD COLUMN `power_supply_nb` integer  AFTER `power_cabinet2`,
 ADD COLUMN `power_protect` varchar(20)  AFTER `power_supply_nb`,
 ADD COLUMN `power_protect_breaker` varchar(20)  AFTER `power_protect`,
 ADD COLUMN `power_breaker1` varchar(20)  AFTER `power_protect_breaker`,
 ADD COLUMN `power_breaker2` varchar(20)  AFTER `power_breaker1`;

DROP VIEW v_svcmon

CREATE VIEW  `opensvc`.`v_svcmon` AS select `s`.`svc_name` AS `svc_name`,`s`.`svc_nodes` AS `svc_nodes`,`s`.`svc_drpnode` AS `svc_drpnode`,`s`.`svc_drpnodes` AS `svc_drpnodes`,`s`.`svc_drptype` AS `svc_drptype`,`s`.`svc_autostart` AS `svc_autostart`,`s`.`svc_type` AS `svc_type`,`s`.`svc_comment` AS `svc_comment`,`s`.`svc_app` AS `svc_app`,`s`.`svc_drnoaction` AS `svc_drnoaction`,`s`.`updated` AS `svc_updated`,`s`.`svc_envdate` AS `svc_envdate`,`s`.`svc_containertype` AS `svc_containertype`,`s`.`svc_metrocluster` AS `svc_metrocluster`,`s`.`responsibles` AS `responsibles`,`s`.`mailto` AS `mailto`,`m`.`mon_svcname` AS `mon_svcname`,`m`.`mon_svctype` AS `mon_svctype`,`m`.`mon_drptype` AS `mon_drptype`,`m`.`mon_nodname` AS `mon_nodname`,`m`.`mon_nodtype` AS `mon_nodtype`,`m`.`mon_nodmode` AS `mon_nodmode`,`m`.`mon_ipstatus` AS `mon_ipstatus`,`m`.`mon_fsstatus` AS `mon_fsstatus`,`m`.`mon_srdf` AS `mon_srdf`,`m`.`mon_r2mode` AS `mon_r2mode`,`m`.`mon_prinodes` AS `mon_prinodes`,`m`.`mon_hostid` AS `mon_hostid`,`m`.`ID` AS `ID`,`m`.`mon_frozen` AS `mon_frozen`,`m`.`mon_rev` AS `mon_rev`,`m`.`mon_os` AS `mon_os`,`m`.`mon_frozentxt` AS `mon_frozentxt`,`m`.`mon_os_rev` AS `mon_os_rev`,`m`.`mon_svcstatus` AS `mon_svcstatus`,`m`.`mon_ipdetail` AS `mon_ipdetail`,`m`.`mon_srdfdetail` AS `mon_srdfdetail`,`m`.`mon_srdfupdated` AS `mon_srdfupdated`,`m`.`mon_diskdetail` AS `mon_diskdetail`,`m`.`mon_srdfinvtracks` AS `mon_srdfinvtracks`,`m`.`mon_lastactionid` AS `mon_lastactionid`,`m`.`mon_lastaction` AS `mon_lastaction`,`m`.`mon_lastactionstatus` AS `mon_lastactionstatus`,`m`.`mon_changed` AS `mon_changed`,`m`.`mon_updated` AS `mon_updated`,`m`.`mon_diskstatus` AS `mon_diskstatus`,`m`.`mon_containerstatus` AS `mon_containerstatus`,`m`.`mon_overallstatus` AS `mon_overallstatus`,`n`.`nodename` AS `nodename`,`n`.`loc_country` AS `loc_country`,`n`.`loc_city` AS `loc_city`,`n`.`loc_addr` AS `loc_addr`,`n`.`loc_building` AS `loc_building`,`n`.`loc_floor` AS `loc_floor`,`n`.`loc_room` AS `loc_room`,`n`.`loc_rack` AS `loc_rack`,`n`.`cpu_freq` AS `cpu_freq`,`n`.`cpu_cores` AS `cpu_cores`,`n`.`cpu_dies` AS `cpu_dies`,`n`.`cpu_vendor` AS `cpu_vendor`,`n`.`cpu_model` AS `cpu_model`,`n`.`mem_banks` AS `mem_banks`,`n`.`mem_slots` AS `mem_slots`,`n`.`mem_bytes` AS `mem_bytes`,`n`.`os_name` AS `os_name`,`n`.`os_release` AS `os_release`,`n`.`os_update` AS `os_update`,`n`.`os_segment` AS `os_segment`,`n`.`os_arch` AS `os_arch`,`n`.`os_vendor` AS `os_vendor`,`n`.`os_kernel` AS `os_kernel`,`n`.`loc_zip` AS `loc_zip`,`n`.`team_responsible` AS `team_responsible`,`n`.`serial` AS `serial`,`n`.`model` AS `model`,`n`.`type` AS `type`,`n`.`warranty_end` AS `warranty_end`,`n`.`status` AS `status`,`n`.`role` AS `role`,`n`.`environnement` AS `environnement`, n.power_supply_nb, n.power_cabinet1, n.power_cabinet2, n.power_protect, n.power_protect_breaker, n.power_breaker1, n.power_breaker2 from ((`svcmon` `m` join `v_services` `s` on((`s`.`svc_name` = `m`.`mon_svcname`))) join `nodes` `n` on((`m`.`mon_nodname` = `n`.`nodename`)))

DROP VIEW v_scvactions

CREATE `opensvc`.`v_svcactions` AS 
 select `ac`.`svcname` AS `svcname`,
        `ac`.`action` AS `action`,
        `ac`.`status` AS `status`,
        `ac`.`time` AS `time`,
        `ac`.`begin` AS `begin`,
        `ac`.`end` AS `end`,
        `ac`.`hostname` AS `hostname`,
        `ac`.`hostid` AS `hostid`,
        `ac`.`status_log` AS `status_log`,
        `ac`.`pid` AS `pid`,
        `ac`.`B_ip_status` AS `B_ip_status`,
        `ac`.`B_mount_status` AS `B_mount_status`,
        `ac`.`B_srdf_status` AS `B_srdf_status`,
        `ac`.`B_dsk_mode` AS `B_dsk_mode`,
        `ac`.`E_ip_status` AS `E_ip_status`,
        `ac`.`E_mount_status` AS `E_mount_status`,
        `ac`.`E_srdf_status` AS `E_srdf_status`,
        `ac`.`E_dsk_mode` AS `E_dsk_mode`,
        `ac`.`ID` AS `ID`,`ac`.`ack` AS `ack`,`ac`.`alert` AS `alert`,`ac`.`scripts_status` AS `scripts_status`,`ac`.`scripts_failed` AS `scripts_failed`,`ac`.`scripts_success` AS `scripts_success`,`ac`.`B_SVCstatus` AS `B_SVCstatus`,`ac`.`E_SVCstatus` AS `E_SVCstatus`,`ac`.`action_group` AS `action_group`,`ac`.`acked_by` AS `acked_by`,`ac`.`acked_comment` AS `acked_comment`,`ac`.`acked_date` AS `acked_date`,`sa`.`app` AS `app`,`sa`.`responsibles` AS `responsibles`,`sa`.`mailto` AS `mailto`,`n`.`nodename` AS `nodename`,`n`.`loc_country` AS `loc_country`,`n`.`loc_city` AS `loc_city`,`n`.`loc_addr` AS `loc_addr`,`n`.`loc_building` AS `loc_building`,`n`.`loc_floor` AS `loc_floor`,`n`.`loc_room` AS `loc_room`,`n`.`loc_rack` AS `loc_rack`,`n`.`cpu_freq` AS `cpu_freq`,`n`.`cpu_cores` AS `cpu_cores`,`n`.`cpu_dies` AS `cpu_dies`,`n`.`cpu_vendor` AS `cpu_vendor`,`n`.`cpu_model` AS `cpu_model`,`n`.`mem_banks` AS `mem_banks`,`n`.`mem_slots` AS `mem_slots`,`n`.`mem_bytes` AS `mem_bytes`,`n`.`os_name` AS `os_name`,`n`.`os_release` AS `os_release`,`n`.`os_update` AS `os_update`,`n`.`os_segment` AS `os_segment`,`n`.`os_arch` AS `os_arch`,`n`.`os_vendor` AS `os_vendor`,`n`.`os_kernel` AS `os_kernel`,`n`.`loc_zip` AS `loc_zip`,`n`.`team_responsible` AS `team_responsible`,`n`.`serial` AS `serial`,`n`.`model` AS `model`,`n`.`type` AS `type`,`n`.`warranty_end` AS `warranty_end`,`n`.`status` AS `asset_status`,`n`.`role` AS `role`,`n`.`environnement` AS `environnement`, n.power_supply_nb, n.power_cabinet1, n.power_cabinet2, n.power_protect, n.power_protect_breaker, n.power_breaker1, n.power_breaker2
 from ((`SVCactions` `ac` left join `v_services` `sa` on((`sa`.`svc_name` = `ac`.`svcname`)))
 join `nodes` `n` on((`ac`.`hostname` = `n`.`nodename`)));

CREATE TABLE  `opensvc`.`svcdisks` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `disk_id` varchar(60) NOT NULL,
  `disk_svcname` varchar(60) NOT NULL,
  `disk_nodename` varchar(60) NOT NULL,
  `disk_size` int(11) NOT NULL,
  `disk_vendor` varchar(8) NOT NULL,
  `disk_model` varchar(16) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `new_index` (`disk_id`,`disk_svcname`,`disk_nodename`)
) ENGINE=MyISAM AUTO_INCREMENT=7 DEFAULT CHARSET=latin1 COMMENT='disks used by services'

alter table services add column svc_vmname varchar(30);

drop view v_services;

CREATE VIEW `v_services` AS select s.svc_vmname, `s`.`svc_version` AS `svc_version`,`s`.`svc_hostid` AS `svc_hostid`,`s`.`svc_name` AS `svc_name`,`s`.`svc_nodes` AS `svc_nodes`,`s`.`svc_drpnode` AS `svc_drpnode`,`s`.`svc_ipname` AS `svc_ipname`,`s`.`svc_ipdev` AS `svc_ipdev`,`s`.`svc_drpipname` AS `svc_drpipname`,`s`.`svc_drpipdev` AS `svc_drpipdev`,`s`.`svc_drptype` AS `svc_drptype`,`s`.`svc_fs` AS `svc_fs`,`s`.`svc_dev` AS `svc_dev`,`s`.`svc_autostart` AS `svc_autostart`,`s`.`svc_mntopt` AS `svc_mntopt`,`s`.`svc_scsi` AS `svc_scsi`,`s`.`svc_type` AS `svc_type`,`s`.`svc_drpnodes` AS `svc_drpnodes`,`s`.`svc_comment` AS `svc_comment`,`s`.`svc_app` AS `svc_app`,`s`.`svc_drnoaction` AS `svc_drnoaction`,`s`.`updated` AS `updated`,`s`.`cksum` AS `cksum`,`s`.`svc_envdate` AS `svc_envdate`,`s`.`svc_containertype` AS `svc_containertype`,`s`.`svc_metrocluster` AS `svc_metrocluster`,`s`.`id` AS `id`,`s`.`svc_hasec` AS `svc_hasec`,`s`.`svc_hapri` AS `svc_hapri`,`s`.`svc_hastonith` AS `svc_hastonith`,`s`.`svc_hastartup` AS `svc_hastartup`,`s`.`svc_wave` AS `svc_wave`,`a`.`app` AS `app`,`a`.`responsibles` AS `responsibles`,`a`.`mailto` AS `mailto` from (`services` `s` left join `v_apps` `a` on((`a`.`app` = `s`.`svc_app`))) group by `s`.`svc_name`;

drop view v_svcmon;

CREATE VIEW `v_svcmon` AS select s.svc_vmname, `s`.`svc_version` AS `svc_version`,`s`.`svc_name` AS `svc_name`,`s`.`svc_nodes` AS `svc_nodes`,`s`.`svc_drpnode` AS `svc_drpnode`,`s`.`svc_drpnodes` AS `svc_drpnodes`,`s`.`svc_drptype` AS `svc_drptype`,`s`.`svc_autostart` AS `svc_autostart`,`s`.`svc_type` AS `svc_type`,`s`.`svc_comment` AS `svc_comment`,`s`.`svc_app` AS `svc_app`,`s`.`svc_drnoaction` AS `svc_drnoaction`,`s`.`updated` AS `svc_updated`,`s`.`svc_envdate` AS `svc_envdate`,`s`.`svc_containertype` AS `svc_containertype`,`s`.`svc_metrocluster` AS `svc_metrocluster`,`s`.`responsibles` AS `responsibles`,`s`.`mailto` AS `mailto`,`m`.`mon_svcname` AS `mon_svcname`,`m`.`mon_svctype` AS `mon_svctype`,`m`.`mon_drptype` AS `mon_drptype`,`m`.`mon_nodname` AS `mon_nodname`,`m`.`mon_nodtype` AS `mon_nodtype`,`m`.`mon_nodmode` AS `mon_nodmode`,`m`.`mon_ipstatus` AS `mon_ipstatus`,`m`.`mon_fsstatus` AS `mon_fsstatus`,`m`.`mon_srdf` AS `mon_srdf`,`m`.`mon_r2mode` AS `mon_r2mode`,`m`.`mon_prinodes` AS `mon_prinodes`,`m`.`mon_hostid` AS `mon_hostid`,`m`.`ID` AS `ID`,`m`.`mon_frozen` AS `mon_frozen`,`m`.`mon_rev` AS `mon_rev`,`m`.`mon_os` AS `mon_os`,`m`.`mon_frozentxt` AS `mon_frozentxt`,`m`.`mon_os_rev` AS `mon_os_rev`,`m`.`mon_svcstatus` AS `mon_svcstatus`,`m`.`mon_ipdetail` AS `mon_ipdetail`,`m`.`mon_srdfdetail` AS `mon_srdfdetail`,`m`.`mon_srdfupdated` AS `mon_srdfupdated`,`m`.`mon_diskdetail` AS `mon_diskdetail`,`m`.`mon_srdfinvtracks` AS `mon_srdfinvtracks`,`m`.`mon_lastactionid` AS `mon_lastactionid`,`m`.`mon_lastaction` AS `mon_lastaction`,`m`.`mon_lastactionstatus` AS `mon_lastactionstatus`,`m`.`mon_changed` AS `mon_changed`,`m`.`mon_updated` AS `mon_updated`,`m`.`mon_diskstatus` AS `mon_diskstatus`,`m`.`mon_containerstatus` AS `mon_containerstatus`,`m`.`mon_overallstatus` AS `mon_overallstatus`,`n`.`nodename` AS `nodename`,`n`.`loc_country` AS `loc_country`,`n`.`loc_city` AS `loc_city`,`n`.`loc_addr` AS `loc_addr`,`n`.`loc_building` AS `loc_building`,`n`.`loc_floor` AS `loc_floor`,`n`.`loc_room` AS `loc_room`,`n`.`loc_rack` AS `loc_rack`,`n`.`cpu_freq` AS `cpu_freq`,`n`.`cpu_cores` AS `cpu_cores`,`n`.`cpu_dies` AS `cpu_dies`,`n`.`cpu_vendor` AS `cpu_vendor`,`n`.`cpu_model` AS `cpu_model`,`n`.`mem_banks` AS `mem_banks`,`n`.`mem_slots` AS `mem_slots`,`n`.`mem_bytes` AS `mem_bytes`,`n`.`os_name` AS `os_name`,`n`.`os_release` AS `os_release`,`n`.`os_update` AS `os_update`,`n`.`os_segment` AS `os_segment`,`n`.`os_arch` AS `os_arch`,`n`.`os_vendor` AS `os_vendor`,`n`.`os_kernel` AS `os_kernel`,`n`.`loc_zip` AS `loc_zip`,`n`.`team_responsible` AS `team_responsible`,`n`.`serial` AS `serial`,`n`.`model` AS `model`,`n`.`type` AS `type`,`n`.`warranty_end` AS `warranty_end`,`n`.`status` AS `status`,`n`.`role` AS `role`,`n`.`environnement` AS `environnement`,`n`.`power_supply_nb` AS `power_supply_nb`,`n`.`power_cabinet1` AS `power_cabinet1`,`n`.`power_cabinet2` AS `power_cabinet2`,`n`.`power_protect` AS `power_protect`,`n`.`power_protect_breaker` AS `power_protect_breaker`,`n`.`power_breaker1` AS `power_breaker1`,`n`.`power_breaker2` AS `power_breaker2`,`m`.`mon_syncstatus` AS `mon_syncstatus` from ((`svcmon` `m` join `v_services` `s` on((`s`.`svc_name` = `m`.`mon_svcname`))) left join `nodes` `n` on((`m`.`mon_nodname` = `n`.`nodename`)));

alter table alerts add column action_pid integer;

#
# 2010-04-13
#
CREATE TABLE `stats_block` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nodename` varchar(60) NOT NULL,
  `date` datetime NOT NULL,
  `tps` float NOT NULL,
  `rtps` float NOT NULL,
  `wtps` float NOT NULL,
  `rbps` float NOT NULL,
  `wbps` float NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `index_1` (`date`,`nodename`)
);

CREATE TABLE `stats_blockdev` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `date` datetime NOT NULL,
  `nodename` varchar(60) NOT NULL,
  `dev` varchar(20) NOT NULL,
  `tps` float NOT NULL,
  `rsecps` float NOT NULL,
  `wsecps` float NOT NULL,
  `avgrq_sz` float NOT NULL,
  `avgqu_sz` float NOT NULL,
  `await` float NOT NULL,
  `svctm` float NOT NULL,
  `pct_util` float NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `index_1` (`date`,`nodename`,`dev`)
);

CREATE TABLE `stats_cpu` (
  `date` datetime NOT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cpu` varchar(5) NOT NULL,
  `usr` float NOT NULL,
  `nice` float NOT NULL,
  `sys` float NOT NULL,
  `iowait` float NOT NULL,
  `steal` float NOT NULL,
  `irq` float NOT NULL,
  `soft` float NOT NULL,
  `guest` float NOT NULL,
  `idle` float NOT NULL,
  `nodename` varchar(60) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `index_1` (`date`,`cpu`,`nodename`)
);

CREATE TABLE `stats_mem_u` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nodename` varchar(60) NOT NULL,
  `kbmemfree` int(11) NOT NULL,
  `kbmemused` int(11) NOT NULL,
  `pct_memused` float NOT NULL,
  `kbbuffers` int(11) NOT NULL,
  `kbcached` int(11) NOT NULL,
  `kbcommit` int(11) NOT NULL,
  `pct_commit` float NOT NULL,
  `date` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `index_1` (`date`,`nodename`)
);

CREATE TABLE `stats_proc` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `date` datetime NOT NULL,
  `nodename` varchar(60) NOT NULL,
  `runq_sz` int(11) NOT NULL,
  `plist_sz` int(11) NOT NULL,
  `ldavg_1` float NOT NULL,
  `ldavg_5` float NOT NULL,
  `ldavg_15` float NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `index_1` (`date`,`nodename`)
);

CREATE TABLE `stats_swap` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nodename` varchar(60) NOT NULL,
  `date` datetime NOT NULL,
  `kbswpfree` int(11) NOT NULL,
  `kbswpused` int(11) NOT NULL,
  `pct_swpused` float NOT NULL,
  `kbswpcad` int(11) NOT NULL,
  `pct_swpcad` float NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `index_1` (`date`,`nodename`)
);

ALTER TABLE `opensvc`.`apps_responsibles` CHANGE COLUMN `user_id` `group_id` INTEGER NOT NULL;

CREATE VIEW `v_apps_flat` AS (select `a`.`id` AS `id`,`a`.`app` AS `app`,`g`.`role` AS `role`,concat_ws(' ',`u`.`first_name`,`u`.`last_name`) AS `responsible`,`u`.`email` AS `email` from ((((`apps` `a` left join `apps_responsibles` `ar` on((`ar`.`app_id` = `a`.`id`))) left join `auth_group` `g` on((`g`.`id` = `ar`.`group_id`))) left join `auth_membership` `am` on((`am`.`group_id` = `g`.`id`))) left join `auth_user` `u` on((`u`.`id` = `am`.`user_id`))) order by `a`.`app`);

drop view v_apps;

CREATE VIEW `v_apps` AS (select `v_apps_flat`.`id` AS `id`,`v_apps_flat`.`app` AS `app`,group_concat(distinct `v_apps_flat`.`role` separator ', ') AS `roles`,group_concat(distinct `v_apps_flat`.`responsible` separator ', ') AS `responsibles`,group_concat(distinct `v_apps_flat`.`email` separator ', ') AS `mailto` from `v_apps_flat` group by `v_apps_flat`.`app`);

drop view v_users;

CREATE VIEW `v_users` AS (select (select `e`.`time_stamp` AS `time_stamp` from `auth_event` `e` where (`e`.`user_id` = `u`.`id`) order by `e`.`time_stamp` desc limit 1) AS `last`,`u`.`id` AS `id`,concat_ws(' ',`u`.`first_name`,`u`.`last_name`) AS `fullname`,`u`.`email` AS `email`,group_concat(`d`.`domains` separator ', ') AS `domains`,sum((select count(0) AS `count(*)` from `auth_group` `gg` where ((`gg`.`role` = 'Manager') and (`gg`.`id` = `g`.`id`)))) AS `manager`,group_concat(`g`.`role` separator ', ') AS `groups` from (((`auth_user` `u` left join `auth_membership` `m` on((`u`.`id` = `m`.`user_id`))) left join `auth_group` `g` on(((`m`.`group_id` = `g`.`id`) and (not((`g`.`role` like 'user_%')))))) left join `domain_permissions` `d` on((`m`.`group_id` = `d`.`group_id`))) group by concat_ws(' ',`u`.`first_name`,`u`.`last_name`));

#
# 2010-04-20
#
alter table SVCactions add index `err_index` (`svcname`,`status`);

insert into filters set fil_name='team responsible',fil_column='team_responsible', fil_need_value=1,fil_pos=1,fil_table='v_svcmon',fil_img='node16.png';

insert into filters set fil_name='team responsible',fil_column='team_responsible', fil_need_value=1,fil_pos=1,fil_table='v_svcactions',fil_img='node16.png';

#
# 2010-04-23
#
ALTER TABLE `opensvc`.`stats_mem_u` ADD COLUMN `kbmemsys` integer  NOT NULL DEFAULT 0 AFTER `date`;

#
# 2010-04-26
#
DELIMITER //

CREATE FUNCTION trusted_status(status VARCHAR(20), updated DATETIME)
  RETURNS VARCHAR(20)

  BEGIN
    DECLARE s VARCHAR(20);

    IF updated < DATE_SUB(NOW(), INTERVAL 15 MINUTE) THEN SET s = "unknown";
    ELSE SET s = status;
    END IF;

    RETURN s;
  END //

DELIMITER ;

drop view v_svc_group_status;

CREATE VIEW `v_svc_group_status` AS (select `svcmon`.`ID` AS `id`,`svcmon`.`mon_svcname` AS `svcname`,`svcmon`.`mon_svctype` AS `svctype`,group_concat(trusted_status(`svcmon`.`mon_overallstatus`,mon_updated) separator ',') AS `groupstatus` from `svcmon` group by `svcmon`.`mon_svcname`);

#
# 2010-05-03
#
insert into filters values (NULL, 'frozen services', 'mon_frozen', 1, 12, 'v_svcmon', 'svc.png');

#
# 2010-05-06
#
alter table resmon add column `res_log` varchar(200) DEFAULT '';

#
# 2010-05-06
# 
alter table auth_filters add column fil_active boolean default true;
alter table services add column svc_vmem integer default 0;
alter table services add column svc_vcpus integer default 0;
drop view v_svcmon;
create view v_svcmon as select (select count(`a`.`ID`) AS `count(a.id)` from `SVCactions` `a` where ((m.mon_nodname=a.hostname) and (`a`.`svcname` = `s`.`svc_name`) and (`a`.`status` = 'err') and ((`a`.`ack` <> 1) or isnull(`a`.`ack`)))) AS `err`,`s`.`svc_vmname` AS `svc_vmname`,`s`.`svc_version` AS `svc_version`,`s`.`svc_name` AS `svc_name`,`s`.`svc_nodes` AS `svc_nodes`,`s`.`svc_drpnode` AS `svc_drpnode`,`s`.`svc_drpnodes` AS `svc_drpnodes`,`s`.`svc_drptype` AS `svc_drptype`,`s`.`svc_autostart` AS `svc_autostart`,`s`.`svc_type` AS `svc_type`,`s`.`svc_comment` AS `svc_comment`,`s`.`svc_app` AS `svc_app`,`s`.`svc_drnoaction` AS `svc_drnoaction`,`s`.`updated` AS `svc_updated`,`s`.`svc_envdate` AS `svc_envdate`,`s`.`svc_containertype` AS `svc_containertype`,`s`.`svc_metrocluster` AS `svc_metrocluster`,`s`.`responsibles` AS `responsibles`,`s`.`mailto` AS `mailto`,`m`.`mon_svcname` AS `mon_svcname`,`m`.`mon_svctype` AS `mon_svctype`,`m`.`mon_drptype` AS `mon_drptype`,`m`.`mon_nodname` AS `mon_nodname`,`m`.`mon_nodtype` AS `mon_nodtype`,`m`.`mon_nodmode` AS `mon_nodmode`,`m`.`mon_ipstatus` AS `mon_ipstatus`,`m`.`mon_fsstatus` AS `mon_fsstatus`,`m`.`mon_prinodes` AS `mon_prinodes`,`m`.`mon_hostid` AS `mon_hostid`,`m`.`ID` AS `ID`,`m`.`mon_frozen` AS `mon_frozen`,`m`.`mon_frozentxt` AS `mon_frozentxt`,`m`.`mon_changed` AS `mon_changed`,`m`.`mon_updated` AS `mon_updated`,`m`.`mon_diskstatus` AS `mon_diskstatus`,`m`.`mon_containerstatus` AS `mon_containerstatus`,`m`.`mon_overallstatus` AS `mon_overallstatus`,`n`.`nodename` AS `nodename`,`n`.`loc_country` AS `loc_country`,`n`.`loc_city` AS `loc_city`,`n`.`loc_addr` AS `loc_addr`,`n`.`loc_building` AS `loc_building`,`n`.`loc_floor` AS `loc_floor`,`n`.`loc_room` AS `loc_room`,`n`.`loc_rack` AS `loc_rack`,`n`.`cpu_freq` AS `cpu_freq`,`n`.`cpu_cores` AS `cpu_cores`,`n`.`cpu_dies` AS `cpu_dies`,`n`.`cpu_vendor` AS `cpu_vendor`,`n`.`cpu_model` AS `cpu_model`,`n`.`mem_banks` AS `mem_banks`,`n`.`mem_slots` AS `mem_slots`,`n`.`mem_bytes` AS `mem_bytes`,`n`.`os_name` AS `os_name`,`n`.`os_release` AS `os_release`,`n`.`os_update` AS `os_update`,`n`.`os_segment` AS `os_segment`,`n`.`os_arch` AS `os_arch`,`n`.`os_vendor` AS `os_vendor`,`n`.`os_kernel` AS `os_kernel`,`n`.`loc_zip` AS `loc_zip`,`n`.`team_responsible` AS `team_responsible`,`n`.`serial` AS `serial`,`n`.`model` AS `model`,`n`.`type` AS `type`,`n`.`warranty_end` AS `warranty_end`,`n`.`status` AS `status`,`n`.`role` AS `role`,`n`.`environnement` AS `environnement`,`n`.`power_supply_nb` AS `power_supply_nb`,`n`.`power_cabinet1` AS `power_cabinet1`,`n`.`power_cabinet2` AS `power_cabinet2`,`n`.`power_protect` AS `power_protect`,`n`.`power_protect_breaker` AS `power_protect_breaker`,`n`.`power_breaker1` AS `power_breaker1`,`n`.`power_breaker2` AS `power_breaker2`,`m`.`mon_syncstatus` AS `mon_syncstatus`,`m`.`mon_appstatus` AS `mon_appstatus` from ((`svcmon` `m` join `v_services` `s` on((`s`.`svc_name` = `m`.`mon_svcname`))) left join `nodes` `n` on((`m`.`mon_nodname` = `n`.`nodename`)));

#
# 2010-05-11
# 
drop view v_svcmon;
drop view v_services;

CREATE VIEW `v_services` AS select `s`.`svc_vmname` AS `svc_vmname`,`s`.`svc_version` AS `svc_version`,`s`.`svc_hostid` AS `svc_hostid`,`s`.`svc_name` AS `svc_name`,`s`.`svc_nodes` AS `svc_nodes`,`s`.`svc_drpnode` AS `svc_drpnode`,`s`.`svc_ipname` AS `svc_ipname`,`s`.`svc_ipdev` AS `svc_ipdev`,`s`.`svc_drpipname` AS `svc_drpipname`,`s`.`svc_drpipdev` AS `svc_drpipdev`,`s`.`svc_drptype` AS `svc_drptype`,`s`.`svc_fs` AS `svc_fs`,`s`.`svc_dev` AS `svc_dev`,`s`.`svc_autostart` AS `svc_autostart`,`s`.`svc_mntopt` AS `svc_mntopt`,`s`.`svc_scsi` AS `svc_scsi`,`s`.`svc_type` AS `svc_type`,`s`.`svc_drpnodes` AS `svc_drpnodes`,`s`.`svc_comment` AS `svc_comment`,`s`.`svc_app` AS `svc_app`,`s`.`svc_drnoaction` AS `svc_drnoaction`,`s`.`updated` AS `updated`,`s`.`cksum` AS `cksum`,`s`.`svc_envdate` AS `svc_envdate`,`s`.`svc_containertype` AS `svc_containertype`,`s`.`svc_metrocluster` AS `svc_metrocluster`,`s`.`id` AS `id`,`s`.`svc_hasec` AS `svc_hasec`,`s`.`svc_hapri` AS `svc_hapri`,`s`.`svc_hastonith` AS `svc_hastonith`,`s`.`svc_hastartup` AS `svc_hastartup`,`s`.`svc_wave` AS `svc_wave`,s.svc_vcpus, s.svc_vmem,`a`.`app` AS `app`,`a`.`responsibles` AS `responsibles`,`a`.`mailto` AS `mailto` from (`services` `s` left join `v_apps` `a` on((`a`.`app` = `s`.`svc_app`))) group by `s`.`svc_name`;

CREATE VIEW `v_svcmon` AS select (select count(`a`.`ID`) AS `count(a.id)` from `SVCactions` `a` where ((`m`.`mon_nodname` = `a`.`hostname`) and (`a`.`svcname` = `s`.`svc_name`) and (`a`.`status` = 'err') and ((`a`.`ack` <> 1) or isnull(`a`.`ack`)))) AS `err`,`s`.`svc_vmname` AS `svc_vmname`,`s`.`svc_version` AS `svc_version`,`s`.`svc_name` AS `svc_name`,`s`.`svc_nodes` AS `svc_nodes`,`s`.`svc_drpnode` AS `svc_drpnode`,`s`.`svc_drpnodes` AS `svc_drpnodes`,`s`.`svc_drptype` AS `svc_drptype`,`s`.`svc_autostart` AS `svc_autostart`,`s`.`svc_type` AS `svc_type`,`s`.`svc_comment` AS `svc_comment`,`s`.`svc_app` AS `svc_app`,`s`.`svc_drnoaction` AS `svc_drnoaction`,`s`.`updated` AS `svc_updated`,`s`.`svc_envdate` AS `svc_envdate`,`s`.`svc_containertype` AS `svc_containertype`,`s`.`svc_metrocluster` AS `svc_metrocluster`,`s`.`responsibles` AS `responsibles`,`s`.`mailto` AS `mailto`,s.svc_vcpus, s.svc_vmem, `m`.`mon_svcname` AS `mon_svcname`,`m`.`mon_svctype` AS `mon_svctype`,`m`.`mon_drptype` AS `mon_drptype`,`m`.`mon_nodname` AS `mon_nodname`,`m`.`mon_nodtype` AS `mon_nodtype`,`m`.`mon_nodmode` AS `mon_nodmode`,`m`.`mon_ipstatus` AS `mon_ipstatus`,`m`.`mon_fsstatus` AS `mon_fsstatus`,`m`.`mon_prinodes` AS `mon_prinodes`,`m`.`mon_hostid` AS `mon_hostid`,`m`.`ID` AS `ID`,`m`.`mon_frozen` AS `mon_frozen`,`m`.`mon_frozentxt` AS `mon_frozentxt`,`m`.`mon_changed` AS `mon_changed`,`m`.`mon_updated` AS `mon_updated`,`m`.`mon_diskstatus` AS `mon_diskstatus`,`m`.`mon_containerstatus` AS `mon_containerstatus`,`m`.`mon_overallstatus` AS `mon_overallstatus`,`n`.`nodename` AS `nodename`,`n`.`loc_country` AS `loc_country`,`n`.`loc_city` AS `loc_city`,`n`.`loc_addr` AS `loc_addr`,`n`.`loc_building` AS `loc_building`,`n`.`loc_floor` AS `loc_floor`,`n`.`loc_room` AS `loc_room`,`n`.`loc_rack` AS `loc_rack`,`n`.`cpu_freq` AS `cpu_freq`,`n`.`cpu_cores` AS `cpu_cores`,`n`.`cpu_dies` AS `cpu_dies`,`n`.`cpu_vendor` AS `cpu_vendor`,`n`.`cpu_model` AS `cpu_model`,`n`.`mem_banks` AS `mem_banks`,`n`.`mem_slots` AS `mem_slots`,`n`.`mem_bytes` AS `mem_bytes`,`n`.`os_name` AS `os_name`,`n`.`os_release` AS `os_release`,`n`.`os_update` AS `os_update`,`n`.`os_segment` AS `os_segment`,`n`.`os_arch` AS `os_arch`,`n`.`os_vendor` AS `os_vendor`,`n`.`os_kernel` AS `os_kernel`,`n`.`loc_zip` AS `loc_zip`,`n`.`team_responsible` AS `team_responsible`,`n`.`serial` AS `serial`,`n`.`model` AS `model`,`n`.`type` AS `type`,`n`.`warranty_end` AS `warranty_end`,`n`.`status` AS `status`,`n`.`role` AS `role`,`n`.`environnement` AS `environnement`,`n`.`power_supply_nb` AS `power_supply_nb`,`n`.`power_cabinet1` AS `power_cabinet1`,`n`.`power_cabinet2` AS `power_cabinet2`,`n`.`power_protect` AS `power_protect`,`n`.`power_protect_breaker` AS `power_protect_breaker`,`n`.`power_breaker1` AS `power_breaker1`,`n`.`power_breaker2` AS `power_breaker2`,`m`.`mon_syncstatus` AS `mon_syncstatus`,`m`.`mon_appstatus` AS `mon_appstatus` from ((`svcmon` `m` join `v_services` `s` on((`s`.`svc_name` = `m`.`mon_svcname`))) left join `nodes` `n` on((`m`.`mon_nodname` = `n`.`nodename`)));

#
# 2010-05-12
#
alter table filters add column fil_search_table varchar(30) default null;
update filters set fil_search_table='nodes' where fil_column like 'os_%';
update filters set fil_search_table='nodes' where fil_column like 'loc_%';
update filters set fil_search_table='nodes' where fil_column like 'cpu_%';
update filters set fil_search_table='nodes' where fil_column like 'mem_%';
update filters set fil_search_table='nodes' where fil_column like 'serial';
update filters set fil_search_table='nodes' where fil_column like 'team_responsible';
update filters set fil_search_table='nodes' where fil_column like 'nodename';
update filters set fil_search_table='nodes' where fil_column like 'model';
update filters set fil_search_table='nodes' where fil_column like 'type';
update filters set fil_search_table='nodes' where fil_column like 'power_%';
update filters set fil_search_table='services' where fil_column like 'svc_%';
update filters set fil_search_table='svcmon' where fil_column like 'mon_%';
update filters set fil_search_table='SVCactions' where fil_column like 'acked_%';
update filters set fil_search_table='nodes' where fil_column like 'environnement';
update filters set fil_search_table='nodes' where fil_column like 'role';
update filters set fil_search_table='nodes' where fil_column like 'status';
update filters set fil_search_table='nodes' where fil_column like 'warranty_end';
update filters set fil_search_table='SVCactions' where fil_column like 'action';
update filters set fil_search_table='nodes' where fil_column like 'hostname';
update filters set fil_search_table='services' where fil_column like 'hostid';
update filters set fil_search_table='services' where fil_column like 'app';
update filters set fil_search_table='services' where fil_column like 'version';
update filters set fil_search_table='v_services' where fil_column like 'responsibles';

#
# 2010-05-13
#
insert into filters values (null,"environment","environnement",1,1,"v_svcmon","node16.png","nodes");
insert into filters values (null,"environment","environnement",1,1,"v_svcactions","node16.png","nodes");
CREATE TABLE `opensvc`.`packages` (
  `id` integer  NOT NULL AUTO_INCREMENT,
  `pkg_nodename` varchar(60)  NOT NULL,
  `pkg_name` varchar(100)  NOT NULL,
  `pkg_version` varchar(32)  NOT NULL,
  `pkg_arch` varchar(8)  NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `idx1`(`pkg_nodename`),
  INDEX `idx2`(`pkg_version`)
);
create unique index idx3 on packages (pkg_nodename, pkg_name);

drop view v_svc_group_status;

create view v_svc_group_status as (select `svcmon`.`ID` AS `id`,`svcmon`.`mon_svcname` AS `svcname`,`svcmon`.`mon_svctype` AS `svctype`,group_concat(`trusted_status`(`svcmon`.`mon_overallstatus`,`svcmon`.`mon_updated`) separator ',') AS `groupstatus`, group_concat(`svcmon`.`mon_nodname` separator ',') AS `nodes` from `svcmon` group by `svcmon`.`mon_svcname`);

alter table packages add column pkg_updated timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP;

#
# 2010-05-17
#
CREATE TABLE `stats_netdev` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nodename` varchar(60) NOT NULL,
  `date` datetime NOT NULL,
  `dev` varchar(8) NOT NULL,
  `rxkBps` float NOT NULL,
  `txkBps` float NOT NULL,
  `rxpckps` float NOT NULL,
  `txpckps` float NOT NULL,
  PRIMARY KEY (`id`)
);

CREATE TABLE `stats_netdev_err` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nodename` varchar(60) NOT NULL,
  `date` datetime NOT NULL,
  `rxerrps` float NOT NULL,
  `txerrps` float NOT NULL,
  `collps` float NOT NULL,
  `rxdropps` float NOT NULL,
  `txdropps` float NOT NULL,
  `dev` varchar(8) NOT NULL,
  PRIMARY KEY (`id`)
);

#
# 2010-05-19
#
ALTER TABLE `opensvc`.`packages` DROP INDEX `idx3`,
 ADD UNIQUE INDEX `idx3` USING BTREE(`pkg_nodename`, `pkg_name`, `pkg_arch`);

#
# 2010-05-26
#
create view v_stats_netdev_err_avg_last_day as (select id, nodename, dev, avg(rxerrps) as avgrxerrps, avg(txerrps) as avgtxerrps, avg(collps) as avgcollps, avg(rxdropps) as avgrxdropps, avg(txdropps) as avgtxdropps from stats_netdev_err where date > date_sub(now(), interval 1 day) group by nodename, dev order by nodename, dev);

#
# 2010-05-28
#
create view v_svcmon_clusters as (select *, (select group_concat(mon_nodname order by mon_nodname) from svcmon where mon_svcname=m.mon_svcname) as nodes from v_svcmon m);
alter table SVCactions modify pid VARCHAR(32);

#
# 2010-06-02
#
update alerts set body=replace(body, 'node?nodename', 'svcmon?nodename') where body like '%node?nodename%';

#
# 2010-06-18
#
alter table services add column svc_guestos varchar(30);

drop view v_services;

CREATE VIEW `v_services` AS select `s`.`svc_vmname` AS `svc_vmname`, s.svc_guestos, `s`.`svc_version` AS `svc_version`,`s`.`svc_hostid` AS `svc_hostid`,`s`.`svc_name` AS `svc_name`,`s`.`svc_nodes` AS `svc_nodes`,`s`.`svc_drpnode` AS `svc_drpnode`,`s`.`svc_ipname` AS `svc_ipname`,`s`.`svc_ipdev` AS `svc_ipdev`,`s`.`svc_drpipname` AS `svc_drpipname`,`s`.`svc_drpipdev` AS `svc_drpipdev`,`s`.`svc_drptype` AS `svc_drptype`,`s`.`svc_fs` AS `svc_fs`,`s`.`svc_dev` AS `svc_dev`,`s`.`svc_autostart` AS `svc_autostart`,`s`.`svc_mntopt` AS `svc_mntopt`,`s`.`svc_scsi` AS `svc_scsi`,`s`.`svc_type` AS `svc_type`,`s`.`svc_drpnodes` AS `svc_drpnodes`,`s`.`svc_comment` AS `svc_comment`,`s`.`svc_app` AS `svc_app`,`s`.`svc_drnoaction` AS `svc_drnoaction`,`s`.`updated` AS `updated`,`s`.`cksum` AS `cksum`,`s`.`svc_envdate` AS `svc_envdate`,`s`.`svc_containertype` AS `svc_containertype`,`s`.`svc_metrocluster` AS `svc_metrocluster`,`s`.`id` AS `id`,`s`.`svc_hasec` AS `svc_hasec`,`s`.`svc_hapri` AS `svc_hapri`,`s`.`svc_hastonith` AS `svc_hastonith`,`s`.`svc_hastartup` AS `svc_hastartup`,`s`.`svc_wave` AS `svc_wave`,`s`.`svc_vcpus` AS `svc_vcpus`,`s`.`svc_vmem` AS `svc_vmem`,`a`.`app` AS `app`,`a`.`responsibles` AS `responsibles`,`a`.`mailto` AS `mailto` from (`services` `s` left join `v_apps` `a` on((`a`.`app` = `s`.`svc_app`))) group by `s`.`svc_name`;

drop view v_svcmon;

CREATE VIEW `v_svcmon` AS select (select count(`a`.`ID`) AS `count(a.id)` from `SVCactions` `a` where ((`m`.`mon_nodname` = `a`.`hostname`) and (`a`.`svcname` = `s`.`svc_name`) and (`a`.`status` = 'err') and ((`a`.`ack` <> 1) or isnull(`a`.`ack`)))) AS `err`,`s`.`svc_vmname` AS `svc_vmname`,s.svc_guestos,`s`.`svc_version` AS `svc_version`,`s`.`svc_name` AS `svc_name`,`s`.`svc_nodes` AS `svc_nodes`,`s`.`svc_drpnode` AS `svc_drpnode`,`s`.`svc_drpnodes` AS `svc_drpnodes`,`s`.`svc_drptype` AS `svc_drptype`,`s`.`svc_autostart` AS `svc_autostart`,`s`.`svc_type` AS `svc_type`,`s`.`svc_comment` AS `svc_comment`,`s`.`svc_app` AS `svc_app`,`s`.`svc_drnoaction` AS `svc_drnoaction`,`s`.`updated` AS `svc_updated`,`s`.`svc_envdate` AS `svc_envdate`,`s`.`svc_containertype` AS `svc_containertype`,`s`.`svc_metrocluster` AS `svc_metrocluster`,`s`.`responsibles` AS `responsibles`,`s`.`mailto` AS `mailto`,`s`.`svc_vcpus` AS `svc_vcpus`,`s`.`svc_vmem` AS `svc_vmem`,`m`.`mon_svcname` AS `mon_svcname`,`m`.`mon_svctype` AS `mon_svctype`,`m`.`mon_drptype` AS `mon_drptype`,`m`.`mon_nodname` AS `mon_nodname`,`m`.`mon_nodtype` AS `mon_nodtype`,`m`.`mon_nodmode` AS `mon_nodmode`,`m`.`mon_ipstatus` AS `mon_ipstatus`,`m`.`mon_fsstatus` AS `mon_fsstatus`,`m`.`mon_prinodes` AS `mon_prinodes`,`m`.`mon_hostid` AS `mon_hostid`,`m`.`ID` AS `ID`,`m`.`mon_frozen` AS `mon_frozen`,`m`.`mon_frozentxt` AS `mon_frozentxt`,`m`.`mon_changed` AS `mon_changed`,`m`.`mon_updated` AS `mon_updated`,`m`.`mon_diskstatus` AS `mon_diskstatus`,`m`.`mon_containerstatus` AS `mon_containerstatus`,`m`.`mon_overallstatus` AS `mon_overallstatus`,`n`.`nodename` AS `nodename`,`n`.`loc_country` AS `loc_country`,`n`.`loc_city` AS `loc_city`,`n`.`loc_addr` AS `loc_addr`,`n`.`loc_building` AS `loc_building`,`n`.`loc_floor` AS `loc_floor`,`n`.`loc_room` AS `loc_room`,`n`.`loc_rack` AS `loc_rack`,`n`.`cpu_freq` AS `cpu_freq`,`n`.`cpu_cores` AS `cpu_cores`,`n`.`cpu_dies` AS `cpu_dies`,`n`.`cpu_vendor` AS `cpu_vendor`,`n`.`cpu_model` AS `cpu_model`,`n`.`mem_banks` AS `mem_banks`,`n`.`mem_slots` AS `mem_slots`,`n`.`mem_bytes` AS `mem_bytes`,`n`.`os_name` AS `os_name`,`n`.`os_release` AS `os_release`,`n`.`os_update` AS `os_update`,`n`.`os_segment` AS `os_segment`,`n`.`os_arch` AS `os_arch`,`n`.`os_vendor` AS `os_vendor`,`n`.`os_kernel` AS `os_kernel`,`n`.`loc_zip` AS `loc_zip`,`n`.`team_responsible` AS `team_responsible`,`n`.`serial` AS `serial`,`n`.`model` AS `model`,`n`.`type` AS `type`,`n`.`warranty_end` AS `warranty_end`,`n`.`status` AS `status`,`n`.`role` AS `role`,`n`.`environnement` AS `environnement`,`n`.`power_supply_nb` AS `power_supply_nb`,`n`.`power_cabinet1` AS `power_cabinet1`,`n`.`power_cabinet2` AS `power_cabinet2`,`n`.`power_protect` AS `power_protect`,`n`.`power_protect_breaker` AS `power_protect_breaker`,`n`.`power_breaker1` AS `power_breaker1`,`n`.`power_breaker2` AS `power_breaker2`,`m`.`mon_syncstatus` AS `mon_syncstatus`,`m`.`mon_appstatus` AS `mon_appstatus` from ((`svcmon` `m` join `v_services` `s` on((`s`.`svc_name` = `m`.`mon_svcname`))) left join `nodes` `n` on((`m`.`mon_nodname` = `n`.`nodename`)));

#
# 20100719
#
CREATE TABLE `svcmon_log_ack_periodic` (   `id` int(11) NOT NULL AUTO_INCREMENT,   `mon_svcname` varchar(60) NOT NULL,   `mon_begin` datetime NOT NULL,   `mon_end` datetime NOT NULL, mon_period varchar(10) default "",  `mon_comment` text NOT NULL,   `mon_acked_by` varchar(100) NOT NULL,   `mon_acked_on` datetime NOT NULL,   `mon_account` int(11) NOT NULL DEFAULT '1',   PRIMARY KEY (`id`),   UNIQUE KEY `key_1` (`mon_svcname`,`mon_begin`,`mon_end`),   KEY `mon_svcname` (`mon_svcname`),   KEY `mon_begin` (`mon_begin`),   KEY `mon_end` (`mon_end`) );

#
# 20100801
#
alter table nodes modify os_release VARCHAR(64);
alter table SVCactions modify hostid VARCHAR(30);

CREATE TABLE `checks_live` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `chk_nodename` varchar(50) NOT NULL,
  `chk_svcname` varchar(50) NOT NULL,
  `chk_type` varchar(10) NOT NULL,
  `chk_updated` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `chk_value` int(11) NOT NULL,
  `chk_created` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `chk_instance` varchar(60) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx1` (`chk_nodename`,`chk_svcname`,`chk_type`,`chk_instance`)
);

CREATE TABLE `checks_settings` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `chk_nodename` varchar(50) NOT NULL,
  `chk_svcname` varchar(50) NOT NULL,
  `chk_type` varchar(10) NOT NULL,
  `chk_low` int(11) NOT NULL,
  `chk_high` int(11) NOT NULL,
  `chk_changed` datetime NOT NULL,
  `chk_changed_by` varchar(60) NOT NULL,
  `chk_instance` varchar(60) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx1` (`chk_nodename`,`chk_svcname`,`chk_type`,`chk_instance`)
);

CREATE TABLE `checks_defaults` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `chk_type` varchar(10) NOT NULL,
  `chk_low` int(11) NOT NULL,
  `chk_high` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx1` (`chk_type`)
);

CREATE VIEW `v_checks` AS select `cl`.`id` AS `id`,`cl`.`chk_nodename` AS `chk_nodename`,`cl`.`chk_svcname` AS `chk_svcname`,`cl`.`chk_type` AS `chk_type`,`cl`.`chk_updated` AS `chk_updated`,`cl`.`chk_value` AS `chk_value`,`cl`.`chk_created` AS `chk_created`,`cl`.`chk_instance` AS `chk_instance`,if(`cs`.`chk_low` is not NULL,`cs`.`chk_low`,`cd`.`chk_low`) AS `chk_low`,if(`cs`.`chk_high` is not NULL,`cs`.`chk_high`,`cd`.`chk_high`) AS `chk_high` from ((`checks_live` `cl` left join `checks_settings` `cs` on(((`cl`.`chk_nodename` = `cs`.`chk_nodename`) and (`cl`.`chk_svcname` = `cs`.`chk_svcname`) and (`cl`.`chk_type` = `cs`.`chk_type`) and (`cl`.`chk_instance` = `cs`.`chk_instance`)))) left join `checks_defaults` `cd` on((`cl`.`chk_type` = `cd`.`chk_type`)));

#
# 20100909
#
CREATE TABLE `billing` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `bill_min_svc` int(11) NOT NULL,
  `bill_os_name` varchar(50) NOT NULL,
  `bill_cost` float NOT NULL,
  `bill_max_svc` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=19 DEFAULT CHARSET=utf8;

INSERT INTO `billing` VALUES (1,1000,'AIX',200,999999),(2,1000,'SunOS',200,999999),(3,1000,'HP-UX',200,999999),(4,1000,'OpenSolaris',100,999999),(5,1000,'FreeBSD',100,999999),(6,1000,'Linux',100,999999),(7,500,'AIX',240,999),(8,500,'SunOS',240,999),(9,500,'HP-UX',240,999),(10,500,'OpenSolaris',120,999),(11,500,'FreeBSD',120,999),(12,500,'Linux',120,999),(13,0,'AIX',300,499),(14,0,'OpenSolaris',150,499),(15,0,'SunOS',300,499),(16,0,'HP-UX',300,499),(17,0,'FreeBSD',150,499),(18,0,'Linux',150,499);

create view v_billing_svc_os_name as select id,svc_name,os_name from v_svcmon group by svc_name order by svc_name;

create view v_billing_svc_os_count as select id, count(os_name) as nb,os_name,group_concat(svc_name) as svc_list from v_billing_svc_os_name group by os_name order by os_name;

create view v_billing as select c.id, c.nb, c.os_name, b.bill_cost as unit_cost, b.bill_cost*c.nb as cost, c.svc_list from v_billing_svc_os_count c join billing b on c.os_name=b.bill_os_name and c.nb>=b.bill_min_svc and c.nb<=b.bill_max_svc;

#
# 20100913
#
drop view v_billing;

drop view v_billing_svc_os_count;

drop view v_billing_svc_os_name;

create view v_nb_services as select count(id) as nb_svc from services;

create view v_billing as select m.id,m.svc_name,m.os_name,m.svc_app,b.bill_cost from v_svcmon m join v_nb_services n join billing b on m.os_name=b.bill_os_name and n.nb_svc>=b.bill_min_svc and n.nb_svc<=b.bill_max_svc  group by svc_name order by svc_name;

create view v_billing_per_os as select id, count(os_name) as nb,sum(bill_cost) as cost,os_name,group_concat(distinct svc_app) as app_list,group_concat(svc_name) as svc_list from v_billing group by os_name order by os_name;

create view v_billing_per_app as select id, count(svc_app) as nb,sum(bill_cost) as cost,svc_app,group_concat(distinct os_name) as os_list,group_concat(svc_name) as svc_list from v_billing group by svc_app order by svc_app;

create view v_checks_nodes as select cl.id, `cl`.`chk_nodename` AS `chk_nodename`,`cl`.`chk_svcname` AS `chk_svcname`,`cl`.`chk_type` AS `chk_type`,`cl`.`chk_updated` AS `chk_updated`,`cl`.`chk_value` AS `chk_value`,`cl`.`chk_created` AS `chk_created`,`cl`.`chk_instance` AS `chk_instance`,if(`cs`.`chk_low` is not NULL,`cs`.`chk_low`,`cd`.`chk_low`) AS `chk_low`,if(`cs`.`chk_high` is not NULL,`cs`.`chk_high`,`cd`.`chk_high`) AS `chk_high`,n.nodename,n.loc_country,n.loc_city,n.loc_addr,n.loc_building,n.loc_floor,n.loc_room,n.loc_rack,n.cpu_freq,n.cpu_cores,n.cpu_dies,n.cpu_vendor,n.cpu_model,n.mem_banks,n.mem_slots,n.mem_bytes,n.os_name,n.os_release,n.os_update,n.os_segment,n.os_arch,n.os_vendor,n.os_kernel,n.loc_zip,n.team_responsible,n.serial,n.model,n.type,n.warranty_end,n.status,n.role,n.environnement,n.power_cabinet1,n.power_cabinet2,n.power_supply_nb,n.power_protect,n.power_protect_breaker,n.power_breaker1,n.power_breaker2,n.os_concat from ((`checks_live` `cl` left join `checks_settings` `cs` on(((`cl`.`chk_nodename` = `cs`.`chk_nodename`) and (`cl`.`chk_svcname` = `cs`.`chk_svcname`) and (`cl`.`chk_type` = `cs`.`chk_type`) and (`cl`.`chk_instance` = `cs`.`chk_instance`)))) join v_nodes n on n.nodename=cl.chk_nodename left join `checks_defaults` `cd` on((`cl`.`chk_type` = `cd`.`chk_type`)));

create view v_packages_nodes as select p.id, p.pkg_nodename,p.pkg_name,p.pkg_version,p.pkg_arch,p.pkg_updated,n.nodename,n.loc_country,n.loc_city,n.loc_addr,n.loc_building,n.loc_floor,n.loc_room,n.loc_rack,n.cpu_freq,n.cpu_cores,n.cpu_dies,n.cpu_vendor,n.cpu_model,n.mem_banks,n.mem_slots,n.mem_bytes,n.os_name,n.os_release,n.os_update,n.os_segment,n.os_arch,n.os_vendor,n.os_kernel,n.loc_zip,n.team_responsible,n.serial,n.model,n.type,n.warranty_end,n.status,n.role,n.environnement,n.power_cabinet1,n.power_cabinet2,n.power_supply_nb,n.power_protect,n.power_protect_breaker,n.power_breaker1,n.power_breaker2,n.os_concat from packages p join v_nodes n on n.nodename=p.pkg_nodename;

CREATE TABLE `opensvc`.`lifecycle_os` (
  `id` integer  NOT NULL AUTO_INCREMENT,
  `lc_os_concat` varchar(100)  NOT NULL,
  `lc_count` integer  NOT NULL,
  `lc_date` DATE  NOT NULL,
  PRIMARY KEY (`id`)
);

alter table lifecycle_os add unique index idx1 using btree(lc_os_concat,lc_date);

drop view v_packages_nodes;

drop view v_checks_nodes;

alter table lifecycle_os add column lc_os_name varchar(60) default null;

alter table lifecycle_os add column lc_os_vendor varchar(60) default null;

# test => set in config file
set global concurrent_insert=2;

create view v_lifecycle_os_name as select id, lc_date, sum(lc_count) as lc_count,lc_os_name from lifecycle_os group by lc_date, lc_os_name order by lc_date,lc_os_name;

CREATE TABLE `patches` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `patch_nodename` varchar(60) NOT NULL,
  `patch_num` varchar(100) NOT NULL,
  `patch_rev` varchar(32) DEFAULT NULL,
  `patch_updated` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx3` (`patch_nodename`,`patch_num`,`patch_rev`)
);

CREATE TABLE `opensvc`.`user_prefs_columns` (
  `id` integer  NOT NULL AUTO_INCREMENT,
  `upc_user_id` integer  NOT NULL,
  `upc_table` varchar(30)  NOT NULL,
  `upc_field` varchar(30)  NOT NULL,
  `upc_visible` boolean  NOT NULL,
  PRIMARY KEY (`id`)
);

create unique index idx1 on user_prefs_columns (upc_user_id, upc_table, upc_field);

alter table packages modify pkg_version VARCHAR(64);

alter table nodes modify os_kernel VARCHAR(32);

ALTER TABLE `opensvc`.`auth_user` ADD COLUMN `reset_password_key` varchar(512) default "";

alter table apps add column updated timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP;

alter table alerts drop column created_at;

alter table alerts drop column send_at;

alter table alerts drop column action_ids;

alter table alerts drop column action_id;

alter table alerts drop column app_id;

CREATE TABLE `sym_upload` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(512) DEFAULT NULL,
  `bin_file` varchar(512) DEFAULT NULL,
  `aclx_file` varchar(512) DEFAULT NULL,
  `added` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8

alter table sym_upload add column batched integer default 0;

alter table auth_user add column email_notifications varchar(1) default 'T';

alter table services modify svc_drnoaction varchar(1) default 'F';

update services set svc_drnoaction='F';

drop table sym_upload;

CREATE TABLE `sym_upload` (`id` int(11) NOT NULL AUTO_INCREMENT,`name` varchar(512) DEFAULT NULL,archive varchar(512) DEFAULT NULL,`added` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,`batched` int(11) DEFAULT '0', PRIMARY KEY (`id`)) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8;

alter table sym_upload drop column name;

# sncf

CREATE TABLE `opensvc`.`comp_log` (
  `id` integer  NOT NULL AUTO_INCREMENT,
  `run_nodename` varchar(64)  NOT NULL,
  `run_module` varchar(64)  NOT NULL,
  `run_status` integer  NOT NULL DEFAULT 1,
  `run_log` text  NOT NULL,
  `run_date` TIMESTAMP  NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
);

CREATE TABLE `opensvc`.`comp_status` (
  `id` integer  NOT NULL AUTO_INCREMENT,
  `run_nodename` varchar(64)  NOT NULL,
  `run_module` varchar(64)  NOT NULL,
  `run_status` integer  NOT NULL DEFAULT 1,
  `run_log` text  NOT NULL,
  `run_date` TIMESTAMP  NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
);

create unique index idx1 on comp_status (run_nodename, run_module);

CREATE TABLE `opensvc`.`comp_moduleset` (
  `id` integer  NOT NULL AUTO_INCREMENT,
  `moduleset` varchar(60)  NOT NULL,
  `module` varchar(60)  NOT NULL,
  PRIMARY KEY (`id`)
);

create unique index idx1 on comp_moduleset (moduleset, module);

CREATE TABLE `comp_rules` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `rule_table` varchar(30) NOT NULL,
  `rule_field` varchar(30) NOT NULL,
  `rule_value` varchar(60) NOT NULL,
  `rule_var_name` varchar(60) NOT NULL,
  `rule_updated` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `rule_var_value` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx1` (`rule_table`,`rule_field`,`rule_value`)
);

create unique index idx1 on comp_rules (rule_table, rule_field, rule_value, rule_var_name);

CREATE TABLE `opensvc`.`comp_node_ruleset` (
  `id` integer  NOT NULL AUTO_INCREMENT,
  `ruleset_node` varchar(60)  NOT NULL,
  `ruleset_name` varchar(60)  NOT NULL,
  `ruleset_updated` timestamp  NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
);

create unique index idx1 on comp_node_ruleset (ruleset_node,ruleset_name);

CREATE TABLE `opensvc`.`comp_node_moduleset` (
  `id` integer  NOT NULL AUTO_INCREMENT,
  `moduleset_node` varchar(60)  NOT NULL,
  `moduleset_name` varchar(60)  NOT NULL,
  `moduleset_updated` timestamp  NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
);

create unique index idx1 on comp_node_moduleset (moduleset_node,moduleset_name);

ALTER TABLE `opensvc`.`comp_rules` ADD COLUMN `rule_name` varchar(60)  NOT NULL AFTER `rule_var_value`,
 ADD COLUMN `rule_op` varchar(4)  NOT NULL AFTER `rule_name`;

ALTER TABLE `opensvc`.`comp_rules` ADD COLUMN `rule_log_op` varchar(3)  NOT NULL AFTER `rule_op`;

ALTER TABLE `opensvc`.`comp_rules` MODIFY COLUMN `rule_log_op` VARCHAR(3)  CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT "AND";

ALTER TABLE `opensvc`.`comp_log` ADD COLUMN `run_ruleset` char(100)  NOT NULL AFTER `run_date`;

ALTER TABLE `opensvc`.`comp_status` ADD COLUMN `run_ruleset` char(100)  NOT NULL AFTER `run_date`;

# sncf

ALTER TABLE `opensvc`.`comp_rules` DROP COLUMN `rule_var_name`,
 DROP COLUMN `rule_var_value`;

CREATE TABLE `opensvc`.`comp_rules_vars` (
  `id` integer  NOT NULL AUTO_INCREMENT,
  `rule_name` varchar(60)  NOT NULL,
  `rule_var_name` varchar(60)  NOT NULL,
  `rule_var_value` varchar(100)  NOT NULL,
  PRIMARY KEY (`id`)
);

create unique index idx1 on comp_rules_vars (rule_name, rule_var_name);

alter table comp_rules_vars add column rule_var_updated timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP;

# ovh
# sncf

create view v_comp_mod_status as (select id, run_module as mod_name, count(id) as mod_total, sum(if(run_status=0,1,0)) as mod_ok, group_concat(run_nodename) as mod_nodes, ifnull(count(id)/sum(if(run_status=0,1,0))*100,0) as mod_percent from comp_status where run_status in (0,1) group by run_module );

drop view v_comp_mod_status;

alter table comp_rules add column rule_author varchar(100) default '';

alter table comp_rules_vars add column rule_var_author varchar(100) default '';

create view v_comp_ruleset_names as (select distinct rule_name from comp_rules order by rule_name);

create view v_comp_explicit_rulesets as (select r.id, r.rule_name, group_concat(distinct concat(v.rule_var_name,'=',v.rule_var_value) separator '|') as variables from comp_rules r left join comp_rules_vars v on r.rule_name=v.rule_name where r.rule_table='comp_node_ruleset' and r.rule_field='ruleset_name' and r.rule_value=r.rule_name  group by r.rule_name order by r.rule_name);

alter table comp_log add column run_action varchar(5) default '';

alter table comp_status add column run_action varchar(5) default '';

create view v_comp_nodes as (select n.*,group_concat(distinct r.ruleset_name separator ', ') as rulesets from v_nodes n left join comp_node_ruleset r on n.nodename=r.ruleset_node group by n.nodename);

create view v_comp_moduleset_names as (select id, moduleset from comp_moduleset group by moduleset order by moduleset);

drop view v_comp_ruleset_names;

create view v_comp_ruleset_names as (select id, rule_name from comp_rules group by rule_name order by rule_name);

alter table comp_status modify column run_action varchar(7) default '';

alter table comp_log modify column run_action varchar(7) default '';

alter table comp_rules drop index idx1;

create unique index idx1 on comp_rules (rule_table, rule_field, rule_value, rule_name);

alter table comp_moduleset add column modset_author varchar(100) default '';

alter table comp_moduleset add column modset_updated timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP;

drop table comp_moduleset;

create table comp_moduleset (`id` int(11) NOT NULL AUTO_INCREMENT, `modset_name` varchar(60) NOT NULL, `modset_author` varchar(100) DEFAULT '', `modset_updated` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (`id`), UNIQUE KEY `idx1` (`modset_name`)) ENGINE=MyISAM AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;

create table comp_moduleset_modules (`id` int(11) NOT NULL AUTO_INCREMENT, `modset_id` integer, `modset_mod_name` varchar(60) NOT NULL, `modset_mod_author` varchar(100) DEFAULT '', `modset_mod_updated` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (`id`), UNIQUE KEY `idx1` (`modset_mod_name`,`modset_id`)) ENGINE=MyISAM AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;

drop table comp_node_moduleset;

CREATE TABLE `comp_node_moduleset` (   `id` int(11) NOT NULL AUTO_INCREMENT, `modset_node` varchar(60) NOT NULL, `modset_id` integer NOT NULL, `modset_mod_author` varchar(100) DEFAULT '', `modset_updated` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,   PRIMARY KEY (`id`), UNIQUE KEY `idx1` (`modset_node`,`modset_id`) ) ENGINE=MyISAM AUTO_INCREMENT=7 DEFAULT CHARSET=utf8;

drop view v_comp_moduleset_names;

# sncf

CREATE TABLE gen_filters (`id` int(11) NOT NULL AUTO_INCREMENT, f_table varchar(30) NOT NULL, f_field varchar(30) NOT NULL, f_value varchar(60) NOT NULL, f_updated timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP, f_author varchar(100) NOT NULL DEFAULT '', f_op varchar(4) NOT NULL, PRIMARY KEY (`id`), UNIQUE KEY `idx1` (f_table, f_field, f_value, f_op)) ENGINE=MyISAM AUTO_INCREMENT=15 DEFAULT CHARSET=utf8;

CREATE TABLE `gen_filtersets` (`id` int(11) NOT NULL AUTO_INCREMENT,   `fset_name` varchar(30) NOT NULL, fset_updated timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP, fset_author varchar(100) NOT NULL DEFAULT '', PRIMARY KEY (`id`),   UNIQUE KEY `idx1` (`fset_name`) ) ENGINE=MyISAM AUTO_INCREMENT=16 DEFAULT CHARSET=utf8;

CREATE TABLE gen_filtersets_filters (`id` int(11) NOT NULL AUTO_INCREMENT, fset_id integer NOT NULL, f_id integer not null, f_log_op varchar(4) NOT NULL, PRIMARY KEY (`id`), UNIQUE KEY `idx1` (f_id, fset_id)) ENGINE=MyISAM AUTO_INCREMENT=15 DEFAULT CHARSET=utf8;

CREATE TABLE comp_rulesets (`id` int(11) NOT NULL AUTO_INCREMENT, ruleset_name varchar(30) NOT NULL, PRIMARY KEY (`id`), UNIQUE KEY `idx1` (ruleset_name)) ENGINE=MyISAM AUTO_INCREMENT=15 DEFAULT CHARSET=utf8;

CREATE TABLE comp_rulesets_filtersets (`id` int(11) NOT NULL AUTO_INCREMENT, ruleset_id integer NOT NULL, fset_id integer NOT NULL, PRIMARY KEY (`id`), UNIQUE KEY `idx1` (ruleset_id)) ENGINE=MyISAM AUTO_INCREMENT=15 DEFAULT CHARSET=utf8;

CREATE TABLE comp_rulesets_nodes (`id` int(11) NOT NULL AUTO_INCREMENT, ruleset_id integer NOT NULL, nodename varchar(100) NOT NULL, PRIMARY KEY (`id`), UNIQUE KEY `idx1` (ruleset_id,nodename)) ENGINE=MyISAM AUTO_INCREMENT=15 DEFAULT CHARSET=utf8;

create view v_gen_filtersets as (SELECT fs.fset_name, fs.fset_updated, fs.fset_author, g.fset_id, g.f_id, g.f_log_op, f.* FROM gen_filtersets fs left join gen_filtersets_filters g on g.fset_id=fs.id left join gen_filters f on g.f_id=f.id order by fs.fset_name);

CREATE TABLE comp_rulesets_variables (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ruleset_id` integer NOT NULL,
  `var_name` varchar(60)  NOT NULL,
  `var_value` varchar(100)  NOT NULL,
  `var_author` varchar(100)  NOT NULL,
  `var_updated` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx1` (ruleset_id, var_name, var_value)
) ENGINE=MyISAM AUTO_INCREMENT=15 DEFAULT CHARSET=utf8;

drop view v_comp_rulesets;

create view v_comp_rulesets as (select r.id as ruleset_id,r.ruleset_name,rv.id,rv.var_name,rv.var_value,rv.var_author,rv.var_updated,rf.fset_id,fs.fset_name from comp_rulesets r left join comp_rulesets_variables rv on rv.ruleset_id = r.id left join comp_rulesets_filtersets rf on r.id=rf.ruleset_id left join gen_filtersets fs on fs.id=rf.fset_id);

drop table v_comp_ruleset_names;

drop table comp_rules_vars;

drop table comp_rules;

drop table comp_node_ruleset;

drop view v_comp_nodes;

create view v_comp_nodes as (select n.*,group_concat(distinct r.ruleset_name separator ', ') as rulesets from v_nodes n left join comp_rulesets_nodes rn on n.nodename=rn.nodename left join comp_rulesets r on r.id=rn.ruleset_id group by n.nodename);

create view v_comp_explicit_rulesets as (select r.id, r.ruleset_name, group_concat(distinct concat(v.var_name,'=',v.var_value) separator '|') as variables from comp_rulesets r join comp_rulesets_variables v on r.id=v.ruleset_id where r.id not in (select ruleset_id from comp_rulesets_filtersets) group by r.id order by r.ruleset_name);

alter table comp_rulesets modify column ruleset_name varchar(100) default '';

alter table gen_filtersets modify column fset_name varchar(100) default '';

drop view v_comp_nodes;

create view v_comp_nodes as (select n.*,group_concat(distinct r.ruleset_name separator ', ') as rulesets, group_concat(distinct m.modset_name separator ', ') as modulesets from v_nodes n left join comp_rulesets_nodes rn on n.nodename=rn.nodename left join comp_rulesets r on r.id=rn.ruleset_id left join comp_node_moduleset mn on mn.modset_node=n.nodename left join comp_moduleset m on m.id=mn.modset_id group by n.nodename);

alter table nodes modify column loc_room varchar(30) default '';

CREATE TABLE log (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `log_action` varchar(100) NOT NULL,
  `log_user` varchar(100)  NOT NULL,
  `log_fmt` varchar(100)  NOT NULL,
  `log_dict` varchar(200)  NOT NULL,
  `log_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=15 DEFAULT CHARSET=utf8;

alter table comp_log add index idx2 (run_date,run_nodename,run_module,run_action);

create view v_comp_status_weekly as (select id,run_nodename,run_module,max(run_status) as run_status,year(run_date) as year,week(run_date) as week from comp_log l where l.run_action='check' group by run_nodename,run_module,year,week order by run_date);

create view v_comp_node_status_weekly as (select id, year, week, run_nodename,sum(if(run_status=0,1,0)) as nb_ok, sum(if(run_status=1,1,0)) as nb_nok,sum(if(run_status=2,1,0)) as nb_na from v_comp_status_weekly group by year,week,run_nodename);

create view v_comp_module_status_weekly as (select id, year, week, run_module,sum(if(run_status=0,1,0)) as nb_ok, sum(if(run_status=1,1,0)) as nb_nok,sum(if(run_status=2,1,0)) as nb_na from v_comp_status_weekly group by year,week,run_module);

-- drop view v_comp_status_weekly;
-- drop view v_comp_node_status_weekly;
-- drop view v_comp_module_status_weekly;

drop view v_users;

CREATE VIEW `v_users` AS (select (select `e`.`time_stamp` AS `time_stamp` from `auth_event` `e` where (`e`.`user_id` = `u`.`id`) order by `e`.`time_stamp` desc limit 1) AS `last`,`u`.`id` AS `id`,concat_ws(' ',`u`.`first_name`,`u`.`last_name`) AS `fullname`,`u`.`email` AS `email`,group_concat(`d`.`domains` separator ', ') AS `domains`,sum((select count(0) AS `count(*)` from `auth_group` `gg` where ((`gg`.`role` = 'Manager') and (`gg`.`id` = `g`.`id`)))) AS `manager`,group_concat(`g`.`role` separator ', ') AS `groups` from (((`auth_user` `u` left join `auth_membership` `m` on((`u`.`id` = `m`.`user_id`))) left join `auth_group` `g` on(((`m`.`group_id` = `g`.`id`) and (not((`g`.`role` like 'user_%')))))) left join `domain_permissions` `d` on((`m`.`group_id` = `d`.`group_id`))) group by id);

alter table comp_rulesets_variables modify column var_value varchar(200) default '';

CREATE TABLE column_filters (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` integer NOT NULL,
  `col_tableid` varchar(20)  NOT NULL,
  `col_name` varchar(20)  NOT NULL,
  `col_filter` varchar(60)  NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=15 DEFAULT CHARSET=utf8;

alter table comp_log add index idx3 (run_nodename);

alter table comp_rulesets_nodes add index idx2 (nodename);

alter table comp_node_moduleset add index idx2 (modset_node);

delete from column_filters;

create unique index idx1 on column_filters (user_id,col_tableid,col_name);

alter table column_filters modify column col_name varchar(60) default '';

alter table column_filters modify column col_tableid varchar(30) default '';

alter table comp_log modify column run_ruleset varchar(500) default '';

alter table comp_rulesets add column ruleset_type varchar(10) default 'explicit';

drop view v_comp_rulesets;

create view v_comp_rulesets as (select r.id as ruleset_id,r.ruleset_name,r.ruleset_type,rv.id,rv.var_name,rv.var_value,rv.var_author,rv.var_updated,rf.fset_id,fs.fset_name from comp_rulesets r left join comp_rulesets_variables rv on rv.ruleset_id = r.id left join comp_rulesets_filtersets rf on r.id=rf.ruleset_id left join gen_filtersets fs on fs.id=rf.fset_id);

drop view v_comp_explicit_rulesets;

CREATE VIEW `v_comp_explicit_rulesets` AS (select `r`.`id` AS `id`,`r`.`ruleset_name` AS `ruleset_name`,group_concat(distinct concat(`v`.`var_name`,'=',`v`.`var_value`) separator '|') AS `variables` from (`comp_rulesets` `r` join `comp_rulesets_variables` `v` on((`r`.`id` = `v`.`ruleset_id`))) where r.ruleset_type='explicit' group by `r`.`id` order by `r`.`ruleset_name`);

alter table log modify column log_dict varchar(400) default null;

alter table nodes add column updated timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP;

drop view v_nodes;

CREATE VIEW `v_nodes` AS (select `n`.`nodename` AS `nodename`,`n`.`loc_country` AS `loc_country`,`n`.`loc_city` AS `loc_city`,`n`.`loc_addr` AS `loc_addr`,`n`.`loc_building` AS `loc_building`,`n`.`loc_floor` AS `loc_floor`,`n`.`loc_room` AS `loc_room`,`n`.`loc_rack` AS `loc_rack`,`n`.`id` AS `id`,`n`.`cpu_freq` AS `cpu_freq`,`n`.`cpu_cores` AS `cpu_cores`,`n`.`cpu_dies` AS `cpu_dies`,`n`.`cpu_vendor` AS `cpu_vendor`,`n`.`cpu_model` AS `cpu_model`,`n`.`mem_banks` AS `mem_banks`,`n`.`mem_slots` AS `mem_slots`,`n`.`mem_bytes` AS `mem_bytes`,`n`.`os_name` AS `os_name`,`n`.`os_release` AS `os_release`,`n`.`os_update` AS `os_update`,`n`.`os_segment` AS `os_segment`,`n`.`os_arch` AS `os_arch`,`n`.`os_vendor` AS `os_vendor`,`n`.`os_kernel` AS `os_kernel`,`n`.`loc_zip` AS `loc_zip`,`n`.`team_responsible` AS `team_responsible`,`n`.`serial` AS `serial`,`n`.`model` AS `model`,`n`.`type` AS `type`,`n`.`warranty_end` AS `warranty_end`,`n`.`status` AS `status`,`n`.`role` AS `role`,`n`.`environnement` AS `environnement`,`n`.`power_cabinet1` AS `power_cabinet1`,`n`.`power_cabinet2` AS `power_cabinet2`,`n`.`power_supply_nb` AS `power_supply_nb`,`n`.`power_protect` AS `power_protect`,`n`.`power_protect_breaker` AS `power_protect_breaker`,`n`.`power_breaker1` AS `power_breaker1`,`n`.`power_breaker2` AS `power_breaker2`,concat_ws(' ',`n`.`os_name`,`n`.`os_vendor`,`n`.`os_release`,`n`.`os_update`) AS `os_concat`, n.updated from `nodes` `n`);

drop view v_svcmon;

CREATE VIEW `v_svcmon` AS select (select count(`a`.`ID`) AS `count(a.id)` from `SVCactions` `a` where ((`m`.`mon_nodname` = `a`.`hostname`) and (`a`.`svcname` = `s`.`svc_name`) and (`a`.`status` = 'err') and ((`a`.`ack` <> 1) or isnull(`a`.`ack`)))) AS `err`,`s`.`svc_vmname` AS `svc_vmname`,`s`.`svc_guestos` AS `svc_guestos`,`s`.`svc_version` AS `svc_version`,`s`.`svc_name` AS `svc_name`,`s`.`svc_nodes` AS `svc_nodes`,`s`.`svc_drpnode` AS `svc_drpnode`,`s`.`svc_drpnodes` AS `svc_drpnodes`,`s`.`svc_drptype` AS `svc_drptype`,`s`.`svc_autostart` AS `svc_autostart`,`s`.`svc_type` AS `svc_type`,`s`.`svc_comment` AS `svc_comment`,`s`.`svc_app` AS `svc_app`,`s`.`svc_drnoaction` AS `svc_drnoaction`,`s`.`updated` AS `svc_updated`,`s`.`svc_envdate` AS `svc_envdate`,`s`.`svc_containertype` AS `svc_containertype`,`s`.`svc_metrocluster` AS `svc_metrocluster`,`s`.`responsibles` AS `responsibles`,`s`.`mailto` AS `mailto`,`s`.`svc_vcpus` AS `svc_vcpus`,`s`.`svc_vmem` AS `svc_vmem`,`m`.`mon_svcname` AS `mon_svcname`,`m`.`mon_svctype` AS `mon_svctype`,`m`.`mon_drptype` AS `mon_drptype`,`m`.`mon_nodname` AS `mon_nodname`,`m`.`mon_nodtype` AS `mon_nodtype`,`m`.`mon_nodmode` AS `mon_nodmode`,`m`.`mon_ipstatus` AS `mon_ipstatus`,`m`.`mon_fsstatus` AS `mon_fsstatus`,`m`.`mon_prinodes` AS `mon_prinodes`,`m`.`mon_hostid` AS `mon_hostid`,`m`.`ID` AS `ID`,`m`.`mon_frozen` AS `mon_frozen`,`m`.`mon_frozentxt` AS `mon_frozentxt`,`m`.`mon_changed` AS `mon_changed`,`m`.`mon_updated` AS `mon_updated`,`m`.`mon_diskstatus` AS `mon_diskstatus`,`m`.`mon_containerstatus` AS `mon_containerstatus`,`m`.`mon_overallstatus` AS `mon_overallstatus`,`n`.`nodename` AS `nodename`,n.updated as node_updated,`n`.`loc_country` AS `loc_country`,`n`.`loc_city` AS `loc_city`,`n`.`loc_addr` AS `loc_addr`,`n`.`loc_building` AS `loc_building`,`n`.`loc_floor` AS `loc_floor`,`n`.`loc_room` AS `loc_room`,`n`.`loc_rack` AS `loc_rack`,`n`.`cpu_freq` AS `cpu_freq`,`n`.`cpu_cores` AS `cpu_cores`,`n`.`cpu_dies` AS `cpu_dies`,`n`.`cpu_vendor` AS `cpu_vendor`,`n`.`cpu_model` AS `cpu_model`,`n`.`mem_banks` AS `mem_banks`,`n`.`mem_slots` AS `mem_slots`,`n`.`mem_bytes` AS `mem_bytes`,`n`.`os_name` AS `os_name`,`n`.`os_release` AS `os_release`,`n`.`os_update` AS `os_update`,`n`.`os_segment` AS `os_segment`,`n`.`os_arch` AS `os_arch`,`n`.`os_vendor` AS `os_vendor`,`n`.`os_kernel` AS `os_kernel`,`n`.`loc_zip` AS `loc_zip`,`n`.`team_responsible` AS `team_responsible`,`n`.`serial` AS `serial`,`n`.`model` AS `model`,`n`.`type` AS `type`,`n`.`warranty_end` AS `warranty_end`,`n`.`status` AS `status`,`n`.`role` AS `role`,`n`.`environnement` AS `environnement`,`n`.`power_supply_nb` AS `power_supply_nb`,`n`.`power_cabinet1` AS `power_cabinet1`,`n`.`power_cabinet2` AS `power_cabinet2`,`n`.`power_protect` AS `power_protect`,`n`.`power_protect_breaker` AS `power_protect_breaker`,`n`.`power_breaker1` AS `power_breaker1`,`n`.`power_breaker2` AS `power_breaker2`,`m`.`mon_syncstatus` AS `mon_syncstatus`,`m`.`mon_appstatus` AS `mon_appstatus` from ((`svcmon` `m` join `v_services` `s` on((`s`.`svc_name` = `m`.`mon_svcname`))) left join `nodes` `n` on((`m`.`mon_nodname` = `n`.`nodename`)));

CREATE TABLE `opensvc`.`wiki_pages` (
  `id` integer NOT NULL AUTO_INCREMENT,
  `name` varchar(100),
  `author` varchar(100),
  `saved_on` datetime,
  `title` varchar(100),
  `body` text,
  `change_note` varchar(200),
  PRIMARY KEY (`id`)
);

drop table svcmessages;

alter table services drop key svc_name;

drop view v_comp_nodes;

create view v_comp_nodes as (select n.*,group_concat(distinct r.ruleset_name separator ', ') as rulesets, group_concat(distinct m.modset_name separator ', ') as modulesets from v_nodes n left join comp_rulesets_nodes rn on n.nodename=rn.nodename left join comp_rulesets r on r.id=rn.ruleset_id left join comp_node_moduleset mn on mn.modset_node=n.nodename left join comp_moduleset m on m.id=mn.modset_id group by n.nodename);

alter table gen_filtersets_filters add column encap_fset_id integer;

alter table gen_filtersets_filters add column f_order integer default 0;

drop view v_gen_filtersets;

create view v_gen_filtersets as (SELECT fs.fset_name, fs.fset_updated, fs.fset_author, g.fset_id, g.f_order, g.f_id, g.encap_fset_id, (select fset_name from gen_filtersets where id=g.encap_fset_id) as encap_fset_name, g.f_log_op, f.* FROM gen_filtersets fs left join gen_filtersets_filters g on g.fset_id=fs.id left join gen_filters f on g.f_id=f.id order by g.fset_id, g.f_order);

alter table gen_filtersets_filters drop index idx1; 

CREATE TABLE `stats_fs_u` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `date` datetime NOT NULL,
  `nodename` varchar(60) NOT NULL,
  `mntpt` varchar(200) NOT NULL,
  `size` int(11) NOT NULL,
  `used` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `index_1` (`date`,`nodename`,`mntpt`)
);

alter table gen_filtersets_filters modify column f_log_op varchar(8) NOT NULL;

alter table gen_filters modify column f_op varchar(8) NOT NULL;

alter table svcmon_log add index mon_begin (mon_begin);

alter table svcmon_log add index mon_end (mon_end);

create unique index idx1 on stats_netdev (date, dev, nodename);

alter table log add index idx1 (log_user);

alter table log add index idx2 (log_date);

CREATE TABLE `upc_dashboard` (
  `id` integer  NOT NULL AUTO_INCREMENT,
  `upc_user_id` integer  NOT NULL,
  `upc_dashboard` varchar(100)  NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `index_1` (`upc_user_id`,`upc_dashboard`)
);

alter table comp_rulesets_variables drop index idx1;

alter table comp_rulesets_variables modify column var_value text NOT NULL;

ALTER TABLE nodes CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci;

alter table auth_user add column perpage integer default 20;

update auth_user set perpage=20;

alter table log modify column log_dict text;

CREATE TABLE `action_queue` (
  `id` integer  NOT NULL AUTO_INCREMENT,
  `status` varchar(1) default 'W',
  `command` text  NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx1` (`status`)
);

alter table action_queue add column date_queued timestamp not null default CURRENT_TIMESTAMP;

alter table action_queue add column date_dequeued timestamp;

alter table svcmon add column mon_hbstatus varchar(10);

alter table svcmon_log add column mon_hbstatus varchar(10) default 'undef';

drop view v_svcmon;

CREATE VIEW `v_svcmon` AS select (select count(`a`.`ID`) AS `count(a.id)` from `SVCactions` `a` where ((`m`.`mon_nodname` = `a`.`hostname`) and (`a`.`svcname` = `s`.`svc_name`) and (`a`.`status` = 'err') and ((`a`.`ack` <> 1) or isnull(`a`.`ack`)))) AS `err`,`s`.`svc_vmname` AS `svc_vmname`,`s`.`svc_guestos` AS `svc_guestos`,`s`.`svc_version` AS `svc_version`,`s`.`svc_name` AS `svc_name`,`s`.`svc_nodes` AS `svc_nodes`,`s`.`svc_drpnode` AS `svc_drpnode`,`s`.`svc_drpnodes` AS `svc_drpnodes`,`s`.`svc_drptype` AS `svc_drptype`,`s`.`svc_autostart` AS `svc_autostart`,`s`.`svc_type` AS `svc_type`,`s`.`svc_comment` AS `svc_comment`,`s`.`svc_app` AS `svc_app`,`s`.`svc_drnoaction` AS `svc_drnoaction`,`s`.`updated` AS `svc_updated`,`s`.`svc_envdate` AS `svc_envdate`,`s`.`svc_containertype` AS `svc_containertype`,`s`.`svc_metrocluster` AS `svc_metrocluster`,`s`.`responsibles` AS `responsibles`,`s`.`mailto` AS `mailto`,`s`.`svc_vcpus` AS `svc_vcpus`,`s`.`svc_vmem` AS `svc_vmem`,`m`.`mon_svcname` AS `mon_svcname`,`m`.`mon_svctype` AS `mon_svctype`,`m`.`mon_drptype` AS `mon_drptype`,`m`.`mon_nodname` AS `mon_nodname`,`m`.`mon_nodtype` AS `mon_nodtype`,`m`.`mon_nodmode` AS `mon_nodmode`,`m`.`mon_ipstatus` AS `mon_ipstatus`,`m`.`mon_fsstatus` AS `mon_fsstatus`,`m`.`mon_prinodes` AS `mon_prinodes`,`m`.`mon_hostid` AS `mon_hostid`,`m`.`ID` AS `ID`,`m`.`mon_frozen` AS `mon_frozen`,`m`.`mon_frozentxt` AS `mon_frozentxt`,`m`.`mon_changed` AS `mon_changed`,`m`.`mon_updated` AS `mon_updated`,`m`.`mon_diskstatus` AS `mon_diskstatus`,`m`.`mon_containerstatus` AS `mon_containerstatus`,`m`.`mon_overallstatus` AS `mon_overallstatus`,`n`.`nodename` AS `nodename`,n.updated as node_updated,`n`.`loc_country` AS `loc_country`,`n`.`loc_city` AS `loc_city`,`n`.`loc_addr` AS `loc_addr`,`n`.`loc_building` AS `loc_building`,`n`.`loc_floor` AS `loc_floor`,`n`.`loc_room` AS `loc_room`,`n`.`loc_rack` AS `loc_rack`,`n`.`cpu_freq` AS `cpu_freq`,`n`.`cpu_cores` AS `cpu_cores`,`n`.`cpu_dies` AS `cpu_dies`,`n`.`cpu_vendor` AS `cpu_vendor`,`n`.`cpu_model` AS `cpu_model`,`n`.`mem_banks` AS `mem_banks`,`n`.`mem_slots` AS `mem_slots`,`n`.`mem_bytes` AS `mem_bytes`,`n`.`os_name` AS `os_name`,`n`.`os_release` AS `os_release`,`n`.`os_update` AS `os_update`,`n`.`os_segment` AS `os_segment`,`n`.`os_arch` AS `os_arch`,`n`.`os_vendor` AS `os_vendor`,`n`.`os_kernel` AS `os_kernel`,`n`.`loc_zip` AS `loc_zip`,`n`.`team_responsible` AS `team_responsible`,`n`.`serial` AS `serial`,`n`.`model` AS `model`,`n`.`type` AS `type`,`n`.`warranty_end` AS `warranty_end`,`n`.`status` AS `status`,`n`.`role` AS `role`,`n`.`environnement` AS `environnement`,`n`.`power_supply_nb` AS `power_supply_nb`,`n`.`power_cabinet1` AS `power_cabinet1`,`n`.`power_cabinet2` AS `power_cabinet2`,`n`.`power_protect` AS `power_protect`,`n`.`power_protect_breaker` AS `power_protect_breaker`,`n`.`power_breaker1` AS `power_breaker1`,`n`.`power_breaker2` AS `power_breaker2`,`m`.`mon_syncstatus` AS `mon_syncstatus`, m.mon_hbstatus, `m`.`mon_appstatus` AS `mon_appstatus` from ((`svcmon` `m` join `v_services` `s` on((`s`.`svc_name` = `m`.`mon_svcname`))) left join `nodes` `n` on((`m`.`mon_nodname` = `n`.`nodename`)));

drop view v_svcmon_clusters;

create view v_svcmon_clusters as (select *, (select group_concat(mon_nodname order by mon_nodname) from svcmon where mon_svcname=m.mon_svcname) as nodes from v_svcmon m);

alter table services change column changed svc_created timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP;

drop view v_services;

CREATE VIEW `v_services` AS select `s`.`svc_vmname` AS `svc_vmname`,`s`.`svc_guestos` AS `svc_guestos`,`s`.`svc_version` AS `svc_version`,`s`.`svc_hostid` AS `svc_hostid`,`s`.`svc_name` AS `svc_name`,`s`.`svc_nodes` AS `svc_nodes`,`s`.`svc_drpnode` AS `svc_drpnode`,`s`.`svc_ipname` AS `svc_ipname`,`s`.`svc_ipdev` AS `svc_ipdev`,`s`.`svc_drpipname` AS `svc_drpipname`,`s`.`svc_drpipdev` AS `svc_drpipdev`,`s`.`svc_drptype` AS `svc_drptype`,`s`.`svc_fs` AS `svc_fs`,`s`.`svc_dev` AS `svc_dev`,`s`.`svc_autostart` AS `svc_autostart`,`s`.`svc_mntopt` AS `svc_mntopt`,`s`.`svc_scsi` AS `svc_scsi`,`s`.`svc_type` AS `svc_type`,`s`.`svc_drpnodes` AS `svc_drpnodes`,`s`.`svc_comment` AS `svc_comment`,`s`.`svc_app` AS `svc_app`,`s`.`svc_drnoaction` AS `svc_drnoaction`,svc_created,`s`.`updated` AS `updated`,`s`.`cksum` AS `cksum`,`s`.`svc_envdate` AS `svc_envdate`,`s`.`svc_containertype` AS `svc_containertype`,`s`.`svc_metrocluster` AS `svc_metrocluster`,`s`.`id` AS `id`,`s`.`svc_hasec` AS `svc_hasec`,`s`.`svc_hapri` AS `svc_hapri`,`s`.`svc_hastonith` AS `svc_hastonith`,`s`.`svc_hastartup` AS `svc_hastartup`,`s`.`svc_wave` AS `svc_wave`,`s`.`svc_vcpus` AS `svc_vcpus`,`s`.`svc_vmem` AS `svc_vmem`,`a`.`app` AS `app`,`a`.`responsibles` AS `responsibles`,`a`.`mailto` AS `mailto` from (`services` `s` left join `v_apps` `a` on((`a`.`app` = `s`.`svc_app`))) group by `s`.`svc_name`;

drop view v_svcmon;

CREATE VIEW `v_svcmon` AS select (select count(`a`.`ID`) AS `count(a.id)` from `SVCactions` `a` where ((`m`.`mon_nodname` = `a`.`hostname`) and (`a`.`svcname` = `s`.`svc_name`) and (`a`.`status` = 'err') and ((`a`.`ack` <> 1) or isnull(`a`.`ack`)))) AS `err`,`s`.`svc_vmname` AS `svc_vmname`,`s`.`svc_guestos` AS `svc_guestos`,`s`.`svc_version` AS `svc_version`,`s`.`svc_name` AS `svc_name`,`s`.`svc_nodes` AS `svc_nodes`,`s`.`svc_drpnode` AS `svc_drpnode`,`s`.`svc_drpnodes` AS `svc_drpnodes`,`s`.`svc_drptype` AS `svc_drptype`,`s`.`svc_autostart` AS `svc_autostart`,`s`.`svc_type` AS `svc_type`,`s`.`svc_comment` AS `svc_comment`,`s`.`svc_app` AS `svc_app`,`s`.`svc_drnoaction` AS `svc_drnoaction`,s.svc_created,`s`.`updated` AS `svc_updated`,`s`.`svc_envdate` AS `svc_envdate`,`s`.`svc_containertype` AS `svc_containertype`,`s`.`svc_metrocluster` AS `svc_metrocluster`,`s`.`responsibles` AS `responsibles`,`s`.`mailto` AS `mailto`,`s`.`svc_vcpus` AS `svc_vcpus`,`s`.`svc_vmem` AS `svc_vmem`,`m`.`mon_svcname` AS `mon_svcname`,`m`.`mon_svctype` AS `mon_svctype`,`m`.`mon_drptype` AS `mon_drptype`,`m`.`mon_nodname` AS `mon_nodname`,`m`.`mon_nodtype` AS `mon_nodtype`,`m`.`mon_nodmode` AS `mon_nodmode`,`m`.`mon_ipstatus` AS `mon_ipstatus`,`m`.`mon_fsstatus` AS `mon_fsstatus`,`m`.`mon_prinodes` AS `mon_prinodes`,`m`.`mon_hostid` AS `mon_hostid`,`m`.`ID` AS `ID`,`m`.`mon_frozen` AS `mon_frozen`,`m`.`mon_frozentxt` AS `mon_frozentxt`,`m`.`mon_changed` AS `mon_changed`,`m`.`mon_updated` AS `mon_updated`,`m`.`mon_diskstatus` AS `mon_diskstatus`,`m`.`mon_containerstatus` AS `mon_containerstatus`,`m`.`mon_overallstatus` AS `mon_overallstatus`,`n`.`nodename` AS `nodename`,`n`.`updated` AS `node_updated`,`n`.`loc_country` AS `loc_country`,`n`.`loc_city` AS `loc_city`,`n`.`loc_addr` AS `loc_addr`,`n`.`loc_building` AS `loc_building`,`n`.`loc_floor` AS `loc_floor`,`n`.`loc_room` AS `loc_room`,`n`.`loc_rack` AS `loc_rack`,`n`.`cpu_freq` AS `cpu_freq`,`n`.`cpu_cores` AS `cpu_cores`,`n`.`cpu_dies` AS `cpu_dies`,`n`.`cpu_vendor` AS `cpu_vendor`,`n`.`cpu_model` AS `cpu_model`,`n`.`mem_banks` AS `mem_banks`,`n`.`mem_slots` AS `mem_slots`,`n`.`mem_bytes` AS `mem_bytes`,`n`.`os_name` AS `os_name`,`n`.`os_release` AS `os_release`,`n`.`os_update` AS `os_update`,`n`.`os_segment` AS `os_segment`,`n`.`os_arch` AS `os_arch`,`n`.`os_vendor` AS `os_vendor`,`n`.`os_kernel` AS `os_kernel`,`n`.`loc_zip` AS `loc_zip`,`n`.`team_responsible` AS `team_responsible`,`n`.`serial` AS `serial`,`n`.`model` AS `model`,`n`.`type` AS `type`,`n`.`warranty_end` AS `warranty_end`,`n`.`status` AS `status`,`n`.`role` AS `role`,`n`.`environnement` AS `environnement`,`n`.`power_supply_nb` AS `power_supply_nb`,`n`.`power_cabinet1` AS `power_cabinet1`,`n`.`power_cabinet2` AS `power_cabinet2`,`n`.`power_protect` AS `power_protect`,`n`.`power_protect_breaker` AS `power_protect_breaker`,`n`.`power_breaker1` AS `power_breaker1`,`n`.`power_breaker2` AS `power_breaker2`,`m`.`mon_syncstatus` AS `mon_syncstatus`,`m`.`mon_hbstatus` AS `mon_hbstatus`,`m`.`mon_appstatus` AS `mon_appstatus` from ((`svcmon` `m` join `v_services` `s` on((`s`.`svc_name` = `m`.`mon_svcname`))) left join `nodes` `n` on((convert(`m`.`mon_nodname` using utf8) = `n`.`nodename`)));

update filters set fil_search_table="SVCactions" where fil_name like 'action%';

update filters set fil_search_table="SVCactions" where fil_name like '%ackn%';

drop view v_gen_filtersets;

create view v_gen_filtersets as (SELECT fs.fset_name, fs.fset_updated, fs.fset_author, fs.id as fset_id, g.f_order, f.id as f_id, g.encap_fset_id, (select fset_name from gen_filtersets where id=g.encap_fset_id) as encap_fset_name, g.f_log_op, f.* FROM gen_filtersets fs left join gen_filtersets_filters g on g.fset_id=fs.id left join gen_filters f on g.f_id=f.id order by fs.id, g.f_order);

alter table services add column svc_cluster_type varchar(20) default 'failover';
alter table services add column svc_flex_min_nodes integer default 1;
alter table services add column svc_flex_max_nodes integer default 0;
alter table services add column svc_flex_cpu_low_threshold integer default 10;
alter table services add column svc_flex_cpu_high_threshold integer default 70;

drop view v_services;

CREATE VIEW `v_services` AS select s.svc_cluster_type, s.svc_flex_min_nodes, s.svc_flex_max_nodes, s.svc_flex_cpu_low_threshold, s.svc_flex_cpu_high_threshold, `s`.`svc_vmname` AS `svc_vmname`,`s`.`svc_guestos` AS `svc_guestos`,`s`.`svc_version` AS `svc_version`,`s`.`svc_hostid` AS `svc_hostid`,`s`.`svc_name` AS `svc_name`,`s`.`svc_nodes` AS `svc_nodes`,`s`.`svc_drpnode` AS `svc_drpnode`,`s`.`svc_ipname` AS `svc_ipname`,`s`.`svc_ipdev` AS `svc_ipdev`,`s`.`svc_drpipname` AS `svc_drpipname`,`s`.`svc_drpipdev` AS `svc_drpipdev`,`s`.`svc_drptype` AS `svc_drptype`,`s`.`svc_fs` AS `svc_fs`,`s`.`svc_dev` AS `svc_dev`,`s`.`svc_autostart` AS `svc_autostart`,`s`.`svc_mntopt` AS `svc_mntopt`,`s`.`svc_scsi` AS `svc_scsi`,`s`.`svc_type` AS `svc_type`,`s`.`svc_drpnodes` AS `svc_drpnodes`,`s`.`svc_comment` AS `svc_comment`,`s`.`svc_app` AS `svc_app`,`s`.`svc_drnoaction` AS `svc_drnoaction`,svc_created,`s`.`updated` AS `updated`,`s`.`cksum` AS `cksum`,`s`.`svc_envdate` AS `svc_envdate`,`s`.`svc_containertype` AS `svc_containertype`,`s`.`svc_metrocluster` AS `svc_metrocluster`,`s`.`id` AS `id`,`s`.`svc_hasec` AS `svc_hasec`,`s`.`svc_hapri` AS `svc_hapri`,`s`.`svc_hastonith` AS `svc_hastonith`,`s`.`svc_hastartup` AS `svc_hastartup`,`s`.`svc_wave` AS `svc_wave`,`s`.`svc_vcpus` AS `svc_vcpus`,`s`.`svc_vmem` AS `svc_vmem`,`a`.`app` AS `app`,`a`.`responsibles` AS `responsibles`,`a`.`mailto` AS `mailto` from (`services` `s` left join `v_apps` `a` on((`a`.`app` = `s`.`svc_app`))) group by `s`.`svc_name`;

drop view v_svcmon;

CREATE VIEW `v_svcmon` AS select (select count(`a`.`ID`) AS `count(a.id)` from `SVCactions` `a` where ((`m`.`mon_nodname` = `a`.`hostname`) and (`a`.`svcname` = `s`.`svc_name`) and (`a`.`status` = 'err') and ((`a`.`ack` <> 1) or isnull(`a`.`ack`)))) AS `err`,s.svc_cluster_type, s.svc_flex_min_nodes, s.svc_flex_max_nodes, s.svc_flex_cpu_low_threshold, s.svc_flex_cpu_high_threshold, `s`.`svc_vmname` AS `svc_vmname`,`s`.`svc_guestos` AS `svc_guestos`,`s`.`svc_version` AS `svc_version`,`s`.`svc_name` AS `svc_name`,`s`.`svc_nodes` AS `svc_nodes`,`s`.`svc_drpnode` AS `svc_drpnode`,`s`.`svc_drpnodes` AS `svc_drpnodes`,`s`.`svc_drptype` AS `svc_drptype`,`s`.`svc_autostart` AS `svc_autostart`,`s`.`svc_type` AS `svc_type`,`s`.`svc_comment` AS `svc_comment`,`s`.`svc_app` AS `svc_app`,`s`.`svc_drnoaction` AS `svc_drnoaction`,s.svc_created,`s`.`updated` AS `svc_updated`,`s`.`svc_envdate` AS `svc_envdate`,`s`.`svc_containertype` AS `svc_containertype`,`s`.`svc_metrocluster` AS `svc_metrocluster`,`s`.`responsibles` AS `responsibles`,`s`.`mailto` AS `mailto`,`s`.`svc_vcpus` AS `svc_vcpus`,`s`.`svc_vmem` AS `svc_vmem`,`m`.`mon_svcname` AS `mon_svcname`,`m`.`mon_svctype` AS `mon_svctype`,`m`.`mon_drptype` AS `mon_drptype`,`m`.`mon_nodname` AS `mon_nodname`,`m`.`mon_nodtype` AS `mon_nodtype`,`m`.`mon_nodmode` AS `mon_nodmode`,`m`.`mon_ipstatus` AS `mon_ipstatus`,`m`.`mon_fsstatus` AS `mon_fsstatus`,`m`.`mon_prinodes` AS `mon_prinodes`,`m`.`mon_hostid` AS `mon_hostid`,`m`.`ID` AS `ID`,`m`.`mon_frozen` AS `mon_frozen`,`m`.`mon_frozentxt` AS `mon_frozentxt`,`m`.`mon_changed` AS `mon_changed`,`m`.`mon_updated` AS `mon_updated`,`m`.`mon_diskstatus` AS `mon_diskstatus`,`m`.`mon_containerstatus` AS `mon_containerstatus`,`m`.`mon_overallstatus` AS `mon_overallstatus`,`n`.`nodename` AS `nodename`,`n`.`updated` AS `node_updated`,`n`.`loc_country` AS `loc_country`,`n`.`loc_city` AS `loc_city`,`n`.`loc_addr` AS `loc_addr`,`n`.`loc_building` AS `loc_building`,`n`.`loc_floor` AS `loc_floor`,`n`.`loc_room` AS `loc_room`,`n`.`loc_rack` AS `loc_rack`,`n`.`cpu_freq` AS `cpu_freq`,`n`.`cpu_cores` AS `cpu_cores`,`n`.`cpu_dies` AS `cpu_dies`,`n`.`cpu_vendor` AS `cpu_vendor`,`n`.`cpu_model` AS `cpu_model`,`n`.`mem_banks` AS `mem_banks`,`n`.`mem_slots` AS `mem_slots`,`n`.`mem_bytes` AS `mem_bytes`,`n`.`os_name` AS `os_name`,`n`.`os_release` AS `os_release`,`n`.`os_update` AS `os_update`,`n`.`os_segment` AS `os_segment`,`n`.`os_arch` AS `os_arch`,`n`.`os_vendor` AS `os_vendor`,`n`.`os_kernel` AS `os_kernel`,`n`.`loc_zip` AS `loc_zip`,`n`.`team_responsible` AS `team_responsible`,`n`.`serial` AS `serial`,`n`.`model` AS `model`,`n`.`type` AS `type`,`n`.`warranty_end` AS `warranty_end`,`n`.`status` AS `status`,`n`.`role` AS `role`,`n`.`environnement` AS `environnement`,`n`.`power_supply_nb` AS `power_supply_nb`,`n`.`power_cabinet1` AS `power_cabinet1`,`n`.`power_cabinet2` AS `power_cabinet2`,`n`.`power_protect` AS `power_protect`,`n`.`power_protect_breaker` AS `power_protect_breaker`,`n`.`power_breaker1` AS `power_breaker1`,`n`.`power_breaker2` AS `power_breaker2`,`m`.`mon_syncstatus` AS `mon_syncstatus`,`m`.`mon_hbstatus` AS `mon_hbstatus`,`m`.`mon_appstatus` AS `mon_appstatus` from ((`svcmon` `m` join `v_services` `s` on((`s`.`svc_name` = `m`.`mon_svcname`))) left join `nodes` `n` on((convert(`m`.`mon_nodname` using utf8) = `n`.`nodename`)));

create view v_flex_status as (select p.id, p.mon_svcname as svc_name, p.svc_flex_min_nodes, p.svc_flex_max_nodes, p.svc_flex_cpu_low_threshold, p.svc_flex_cpu_high_threshold, count(1) as n, (select count(1) from svcmon c where c.mon_svcname=p.mon_svcname and c.mon_overallstatus="up") as up, (select 100-c.idle from stats_cpu c, svcmon m where c.nodename=m.mon_nodname and m.mon_svcname=p.mon_svcname and date>adddate(now(), interval - 15 minute) and c.CPU="all" and m.mon_overallstatus="up" group by p.mon_svcname) as cpu from v_svcmon p where svc_cluster_type like "%flex" group by p.mon_svcname);

alter table comp_log add index idx4 (run_action);

alter table nodes modify column nodename varchar(60) NOT NULL;

alter table services modify column svc_autostart varchar(60) NOT NULL;

# 2011-04-04

alter table svcmon add column mon_availstatus varchar(10) default 'undef';

alter table svcmon_log add column mon_availstatus varchar(10) default 'undef';

drop view v_svcmon;

CREATE VIEW `v_svcmon` AS select (select count(`a`.`ID`) AS `count(a.id)` from `SVCactions` `a` where ((`m`.`mon_nodname` = `a`.`hostname`) and (`a`.`svcname` = `s`.`svc_name`) and (`a`.`status` = 'err') and ((`a`.`ack` <> 1) or isnull(`a`.`ack`)))) AS `err`,s.svc_cluster_type, s.svc_flex_min_nodes, s.svc_flex_max_nodes, s.svc_flex_cpu_low_threshold, s.svc_flex_cpu_high_threshold, `s`.`svc_vmname` AS `svc_vmname`,`s`.`svc_guestos` AS `svc_guestos`,`s`.`svc_version` AS `svc_version`,`s`.`svc_name` AS `svc_name`,`s`.`svc_nodes` AS `svc_nodes`,`s`.`svc_drpnode` AS `svc_drpnode`,`s`.`svc_drpnodes` AS `svc_drpnodes`,`s`.`svc_drptype` AS `svc_drptype`,`s`.`svc_autostart` AS `svc_autostart`,`s`.`svc_type` AS `svc_type`,`s`.`svc_comment` AS `svc_comment`,`s`.`svc_app` AS `svc_app`,`s`.`svc_drnoaction` AS `svc_drnoaction`,s.svc_created,`s`.`updated` AS `svc_updated`,`s`.`svc_envdate` AS `svc_envdate`,`s`.`svc_containertype` AS `svc_containertype`,`s`.`svc_metrocluster` AS `svc_metrocluster`,`s`.`responsibles` AS `responsibles`,`s`.`mailto` AS `mailto`,`s`.`svc_vcpus` AS `svc_vcpus`,`s`.`svc_vmem` AS `svc_vmem`,`m`.`mon_svcname` AS `mon_svcname`,`m`.`mon_svctype` AS `mon_svctype`,`m`.`mon_drptype` AS `mon_drptype`,`m`.`mon_nodname` AS `mon_nodname`,`m`.`mon_nodtype` AS `mon_nodtype`,`m`.`mon_nodmode` AS `mon_nodmode`,`m`.`mon_ipstatus` AS `mon_ipstatus`,`m`.`mon_fsstatus` AS `mon_fsstatus`,`m`.`mon_prinodes` AS `mon_prinodes`,`m`.`mon_hostid` AS `mon_hostid`,`m`.`ID` AS `ID`,`m`.`mon_frozen` AS `mon_frozen`,`m`.`mon_frozentxt` AS `mon_frozentxt`,`m`.`mon_changed` AS `mon_changed`,`m`.`mon_updated` AS `mon_updated`,`m`.`mon_diskstatus` AS `mon_diskstatus`,`m`.`mon_containerstatus` AS `mon_containerstatus`,`m`.`mon_overallstatus` AS `mon_overallstatus`,`n`.`nodename` AS `nodename`,`n`.`updated` AS `node_updated`,`n`.`loc_country` AS `loc_country`,`n`.`loc_city` AS `loc_city`,`n`.`loc_addr` AS `loc_addr`,`n`.`loc_building` AS `loc_building`,`n`.`loc_floor` AS `loc_floor`,`n`.`loc_room` AS `loc_room`,`n`.`loc_rack` AS `loc_rack`,`n`.`cpu_freq` AS `cpu_freq`,`n`.`cpu_cores` AS `cpu_cores`,`n`.`cpu_dies` AS `cpu_dies`,`n`.`cpu_vendor` AS `cpu_vendor`,`n`.`cpu_model` AS `cpu_model`,`n`.`mem_banks` AS `mem_banks`,`n`.`mem_slots` AS `mem_slots`,`n`.`mem_bytes` AS `mem_bytes`,`n`.`os_name` AS `os_name`,`n`.`os_release` AS `os_release`,`n`.`os_update` AS `os_update`,`n`.`os_segment` AS `os_segment`,`n`.`os_arch` AS `os_arch`,`n`.`os_vendor` AS `os_vendor`,`n`.`os_kernel` AS `os_kernel`,`n`.`loc_zip` AS `loc_zip`,`n`.`team_responsible` AS `team_responsible`,`n`.`serial` AS `serial`,`n`.`model` AS `model`,`n`.`type` AS `type`,`n`.`warranty_end` AS `warranty_end`,`n`.`status` AS `status`,`n`.`role` AS `role`,`n`.`environnement` AS `environnement`,`n`.`power_supply_nb` AS `power_supply_nb`,`n`.`power_cabinet1` AS `power_cabinet1`,`n`.`power_cabinet2` AS `power_cabinet2`,`n`.`power_protect` AS `power_protect`,`n`.`power_protect_breaker` AS `power_protect_breaker`,`n`.`power_breaker1` AS `power_breaker1`,`n`.`power_breaker2` AS `power_breaker2`,`m`.`mon_syncstatus` AS `mon_syncstatus`,`m`.`mon_hbstatus` AS `mon_hbstatus`,`m`.`mon_availstatus` AS `mon_availstatus`,`m`.`mon_appstatus` AS `mon_appstatus` from ((`svcmon` `m` join `v_services` `s` on((`s`.`svc_name` = `m`.`mon_svcname`))) left join `nodes` `n` on((convert(`m`.`mon_nodname` using utf8) = `n`.`nodename`)));

drop view v_svc_group_status;

create view v_svc_group_status as (select `svcmon`.`ID` AS `id`,`svcmon`.`mon_svcname` AS `svcname`,`svcmon`.`mon_svctype` AS `svctype`,group_concat(`trusted_status`(`svcmon`.`mon_availstatus`,`svcmon`.`mon_updated`) separator ',') AS `groupstatus`, group_concat(`svcmon`.`mon_nodname` separator ',') AS `nodes` from `svcmon` group by `svcmon`.`mon_svcname`);

# 2011-04-05

alter table services add column svc_status varchar(10) default 'undef';

alter table services add column svc_availstatus varchar(10) default 'undef';

drop view v_gen_filtersets;

create view v_gen_filtersets as (SELECT fs.fset_name, fs.fset_updated, fs.fset_author, fs.id as fset_id, g.id as join_id, g.f_order, f.id as f_id, g.encap_fset_id, (select fset_name from gen_filtersets where id=g.encap_fset_id) as encap_fset_name, g.f_log_op, f.* FROM gen_filtersets fs left join gen_filtersets_filters g on g.fset_id=fs.id left join gen_filters f on g.f_id=f.id order by fs.id, g.f_order);

drop view v_services;

CREATE VIEW `v_services` AS select s.svc_status, s.svc_availstatus, s.svc_cluster_type, s.svc_flex_min_nodes, s.svc_flex_max_nodes, s.svc_flex_cpu_low_threshold, s.svc_flex_cpu_high_threshold, `s`.`svc_vmname` AS `svc_vmname`,`s`.`svc_guestos` AS `svc_guestos`,`s`.`svc_version` AS `svc_version`,`s`.`svc_hostid` AS `svc_hostid`,`s`.`svc_name` AS `svc_name`,`s`.`svc_nodes` AS `svc_nodes`,`s`.`svc_drpnode` AS `svc_drpnode`,`s`.`svc_ipname` AS `svc_ipname`,`s`.`svc_ipdev` AS `svc_ipdev`,`s`.`svc_drpipname` AS `svc_drpipname`,`s`.`svc_drpipdev` AS `svc_drpipdev`,`s`.`svc_drptype` AS `svc_drptype`,`s`.`svc_fs` AS `svc_fs`,`s`.`svc_dev` AS `svc_dev`,`s`.`svc_autostart` AS `svc_autostart`,`s`.`svc_mntopt` AS `svc_mntopt`,`s`.`svc_scsi` AS `svc_scsi`,`s`.`svc_type` AS `svc_type`,`s`.`svc_drpnodes` AS `svc_drpnodes`,`s`.`svc_comment` AS `svc_comment`,`s`.`svc_app` AS `svc_app`,`s`.`svc_drnoaction` AS `svc_drnoaction`,svc_created,`s`.`updated` AS `updated`,`s`.`cksum` AS `cksum`,`s`.`svc_envdate` AS `svc_envdate`,`s`.`svc_containertype` AS `svc_containertype`,`s`.`svc_metrocluster` AS `svc_metrocluster`,`s`.`id` AS `id`,`s`.`svc_hasec` AS `svc_hasec`,`s`.`svc_hapri` AS `svc_hapri`,`s`.`svc_hastonith` AS `svc_hastonith`,`s`.`svc_hastartup` AS `svc_hastartup`,`s`.`svc_wave` AS `svc_wave`,`s`.`svc_vcpus` AS `svc_vcpus`,`s`.`svc_vmem` AS `svc_vmem`,`a`.`app` AS `app`,`a`.`responsibles` AS `responsibles`,`a`.`mailto` AS `mailto` from (`services` `s` left join `v_apps` `a` on((`a`.`app` = `s`.`svc_app`))) group by `s`.`svc_name`;

drop view v_svcmon;

CREATE VIEW `v_svcmon` AS select (select count(`a`.`ID`) AS `count(a.id)` from `SVCactions` `a` where ((`m`.`mon_nodname` = `a`.`hostname`) and (`a`.`svcname` = `s`.`svc_name`) and (`a`.`status` = 'err') and ((`a`.`ack` <> 1) or isnull(`a`.`ack`)))) AS `err`,s.svc_cluster_type, s.svc_status, s.svc_availstatus, s.svc_flex_min_nodes, s.svc_flex_max_nodes, s.svc_flex_cpu_low_threshold, s.svc_flex_cpu_high_threshold, `s`.`svc_vmname` AS `svc_vmname`,`s`.`svc_guestos` AS `svc_guestos`,`s`.`svc_version` AS `svc_version`,`s`.`svc_name` AS `svc_name`,`s`.`svc_nodes` AS `svc_nodes`,`s`.`svc_drpnode` AS `svc_drpnode`,`s`.`svc_drpnodes` AS `svc_drpnodes`,`s`.`svc_drptype` AS `svc_drptype`,`s`.`svc_autostart` AS `svc_autostart`,`s`.`svc_type` AS `svc_type`,`s`.`svc_comment` AS `svc_comment`,`s`.`svc_app` AS `svc_app`,`s`.`svc_drnoaction` AS `svc_drnoaction`,s.svc_created,`s`.`updated` AS `svc_updated`,`s`.`svc_envdate` AS `svc_envdate`,`s`.`svc_containertype` AS `svc_containertype`,`s`.`svc_metrocluster` AS `svc_metrocluster`,`s`.`responsibles` AS `responsibles`,`s`.`mailto` AS `mailto`,`s`.`svc_vcpus` AS `svc_vcpus`,`s`.`svc_vmem` AS `svc_vmem`,`m`.`mon_svcname` AS `mon_svcname`,`m`.`mon_svctype` AS `mon_svctype`,`m`.`mon_drptype` AS `mon_drptype`,`m`.`mon_nodname` AS `mon_nodname`,`m`.`mon_nodtype` AS `mon_nodtype`,`m`.`mon_nodmode` AS `mon_nodmode`,`m`.`mon_ipstatus` AS `mon_ipstatus`,`m`.`mon_fsstatus` AS `mon_fsstatus`,`m`.`mon_prinodes` AS `mon_prinodes`,`m`.`mon_hostid` AS `mon_hostid`,`m`.`ID` AS `ID`,`m`.`mon_frozen` AS `mon_frozen`,`m`.`mon_frozentxt` AS `mon_frozentxt`,`m`.`mon_changed` AS `mon_changed`,`m`.`mon_updated` AS `mon_updated`,`m`.`mon_diskstatus` AS `mon_diskstatus`,`m`.`mon_containerstatus` AS `mon_containerstatus`,`m`.`mon_overallstatus` AS `mon_overallstatus`,`n`.`nodename` AS `nodename`,`n`.`updated` AS `node_updated`,`n`.`loc_country` AS `loc_country`,`n`.`loc_city` AS `loc_city`,`n`.`loc_addr` AS `loc_addr`,`n`.`loc_building` AS `loc_building`,`n`.`loc_floor` AS `loc_floor`,`n`.`loc_room` AS `loc_room`,`n`.`loc_rack` AS `loc_rack`,`n`.`cpu_freq` AS `cpu_freq`,`n`.`cpu_cores` AS `cpu_cores`,`n`.`cpu_dies` AS `cpu_dies`,`n`.`cpu_vendor` AS `cpu_vendor`,`n`.`cpu_model` AS `cpu_model`,`n`.`mem_banks` AS `mem_banks`,`n`.`mem_slots` AS `mem_slots`,`n`.`mem_bytes` AS `mem_bytes`,`n`.`os_name` AS `os_name`,`n`.`os_release` AS `os_release`,`n`.`os_update` AS `os_update`,`n`.`os_segment` AS `os_segment`,`n`.`os_arch` AS `os_arch`,`n`.`os_vendor` AS `os_vendor`,`n`.`os_kernel` AS `os_kernel`,`n`.`loc_zip` AS `loc_zip`,`n`.`team_responsible` AS `team_responsible`,`n`.`serial` AS `serial`,`n`.`model` AS `model`,`n`.`type` AS `type`,`n`.`warranty_end` AS `warranty_end`,`n`.`status` AS `status`,`n`.`role` AS `role`,`n`.`environnement` AS `environnement`,`n`.`power_supply_nb` AS `power_supply_nb`,`n`.`power_cabinet1` AS `power_cabinet1`,`n`.`power_cabinet2` AS `power_cabinet2`,`n`.`power_protect` AS `power_protect`,`n`.`power_protect_breaker` AS `power_protect_breaker`,`n`.`power_breaker1` AS `power_breaker1`,`n`.`power_breaker2` AS `power_breaker2`,`m`.`mon_syncstatus` AS `mon_syncstatus`,`m`.`mon_hbstatus` AS `mon_hbstatus`,`m`.`mon_availstatus` AS `mon_availstatus`,`m`.`mon_appstatus` AS `mon_appstatus` from ((`svcmon` `m` join `v_services` `s` on((`s`.`svc_name` = `m`.`mon_svcname`))) left join `nodes` `n` on((convert(`m`.`mon_nodname` using utf8) = `n`.`nodename`)));

# 2011-04-06

drop view v_flex_status;

create view v_flex_status as (select p.id, p.mon_svcname as svc_name, p.svc_flex_min_nodes, p.svc_flex_max_nodes, p.svc_flex_cpu_low_threshold, p.svc_flex_cpu_high_threshold, count(1) as n, (select count(1) from svcmon c where c.mon_svcname=p.mon_svcname and c.mon_availstatus="up") as up, (select 100-c.idle from stats_cpu c, svcmon m where c.nodename=m.mon_nodname and m.mon_svcname=p.mon_svcname and date>adddate(now(), interval - 15 minute) and c.CPU="all" and m.mon_overallstatus="up" group by p.mon_svcname) as cpu from v_svcmon p where svc_cluster_type like "%flex" group by p.mon_svcname);

# 2011-04-11

CREATE TABLE `comp_ruleset_team_responsible` (
  `id` integer  NOT NULL AUTO_INCREMENT,
  `ruleset_id` integer NOT NULL,
  `group_id` integer NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx1` (`ruleset_id`)
);

drop view v_comp_rulesets;

create view v_comp_rulesets as (select r.id as ruleset_id,r.ruleset_name,r.ruleset_type,group_concat(distinct g.role separator ', ') as teams_responsible,rv.id,rv.var_name,rv.var_value,rv.var_author,rv.var_updated,rf.fset_id,fs.fset_name from comp_rulesets r left join comp_rulesets_variables rv on rv.ruleset_id = r.id left join comp_rulesets_filtersets rf on r.id=rf.ruleset_id left join gen_filtersets fs on fs.id=rf.fset_id left join comp_ruleset_team_responsible rt on r.id=rt.ruleset_id left join auth_group g on rt.group_id=g.id group by r.id, rv.id);

# 2011-04-13

create view v_outdated_services as (select mon_svcname as svcname, sum(if(mon_updated >= DATE_SUB(NOW(), INTERVAL 15 MINUTE), 1, 0)) as uptodate from svcmon group by mon_svcname);

# 2011-04-14

CREATE TABLE `services_log` (
  `id` integer  NOT NULL AUTO_INCREMENT,
  `svc_name` varchar(60) NOT NULL,
  `svc_availstatus` varchar(10) NOT NULL,
  `svc_begin` datetime NOT NULL,
  `svc_end` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx1` (`svc_name`)
);

# 2011-04-15

alter table comp_rulesets_variables add column var_class varchar(60) not null default "raw";

drop view v_comp_rulesets;

create view v_comp_rulesets as (select r.id as ruleset_id,r.ruleset_name,r.ruleset_type,group_concat(distinct g.role separator ', ') as teams_responsible,rv.id,rv.var_name,rv.var_class,rv.var_value,rv.var_author,rv.var_updated,rf.fset_id,fs.fset_name from comp_rulesets r left join comp_rulesets_variables rv on rv.ruleset_id = r.id left join comp_rulesets_filtersets rf on r.id=rf.ruleset_id left join gen_filtersets fs on fs.id=rf.fset_id left join comp_ruleset_team_responsible rt on r.id=rt.ruleset_id left join auth_group g on rt.group_id=g.id group by r.id, rv.id);

# 2011-04-21

CREATE TABLE auth_node (
  `id` integer  NOT NULL AUTO_INCREMENT,
  `nodename` varchar(60) NOT NULL,
  `uuid` varchar(36) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx1` (`nodename`)
)

# 2011-04-22

CREATE TABLE `comp_moduleset_team_responsible` (
  `id` integer  NOT NULL AUTO_INCREMENT,
  `modset_id` integer NOT NULL,
  `group_id` integer NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx1` (`modset_id`)
);

CREATE TABLE `gen_filterset_team_responsible` (
  `id` integer  NOT NULL AUTO_INCREMENT,
  `fset_id` integer NOT NULL,
  `group_id` integer NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx1` (`fset_id`)
);

create view v_comp_moduleset_teams_responsible as (select m.id as modset_id, group_concat(g.role separator ', ') as teams_responsible from comp_moduleset m left join comp_moduleset_team_responsible j on m.id=j.modset_id left join auth_group g on j.group_id=g.id group by m.id);

create view v_gen_filterset_teams_responsible as (select m.id as fset_id, group_concat(g.role separator ', ') as teams_responsible from gen_filtersets m left join gen_filterset_team_responsible j on m.id=j.fset_id left join auth_group g on j.group_id=g.id group by m.id);

# 2011-04-26

CREATE TABLE `gen_filterset_check_threshold` (
  `id` integer  NOT NULL AUTO_INCREMENT,
  `fset_id` integer NOT NULL,
  `chk_type` varchar(10) NOT NULL,
  `chk_low` int(11) NOT NULL,
  `chk_high` int(11) NOT NULL,
  `chk_instance` varchar(60) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx1` (`fset_id`)
);

alter table checks_live add column chk_low integer;
alter table checks_live add column chk_high integer;
alter table checks_live add column chk_threshold_provider varchar(60);

drop view v_checks;

# 2011-05-07

CREATE TABLE `prov_templates` (
  `id` integer  NOT NULL AUTO_INCREMENT,
  `tpl_name` varchar(100) NOT NULL,
  `tpl_command` text NOT NULL,
  `tpl_comment` text NOT NULL,
  `tpl_author` varchar(100) NOT NULL,
  `tpl_created` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx1` (`tpl_name`)
);

CREATE TABLE `prov_template_team_responsible` (
  `id` integer  NOT NULL AUTO_INCREMENT,
  `tpl_id` integer NOT NULL,
  `group_id` integer NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx1` (`tpl_id`),
  KEY `idx2` (`group_id`)
);

#
# 2011-06-02
#
# as root
# set global slow_query_log=1;

alter table SVCactions modify column status ENUM('err','ok','warn') NOT NULL;
alter table SVCactions modify column ack tinyint default NULL;

drop view v_services;

CREATE VIEW `v_services` AS select s.svc_status, s.svc_availstatus, s.svc_cluster_type, s.svc_flex_min_nodes, s.svc_flex_max_nodes, s.svc_flex_cpu_low_threshold, s.svc_flex_cpu_high_threshold, `s`.`svc_vmname` AS `svc_vmname`,`s`.`svc_guestos` AS `svc_guestos`,`s`.`svc_version` AS `svc_version`,`s`.`svc_hostid` AS `svc_hostid`,`s`.`svc_name` AS `svc_name`,`s`.`svc_nodes` AS `svc_nodes`,`s`.`svc_drpnode` AS `svc_drpnode`,`s`.`svc_ipname` AS `svc_ipname`,`s`.`svc_ipdev` AS `svc_ipdev`,`s`.`svc_drpipname` AS `svc_drpipname`,`s`.`svc_drpipdev` AS `svc_drpipdev`,`s`.`svc_drptype` AS `svc_drptype`,`s`.`svc_fs` AS `svc_fs`,`s`.`svc_dev` AS `svc_dev`,`s`.`svc_autostart` AS `svc_autostart`,`s`.`svc_mntopt` AS `svc_mntopt`,`s`.`svc_scsi` AS `svc_scsi`,`s`.`svc_type` AS `svc_type`,`s`.`svc_drpnodes` AS `svc_drpnodes`,`s`.`svc_comment` AS `svc_comment`,`s`.`svc_app` AS `svc_app`,`s`.`svc_drnoaction` AS `svc_drnoaction`,svc_created,`s`.`updated` AS `updated`,`s`.`cksum` AS `cksum`,`s`.`svc_envdate` AS `svc_envdate`,`s`.`svc_containertype` AS `svc_containertype`,`s`.`svc_metrocluster` AS `svc_metrocluster`,`s`.`id` AS `id`,`s`.`svc_hasec` AS `svc_hasec`,`s`.`svc_hapri` AS `svc_hapri`,`s`.`svc_hastonith` AS `svc_hastonith`,`s`.`svc_hastartup` AS `svc_hastartup`,`s`.`svc_wave` AS `svc_wave`,`s`.`svc_vcpus` AS `svc_vcpus`,`s`.`svc_vmem` AS `svc_vmem`,`a`.`app` AS `app`,`a`.`responsibles` AS `responsibles`,`a`.`mailto` AS `mailto` from (`services` `s` left join `v_apps` `a` on((`a`.`app` = `s`.`svc_app`))) ;

DROP VIEW v_svcactions;

CREATE VIEW `v_svcactions` AS select `ac`.`version` AS `version`,`ac`.`svcname` AS `svcname`,`ac`.`action` AS `action`,`ac`.`status` AS `status`,`ac`.`time` AS `time`,`ac`.`begin` AS `begin`,`ac`.`end` AS `end`,`ac`.`hostname` AS `hostname`,`ac`.`hostid` AS `hostid`,`ac`.`status_log` AS `status_log`,`ac`.`pid` AS `pid`,`ac`.`ID` AS `ID`,`ac`.`ack` AS `ack`,`ac`.`alert` AS `alert`,`ac`.`action_group` AS `action_group`,`ac`.`acked_by` AS `acked_by`,`ac`.`acked_comment` AS `acked_comment`,`ac`.`acked_date` AS `acked_date`,`s`.`svc_app` AS `app`,(select `sa`.`responsibles` from v_apps sa where sa.app=s.svc_app limit 1) AS `responsibles`,(select `sa`.`mailto` from v_apps sa where sa.app=s.svc_app limit 1) AS `mailto`,`n`.`nodename` AS `nodename`,`n`.`loc_country` AS `loc_country`,`n`.`loc_city` AS `loc_city`,`n`.`loc_addr` AS `loc_addr`,`n`.`loc_building` AS `loc_building`,`n`.`loc_floor` AS `loc_floor`,`n`.`loc_room` AS `loc_room`,`n`.`loc_rack` AS `loc_rack`,`n`.`cpu_freq` AS `cpu_freq`,`n`.`cpu_cores` AS `cpu_cores`,`n`.`cpu_dies` AS `cpu_dies`,`n`.`cpu_vendor` AS `cpu_vendor`,`n`.`cpu_model` AS `cpu_model`,`n`.`mem_banks` AS `mem_banks`,`n`.`mem_slots` AS `mem_slots`,`n`.`mem_bytes` AS `mem_bytes`,`n`.`os_name` AS `os_name`,`n`.`os_release` AS `os_release`,`n`.`os_update` AS `os_update`,`n`.`os_segment` AS `os_segment`,`n`.`os_arch` AS `os_arch`,`n`.`os_vendor` AS `os_vendor`,`n`.`os_kernel` AS `os_kernel`,`n`.`loc_zip` AS `loc_zip`,`n`.`team_responsible` AS `team_responsible`,`n`.`serial` AS `serial`,`n`.`model` AS `model`,`n`.`type` AS `type`,`n`.`warranty_end` AS `warranty_end`,`n`.`status` AS `asset_status`,`n`.`role` AS `role`,`n`.`environnement` AS `environnement`,`n`.`power_supply_nb` AS `power_supply_nb`,`n`.`power_cabinet1` AS `power_cabinet1`,`n`.`power_cabinet2` AS `power_cabinet2`,`n`.`power_protect` AS `power_protect`,`n`.`power_protect_breaker` AS `power_protect_breaker`,`n`.`power_breaker1` AS `power_breaker1`,`n`.`power_breaker2` AS `power_breaker2` from ((`SVCactions` `ac` left join `services` `s` on((`s`.`svc_name` = `ac`.`svcname`))) join `nodes` `n` on((convert(`ac`.`hostname` using utf8) = `n`.`nodename`)));

alter table apps add index i_app (app);

#alter table SVCactions engine=innodb;

alter table SVCactions modify hostname varchar(50) CHARACTER SET utf8 NOT NULL DEFAULT '';

DROP VIEW v_svcactions;

CREATE VIEW `v_svcactions` AS select `ac`.`version` AS `version`,`ac`.`svcname` AS `svcname`,`ac`.`action` AS `action`,`ac`.`status` AS `status`,`ac`.`time` AS `time`,`ac`.`begin` AS `begin`,`ac`.`end` AS `end`,`ac`.`hostname` AS `hostname`,`ac`.`hostid` AS `hostid`,`ac`.`status_log` AS `status_log`,`ac`.`pid` AS `pid`,`ac`.`ID` AS `ID`,`ac`.`ack` AS `ack`,`ac`.`alert` AS `alert`,`ac`.`action_group` AS `action_group`,`ac`.`acked_by` AS `acked_by`,`ac`.`acked_comment` AS `acked_comment`,`ac`.`acked_date` AS `acked_date`,`s`.`svc_app` AS `app`,(select `sa`.`responsibles` from v_apps sa where sa.app=s.svc_app limit 1) AS `responsibles`,(select `sa`.`mailto` from v_apps sa where sa.app=s.svc_app limit 1) AS `mailto`,`n`.`nodename` AS `nodename`,`n`.`loc_country` AS `loc_country`,`n`.`loc_city` AS `loc_city`,`n`.`loc_addr` AS `loc_addr`,`n`.`loc_building` AS `loc_building`,`n`.`loc_floor` AS `loc_floor`,`n`.`loc_room` AS `loc_room`,`n`.`loc_rack` AS `loc_rack`,`n`.`cpu_freq` AS `cpu_freq`,`n`.`cpu_cores` AS `cpu_cores`,`n`.`cpu_dies` AS `cpu_dies`,`n`.`cpu_vendor` AS `cpu_vendor`,`n`.`cpu_model` AS `cpu_model`,`n`.`mem_banks` AS `mem_banks`,`n`.`mem_slots` AS `mem_slots`,`n`.`mem_bytes` AS `mem_bytes`,`n`.`os_name` AS `os_name`,`n`.`os_release` AS `os_release`,`n`.`os_update` AS `os_update`,`n`.`os_segment` AS `os_segment`,`n`.`os_arch` AS `os_arch`,`n`.`os_vendor` AS `os_vendor`,`n`.`os_kernel` AS `os_kernel`,`n`.`loc_zip` AS `loc_zip`,`n`.`team_responsible` AS `team_responsible`,`n`.`serial` AS `serial`,`n`.`model` AS `model`,`n`.`type` AS `type`,`n`.`warranty_end` AS `warranty_end`,`n`.`status` AS `asset_status`,`n`.`role` AS `role`,`n`.`environnement` AS `environnement`,`n`.`power_supply_nb` AS `power_supply_nb`,`n`.`power_cabinet1` AS `power_cabinet1`,`n`.`power_cabinet2` AS `power_cabinet2`,`n`.`power_protect` AS `power_protect`,`n`.`power_protect_breaker` AS `power_protect_breaker`,`n`.`power_breaker1` AS `power_breaker1`,`n`.`power_breaker2` AS `power_breaker2` from `SVCactions` `ac` left join `services` `s` on `s`.`svc_name` = `ac`.`svcname` left join `nodes` `n` on `ac`.`hostname` = `n`.`nodename`;

CREATE TABLE `b_apps` (
  `id` int(11) NOT NULL DEFAULT '0',
  `app` varchar(20) CHARACTER SET latin1 NOT NULL,
  `roles` varchar(342) DEFAULT NULL,
  `responsibles` varchar(342) DEFAULT NULL,
  `mailto` varchar(342) DEFAULT NULL,
  KEY `i_app` (`app`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

DROP VIEW v_svcactions;

CREATE VIEW `v_svcactions` AS select `ac`.`version` AS `version`,`ac`.`svcname` AS `svcname`,`ac`.`action` AS `action`,`ac`.`status` AS `status`,`ac`.`time` AS `time`,`ac`.`begin` AS `begin`,`ac`.`end` AS `end`,`ac`.`hostname` AS `hostname`,`ac`.`hostid` AS `hostid`,`ac`.`status_log` AS `status_log`,`ac`.`pid` AS `pid`,`ac`.`ID` AS `ID`,`ac`.`ack` AS `ack`,`ac`.`alert` AS `alert`,`ac`.`action_group` AS `action_group`,`ac`.`acked_by` AS `acked_by`,`ac`.`acked_comment` AS `acked_comment`,`ac`.`acked_date` AS `acked_date`,`s`.`svc_app` AS `app`, a.mailto, a.responsibles,`n`.`nodename` AS `nodename`,`n`.`loc_country` AS `loc_country`,`n`.`loc_city` AS `loc_city`,`n`.`loc_addr` AS `loc_addr`,`n`.`loc_building` AS `loc_building`,`n`.`loc_floor` AS `loc_floor`,`n`.`loc_room` AS `loc_room`,`n`.`loc_rack` AS `loc_rack`,`n`.`cpu_freq` AS `cpu_freq`,`n`.`cpu_cores` AS `cpu_cores`,`n`.`cpu_dies` AS `cpu_dies`,`n`.`cpu_vendor` AS `cpu_vendor`,`n`.`cpu_model` AS `cpu_model`,`n`.`mem_banks` AS `mem_banks`,`n`.`mem_slots` AS `mem_slots`,`n`.`mem_bytes` AS `mem_bytes`,`n`.`os_name` AS `os_name`,`n`.`os_release` AS `os_release`,`n`.`os_update` AS `os_update`,`n`.`os_segment` AS `os_segment`,`n`.`os_arch` AS `os_arch`,`n`.`os_vendor` AS `os_vendor`,`n`.`os_kernel` AS `os_kernel`,`n`.`loc_zip` AS `loc_zip`,`n`.`team_responsible` AS `team_responsible`,`n`.`serial` AS `serial`,`n`.`model` AS `model`,`n`.`type` AS `type`,`n`.`warranty_end` AS `warranty_end`,`n`.`status` AS `asset_status`,`n`.`role` AS `role`,`n`.`environnement` AS `environnement`,`n`.`power_supply_nb` AS `power_supply_nb`,`n`.`power_cabinet1` AS `power_cabinet1`,`n`.`power_cabinet2` AS `power_cabinet2`,`n`.`power_protect` AS `power_protect`,`n`.`power_protect_breaker` AS `power_protect_breaker`,`n`.`power_breaker1` AS `power_breaker1`,`n`.`power_breaker2` AS `power_breaker2` from `SVCactions` `ac` left join `services` `s` on `s`.`svc_name` = `ac`.`svcname` left join `nodes` `n` on `ac`.`hostname` = `n`.`nodename` left join b_apps a on a.app=s.svc_app;

alter table SVCactions drop index begin_2;
alter table SVCactions drop index action_2;
alter table SVCactions drop index svcname_2;
alter table SVCactions drop index hostid_2;
alter table SVCactions drop index err_index;

drop view v_svcmon;

CREATE VIEW `v_svcmon` AS select (select count(`a`.`ID`) AS `count(a.id)` from `SVCactions` `a` where ((convert(`m`.`mon_nodname` using utf8) = `a`.`hostname`) and (`a`.`svcname` = `s`.`svc_name`) and (`a`.`status` = 'err') and ((`a`.`ack` <> 1) or isnull(`a`.`ack`)))) AS `err`,`s`.`svc_cluster_type` AS `svc_cluster_type`,`s`.`svc_status` AS `svc_status`,`s`.`svc_availstatus` AS `svc_availstatus`,`s`.`svc_flex_min_nodes` AS `svc_flex_min_nodes`,`s`.`svc_flex_max_nodes` AS `svc_flex_max_nodes`,`s`.`svc_flex_cpu_low_threshold` AS `svc_flex_cpu_low_threshold`,`s`.`svc_flex_cpu_high_threshold` AS `svc_flex_cpu_high_threshold`,`s`.`svc_vmname` AS `svc_vmname`,`s`.`svc_guestos` AS `svc_guestos`,`s`.`svc_version` AS `svc_version`,`s`.`svc_name` AS `svc_name`,`s`.`svc_nodes` AS `svc_nodes`,`s`.`svc_drpnode` AS `svc_drpnode`,`s`.`svc_drpnodes` AS `svc_drpnodes`,`s`.`svc_drptype` AS `svc_drptype`,`s`.`svc_autostart` AS `svc_autostart`,`s`.`svc_type` AS `svc_type`,`s`.`svc_comment` AS `svc_comment`,`s`.`svc_app` AS `svc_app`,`s`.`svc_drnoaction` AS `svc_drnoaction`,`s`.`svc_created` AS `svc_created`,`s`.`updated` AS `svc_updated`,`s`.`svc_envdate` AS `svc_envdate`,`s`.`svc_containertype` AS `svc_containertype`,`s`.`svc_metrocluster` AS `svc_metrocluster`,`s`.`svc_vcpus` AS `svc_vcpus`,`s`.`svc_vmem` AS `svc_vmem`,`m`.`mon_svcname` AS `mon_svcname`,`m`.`mon_svctype` AS `mon_svctype`,`m`.`mon_drptype` AS `mon_drptype`,`m`.`mon_nodname` AS `mon_nodname`,`m`.`mon_nodtype` AS `mon_nodtype`,`m`.`mon_nodmode` AS `mon_nodmode`,`m`.`mon_ipstatus` AS `mon_ipstatus`,`m`.`mon_fsstatus` AS `mon_fsstatus`,`m`.`mon_prinodes` AS `mon_prinodes`,`m`.`mon_hostid` AS `mon_hostid`,`m`.`ID` AS `ID`,`m`.`mon_frozen` AS `mon_frozen`,`m`.`mon_frozentxt` AS `mon_frozentxt`,`m`.`mon_changed` AS `mon_changed`,`m`.`mon_updated` AS `mon_updated`,`m`.`mon_diskstatus` AS `mon_diskstatus`,`m`.`mon_containerstatus` AS `mon_containerstatus`,`m`.`mon_overallstatus` AS `mon_overallstatus`,`n`.`nodename` AS `nodename`,`n`.`updated` AS `node_updated`,`n`.`loc_country` AS `loc_country`,`n`.`loc_city` AS `loc_city`,`n`.`loc_addr` AS `loc_addr`,`n`.`loc_building` AS `loc_building`,`n`.`loc_floor` AS `loc_floor`,`n`.`loc_room` AS `loc_room`,`n`.`loc_rack` AS `loc_rack`,`n`.`cpu_freq` AS `cpu_freq`,`n`.`cpu_cores` AS `cpu_cores`,`n`.`cpu_dies` AS `cpu_dies`,`n`.`cpu_vendor` AS `cpu_vendor`,`n`.`cpu_model` AS `cpu_model`,`n`.`mem_banks` AS `mem_banks`,`n`.`mem_slots` AS `mem_slots`,`n`.`mem_bytes` AS `mem_bytes`,`n`.`os_name` AS `os_name`,`n`.`os_release` AS `os_release`,`n`.`os_update` AS `os_update`,`n`.`os_segment` AS `os_segment`,`n`.`os_arch` AS `os_arch`,`n`.`os_vendor` AS `os_vendor`,`n`.`os_kernel` AS `os_kernel`,`n`.`loc_zip` AS `loc_zip`,`n`.`team_responsible` AS `team_responsible`,`n`.`serial` AS `serial`,`n`.`model` AS `model`,`n`.`type` AS `type`,`n`.`warranty_end` AS `warranty_end`,`n`.`status` AS `status`,`n`.`role` AS `role`,`n`.`environnement` AS `environnement`,`n`.`power_supply_nb` AS `power_supply_nb`,`n`.`power_cabinet1` AS `power_cabinet1`,`n`.`power_cabinet2` AS `power_cabinet2`,`n`.`power_protect` AS `power_protect`,`n`.`power_protect_breaker` AS `power_protect_breaker`,`n`.`power_breaker1` AS `power_breaker1`,`n`.`power_breaker2` AS `power_breaker2`,`m`.`mon_syncstatus` AS `mon_syncstatus`,`m`.`mon_hbstatus` AS `mon_hbstatus`,`m`.`mon_availstatus` AS `mon_availstatus`,`m`.`mon_appstatus` AS `mon_appstatus`, ap.responsibles as responsibles, ap.mailto as mailto from `svcmon` `m` left join `services` `s` on `s`.`svc_name` = `m`.`mon_svcname` left join `nodes` `n` on `m`.`mon_nodname` = `n`.`nodename` left join b_apps ap on ap.app=s.svc_app;

create table b_action_errors (`id` int(11) NOT NULL AUTO_INCREMENT, `svcname` varchar(60) NOT NULL, nodename varchar(60) not null, `err` int(11) NOT NULL, PRIMARY KEY (`id`), UNIQUE KEY `i_svcname` (`svcname`, `nodename`));

drop view v_svcmon;

CREATE VIEW `v_svcmon` AS select e.err AS `err`,`s`.`svc_cluster_type` AS `svc_cluster_type`,`s`.`svc_status` AS `svc_status`,`s`.`svc_availstatus` AS `svc_availstatus`,`s`.`svc_flex_min_nodes` AS `svc_flex_min_nodes`,`s`.`svc_flex_max_nodes` AS `svc_flex_max_nodes`,`s`.`svc_flex_cpu_low_threshold` AS `svc_flex_cpu_low_threshold`,`s`.`svc_flex_cpu_high_threshold` AS `svc_flex_cpu_high_threshold`,`s`.`svc_vmname` AS `svc_vmname`,`s`.`svc_guestos` AS `svc_guestos`,`s`.`svc_version` AS `svc_version`,`s`.`svc_name` AS `svc_name`,`s`.`svc_nodes` AS `svc_nodes`,`s`.`svc_drpnode` AS `svc_drpnode`,`s`.`svc_drpnodes` AS `svc_drpnodes`,`s`.`svc_drptype` AS `svc_drptype`,`s`.`svc_autostart` AS `svc_autostart`,`s`.`svc_type` AS `svc_type`,`s`.`svc_comment` AS `svc_comment`,`s`.`svc_app` AS `svc_app`,`s`.`svc_drnoaction` AS `svc_drnoaction`,`s`.`svc_created` AS `svc_created`,`s`.`updated` AS `svc_updated`,`s`.`svc_envdate` AS `svc_envdate`,`s`.`svc_containertype` AS `svc_containertype`,`s`.`svc_metrocluster` AS `svc_metrocluster`,`s`.`svc_vcpus` AS `svc_vcpus`,`s`.`svc_vmem` AS `svc_vmem`,`m`.`mon_svcname` AS `mon_svcname`,`m`.`mon_svctype` AS `mon_svctype`,`m`.`mon_drptype` AS `mon_drptype`,`m`.`mon_nodname` AS `mon_nodname`,`m`.`mon_nodtype` AS `mon_nodtype`,`m`.`mon_nodmode` AS `mon_nodmode`,`m`.`mon_ipstatus` AS `mon_ipstatus`,`m`.`mon_fsstatus` AS `mon_fsstatus`,`m`.`mon_prinodes` AS `mon_prinodes`,`m`.`mon_hostid` AS `mon_hostid`,`m`.`ID` AS `ID`,`m`.`mon_frozen` AS `mon_frozen`,`m`.`mon_frozentxt` AS `mon_frozentxt`,`m`.`mon_changed` AS `mon_changed`,`m`.`mon_updated` AS `mon_updated`,`m`.`mon_diskstatus` AS `mon_diskstatus`,`m`.`mon_containerstatus` AS `mon_containerstatus`,`m`.`mon_overallstatus` AS `mon_overallstatus`,`n`.`nodename` AS `nodename`,`n`.`updated` AS `node_updated`,`n`.`loc_country` AS `loc_country`,`n`.`loc_city` AS `loc_city`,`n`.`loc_addr` AS `loc_addr`,`n`.`loc_building` AS `loc_building`,`n`.`loc_floor` AS `loc_floor`,`n`.`loc_room` AS `loc_room`,`n`.`loc_rack` AS `loc_rack`,`n`.`cpu_freq` AS `cpu_freq`,`n`.`cpu_cores` AS `cpu_cores`,`n`.`cpu_dies` AS `cpu_dies`,`n`.`cpu_vendor` AS `cpu_vendor`,`n`.`cpu_model` AS `cpu_model`,`n`.`mem_banks` AS `mem_banks`,`n`.`mem_slots` AS `mem_slots`,`n`.`mem_bytes` AS `mem_bytes`,`n`.`os_name` AS `os_name`,`n`.`os_release` AS `os_release`,`n`.`os_update` AS `os_update`,`n`.`os_segment` AS `os_segment`,`n`.`os_arch` AS `os_arch`,`n`.`os_vendor` AS `os_vendor`,`n`.`os_kernel` AS `os_kernel`,`n`.`loc_zip` AS `loc_zip`,`n`.`team_responsible` AS `team_responsible`,`n`.`serial` AS `serial`,`n`.`model` AS `model`,`n`.`type` AS `type`,`n`.`warranty_end` AS `warranty_end`,`n`.`status` AS `status`,`n`.`role` AS `role`,`n`.`environnement` AS `environnement`,`n`.`power_supply_nb` AS `power_supply_nb`,`n`.`power_cabinet1` AS `power_cabinet1`,`n`.`power_cabinet2` AS `power_cabinet2`,`n`.`power_protect` AS `power_protect`,`n`.`power_protect_breaker` AS `power_protect_breaker`,`n`.`power_breaker1` AS `power_breaker1`,`n`.`power_breaker2` AS `power_breaker2`,`m`.`mon_syncstatus` AS `mon_syncstatus`,`m`.`mon_hbstatus` AS `mon_hbstatus`,`m`.`mon_availstatus` AS `mon_availstatus`,`m`.`mon_appstatus` AS `mon_appstatus`,`ap`.`responsibles` AS `responsibles`,`ap`.`mailto` AS `mailto` from (((`svcmon` `m` left join `services` `s` on((`s`.`svc_name` = `m`.`mon_svcname`))) left join `nodes` `n` on((convert(`m`.`mon_nodname` using utf8) = `n`.`nodename`))) left join `b_apps` `ap` on((`ap`.`app` = `s`.`svc_app`))) left join b_action_errors e on e.svcname=s.svc_name and e.nodename=m.mon_nodname;

truncate b_action_errors; insert into b_action_errors select NULL, m.mon_svcname, m.mon_nodname, count(a.id) from svcmon m left join SVCactions a on m.mon_svcname=a.svcname and m.mon_nodname=a.hostname where a.status='err' and (a.ack=0 or isnull(a.ack)) group by m.mon_svcname, m.mon_nodname;

#
# 2011-06-06
#
create tables services2 like services;

create table services2 like services;

alter table services2 drop index svc_hostid_3;

alter table services2 add unique index i_svc_name (svc_name);

insert into services2 select * from services group by svc_name;

alter table services rename services_old;

alter table services2 rename services;

#
# 2011-06-23
#
CREATE TABLE `im_types` (
  `id` integer  NOT NULL AUTO_INCREMENT,
  `im_type` varchar(64)  NOT NULL,
  PRIMARY KEY (`id`)
);

insert into im_types set im_type="gtalk";

alter table auth_user add column im_notifications varchar(1) default 'T';

alter table auth_user add column im_type integer;

alter table auth_user add column im_username varchar(100);

drop table user_im;

alter table SVCactions add column cron tinyint(1) default 0;

DROP VIEW v_svcactions;

CREATE VIEW `v_svcactions` AS select ac.cron as cron, `ac`.`version` AS `version`,`ac`.`svcname` AS `svcname`,`ac`.`action` AS `action`,`ac`.`status` AS `status`,`ac`.`time` AS `time`,`ac`.`begin` AS `begin`,`ac`.`end` AS `end`,`ac`.`hostname` AS `hostname`,`ac`.`hostid` AS `hostid`,`ac`.`status_log` AS `status_log`,`ac`.`pid` AS `pid`,`ac`.`ID` AS `ID`,`ac`.`ack` AS `ack`,`ac`.`alert` AS `alert`,`ac`.`action_group` AS `action_group`,`ac`.`acked_by` AS `acked_by`,`ac`.`acked_comment` AS `acked_comment`,`ac`.`acked_date` AS `acked_date`,`s`.`svc_app` AS `app`, a.mailto, a.responsibles,`n`.`nodename` AS `nodename`,`n`.`loc_country` AS `loc_country`,`n`.`loc_city` AS `loc_city`,`n`.`loc_addr` AS `loc_addr`,`n`.`loc_building` AS `loc_building`,`n`.`loc_floor` AS `loc_floor`,`n`.`loc_room` AS `loc_room`,`n`.`loc_rack` AS `loc_rack`,`n`.`cpu_freq` AS `cpu_freq`,`n`.`cpu_cores` AS `cpu_cores`,`n`.`cpu_dies` AS `cpu_dies`,`n`.`cpu_vendor` AS `cpu_vendor`,`n`.`cpu_model` AS `cpu_model`,`n`.`mem_banks` AS `mem_banks`,`n`.`mem_slots` AS `mem_slots`,`n`.`mem_bytes` AS `mem_bytes`,`n`.`os_name` AS `os_name`,`n`.`os_release` AS `os_release`,`n`.`os_update` AS `os_update`,`n`.`os_segment` AS `os_segment`,`n`.`os_arch` AS `os_arch`,`n`.`os_vendor` AS `os_vendor`,`n`.`os_kernel` AS `os_kernel`,`n`.`loc_zip` AS `loc_zip`,`n`.`team_responsible` AS `team_responsible`,`n`.`serial` AS `serial`,`n`.`model` AS `model`,`n`.`type` AS `type`,`n`.`warranty_end` AS `warranty_end`,`n`.`status` AS `asset_status`,`n`.`role` AS `role`,`n`.`environnement` AS `environnement`,`n`.`power_supply_nb` AS `power_supply_nb`,`n`.`power_cabinet1` AS `power_cabinet1`,`n`.`power_cabinet2` AS `power_cabinet2`,`n`.`power_protect` AS `power_protect`,`n`.`power_protect_breaker` AS `power_protect_breaker`,`n`.`power_breaker1` AS `power_breaker1`,`n`.`power_breaker2` AS `power_breaker2` from `SVCactions` `ac` left join `services` `s` on `s`.`svc_name` = `ac`.`svcname` left join `nodes` `n` on `ac`.`hostname` = `n`.`nodename` left join b_apps a on a.app=s.svc_app;

alter table services add column svc_ha tinyint(1) default 0;

drop view v_svcmon;

CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `v_svcmon` AS select e.err AS `err`,s.svc_ha as svc_ha,`s`.`svc_cluster_type` AS `svc_cluster_type`,`s`.`svc_status` AS `svc_status`,`s`.`svc_availstatus` AS `svc_availstatus`,`s`.`svc_flex_min_nodes` AS `svc_flex_min_nodes`,`s`.`svc_flex_max_nodes` AS `svc_flex_max_nodes`,`s`.`svc_flex_cpu_low_threshold` AS `svc_flex_cpu_low_threshold`,`s`.`svc_flex_cpu_high_threshold` AS `svc_flex_cpu_high_threshold`,`s`.`svc_vmname` AS `svc_vmname`,`s`.`svc_guestos` AS `svc_guestos`,`s`.`svc_version` AS `svc_version`,`s`.`svc_name` AS `svc_name`,`s`.`svc_nodes` AS `svc_nodes`,`s`.`svc_drpnode` AS `svc_drpnode`,`s`.`svc_drpnodes` AS `svc_drpnodes`,`s`.`svc_drptype` AS `svc_drptype`,`s`.`svc_autostart` AS `svc_autostart`,`s`.`svc_type` AS `svc_type`,`s`.`svc_comment` AS `svc_comment`,`s`.`svc_app` AS `svc_app`,`s`.`svc_drnoaction` AS `svc_drnoaction`,`s`.`svc_created` AS `svc_created`,`s`.`updated` AS `svc_updated`,`s`.`svc_envdate` AS `svc_envdate`,`s`.`svc_containertype` AS `svc_containertype`,`s`.`svc_metrocluster` AS `svc_metrocluster`,`s`.`svc_vcpus` AS `svc_vcpus`,`s`.`svc_vmem` AS `svc_vmem`,`m`.`mon_svcname` AS `mon_svcname`,`m`.`mon_svctype` AS `mon_svctype`,`m`.`mon_drptype` AS `mon_drptype`,`m`.`mon_nodname` AS `mon_nodname`,`m`.`mon_nodtype` AS `mon_nodtype`,`m`.`mon_nodmode` AS `mon_nodmode`,`m`.`mon_ipstatus` AS `mon_ipstatus`,`m`.`mon_fsstatus` AS `mon_fsstatus`,`m`.`mon_prinodes` AS `mon_prinodes`,`m`.`mon_hostid` AS `mon_hostid`,`m`.`ID` AS `ID`,`m`.`mon_frozen` AS `mon_frozen`,`m`.`mon_frozentxt` AS `mon_frozentxt`,`m`.`mon_changed` AS `mon_changed`,`m`.`mon_updated` AS `mon_updated`,`m`.`mon_diskstatus` AS `mon_diskstatus`,`m`.`mon_containerstatus` AS `mon_containerstatus`,`m`.`mon_overallstatus` AS `mon_overallstatus`,`n`.`nodename` AS `nodename`,`n`.`updated` AS `node_updated`,`n`.`loc_country` AS `loc_country`,`n`.`loc_city` AS `loc_city`,`n`.`loc_addr` AS `loc_addr`,`n`.`loc_building` AS `loc_building`,`n`.`loc_floor` AS `loc_floor`,`n`.`loc_room` AS `loc_room`,`n`.`loc_rack` AS `loc_rack`,`n`.`cpu_freq` AS `cpu_freq`,`n`.`cpu_cores` AS `cpu_cores`,`n`.`cpu_dies` AS `cpu_dies`,`n`.`cpu_vendor` AS `cpu_vendor`,`n`.`cpu_model` AS `cpu_model`,`n`.`mem_banks` AS `mem_banks`,`n`.`mem_slots` AS `mem_slots`,`n`.`mem_bytes` AS `mem_bytes`,`n`.`os_name` AS `os_name`,`n`.`os_release` AS `os_release`,`n`.`os_update` AS `os_update`,`n`.`os_segment` AS `os_segment`,`n`.`os_arch` AS `os_arch`,`n`.`os_vendor` AS `os_vendor`,`n`.`os_kernel` AS `os_kernel`,`n`.`loc_zip` AS `loc_zip`,`n`.`team_responsible` AS `team_responsible`,`n`.`serial` AS `serial`,`n`.`model` AS `model`,`n`.`type` AS `type`,`n`.`warranty_end` AS `warranty_end`,`n`.`status` AS `status`,`n`.`role` AS `role`,`n`.`environnement` AS `environnement`,`n`.`power_supply_nb` AS `power_supply_nb`,`n`.`power_cabinet1` AS `power_cabinet1`,`n`.`power_cabinet2` AS `power_cabinet2`,`n`.`power_protect` AS `power_protect`,`n`.`power_protect_breaker` AS `power_protect_breaker`,`n`.`power_breaker1` AS `power_breaker1`,`n`.`power_breaker2` AS `power_breaker2`,`m`.`mon_syncstatus` AS `mon_syncstatus`,`m`.`mon_hbstatus` AS `mon_hbstatus`,`m`.`mon_availstatus` AS `mon_availstatus`,`m`.`mon_appstatus` AS `mon_appstatus`,`ap`.`responsibles` AS `responsibles`,`ap`.`mailto` AS `mailto` from (((`svcmon` `m` left join `services` `s` on((`s`.`svc_name` = `m`.`mon_svcname`))) left join `nodes` `n` on((convert(`m`.`mon_nodname` using utf8) = `n`.`nodename`))) left join `b_apps` `ap` on((`ap`.`app` = `s`.`svc_app`))) left join b_action_errors e on e.svcname=s.svc_name and e.nodename=m.mon_nodname;

DROP VIEW v_svcactions;

CREATE VIEW `v_svcactions` AS select ac.cron as cron, `ac`.`version` AS `version`,`ac`.`svcname` AS `svcname`,`ac`.`action` AS `action`,`ac`.`status` AS `status`,`ac`.`time` AS `time`,`ac`.`begin` AS `begin`,`ac`.`end` AS `end`,`ac`.`hostname` AS `hostname`,`ac`.`hostid` AS `hostid`,`ac`.`status_log` AS `status_log`,`ac`.`pid` AS `pid`,`ac`.`ID` AS `ID`,`ac`.`ack` AS `ack`,`ac`.`alert` AS `alert`,`ac`.`action_group` AS `action_group`,`ac`.`acked_by` AS `acked_by`,`ac`.`acked_comment` AS `acked_comment`,`ac`.`acked_date` AS `acked_date`,s.svc_ha as svc_ha,`s`.`svc_app` AS `app`, a.mailto, a.responsibles,`n`.`nodename` AS `nodename`,`n`.`loc_country` AS `loc_country`,`n`.`loc_city` AS `loc_city`,`n`.`loc_addr` AS `loc_addr`,`n`.`loc_building` AS `loc_building`,`n`.`loc_floor` AS `loc_floor`,`n`.`loc_room` AS `loc_room`,`n`.`loc_rack` AS `loc_rack`,`n`.`cpu_freq` AS `cpu_freq`,`n`.`cpu_cores` AS `cpu_cores`,`n`.`cpu_dies` AS `cpu_dies`,`n`.`cpu_vendor` AS `cpu_vendor`,`n`.`cpu_model` AS `cpu_model`,`n`.`mem_banks` AS `mem_banks`,`n`.`mem_slots` AS `mem_slots`,`n`.`mem_bytes` AS `mem_bytes`,`n`.`os_name` AS `os_name`,`n`.`os_release` AS `os_release`,`n`.`os_update` AS `os_update`,`n`.`os_segment` AS `os_segment`,`n`.`os_arch` AS `os_arch`,`n`.`os_vendor` AS `os_vendor`,`n`.`os_kernel` AS `os_kernel`,`n`.`loc_zip` AS `loc_zip`,`n`.`team_responsible` AS `team_responsible`,`n`.`serial` AS `serial`,`n`.`model` AS `model`,`n`.`type` AS `type`,`n`.`warranty_end` AS `warranty_end`,`n`.`status` AS `asset_status`,`n`.`role` AS `role`,`n`.`environnement` AS `environnement`,`n`.`power_supply_nb` AS `power_supply_nb`,`n`.`power_cabinet1` AS `power_cabinet1`,`n`.`power_cabinet2` AS `power_cabinet2`,`n`.`power_protect` AS `power_protect`,`n`.`power_protect_breaker` AS `power_protect_breaker`,`n`.`power_breaker1` AS `power_breaker1`,`n`.`power_breaker2` AS `power_breaker2` from `SVCactions` `ac` left join `services` `s` on `s`.`svc_name` = `ac`.`svcname` left join `nodes` `n` on `ac`.`hostname` = `n`.`nodename` left join b_apps a on a.app=s.svc_app;

drop view v_services;

CREATE VIEW `v_services` AS select s.svc_ha, s.svc_status, s.svc_availstatus, s.svc_cluster_type, s.svc_flex_min_nodes, s.svc_flex_max_nodes, s.svc_flex_cpu_low_threshold, s.svc_flex_cpu_high_threshold, `s`.`svc_vmname` AS `svc_vmname`,`s`.`svc_guestos` AS `svc_guestos`,`s`.`svc_version` AS `svc_version`,`s`.`svc_hostid` AS `svc_hostid`,`s`.`svc_name` AS `svc_name`,`s`.`svc_nodes` AS `svc_nodes`,`s`.`svc_drpnode` AS `svc_drpnode`,`s`.`svc_ipname` AS `svc_ipname`,`s`.`svc_ipdev` AS `svc_ipdev`,`s`.`svc_drpipname` AS `svc_drpipname`,`s`.`svc_drpipdev` AS `svc_drpipdev`,`s`.`svc_drptype` AS `svc_drptype`,`s`.`svc_fs` AS `svc_fs`,`s`.`svc_dev` AS `svc_dev`,`s`.`svc_autostart` AS `svc_autostart`,`s`.`svc_mntopt` AS `svc_mntopt`,`s`.`svc_scsi` AS `svc_scsi`,`s`.`svc_type` AS `svc_type`,`s`.`svc_drpnodes` AS `svc_drpnodes`,`s`.`svc_comment` AS `svc_comment`,`s`.`svc_app` AS `svc_app`,`s`.`svc_drnoaction` AS `svc_drnoaction`,svc_created,`s`.`updated` AS `updated`,`s`.`cksum` AS `cksum`,`s`.`svc_envdate` AS `svc_envdate`,`s`.`svc_containertype` AS `svc_containertype`,`s`.`svc_metrocluster` AS `svc_metrocluster`,`s`.`id` AS `id`,`s`.`svc_hasec` AS `svc_hasec`,`s`.`svc_hapri` AS `svc_hapri`,`s`.`svc_hastonith` AS `svc_hastonith`,`s`.`svc_hastartup` AS `svc_hastartup`,`s`.`svc_wave` AS `svc_wave`,`s`.`svc_vcpus` AS `svc_vcpus`,`s`.`svc_vmem` AS `svc_vmem`,`a`.`app` AS `app`,`a`.`responsibles` AS `responsibles`,`a`.`mailto` AS `mailto` from (`services` `s` left join `v_apps` `a` on((`a`.`app` = `s`.`svc_app`))) ;

#
# 2011-07-02
#
alter table action_queue add column ret integer default 0;

alter table svcmon engine=innodb;
alter table svcmon_log engine=innodb;
alter table services engine=innodb;
alter table services_log engine=innodb;

alter table log add column log_svcname varchar(256) default NULL;
alter table log add column log_nodename varchar(256) default NULL;
alter table log add column log_gtalk_sent tinyint(1) default 0;

#
# 2011-07-19
#
alter table resmon modify column res_desc varchar(200);
alter table stats_fs_u modify column size bigint;
alter table stats_cpu modify column soft float default 0;
alter table stats_cpu modify column irq float default 0;
alter table stats_cpu modify column guest float default 0;
alter table stats_cpu modify column steal float default 0;
alter table SVCactions modify column svcname varchar(60);
alter table SVCactions drop column action_group;
alter table SVCactions drop column B_SVCstatus, drop column E_SVCstatus;

drop view v_svcactions;

CREATE VIEW `v_svcactions` AS select ac.cron as cron, `ac`.`time` AS `time`, `ac`.`version` AS `version`,`ac`.`svcname` AS `svcname`,`ac`.`action` AS `action`,`ac`.`status` AS `status`,`ac`.`begin` AS `begin`,`ac`.`end` AS `end`,`ac`.`hostname` AS `hostname`,`ac`.`hostid` AS `hostid`,`ac`.`status_log` AS `status_log`,`ac`.`pid` AS `pid`,`ac`.`ID` AS `ID`,`ac`.`ack` AS `ack`,`ac`.`alert` AS `alert`,`ac`.`acked_by` AS `acked_by`,`ac`.`acked_comment` AS `acked_comment`,`ac`.`acked_date` AS `acked_date`,s.svc_ha as svc_ha,`s`.`svc_app` AS `app`, a.mailto, a.responsibles,`n`.`nodename` AS `nodename`,`n`.`loc_country` AS `loc_country`,`n`.`loc_city` AS `loc_city`,`n`.`loc_addr` AS `loc_addr`,`n`.`loc_building` AS `loc_building`,`n`.`loc_floor` AS `loc_floor`,`n`.`loc_room` AS `loc_room`,`n`.`loc_rack` AS `loc_rack`,`n`.`cpu_freq` AS `cpu_freq`,`n`.`cpu_cores` AS `cpu_cores`,`n`.`cpu_dies` AS `cpu_dies`,`n`.`cpu_vendor` AS `cpu_vendor`,`n`.`cpu_model` AS `cpu_model`,`n`.`mem_banks` AS `mem_banks`,`n`.`mem_slots` AS `mem_slots`,`n`.`mem_bytes` AS `mem_bytes`,`n`.`os_name` AS `os_name`,`n`.`os_release` AS `os_release`,`n`.`os_update` AS `os_update`,`n`.`os_segment` AS `os_segment`,`n`.`os_arch` AS `os_arch`,`n`.`os_vendor` AS `os_vendor`,`n`.`os_kernel` AS `os_kernel`,`n`.`loc_zip` AS `loc_zip`,`n`.`team_responsible` AS `team_responsible`,`n`.`serial` AS `serial`,`n`.`model` AS `model`,`n`.`type` AS `type`,`n`.`warranty_end` AS `warranty_end`,`n`.`status` AS `asset_status`,`n`.`role` AS `role`,`n`.`environnement` AS `environnement`,`n`.`power_supply_nb` AS `power_supply_nb`,`n`.`power_cabinet1` AS `power_cabinet1`,`n`.`power_cabinet2` AS `power_cabinet2`,`n`.`power_protect` AS `power_protect`,`n`.`power_protect_breaker` AS `power_protect_breaker`,`n`.`power_breaker1` AS `power_breaker1`,`n`.`power_breaker2` AS `power_breaker2` from `SVCactions` `ac` left join `services` `s` on `s`.`svc_name` = `ac`.`svcname` left join `nodes` `n` on `ac`.`hostname` = `n`.`nodename` left join b_apps a on a.app=s.svc_app;

#
# 2011-07-21
#
create view v_comp_node_status_current_week as (select `v_comp_status_weekly`.`id` AS `id`,`v_comp_status_weekly`.`year` AS `year`,`v_comp_status_weekly`.`week` AS `week`,`v_comp_status_weekly`.`run_nodename` AS `run_nodename`,sum(if((`v_comp_status_weekly`.`run_status` = 0),1,0)) AS `nb_ok`,sum(if((`v_comp_status_weekly`.`run_status` = 1),1,0)) AS `nb_nok`,sum(if((`v_comp_status_weekly`.`run_status` = 2),1,0)) AS `nb_na` from `v_comp_status_weekly` where `v_comp_status_weekly`.`year`=year(now()) and `v_comp_status_weekly`.`week`=week(now()) group by `v_comp_status_weekly`.`year`,`v_comp_status_weekly`.`week`,`v_comp_status_weekly`.`run_nodename`);

create table b_comp_node_status_weekly as (select `v_comp_status_weekly`.`id` AS `id`,`v_comp_status_weekly`.`year` AS `year`,`v_comp_status_weekly`.`week` AS `week`,`v_comp_status_weekly`.`run_nodename` AS `run_nodename`,sum(if((`v_comp_status_weekly`.`run_status` = 0),1,0)) AS `nb_ok`,sum(if((`v_comp_status_weekly`.`run_status` = 1),1,0)) AS `nb_nok`,sum(if((`v_comp_status_weekly`.`run_status` = 2),1,0)) AS `nb_na` from `v_comp_status_weekly` group by `v_comp_status_weekly`.`year`,`v_comp_status_weekly`.`week`,`v_comp_status_weekly`.`run_nodename`);

create unique index idx1 on b_comp_node_status_weekly (year, week, run_nodename);

drop view v_comp_node_status_weekly;


create view v_comp_module_status_current_week AS (select `v_comp_status_weekly`.`id` AS `id`,`v_comp_status_weekly`.`year` AS `year`,`v_comp_status_weekly`.`week` AS `week`,`v_comp_status_weekly`.`run_module` AS `run_module`,sum(if((`v_comp_status_weekly`.`run_status` = 0),1,0)) AS `nb_ok`,sum(if((`v_comp_status_weekly`.`run_status` = 1),1,0)) AS `nb_nok`,sum(if((`v_comp_status_weekly`.`run_status` = 2),1,0)) AS `nb_na` from `v_comp_status_weekly` where v_comp_status_weekly.year=year(now()) and v_comp_status_weekly.week=week(now()) group by `v_comp_status_weekly`.`year`,`v_comp_status_weekly`.`week`,`v_comp_status_weekly`.`run_module`);

create table b_comp_module_status_weekly AS (select `v_comp_status_weekly`.`id` AS `id`,`v_comp_status_weekly`.`year` AS `year`,`v_comp_status_weekly`.`week` AS `week`,`v_comp_status_weekly`.`run_module` AS `run_module`,sum(if((`v_comp_status_weekly`.`run_status` = 0),1,0)) AS `nb_ok`,sum(if((`v_comp_status_weekly`.`run_status` = 1),1,0)) AS `nb_nok`,sum(if((`v_comp_status_weekly`.`run_status` = 2),1,0)) AS `nb_na` from `v_comp_status_weekly` group by `v_comp_status_weekly`.`year`,`v_comp_status_weekly`.`week`,`v_comp_status_weekly`.`run_module`);

create unique index idx1 on b_comp_module_status_weekly (year, week, run_module);

drop view v_comp_module_status_weekly;

#
# 2011-07-29
#  v_svcactions optimization for 100k nodes & 100k services
#  - do not convert to utf8 on join
#  - join instead of left join in v_svcactions
#
alter table services default charset utf8;

drop view v_svcactions;

CREATE VIEW `v_svcactions` AS select `ac`.`cron` AS `cron`,`ac`.`time` AS `time`,`ac`.`version` AS `version`,`ac`.`svcname` AS `svcname`,`ac`.`action` AS `action`,`ac`.`status` AS `status`,`ac`.`begin` AS `begin`,`ac`.`end` AS `end`,`ac`.`hostname` AS `hostname`,`ac`.`hostid` AS `hostid`,`ac`.`status_log` AS `status_log`,`ac`.`pid` AS `pid`,`ac`.`ID` AS `ID`,`ac`.`ack` AS `ack`,`ac`.`alert` AS `alert`,`ac`.`acked_by` AS `acked_by`,`ac`.`acked_comment` AS `acked_comment`,`ac`.`acked_date` AS `acked_date`,`s`.`svc_ha` AS `svc_ha`,`s`.`svc_app` AS `app`,`a`.`mailto` AS `mailto`,`a`.`responsibles` AS `responsibles`,`n`.`nodename` AS `nodename`,`n`.`loc_country` AS `loc_country`,`n`.`loc_city` AS `loc_city`,`n`.`loc_addr` AS `loc_addr`,`n`.`loc_building` AS `loc_building`,`n`.`loc_floor` AS `loc_floor`,`n`.`loc_room` AS `loc_room`,`n`.`loc_rack` AS `loc_rack`,`n`.`cpu_freq` AS `cpu_freq`,`n`.`cpu_cores` AS `cpu_cores`,`n`.`cpu_dies` AS `cpu_dies`,`n`.`cpu_vendor` AS `cpu_vendor`,`n`.`cpu_model` AS `cpu_model`,`n`.`mem_banks` AS `mem_banks`,`n`.`mem_slots` AS `mem_slots`,`n`.`mem_bytes` AS `mem_bytes`,`n`.`os_name` AS `os_name`,`n`.`os_release` AS `os_release`,`n`.`os_update` AS `os_update`,`n`.`os_segment` AS `os_segment`,`n`.`os_arch` AS `os_arch`,`n`.`os_vendor` AS `os_vendor`,`n`.`os_kernel` AS `os_kernel`,`n`.`loc_zip` AS `loc_zip`,`n`.`team_responsible` AS `team_responsible`,`n`.`serial` AS `serial`,`n`.`model` AS `model`,`n`.`type` AS `type`,`n`.`warranty_end` AS `warranty_end`,`n`.`status` AS `asset_status`,`n`.`role` AS `role`,`n`.`environnement` AS `environnement`,`n`.`power_supply_nb` AS `power_supply_nb`,`n`.`power_cabinet1` AS `power_cabinet1`,`n`.`power_cabinet2` AS `power_cabinet2`,`n`.`power_protect` AS `power_protect`,`n`.`power_protect_breaker` AS `power_protect_breaker`,`n`.`power_breaker1` AS `power_breaker1`,`n`.`power_breaker2` AS `power_breaker2` from `SVCactions` `ac` join `services` `s` on `s`.`svc_name` = `ac`.`svcname` join `nodes` `n` on `ac`.`hostname` = `n`.`nodename` join `b_apps` `a` on `a`.`app` = `s`.`svc_app`;

alter table comp_status add index idx2 (run_nodename);

alter table comp_status add index idx3 (run_date);

alter table comp_log add index idx5 (run_module);

drop table b_comp_module_status_weekly_series;

drop table b_comp_node_status_weekly_series;

drop table b_comp_module_status_weekly;

drop table b_comp_node_status_weekly;

alter table log add column log_entry_id varchar(32);

update log set log_entry_id=md5(id);

alter table log add unique index idx3 (log_entry_id);

alter table log add column log_email_sent tinyint(1) default 0 after log_gtalk_sent;

alter table log add index idx4 (log_nodename);

alter table log add index idx5 (log_svcname);

create table pdns_domains (
 id		 INT auto_increment,
 name		 VARCHAR(255) NOT NULL,
 master		 VARCHAR(128) DEFAULT NULL,
 last_check	 INT DEFAULT NULL,
 type		 VARCHAR(6) NOT NULL,
 notified_serial INT DEFAULT NULL, 
 account         VARCHAR(40) DEFAULT NULL,
 primary key (id)
) Engine=InnoDB;

CREATE UNIQUE INDEX name_index ON pdns_domains(name);

CREATE TABLE pdns_records (
  id              INT auto_increment,
  domain_id       INT DEFAULT NULL,
  name            VARCHAR(255) DEFAULT NULL,
  type            VARCHAR(10) DEFAULT NULL,
  content         VARCHAR(255) DEFAULT NULL,
  ttl             INT DEFAULT NULL,
  prio            INT DEFAULT NULL,
  change_date     INT DEFAULT NULL,
  primary key(id)
)Engine=InnoDB;

CREATE INDEX rec_name_index ON pdns_records(name);
CREATE INDEX nametype_index ON pdns_records(name,type);
CREATE INDEX domain_id ON pdns_records(domain_id);

create table pdns_supermasters (
  ip VARCHAR(25) NOT NULL, 
  nameserver VARCHAR(255) NOT NULL, 
  account VARCHAR(40) DEFAULT NULL
) Engine=InnoDB;

alter table pdns_records add CONSTRAINT `records_ibfk_1` FOREIGN KEY (`domain_id`) REFERENCES `pdns_domains` (`id`) ON DELETE CASCADE;

CREATE TABLE networks (
  id              INT auto_increment,
  name            VARCHAR(255) DEFAULT NULL,
  network         VARCHAR(40) DEFAULT NULL,
  broadcast       VARCHAR(40) DEFAULT NULL,
  netmask         SMALLINT UNSIGNED DEFAULT NULL,
  team_responsible VARCHAR(255) DEFAULT NULL,
  primary key(id)
) Engine=InnoDB;

alter table networks add unique index idx1 (name);

alter table networks add unique index idx2 (network, broadcast);

CREATE TABLE appinfo (
  id              INT auto_increment,
  app_svcname     VARCHAR(60) DEFAULT NULL,
  app_launcher    VARCHAR(255) DEFAULT NULL,
  app_key         VARCHAR(40) DEFAULT NULL,
  app_value       VARCHAR(255) DEFAULT NULL,
  app_updated     timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  primary key(id)
) Engine=InnoDB;

alter table comp_status add column run_svcname varchar(64);

alter table comp_log add column run_svcname varchar(64);

alter table comp_status drop index idx1;

create unique index idx1 on comp_status (run_nodename, run_svcname, run_module);

CREATE TABLE `comp_rulesets_services` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ruleset_id` int(11) NOT NULL,
  `svcname` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx1` (`ruleset_id`,`svcname`),
  KEY `idx2` (`svcname`)
);

CREATE TABLE `comp_modulesets_services` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `modset_svcname` varchar(60) NOT NULL,
  `modset_id` int(11) NOT NULL,
  `modset_mod_author` varchar(100) DEFAULT '',
  `modset_updated` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx1` (`modset_svcname`,`modset_id`),
  KEY `idx2` (`modset_svcname`)
);

alter table log add column log_level enum("debug", "info", "warning", "error", "critical") default "info";

alter table auth_user add column email_log_level enum("debug", "info", "warning", "error", "critical") default "warning";

alter table auth_user add column im_log_level enum("debug", "info", "warning", "error", "critical") default "warning";

drop table alerts;

#
# remove join key conversion to utf8
#
alter table services modify column svc_name varchar(60) character set utf8;

drop view v_svcactions;

CREATE VIEW `v_svcactions` AS select `ac`.`cron` AS `cron`,`ac`.`time` AS `time`,`ac`.`version` AS `version`,`ac`.`svcname` AS `svcname`,`ac`.`action` AS `action`,`ac`.`status` AS `status`,`ac`.`begin` AS `begin`,`ac`.`end` AS `end`,`ac`.`hostname` AS `hostname`,`ac`.`hostid` AS `hostid`,`ac`.`status_log` AS `status_log`,`ac`.`pid` AS `pid`,`ac`.`ID` AS `ID`,`ac`.`ack` AS `ack`,`ac`.`alert` AS `alert`,`ac`.`acked_by` AS `acked_by`,`ac`.`acked_comment` AS `acked_comment`,`ac`.`acked_date` AS `acked_date`,`s`.`svc_ha` AS `svc_ha`,`s`.`svc_app` AS `app`,`a`.`mailto` AS `mailto`,`a`.`responsibles` AS `responsibles`,`n`.`nodename` AS `nodename`,`n`.`loc_country` AS `loc_country`,`n`.`loc_city` AS `loc_city`,`n`.`loc_addr` AS `loc_addr`,`n`.`loc_building` AS `loc_building`,`n`.`loc_floor` AS `loc_floor`,`n`.`loc_room` AS `loc_room`,`n`.`loc_rack` AS `loc_rack`,`n`.`cpu_freq` AS `cpu_freq`,`n`.`cpu_cores` AS `cpu_cores`,`n`.`cpu_dies` AS `cpu_dies`,`n`.`cpu_vendor` AS `cpu_vendor`,`n`.`cpu_model` AS `cpu_model`,`n`.`mem_banks` AS `mem_banks`,`n`.`mem_slots` AS `mem_slots`,`n`.`mem_bytes` AS `mem_bytes`,`n`.`os_name` AS `os_name`,`n`.`os_release` AS `os_release`,`n`.`os_update` AS `os_update`,`n`.`os_segment` AS `os_segment`,`n`.`os_arch` AS `os_arch`,`n`.`os_vendor` AS `os_vendor`,`n`.`os_kernel` AS `os_kernel`,`n`.`loc_zip` AS `loc_zip`,`n`.`team_responsible` AS `team_responsible`,`n`.`serial` AS `serial`,`n`.`model` AS `model`,`n`.`type` AS `type`,`n`.`warranty_end` AS `warranty_end`,`n`.`status` AS `asset_status`,`n`.`role` AS `role`,`n`.`environnement` AS `environnement`,`n`.`power_supply_nb` AS `power_supply_nb`,`n`.`power_cabinet1` AS `power_cabinet1`,`n`.`power_cabinet2` AS `power_cabinet2`,`n`.`power_protect` AS `power_protect`,`n`.`power_protect_breaker` AS `power_protect_breaker`,`n`.`power_breaker1` AS `power_breaker1`,`n`.`power_breaker2` AS `power_breaker2` from `SVCactions` `ac` join `services` `s` on `s`.`svc_name` = `ac`.`svcname` join `nodes` `n` on `ac`.`hostname` = `n`.`nodename` join `b_apps` `a` on `a`.`app` = `s`.`svc_app`;

CREATE TABLE `dashboard` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `dash_type` varchar(60) NOT NULL,
  `dash_svcname` varchar(60) NOT NULL,
  `dash_nodename` varchar(60) NOT NULL,
  `dash_severity` tinyint(4) NOT NULL,
  `dash_fmt` varchar(100) DEFAULT '',
  `dash_dict` varchar(200) DEFAULT '',
  `dash_created` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx1` (`dash_type`)
);

CREATE TABLE `dashboard_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `dash_type` varchar(60) NOT NULL,
  `dash_filters_md5` varchar(32) NOT NULL,
  `dash_alerts` integer DEFAULT NULL,
  `dash_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx1` (`dash_type`, `dash_date`)
);

alter table comp_status modify run_svcname varchar(60) default "";

# re-factorize comp_status
# alter table comp_status rename comp_status_old
# create table comp_status like comp_status_old
# insert into comp_status select a.* from comp_status_old a inner join (select max(id) as maxid from comp_status_old group by run_nodename, run_module) as b on a.id=b.maxid;

# use rw compression for data with high compression ratio ?
# alter table comp_log engine=innodb ROW_FORMAT=COMPRESSED;
# alter table stats_netdev_err engine=innodb ROW_FORMAT=COMPRESSED;
# alter table stats_netdev engine=innodb ROW_FORMAT=COMPRESSED;
# alter table stats_fs_u engine=innodb ROW_FORMAT=COMPRESSED;

alter table dashboard add column dash_dict_md5 varchar(32) default "";

alter table dashboard drop key idx1;

alter table dashboard add unique key idx1 (dash_type, dash_svcname, dash_nodename, dash_dict_md5);

CREATE TABLE `feed_queue` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `q_fn` varchar(60) NOT NULL,
  `q_args` longblob NOT NULL,
  PRIMARY KEY (`id`)
);

CREATE TABLE `feed_queue_stats` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `q_start` timestamp NOT NULL,
  `q_end` timestamp NOT NULL,
  `q_fn` varchar(60) NOT NULL,
  `q_count` integer NOT NULL,
  `q_avg` float NOT NULL,
  PRIMARY KEY (`id`)
);

# optimize v_flex_status
alter table services add index idx2 (svc_cluster_type);

drop view v_flex_status;

CREATE VIEW `v_flex_status` AS (select `p`.`ID` AS `id`,`p`.`mon_svcname` AS `svc_name`,`p`.`svc_flex_min_nodes` AS `svc_flex_min_nodes`,`p`.`svc_flex_max_nodes` AS `svc_flex_max_nodes`,`p`.`svc_flex_cpu_low_threshold` AS `svc_flex_cpu_low_threshold`,`p`.`svc_flex_cpu_high_threshold` AS `svc_flex_cpu_high_threshold`,count(1) AS `n`,(select count(1) AS `count(1)` from `svcmon` `c` where ((`c`.`mon_svcname` = `p`.`mon_svcname`) and (`c`.`mon_availstatus` = 'up'))) AS `up`,(select (100 - `c`.`idle`) AS `100-c.idle` from (`stats_cpu` `c` join `svcmon` `m`) where ((`c`.`nodename` = `m`.`mon_nodname`) and (`m`.`mon_svcname` = `p`.`mon_svcname`) and (`c`.`date` > (now() + interval -(15) minute)) and (`c`.`cpu` = 'all') and (`m`.`mon_overallstatus` = 'up')) group by `p`.`mon_svcname`) AS `cpu` from `v_svcmon` `p` where (`p`.`svc_cluster_type` in ('flex','autoflex')) group by `p`.`mon_svcname`);

alter table dashboard_log drop column dash_nodename;

# 2011-10-22
alter table gen_filterset_check_threshold add unique key idx2 (fset_id, chk_type, chk_instance);

CREATE TABLE gen_filterset_user (  `id` int(11) NOT NULL AUTO_INCREMENT,   `fset_id` int(11) NOT NULL, user_id int(11) NOT NULL,   PRIMARY KEY (`id`), UNIQUE KEY idx1 (fset_id, user_id) ) CHARSET=utf8;

alter table nodes modify column model varchar(60);

#
# upgrade CGR 2011-11-03
#

alter table svcmon drop key mon_svcname_2;
alter table svcmon drop key mon_svcname_3;
alter table svcmon drop key mon_svcname_4;
alter table svcmon drop key mon_hostid;

CREATE TABLE network_segments (
  id              INT auto_increment,
  net_id          INTEGER DEFAULT NULL,
  seg_type        ENUM("dynamic", "static") DEFAULT "static",
  seg_begin       VARCHAR(40) DEFAULT NULL,
  seg_end         VARCHAR(40) DEFAULT NULL,
  primary key(id)
) Engine=InnoDB;

CREATE TABLE network_segment_responsibles (
  id              INT auto_increment,
  seg_id          INTEGER DEFAULT NULL,
  group_id        INTEGER DEFAULT NULL,
  primary key(id)
) Engine=InnoDB;

alter table auth_user engine=InnoDB;

alter table comp_moduleset engine=InnoDB;

alter table comp_moduleset_modules engine=InnoDB;

alter table gen_filtersets engine=InnoDB;

alter table gen_filtersets_filters engine=InnoDB;

alter table gen_filters engine=InnoDB;

alter table upc_dashboard engine=InnoDB;

alter table user_prefs_columns engine=InnoDB;

alter table auth_group engine=InnoDB;

alter table resmon engine=InnoDB;

alter table prov_templates engine=InnoDB;

alter table prov_template_team_responsible engine=InnoDB;

alter table nodes engine=InnoDB;

alter table patches engine=InnoDB;

alter table packages engine=InnoDB;

alter table gen_filterset_user engine=InnoDB;

alter table gen_filterset_team_responsible engine=InnoDB;

alter table gen_filterset_check_threshold engine=InnoDB;

alter table drpservices engine=InnoDB;

alter table drpprojects engine=InnoDB;

alter table services engine=InnoDB;

alter table domain_permissions engine=InnoDB;

alter table dashboard engine=InnoDB;

alter table comp_rulesets_variables engine=InnoDB;

alter table comp_rulesets_services engine=InnoDB;

alter table comp_rulesets_nodes engine=InnoDB;

alter table comp_rulesets engine=InnoDB;

alter table comp_rulesets_filtersets engine=InnoDB;

alter table comp_ruleset_team_responsible engine=InnoDB;

alter table comp_node_moduleset engine=InnoDB;

alter table comp_moduleset engine=InnoDB;

alter table comp_modulesets_services engine=InnoDB;

alter table comp_moduleset_team_responsible engine=InnoDB;

alter table column_filters engine=InnoDB;

alter table auth_membership engine=InnoDB;

alter table apps_responsibles engine=InnoDB;

alter table apps engine=InnoDB;

alter table drpservices charset=utf8;

alter table drpprojects charset=utf8;

alter table domain_permissions charset=utf8;

alter table resmon charset utf8;

alter table patches charset=utf8;

alter table packages charset=utf8;

alter table packages modify `pkg_nodename` varchar(60) character set utf8 not null;

alter table packages modify `pkg_name` varchar(100) character set utf8 not null;

alter table packages modify `pkg_version` varchar(64) character set utf8 not null;

alter table packages modify `pkg_arch` varchar(8) character set utf8 not null;

alter table patches modify patch_nodename varchar(60) CHARACTER SET utf8 not null;

alter table patches modify patch_num varchar(100) CHARACTER SET utf8 not null;

alter table patches modify patch_rev varchar(32) CHARACTER SET utf8 not null;

alter table resmon modify svcname varchar(60);

alter table resmon modify nodename varchar(60);

alter table resmon modify rid varchar(10);

alter table resmon modify res_status enum('up','down','warn','n/a','undef','stdby up','stdby down') DEFAULT 'undef';

alter table resmon modify res_desc varchar(200);

alter table resmon modify res_log varchar(200) default "";

alter table svcmon rename svcmon2;

CREATE TABLE `svcmon` (
  `mon_svcname` varchar(60) NOT NULL,
  `mon_svctype` varchar(10) DEFAULT NULL,
  `mon_drptype` varchar(10) DEFAULT NULL,
  `mon_nodname` varchar(50) DEFAULT NULL,
  `mon_nodtype` varchar(10) DEFAULT NULL,
  `mon_nodmode` varchar(10) DEFAULT NULL,
  `mon_ipstatus` enum('up','down','warn','n/a','undef','stdby up','stdby down') DEFAULT 'undef',
  `mon_fsstatus` enum('up','down','warn','n/a','undef','stdby up','stdby down') DEFAULT 'undef',
  `mon_prinodes` varchar(255) DEFAULT NULL,
  `mon_updated` datetime DEFAULT NULL,
  `mon_hostid` varchar(30) DEFAULT NULL,
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `mon_frozen` int(11) DEFAULT NULL,
  `mon_frozentxt` varchar(255) DEFAULT NULL,
  `mon_changed` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `mon_diskstatus` enum('up','down','warn','n/a','undef','stdby up','stdby down') DEFAULT 'undef',
  `mon_containerstatus` enum('up','down','warn','n/a','undef','stdby up','stdby down') DEFAULT 'undef',
  `mon_overallstatus` enum('up','down','warn','n/a','undef','stdby up','stdby down') DEFAULT 'undef',
  `mon_syncstatus` enum('up','down','warn','n/a','undef','stdby up','stdby down') DEFAULT 'undef',
  `mon_appstatus` enum('up','down','warn','n/a','undef','stdby up','stdby down') DEFAULT 'undef',
  `mon_hbstatus` enum('up','down','warn','n/a','undef','stdby up','stdby down') DEFAULT 'undef',
  `mon_availstatus` enum('up','down','warn','n/a','undef','stdby up','stdby down') DEFAULT 'undef',
  PRIMARY KEY (`ID`),
  UNIQUE KEY `mon_svcname_5` (`mon_svcname`,`mon_nodname`),
  KEY `mon_svcname` (`mon_svcname`),
  KEY `mon_nodname` (`mon_nodname`)
) ENGINE=InnoDB AUTO_INCREMENT=206504424 DEFAULT CHARSET=utf8;

alter table svcmon_log charset utf8;

alter table svcmon_log modify `mon_overallstatus` enum('up','down','warn','n/a','undef','stdby up','stdby down') DEFAULT 'undef';
alter table svcmon_log modify `mon_ipstatus` enum('up','down','warn','n/a','undef','stdby up','stdby down') DEFAULT 'undef';
alter table svcmon_log modify `mon_fsstatus` enum('up','down','warn','n/a','undef','stdby up','stdby down') DEFAULT 'undef';
alter table svcmon_log modify `mon_diskstatus` enum('up','down','warn','n/a','undef','stdby up','stdby down') DEFAULT 'undef';
alter table svcmon_log modify `mon_containerstatus` enum('up','down','warn','n/a','undef','stdby up','stdby down') DEFAULT 'undef';
alter table svcmon_log modify `mon_syncstatus` enum('up','down','warn','n/a','undef','stdby up','stdby down') DEFAULT 'undef';
alter table svcmon_log modify `mon_appstatus` enum('up','down','warn','n/a','undef','stdby up','stdby down') DEFAULT 'undef';
alter table svcmon_log modify `mon_hbstatus` enum('up','down','warn','n/a','undef','stdby up','stdby down') DEFAULT 'undef';
alter table svcmon_log modify `mon_availstatus` enum('up','down','warn','n/a','undef','stdby up','stdby down') DEFAULT 'undef';
alter table svcmon_log modify `mon_svcname` varchar(60);
alter table svcmon_log modify `mon_nodname` varchar(60);

insert into svcmon (select * from svcmon2);

drop table svcmon2;

alter table network_segments ADD CONSTRAINT network_segments_fk1 FOREIGN KEY (net_id) REFERENCES networks(id) ON DELETE CASCADE;

alter table network_segment_responsibles ADD CONSTRAINT network_segment_responsibles_fk1 FOREIGN KEY (seg_id) REFERENCES network_segments(id) ON DELETE CASCADE;

alter table network_segment_responsibles ADD CONSTRAINT network_segment_responsibles_fk2 FOREIGN KEY (group_id) REFERENCES auth_group(id) ON DELETE CASCADE;

alter table user_prefs_columns ADD CONSTRAINT user_prefs_columns_fk1 FOREIGN KEY (upc_user_id) REFERENCES auth_user(id) ON DELETE CASCADE;

alter table upc_dashboard ADD CONSTRAINT upc_dashboard_fk1 FOREIGN KEY (upc_user_id) REFERENCES auth_user(id) ON DELETE CASCADE;

delete from resmon where concat(svcname,nodename) not in (select concat(mon_svcname,mon_nodname) from svcmon);

alter table resmon ADD CONSTRAINT resmon_fk1 FOREIGN KEY (svcname, nodename) REFERENCES svcmon(mon_svcname, mon_nodname) ON DELETE CASCADE;

alter table prov_template_team_responsible ADD CONSTRAINT prov_template_team_responsible_fk1 FOREIGN KEY (tpl_id) REFERENCES prov_templates(id) ON DELETE CASCADE;

alter table patches ADD CONSTRAINT patches_fk1 FOREIGN KEY (patch_nodename) REFERENCES nodes(nodename) ON DELETE CASCADE;

delete from packages where pkg_nodename not in (select nodename from nodes);

alter table packages ADD CONSTRAINT packages_fk1 FOREIGN KEY (pkg_nodename) REFERENCES nodes(nodename) ON DELETE CASCADE;

delete from gen_filtersets_filters where fset_id not in (select id from gen_filtersets);

#alter table gen_filtersets_filters ADD CONSTRAINT gen_filtersets_filters_fk1 FOREIGN KEY (fset_id) REFERENCES gen_filtersets(id) ON DELETE CASCADE;

delete from gen_filtersets_filters where f_id not in (select id from gen_filters);

#alter table gen_filtersets_filters ADD CONSTRAINT gen_filtersets_filters_fk2 FOREIGN KEY (f_id) REFERENCES gen_filters(id) ON DELETE CASCADE;

alter table gen_filterset_user ADD CONSTRAINT gen_filterset_user_fk1 FOREIGN KEY (fset_id) REFERENCES gen_filtersets(id) ON DELETE CASCADE;

alter table gen_filterset_user ADD CONSTRAINT gen_filterset_user_fk2 FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE;

alter table gen_filterset_team_responsible ADD CONSTRAINT gen_filterset_team_responsible_fk1 FOREIGN KEY (fset_id) REFERENCES gen_filtersets(id) ON DELETE CASCADE;

alter table gen_filterset_team_responsible ADD CONSTRAINT gen_filterset_team_responsible_fk2 FOREIGN KEY (group_id) REFERENCES auth_group(id) ON DELETE CASCADE;

alter table gen_filterset_check_threshold ADD CONSTRAINT gen_filterset_check_threshold_fk1 FOREIGN KEY (fset_id) REFERENCES gen_filtersets(id) ON DELETE CASCADE;

alter table drpprojects drop key drp_project_index;

delete from drpservices where drp_project_id not in (select drp_project_id from drpprojects);

alter table drpservices ADD CONSTRAINT drpservices_fk1 FOREIGN KEY (drp_project_id) REFERENCES drpprojects(drp_project_id) ON DELETE CASCADE;

delete from drpservices where drp_svcname not in (select svc_name from services);

alter table drpservices modify drp_wave varchar(10);

alter table drpservices modify drp_svcname varchar(60);

alter table drpservices ADD CONSTRAINT drpservices_fk2 FOREIGN KEY (drp_svcname) REFERENCES services(svc_name) ON DELETE CASCADE;

alter table domain_permissions ADD CONSTRAINT domain_permissions_fk1 FOREIGN KEY (group_id) REFERENCES auth_group(id) ON DELETE CASCADE;

alter table comp_rulesets_variables ADD CONSTRAINT comp_rulesets_variables_fk1 FOREIGN KEY (ruleset_id) REFERENCES comp_rulesets(id) ON DELETE CASCADE;

alter table comp_rulesets_services charset utf8;

alter table comp_rulesets_services modify svcname varchar(100) character set utf8 not null;

alter table comp_rulesets_services ADD CONSTRAINT comp_rulesets_services_fk1 FOREIGN KEY (ruleset_id) REFERENCES comp_rulesets(id) ON DELETE CASCADE;

alter table comp_rulesets_services ADD CONSTRAINT comp_rulesets_services_fk2 FOREIGN KEY (svcname) REFERENCES services(svc_name) ON DELETE CASCADE;

delete from comp_rulesets_nodes where ruleset_id not in (select id from comp_rulesets);

alter table comp_rulesets_nodes ADD CONSTRAINT comp_rulesets_nodes_fk1 FOREIGN KEY (ruleset_id) REFERENCES comp_rulesets(id) ON DELETE CASCADE;

alter table comp_rulesets_nodes ADD CONSTRAINT comp_rulesets_nodes_fk2 FOREIGN KEY (nodename) REFERENCES nodes(nodename) ON DELETE CASCADE;

alter table comp_rulesets_filtersets ADD CONSTRAINT comp_rulesets_filtersets_fk1 FOREIGN KEY (ruleset_id) REFERENCES comp_rulesets(id) ON DELETE CASCADE;

alter table comp_rulesets_filtersets ADD CONSTRAINT comp_rulesets_filtersets_fk2 FOREIGN KEY (fset_id) REFERENCES gen_filtersets(id) ON DELETE CASCADE;

alter table comp_ruleset_team_responsible ADD CONSTRAINT comp_ruleset_team_responsible_fk1 FOREIGN KEY (ruleset_id) REFERENCES comp_rulesets(id) ON DELETE CASCADE;

alter table comp_ruleset_team_responsible ADD CONSTRAINT comp_ruleset_team_responsible_fk2 FOREIGN KEY (group_id) REFERENCES auth_group(id) ON DELETE CASCADE;

delete from comp_node_moduleset where modset_id not in (select id from comp_moduleset);

alter table comp_node_moduleset ADD CONSTRAINT comp_node_moduleset_fk1 FOREIGN KEY (modset_id) REFERENCES comp_moduleset(id) ON DELETE CASCADE;

delete from comp_node_moduleset where modset_node not in (select nodename from nodes);

alter table comp_node_moduleset ADD CONSTRAINT comp_node_moduleset_fk2 FOREIGN KEY (modset_node) REFERENCES nodes(nodename) ON DELETE CASCADE;

alter table comp_modulesets_services charset=utf8;

alter table comp_modulesets_services modify modset_svcname varchar(60) character set utf8 not null;

alter table comp_modulesets_services modify modset_mod_author varchar(100) character set utf8 default '';

alter table comp_modulesets_services ADD CONSTRAINT comp_modulesets_services_fk1 FOREIGN KEY (modset_id) REFERENCES comp_moduleset(id) ON DELETE CASCADE;

alter table comp_modulesets_services ADD CONSTRAINT comp_modulesets_services_fk2 FOREIGN KEY (modset_svcname) REFERENCES services(svc_name) ON DELETE CASCADE;

delete from comp_moduleset_team_responsible where modset_id not in (select id from comp_moduleset);

alter table comp_moduleset_team_responsible ADD CONSTRAINT comp_moduleset_team_responsible_fk1 FOREIGN KEY (modset_id) REFERENCES comp_moduleset(id) ON DELETE CASCADE;

alter table comp_moduleset_team_responsible ADD CONSTRAINT comp_moduleset_team_responsible_fk2 FOREIGN KEY (group_id) REFERENCES auth_group(id) ON DELETE CASCADE;

alter table comp_moduleset_modules ADD CONSTRAINT comp_moduleset_modules_fk1 FOREIGN KEY (modset_id) REFERENCES comp_moduleset(id) ON DELETE CASCADE;

alter table column_filters ADD CONSTRAINT column_filters_fk1 FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE;

alter table auth_membership ADD CONSTRAINT auth_membership_fk1 FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE;

alter table auth_membership ADD CONSTRAINT auth_membership_fk2 FOREIGN KEY (group_id) REFERENCES auth_group(id) ON DELETE CASCADE;

alter table apps_responsibles ADD CONSTRAINT apps_responsibles_fk2 FOREIGN KEY (group_id) REFERENCES auth_group(id) ON DELETE CASCADE;

alter table apps_responsibles ADD CONSTRAINT apps_responsibles_fk1 FOREIGN KEY (app_id) REFERENCES apps(id) ON DELETE CASCADE;

alter table appinfo charset=utf8;

alter table appinfo modify `app_svcname` varchar(60) character set utf8 default null;

alter table appinfo modify `app_launcher` varchar(255) character set utf8 default null;

alter table appinfo modify `app_key` varchar(40) character set utf8 default null;

alter table appinfo modify `app_value` varchar(255) character set utf8 default null;

alter table appinfo ADD CONSTRAINT appinfo_fk1 FOREIGN KEY (app_svcname) REFERENCES services(svc_name) ON DELETE CASCADE;

delete from svcmon where mon_nodname not in (select distinct nodename from nodes);

alter table svcmon ADD CONSTRAINT svcmon_fk1 FOREIGN KEY (mon_nodname) REFERENCES nodes(nodename) ON DELETE CASCADE;

drop table services2;

drop table dashboard_old;

drop table dashboard_tmp;

create view v_network_segments as (select s.*, group_concat(g.role separator ", ") as teams_responsible from network_segments s left join network_segment_responsibles sr on s.id=sr.seg_id left join auth_group g on sr.group_id=g.id group by s.id);

alter table services modify svc_vcpus float default 0;

#

alter table stat_day add column fset_id integer default 0;

alter table stat_day drop key new_index;

alter table stat_day add unique key stat_day_uk1 (day, fset_id);

alter table lifecycle_os add column fset_id integer default 0;

alter table lifecycle_os drop key idx1;

alter table lifecycle_os add unique key lifecycle_os_uk1 (lc_os_concat, lc_date, fset_id);

alter table stat_day modify column ram_size int(11) default 0;
alter table stat_day modify column nb_cpu_core int(11) default 0;
alter table stat_day modify column nb_cpu_die int(11) default 0;
alter table stat_day modify column watt int(11) default 0;
alter table stat_day modify column rackunit int(11) default 0;

drop view v_lifecycle_os_name;

CREATE VIEW `v_lifecycle_os_name` AS select `lifecycle_os`.`id` AS `id`,`lifecycle_os`.`fset_id` AS `fset_id`, `lifecycle_os`.`lc_date` AS `lc_date`,sum(`lifecycle_os`.`lc_count`) AS `lc_count`,`lifecycle_os`.`lc_os_name` AS `lc_os_name` from `lifecycle_os` group by `lifecycle_os`.`lc_date`,`lifecycle_os`.`lc_os_name`,`lifecycle_os`.`fset_id` order by `lifecycle_os`.`lc_date`,`lifecycle_os`.`lc_os_name`;

alter table nodes add column team_integ varchar(20);

drop view v_nodes;

CREATE VIEW `v_nodes` AS (select `n`.`nodename` AS `nodename`,`n`.`loc_country` AS `loc_country`,`n`.`loc_city` AS `loc_city`,`n`.`loc_addr` AS `loc_addr`,`n`.`loc_building` AS `loc_building`,`n`.`loc_floor` AS `loc_floor`,`n`.`loc_room` AS `loc_room`,`n`.`loc_rack` AS `loc_rack`,`n`.`id` AS `id`,`n`.`cpu_freq` AS `cpu_freq`,`n`.`cpu_cores` AS `cpu_cores`,`n`.`cpu_dies` AS `cpu_dies`,`n`.`cpu_vendor` AS `cpu_vendor`,`n`.`cpu_model` AS `cpu_model`,`n`.`mem_banks` AS `mem_banks`,`n`.`mem_slots` AS `mem_slots`,`n`.`mem_bytes` AS `mem_bytes`,`n`.`os_name` AS `os_name`,`n`.`os_release` AS `os_release`,`n`.`os_update` AS `os_update`,`n`.`os_segment` AS `os_segment`,`n`.`os_arch` AS `os_arch`,`n`.`os_vendor` AS `os_vendor`,`n`.`os_kernel` AS `os_kernel`,`n`.`loc_zip` AS `loc_zip`,`n`.`team_responsible` AS `team_responsible`, n.team_integ as team_integ, `n`.`serial` AS `serial`,`n`.`model` AS `model`,`n`.`type` AS `type`,`n`.`warranty_end` AS `warranty_end`,`n`.`status` AS `status`,`n`.`role` AS `role`,`n`.`environnement` AS `environnement`,`n`.`power_cabinet1` AS `power_cabinet1`,`n`.`power_cabinet2` AS `power_cabinet2`,`n`.`power_supply_nb` AS `power_supply_nb`,`n`.`power_protect` AS `power_protect`,`n`.`power_protect_breaker` AS `power_protect_breaker`,`n`.`power_breaker1` AS `power_breaker1`,`n`.`power_breaker2` AS `power_breaker2`,concat_ws(' ',`n`.`os_name`,`n`.`os_vendor`,`n`.`os_release`,`n`.`os_update`) AS `os_concat`,`n`.`updated` AS `updated` from `nodes` `n`);

drop view v_svcmon;

CREATE VIEW `v_svcmon` AS select `e`.`err` AS `err`,`s`.`svc_ha` AS `svc_ha`,`s`.`svc_cluster_type` AS `svc_cluster_type`,`s`.`svc_status` AS `svc_status`,`s`.`svc_availstatus` AS `svc_availstatus`,`s`.`svc_flex_min_nodes` AS `svc_flex_min_nodes`,`s`.`svc_flex_max_nodes` AS `svc_flex_max_nodes`,`s`.`svc_flex_cpu_low_threshold` AS `svc_flex_cpu_low_threshold`,`s`.`svc_flex_cpu_high_threshold` AS `svc_flex_cpu_high_threshold`,`s`.`svc_vmname` AS `svc_vmname`,`s`.`svc_guestos` AS `svc_guestos`,`s`.`svc_version` AS `svc_version`,`s`.`svc_name` AS `svc_name`,`s`.`svc_nodes` AS `svc_nodes`,`s`.`svc_drpnode` AS `svc_drpnode`,`s`.`svc_drpnodes` AS `svc_drpnodes`,`s`.`svc_drptype` AS `svc_drptype`,`s`.`svc_autostart` AS `svc_autostart`,`s`.`svc_type` AS `svc_type`,`s`.`svc_comment` AS `svc_comment`,`s`.`svc_app` AS `svc_app`,`s`.`svc_drnoaction` AS `svc_drnoaction`,`s`.`svc_created` AS `svc_created`,`s`.`updated` AS `svc_updated`,`s`.`svc_envdate` AS `svc_envdate`,`s`.`svc_containertype` AS `svc_containertype`,`s`.`svc_metrocluster` AS `svc_metrocluster`,`s`.`svc_vcpus` AS `svc_vcpus`,`s`.`svc_vmem` AS `svc_vmem`,`m`.`mon_svcname` AS `mon_svcname`,`m`.`mon_svctype` AS `mon_svctype`,`m`.`mon_drptype` AS `mon_drptype`,`m`.`mon_nodname` AS `mon_nodname`,`m`.`mon_nodtype` AS `mon_nodtype`,`m`.`mon_nodmode` AS `mon_nodmode`,`m`.`mon_ipstatus` AS `mon_ipstatus`,`m`.`mon_fsstatus` AS `mon_fsstatus`,`m`.`mon_prinodes` AS `mon_prinodes`,`m`.`mon_hostid` AS `mon_hostid`,`m`.`ID` AS `ID`,`m`.`mon_frozen` AS `mon_frozen`,`m`.`mon_frozentxt` AS `mon_frozentxt`,`m`.`mon_changed` AS `mon_changed`,`m`.`mon_updated` AS `mon_updated`,`m`.`mon_diskstatus` AS `mon_diskstatus`,`m`.`mon_containerstatus` AS `mon_containerstatus`,`m`.`mon_overallstatus` AS `mon_overallstatus`,`n`.`nodename` AS `nodename`,`n`.`updated` AS `node_updated`,`n`.`loc_country` AS `loc_country`,`n`.`loc_city` AS `loc_city`,`n`.`loc_addr` AS `loc_addr`,`n`.`loc_building` AS `loc_building`,`n`.`loc_floor` AS `loc_floor`,`n`.`loc_room` AS `loc_room`,`n`.`loc_rack` AS `loc_rack`,`n`.`cpu_freq` AS `cpu_freq`,`n`.`cpu_cores` AS `cpu_cores`,`n`.`cpu_dies` AS `cpu_dies`,`n`.`cpu_vendor` AS `cpu_vendor`,`n`.`cpu_model` AS `cpu_model`,`n`.`mem_banks` AS `mem_banks`,`n`.`mem_slots` AS `mem_slots`,`n`.`mem_bytes` AS `mem_bytes`,`n`.`os_name` AS `os_name`,`n`.`os_release` AS `os_release`,`n`.`os_update` AS `os_update`,`n`.`os_segment` AS `os_segment`,`n`.`os_arch` AS `os_arch`,`n`.`os_vendor` AS `os_vendor`,`n`.`os_kernel` AS `os_kernel`,`n`.`loc_zip` AS `loc_zip`,`n`.`team_responsible` AS `team_responsible`, n.team_integ as team_integ, `n`.`serial` AS `serial`,`n`.`model` AS `model`,`n`.`type` AS `type`,`n`.`warranty_end` AS `warranty_end`,`n`.`status` AS `status`,`n`.`role` AS `role`,`n`.`environnement` AS `environnement`,`n`.`power_supply_nb` AS `power_supply_nb`,`n`.`power_cabinet1` AS `power_cabinet1`,`n`.`power_cabinet2` AS `power_cabinet2`,`n`.`power_protect` AS `power_protect`,`n`.`power_protect_breaker` AS `power_protect_breaker`,`n`.`power_breaker1` AS `power_breaker1`,`n`.`power_breaker2` AS `power_breaker2`,`m`.`mon_syncstatus` AS `mon_syncstatus`,`m`.`mon_hbstatus` AS `mon_hbstatus`,`m`.`mon_availstatus` AS `mon_availstatus`,`m`.`mon_appstatus` AS `mon_appstatus`,`ap`.`responsibles` AS `responsibles`,`ap`.`mailto` AS `mailto` from ((((`svcmon` `m` left join `services` `s` on((`s`.`svc_name` = `m`.`mon_svcname`))) left join `nodes` `n` on((convert(`m`.`mon_nodname` using utf8) = `n`.`nodename`))) left join `b_apps` `ap` on((`ap`.`app` = `s`.`svc_app`))) left join `b_action_errors` `e` on(((`e`.`svcname` = convert(`s`.`svc_name` using utf8)) and (`e`.`nodename` = convert(`m`.`mon_nodname` using utf8)))));

drop view v_svcactions;

CREATE VIEW `v_svcactions` AS select `ac`.`cron` AS `cron`,`ac`.`time` AS `time`,`ac`.`version` AS `version`,`ac`.`svcname` AS `svcname`,`ac`.`action` AS `action`,`ac`.`status` AS `status`,`ac`.`begin` AS `begin`,`ac`.`end` AS `end`,`ac`.`hostname` AS `hostname`,`ac`.`hostid` AS `hostid`,`ac`.`status_log` AS `status_log`,`ac`.`pid` AS `pid`,`ac`.`ID` AS `ID`,`ac`.`ack` AS `ack`,`ac`.`alert` AS `alert`,`ac`.`acked_by` AS `acked_by`,`ac`.`acked_comment` AS `acked_comment`,`ac`.`acked_date` AS `acked_date`,`s`.`svc_ha` AS `svc_ha`,`s`.`svc_app` AS `app`,`a`.`mailto` AS `mailto`,`a`.`responsibles` AS `responsibles`,`n`.`nodename` AS `nodename`,`n`.`loc_country` AS `loc_country`,`n`.`loc_city` AS `loc_city`,`n`.`loc_addr` AS `loc_addr`,`n`.`loc_building` AS `loc_building`,`n`.`loc_floor` AS `loc_floor`,`n`.`loc_room` AS `loc_room`,`n`.`loc_rack` AS `loc_rack`,`n`.`cpu_freq` AS `cpu_freq`,`n`.`cpu_cores` AS `cpu_cores`,`n`.`cpu_dies` AS `cpu_dies`,`n`.`cpu_vendor` AS `cpu_vendor`,`n`.`cpu_model` AS `cpu_model`,`n`.`mem_banks` AS `mem_banks`,`n`.`mem_slots` AS `mem_slots`,`n`.`mem_bytes` AS `mem_bytes`,`n`.`os_name` AS `os_name`,`n`.`os_release` AS `os_release`,`n`.`os_update` AS `os_update`,`n`.`os_segment` AS `os_segment`,`n`.`os_arch` AS `os_arch`,`n`.`os_vendor` AS `os_vendor`,`n`.`os_kernel` AS `os_kernel`,`n`.`loc_zip` AS `loc_zip`,`n`.`team_responsible` AS `team_responsible`, n.team_integ as team_integ, `n`.`serial` AS `serial`,`n`.`model` AS `model`,`n`.`type` AS `type`,`n`.`warranty_end` AS `warranty_end`,`n`.`status` AS `asset_status`,`n`.`role` AS `role`,`n`.`environnement` AS `environnement`,`n`.`power_supply_nb` AS `power_supply_nb`,`n`.`power_cabinet1` AS `power_cabinet1`,`n`.`power_cabinet2` AS `power_cabinet2`,`n`.`power_protect` AS `power_protect`,`n`.`power_protect_breaker` AS `power_protect_breaker`,`n`.`power_breaker1` AS `power_breaker1`,`n`.`power_breaker2` AS `power_breaker2` from (((`SVCactions` `ac` join `services` `s` on((`s`.`svc_name` = `ac`.`svcname`))) join `nodes` `n` on((`ac`.`hostname` = `n`.`nodename`))) join `b_apps` `a` on((`a`.`app` = `s`.`svc_app`)));

CREATE TABLE comp_rulesets_rulesets (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `parent_rset_id` integer NOT NULL,
  `child_rset_id` integer NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `comp_rulesets_rulesets_uk1` (parent_rset_id, child_rset_id)

) ENGINE=InnoDB CHARSET=utf8;

alter table comp_rulesets_rulesets ADD CONSTRAINT comp_rulesets_rulesets_fk1 FOREIGN KEY (parent_rset_id) REFERENCES comp_rulesets(id) ON DELETE CASCADE;
alter table comp_rulesets_rulesets ADD CONSTRAINT comp_rulesets_rulesets_fk2 FOREIGN KEY (child_rset_id) REFERENCES comp_rulesets(id) ON DELETE CASCADE;

drop view v_comp_rulesets;

create view v_comp_rulesets as (select `r`.`id` AS `ruleset_id`,`r`.`ruleset_name` AS `ruleset_name`,`r`.`ruleset_type` AS `ruleset_type`,group_concat(distinct `g`.`role` separator ', ') AS `teams_responsible`,(select ruleset_name from comp_rulesets where id=rr.child_rset_id) as encap_rset, rr.child_rset_id as encap_rset_id, `rv`.`id` AS `id`,`rv`.`var_name` AS `var_name`,`rv`.`var_class` AS `var_class`,`rv`.`var_value` AS `var_value`,`rv`.`var_author` AS `var_author`,`rv`.`var_updated` AS `var_updated`,`rf`.`fset_id` AS `fset_id`,`fs`.`fset_name` AS `fset_name` from (((((`comp_rulesets` `r` left join comp_rulesets_rulesets rr on r.id=rr.parent_rset_id left join `comp_rulesets_variables` `rv` on((`rv`.`ruleset_id` = `r`.`id` or rv.ruleset_id = rr.child_rset_id))) left join `comp_rulesets_filtersets` `rf` on((`r`.`id` = `rf`.`ruleset_id`))) left join `gen_filtersets` `fs` on((`fs`.`id` = `rf`.`fset_id`))) left join `comp_ruleset_team_responsible` `rt` on((`r`.`id` = `rt`.`ruleset_id`))) left join `auth_group` `g` on((`rt`.`group_id` = `g`.`id`))) group by `r`.`id`,`rv`.`id`, rr.id);

drop view v_comp_explicit_rulesets;

CREATE VIEW `v_comp_explicit_rulesets` AS (select `r`.`id` AS `id`,`r`.`ruleset_name` AS `ruleset_name`,group_concat(distinct concat(`v`.`var_name`,'=',`v`.`var_value`) separator '|') AS `variables` from (`comp_rulesets` `r` left join `comp_rulesets_variables` `v` on((`r`.`id` = `v`.`ruleset_id`))) where r.ruleset_type='explicit' group by `r`.`id` order by `r`.`ruleset_name`);

alter table nodes add column project varchar(64);

drop view v_nodes;

CREATE VIEW `v_nodes` AS (select `n`.`nodename` AS `nodename`,`n`.`loc_country` AS `loc_country`,`n`.`loc_city` AS `loc_city`,`n`.`loc_addr` AS `loc_addr`,`n`.`loc_building` AS `loc_building`,`n`.`loc_floor` AS `loc_floor`,`n`.`loc_room` AS `loc_room`,`n`.`loc_rack` AS `loc_rack`,`n`.`id` AS `id`,`n`.`cpu_freq` AS `cpu_freq`,`n`.`cpu_cores` AS `cpu_cores`,`n`.`cpu_dies` AS `cpu_dies`,`n`.`cpu_vendor` AS `cpu_vendor`,`n`.`cpu_model` AS `cpu_model`,`n`.`mem_banks` AS `mem_banks`,`n`.`mem_slots` AS `mem_slots`,`n`.`mem_bytes` AS `mem_bytes`,`n`.`os_name` AS `os_name`,`n`.`os_release` AS `os_release`,`n`.`os_update` AS `os_update`,`n`.`os_segment` AS `os_segment`,`n`.`os_arch` AS `os_arch`,`n`.`os_vendor` AS `os_vendor`,`n`.`os_kernel` AS `os_kernel`,`n`.`loc_zip` AS `loc_zip`,`n`.`team_responsible` AS `team_responsible`, n.team_integ as team_integ, n.project as project, `n`.`serial` AS `serial`,`n`.`model` AS `model`,`n`.`type` AS `type`,`n`.`warranty_end` AS `warranty_end`,`n`.`status` AS `status`,`n`.`role` AS `role`,`n`.`environnement` AS `environnement`,`n`.`power_cabinet1` AS `power_cabinet1`,`n`.`power_cabinet2` AS `power_cabinet2`,`n`.`power_supply_nb` AS `power_supply_nb`,`n`.`power_protect` AS `power_protect`,`n`.`power_protect_breaker` AS `power_protect_breaker`,`n`.`power_breaker1` AS `power_breaker1`,`n`.`power_breaker2` AS `power_breaker2`,concat_ws(' ',`n`.`os_name`,`n`.`os_vendor`,`n`.`os_release`,`n`.`os_update`) AS `os_concat`,`n`.`updated` AS `updated` from `nodes` `n`);

drop view v_svcmon;

CREATE VIEW `v_svcmon` AS select `e`.`err` AS `err`,`s`.`svc_ha` AS `svc_ha`,`s`.`svc_cluster_type` AS `svc_cluster_type`,`s`.`svc_status` AS `svc_status`,`s`.`svc_availstatus` AS `svc_availstatus`,`s`.`svc_flex_min_nodes` AS `svc_flex_min_nodes`,`s`.`svc_flex_max_nodes` AS `svc_flex_max_nodes`,`s`.`svc_flex_cpu_low_threshold` AS `svc_flex_cpu_low_threshold`,`s`.`svc_flex_cpu_high_threshold` AS `svc_flex_cpu_high_threshold`,`s`.`svc_vmname` AS `svc_vmname`,`s`.`svc_guestos` AS `svc_guestos`,`s`.`svc_version` AS `svc_version`,`s`.`svc_name` AS `svc_name`,`s`.`svc_nodes` AS `svc_nodes`,`s`.`svc_drpnode` AS `svc_drpnode`,`s`.`svc_drpnodes` AS `svc_drpnodes`,`s`.`svc_drptype` AS `svc_drptype`,`s`.`svc_autostart` AS `svc_autostart`,`s`.`svc_type` AS `svc_type`,`s`.`svc_comment` AS `svc_comment`,`s`.`svc_app` AS `svc_app`,`s`.`svc_drnoaction` AS `svc_drnoaction`,`s`.`svc_created` AS `svc_created`,`s`.`updated` AS `svc_updated`,`s`.`svc_envdate` AS `svc_envdate`,`s`.`svc_containertype` AS `svc_containertype`,`s`.`svc_metrocluster` AS `svc_metrocluster`,`s`.`svc_vcpus` AS `svc_vcpus`,`s`.`svc_vmem` AS `svc_vmem`,`m`.`mon_svcname` AS `mon_svcname`,`m`.`mon_svctype` AS `mon_svctype`,`m`.`mon_drptype` AS `mon_drptype`,`m`.`mon_nodname` AS `mon_nodname`,`m`.`mon_nodtype` AS `mon_nodtype`,`m`.`mon_nodmode` AS `mon_nodmode`,`m`.`mon_ipstatus` AS `mon_ipstatus`,`m`.`mon_fsstatus` AS `mon_fsstatus`,`m`.`mon_prinodes` AS `mon_prinodes`,`m`.`mon_hostid` AS `mon_hostid`,`m`.`ID` AS `ID`,`m`.`mon_frozen` AS `mon_frozen`,`m`.`mon_frozentxt` AS `mon_frozentxt`,`m`.`mon_changed` AS `mon_changed`,`m`.`mon_updated` AS `mon_updated`,`m`.`mon_diskstatus` AS `mon_diskstatus`,`m`.`mon_containerstatus` AS `mon_containerstatus`,`m`.`mon_overallstatus` AS `mon_overallstatus`,`n`.`nodename` AS `nodename`,`n`.`updated` AS `node_updated`,`n`.`loc_country` AS `loc_country`,`n`.`loc_city` AS `loc_city`,`n`.`loc_addr` AS `loc_addr`,`n`.`loc_building` AS `loc_building`,`n`.`loc_floor` AS `loc_floor`,`n`.`loc_room` AS `loc_room`,`n`.`loc_rack` AS `loc_rack`,`n`.`cpu_freq` AS `cpu_freq`,`n`.`cpu_cores` AS `cpu_cores`,`n`.`cpu_dies` AS `cpu_dies`,`n`.`cpu_vendor` AS `cpu_vendor`,`n`.`cpu_model` AS `cpu_model`,`n`.`mem_banks` AS `mem_banks`,`n`.`mem_slots` AS `mem_slots`,`n`.`mem_bytes` AS `mem_bytes`,`n`.`os_name` AS `os_name`,`n`.`os_release` AS `os_release`,`n`.`os_update` AS `os_update`,`n`.`os_segment` AS `os_segment`,`n`.`os_arch` AS `os_arch`,`n`.`os_vendor` AS `os_vendor`,`n`.`os_kernel` AS `os_kernel`,`n`.`loc_zip` AS `loc_zip`,`n`.`team_responsible` AS `team_responsible`, n.team_integ as team_integ, n.project as project, `n`.`serial` AS `serial`,`n`.`model` AS `model`,`n`.`type` AS `type`,`n`.`warranty_end` AS `warranty_end`,`n`.`status` AS `status`,`n`.`role` AS `role`,`n`.`environnement` AS `environnement`,`n`.`power_supply_nb` AS `power_supply_nb`,`n`.`power_cabinet1` AS `power_cabinet1`,`n`.`power_cabinet2` AS `power_cabinet2`,`n`.`power_protect` AS `power_protect`,`n`.`power_protect_breaker` AS `power_protect_breaker`,`n`.`power_breaker1` AS `power_breaker1`,`n`.`power_breaker2` AS `power_breaker2`,`m`.`mon_syncstatus` AS `mon_syncstatus`,`m`.`mon_hbstatus` AS `mon_hbstatus`,`m`.`mon_availstatus` AS `mon_availstatus`,`m`.`mon_appstatus` AS `mon_appstatus`,`ap`.`responsibles` AS `responsibles`,`ap`.`mailto` AS `mailto` from ((((`svcmon` `m` left join `services` `s` on((`s`.`svc_name` = `m`.`mon_svcname`))) left join `nodes` `n` on((convert(`m`.`mon_nodname` using utf8) = `n`.`nodename`))) left join `b_apps` `ap` on((`ap`.`app` = `s`.`svc_app`))) left join `b_action_errors` `e` on(((`e`.`svcname` = convert(`s`.`svc_name` using utf8)) and (`e`.`nodename` = convert(`m`.`mon_nodname` using utf8)))));

drop view v_svcactions;

CREATE VIEW `v_svcactions` AS select `ac`.`cron` AS `cron`,`ac`.`time` AS `time`,`ac`.`version` AS `version`,`ac`.`svcname` AS `svcname`,`ac`.`action` AS `action`,`ac`.`status` AS `status`,`ac`.`begin` AS `begin`,`ac`.`end` AS `end`,`ac`.`hostname` AS `hostname`,`ac`.`hostid` AS `hostid`,`ac`.`status_log` AS `status_log`,`ac`.`pid` AS `pid`,`ac`.`ID` AS `ID`,`ac`.`ack` AS `ack`,`ac`.`alert` AS `alert`,`ac`.`acked_by` AS `acked_by`,`ac`.`acked_comment` AS `acked_comment`,`ac`.`acked_date` AS `acked_date`,`s`.`svc_ha` AS `svc_ha`,`s`.`svc_app` AS `app`,`a`.`mailto` AS `mailto`,`a`.`responsibles` AS `responsibles`,`n`.`nodename` AS `nodename`,`n`.`loc_country` AS `loc_country`,`n`.`loc_city` AS `loc_city`,`n`.`loc_addr` AS `loc_addr`,`n`.`loc_building` AS `loc_building`,`n`.`loc_floor` AS `loc_floor`,`n`.`loc_room` AS `loc_room`,`n`.`loc_rack` AS `loc_rack`,`n`.`cpu_freq` AS `cpu_freq`,`n`.`cpu_cores` AS `cpu_cores`,`n`.`cpu_dies` AS `cpu_dies`,`n`.`cpu_vendor` AS `cpu_vendor`,`n`.`cpu_model` AS `cpu_model`,`n`.`mem_banks` AS `mem_banks`,`n`.`mem_slots` AS `mem_slots`,`n`.`mem_bytes` AS `mem_bytes`,`n`.`os_name` AS `os_name`,`n`.`os_release` AS `os_release`,`n`.`os_update` AS `os_update`,`n`.`os_segment` AS `os_segment`,`n`.`os_arch` AS `os_arch`,`n`.`os_vendor` AS `os_vendor`,`n`.`os_kernel` AS `os_kernel`,`n`.`loc_zip` AS `loc_zip`,`n`.`team_responsible` AS `team_responsible`, n.team_integ as team_integ, n.project as project, `n`.`serial` AS `serial`,`n`.`model` AS `model`,`n`.`type` AS `type`,`n`.`warranty_end` AS `warranty_end`,`n`.`status` AS `asset_status`,`n`.`role` AS `role`,`n`.`environnement` AS `environnement`,`n`.`power_supply_nb` AS `power_supply_nb`,`n`.`power_cabinet1` AS `power_cabinet1`,`n`.`power_cabinet2` AS `power_cabinet2`,`n`.`power_protect` AS `power_protect`,`n`.`power_protect_breaker` AS `power_protect_breaker`,`n`.`power_breaker1` AS `power_breaker1`,`n`.`power_breaker2` AS `power_breaker2` from (((`SVCactions` `ac` join `services` `s` on((`s`.`svc_name` = `ac`.`svcname`))) join `nodes` `n` on((`ac`.`hostname` = `n`.`nodename`))) join `b_apps` `a` on((`a`.`app` = `s`.`svc_app`)));


alter table stats_netdev_err add key stats_netdev_err_k1 (nodename);
alter table stats_netdev_err add key stats_netdev_err_k2 (date);

drop view v_comp_nodes;

create view v_comp_nodes as (select n.*,group_concat(distinct r.ruleset_name separator ', ') as rulesets, group_concat(distinct m.modset_name separator ', ') as modulesets from v_nodes n left join comp_rulesets_nodes rn on n.nodename=rn.nodename left join comp_rulesets r on r.id=rn.ruleset_id left join comp_node_moduleset mn on mn.modset_node=n.nodename left join comp_moduleset m on m.id=mn.modset_id group by n.nodename);

alter table nodes modify model varchar(50);

alter table stat_day add column nb_vcpu int(11) default 0;
alter table stat_day add column nb_vmem int(11) default 0;
alter table stat_day add column nb_resp_accounts int(11) default 0;

alter table auth_user add column lock_filter varchar(1) default 'F';

drop view v_users;

CREATE VIEW `v_users` AS (select (select `e`.`time_stamp` AS `time_stamp` from `auth_event` `e` where (`e`.`user_id` = `u`.`id`) order by `e`.`time_stamp` desc limit 1) AS `last`,`u`.`id` AS `id`,concat_ws(' ',`u`.`first_name`,`u`.`last_name`) AS `fullname`,`u`.`email` AS `email`,group_concat(`d`.`domains` separator ', ') AS `domains`,sum((select count(0) AS `count(*)` from `auth_group` `gg` where ((`gg`.`role` = 'Manager') and (`gg`.`id` = `g`.`id`)))) AS `manager`,group_concat(`g`.`role` separator ', ') AS `groups`, u.lock_filter as lock_filter, fs.fset_name as fset_name from (((`auth_user` `u` left join `auth_membership` `m` on((`u`.`id` = `m`.`user_id`))) left join `auth_group` `g` on(((`m`.`group_id` = `g`.`id`) and (not((`g`.`role` like 'user_%')))))) left join `domain_permissions` `d` on((`m`.`group_id` = `d`.`group_id`))) left join gen_filterset_user fsu on fsu.user_id = u.id left join gen_filtersets fs on fs.id = fsu.fset_id group by id);

alter table stat_day add column nb_virt_nodes int(11) default 0;

CREATE TABLE  `opensvc`.`stats_compare` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(60) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB CHARSET=utf8;

CREATE TABLE  `opensvc`.`stats_compare_fset` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `compare_id` int(11) NOT NULL,
  `fset_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY stats_compare_fset_uk1 (`compare_id`, fset_id)
) ENGINE=InnoDB CHARSET=utf8;

alter table stats_compare_fset add CONSTRAINT `stats_compare_fset_ibfk_1` FOREIGN KEY (`fset_id`) REFERENCES `gen_filtersets` (`id`) ON DELETE CASCADE;
alter table stats_compare_fset add CONSTRAINT `stats_compare_fset_ibfk_2` FOREIGN KEY (`compare_id`) REFERENCES `stats_compare` (`id`) ON DELETE CASCADE;

CREATE TABLE  `opensvc`.`stats_compare_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `compare_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY stats_compare_user_uk1 (`compare_id`, user_id)
) ENGINE=InnoDB CHARSET=utf8;

alter table stats_compare_user add CONSTRAINT `stats_compare_user_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`) ON DELETE CASCADE;
alter table stats_compare_user add CONSTRAINT `stats_compare_user_ibfk_2` FOREIGN KEY (`compare_id`) REFERENCES `stats_compare` (`id`) ON DELETE CASCADE;


alter table svcdisks engine=InnoDB;
alter table svcdisks charset=utf8;
alter table svcdisks modify column disk_svcname varchar(60) CHARACTER SET utf8;
alter table svcdisks modify column disk_nodename varchar(60) CHARACTER SET utf8;
alter table svcdisks modify column disk_id varchar(60) CHARACTER SET utf8;
alter table svcdisks modify column disk_vendor varchar(60) CHARACTER SET utf8;
alter table svcdisks modify column disk_model varchar(60) CHARACTER SET utf8;
alter table svcdisks modify column disk_dg varchar(60) CHARACTER SET utf8;
alter table svcdisks modify column disk_target_port_id varchar(60) CHARACTER SET utf8;
alter table svcmon add key svcmon_k1 (disk_nodename, disk_svcname);
alter table svcdisks add key svcdisks_k1 (mon_nodname, mon_svcname);
alter table svcdisks add CONSTRAINT `svcdisks_ibfk_1` FOREIGN KEY (disk_nodename, disk_svcname) REFERENCES `svcmon` (mon_nodname, mon_svcname) ON DELETE CASCADE;


# zstat format
# datenow, z, stor[z]['SWAP'], stor[z]['RSS'], stor[z]['CAP'], stor[z]['at'], stor[z]['avgat'], stor[z]['pg'], stor[z]['avgpg'], stor[z]['NPROC'], stor[z]['mem'], stor[z]['cpu'], stor[z]['TIME'], txt[-3], txt[-2], txt[-1]
# 2011-12-31 16:24:00 v11z5 29M 35M 0 0 0 0 0 22 2.3% 0.0% 0:06:57 Nov 9 21:47

CREATE TABLE `stats_svc` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `date` datetime NOT NULL,
  `svcname` varchar(60) NOT NULL,
  `swap` integer NOT NULL,
  `rss` integer NOT NULL,
  `cap` float NOT NULL,
  `at` float NOT NULL,
  `avgat` float NOT NULL,
  `pg` float NOT NULL,
  `avgpg` float NOT NULL,
  `nproc` float NOT NULL,
  `mem` float NOT NULL,
  `cpu` float NOT NULL,
  `nodename` varchar(60) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `index_1` (`date`,`svcname`,`nodename`)
);

alter table svcdisks modify column disk_id varchar(120);

alter table stat_day add column local_disk_size int(11) NOT NULL default 0;

alter table stat_day_svc add column local_disk_size int(11) NOT NULL default 0;

alter table svcdisks add column disk_local varchar(1) default 'T';

alter table stat_day_svc modify column local_disk_size int(11) DEFAULT '0';

update stat_day_svc set disk_size = 0 where disk_size is NULL;

update stat_day_svc set local_disk_size = 0 where local_disk_size is NULL;


CREATE TABLE `node_hba` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `updated` datetime NOT NULL,
  `nodename` varchar(60) NOT NULL,
  `hba_id` varchar(60) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `index_1` (`nodename`,`hba_id`)
);

alter table node_hba ADD CONSTRAINT node_hba_fk1 FOREIGN KEY (nodename) REFERENCES nodes(nodename) ON DELETE CASCADE;


alter table nodes add column team_support varchar(20);

drop view v_nodes;

CREATE VIEW `v_nodes` AS (select `n`.`nodename` AS `nodename`,`n`.`loc_country` AS `loc_country`,`n`.`loc_city` AS `loc_city`,`n`.`loc_addr` AS `loc_addr`,`n`.`loc_building` AS `loc_building`,`n`.`loc_floor` AS `loc_floor`,`n`.`loc_room` AS `loc_room`,`n`.`loc_rack` AS `loc_rack`,`n`.`id` AS `id`,`n`.`cpu_freq` AS `cpu_freq`,`n`.`cpu_cores` AS `cpu_cores`,`n`.`cpu_dies` AS `cpu_dies`,`n`.`cpu_vendor` AS `cpu_vendor`,`n`.`cpu_model` AS `cpu_model`,`n`.`mem_banks` AS `mem_banks`,`n`.`mem_slots` AS `mem_slots`,`n`.`mem_bytes` AS `mem_bytes`,`n`.`os_name` AS `os_name`,`n`.`os_release` AS `os_release`,`n`.`os_update` AS `os_update`,`n`.`os_segment` AS `os_segment`,`n`.`os_arch` AS `os_arch`,`n`.`os_vendor` AS `os_vendor`,`n`.`os_kernel` AS `os_kernel`,`n`.`loc_zip` AS `loc_zip`,`n`.`team_responsible` AS `team_responsible`, n.team_integ as team_integ, n.team_support as team_support, n.project as project, `n`.`serial` AS `serial`,`n`.`model` AS `model`,`n`.`type` AS `type`,`n`.`warranty_end` AS `warranty_end`,`n`.`status` AS `status`,`n`.`role` AS `role`,`n`.`environnement` AS `environnement`,`n`.`power_cabinet1` AS `power_cabinet1`,`n`.`power_cabinet2` AS `power_cabinet2`,`n`.`power_supply_nb` AS `power_supply_nb`,`n`.`power_protect` AS `power_protect`,`n`.`power_protect_breaker` AS `power_protect_breaker`,`n`.`power_breaker1` AS `power_breaker1`,`n`.`power_breaker2` AS `power_breaker2`,concat_ws(' ',`n`.`os_name`,`n`.`os_vendor`,`n`.`os_release`,`n`.`os_update`) AS `os_concat`,`n`.`updated` AS `updated` from `nodes` `n`);

drop view v_svcmon;

CREATE VIEW `v_svcmon` AS select `e`.`err` AS `err`,`s`.`svc_ha` AS `svc_ha`,`s`.`svc_cluster_type` AS `svc_cluster_type`,`s`.`svc_status` AS `svc_status`,`s`.`svc_availstatus` AS `svc_availstatus`,`s`.`svc_flex_min_nodes` AS `svc_flex_min_nodes`,`s`.`svc_flex_max_nodes` AS `svc_flex_max_nodes`,`s`.`svc_flex_cpu_low_threshold` AS `svc_flex_cpu_low_threshold`,`s`.`svc_flex_cpu_high_threshold` AS `svc_flex_cpu_high_threshold`,`s`.`svc_vmname` AS `svc_vmname`,`s`.`svc_guestos` AS `svc_guestos`,`s`.`svc_version` AS `svc_version`,`s`.`svc_name` AS `svc_name`,`s`.`svc_nodes` AS `svc_nodes`,`s`.`svc_drpnode` AS `svc_drpnode`,`s`.`svc_drpnodes` AS `svc_drpnodes`,`s`.`svc_drptype` AS `svc_drptype`,`s`.`svc_autostart` AS `svc_autostart`,`s`.`svc_type` AS `svc_type`,`s`.`svc_comment` AS `svc_comment`,`s`.`svc_app` AS `svc_app`,`s`.`svc_drnoaction` AS `svc_drnoaction`,`s`.`svc_created` AS `svc_created`,`s`.`updated` AS `svc_updated`,`s`.`svc_envdate` AS `svc_envdate`,`s`.`svc_containertype` AS `svc_containertype`,`s`.`svc_metrocluster` AS `svc_metrocluster`,`s`.`svc_vcpus` AS `svc_vcpus`,`s`.`svc_vmem` AS `svc_vmem`,`m`.`mon_svcname` AS `mon_svcname`,`m`.`mon_svctype` AS `mon_svctype`,`m`.`mon_drptype` AS `mon_drptype`,`m`.`mon_nodname` AS `mon_nodname`,`m`.`mon_nodtype` AS `mon_nodtype`,`m`.`mon_nodmode` AS `mon_nodmode`,`m`.`mon_ipstatus` AS `mon_ipstatus`,`m`.`mon_fsstatus` AS `mon_fsstatus`,`m`.`mon_prinodes` AS `mon_prinodes`,`m`.`mon_hostid` AS `mon_hostid`,`m`.`ID` AS `ID`,`m`.`mon_frozen` AS `mon_frozen`,`m`.`mon_frozentxt` AS `mon_frozentxt`,`m`.`mon_changed` AS `mon_changed`,`m`.`mon_updated` AS `mon_updated`,`m`.`mon_diskstatus` AS `mon_diskstatus`,`m`.`mon_containerstatus` AS `mon_containerstatus`,`m`.`mon_overallstatus` AS `mon_overallstatus`,`n`.`nodename` AS `nodename`,`n`.`updated` AS `node_updated`,`n`.`loc_country` AS `loc_country`,`n`.`loc_city` AS `loc_city`,`n`.`loc_addr` AS `loc_addr`,`n`.`loc_building` AS `loc_building`,`n`.`loc_floor` AS `loc_floor`,`n`.`loc_room` AS `loc_room`,`n`.`loc_rack` AS `loc_rack`,`n`.`cpu_freq` AS `cpu_freq`,`n`.`cpu_cores` AS `cpu_cores`,`n`.`cpu_dies` AS `cpu_dies`,`n`.`cpu_vendor` AS `cpu_vendor`,`n`.`cpu_model` AS `cpu_model`,`n`.`mem_banks` AS `mem_banks`,`n`.`mem_slots` AS `mem_slots`,`n`.`mem_bytes` AS `mem_bytes`,`n`.`os_name` AS `os_name`,`n`.`os_release` AS `os_release`,`n`.`os_update` AS `os_update`,`n`.`os_segment` AS `os_segment`,`n`.`os_arch` AS `os_arch`,`n`.`os_vendor` AS `os_vendor`,`n`.`os_kernel` AS `os_kernel`,`n`.`loc_zip` AS `loc_zip`,`n`.`team_responsible` AS `team_responsible`, n.team_integ as team_integ, n.team_support as team_support, n.project as project, `n`.`serial` AS `serial`,`n`.`model` AS `model`,`n`.`type` AS `type`,`n`.`warranty_end` AS `warranty_end`,`n`.`status` AS `status`,`n`.`role` AS `role`,`n`.`environnement` AS `environnement`,`n`.`power_supply_nb` AS `power_supply_nb`,`n`.`power_cabinet1` AS `power_cabinet1`,`n`.`power_cabinet2` AS `power_cabinet2`,`n`.`power_protect` AS `power_protect`,`n`.`power_protect_breaker` AS `power_protect_breaker`,`n`.`power_breaker1` AS `power_breaker1`,`n`.`power_breaker2` AS `power_breaker2`,`m`.`mon_syncstatus` AS `mon_syncstatus`,`m`.`mon_hbstatus` AS `mon_hbstatus`,`m`.`mon_availstatus` AS `mon_availstatus`,`m`.`mon_appstatus` AS `mon_appstatus`,`ap`.`responsibles` AS `responsibles`,`ap`.`mailto` AS `mailto` from ((((`svcmon` `m` left join `services` `s` on((`s`.`svc_name` = `m`.`mon_svcname`))) left join `nodes` `n` on((convert(`m`.`mon_nodname` using utf8) = `n`.`nodename`))) left join `b_apps` `ap` on((`ap`.`app` = `s`.`svc_app`))) left join `b_action_errors` `e` on(((`e`.`svcname` = convert(`s`.`svc_name` using utf8)) and (`e`.`nodename` = convert(`m`.`mon_nodname` using utf8)))));

drop view v_svcactions;

CREATE VIEW `v_svcactions` AS select `ac`.`cron` AS `cron`,`ac`.`time` AS `time`,`ac`.`version` AS `version`,`ac`.`svcname` AS `svcname`,`ac`.`action` AS `action`,`ac`.`status` AS `status`,`ac`.`begin` AS `begin`,`ac`.`end` AS `end`,`ac`.`hostname` AS `hostname`,`ac`.`hostid` AS `hostid`,`ac`.`status_log` AS `status_log`,`ac`.`pid` AS `pid`,`ac`.`ID` AS `ID`,`ac`.`ack` AS `ack`,`ac`.`alert` AS `alert`,`ac`.`acked_by` AS `acked_by`,`ac`.`acked_comment` AS `acked_comment`,`ac`.`acked_date` AS `acked_date`,`s`.`svc_ha` AS `svc_ha`,`s`.`svc_app` AS `app`,`a`.`mailto` AS `mailto`,`a`.`responsibles` AS `responsibles`,`n`.`nodename` AS `nodename`,`n`.`loc_country` AS `loc_country`,`n`.`loc_city` AS `loc_city`,`n`.`loc_addr` AS `loc_addr`,`n`.`loc_building` AS `loc_building`,`n`.`loc_floor` AS `loc_floor`,`n`.`loc_room` AS `loc_room`,`n`.`loc_rack` AS `loc_rack`,`n`.`cpu_freq` AS `cpu_freq`,`n`.`cpu_cores` AS `cpu_cores`,`n`.`cpu_dies` AS `cpu_dies`,`n`.`cpu_vendor` AS `cpu_vendor`,`n`.`cpu_model` AS `cpu_model`,`n`.`mem_banks` AS `mem_banks`,`n`.`mem_slots` AS `mem_slots`,`n`.`mem_bytes` AS `mem_bytes`,`n`.`os_name` AS `os_name`,`n`.`os_release` AS `os_release`,`n`.`os_update` AS `os_update`,`n`.`os_segment` AS `os_segment`,`n`.`os_arch` AS `os_arch`,`n`.`os_vendor` AS `os_vendor`,`n`.`os_kernel` AS `os_kernel`,`n`.`loc_zip` AS `loc_zip`,`n`.`team_responsible` AS `team_responsible`, n.team_integ as team_integ, n.team_support as team_support, n.project as project, `n`.`serial` AS `serial`,`n`.`model` AS `model`,`n`.`type` AS `type`,`n`.`warranty_end` AS `warranty_end`,`n`.`status` AS `asset_status`,`n`.`role` AS `role`,`n`.`environnement` AS `environnement`,`n`.`power_supply_nb` AS `power_supply_nb`,`n`.`power_cabinet1` AS `power_cabinet1`,`n`.`power_cabinet2` AS `power_cabinet2`,`n`.`power_protect` AS `power_protect`,`n`.`power_protect_breaker` AS `power_protect_breaker`,`n`.`power_breaker1` AS `power_breaker1`,`n`.`power_breaker2` AS `power_breaker2` from (((`SVCactions` `ac` join `services` `s` on((`s`.`svc_name` = `ac`.`svcname`))) join `nodes` `n` on((`ac`.`hostname` = `n`.`nodename`))) join `b_apps` `a` on((`a`.`app` = `s`.`svc_app`)));

alter table node_hba add column hba_type varchar(5);

CREATE TABLE `stor_array` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `array_name` varchar(60) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `index_1` (`array_name`)
);

CREATE TABLE `stor_array_proxy` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `array_id` int(11) NOT NULL,
  `nodename` varchar(60) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `index_1` (`array_id`, `nodename`)
);

alter table stor_array_proxy add CONSTRAINT `stor_array_proxy_ibfk_1` FOREIGN KEY (`array_id`) REFERENCES `stor_array` (`id`) ON DELETE CASCADE;

CREATE TABLE `stor_pool` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `pool_name` varchar(60) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `index_1` (`pool_id`)
);

CREATE TABLE `stor_array_tgtid` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `array_id` varchar(60) NOT NULL,
  `array_tgtid` varchar(60) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `index_1` (`array_id`, `array_tgtid`)
);

alter table stor_array_tgtid add CONSTRAINT `stor_array_tgtid_ibfk_1` FOREIGN KEY (`array_id`) REFERENCES `stor_array` (`id`) ON DELETE CASCADE;

CREATE TABLE `stor_array_dg` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `array_id` varchar(60) NOT NULL,
  `dg_name` varchar(60) NOT NULL,
  `dg_free` integer NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `index_1` (`array_id`, `dg_name`)
);

alter table stor_array_dg add CONSTRAINT `stor_array_dg_ibfk_1` FOREIGN KEY (`array_id`) REFERENCES `stor_array` (`id`) ON DELETE CASCADE;

CREATE TABLE `stor_array_dg_quota` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `dg_id` int(11) NOT NULL,
  `app_id` int(11) NOT NULL,
  `quota` integer,
  PRIMARY KEY (`id`),
  UNIQUE KEY `index_1` (`dg_id`, `app_id`)
);

alter table stor_array_dg_quota add CONSTRAINT `stor_array_dg_quota_ibfk_1` FOREIGN KEY (`dg_id`) REFERENCES `stor_array_dg` (`id`) ON DELETE CASCADE;
alter table stor_array_dg_quota add CONSTRAINT `stor_array_dg_quota_ibfk_2` FOREIGN KEY (`app_id`) REFERENCES `apps` (`id`) ON DELETE CASCADE;

CREATE TABLE `stor_zone` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tgt_id` varchar(60) NOT NULL,
  `hba_id` varchar(60) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `index_1` (`tgt_id`, `hba_id`)
);

alter table stor_array add column array_model varchar(30) not null;

alter table stor_zone add column nodename varchar(60);
alter table stor_zone add column updated timestamp;

alter table stor_array add column array_cache integer;
alter table stor_array add column array_firmware varchar(60);
alter table stor_array add column array_updated timestamp;

alter table stor_array_dg add column dg_updated timestamp;

alter table diskinfo add column disk_raid varchar(16);
alter table diskinfo add column disk_size integer;
alter table diskinfo add column disk_group varchar(60);

alter table svcdisks drop column disk_target_port_id;

alter table stor_array_dg add column dg_size int(11);
alter table stor_array_dg add column dg_used int(11);

drop view v_comp_nodes;

create view v_comp_nodes as (select n.*,group_concat(distinct r.ruleset_name separator ', ') as rulesets, group_concat(distinct m.modset_name separator ', ') as modulesets from v_nodes n left join comp_rulesets_nodes rn on n.nodename=rn.nodename left join comp_rulesets r on r.id=rn.ruleset_id left join comp_node_moduleset mn on mn.modset_node=n.nodename left join comp_moduleset m on m.id=mn.modset_id group by n.nodename);

# add host_mode column

alter table nodes add column host_mode varchar(6) not null default "TST";

drop view v_nodes;

CREATE VIEW `v_nodes` AS (select `n`.`nodename` AS `nodename`,`n`.`loc_country` AS `loc_country`,`n`.`loc_city` AS `loc_city`,`n`.`loc_addr` AS `loc_addr`,`n`.`loc_building` AS `loc_building`,`n`.`loc_floor` AS `loc_floor`,`n`.`loc_room` AS `loc_room`,`n`.`loc_rack` AS `loc_rack`,`n`.`id` AS `id`,`n`.`cpu_freq` AS `cpu_freq`,`n`.`cpu_cores` AS `cpu_cores`,`n`.`cpu_dies` AS `cpu_dies`,`n`.`cpu_vendor` AS `cpu_vendor`,`n`.`cpu_model` AS `cpu_model`,`n`.`mem_banks` AS `mem_banks`,`n`.`mem_slots` AS `mem_slots`,`n`.`mem_bytes` AS `mem_bytes`,`n`.`os_name` AS `os_name`,`n`.`os_release` AS `os_release`,`n`.`os_update` AS `os_update`,`n`.`os_segment` AS `os_segment`,`n`.`os_arch` AS `os_arch`,`n`.`os_vendor` AS `os_vendor`,`n`.`os_kernel` AS `os_kernel`,`n`.`loc_zip` AS `loc_zip`,`n`.`team_responsible` AS `team_responsible`, n.team_integ as team_integ, n.team_support as team_support, n.project as project, `n`.`serial` AS `serial`,`n`.`model` AS `model`,`n`.`type` AS `type`,`n`.`warranty_end` AS `warranty_end`,`n`.`status` AS `status`,`n`.`role` AS `role`,`n`.`environnement` AS `environnement`,n.host_mode as host_mode, `n`.`power_cabinet1` AS `power_cabinet1`,`n`.`power_cabinet2` AS `power_cabinet2`,`n`.`power_supply_nb` AS `power_supply_nb`,`n`.`power_protect` AS `power_protect`,`n`.`power_protect_breaker` AS `power_protect_breaker`,`n`.`power_breaker1` AS `power_breaker1`,`n`.`power_breaker2` AS `power_breaker2`,concat_ws(' ',`n`.`os_name`,`n`.`os_vendor`,`n`.`os_release`,`n`.`os_update`) AS `os_concat`,`n`.`updated` AS `updated` from `nodes` `n`);
drop view v_svcmon;

CREATE VIEW `v_svcmon` AS select `e`.`err` AS `err`,`s`.`svc_ha` AS `svc_ha`,`s`.`svc_cluster_type` AS `svc_cluster_type`,`s`.`svc_status` AS `svc_status`,`s`.`svc_availstatus` AS `svc_availstatus`,`s`.`svc_flex_min_nodes` AS `svc_flex_min_nodes`,`s`.`svc_flex_max_nodes` AS `svc_flex_max_nodes`,`s`.`svc_flex_cpu_low_threshold` AS `svc_flex_cpu_low_threshold`,`s`.`svc_flex_cpu_high_threshold` AS `svc_flex_cpu_high_threshold`,`s`.`svc_vmname` AS `svc_vmname`,`s`.`svc_guestos` AS `svc_guestos`,`s`.`svc_version` AS `svc_version`,`s`.`svc_name` AS `svc_name`,`s`.`svc_nodes` AS `svc_nodes`,`s`.`svc_drpnode` AS `svc_drpnode`,`s`.`svc_drpnodes` AS `svc_drpnodes`,`s`.`svc_drptype` AS `svc_drptype`,`s`.`svc_autostart` AS `svc_autostart`,`s`.`svc_type` AS `svc_type`,`s`.`svc_comment` AS `svc_comment`,`s`.`svc_app` AS `svc_app`,`s`.`svc_drnoaction` AS `svc_drnoaction`,`s`.`svc_created` AS `svc_created`,`s`.`updated` AS `svc_updated`,`s`.`svc_envdate` AS `svc_envdate`,`s`.`svc_containertype` AS `svc_containertype`,`s`.`svc_metrocluster` AS `svc_metrocluster`,`s`.`svc_vcpus` AS `svc_vcpus`,`s`.`svc_vmem` AS `svc_vmem`,`m`.`mon_svcname` AS `mon_svcname`,`m`.`mon_svctype` AS `mon_svctype`,`m`.`mon_drptype` AS `mon_drptype`,`m`.`mon_nodname` AS `mon_nodname`,`m`.`mon_nodtype` AS `mon_nodtype`,`m`.`mon_nodmode` AS `mon_nodmode`,`m`.`mon_ipstatus` AS `mon_ipstatus`,`m`.`mon_fsstatus` AS `mon_fsstatus`,`m`.`mon_prinodes` AS `mon_prinodes`,`m`.`mon_hostid` AS `mon_hostid`,`m`.`ID` AS `ID`,`m`.`mon_frozen` AS `mon_frozen`,`m`.`mon_frozentxt` AS `mon_frozentxt`,`m`.`mon_changed` AS `mon_changed`,`m`.`mon_updated` AS `mon_updated`,`m`.`mon_diskstatus` AS `mon_diskstatus`,`m`.`mon_containerstatus` AS `mon_containerstatus`,`m`.`mon_overallstatus` AS `mon_overallstatus`,`n`.`nodename` AS `nodename`,`n`.`updated` AS `node_updated`,`n`.`loc_country` AS `loc_country`,`n`.`loc_city` AS `loc_city`,`n`.`loc_addr` AS `loc_addr`,`n`.`loc_building` AS `loc_building`,`n`.`loc_floor` AS `loc_floor`,`n`.`loc_room` AS `loc_room`,`n`.`loc_rack` AS `loc_rack`,`n`.`cpu_freq` AS `cpu_freq`,`n`.`cpu_cores` AS `cpu_cores`,`n`.`cpu_dies` AS `cpu_dies`,`n`.`cpu_vendor` AS `cpu_vendor`,`n`.`cpu_model` AS `cpu_model`,`n`.`mem_banks` AS `mem_banks`,`n`.`mem_slots` AS `mem_slots`,`n`.`mem_bytes` AS `mem_bytes`,`n`.`os_name` AS `os_name`,`n`.`os_release` AS `os_release`,`n`.`os_update` AS `os_update`,`n`.`os_segment` AS `os_segment`,`n`.`os_arch` AS `os_arch`,`n`.`os_vendor` AS `os_vendor`,`n`.`os_kernel` AS `os_kernel`,`n`.`loc_zip` AS `loc_zip`,`n`.`team_responsible` AS `team_responsible`, n.team_integ as team_integ, n.team_support as team_support, n.project as project, `n`.`serial` AS `serial`,`n`.`model` AS `model`,`n`.`type` AS `type`,`n`.`warranty_end` AS `warranty_end`,`n`.`status` AS `status`,`n`.`role` AS `role`,`n`.`environnement` AS `environnement`,n.host_mode as host_mode,`n`.`power_supply_nb` AS `power_supply_nb`,`n`.`power_cabinet1` AS `power_cabinet1`,`n`.`power_cabinet2` AS `power_cabinet2`,`n`.`power_protect` AS `power_protect`,`n`.`power_protect_breaker` AS `power_protect_breaker`,`n`.`power_breaker1` AS `power_breaker1`,`n`.`power_breaker2` AS `power_breaker2`,`m`.`mon_syncstatus` AS `mon_syncstatus`,`m`.`mon_hbstatus` AS `mon_hbstatus`,`m`.`mon_availstatus` AS `mon_availstatus`,`m`.`mon_appstatus` AS `mon_appstatus`,`ap`.`responsibles` AS `responsibles`,`ap`.`mailto` AS `mailto` from ((((`svcmon` `m` left join `services` `s` on((`s`.`svc_name` = `m`.`mon_svcname`))) left join `nodes` `n` on((convert(`m`.`mon_nodname` using utf8) = `n`.`nodename`))) left join `b_apps` `ap` on((`ap`.`app` = `s`.`svc_app`))) left join `b_action_errors` `e` on(((`e`.`svcname` = convert(`s`.`svc_name` using utf8)) and (`e`.`nodename` = convert(`m`.`mon_nodname` using utf8)))));
drop view v_svcactions;

CREATE VIEW `v_svcactions` AS select `ac`.`cron` AS `cron`,`ac`.`time` AS `time`,`ac`.`version` AS `version`,`ac`.`svcname` AS `svcname`,`ac`.`action` AS `action`,`ac`.`status` AS `status`,`ac`.`begin` AS `begin`,`ac`.`end` AS `end`,`ac`.`hostname` AS `hostname`,`ac`.`hostid` AS `hostid`,`ac`.`status_log` AS `status_log`,`ac`.`pid` AS `pid`,`ac`.`ID` AS `ID`,`ac`.`ack` AS `ack`,`ac`.`alert` AS `alert`,`ac`.`acked_by` AS `acked_by`,`ac`.`acked_comment` AS `acked_comment`,`ac`.`acked_date` AS `acked_date`,`s`.`svc_ha` AS `svc_ha`,`s`.`svc_app` AS `app`,`a`.`mailto` AS `mailto`,`a`.`responsibles` AS `responsibles`,`n`.`nodename` AS `nodename`,`n`.`loc_country` AS `loc_country`,`n`.`loc_city` AS `loc_city`,`n`.`loc_addr` AS `loc_addr`,`n`.`loc_building` AS `loc_building`,`n`.`loc_floor` AS `loc_floor`,`n`.`loc_room` AS `loc_room`,`n`.`loc_rack` AS `loc_rack`,`n`.`cpu_freq` AS `cpu_freq`,`n`.`cpu_cores` AS `cpu_cores`,`n`.`cpu_dies` AS `cpu_dies`,`n`.`cpu_vendor` AS `cpu_vendor`,`n`.`cpu_model` AS `cpu_model`,`n`.`mem_banks` AS `mem_banks`,`n`.`mem_slots` AS `mem_slots`,`n`.`mem_bytes` AS `mem_bytes`,`n`.`os_name` AS `os_name`,`n`.`os_release` AS `os_release`,`n`.`os_update` AS `os_update`,`n`.`os_segment` AS `os_segment`,`n`.`os_arch` AS `os_arch`,`n`.`os_vendor` AS `os_vendor`,`n`.`os_kernel` AS `os_kernel`,`n`.`loc_zip` AS `loc_zip`,`n`.`team_responsible` AS `team_responsible`, n.team_integ as team_integ, n.team_support as team_support, n.project as project, `n`.`serial` AS `serial`,`n`.`model` AS `model`,`n`.`type` AS `type`,`n`.`warranty_end` AS `warranty_end`,`n`.`status` AS `asset_status`,`n`.`role` AS `role`,`n`.`environnement` AS `environnement`, n.host_mode AS host_mode, `n`.`power_supply_nb` AS `power_supply_nb`,`n`.`power_cabinet1` AS `power_cabinet1`,`n`.`power_cabinet2` AS `power_cabinet2`,`n`.`power_protect` AS `power_protect`,`n`.`power_protect_breaker` AS `power_protect_breaker`,`n`.`power_breaker1` AS `power_breaker1`,`n`.`power_breaker2` AS `power_breaker2` from (((`SVCactions` `ac` join `services` `s` on((`s`.`svc_name` = `ac`.`svcname`))) join `nodes` `n` on((`ac`.`hostname` = `n`.`nodename`))) join `b_apps` `a` on((`a`.`app` = `s`.`svc_app`)));

drop view v_comp_nodes;

create view v_comp_nodes as (select n.*,group_concat(distinct r.ruleset_name separator ', ') as rulesets, group_concat(distinct m.modset_name separator ', ') as modulesets from v_nodes n left join comp_rulesets_nodes rn on n.nodename=rn.nodename left join comp_rulesets r on r.id=rn.ruleset_id left join comp_node_moduleset mn on mn.modset_node=n.nodename left join comp_moduleset m on m.id=mn.modset_id group by n.nodename);

#

alter table svcdisks add column disk_used integer not null default 0;

drop view v_svcdisks;

CREATE VIEW `v_svcdisks` AS select `s`.`id` AS `id`,`s`.`disk_id` AS `disk_id`,`s`.`disk_svcname` AS `disk_svcname`,`s`.`disk_nodename` AS `disk_nodename`,`s`.`disk_size` AS `disk_size`,s.disk_used as disk_used, `s`.`disk_vendor` AS `disk_vendor`,`s`.`disk_model` AS `disk_model`,`s`.`disk_dg` AS `disk_dg`,`s`.`disk_updated` AS `disk_updated`,`i`.`disk_devid` AS `disk_devid`,`i`.`disk_arrayid` AS `disk_arrayid` from (`svcdisks` `s` left join `diskinfo` `i` on((`s`.`disk_id` = convert(`i`.`disk_id` using utf8))));

alter table apps drop key i_app;

alter table apps add unique key i_app (app);

alter table apps modify column app varchar(64);

alter table services modify column svc_app varchar(64);

alter table svcdisks drop foreign key svcdisks_ibfk_1;

alter table svcdisks add CONSTRAINT `svcdisks_ibfk_1` FOREIGN KEY (disk_nodename) REFERENCES nodes (nodename) ON DELETE CASCADE;

CREATE TABLE  `opensvc`.`comp_run_ruleset` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `rset_md5` varchar(32) NOT NULL,
  `rset` longblob NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `new_index` (`rset_md5`)
) ENGINE=InnoDB CHARSET=utf8;


alter table comp_log add column rset_md5 varchar(32);

alter table comp_status add column rset_md5 varchar(32);

drop view v_disk_app;

create view v_disk_app as select n.project, group_concat(sd.disk_nodename) as object, d.*, if(max(sd.disk_used)>0, max(sd.disk_used), max(sd.disk_size)) as disk_used from diskinfo d left join svcdisks sd on d.disk_id=sd.disk_id join nodes n on sd.disk_nodename=n.nodename where sd.disk_nodename != "" and sd.disk_svcname = "" group by d.disk_id union all select s.svc_app, group_concat(sd.disk_svcname) as object, d.*, if(max(sd.disk_used)>0, max(sd.disk_used), max(sd.disk_size)) as disk_used from diskinfo d left join svcdisks sd on d.disk_id=sd.disk_id join services s on sd.disk_svcname=s.svc_name where sd.disk_svcname != "" group by d.disk_id, s.svc_app;

drop view v_disk_quota;

create view v_disk_quota as (SELECT stor_array_dg_quota.id, stor_array.id as array_id, stor_array_dg.id as dg_id, apps.id as app_id, stor_array.array_name, stor_array_dg.dg_name, stor_array_dg.dg_free, stor_array_dg.dg_size, stor_array_dg.dg_used, stor_array.array_model, apps.app, stor_array_dg_quota.quota, (select sum(disk_used) from v_disk_app where project=apps.app and disk_arrayid=stor_array.array_name and stor_array_dg.dg_name=disk_group) as quota_used FROM stor_array, stor_array_dg LEFT JOIN stor_array_dg_quota ON (stor_array_dg.id = stor_array_dg_quota.dg_id) LEFT JOIN apps ON (apps.id = stor_array_dg_quota.app_id) WHERE stor_array_dg.array_id = stor_array.id ORDER BY stor_array.array_name, stor_array_dg.dg_name);

CREATE TABLE  `opensvc`.`disk_blacklist` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `disk_id` varchar(120) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx1` (`disk_id`)
) ENGINE=InnoDB CHARSET=utf8;

alter table svcdisks add column disk_region integer default 0;

CREATE TABLE `stat_day_disk_app` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `day` datetime NOT NULL,
  `app` varchar(100) NOT NULL,
  `disk_used` int(11) DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `new_index` (`day`,`app`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `stat_day_disk_array` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `day` datetime NOT NULL,
  `array_name` varchar(100) NOT NULL,
  `disk_used` int(11) DEFAULT '0',
  `disk_size` int(11) DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `new_index` (`day`,`array_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `stat_day_disk_array_dg` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `day` datetime NOT NULL,
  `array_name` varchar(100) NOT NULL,
  `array_dg` varchar(100) NOT NULL,
  `disk_used` int(11) DEFAULT '0',
  `disk_size` int(11) DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `new_index` (`day`,`array_name`, `array_dg`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

alter table svcdisks modify column disk_region varchar(32) default "0";

alter table appinfo add column app_nodename varchar(60) default "";
alter table appinfo add column cluster_type varchar(10) default "";


drop view v_disk_quota;

drop view v_disk_app;

create view v_disk_app as 
                     select
                       diskinfo.disk_id,
                       svcdisks.disk_region,
                       services.svc_app as app,
                       svcdisks.disk_used as disk_used,
                       diskinfo.disk_size,
                       diskinfo.disk_arrayid,
                       diskinfo.disk_group
                     from
                       diskinfo
                     left join svcdisks on diskinfo.disk_id=svcdisks.disk_id
                     left join services on svcdisks.disk_svcname=services.svc_name
                     where svcdisks.disk_svcname != ""
                     union all
                     select
                       diskinfo.disk_id,
                       svcdisks.disk_region,
                       nodes.project as app,
                       svcdisks.disk_used as disk_used,
                       diskinfo.disk_size,
                       diskinfo.disk_arrayid,
                       diskinfo.disk_group
                     from
                       diskinfo
                     left join svcdisks on diskinfo.disk_id=svcdisks.disk_id
                     left join nodes on svcdisks.disk_nodename=nodes.nodename
                     where (svcdisks.disk_svcname = "" or svcdisks.disk_svcname is NULL)
;

create view v_disk_app_dedup as 
                   select
                     app,
                     max(disk_used) as disk_used,
                     disk_size,
                     disk_arrayid,
                     disk_group
                   from
                     v_disk_app
                   group by disk_id, disk_region
;

create view v_disks_app as 
                 select
                   app,
                   sum(if(disk_used is not NULL and disk_used>0, disk_used, disk_size)) as disk_used,
                   disk_arrayid,
                   disk_group
                 from 
                   v_disk_app_dedup
                 group by app, disk_arrayid, disk_group
;

alter table stor_array_dg add column dg_reserved integer default 0;

create view v_disk_quota as 
  SELECT
    stor_array_dg_quota.id,
    stor_array.id as array_id,
    stor_array_dg.id as dg_id,
    apps.id as app_id,
    stor_array.array_name,
    stor_array_dg.dg_name,
    stor_array_dg.dg_free,
    stor_array_dg.dg_size,
    stor_array_dg.dg_used,
    stor_array_dg.dg_reserved,
    stor_array_dg.dg_size - stor_array_dg.dg_reserved as dg_reservable,
    stor_array.array_model,
    apps.app,
    stor_array_dg_quota.quota,
    v_disks_app.disk_used as quota_used
  FROM
    stor_array
    JOIN stor_array_dg ON (stor_array_dg.array_id = stor_array.id)
    LEFT JOIN stor_array_dg_quota ON (stor_array_dg.id = stor_array_dg_quota.dg_id)
    LEFT JOIN apps ON (apps.id = stor_array_dg_quota.app_id)
    LEFT JOIN v_disks_app ON (
          v_disks_app.app=apps.app and
          v_disks_app.disk_arrayid=stor_array.array_name and
          v_disks_app.disk_group=stor_array_dg.dg_name
    )
  WHERE
    apps.id is not NULL
  UNION ALL
  SELECT
    stor_array_dg_quota.id,
    stor_array.id as array_id,
    stor_array_dg.id as dg_id,
    NULL as app_id,
    stor_array.array_name,
    stor_array_dg.dg_name,
    stor_array_dg.dg_free,
    stor_array_dg.dg_size,
    stor_array_dg.dg_used,
    stor_array_dg.dg_reserved,
    stor_array_dg.dg_size - stor_array_dg.dg_reserved as dg_reservable,
    stor_array.array_model,
    "unknown",
    stor_array_dg.dg_used - if(sum(v_disks_app.disk_used) is NULL, 0, sum(v_disks_app.disk_used)) as quota,
    stor_array_dg.dg_used - if(sum(v_disks_app.disk_used) is NULL, 0, sum(v_disks_app.disk_used)) as quota_used
  FROM
    stor_array
    JOIN stor_array_dg ON (stor_array_dg.array_id = stor_array.id)
    LEFT JOIN stor_array_dg_quota ON (stor_array_dg.id = stor_array_dg_quota.dg_id)
    LEFT JOIN apps ON (apps.id = stor_array_dg_quota.app_id)
    LEFT JOIN v_disks_app ON (
          v_disks_app.app=apps.app and
          v_disks_app.disk_arrayid=stor_array.array_name and
          v_disks_app.disk_group=stor_array_dg.dg_name
    )
  GROUP BY stor_array.id, stor_array_dg.id
;

alter table  stat_day_disk_app add column quota integer default 0;


CREATE TABLE `stat_day_disk_app_dg` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `day` datetime NOT NULL,
  `dg_id` integer NOT NULL,
  `app` varchar(100) NOT NULL,
  `disk_used` int(11) DEFAULT '0',
  `quota` int(11) DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `new_index` (`day`,`app`, `dg_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

alter table stat_day_disk_array_dg add column reserved integer default 0;

alter table stat_day_disk_array_dg add column reservable integer default 0;

alter table stat_day_disk_array add column reserved integer default 0;

alter table stat_day_disk_array add column reservable integer default 0;

alter table diskinfo modify disk_id varchar(120);

alter table feed_queue add column created timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP;

alter table stor_array add column array_level integer not null default 0;

alter table diskinfo add column disk_level integer not null default 0;

alter table diskinfo modify column disk_arrayid varchar(300);

alter table stor_array modify column array_name varchar(300);

ALTER TABLE apps CONVERT TO CHARACTER SET utf8;

alter table apps modify column app varchar(64) CHARACTER SET utf8;

drop view v_apps_flat;

create view v_apps_flat  AS (select `a`.`id` AS `id`,`a`.`app` AS `app`,`g`.`role` AS `role`,concat_ws(' ',`u`.`first_name`,`u`.`last_name`) AS `responsible`,`u`.`email` AS `email` from ((((`apps` `a` left join `apps_responsibles` `ar` on((`ar`.`app_id` = `a`.`id`))) left join `auth_group` `g` on((`g`.`id` = `ar`.`group_id`))) left join `auth_membership` `am` on((`am`.`group_id` = `g`.`id`))) left join `auth_user` `u` on((`u`.`id` = `am`.`user_id`))) order by `a`.`app`);

drop view v_apps;

CREATE VIEW `v_apps` AS (select `v_apps_flat`.`id` AS `id`,`v_apps_flat`.`app` AS `app`,group_concat(distinct `v_apps_flat`.`role` separator ', ') AS `roles`,group_concat(distinct `v_apps_flat`.`responsible` separator ', ') AS `responsibles`,group_concat(distinct `v_apps_flat`.`email` separator ', ') AS `mailto` from `v_apps_flat` group by `v_apps_flat`.`app`);

drop view v_svcactions;

CREATE VIEW `v_svcactions` AS select `ac`.`cron` AS `cron`,`ac`.`time` AS `time`,`ac`.`version` AS `version`,`ac`.`svcname` AS `svcname`,`ac`.`action` AS `action`,`ac`.`status` AS `status`,`ac`.`begin` AS `begin`,`ac`.`end` AS `end`,`ac`.`hostname` AS `hostname`,`ac`.`hostid` AS `hostid`,`ac`.`status_log` AS `status_log`,`ac`.`pid` AS `pid`,`ac`.`ID` AS `ID`,`ac`.`ack` AS `ack`,`ac`.`alert` AS `alert`,`ac`.`acked_by` AS `acked_by`,`ac`.`acked_comment` AS `acked_comment`,`ac`.`acked_date` AS `acked_date`,`s`.`svc_ha` AS `svc_ha`,`s`.`svc_app` AS `app`,`a`.`mailto` AS `mailto`,`a`.`responsibles` AS `responsibles`,`n`.`nodename` AS `nodename`,`n`.`loc_country` AS `loc_country`,`n`.`loc_city` AS `loc_city`,`n`.`loc_addr` AS `loc_addr`,`n`.`loc_building` AS `loc_building`,`n`.`loc_floor` AS `loc_floor`,`n`.`loc_room` AS `loc_room`,`n`.`loc_rack` AS `loc_rack`,`n`.`cpu_freq` AS `cpu_freq`,`n`.`cpu_cores` AS `cpu_cores`,`n`.`cpu_dies` AS `cpu_dies`,`n`.`cpu_vendor` AS `cpu_vendor`,`n`.`cpu_model` AS `cpu_model`,`n`.`mem_banks` AS `mem_banks`,`n`.`mem_slots` AS `mem_slots`,`n`.`mem_bytes` AS `mem_bytes`,`n`.`os_name` AS `os_name`,`n`.`os_release` AS `os_release`,`n`.`os_update` AS `os_update`,`n`.`os_segment` AS `os_segment`,`n`.`os_arch` AS `os_arch`,`n`.`os_vendor` AS `os_vendor`,`n`.`os_kernel` AS `os_kernel`,`n`.`loc_zip` AS `loc_zip`,`n`.`team_responsible` AS `team_responsible`, n.team_integ as team_integ, n.team_support as team_support, n.project as project, `n`.`serial` AS `serial`,`n`.`model` AS `model`,`n`.`type` AS `type`,`n`.`warranty_end` AS `warranty_end`,`n`.`status` AS `asset_status`,`n`.`role` AS `role`,`n`.`environnement` AS `environnement`, n.host_mode AS host_mode, `n`.`power_supply_nb` AS `power_supply_nb`,`n`.`power_cabinet1` AS `power_cabinet1`,`n`.`power_cabinet2` AS `power_cabinet2`,`n`.`power_protect` AS `power_protect`,`n`.`power_protect_breaker` AS `power_protect_breaker`,`n`.`power_breaker1` AS `power_breaker1`,`n`.`power_breaker2` AS `power_breaker2` from (((`SVCactions` `ac` join `services` `s` on((`s`.`svc_name` = `ac`.`svcname`))) join `nodes` `n` on((`ac`.`hostname` = `n`.`nodename`))) join `b_apps` `a` on((`a`.`app` = `s`.`svc_app`)));

alter table comp_log drop key idx2;

alter table comp_log add key idx2 (`run_date`);

CREATE TABLE `comp_log2` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `run_nodename` varchar(64) NOT NULL,
  `run_module` varchar(64) NOT NULL,
  `run_status` int(11) NOT NULL DEFAULT '1',
  `run_log` text NOT NULL,
  `run_date` datetime NOT NULL,
  `run_ruleset` varchar(500) DEFAULT '',
  `run_action` varchar(7) DEFAULT '',
  `run_svcname` varchar(64) DEFAULT NULL,
  `rset_md5` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`, `run_date`),
  KEY `idx1` (`run_nodename`),
  KEY `idx2` (`run_action`),
  KEY `idx3` (`run_module`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8
PARTITION BY RANGE (TO_DAYS(run_date))
(
 PARTITION pNULL VALUES LESS THAN (0),
 PARTITION p201010 VALUES LESS THAN (TO_DAYS('2010-10-01')),
 PARTITION p201011 VALUES LESS THAN (TO_DAYS('2010-11-01')),
 PARTITION p201012 VALUES LESS THAN (TO_DAYS('2010-12-01')),
 PARTITION p201101 VALUES LESS THAN (TO_DAYS('2011-01-01')),
 PARTITION p201102 VALUES LESS THAN (TO_DAYS('2011-02-01')),
 PARTITION p201103 VALUES LESS THAN (TO_DAYS('2011-03-01')),
 PARTITION p201104 VALUES LESS THAN (TO_DAYS('2011-04-01')),
 PARTITION p201105 VALUES LESS THAN (TO_DAYS('2011-05-01')),
 PARTITION p201106 VALUES LESS THAN (TO_DAYS('2011-06-01')),
 PARTITION p201107 VALUES LESS THAN (TO_DAYS('2011-07-01')),
 PARTITION p201108 VALUES LESS THAN (TO_DAYS('2011-08-01')),
 PARTITION p201109 VALUES LESS THAN (TO_DAYS('2011-09-01')),
 PARTITION p201110 VALUES LESS THAN (TO_DAYS('2011-10-01')),
 PARTITION p201111 VALUES LESS THAN (TO_DAYS('2011-11-01')),
 PARTITION p201112 VALUES LESS THAN (TO_DAYS('2011-12-01')),
 PARTITION p201201 VALUES LESS THAN (TO_DAYS('2012-01-01')),
 PARTITION p201202 VALUES LESS THAN (TO_DAYS('2012-02-01')),
 PARTITION p201203 VALUES LESS THAN (TO_DAYS('2012-03-01')),
 PARTITION p201204 VALUES LESS THAN (TO_DAYS('2012-04-01')),
 PARTITION p201205 VALUES LESS THAN (TO_DAYS('2012-05-01')),
 PARTITION p201206 VALUES LESS THAN (TO_DAYS('2012-06-01')),
 PARTITION p201207 VALUES LESS THAN (TO_DAYS('2012-07-01')),
 PARTITION p201208 VALUES LESS THAN (TO_DAYS('2012-08-01')),
 PARTITION p201209 VALUES LESS THAN (TO_DAYS('2012-09-01')),
 PARTITION p201210 VALUES LESS THAN (TO_DAYS('2012-10-01')),
 PARTITION p201211 VALUES LESS THAN (TO_DAYS('2012-11-01')),
 PARTITION p201212 VALUES LESS THAN (TO_DAYS('2012-12-01')),
 PARTITION pNew VALUES LESS THAN MAXVALUE
);

insert into comp_log2 (select * from comp_log);

alter table comp_log rename to comp_log_old;

alter table comp_log2 rename to comp_log;

ALTER TABLE comp_log REORGANIZE PARTITION pNew INTO (
  PARTITION p201301 VALUES LESS THAN (TO_DAYS('2013-01-01')),
  PARTITION p201302 VALUES LESS THAN (TO_DAYS('2013-02-01')),
  PARTITION p201303 VALUES LESS THAN (TO_DAYS('2013-03-01')),
  PARTITION p201304 VALUES LESS THAN (TO_DAYS('2013-04-01')),
  PARTITION p201305 VALUES LESS THAN (TO_DAYS('2013-05-01')),
  PARTITION p201306 VALUES LESS THAN (TO_DAYS('2013-06-01')),
  PARTITION p201307 VALUES LESS THAN (TO_DAYS('2013-07-01')),
  PARTITION p201308 VALUES LESS THAN (TO_DAYS('2013-08-01')),
  PARTITION p201309 VALUES LESS THAN (TO_DAYS('2013-09-01')),
  PARTITION p201310 VALUES LESS THAN (TO_DAYS('2013-10-01')),
  PARTITION p201311 VALUES LESS THAN (TO_DAYS('2013-11-01')),
  PARTITION p201312 VALUES LESS THAN (TO_DAYS('2013-12-01')),
  PARTITION pNew VALUES LESS THAN (MAXVALUE)
);

CREATE TABLE `SVCactions2` (
  `svcname` varchar(60) DEFAULT NULL,
  `action` varchar(30) CHARACTER SET latin1 DEFAULT NULL,
  `status` enum('err','ok','warn') NOT NULL,
  `begin` datetime NOT NULL DEFAULT '0000-00-00 00:00:00',
  `end` datetime DEFAULT NULL,
  `hostname` varchar(50) NOT NULL DEFAULT '',
  `hostid` varchar(30) DEFAULT NULL,
  `status_log` text CHARACTER SET latin1,
  `pid` varchar(32) DEFAULT NULL,
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `ack` tinyint(4) DEFAULT NULL,
  `alert` tinyint(1) DEFAULT NULL,
  `acked_by` varchar(50) CHARACTER SET latin1 DEFAULT NULL,
  `acked_comment` text CHARACTER SET latin1,
  `acked_date` datetime NOT NULL,
  `version` varchar(20) CHARACTER SET latin1 DEFAULT NULL,
  `cron` tinyint(1) DEFAULT '0',
  `time` datetime DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`ID`, `begin`),
  KEY `hostname` (`hostname`),
  KEY `svcname` (`svcname`),
  KEY `hostid` (`hostid`),
  KEY `action` (`action`),
  KEY `end` (`end`),
  KEY `status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8
PARTITION BY RANGE (TO_DAYS(begin))
(
 PARTITION pNULL VALUES LESS THAN (0),
 PARTITION p201010 VALUES LESS THAN (TO_DAYS('2010-10-01')),
 PARTITION p201011 VALUES LESS THAN (TO_DAYS('2010-11-01')),
 PARTITION p201012 VALUES LESS THAN (TO_DAYS('2010-12-01')),
 PARTITION p201101 VALUES LESS THAN (TO_DAYS('2011-01-01')),
 PARTITION p201102 VALUES LESS THAN (TO_DAYS('2011-02-01')),
 PARTITION p201103 VALUES LESS THAN (TO_DAYS('2011-03-01')),
 PARTITION p201104 VALUES LESS THAN (TO_DAYS('2011-04-01')),
 PARTITION p201105 VALUES LESS THAN (TO_DAYS('2011-05-01')),
 PARTITION p201106 VALUES LESS THAN (TO_DAYS('2011-06-01')),
 PARTITION p201107 VALUES LESS THAN (TO_DAYS('2011-07-01')),
 PARTITION p201108 VALUES LESS THAN (TO_DAYS('2011-08-01')),
 PARTITION p201109 VALUES LESS THAN (TO_DAYS('2011-09-01')),
 PARTITION p201110 VALUES LESS THAN (TO_DAYS('2011-10-01')),
 PARTITION p201111 VALUES LESS THAN (TO_DAYS('2011-11-01')),
 PARTITION p201112 VALUES LESS THAN (TO_DAYS('2011-12-01')),
 PARTITION p201201 VALUES LESS THAN (TO_DAYS('2012-01-01')),
 PARTITION p201202 VALUES LESS THAN (TO_DAYS('2012-02-01')),
 PARTITION p201203 VALUES LESS THAN (TO_DAYS('2012-03-01')),
 PARTITION p201204 VALUES LESS THAN (TO_DAYS('2012-04-01')),
 PARTITION p201205 VALUES LESS THAN (TO_DAYS('2012-05-01')),
 PARTITION p201206 VALUES LESS THAN (TO_DAYS('2012-06-01')),
 PARTITION p201207 VALUES LESS THAN (TO_DAYS('2012-07-01')),
 PARTITION p201208 VALUES LESS THAN (TO_DAYS('2012-08-01')),
 PARTITION p201209 VALUES LESS THAN (TO_DAYS('2012-09-01')),
 PARTITION p201210 VALUES LESS THAN (TO_DAYS('2012-10-01')),
 PARTITION p201211 VALUES LESS THAN (TO_DAYS('2012-11-01')),
 PARTITION p201212 VALUES LESS THAN (TO_DAYS('2012-12-01')),
 PARTITION p201301 VALUES LESS THAN (TO_DAYS('2013-01-01')),
 PARTITION p201302 VALUES LESS THAN (TO_DAYS('2013-02-01')),
 PARTITION p201303 VALUES LESS THAN (TO_DAYS('2013-03-01')),
 PARTITION p201304 VALUES LESS THAN (TO_DAYS('2013-04-01')),
 PARTITION p201305 VALUES LESS THAN (TO_DAYS('2013-05-01')),
 PARTITION p201306 VALUES LESS THAN (TO_DAYS('2013-06-01')),
 PARTITION p201307 VALUES LESS THAN (TO_DAYS('2013-07-01')),
 PARTITION p201308 VALUES LESS THAN (TO_DAYS('2013-08-01')),
 PARTITION p201309 VALUES LESS THAN (TO_DAYS('2013-09-01')),
 PARTITION p201310 VALUES LESS THAN (TO_DAYS('2013-10-01')),
 PARTITION p201311 VALUES LESS THAN (TO_DAYS('2013-11-01')),
 PARTITION p201312 VALUES LESS THAN (TO_DAYS('2013-12-01')),
 PARTITION pNew VALUES LESS THAN MAXVALUE
);

insert into SVCactions2 (select * from SVCactions);

alter table SVCactions rename to SVCactionsold;

alter table SVCactions2 rename to SVCactions;

drop view v_disk_app;

create view v_disk_app as 
                     select
                       diskinfo.id,
                       diskinfo.disk_id,
                       svcdisks.disk_region,
                       svcdisks.disk_svcname,
                       svcdisks.disk_nodename,
                       svcdisks.disk_vendor,
                       svcdisks.disk_model,
                       svcdisks.disk_dg,
                       svcdisks.disk_updated as svcdisk_updated,
                       svcdisks.id as svcdisk_id,
                       svcdisks.disk_local,
                       services.svc_app as app,
                       svcdisks.disk_used as disk_used,
                       diskinfo.disk_size,
                       diskinfo.disk_arrayid,
                       diskinfo.disk_group,
                       diskinfo.disk_devid,
                       diskinfo.disk_updated,
                       diskinfo.disk_raid,
                       diskinfo.disk_level
                     from
                       diskinfo
                     left join svcdisks on diskinfo.disk_id=svcdisks.disk_id
                     left join services on svcdisks.disk_svcname=services.svc_name
                     where svcdisks.disk_svcname != ""
                     union all
                     select
                       diskinfo.id,
                       diskinfo.disk_id,
                       svcdisks.disk_region,
                       svcdisks.disk_svcname,
                       svcdisks.disk_nodename,
                       svcdisks.disk_vendor,
                       svcdisks.disk_model,
                       svcdisks.disk_dg,
                       svcdisks.disk_updated as svcdisk_updated,
                       svcdisks.id as svcdisk_id,
                       svcdisks.disk_local,
                       nodes.project as app,
                       svcdisks.disk_used as disk_used,
                       diskinfo.disk_size,
                       diskinfo.disk_arrayid,
                       diskinfo.disk_group,
                       diskinfo.disk_devid,
                       diskinfo.disk_updated,
                       diskinfo.disk_raid,
                       diskinfo.disk_level
                     from
                       diskinfo
                     left join svcdisks on diskinfo.disk_id=svcdisks.disk_id
                     left join nodes on svcdisks.disk_nodename=nodes.nodename
                     where (svcdisks.disk_svcname = "" or svcdisks.disk_svcname is NULL)
;


alter table diskinfo modify column disk_raid varchar(24);

alter table diskinfo drop key new_index;

alter table diskinfo modify column disk_group varchar(60) default "";

update diskinfo set disk_group="" where disk_group is NULL;

alter table diskinfo add unique key new_index (disk_id, disk_group);

drop view v_comp_rulesets;

create view v_comp_rulesets as (select `r`.`id` AS `ruleset_id`,`r`.`ruleset_name` AS `ruleset_name`,`r`.`ruleset_type` AS `ruleset_type`,group_concat(distinct `g`.`role` separator ', ') AS `teams_responsible`,(select ruleset_name from comp_rulesets where id=rr.child_rset_id) as encap_rset, rr.child_rset_id as encap_rset_id, `rv`.`id` AS `id`,`rv`.`var_name` AS `var_name`,`rv`.`var_class` AS `var_class`,`rv`.`var_value` AS `var_value`,`rv`.`var_author` AS `var_author`,`rv`.`var_updated` AS `var_updated`,`rf`.`fset_id` AS `fset_id`,`fs`.`fset_name` AS `fset_name` from (((((`comp_rulesets` `r` left join comp_rulesets_rulesets rr on r.id=rr.parent_rset_id left join `comp_rulesets_variables` `rv` on(((`rv`.`ruleset_id` = `r`.`id` and rr.child_rset_id is NULL) or rv.ruleset_id = rr.child_rset_id))) left join `comp_rulesets_filtersets` `rf` on((`r`.`id` = `rf`.`ruleset_id`))) left join `gen_filtersets` `fs` on((`fs`.`id` = `rf`.`fset_id`))) left join `comp_ruleset_team_responsible` `rt` on((`r`.`id` = `rt`.`ruleset_id`))) left join `auth_group` `g` on((`rt`.`group_id` = `g`.`id`))) group by `r`.`id`,`rv`.`id`, rr.id);

alter table gen_filters modify column f_value varchar(128);

CREATE TABLE `switches` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sw_name` varchar(64) NOT NULL,
  `sw_slot` int(11),
  `sw_port` int(11),
  `sw_portspeed` int(11),
  `sw_portnego` varchar(1) DEFAULT '',
  `sw_porttype` varchar(16) DEFAULT '',
  `sw_portstate` varchar(16) DEFAULT '',
  `sw_portname` varchar(16) DEFAULT '',
  `sw_rportname` varchar(16) DEFAULT '',
  `sw_updated` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx1` (`sw_name`, `sw_slot`, `sw_port`)
);

CREATE TABLE `node_ip` (
  `nodename` varchar(64) DEFAULT '',
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `mac` varchar(17) NOT NULL,
  `intf` varchar(12) NOT NULL,
  `type` enum('ipv4', 'ipv6') default 'ipv4',
  `addr` varchar(128) DEFAULT '',
  `mask` varchar(64) DEFAULT '',
  `updated` datetime not null,
  PRIMARY KEY (`id`)
);

alter table switches drop key idx1;

alter table switches add unique key idx1 (`sw_name`,`sw_slot`,`sw_port`,`sw_rportname`);

alter table switches add column sw_fabric varchar(128);

alter table services add column svc_containerpath varchar(512);

alter table switches add column sw_index integer;

CREATE TABLE `san_zone` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cfg` varchar(128) DEFAULT '',
  `zone` varchar(128) DEFAULT '',
  `port` varchar(16) DEFAULT '',
  `updated` datetime not null,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx1` (`cfg`, `zone`, `port`)
);

CREATE TABLE `san_zone_alias` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cfg` varchar(128) DEFAULT '',
  `alias` varchar(128) DEFAULT '',
  `port` varchar(16) DEFAULT '',
  `updated` datetime not null,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx1` (`cfg`, `alias`, `port`)
);

CREATE TABLE `billing_agent` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `bill_min_agt` int(11) NOT NULL,
  `bill_os_name` varchar(50) NOT NULL,
  `bill_cost` float NOT NULL,
  `bill_max_agt` int(11) NOT NULL,
  `bill_env` enum('prd', 'nonprd') default 'prd' NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=19 DEFAULT CHARSET=utf8;

INSERT INTO `billing_agent` VALUES (null,1000,'AIX',20,999999, 'prd'),(null,1000,'SunOS',20,999999, 'prd'),(null,1000,'HP-UX',20,999999, 'prd'),(null,1000,'OpenSolaris',10,999999, 'prd'),(null,1000,'FreeBSD',10,999999, 'prd'),(null,1000,'Linux',10,999999, 'prd'),(null,500,'AIX',24,999, 'prd'),(null,500,'SunOS',24,999, 'prd'),(null,500,'HP-UX',24,999, 'prd'),(null,500,'OpenSolaris',12,999, 'prd'),(null,500,'FreeBSD',12,999, 'prd'),(null,500,'Linux',12,999, 'prd'),(null,0,'AIX',30,499, 'prd'),(null,0,'OpenSolaris',15,499, 'prd'),(null,0,'SunOS',30,499, 'prd'),(null,0,'HP-UX',30,499, 'prd'),(null,0,'FreeBSD',15,499, 'prd'),(null,0,'Linux',15,499, 'prd'),  (null,1000,'AIX',20,999999, 'nonprd'),(null,1000,'SunOS',20,999999, 'nonprd'),(null,1000,'HP-UX',20,999999, 'nonprd'),(null,1000,'OpenSolaris',10,999999, 'nonprd'),(null,1000,'FreeBSD',10,999999, 'nonprd'),(null,1000,'Linux',10,999999, 'nonprd'),(null,500,'AIX',24,999, 'nonprd'),(null,500,'SunOS',24,999, 'nonprd'),(null,500,'HP-UX',24,999, 'nonprd'),(null,500,'OpenSolaris',12,999, 'nonprd'),(null,500,'FreeBSD',12,999, 'nonprd'),(null,500,'Linux',12,999, 'nonprd'),(null,0,'AIX',30,499, 'nonprd'),(null,0,'OpenSolaris',15,499, 'nonprd'),(null,0,'SunOS',30,499, 'nonprd'),(null,0,'HP-UX',30,499, 'nonprd'),(null,0,'FreeBSD',15,499, 'nonprd'),(null,0,'Linux',15,499, 'nonprd');

alter table billing add column `bill_env` enum('prd', 'nonprd') default 'prd' NOT NULL;

INSERT INTO `billing` VALUES (null,1000,'AIX',100,999999, 'nonprd'),(null,1000,'SunOS',100,999999, 'nonprd'),(null,1000,'HP-UX',100,999999, 'nonprd'),(null,1000,'OpenSolaris',50,999999, 'nonprd'),(null,1000,'FreeBSD',50,999999, 'nonprd'),(null,1000,'Linux',50,999999, 'nonprd'),(null,500,'AIX',120,999, 'nonprd'),(null,500,'SunOS',120,999, 'nonprd'),(null,500,'HP-UX',120,999, 'nonprd'),(null,500,'OpenSolaris',60,999, 'nonprd'),(null,500,'FreeBSD',60,999, 'nonprd'),(null,500,'Linux',60,999, 'nonprd'),(null,0,'AIX',150,499, 'nonprd'),(null,0,'OpenSolaris',75,499, 'nonprd'),(null,0,'SunOS',150,499, 'nonprd'),(null,0,'HP-UX',150,499, 'nonprd'),(null,0,'FreeBSD',75,499, 'nonprd'),(null,0,'Linux',75,499, 'nonprd');

CREATE TABLE `stat_day_billing` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `fset_id` int(11) not null default 0,
  `day` datetime NOT NULL,
  `os_name` varchar(100) NOT NULL,
  `nb_svc_prd` int(11) DEFAULT 0,
  `nb_svc_nonprd` int(11) DEFAULT 0,
  `nb_agents_without_svc_prd` int(11) DEFAULT 0,
  `nb_agents_without_svc_nonprd` int(11) DEFAULT 0,
  PRIMARY KEY (`id`),
  UNIQUE KEY `new_index` (`day`,`fset_id`,`os_name`)
);

alter table stat_day_billing modify column day datetime not null;

alter table dashboard add column dash_env enum ('DEV', 'PRD', 'TST', 'REC', 'INT', '') default '';

alter table svcmon add column mon_vmname varchar(30);
alter table svcmon add column mon_guestos varchar(30);
alter table svcmon add column mon_vmem integer default 0;
alter table svcmon add column mon_vcpus float default 0;

drop view v_svcmon;

CREATE VIEW `v_svcmon` AS select `e`.`err` AS `err`,`s`.`svc_ha` AS `svc_ha`,`s`.`svc_cluster_type` AS `svc_cluster_type`,`s`.`svc_status` AS `svc_status`,`s`.`svc_availstatus` AS `svc_availstatus`,`s`.`svc_flex_min_nodes` AS `svc_flex_min_nodes`,`s`.`svc_flex_max_nodes` AS `svc_flex_max_nodes`,`s`.`svc_flex_cpu_low_threshold` AS `svc_flex_cpu_low_threshold`,`s`.`svc_flex_cpu_high_threshold` AS `svc_flex_cpu_high_threshold`,`m`.`mon_vmname` AS `mon_vmname`,`m`.`mon_guestos` AS `mon_guestos`,`s`.`svc_version` AS `svc_version`,`s`.`svc_name` AS `svc_name`,`s`.`svc_nodes` AS `svc_nodes`,`s`.`svc_drpnode` AS `svc_drpnode`,`s`.`svc_drpnodes` AS `svc_drpnodes`,`s`.`svc_drptype` AS `svc_drptype`,`s`.`svc_autostart` AS `svc_autostart`,`s`.`svc_type` AS `svc_type`,`s`.`svc_comment` AS `svc_comment`,`s`.`svc_app` AS `svc_app`,`s`.`svc_drnoaction` AS `svc_drnoaction`,`s`.`svc_created` AS `svc_created`,`s`.`updated` AS `svc_updated`,`s`.`svc_envdate` AS `svc_envdate`,`s`.`svc_containertype` AS `svc_containertype`,`s`.`svc_metrocluster` AS `svc_metrocluster`,`m`.`mon_vcpus` AS `mon_vcpus`,`m`.`mon_vmem` AS `mon_vmem`,`m`.`mon_svcname` AS `mon_svcname`,`m`.`mon_svctype` AS `mon_svctype`,`m`.`mon_drptype` AS `mon_drptype`,`m`.`mon_nodname` AS `mon_nodname`,`m`.`mon_nodtype` AS `mon_nodtype`,`m`.`mon_nodmode` AS `mon_nodmode`,`m`.`mon_ipstatus` AS `mon_ipstatus`,`m`.`mon_fsstatus` AS `mon_fsstatus`,`m`.`mon_prinodes` AS `mon_prinodes`,`m`.`mon_hostid` AS `mon_hostid`,`m`.`ID` AS `ID`,`m`.`mon_frozen` AS `mon_frozen`,`m`.`mon_frozentxt` AS `mon_frozentxt`,`m`.`mon_changed` AS `mon_changed`,`m`.`mon_updated` AS `mon_updated`,`m`.`mon_diskstatus` AS `mon_diskstatus`,`m`.`mon_containerstatus` AS `mon_containerstatus`,`m`.`mon_overallstatus` AS `mon_overallstatus`,`n`.`nodename` AS `nodename`,`n`.`updated` AS `node_updated`,`n`.`loc_country` AS `loc_country`,`n`.`loc_city` AS `loc_city`,`n`.`loc_addr` AS `loc_addr`,`n`.`loc_building` AS `loc_building`,`n`.`loc_floor` AS `loc_floor`,`n`.`loc_room` AS `loc_room`,`n`.`loc_rack` AS `loc_rack`,`n`.`cpu_freq` AS `cpu_freq`,`n`.`cpu_cores` AS `cpu_cores`,`n`.`cpu_dies` AS `cpu_dies`,`n`.`cpu_vendor` AS `cpu_vendor`,`n`.`cpu_model` AS `cpu_model`,`n`.`mem_banks` AS `mem_banks`,`n`.`mem_slots` AS `mem_slots`,`n`.`mem_bytes` AS `mem_bytes`,`n`.`os_name` AS `os_name`,`n`.`os_release` AS `os_release`,`n`.`os_update` AS `os_update`,`n`.`os_segment` AS `os_segment`,`n`.`os_arch` AS `os_arch`,`n`.`os_vendor` AS `os_vendor`,`n`.`os_kernel` AS `os_kernel`,`n`.`loc_zip` AS `loc_zip`,`n`.`team_responsible` AS `team_responsible`, n.team_integ as team_integ, n.team_support as team_support, n.project as project, `n`.`serial` AS `serial`,`n`.`model` AS `model`,`n`.`type` AS `type`,`n`.`warranty_end` AS `warranty_end`,`n`.`status` AS `status`,`n`.`role` AS `role`,`n`.`environnement` AS `environnement`,n.host_mode as host_mode,`n`.`power_supply_nb` AS `power_supply_nb`,`n`.`power_cabinet1` AS `power_cabinet1`,`n`.`power_cabinet2` AS `power_cabinet2`,`n`.`power_protect` AS `power_protect`,`n`.`power_protect_breaker` AS `power_protect_breaker`,`n`.`power_breaker1` AS `power_breaker1`,`n`.`power_breaker2` AS `power_breaker2`,`m`.`mon_syncstatus` AS `mon_syncstatus`,`m`.`mon_hbstatus` AS `mon_hbstatus`,`m`.`mon_availstatus` AS `mon_availstatus`,`m`.`mon_appstatus` AS `mon_appstatus`,`ap`.`responsibles` AS `responsibles`,`ap`.`mailto` AS `mailto` from ((((`svcmon` `m` left join `services` `s` on((`s`.`svc_name` = `m`.`mon_svcname`))) left join `nodes` `n` on((convert(`m`.`mon_nodname` using utf8) = `n`.`nodename`))) left join `b_apps` `ap` on((`ap`.`app` = `s`.`svc_app`))) left join `b_action_errors` `e` on(((`e`.`svcname` = convert(`s`.`svc_name` using utf8)) and (`e`.`nodename` = convert(`m`.`mon_nodname` using utf8)))));

drop view v_services;

CREATE VIEW `v_services` AS select s.svc_ha, s.svc_status, s.svc_availstatus, s.svc_cluster_type, s.svc_flex_min_nodes, s.svc_flex_max_nodes, s.svc_flex_cpu_low_threshold, s.svc_flex_cpu_high_threshold, `s`.`svc_version` AS `svc_version`,`s`.`svc_hostid` AS `svc_hostid`,`s`.`svc_name` AS `svc_name`,`s`.`svc_nodes` AS `svc_nodes`,`s`.`svc_drpnode` AS `svc_drpnode`,`s`.`svc_ipname` AS `svc_ipname`,`s`.`svc_ipdev` AS `svc_ipdev`,`s`.`svc_drpipname` AS `svc_drpipname`,`s`.`svc_drpipdev` AS `svc_drpipdev`,`s`.`svc_drptype` AS `svc_drptype`,`s`.`svc_fs` AS `svc_fs`,`s`.`svc_dev` AS `svc_dev`,`s`.`svc_autostart` AS `svc_autostart`,`s`.`svc_mntopt` AS `svc_mntopt`,`s`.`svc_scsi` AS `svc_scsi`,`s`.`svc_type` AS `svc_type`,`s`.`svc_drpnodes` AS `svc_drpnodes`,`s`.`svc_comment` AS `svc_comment`,`s`.`svc_app` AS `svc_app`,`s`.`svc_drnoaction` AS `svc_drnoaction`,svc_created,`s`.`updated` AS `updated`,`s`.`cksum` AS `cksum`,`s`.`svc_envdate` AS `svc_envdate`,`s`.`svc_containertype` AS `svc_containertype`,`s`.`svc_metrocluster` AS `svc_metrocluster`,`s`.`id` AS `id`,`s`.`svc_hasec` AS `svc_hasec`,`s`.`svc_hapri` AS `svc_hapri`,`s`.`svc_hastonith` AS `svc_hastonith`,`s`.`svc_hastartup` AS `svc_hastartup`,`s`.`svc_wave` AS `svc_wave`,`a`.`app` AS `app`,`a`.`responsibles` AS `responsibles`,`a`.`mailto` AS `mailto` from (`services` `s` left join `v_apps` `a` on((`a`.`app` = `s`.`svc_app`))) ;

alter table svcmon add column mon_containerpath varchar(512);

alter table diskinfo add column disk_controller varchar(32);

drop view v_disk_quota;

create view v_disk_quota as 
  SELECT
    stor_array_dg_quota.id,
    stor_array.id as array_id,
    stor_array_dg.id as dg_id,
    apps.id as app_id,
    stor_array.array_name,
    stor_array_dg.dg_name,
    stor_array_dg.dg_free,
    stor_array_dg.dg_size,
    stor_array_dg.dg_used,
    stor_array_dg.dg_reserved,
    stor_array_dg.dg_size - stor_array_dg.dg_reserved as dg_reservable,
    stor_array.array_model,
    apps.app,
    stor_array_dg_quota.quota,
    v_disks_app.disk_used as quota_used
  FROM
    stor_array
    JOIN stor_array_dg ON (stor_array_dg.array_id = stor_array.id)
    LEFT JOIN v_disks_app ON (
          v_disks_app.disk_arrayid=stor_array.array_name and
          v_disks_app.disk_group=stor_array_dg.dg_name
    )
    LEFT JOIN apps ON (apps.app = v_disks_app.app)
    LEFT JOIN stor_array_dg_quota ON (
      stor_array_dg.id = stor_array_dg_quota.dg_id and
      apps.id = stor_array_dg_quota.app_id
    )
  WHERE
    apps.id is not NULL
  GROUP BY apps.id, stor_array.id, stor_array_dg.id
  UNION ALL
  SELECT
    stor_array_dg_quota.id,
    stor_array.id as array_id,
    stor_array_dg.id as dg_id,
    NULL as app_id,
    stor_array.array_name,
    stor_array_dg.dg_name,
    stor_array_dg.dg_free,
    stor_array_dg.dg_size,
    stor_array_dg.dg_used,
    stor_array_dg.dg_reserved,
    stor_array_dg.dg_size - stor_array_dg.dg_reserved as dg_reservable,
    stor_array.array_model,
    "unknown",
    v_disks_app.disk_used as quota,
    v_disks_app.disk_used as quota_used
  FROM
    stor_array
    JOIN stor_array_dg ON (stor_array_dg.array_id = stor_array.id)
    LEFT JOIN stor_array_dg_quota ON (stor_array_dg.id = stor_array_dg_quota.dg_id)
    LEFT JOIN v_disks_app ON (
          v_disks_app.disk_arrayid=stor_array.array_name and
          v_disks_app.disk_group=stor_array_dg.dg_name
    )
  WHERE
    v_disks_app.app is NULL
  GROUP BY stor_array.id, stor_array_dg.id
;

drop view v_disk_app_dedup;

create view v_disk_app_dedup as
                   select
                     app,
                     max(disk_used) as disk_used,
                     disk_size,
                     disk_arrayid,
                     disk_group
                   from
                     b_disk_app
                   group by disk_id, disk_region, disk_arrayid, disk_group
;

alter table action_queue add column stdout text;

alter table action_queue add column stderr text;

CREATE TABLE `stats_fs_u2` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `date` datetime NOT NULL,
  `nodename` varchar(60) NOT NULL,
  `mntpt` varchar(200) NOT NULL,
  `size` bigint(20) DEFAULT NULL,
  `used` int(11) NOT NULL,
  PRIMARY KEY (`id`, `date`),
  UNIQUE KEY `index_1` (`date`,`nodename`,`mntpt`)
) ENGINE=InnoDB AUTO_INCREMENT=179025 DEFAULT CHARSET=utf8 ROW_FORMAT=COMPRESSED
PARTITION BY RANGE (TO_DAYS(date))
(
 PARTITION pNULL VALUES LESS THAN (0),
 PARTITION p201010 VALUES LESS THAN (TO_DAYS('2010-10-01')),
 PARTITION p201011 VALUES LESS THAN (TO_DAYS('2010-11-01')),
 PARTITION p201012 VALUES LESS THAN (TO_DAYS('2010-12-01')),
 PARTITION p201101 VALUES LESS THAN (TO_DAYS('2011-01-01')),
 PARTITION p201102 VALUES LESS THAN (TO_DAYS('2011-02-01')),
 PARTITION p201103 VALUES LESS THAN (TO_DAYS('2011-03-01')),
 PARTITION p201104 VALUES LESS THAN (TO_DAYS('2011-04-01')),
 PARTITION p201105 VALUES LESS THAN (TO_DAYS('2011-05-01')),
 PARTITION p201106 VALUES LESS THAN (TO_DAYS('2011-06-01')),
 PARTITION p201107 VALUES LESS THAN (TO_DAYS('2011-07-01')),
 PARTITION p201108 VALUES LESS THAN (TO_DAYS('2011-08-01')),
 PARTITION p201109 VALUES LESS THAN (TO_DAYS('2011-09-01')),
 PARTITION p201110 VALUES LESS THAN (TO_DAYS('2011-10-01')),
 PARTITION p201111 VALUES LESS THAN (TO_DAYS('2011-11-01')),
 PARTITION p201112 VALUES LESS THAN (TO_DAYS('2011-12-01')),
 PARTITION p201201 VALUES LESS THAN (TO_DAYS('2012-01-01')),
 PARTITION p201202 VALUES LESS THAN (TO_DAYS('2012-02-01')),
 PARTITION p201203 VALUES LESS THAN (TO_DAYS('2012-03-01')),
 PARTITION p201204 VALUES LESS THAN (TO_DAYS('2012-04-01')),
 PARTITION p201205 VALUES LESS THAN (TO_DAYS('2012-05-01')),
 PARTITION p201206 VALUES LESS THAN (TO_DAYS('2012-06-01')),
 PARTITION p201207 VALUES LESS THAN (TO_DAYS('2012-07-01')),
 PARTITION p201208 VALUES LESS THAN (TO_DAYS('2012-08-01')),
 PARTITION p201209 VALUES LESS THAN (TO_DAYS('2012-09-01')),
 PARTITION p201210 VALUES LESS THAN (TO_DAYS('2012-10-01')),
 PARTITION p201211 VALUES LESS THAN (TO_DAYS('2012-11-01')),
 PARTITION p201212 VALUES LESS THAN (TO_DAYS('2012-12-01')),
 PARTITION pNew VALUES LESS THAN MAXVALUE
);

ALTER TABLE stats_fs_u2 REORGANIZE PARTITION pNew INTO (
  PARTITION p201301 VALUES LESS THAN (TO_DAYS('2013-01-01')),
  PARTITION p201302 VALUES LESS THAN (TO_DAYS('2013-02-01')),
  PARTITION p201303 VALUES LESS THAN (TO_DAYS('2013-03-01')),
  PARTITION p201304 VALUES LESS THAN (TO_DAYS('2013-04-01')),
  PARTITION p201305 VALUES LESS THAN (TO_DAYS('2013-05-01')),
  PARTITION p201306 VALUES LESS THAN (TO_DAYS('2013-06-01')),
  PARTITION p201307 VALUES LESS THAN (TO_DAYS('2013-07-01')),
  PARTITION p201308 VALUES LESS THAN (TO_DAYS('2013-08-01')),
  PARTITION p201309 VALUES LESS THAN (TO_DAYS('2013-09-01')),
  PARTITION p201310 VALUES LESS THAN (TO_DAYS('2013-10-01')),
  PARTITION p201311 VALUES LESS THAN (TO_DAYS('2013-11-01')),
  PARTITION p201312 VALUES LESS THAN (TO_DAYS('2013-12-01')),
  PARTITION pNew VALUES LESS THAN (MAXVALUE)
);

insert into stats_fs_u2 (select * from stats_fs_u);

alter table stats_fs_u rename to stats_fs_uold;

alter table stats_fs_u2 rename to stats_fs_u;


alter table checks_defaults add column chk_inst varchar(128) default NULL;

alter table checks_defaults drop key idx1;

alter table checks_defaults add unique key idx1 (`chk_type`, `chk_inst`);

drop view v_svcmon;

CREATE VIEW `v_svcmon` AS select `e`.`err` AS `err`,`s`.`svc_ha` AS `svc_ha`,`s`.`svc_cluster_type` AS `svc_cluster_type`,`s`.`svc_status` AS `svc_status`,`s`.`svc_availstatus` AS `svc_availstatus`,`s`.`svc_flex_min_nodes` AS `svc_flex_min_nodes`,`s`.`svc_flex_max_nodes` AS `svc_flex_max_nodes`,`s`.`svc_flex_cpu_low_threshold` AS `svc_flex_cpu_low_threshold`,`s`.`svc_flex_cpu_high_threshold` AS `svc_flex_cpu_high_threshold`,`m`.`mon_vmname` AS `mon_vmname`,`m`.`mon_guestos` AS `mon_guestos`,`s`.`svc_version` AS `svc_version`,`s`.`svc_name` AS `svc_name`,`s`.`svc_nodes` AS `svc_nodes`,`s`.`svc_drpnode` AS `svc_drpnode`,`s`.`svc_drpnodes` AS `svc_drpnodes`,`s`.`svc_drptype` AS `svc_drptype`,`s`.`svc_autostart` AS `svc_autostart`,`s`.`svc_type` AS `svc_type`,`s`.`svc_comment` AS `svc_comment`,`s`.`svc_app` AS `svc_app`,`s`.`svc_drnoaction` AS `svc_drnoaction`,`s`.`svc_created` AS `svc_created`,`s`.`updated` AS `svc_updated`,`s`.`svc_envdate` AS `svc_envdate`,`s`.`svc_containertype` AS `svc_containertype`,`s`.`svc_metrocluster` AS `svc_metrocluster`,`m`.`mon_vcpus` AS `mon_vcpus`,`m`.`mon_vmem` AS `mon_vmem`,`m`.`mon_svcname` AS `mon_svcname`,`m`.`mon_svctype` AS `mon_svctype`,`m`.`mon_drptype` AS `mon_drptype`,`m`.`mon_nodname` AS `mon_nodname`,`m`.`mon_nodtype` AS `mon_nodtype`,`m`.`mon_nodmode` AS `mon_nodmode`,`m`.`mon_ipstatus` AS `mon_ipstatus`,`m`.`mon_fsstatus` AS `mon_fsstatus`,`m`.`mon_prinodes` AS `mon_prinodes`,`m`.`mon_hostid` AS `mon_hostid`,`m`.`ID` AS `ID`,`m`.`mon_frozen` AS `mon_frozen`,`m`.`mon_frozentxt` AS `mon_frozentxt`,`m`.`mon_changed` AS `mon_changed`,`m`.`mon_updated` AS `mon_updated`,`m`.`mon_diskstatus` AS `mon_diskstatus`,`m`.`mon_containerstatus` AS `mon_containerstatus`,`m`.`mon_overallstatus` AS `mon_overallstatus`,`n`.`nodename` AS `nodename`,`n`.`updated` AS `node_updated`,`n`.`loc_country` AS `loc_country`,`n`.`loc_city` AS `loc_city`,`n`.`loc_addr` AS `loc_addr`,`n`.`loc_building` AS `loc_building`,`n`.`loc_floor` AS `loc_floor`,`n`.`loc_room` AS `loc_room`,`n`.`loc_rack` AS `loc_rack`,`n`.`cpu_freq` AS `cpu_freq`,`n`.`cpu_cores` AS `cpu_cores`,`n`.`cpu_dies` AS `cpu_dies`,`n`.`cpu_vendor` AS `cpu_vendor`,`n`.`cpu_model` AS `cpu_model`,`n`.`mem_banks` AS `mem_banks`,`n`.`mem_slots` AS `mem_slots`,`n`.`mem_bytes` AS `mem_bytes`,`n`.`os_name` AS `os_name`,`n`.`os_release` AS `os_release`,`n`.`os_update` AS `os_update`,`n`.`os_segment` AS `os_segment`,`n`.`os_arch` AS `os_arch`,`n`.`os_vendor` AS `os_vendor`,`n`.`os_kernel` AS `os_kernel`,`n`.`loc_zip` AS `loc_zip`,`n`.`team_responsible` AS `team_responsible`,`n`.`team_integ` AS `team_integ`,`n`.`team_support` AS `team_support`,`n`.`project` AS `project`,`n`.`serial` AS `serial`,`n`.`model` AS `model`,`n`.`type` AS `type`,`n`.`warranty_end` AS `warranty_end`,`n`.`status` AS `status`,`n`.`role` AS `role`,`n`.`environnement` AS `environnement`,`n`.`host_mode` AS `host_mode`,`n`.`power_supply_nb` AS `power_supply_nb`,`n`.`power_cabinet1` AS `power_cabinet1`,`n`.`power_cabinet2` AS `power_cabinet2`,`n`.`power_protect` AS `power_protect`,`n`.`power_protect_breaker` AS `power_protect_breaker`,`n`.`power_breaker1` AS `power_breaker1`,`n`.`power_breaker2` AS `power_breaker2`,`m`.`mon_syncstatus` AS `mon_syncstatus`,`m`.`mon_hbstatus` AS `mon_hbstatus`,`m`.`mon_availstatus` AS `mon_availstatus`,`m`.`mon_appstatus` AS `mon_appstatus`,`ap`.`responsibles` AS `responsibles`,`ap`.`mailto` AS `mailto` from `svcmon` `m` left join `services` `s` on `s`.`svc_name` = `m`.`mon_svcname` left join `nodes` `n` on `m`.`mon_nodname` = `n`.`nodename` left join `b_apps` `ap` on `ap`.`app` = `s`.`svc_app` left join `b_action_errors` `e` on `e`.`svcname` = `s`.`svc_name` and `e`.`nodename` = `m`.`mon_nodname`;

alter table svcmon drop key svcmon_k1;

alter table dashboard add index i_dash_type (dash_type);
alter table dashboard add index i_dash_nodename (dash_nodename);
alter table dashboard engine=InnoDB;

alter table nodes add column maintenance_end datetime;

drop view v_nodes;

CREATE VIEW `v_nodes` AS (select `n`.`nodename` AS `nodename`,`n`.`loc_country` AS `loc_country`,`n`.`loc_city` AS `loc_city`,`n`.`loc_addr` AS `loc_addr`,`n`.`loc_building` AS `loc_building`,`n`.`loc_floor` AS `loc_floor`,`n`.`loc_room` AS `loc_room`,`n`.`loc_rack` AS `loc_rack`,`n`.`id` AS `id`,`n`.`cpu_freq` AS `cpu_freq`,`n`.`cpu_cores` AS `cpu_cores`,`n`.`cpu_dies` AS `cpu_dies`,`n`.`cpu_vendor` AS `cpu_vendor`,`n`.`cpu_model` AS `cpu_model`,`n`.`mem_banks` AS `mem_banks`,`n`.`mem_slots` AS `mem_slots`,`n`.`mem_bytes` AS `mem_bytes`,`n`.`os_name` AS `os_name`,`n`.`os_release` AS `os_release`,`n`.`os_update` AS `os_update`,`n`.`os_segment` AS `os_segment`,`n`.`os_arch` AS `os_arch`,`n`.`os_vendor` AS `os_vendor`,`n`.`os_kernel` AS `os_kernel`,`n`.`loc_zip` AS `loc_zip`,`n`.`team_responsible` AS `team_responsible`, n.team_integ as team_integ, n.team_support as team_support, n.project as project, `n`.`serial` AS `serial`,`n`.`model` AS `model`,`n`.`type` AS `type`,`n`.`warranty_end` AS `warranty_end`,`n`.`maintenance_end` AS `maintenance_end`,`n`.`status` AS `status`,`n`.`role` AS `role`,`n`.`environnement` AS `environnement`,n.host_mode as host_mode, `n`.`power_cabinet1` AS `power_cabinet1`,`n`.`power_cabinet2` AS `power_cabinet2`,`n`.`power_supply_nb` AS `power_supply_nb`,`n`.`power_protect` AS `power_protect`,`n`.`power_protect_breaker` AS `power_protect_breaker`,`n`.`power_breaker1` AS `power_breaker1`,`n`.`power_breaker2` AS `power_breaker2`,concat_ws(' ',`n`.`os_name`,`n`.`os_vendor`,`n`.`os_release`,`n`.`os_update`) AS `os_concat`,`n`.`updated` AS `updated` from `nodes` `n`);

drop view v_svcmon;

CREATE VIEW `v_svcmon` AS select `e`.`err` AS `err`,`s`.`svc_ha` AS `svc_ha`,`s`.`svc_cluster_type` AS `svc_cluster_type`,`s`.`svc_status` AS `svc_status`,`s`.`svc_availstatus` AS `svc_availstatus`,`s`.`svc_flex_min_nodes` AS `svc_flex_min_nodes`,`s`.`svc_flex_max_nodes` AS `svc_flex_max_nodes`,`s`.`svc_flex_cpu_low_threshold` AS `svc_flex_cpu_low_threshold`,`s`.`svc_flex_cpu_high_threshold` AS `svc_flex_cpu_high_threshold`,`m`.`mon_vmname` AS `mon_vmname`,`m`.`mon_guestos` AS `mon_guestos`,`s`.`svc_version` AS `svc_version`,`s`.`svc_name` AS `svc_name`,`s`.`svc_nodes` AS `svc_nodes`,`s`.`svc_drpnode` AS `svc_drpnode`,`s`.`svc_drpnodes` AS `svc_drpnodes`,`s`.`svc_drptype` AS `svc_drptype`,`s`.`svc_autostart` AS `svc_autostart`,`s`.`svc_type` AS `svc_type`,`s`.`svc_comment` AS `svc_comment`,`s`.`svc_app` AS `svc_app`,`s`.`svc_drnoaction` AS `svc_drnoaction`,`s`.`svc_created` AS `svc_created`,`s`.`updated` AS `svc_updated`,`s`.`svc_envdate` AS `svc_envdate`,`s`.`svc_containertype` AS `svc_containertype`,`s`.`svc_metrocluster` AS `svc_metrocluster`,`m`.`mon_vcpus` AS `mon_vcpus`,`m`.`mon_vmem` AS `mon_vmem`,`m`.`mon_svcname` AS `mon_svcname`,`m`.`mon_svctype` AS `mon_svctype`,`m`.`mon_drptype` AS `mon_drptype`,`m`.`mon_nodname` AS `mon_nodname`,`m`.`mon_nodtype` AS `mon_nodtype`,`m`.`mon_nodmode` AS `mon_nodmode`,`m`.`mon_ipstatus` AS `mon_ipstatus`,`m`.`mon_fsstatus` AS `mon_fsstatus`,`m`.`mon_prinodes` AS `mon_prinodes`,`m`.`mon_hostid` AS `mon_hostid`,`m`.`ID` AS `ID`,`m`.`mon_frozen` AS `mon_frozen`,`m`.`mon_frozentxt` AS `mon_frozentxt`,`m`.`mon_changed` AS `mon_changed`,`m`.`mon_updated` AS `mon_updated`,`m`.`mon_diskstatus` AS `mon_diskstatus`,`m`.`mon_containerstatus` AS `mon_containerstatus`,`m`.`mon_overallstatus` AS `mon_overallstatus`,`n`.`nodename` AS `nodename`,`n`.`updated` AS `node_updated`,`n`.`loc_country` AS `loc_country`,`n`.`loc_city` AS `loc_city`,`n`.`loc_addr` AS `loc_addr`,`n`.`loc_building` AS `loc_building`,`n`.`loc_floor` AS `loc_floor`,`n`.`loc_room` AS `loc_room`,`n`.`loc_rack` AS `loc_rack`,`n`.`cpu_freq` AS `cpu_freq`,`n`.`cpu_cores` AS `cpu_cores`,`n`.`cpu_dies` AS `cpu_dies`,`n`.`cpu_vendor` AS `cpu_vendor`,`n`.`cpu_model` AS `cpu_model`,`n`.`mem_banks` AS `mem_banks`,`n`.`mem_slots` AS `mem_slots`,`n`.`mem_bytes` AS `mem_bytes`,`n`.`os_name` AS `os_name`,`n`.`os_release` AS `os_release`,`n`.`os_update` AS `os_update`,`n`.`os_segment` AS `os_segment`,`n`.`os_arch` AS `os_arch`,`n`.`os_vendor` AS `os_vendor`,`n`.`os_kernel` AS `os_kernel`,`n`.`loc_zip` AS `loc_zip`,`n`.`team_responsible` AS `team_responsible`,`n`.`team_integ` AS `team_integ`,`n`.`team_support` AS `team_support`,`n`.`project` AS `project`,`n`.`serial` AS `serial`,`n`.`model` AS `model`,`n`.`type` AS `type`,`n`.`warranty_end` AS `warranty_end`,`n`.`maintenance_end` AS `maintenance_end`,`n`.`status` AS `status`,`n`.`role` AS `role`,`n`.`environnement` AS `environnement`,`n`.`host_mode` AS `host_mode`,`n`.`power_supply_nb` AS `power_supply_nb`,`n`.`power_cabinet1` AS `power_cabinet1`,`n`.`power_cabinet2` AS `power_cabinet2`,`n`.`power_protect` AS `power_protect`,`n`.`power_protect_breaker` AS `power_protect_breaker`,`n`.`power_breaker1` AS `power_breaker1`,`n`.`power_breaker2` AS `power_breaker2`,`m`.`mon_syncstatus` AS `mon_syncstatus`,`m`.`mon_hbstatus` AS `mon_hbstatus`,`m`.`mon_availstatus` AS `mon_availstatus`,`m`.`mon_appstatus` AS `mon_appstatus`,`ap`.`responsibles` AS `responsibles`,`ap`.`mailto` AS `mailto` from `svcmon` `m` left join `services` `s` on `s`.`svc_name` = `m`.`mon_svcname` left join `nodes` `n` on `m`.`mon_nodname` = `n`.`nodename` left join `b_apps` `ap` on `ap`.`app` = `s`.`svc_app` left join `b_action_errors` `e` on `e`.`svcname` = `s`.`svc_name` and `e`.`nodename` = `m`.`mon_nodname`;

drop view v_svcactions;

CREATE VIEW `v_svcactions` AS select `ac`.`cron` AS `cron`,`ac`.`time` AS `time`,`ac`.`version` AS `version`,`ac`.`svcname` AS `svcname`,`ac`.`action` AS `action`,`ac`.`status` AS `status`,`ac`.`begin` AS `begin`,`ac`.`end` AS `end`,`ac`.`hostname` AS `hostname`,`ac`.`hostid` AS `hostid`,`ac`.`status_log` AS `status_log`,`ac`.`pid` AS `pid`,`ac`.`ID` AS `ID`,`ac`.`ack` AS `ack`,`ac`.`alert` AS `alert`,`ac`.`acked_by` AS `acked_by`,`ac`.`acked_comment` AS `acked_comment`,`ac`.`acked_date` AS `acked_date`,`s`.`svc_ha` AS `svc_ha`,`s`.`svc_app` AS `app`,`a`.`mailto` AS `mailto`,`a`.`responsibles` AS `responsibles`,`n`.`nodename` AS `nodename`,`n`.`loc_country` AS `loc_country`,`n`.`loc_city` AS `loc_city`,`n`.`loc_addr` AS `loc_addr`,`n`.`loc_building` AS `loc_building`,`n`.`loc_floor` AS `loc_floor`,`n`.`loc_room` AS `loc_room`,`n`.`loc_rack` AS `loc_rack`,`n`.`cpu_freq` AS `cpu_freq`,`n`.`cpu_cores` AS `cpu_cores`,`n`.`cpu_dies` AS `cpu_dies`,`n`.`cpu_vendor` AS `cpu_vendor`,`n`.`cpu_model` AS `cpu_model`,`n`.`mem_banks` AS `mem_banks`,`n`.`mem_slots` AS `mem_slots`,`n`.`mem_bytes` AS `mem_bytes`,`n`.`os_name` AS `os_name`,`n`.`os_release` AS `os_release`,`n`.`os_update` AS `os_update`,`n`.`os_segment` AS `os_segment`,`n`.`os_arch` AS `os_arch`,`n`.`os_vendor` AS `os_vendor`,`n`.`os_kernel` AS `os_kernel`,`n`.`loc_zip` AS `loc_zip`,`n`.`team_responsible` AS `team_responsible`, n.team_integ as team_integ, n.team_support as team_support, n.project as project, `n`.`serial` AS `serial`,`n`.`model` AS `model`,`n`.`type` AS `type`,`n`.`warranty_end` AS `warranty_end`,`n`.`maintenance_end` AS `maintenance_end`,`n`.`status` AS `asset_status`,`n`.`role` AS `role`,`n`.`environnement` AS `environnement`, n.host_mode AS host_mode, `n`.`power_supply_nb` AS `power_supply_nb`,`n`.`power_cabinet1` AS `power_cabinet1`,`n`.`power_cabinet2` AS `power_cabinet2`,`n`.`power_protect` AS `power_protect`,`n`.`power_protect_breaker` AS `power_protect_breaker`,`n`.`power_breaker1` AS `power_breaker1`,`n`.`power_breaker2` AS `power_breaker2` from (((`SVCactions` `ac` join `services` `s` on((`s`.`svc_name` = `ac`.`svcname`))) join `nodes` `n` on((`ac`.`hostname` = `n`.`nodename`))) join `b_apps` `a` on((`a`.`app` = `s`.`svc_app`)));


drop view v_comp_nodes;

create view v_comp_nodes as (select n.*,group_concat(distinct r.ruleset_name separator ', ') as rulesets, group_concat(distinct m.modset_name separator ', ') as modulesets from v_nodes n left join comp_rulesets_nodes rn on n.nodename=rn.nodename left join comp_rulesets r on r.id=rn.ruleset_id left join comp_node_moduleset mn on mn.modset_node=n.nodename left join comp_moduleset m on m.id=mn.modset_id group by n.nodename);

#alter table dashboard add column dash_updated datetime;

alter table diskinfo add column disk_name varchar(120) default "";

alter table diskinfo add column disk_alloc int(11);

drop view v_svcdisks;

CREATE VIEW `v_svcdisks` AS select `s`.`id` AS `id`,`s`.`disk_id` AS `disk_id`,`s`.`disk_svcname` AS `disk_svcname`,`s`.`disk_nodename` AS `disk_nodename`,`s`.`disk_size` AS `disk_size`,s.disk_used as disk_used, `s`.`disk_vendor` AS `disk_vendor`,`s`.`disk_model` AS `disk_model`,`s`.`disk_dg` AS `disk_dg`,`s`.`disk_updated` AS `disk_updated`,`i`.`disk_devid` AS `disk_devid`,`i`.`disk_name` AS `disk_name`,`i`.`disk_alloc` AS `disk_alloc`,`i`.`disk_arrayid` AS `disk_arrayid` from (`svcdisks` `s` left join `diskinfo` `i` on((`s`.`disk_id` = convert(`i`.`disk_id` using utf8))));

drop view v_disk_app;

create view v_disk_app as 
                     select
                       diskinfo.id,
                       diskinfo.disk_id,
                       svcdisks.disk_region,
                       svcdisks.disk_svcname,
                       svcdisks.disk_nodename,
                       svcdisks.disk_vendor,
                       svcdisks.disk_model,
                       svcdisks.disk_dg,
                       svcdisks.disk_updated as svcdisk_updated,
                       svcdisks.id as svcdisk_id,
                       svcdisks.disk_local,
                       services.svc_app as app,
                       svcdisks.disk_used as disk_used,
                       diskinfo.disk_size,
                       diskinfo.disk_arrayid,
                       diskinfo.disk_group,
                       diskinfo.disk_devid,
                       diskinfo.disk_name,
                       diskinfo.disk_alloc,
                       diskinfo.disk_updated,
                       diskinfo.disk_raid,
                       diskinfo.disk_level
                     from
                       diskinfo
                     left join svcdisks on diskinfo.disk_id=svcdisks.disk_id
                     left join services on svcdisks.disk_svcname=services.svc_name
                     where svcdisks.disk_svcname != ""
                     union all
                     select
                       diskinfo.id,
                       diskinfo.disk_id,
                       svcdisks.disk_region,
                       svcdisks.disk_svcname,
                       svcdisks.disk_nodename,
                       svcdisks.disk_vendor,
                       svcdisks.disk_model,
                       svcdisks.disk_dg,
                       svcdisks.disk_updated as svcdisk_updated,
                       svcdisks.id as svcdisk_id,
                       svcdisks.disk_local,
                       nodes.project as app,
                       svcdisks.disk_used as disk_used,
                       diskinfo.disk_size,
                       diskinfo.disk_arrayid,
                       diskinfo.disk_group,
                       diskinfo.disk_devid,
                       diskinfo.disk_name,
                       diskinfo.disk_alloc,
                       diskinfo.disk_updated,
                       diskinfo.disk_raid,
                       diskinfo.disk_level
                     from
                       diskinfo
                     left join svcdisks on diskinfo.disk_id=svcdisks.disk_id
                     left join nodes on svcdisks.disk_nodename=nodes.nodename
                     where (svcdisks.disk_svcname = "" or svcdisks.disk_svcname is NULL)
;


alter table packages drop index idx3;

alter table packages add unique key idx3 (`pkg_nodename`,`pkg_name`,`pkg_arch`,`pkg_version`);


alter table column_filters modify col_filter text;

drop table if exists dashboard_events;

CREATE TABLE `dashboard_events` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `dash_nodename` varchar(60) DEFAULT NULL,
  `dash_svcname` varchar(60) DEFAULT NULL,
  `dash_md5` varchar(32) DEFAULT NULL,
  `dash_begin` datetime NOT NULL,
  `dash_end` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx1` (`dash_md5`)
);

drop table if exists dashboard_ref;

CREATE TABLE `dashboard_ref` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `dash_md5` varchar(32) DEFAULT NULL,
  `dash_type` varchar(60) DEFAULT NULL,
  `dash_fmt` varchar(100) DEFAULT NULL,
  `dash_dict` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx1` (`dash_md5`)
);


alter table dashboard add column dash_md5 varchar(32);
 
drop trigger if exists dash_add;

create trigger dash_add before insert on dashboard for each row set new.dash_md5 = md5(concat(new.dash_type, new.dash_fmt, new.dash_dict));

drop trigger if exists dash_add_evt;
delimiter #
create trigger dash_add_evt after insert on dashboard for each row
begin
 insert ignore into dashboard_ref (dash_md5, dash_fmt, dash_dict, dash_type) values (new.dash_md5, new.dash_fmt, new.dash_dict, new.dash_type) ; 
 insert into dashboard_events (dash_md5, dash_nodename, dash_svcname, dash_begin) values (new.dash_md5, new.dash_nodename, new.dash_svcname, now()) ; 
end#
delimiter ;

drop trigger if exists dash_del_evt;
delimiter #
create trigger dash_del_evt before delete on dashboard for each row begin update dashboard_events set dash_end=now() where dash_md5=old.dash_md5 and dash_nodename=old.dash_nodename and dash_svcname=old.dash_svcname and dash_end is null ; end#
delimiter ;


alter table checks_live modify column chk_instance varchar(100);

alter table checks_settings modify column chk_instance varchar(100);

alter table checks_defaults add column chk_prio integer default 0;

# display actions on services without "app" set
# (ie "left join b_apps" instead of "join")

drop view v_svcactions;

CREATE VIEW `v_svcactions` AS select `ac`.`cron` AS `cron`,`ac`.`time` AS `time`,`ac`.`version` AS `version`,`ac`.`svcname` AS `svcname`,`ac`.`action` AS `action`,`ac`.`status` AS `status`,`ac`.`begin` AS `begin`,`ac`.`end` AS `end`,`ac`.`hostname` AS `hostname`,`ac`.`hostid` AS `hostid`,`ac`.`status_log` AS `status_log`,`ac`.`pid` AS `pid`,`ac`.`ID` AS `ID`,`ac`.`ack` AS `ack`,`ac`.`alert` AS `alert`,`ac`.`acked_by` AS `acked_by`,`ac`.`acked_comment` AS `acked_comment`,`ac`.`acked_date` AS `acked_date`,`s`.`svc_ha` AS `svc_ha`,`s`.`svc_app` AS `app`,`a`.`mailto` AS `mailto`,`a`.`responsibles` AS `responsibles`,`n`.`nodename` AS `nodename`,`n`.`loc_country` AS `loc_country`,`n`.`loc_city` AS `loc_city`,`n`.`loc_addr` AS `loc_addr`,`n`.`loc_building` AS `loc_building`,`n`.`loc_floor` AS `loc_floor`,`n`.`loc_room` AS `loc_room`,`n`.`loc_rack` AS `loc_rack`,`n`.`cpu_freq` AS `cpu_freq`,`n`.`cpu_cores` AS `cpu_cores`,`n`.`cpu_dies` AS `cpu_dies`,`n`.`cpu_vendor` AS `cpu_vendor`,`n`.`cpu_model` AS `cpu_model`,`n`.`mem_banks` AS `mem_banks`,`n`.`mem_slots` AS `mem_slots`,`n`.`mem_bytes` AS `mem_bytes`,`n`.`os_name` AS `os_name`,`n`.`os_release` AS `os_release`,`n`.`os_update` AS `os_update`,`n`.`os_segment` AS `os_segment`,`n`.`os_arch` AS `os_arch`,`n`.`os_vendor` AS `os_vendor`,`n`.`os_kernel` AS `os_kernel`,`n`.`loc_zip` AS `loc_zip`,`n`.`team_responsible` AS `team_responsible`,`n`.`team_integ` AS `team_integ`,`n`.`team_support` AS `team_support`,`n`.`project` AS `project`,`n`.`serial` AS `serial`,`n`.`model` AS `model`,`n`.`type` AS `type`,`n`.`warranty_end` AS `warranty_end`,`n`.`maintenance_end` AS `maintenance_end`,`n`.`status` AS `asset_status`,`n`.`role` AS `role`,`n`.`environnement` AS `environnement`,`n`.`host_mode` AS `host_mode`,`n`.`power_supply_nb` AS `power_supply_nb`,`n`.`power_cabinet1` AS `power_cabinet1`,`n`.`power_cabinet2` AS `power_cabinet2`,`n`.`power_protect` AS `power_protect`,`n`.`power_protect_breaker` AS `power_protect_breaker`,`n`.`power_breaker1` AS `power_breaker1`,`n`.`power_breaker2` AS `power_breaker2` from (((`SVCactions` `ac` join `services` `s` on((`s`.`svc_name` = `ac`.`svcname`))) join `nodes` `n` on((`ac`.`hostname` = `n`.`nodename`))) left join `b_apps` `a` on((convert(`a`.`app` using utf8) = `s`.`svc_app`)));

create table u_inc as SELECT @row := @row + 1 as inc FROM apps t, (SELECT @row := 0) r;

alter table dashboard_events engine=InnoDB;

alter table dashboard_events add key idx2 (dash_begin, dash_end);

alter table nodes add column enclosure varchar(64);

drop view v_nodes;

create VIEW `v_nodes` AS (select `n`.`nodename` AS `nodename`,`n`.`loc_country` AS `loc_country`,`n`.`loc_city` AS `loc_city`,`n`.`loc_addr` AS `loc_addr`,`n`.`loc_building` AS `loc_building`,`n`.`loc_floor` AS `loc_floor`,`n`.`loc_room` AS `loc_room`,`n`.`loc_rack` AS `loc_rack`,`n`.`id` AS `id`,`n`.`cpu_freq` AS `cpu_freq`,`n`.`cpu_cores` AS `cpu_cores`,`n`.`cpu_dies` AS `cpu_dies`,`n`.`cpu_vendor` AS `cpu_vendor`,`n`.`cpu_model` AS `cpu_model`,`n`.`mem_banks` AS `mem_banks`,`n`.`mem_slots` AS `mem_slots`,`n`.`mem_bytes` AS `mem_bytes`,`n`.`os_name` AS `os_name`,`n`.`os_release` AS `os_release`,`n`.`os_update` AS `os_update`,`n`.`os_segment` AS `os_segment`,`n`.`os_arch` AS `os_arch`,`n`.`os_vendor` AS `os_vendor`,`n`.`os_kernel` AS `os_kernel`,`n`.`loc_zip` AS `loc_zip`,`n`.`team_responsible` AS `team_responsible`,`n`.`team_integ` AS `team_integ`,`n`.`team_support` AS `team_support`,`n`.`project` AS `project`,`n`.`serial` AS `serial`,`n`.`model` AS `model`,`n`.`type` AS `type`,`n`.`warranty_end` AS `warranty_end`,`n`.`maintenance_end` AS `maintenance_end`,`n`.`status` AS `status`,`n`.`role` AS `role`,`n`.`environnement` AS `environnement`,`n`.`host_mode` AS `host_mode`,`n`.`power_cabinet1` AS `power_cabinet1`,`n`.`power_cabinet2` AS `power_cabinet2`,`n`.`power_supply_nb` AS `power_supply_nb`,`n`.`power_protect` AS `power_protect`,`n`.`power_protect_breaker` AS `power_protect_breaker`,`n`.`power_breaker1` AS `power_breaker1`,`n`.`power_breaker2` AS `power_breaker2`,concat_ws(' ',`n`.`os_name`,`n`.`os_vendor`,`n`.`os_release`,`n`.`os_update`) AS `os_concat`,`n`.`updated` AS `updated`, n.enclosure as enclosure from `nodes` `n`);

drop view v_svcmon;

CREATE VIEW `v_svcmon` AS select `e`.`err` AS `err`,`s`.`svc_ha` AS `svc_ha`,`s`.`svc_cluster_type` AS `svc_cluster_type`,`s`.`svc_status` AS `svc_status`,`s`.`svc_availstatus` AS `svc_availstatus`,`s`.`svc_flex_min_nodes` AS `svc_flex_min_nodes`,`s`.`svc_flex_max_nodes` AS `svc_flex_max_nodes`,`s`.`svc_flex_cpu_low_threshold` AS `svc_flex_cpu_low_threshold`,`s`.`svc_flex_cpu_high_threshold` AS `svc_flex_cpu_high_threshold`,`m`.`mon_vmname` AS `mon_vmname`,`m`.`mon_guestos` AS `mon_guestos`,`s`.`svc_version` AS `svc_version`,`s`.`svc_name` AS `svc_name`,`s`.`svc_nodes` AS `svc_nodes`,`s`.`svc_drpnode` AS `svc_drpnode`,`s`.`svc_drpnodes` AS `svc_drpnodes`,`s`.`svc_drptype` AS `svc_drptype`,`s`.`svc_autostart` AS `svc_autostart`,`s`.`svc_type` AS `svc_type`,`s`.`svc_comment` AS `svc_comment`,`s`.`svc_app` AS `svc_app`,`s`.`svc_drnoaction` AS `svc_drnoaction`,`s`.`svc_created` AS `svc_created`,`s`.`updated` AS `svc_updated`,`s`.`svc_envdate` AS `svc_envdate`,`s`.`svc_containertype` AS `svc_containertype`,`s`.`svc_metrocluster` AS `svc_metrocluster`,`m`.`mon_vcpus` AS `mon_vcpus`,`m`.`mon_vmem` AS `mon_vmem`,`m`.`mon_svcname` AS `mon_svcname`,`m`.`mon_svctype` AS `mon_svctype`,`m`.`mon_drptype` AS `mon_drptype`,`m`.`mon_nodname` AS `mon_nodname`,`m`.`mon_nodtype` AS `mon_nodtype`,`m`.`mon_nodmode` AS `mon_nodmode`,`m`.`mon_ipstatus` AS `mon_ipstatus`,`m`.`mon_fsstatus` AS `mon_fsstatus`,`m`.`mon_prinodes` AS `mon_prinodes`,`m`.`mon_hostid` AS `mon_hostid`,`m`.`ID` AS `ID`,`m`.`mon_frozen` AS `mon_frozen`,`m`.`mon_frozentxt` AS `mon_frozentxt`,`m`.`mon_changed` AS `mon_changed`,`m`.`mon_updated` AS `mon_updated`,`m`.`mon_diskstatus` AS `mon_diskstatus`,`m`.`mon_containerstatus` AS `mon_containerstatus`,`m`.`mon_overallstatus` AS `mon_overallstatus`,`n`.`nodename` AS `nodename`,`n`.`updated` AS `node_updated`,`n`.`loc_country` AS `loc_country`,`n`.`loc_city` AS `loc_city`,`n`.`loc_addr` AS `loc_addr`,`n`.`loc_building` AS `loc_building`,`n`.`loc_floor` AS `loc_floor`,`n`.`loc_room` AS `loc_room`,`n`.`loc_rack` AS `loc_rack`,`n`.`cpu_freq` AS `cpu_freq`,`n`.`cpu_cores` AS `cpu_cores`,`n`.`cpu_dies` AS `cpu_dies`,`n`.`cpu_vendor` AS `cpu_vendor`,`n`.`cpu_model` AS `cpu_model`,`n`.`mem_banks` AS `mem_banks`,`n`.`mem_slots` AS `mem_slots`,`n`.`mem_bytes` AS `mem_bytes`,`n`.`os_name` AS `os_name`,`n`.`os_release` AS `os_release`,`n`.`os_update` AS `os_update`,`n`.`os_segment` AS `os_segment`,`n`.`os_arch` AS `os_arch`,`n`.`os_vendor` AS `os_vendor`,`n`.`os_kernel` AS `os_kernel`,`n`.`loc_zip` AS `loc_zip`,`n`.`team_responsible` AS `team_responsible`,`n`.`team_integ` AS `team_integ`,`n`.`team_support` AS `team_support`,`n`.`project` AS `project`,`n`.`serial` AS `serial`,`n`.`model` AS `model`,`n`.`type` AS `type`,`n`.`warranty_end` AS `warranty_end`,`n`.`maintenance_end` AS `maintenance_end`,`n`.`status` AS `status`,`n`.`role` AS `role`,`n`.`environnement` AS `environnement`,`n`.`host_mode` AS `host_mode`,`n`.`power_supply_nb` AS `power_supply_nb`,`n`.`power_cabinet1` AS `power_cabinet1`,`n`.`power_cabinet2` AS `power_cabinet2`,`n`.`power_protect` AS `power_protect`,`n`.`power_protect_breaker` AS `power_protect_breaker`,`n`.`power_breaker1` AS `power_breaker1`,`n`.`power_breaker2` AS `power_breaker2`,`m`.`mon_syncstatus` AS `mon_syncstatus`,`m`.`mon_hbstatus` AS `mon_hbstatus`,`m`.`mon_availstatus` AS `mon_availstatus`,`m`.`mon_appstatus` AS `mon_appstatus`,`ap`.`responsibles` AS `responsibles`,`ap`.`mailto` AS `mailto`, n.enclosure as enclosure from ((((`svcmon` `m` left join `services` `s` on((`s`.`svc_name` = `m`.`mon_svcname`))) left join `nodes` `n` on((`m`.`mon_nodname` = `n`.`nodename`))) left join `b_apps` `ap` on((`ap`.`app` = `s`.`svc_app`))) left join `b_action_errors` `e` on(((`e`.`svcname` = `s`.`svc_name`) and (`e`.`nodename` = `m`.`mon_nodname`))));

drop view v_comp_nodes;

create view v_comp_nodes as (select n.*,group_concat(distinct r.ruleset_name separator ', ') as rulesets, group_concat(distinct m.modset_name separator ', ') as modulesets from v_nodes n left join comp_rulesets_nodes rn on n.nodename=rn.nodename left join comp_rulesets r on r.id=rn.ruleset_id left join comp_node_moduleset mn on mn.modset_node=n.nodename left join comp_moduleset m on m.id=mn.modset_id group by n.nodename);

#drop table nodes_import;

#create table nodes_import as select * from nodes;

alter table dashboard add column dash_updated datetime;

CREATE TABLE  `opensvc`.`saves` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `save_nodename` varchar(60) NOT NULL,
  `save_svcname` varchar(60) NOT NULL,
  `save_name` varchar(200) NOT NULL,
  `save_group` varchar(100) NOT NULL,
  `save_size` int(11) NOT NULL,
  `save_date` datetime NOT NULL,
  `save_retention` datetime NOT NULL,
  `save_volume` varchar(64) NOT NULL,
  `save_level` varchar(8) NOT NULL,
  `save_server` varchar(60) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx1` (`save_nodename`,`save_svcname`,`save_name`, `save_level`)
) ENGINE=InnoDB;

alter table saves modify column save_size bigint;

alter table saves add save_app varchar(64);

alter table saves add column save_id varchar(64);

alter table saves drop key idx1;

alter table saves add unique key idx1 (save_server, save_id, save_volume);

alter table packages drop foreign key packages_ibfk_1;

alter table packages add foreign key packages_ibfk_1 (`pkg_nodename`) REFERENCES `nodes` (`nodename`) ON DELETE CASCADE ON UPDATE CASCADE;

alter table patches drop foreign key patches_ibfk_1;

alter table patches add foreign key patches_ibfk_1 (`patch_nodename`) REFERENCES `nodes` (`nodename`) ON DELETE CASCADE ON UPDATE CASCADE;

alter table comp_node_moduleset drop foreign key comp_node_moduleset_fk2;

alter table comp_node_moduleset add foreign key comp_node_moduleset_fk2 (`modset_node`) REFERENCES `nodes` (`nodename`) ON DELETE CASCADE ON UPDATE CASCADE;

alter table comp_rulesets_nodes drop foreign key comp_rulesets_nodes_fk2;

alter table comp_rulesets_nodes add foreign key comp_rulesets_nodes_fk2 (`nodename`) REFERENCES `nodes` (`nodename`) ON DELETE CASCADE ON UPDATE CASCADE;

alter table svcmon drop foreign key svcmon_ibfk_1;

alter table svcmon add foreign key svcmon_ibfk_1 (`mon_nodname`) REFERENCES `nodes` (`nodename`) ON DELETE CASCADE ON UPDATE CASCADE;

alter table svcdisks drop foreign key svcdisks_ibfk_1;

alter table svcdisks add foreign key svcdisks_ibfk_1 (disk_nodename) REFERENCES nodes (nodename) ON DELETE CASCADE ON UPDATE CASCADE;

alter table svcmon modify column mon_vmname varchar(192);

alter table saves add key idx2 (save_nodename, save_svcname);

delete from comp_run_ruleset where rset_md5 not in (select distinct rset_md5 from comp_log);

alter table stor_array_tgtid add column updated timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;

alter table resmon modify column rid varchar(16);

alter table svcmon drop key mon_svcname_5;

alter table svcmon add unique key mon_svcname_5 (`mon_svcname`,`mon_nodname`, mon_vmname);

alter table svcmon modify column mon_vmname varchar(50) default "";

alter table resmon add column vmname varchar(60) default "";

alter table svcmon add column mon_vmtype varchar(10);

drop view v_svcmon;

CREATE VIEW `v_svcmon` AS select `e`.`err` AS `err`,`s`.`svc_ha` AS `svc_ha`,`s`.`svc_cluster_type` AS `svc_cluster_type`,`s`.`svc_status` AS `svc_status`,`s`.`svc_availstatus` AS `svc_availstatus`,`s`.`svc_flex_min_nodes` AS `svc_flex_min_nodes`,`s`.`svc_flex_max_nodes` AS `svc_flex_max_nodes`,`s`.`svc_flex_cpu_low_threshold` AS `svc_flex_cpu_low_threshold`,`s`.`svc_flex_cpu_high_threshold` AS `svc_flex_cpu_high_threshold`,`m`.`mon_vmname` AS `mon_vmname`,`m`.`mon_vmtype` AS `mon_vmtype`,`m`.`mon_guestos` AS `mon_guestos`,`s`.`svc_version` AS `svc_version`,`s`.`svc_name` AS `svc_name`,`s`.`svc_nodes` AS `svc_nodes`,`s`.`svc_drpnode` AS `svc_drpnode`,`s`.`svc_drpnodes` AS `svc_drpnodes`,`s`.`svc_drptype` AS `svc_drptype`,`s`.`svc_autostart` AS `svc_autostart`,`s`.`svc_type` AS `svc_type`,`s`.`svc_comment` AS `svc_comment`,`s`.`svc_app` AS `svc_app`,`s`.`svc_drnoaction` AS `svc_drnoaction`,`s`.`svc_created` AS `svc_created`,`s`.`updated` AS `svc_updated`,`s`.`svc_envdate` AS `svc_envdate`,`s`.`svc_containertype` AS `svc_containertype`,`s`.`svc_metrocluster` AS `svc_metrocluster`,`m`.`mon_vcpus` AS `mon_vcpus`,`m`.`mon_vmem` AS `mon_vmem`,`m`.`mon_svcname` AS `mon_svcname`,`m`.`mon_svctype` AS `mon_svctype`,`m`.`mon_drptype` AS `mon_drptype`,`m`.`mon_nodname` AS `mon_nodname`,`m`.`mon_nodtype` AS `mon_nodtype`,`m`.`mon_nodmode` AS `mon_nodmode`,`m`.`mon_ipstatus` AS `mon_ipstatus`,`m`.`mon_fsstatus` AS `mon_fsstatus`,`m`.`mon_prinodes` AS `mon_prinodes`,`m`.`mon_hostid` AS `mon_hostid`,`m`.`ID` AS `ID`,`m`.`mon_frozen` AS `mon_frozen`,`m`.`mon_frozentxt` AS `mon_frozentxt`,`m`.`mon_changed` AS `mon_changed`,`m`.`mon_updated` AS `mon_updated`,`m`.`mon_diskstatus` AS `mon_diskstatus`,`m`.`mon_containerstatus` AS `mon_containerstatus`,`m`.`mon_overallstatus` AS `mon_overallstatus`,`n`.`nodename` AS `nodename`,`n`.`updated` AS `node_updated`,`n`.`loc_country` AS `loc_country`,`n`.`loc_city` AS `loc_city`,`n`.`loc_addr` AS `loc_addr`,`n`.`loc_building` AS `loc_building`,`n`.`loc_floor` AS `loc_floor`,`n`.`loc_room` AS `loc_room`,`n`.`loc_rack` AS `loc_rack`,`n`.`cpu_freq` AS `cpu_freq`,`n`.`cpu_cores` AS `cpu_cores`,`n`.`cpu_dies` AS `cpu_dies`,`n`.`cpu_vendor` AS `cpu_vendor`,`n`.`cpu_model` AS `cpu_model`,`n`.`mem_banks` AS `mem_banks`,`n`.`mem_slots` AS `mem_slots`,`n`.`mem_bytes` AS `mem_bytes`,`n`.`os_name` AS `os_name`,`n`.`os_release` AS `os_release`,`n`.`os_update` AS `os_update`,`n`.`os_segment` AS `os_segment`,`n`.`os_arch` AS `os_arch`,`n`.`os_vendor` AS `os_vendor`,`n`.`os_kernel` AS `os_kernel`,`n`.`loc_zip` AS `loc_zip`,`n`.`team_responsible` AS `team_responsible`,`n`.`team_integ` AS `team_integ`,`n`.`team_support` AS `team_support`,`n`.`project` AS `project`,`n`.`serial` AS `serial`,`n`.`model` AS `model`,`n`.`type` AS `type`,`n`.`warranty_end` AS `warranty_end`,`n`.`maintenance_end` AS `maintenance_end`,`n`.`status` AS `status`,`n`.`role` AS `role`,`n`.`environnement` AS `environnement`,`n`.`host_mode` AS `host_mode`,`n`.`power_supply_nb` AS `power_supply_nb`,`n`.`power_cabinet1` AS `power_cabinet1`,`n`.`power_cabinet2` AS `power_cabinet2`,`n`.`power_protect` AS `power_protect`,`n`.`power_protect_breaker` AS `power_protect_breaker`,`n`.`power_breaker1` AS `power_breaker1`,`n`.`power_breaker2` AS `power_breaker2`,`m`.`mon_syncstatus` AS `mon_syncstatus`,`m`.`mon_hbstatus` AS `mon_hbstatus`,`m`.`mon_availstatus` AS `mon_availstatus`,`m`.`mon_appstatus` AS `mon_appstatus`,`ap`.`responsibles` AS `responsibles`,`ap`.`mailto` AS `mailto`, n.enclosure as enclosure from ((((`svcmon` `m` left join `services` `s` on((`s`.`svc_name` = `m`.`mon_svcname`))) left join `nodes` `n` on((`m`.`mon_nodname` = `n`.`nodename`))) left join `b_apps` `ap` on((`ap`.`app` = `s`.`svc_app`))) left join `b_action_errors` `e` on(((`e`.`svcname` = `s`.`svc_name`) and (`e`.`nodename` = `m`.`mon_nodname`))));

alter table resmon drop key resmon_1;

alter table resmon add unique key resmon_1 (`svcname`,`nodename`,`vmname`, `rid`);

alter table checks_live add column chk_err tinyint default 0;

alter table stats_svc add column cap_cpu float default 1;

update stats_svc set cap_cpu=(select mon_vcpus from svcmon s where s.mon_svcname=svcname and s.mon_nodname=nodename) ;

#

alter table comp_rulesets_services add column slave varchar(1) DEFAULT 'F';

alter table comp_modulesets_services add column slave varchar(1) DEFAULT 'F';

alter table comp_rulesets_services drop key idx1;

alter table comp_rulesets_services add unique key (ruleset_id,svcname,slave);

alter table comp_modulesets_services drop key idx1;

alter table comp_modulesets_services add unique key idx1 (modset_svcname,modset_id,slave);

CREATE TABLE `stats_fs_u_diff` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `begin` datetime NOT NULL,
  `end` datetime NOT NULL,
  `nodename` varchar(60) NOT NULL,
  `mntpt` varchar(200) NOT NULL,
  `size` bigint(20) DEFAULT NULL,
  `used` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=179025 DEFAULT CHARSET=utf8;

CREATE TABLE `stats_fs_u_last` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `begin` datetime NOT NULL,
  `end` datetime NOT NULL,
  `nodename` varchar(60) NOT NULL,
  `mntpt` varchar(200) NOT NULL,
  `size` bigint(20) DEFAULT NULL,
  `used` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `index_1` (`nodename`, `mntpt`)
) ENGINE=InnoDB AUTO_INCREMENT=179025 DEFAULT CHARSET=utf8;

#drop trigger if exists stats_fs_u_add;
#delimiter #
#create trigger stats_fs_u_add before insert on stats_fs_u for each row
#begin
# declare _size bigint ;
# declare _used int ;
# set _size = (select size from stats_fs_u_last where nodename=new.nodename and mntpt=new.mntpt) ;
# set _used = (select used from stats_fs_u_last where nodename=new.nodename and mntpt=new.mntpt) ;
# if (_size is null) then
#  insert into stats_fs_u_last (begin, end, nodename, mntpt, size, used) values (new.date, new.date, new.nodename, new.mntpt, new.size, new.used) ;
#  set _size = new.size ;
#  set _used = new.used ;
# end if ;
#
# if (new.size != _size or new.used != _used) then
#  insert into stats_fs_u_diff (select null, begin, end, nodename, mntpt, size, used from stats_fs_u_last where nodename=new.nodename and mntpt=new.mntpt) ;
#  update stats_fs_u_last set begin=new.date, end=new.date, size=new.size, used=new.used where nodename=new.nodename and mntpt=new.mntpt ;
# else
#  update stats_fs_u_last set end=new.date ;
# end if ;
#  
# set new.date = "0000-00-00 00:00:00" ;
#end#
#delimiter ;

alter table comp_rulesets add column ruleset_public varchar(1) default 'T';

drop view v_comp_rulesets ;

CREATE VIEW `v_comp_rulesets` AS (select `r`.`id` AS `ruleset_id`,`r`.`ruleset_name` AS `ruleset_name`,`r`.`ruleset_type` AS `ruleset_type`, r.ruleset_public as ruleset_public, group_concat(distinct `g`.`role` separator ', ') AS `teams_responsible`,(select `comp_rulesets`.`ruleset_name` from `comp_rulesets` where (`comp_rulesets`.`id` = `rr`.`child_rset_id`)) AS `encap_rset`,`rr`.`child_rset_id` AS `encap_rset_id`,`rv`.`id` AS `id`,`rv`.`var_name` AS `var_name`,`rv`.`var_class` AS `var_class`,`rv`.`var_value` AS `var_value`,`rv`.`var_author` AS `var_author`,`rv`.`var_updated` AS `var_updated`,`rf`.`fset_id` AS `fset_id`,`fs`.`fset_name` AS `fset_name` from ((((((`comp_rulesets` `r` left join `comp_rulesets_rulesets` `rr` on((`r`.`id` = `rr`.`parent_rset_id`))) left join `comp_rulesets_variables` `rv` on((((`rv`.`ruleset_id` = `r`.`id`) and isnull(`rr`.`child_rset_id`)) or (`rv`.`ruleset_id` = `rr`.`child_rset_id`)))) left join `comp_rulesets_filtersets` `rf` on((`r`.`id` = `rf`.`ruleset_id`))) left join `gen_filtersets` `fs` on((`fs`.`id` = `rf`.`fset_id`))) left join `comp_ruleset_team_responsible` `rt` on((`r`.`id` = `rt`.`ruleset_id`))) left join `auth_group` `g` on((`rt`.`group_id` = `g`.`id`))) group by `r`.`id`,`rv`.`id`,`rr`.`id`);

alter table auth_group add column privilege varchar(1) default 'F';

update auth_group set privilege='T' where role like "%Manager" or role like "%Exec";

alter table nodes add column hw_obs_warn_date datetime ;
alter table nodes add column hw_obs_alert_date datetime ;
alter table nodes add column os_obs_warn_date datetime ;
alter table nodes add column os_obs_alert_date datetime ;

alter table nodes_import add column hw_obs_warn_date datetime ;
alter table nodes_import add column hw_obs_alert_date datetime ;
alter table nodes_import add column os_obs_warn_date datetime ;
alter table nodes_import add column os_obs_alert_date datetime ;

drop view v_nodes ;

create view v_nodes as (select `n`.`nodename` AS `nodename`,`n`.`loc_country` AS `loc_country`,`n`.`loc_city` AS `loc_city`,`n`.`loc_addr` AS `loc_addr`,`n`.`loc_building` AS `loc_building`,`n`.`loc_floor` AS `loc_floor`,`n`.`loc_room` AS `loc_room`,`n`.`loc_rack` AS `loc_rack`,`n`.`id` AS `id`,`n`.`cpu_freq` AS `cpu_freq`,`n`.`cpu_cores` AS `cpu_cores`,`n`.`cpu_dies` AS `cpu_dies`,`n`.`cpu_vendor` AS `cpu_vendor`,`n`.`cpu_model` AS `cpu_model`,`n`.`mem_banks` AS `mem_banks`,`n`.`mem_slots` AS `mem_slots`,`n`.`mem_bytes` AS `mem_bytes`,`n`.`os_name` AS `os_name`,`n`.`os_release` AS `os_release`,`n`.`os_update` AS `os_update`,`n`.`os_segment` AS `os_segment`,`n`.`os_arch` AS `os_arch`,`n`.`os_vendor` AS `os_vendor`,`n`.`os_kernel` AS `os_kernel`,`n`.`loc_zip` AS `loc_zip`,`n`.`team_responsible` AS `team_responsible`,`n`.`team_integ` AS `team_integ`,`n`.`team_support` AS `team_support`,`n`.`project` AS `project`,`n`.`serial` AS `serial`,`n`.`model` AS `model`,`n`.`type` AS `type`,`n`.`warranty_end` AS `warranty_end`,`n`.`maintenance_end` AS `maintenance_end`,`n`.`status` AS `status`,`n`.`role` AS `role`,`n`.`environnement` AS `environnement`,`n`.`host_mode` AS `host_mode`,`n`.`power_cabinet1` AS `power_cabinet1`,`n`.`power_cabinet2` AS `power_cabinet2`,`n`.`power_supply_nb` AS `power_supply_nb`,`n`.`power_protect` AS `power_protect`,`n`.`power_protect_breaker` AS `power_protect_breaker`,`n`.`power_breaker1` AS `power_breaker1`,`n`.`power_breaker2` AS `power_breaker2`,concat_ws(' ',`n`.`os_name`,`n`.`os_vendor`,`n`.`os_release`,`n`.`os_update`) AS `os_concat`,`n`.`updated` AS `updated`,`n`.`enclosure` AS `enclosure`, n.hw_obs_warn_date as hw_obs_warn_date, n.hw_obs_alert_date as hw_obs_alert_date, n.os_obs_warn_date as os_obs_warn_date, n.os_obs_alert_date as os_obs_alert_date from `nodes` `n`);

CREATE TABLE `comp_forms` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `form_name` varchar(100) DEFAULT NULL,
  `form_yaml` text,
  `form_comment` text,
  `form_author` varchar(100) DEFAULT NULL,
  `form_created` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx1` (`form_name`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8

alter table log modify column log_fmt varchar(200);
