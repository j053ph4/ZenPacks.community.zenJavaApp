import Globals
from Products.ZenModel.ZenPack import ZenPack as ZenPackBase
from Products.ZenUtils.Utils import unused
import os

unused(Globals)

from Products.ZenRelations.RelSchema import *
from Products.ZenModel.Device import Device
Device._relations += (('javaApps', ToManyCont(ToOne,'ZenPacks.community.zenJavaApp.JavaApp.JavaApp','javaHost')),)

       
class ZenPack(ZenPackBase):
    # All zProperties defined here will automatically be created when the
    # ZenPack is installed.
    packZProperties = [
        ('zJavaAppPorts', '', 'lines'),
        ]

    def symlinkScript(self):
        os.system('ln -sf %s/cmdline-jmxclient-0.10.3.jar %s/cmdline-jmxclient' %
            (self.path('bin'), zenPath('libexec')))
        os.system('ln -sf %s/jmxQuery.py %s/jmxQuery.py' %
            (self.path('bin'), zenPath('libexec')))
        
    def removeScriptSymlink(self):
        os.system('rm -f %s/cmdline-jmxclient' % (zenPath('libexec')))
        os.system('rm -f %s/jmxQuery.py' % (zenPath('libexec')))
        
    def install(self, dmd):
        ZenPackBase.install(self, dmd)
         # Put your customer installation logic here.
        #self.symlinkScript()
        for d in self.dmd.Devices.getSubDevices():
            d.buildRelations()
        #pass

    def remove(self, dmd, leaveObjects=False):
        #if not leaveObjects:
        #    pass
        #self.removeScriptSymlink()
        ZenPackBase.remove(self, dmd, leaveObjects=leaveObjects)
        Device._relations = tuple([x for x in Device._relations if x[0] not in ('javaApps')])
        for d in self.dmd.Devices.getSubDevices():
            d.buildRelations()
