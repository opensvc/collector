-- MySQL dump 10.13  Distrib 5.1.40, for unknown-linux-gnu (x86_64)
--
-- Host: dbopensvc    Database: opensvc
-- ------------------------------------------------------
-- Server version	5.1.40

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `filters`
--

DROP TABLE IF EXISTS `filters`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `filters` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `fil_name` varchar(30) NOT NULL,
  `fil_column` varchar(30) NOT NULL,
  `fil_need_value` tinyint(1) NOT NULL DEFAULT '1',
  `fil_pos` int(11) NOT NULL DEFAULT '1',
  `fil_table` varchar(30) NOT NULL,
  `fil_img` varchar(30) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=111 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `filters`
--

LOCK TABLES `filters` WRITE;
/*!40000 ALTER TABLE `filters` DISABLE KEYS */;
INSERT INTO `filters` VALUES (2,'service name','svc_name',1,1,'v_svcmon','svc.png'),(3,'container name','svc_vmname',1,20,'v_svcmon','svc.png'),(4,'container type','svc_containertype',1,21,'v_svcmon','svc.png'),(5,'os kernel','os_kernel',1,206,'v_svcmon','os16.png'),(6,'os arch','os_arch',1,205,'v_svcmon','os16.png'),(7,'os segment','os_segment',1,204,'v_svcmon','os16.png'),(8,'os update','os_update',1,203,'v_svcmon','os16.png'),(9,'os release','os_release',1,202,'v_svcmon','os16.png'),(10,'os vendor','os_vendor',1,201,'v_svcmon','os16.png'),(11,'os name','os_name',1,200,'v_svcmon','os16.png'),(12,'rack','loc_rack',1,106,'v_svcmon','loc.png'),(13,'room','loc_room',1,105,'v_svcmon','loc.png'),(14,'floor','loc_floor',1,104,'v_svcmon','loc.png'),(15,'building','loc_building',1,103,'v_svcmon','loc.png'),(16,'address','loc_addr',1,102,'v_svcmon','loc.png'),(17,'city','loc_city',1,101,'v_svcmon','loc.png'),(18,'country','loc_country',1,100,'v_svcmon','loc.png'),(19,'status last changed','mon_changed',1,10,'v_svcmon','svc.png'),(20,'status last update','mon_updated',1,10,'v_svcmon','svc.png'),(21,'host id','mon_hostid',1,1,'v_svcmon','node16.png'),(22,'node type','mon_nodtype',1,1,'v_svcmon','node16.png'),(23,'node name','mon_nodname',1,1,'v_svcmon','node16.png'),(24,'responsibles','responsibles',1,1,'v_svcmon','guy16.png'),(26,'service config last update','svc_updated',1,11,'v_svcmon','svc.png'),(27,'application code','svc_app',1,2,'v_svcmon','svc.png'),(28,'service type','svc_type',1,2,'v_svcmon','svc.png'),(29,'service primary node','svc_autostart',1,2,'v_svcmon','svc.png'),(30,'service drp nodes','svc_drpnodes',1,2,'v_svcmon','svc.png'),(31,'service drp node','svc_drpnode',1,2,'v_svcmon','svc.png'),(32,'service nodes','svc_nodes',1,2,'v_svcmon','svc.png'),(33,'opensvc version','svc_version',1,30,'v_svcmon','svc.png'),(34,'service error count','err',1,31,'v_svcmon','svc.png'),(35,'prefered node','ref1',0,1,'v_svcmon','svc.png'),(70,'power breaker #2','power_breaker2',1,506,'nodes','pwr.png'),(36,'acknowledge time','acked_date',1,1,'v_svcactions','action16.png'),(37,'acknowledge comment','acked_comment',1,1,'v_svcactions','action16.png'),(38,'acknowledged by','acked_by',1,1,'v_svcactions','action16.png'),(39,'alert id','alert',1,1,'v_svcactions','action16.png'),(40,'acknowledged','ack',1,1,'v_svcactions','action16.png'),(41,'action pid','pid',1,1,'v_svcactions','action16.png'),(42,'action log','status_log',1,1,'v_svcactions','action16.png'),(43,'host id','hostid',1,1,'v_svcactions','action16.png'),(44,'node name','hostname',1,1,'v_svcactions','node16.png'),(45,'action begin time','begin',1,1,'v_svcactions','action16.png'),(46,'action end time','end',1,1,'v_svcactions','action16.png'),(47,'action duration','time',1,1,'v_svcactions','action16.png'),(48,'action status','status',1,1,'v_svcactions','action16.png'),(49,'action','action',1,1,'v_svcactions','action16.png'),(50,'service name','svcname',1,1,'v_svcactions','svc.png'),(51,'opensvc version','version',1,1,'v_svcactions','svc.png'),(52,'zip','loc_zip',1,101,'v_svcmon','loc.png'),(53,'zip','loc_zip',1,101,'v_svcactions','loc.png'),(54,'os kernel','os_kernel',1,206,'v_svcactions','os16.png'),(55,'os arch','os_arch',1,205,'v_svcactions','os16.png'),(56,'os segment','os_segment',1,204,'v_svcactions','os16.png'),(57,'os update','os_update',1,203,'v_svcactions','os16.png'),(58,'os release','os_release',1,202,'v_svcactions','os16.png'),(59,'os vendor','os_vendor',1,201,'v_svcactions','os16.png'),(60,'os name','os_name',1,200,'v_svcactions','os16.png'),(61,'rack','loc_rack',1,106,'v_svcactions','loc.png'),(62,'room','loc_room',1,105,'v_svcactions','loc.png'),(63,'floor','loc_floor',1,104,'v_svcactions','loc.png'),(64,'building','loc_building',1,103,'v_svcactions','loc.png'),(65,'address','loc_addr',1,102,'v_svcactions','loc.png'),(66,'city','loc_city',1,101,'v_svcactions','loc.png'),(67,'country','loc_country',1,100,'v_svcactions','loc.png'),(68,'responsibles','responsibles',1,1,'v_svcactions','guy16.png'),(69,'application code','app',1,1,'v_svcactions','svc.png'),(71,'power breaker #1','power_breaker1',1,505,'nodes','pwr.png'),(72,'power protect breaker','power_protect_breaker',1,504,'nodes','pwr.png'),(73,'power protect','power_protect',1,503,'nodes','pwr.png'),(74,'power supply count','power_supply_nb',1,502,'nodes','pwr.png'),(75,'power cabinet #2','power_cabinet2',1,501,'nodes','pwr.png'),(76,'power cabinet #1','power_cabinet1',1,500,'nodes','pwr.png'),(77,'environment','environnement',1,1,'nodes','node16.png'),(78,'role','role',1,1,'nodes','node16.png'),(79,'status','status',1,1,'nodes','node16.png'),(80,'warranty end','warranty_end',1,1,'nodes','node16.png'),(81,'server type','type',1,1,'nodes','node16.png'),(82,'server model','model',1,1,'nodes','node16.png'),(83,'server serial number','serial',1,1,'nodes','node16.png'),(84,'team responsible','team_responsible',1,1,'nodes','node16.png'),(85,'os kernel','os_kernel',1,206,'nodes','os16.png'),(86,'os arch','os_arch',1,205,'nodes','os16.png'),(87,'os segment','os_segment',1,204,'nodes','os16.png'),(88,'os update','os_update',1,203,'nodes','os16.png'),(89,'os release','os_release',1,202,'nodes','os16.png'),(90,'os vendor','os_vendor',1,201,'nodes','os16.png'),(91,'os name','os_name',1,200,'nodes','os16.png'),(92,'memory banks','mem_banks',1,400,'nodes','mem16.png'),(93,'memory slots','mem_slots',1,401,'nodes','mem16.png'),(94,'memory size','mem_bytes',1,402,'nodes','mem16.png'),(95,'cpu model','cpu_model',1,304,'nodes','cpu16.png'),(96,'cpu vendor','cpu_vendor',1,303,'nodes','cpu16.png'),(97,'cpu dies','cpu_dies',1,302,'nodes','cpu16.png'),(98,'cpu cores','cpu_cores',1,301,'nodes','cpu16.png'),(99,'cpu frequency','cpu_freq',1,300,'nodes','cpu16.png'),(100,'rack','loc_rack',1,106,'nodes','loc.png'),(101,'room','loc_room',1,105,'nodes','loc.png'),(102,'floor','loc_floor',1,104,'nodes','loc.png'),(103,'building','loc_building',1,103,'nodes','loc.png'),(104,'address','loc_addr',1,102,'nodes','loc.png'),(105,'zip','loc_zip',1,101,'nodes','loc.png'),(106,'country','loc_country',1,100,'nodes','loc.png'),(107,'city','loc_city',1,101,'nodes','loc.png'),(108,'node name','nodename',1,1,'nodes','node16.png'),(109,'nodes with service','ref2',0,1,'nodes','svc.png'),(110,'not acknowledged','ref3',0,1,'v_svcactions','action16.png');
/*!40000 ALTER TABLE `filters` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_filters`
--

DROP TABLE IF EXISTS `auth_filters`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_filters` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `fil_uid` int(11) NOT NULL,
  `fil_id` int(11) DEFAULT NULL,
  `fil_value` varchar(200) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `index1` (`fil_uid`,`fil_id`)
) ENGINE=MyISAM AUTO_INCREMENT=43 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_filters`
--

LOCK TABLES `auth_filters` WRITE;
/*!40000 ALTER TABLE `auth_filters` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_filters` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2010-03-24 16:00:12
