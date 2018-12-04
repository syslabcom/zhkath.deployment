from batou import UpdateNeeded
from batou.component import Component, Attribute
from batou.lib.cmmi import Build
from batou.lib.file import File
from batou.lib.supervisor import Program
from batou.utils import Address


class Varnish(Component):

    address = Attribute(Address, '127.0.0.1:9090')
    control_port = Attribute(int, '6083')

    def configure(self):
        self.provide('varnish:http', self)
        self.purgehosts = self.require('zope:http')
        self.haproxy = self.require_one('haproxy:frontend')

        self += Build(
            'http://varnish-cache.org/_downloads/varnish-3.0.2.tgz',
            checksum='sha1:906f1536cb7e728d18d9425677907ae723943df7')

        self += File('etc/varnish/zhkath.vcl', source='zhkath.vcl')
        self += Program(
            'varnish',
            priority=20,
            command='sbin/varnishd',
            args=self.expand(
                '-F -f etc/varnish/zhkath.vcl '
                '-T localhost:{{component.control_port}} '
                '-a {{component.address.listen}} -p thread_pool_min=10 '
                '-p thread_pool_max=50 -s malloc,250M'))

        self += PurgeCache()


class PurgeCache(Component):

    varnishadm = 'bin/varnishadm'

    def verify(self):
        raise UpdateNeeded()

    def update(self):
        self.cmd(self.expand(
            '{{component.varnishadm}}'
            ' -T "localhost:{{component.parent.control_port}}"'
            ' "ban.url .*"'))
