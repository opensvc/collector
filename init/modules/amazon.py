#!/opt/opensvc/bin/python

import sys
import os
import datetime

from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver

sys.path.append(os.path.dirname(__file__))

def get_cloud(provider, access_key_id):
    import config as config
    for cloud in config.clouds:
        if cloud['driver'] != 'amazon':
            continue
        if cloud['provider'] == provider and cloud['access_key_id'] == access_key_id:
            return Cloud(cloud)

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

    def list_sizes(self):
        l = self.driver.list_sizes()
        return l

    def list_sizes_value_label(self):
        l = []
        for s in self.driver.list_sizes():
            label = "%s, %s, ram:%d disk:%s price:%s" % (s.id, s.name, s.ram, str(s.disk), str(s.price))
            l.append((s.id, label))
        return l

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
              "disk_arrayid": volume.extra['zone'],
              "disk_created": volume.extra['create_time'],
              "disk_updated": datetime.datetime.now(),
            }
            l.append(osvc_disk)
        return l

    def list_secgroups(self):
        l = self.driver.ex_get_security_groups()
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
              "comment": subnet.extra["vpc_id"],
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

    def create_node(self, *args, **kwargs):
        data = {}
        for i in ["name", "keyname", "image", "size", "subnet"]:
            if i not in kwargs:
                raise Exception("missing '%s' parameter"%i)

        # name
        data["name"] = kwargs["name"]

        # keyname
        keyname = kwargs['keyname']
        keynames = [s for s in self.driver.list_key_pairs() if s.name==keyname]
        if len(keynames) != 1:
            raise Exception("keyname '%s' object not found" % keyname)
        data["ex_keyname"] = keyname
        print "validated keyname:", keyname

        # image
        image = kwargs['image']
        images = self.driver.list_images(ex_image_ids=[image])
        if len(images) != 1:
            raise Exception("image '%s' object not found" % image)
        data["image"] = images[0]
        print "validated image:", images[0].id

        # size
        size = kwargs['size']
        sizes = [s for s in self.driver.list_sizes() if s.id==size]
        if len(sizes) != 1:
            raise Exception("size '%s' object not found" % size)
        data["size"] = sizes[0]
        print "validated size:", sizes[0].id

        # subnet
        subnet = kwargs['subnet']
        subnets = [s for s in self.driver.ex_list_subnets() if s.name==subnet]
        if len(subnets) != 1:
            raise Exception("subnet '%s' object not found" % subnet)
        data["ex_subnet"] = subnets[0]
        print "validated subnet:", subnets[0].id

        print self.driver.create_node(**data)

if __name__ == "__main__":
    import config as config
    o = Cloud(config.clouds[0])
    for s in o.list_sizes_value_label():
        print s
#    for node in o.list_nodes():
#        print node
#        print node.extra


