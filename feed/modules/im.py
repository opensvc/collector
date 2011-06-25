import xmpp
import sys

class NullDevice():
    def write(self, s):
        pass

class gtalk(object):
    def __init__(self):
        import config
        if "gtalk" not in dir(config) or not gtalk:
            self.send = self.dummy_send
            return
        sys.stdout = NullDevice()
        self.c = xmpp.Client("gmail.com")
        self.c.connect(("talk.google.com", 5223))
        self.c.auth(config.gtalk_username, config.gtalk_password)

    def dummy_send(self, to, msg):
        return

    def send(self, to, msg):
        self.c.send(xmpp.Message(to, msg))
