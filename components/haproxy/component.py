from batou.component import Component, Attribute, platform
from batou.lib.file import File
from batou.utils import Address


class HAProxy(Component):

    address = Attribute(Address, '{{host.fqdn}}:8002')

    def configure(self):
        self.provide('haproxy:frontend', self)

        self.bindspec = str(self.address.listen)
        if '127.0.0.1:8002' not in self.bindspec:
            # need to cater for the standard nagios check as well
            self.bindspec += ',127.0.0.1:8002'

        self.servers = self.require('zope:http')
        self.servers.sort(key=lambda s: s.host.name)

        self += File(
            self.expand('{{component.workdir}}/haproxy.cfg'),
            source='haproxy.cfg'
        )


@platform('ubuntu', HAProxy)
class HAProxyReload(Component):

    def verify(self):
        self.parent.assert_no_subcomponent_changes()

    def update(self):
        self.cmd('sudo -n /etc/init.d/haproxy reload')
