from batou.component import Component, Attribute
from batou.lib.file import File
from batou.lib.file import Directory
from batou.utils import Address

import batou.c
import os.path


class Frontend(Component):

    server_name = Attribute(str, 'localhost')
    ssl_crt = ''
    ssl_key = ''

    def configure(self):
        self.provide(self.root.name, self)


class PortalFrontend(Frontend):

    wiki_page = ''


class PortalNginx(Component):
    """nginx front-end configuration for portal.
    """

    confdir = '/etc/local/nginx'

    ssl_crt_path = ''
    ssl_key_path = ''

    reload = Attribute('literal', True)
    default_server = Attribute('literal', False)
    external_scheme = 'https'
    instance_name = 'Plone'
    address = ''
    listen_port = '80'
    ssl_listen_port = '443'
    conf_file_name = 'zhkath.conf'

    def configure(self):
        self.settings = self.require_one('portalfrontend')
        self.zopes = self.require('zope:http')
        self.zope_common = self.require_one('zope:common')
        self.instance_name = self.zope_common.instance_name
        self.server_name = self.settings.server_name
        self.address = Address(self.host.fqdn, self.listen_port)
        self.ssl_address = Address(self.host.fqdn, self.ssl_listen_port)
        self.varnish = self.require_one('varnish:http')

        # XXX This causes flapping because it's managed for every frontend.
        # Not a tragic problem, but annoying.
        # Redirect mappings
        self += File(
            os.path.join(self.confdir, 'common.inc'),
            source='config/common.inc',
            mode=0o644,
        )

        self.ssl_crt = self.settings.ssl_crt
        self.ssl_key = self.settings.ssl_key

        self.ssl_crt_path = os.path.join(
            self.confdir, '%s.crt' % (self.server_name))
        self.ssl_key_path = os.path.join(
            self.confdir, '%s.key' % (self.server_name))
        self += File(self.ssl_crt_path, content=self.ssl_crt, mode=0o640)
        self += File(self.ssl_key_path, content=self.ssl_key, mode=0o600)

        self += File(
            os.path.join(self.confdir, self.conf_file_name),
            source='config/zhkath.conf',
            mode=0o644,
        )

        self += File('robots.txt')


@batou.component.platform('ubuntu', PortalNginx)
class ReloadNginx(Component):

    def verify(self):
        if self.parent.reload:
            self.parent.assert_no_changes()

    def update(self):
        self.cmd('sudo -n /etc/init.d/nginx reload')
