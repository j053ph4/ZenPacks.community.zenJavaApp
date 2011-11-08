import Globals
from Products.ZenModel.ZenPack import ZenPack as ZenPackBase
from Products.ZenUtils.Utils import zenPath,unused
import os

unused(Globals)

from Products.ZenRelations.RelSchema import *
from Products.ZenModel.Device import Device
Device._relations += (('javaApps', ToManyCont(ToOne,'ZenPacks.community.zenJavaApp.JavaApp.JavaApp','javaHost')),)
 
class ZenPack(ZenPackBase):
    """
    """
    packZProperties = [
        ('zJavaAppPorts', '', 'lines'),
        ]

    def symlinkScript(self):
        os.system('ln -sf %s/cmdline-jmxclient-0.10.3.jar %s/cmdline-jmxclient' %
            (self.path('bin'), zenPath('libexec')))

    def removeScriptSymlink(self):
        os.system('rm -f %s/cmdline-jmxclient' % (zenPath('libexec')))

    def install(self, dmd):
        ZenPackBase.install(self, dmd)
        self.symlinkScript()
        for d in self.dmd.Devices.getSubDevices():
            d.buildRelations()

    def remove(self, dmd, leaveObjects=False):
        self.removeScriptSymlink()
        ZenPackBase.remove(self, dmd, leaveObjects=leaveObjects)
        Device._relations = tuple([x for x in Device._relations if x[0] not in ('javaApps')])
        for d in self.dmd.Devices.getSubDevices():
            d.buildRelations()
