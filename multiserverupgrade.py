#!/usr/bin/python

import sys, os
from twisted.python.filepath import FilePath
from twisted.python.failure import Failure
from twisted.internet import reactor

from lae_automation.config import Config
from lae_automation.server import set_up_monitors
from lae_automation.signup import wait_for_EC2_addresses


endpoint_uri = 'https://ec2.us-east-1.amazonaws.com/'
configpath='../lae_automation_config.json'
config = Config(configpath)

ec2secretpath='../ec2secret'
ec2accesskeyid = str(config.other['ec2_access_key_id'])
ec2secretkey = FilePath(ec2secretpath).getContent().strip()

monitor_privkey_path = str(config.other['monitor_privkey_path'])


d = wait_for_EC2_addresses(ec2accesskeyid, ec2secretkey, endpoint_uri, sys.stdout, sys.stderr)

def upgrade_servers(host_list):
    for (public_host, private_host) in host_list:
        print "Upgrading %r..." % (public_host,)
        set_up_monitors(public_host, monitor_privkey_path, sys.stdout, sys.stderr)

d.addCallback(upgrade_servers)


def cb(x):
    print str(x)
    if isinstance(x, Failure) and hasattr(x.value, 'response'):
        print x.value.response

d.addBoth(cb)
d.addCallbacks(lambda ign: os._exit(0), lambda ign: os._exit(1))
reactor.run()
