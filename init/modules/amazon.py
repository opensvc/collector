#!/opt/opensvc/bin/python

import sys
import os
import datetime

from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver

sys.path.append(os.path.dirname(__file__))

class Cloud(object):
    def __init__(self, data):
        self.data = data
        self.driver = None
        self.control_data()
        self.get_driver()

    def control_data(self):
        if type(self.data) != dict:
            raise Exception("This class init needs a dict type parameter")
        if "access_key_id" not in self.data:
            raise Exception("This class init needs a 'access_key_id' key in the dict parameter")
        if "secret_key" not in self.data:
            raise Exception("This class init needs a 'secret_key' key in the dict parameter")

    def get_driver(self):
        if self.driver:
            return self.driver
        driver = get_driver(self.data['provider'])
        self.driver = driver(self.data['access_key_id'], self.data['secret_key'])
        if 'proxy' in self.data:
            self.driver.connection.set_http_proxy(proxy_url=self.data['proxy'])
        return self.driver

    def list_volumes(self):
        l = self.driver.list_volumes()
        return l

    def get_osvc_volumes(self):
        volumes = self.list_volumes()
        l = []
        for volume in volumes:
            if volume.extra['iops']:
                raid = "%d iops" % volume.extra['iops']
            else:
                raid = ""
            osvc_disk = {
              "disk_id": volume.id,
              "disk_devid": volume.id,
              "disk_size": volume.size*1024,
              "disk_raid": raid,
              "disk_group": volume.extra['zone'],
              "disk_created": volume.extra['create_time'],
              "disk_updated": datetime.datetime.now(),
            }
            l.append(osvc_disk)
        return l

    def list_subnets(self):
        l = self.driver.ex_list_subnets()
        return l

    def get_osvc_subnets(self):
        subnets = self.list_subnets()
        l = []
        for subnet in subnets:
            v = subnet.extra['cidr_block']
            base, mask = v.split("/")
            osvc_subnet = {
              "name": subnet.name,
              "network": base,
              "netmask": mask,
              "updated": datetime.datetime.now(),
            }
            l.append(osvc_subnet)
        return l

    def list_networks(self):
        l = self.driver.ex_list_networks()
        return l

    def get_osvc_networks(self):
        networks = self.list_networks()
        l = []
        for network in networks:
            v = network.cidr_block
            base, mask = v.split("/")
            osvc_network = {
              "name": network.name,
              "network": base,
              "netmask": mask,
              "updated": datetime.datetime.now(),
            }
            l.append(osvc_network)
        return l

    def list_nodes(self):
        nodes = self.driver.list_nodes()
        return nodes

    def get_osvc_nodes(self):
        nodes = self.list_nodes()
        l = []
        for node in nodes:
            osvc_node = {
              "nodename": node.extra["private_dns"].split(".")[0],
              "fqdn": node.extra["private_dns"],
              "assetname": "-".join(("amazon", self.data['provider'], node.uuid)),
              "loc_city": self.data['provider'],
              "type": node.extra["instance_type"],
              "role": node.name,
              "status": node.state,
              "updated": datetime.datetime.now(),
            }
            l.append(osvc_node)
        return l

if __name__ == "__main__":
    import config as config
    o = Cloud(config.clouds[0])
    for n in  o.list_subnets():
        print n
        print n.extra
    #for n in  o.driver.list_volumes():
    #    print n
    #    print n.extra
    #for node in o.list_nodes():
        #print node
        #print node.extra


