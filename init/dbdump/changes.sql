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

CREATE ALGORITHM=UNDEFINED DEFINER=`opensvc`@`unxdevweb` SQL SECURITY DEFINER VIEW `v_svcmon` AS select (select count(`a`.`ID`) AS `count(a.id)` from `SVCactions` `a` where ((convert(`m`.`mon_nodname` using utf8) = `a`.`hostname`) and (`a`.`svcname` = `s`.`svc_name`) and (`a`.`status` = 'err') and ((`a`.`ack` <> 1) or isnull(`a`.`ack`)))) AS `err`,`s`.`svc_cluster_type` AS `svc_cluster_type`,`s`.`svc_status` AS `svc_status`,`s`.`svc_availstatus` AS `svc_availstatus`,`s`.`svc_flex_min_nodes` AS `svc_flex_min_nodes`,`s`.`svc_flex_max_nodes` AS `svc_flex_max_nodes`,`s`.`svc_flex_cpu_low_threshold` AS `svc_flex_cpu_low_threshold`,`s`.`svc_flex_cpu_high_threshold` AS `svc_flex_cpu_high_threshold`,`s`.`svc_vmname` AS `svc_vmname`,`s`.`svc_guestos` AS `svc_guestos`,`s`.`svc_version` AS `svc_version`,`s`.`svc_name` AS `svc_name`,`s`.`svc_nodes` AS `svc_nodes`,`s`.`svc_drpnode` AS `svc_drpnode`,`s`.`svc_drpnodes` AS `svc_drpnodes`,`s`.`svc_drptype` AS `svc_drptype`,`s`.`svc_autostart` AS `svc_autostart`,`s`.`svc_type` AS `svc_type`,`s`.`svc_comment` AS `svc_comment`,`s`.`svc_app` AS `svc_app`,`s`.`svc_drnoaction` AS `svc_drnoaction`,`s`.`svc_created` AS `svc_created`,`s`.`updated` AS `svc_updated`,`s`.`svc_envdate` AS `svc_envdate`,`s`.`svc_containertype` AS `svc_containertype`,`s`.`svc_metrocluster` AS `svc_metrocluster`,`s`.`svc_vcpus` AS `svc_vcpus`,`s`.`svc_vmem` AS `svc_vmem`,`m`.`mon_svcname` AS `mon_svcname`,`m`.`mon_svctype` AS `mon_svctype`,`m`.`mon_drptype` AS `mon_drptype`,`m`.`mon_nodname` AS `mon_nodname`,`m`.`mon_nodtype` AS `mon_nodtype`,`m`.`mon_nodmode` AS `mon_nodmode`,`m`.`mon_ipstatus` AS `mon_ipstatus`,`m`.`mon_fsstatus` AS `mon_fsstatus`,`m`.`mon_prinodes` AS `mon_prinodes`,`m`.`mon_hostid` AS `mon_hostid`,`m`.`ID` AS `ID`,`m`.`mon_frozen` AS `mon_frozen`,`m`.`mon_frozentxt` AS `mon_frozentxt`,`m`.`mon_changed` AS `mon_changed`,`m`.`mon_updated` AS `mon_updated`,`m`.`mon_diskstatus` AS `mon_diskstatus`,`m`.`mon_containerstatus` AS `mon_containerstatus`,`m`.`mon_overallstatus` AS `mon_overallstatus`,`n`.`nodename` AS `nodename`,`n`.`updated` AS `node_updated`,`n`.`loc_country` AS `loc_country`,`n`.`loc_city` AS `loc_city`,`n`.`loc_addr` AS `loc_addr`,`n`.`loc_building` AS `loc_building`,`n`.`loc_floor` AS `loc_floor`,`n`.`loc_room` AS `loc_room`,`n`.`loc_rack` AS `loc_rack`,`n`.`cpu_freq` AS `cpu_freq`,`n`.`cpu_cores` AS `cpu_cores`,`n`.`cpu_dies` AS `cpu_dies`,`n`.`cpu_vendor` AS `cpu_vendor`,`n`.`cpu_model` AS `cpu_model`,`n`.`mem_banks` AS `mem_banks`,`n`.`mem_slots` AS `mem_slots`,`n`.`mem_bytes` AS `mem_bytes`,`n`.`os_name` AS `os_name`,`n`.`os_release` AS `os_release`,`n`.`os_update` AS `os_update`,`n`.`os_segment` AS `os_segment`,`n`.`os_arch` AS `os_arch`,`n`.`os_vendor` AS `os_vendor`,`n`.`os_kernel` AS `os_kernel`,`n`.`loc_zip` AS `loc_zip`,`n`.`team_responsible` AS `team_responsible`,`n`.`serial` AS `serial`,`n`.`model` AS `model`,`n`.`type` AS `type`,`n`.`warranty_end` AS `warranty_end`,`n`.`status` AS `status`,`n`.`role` AS `role`,`n`.`environnement` AS `environnement`,`n`.`power_supply_nb` AS `power_supply_nb`,`n`.`power_cabinet1` AS `power_cabinet1`,`n`.`power_cabinet2` AS `power_cabinet2`,`n`.`power_protect` AS `power_protect`,`n`.`power_protect_breaker` AS `power_protect_breaker`,`n`.`power_breaker1` AS `power_breaker1`,`n`.`power_breaker2` AS `power_breaker2`,`m`.`mon_syncstatus` AS `mon_syncstatus`,`m`.`mon_hbstatus` AS `mon_hbstatus`,`m`.`mon_availstatus` AS `mon_availstatus`,`m`.`mon_appstatus` AS `mon_appstatus`, ap.responsibles as responsibles, ap.mailto as mailto from `svcmon` `m` left join `services` `s` on `s`.`svc_name` = `m`.`mon_svcname` left join `nodes` `n` on `m`.`mon_nodname` = `n`.`nodename` left join b_apps ap on ap.app=s.svc_app;

create table b_action_errors (`id` int(11) NOT NULL AUTO_INCREMENT, `svcname` varchar(60) NOT NULL, nodename varchar(60) not null, `err` int(11) NOT NULL, PRIMARY KEY (`id`), UNIQUE KEY `i_svcname` (`svcname`, `nodename`));

drop view v_svcmon;

CREATE ALGORITHM=UNDEFINED DEFINER=`opensvc`@`unxdevweb` SQL SECURITY DEFINER VIEW `v_svcmon` AS select e.err AS `err`,`s`.`svc_cluster_type` AS `svc_cluster_type`,`s`.`svc_status` AS `svc_status`,`s`.`svc_availstatus` AS `svc_availstatus`,`s`.`svc_flex_min_nodes` AS `svc_flex_min_nodes`,`s`.`svc_flex_max_nodes` AS `svc_flex_max_nodes`,`s`.`svc_flex_cpu_low_threshold` AS `svc_flex_cpu_low_threshold`,`s`.`svc_flex_cpu_high_threshold` AS `svc_flex_cpu_high_threshold`,`s`.`svc_vmname` AS `svc_vmname`,`s`.`svc_guestos` AS `svc_guestos`,`s`.`svc_version` AS `svc_version`,`s`.`svc_name` AS `svc_name`,`s`.`svc_nodes` AS `svc_nodes`,`s`.`svc_drpnode` AS `svc_drpnode`,`s`.`svc_drpnodes` AS `svc_drpnodes`,`s`.`svc_drptype` AS `svc_drptype`,`s`.`svc_autostart` AS `svc_autostart`,`s`.`svc_type` AS `svc_type`,`s`.`svc_comment` AS `svc_comment`,`s`.`svc_app` AS `svc_app`,`s`.`svc_drnoaction` AS `svc_drnoaction`,`s`.`svc_created` AS `svc_created`,`s`.`updated` AS `svc_updated`,`s`.`svc_envdate` AS `svc_envdate`,`s`.`svc_containertype` AS `svc_containertype`,`s`.`svc_metrocluster` AS `svc_metrocluster`,`s`.`svc_vcpus` AS `svc_vcpus`,`s`.`svc_vmem` AS `svc_vmem`,`m`.`mon_svcname` AS `mon_svcname`,`m`.`mon_svctype` AS `mon_svctype`,`m`.`mon_drptype` AS `mon_drptype`,`m`.`mon_nodname` AS `mon_nodname`,`m`.`mon_nodtype` AS `mon_nodtype`,`m`.`mon_nodmode` AS `mon_nodmode`,`m`.`mon_ipstatus` AS `mon_ipstatus`,`m`.`mon_fsstatus` AS `mon_fsstatus`,`m`.`mon_prinodes` AS `mon_prinodes`,`m`.`mon_hostid` AS `mon_hostid`,`m`.`ID` AS `ID`,`m`.`mon_frozen` AS `mon_frozen`,`m`.`mon_frozentxt` AS `mon_frozentxt`,`m`.`mon_changed` AS `mon_changed`,`m`.`mon_updated` AS `mon_updated`,`m`.`mon_diskstatus` AS `mon_diskstatus`,`m`.`mon_containerstatus` AS `mon_containerstatus`,`m`.`mon_overallstatus` AS `mon_overallstatus`,`n`.`nodename` AS `nodename`,`n`.`updated` AS `node_updated`,`n`.`loc_country` AS `loc_country`,`n`.`loc_city` AS `loc_city`,`n`.`loc_addr` AS `loc_addr`,`n`.`loc_building` AS `loc_building`,`n`.`loc_floor` AS `loc_floor`,`n`.`loc_room` AS `loc_room`,`n`.`loc_rack` AS `loc_rack`,`n`.`cpu_freq` AS `cpu_freq`,`n`.`cpu_cores` AS `cpu_cores`,`n`.`cpu_dies` AS `cpu_dies`,`n`.`cpu_vendor` AS `cpu_vendor`,`n`.`cpu_model` AS `cpu_model`,`n`.`mem_banks` AS `mem_banks`,`n`.`mem_slots` AS `mem_slots`,`n`.`mem_bytes` AS `mem_bytes`,`n`.`os_name` AS `os_name`,`n`.`os_release` AS `os_release`,`n`.`os_update` AS `os_update`,`n`.`os_segment` AS `os_segment`,`n`.`os_arch` AS `os_arch`,`n`.`os_vendor` AS `os_vendor`,`n`.`os_kernel` AS `os_kernel`,`n`.`loc_zip` AS `loc_zip`,`n`.`team_responsible` AS `team_responsible`,`n`.`serial` AS `serial`,`n`.`model` AS `model`,`n`.`type` AS `type`,`n`.`warranty_end` AS `warranty_end`,`n`.`status` AS `status`,`n`.`role` AS `role`,`n`.`environnement` AS `environnement`,`n`.`power_supply_nb` AS `power_supply_nb`,`n`.`power_cabinet1` AS `power_cabinet1`,`n`.`power_cabinet2` AS `power_cabinet2`,`n`.`power_protect` AS `power_protect`,`n`.`power_protect_breaker` AS `power_protect_breaker`,`n`.`power_breaker1` AS `power_breaker1`,`n`.`power_breaker2` AS `power_breaker2`,`m`.`mon_syncstatus` AS `mon_syncstatus`,`m`.`mon_hbstatus` AS `mon_hbstatus`,`m`.`mon_availstatus` AS `mon_availstatus`,`m`.`mon_appstatus` AS `mon_appstatus`,`ap`.`responsibles` AS `responsibles`,`ap`.`mailto` AS `mailto` from (((`svcmon` `m` left join `services` `s` on((`s`.`svc_name` = `m`.`mon_svcname`))) left join `nodes` `n` on((convert(`m`.`mon_nodname` using utf8) = `n`.`nodename`))) left join `b_apps` `ap` on((`ap`.`app` = `s`.`svc_app`))) left join b_action_errors e on e.svcname=s.svc_name and e.nodename=m.mon_nodname;

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
