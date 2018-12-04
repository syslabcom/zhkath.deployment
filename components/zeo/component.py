from batou.component import Component, Attribute
from batou.lib.buildout import Buildout
from batou.lib.file import Directory
from batou.lib.supervisor import Program
from batou.utils import Address


class ZEO(Component):

    address = Attribute(Address, '127.0.0.1:9100')
    profile = 'base'
    eggs_directory = '{{component.environment.workdir_base}}/eggs'

    def configure(self):
        self.common = self.require_one('common', host=self.host)
        self.provide('zhkath:zeo:server', self.address)
        self += Directory('download-cache')
        self += Buildout(
            python='2.7',
            setuptools='40.0.0',
            version='2.12.1',
        )

        self += Program(
            'zeo',
            options={'startsecs': 30},
            command=self.map('bin/zeo start'),
            args=self.expand('-C {{component.workdir}}/parts/zeo/zeo.conf')
        )
