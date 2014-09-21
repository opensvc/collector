from applications.init.modules import amazon

class Clouds(object):
    def __init__(self):
        self.clouds = self.get_clouds()

    def get_clouds(self):
        l = []
        for data in config.clouds:
            drv = data['driver']
            if drv == 'amazon':
                try:
                    l.append(amazon.Cloud(data))
                except Exception as e:
                    print e
        return l

    def import_nodes(self):
        for cloud in self.clouds:
            for o in cloud.get_osvc_nodes():
                print o
                k = dict(nodename = o['nodename'])
                db.nodes.update_or_insert(k, **o)
        db.commit()

    def import_networks(self):
        for cloud in self.clouds:
            for o in cloud.get_osvc_networks():
                print o
                k = dict(network = o['network'])
                db.networks.update_or_insert(k, **o)
        db.commit()

    def import_volumes(self):
        for cloud in self.clouds:
            for o in cloud.get_osvc_volumes():
                print o
                k = dict(disk_id = o['disk_id'])
                db.diskinfo.update_or_insert(k, **o)
        db.commit()

def import_clouds():
    o = Clouds()
    o.import_nodes()
    o.import_networks()
    o.import_volumes()
