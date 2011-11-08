######################################################################
#
# JmxComponent modeler plugin
#
######################################################################
from Products.DataCollector.plugins.CollectorPlugin import PythonPlugin
from Products.DataCollector.plugins.CollectorPlugin import CollectorPlugin
from Products.DataCollector.plugins.DataMaps import ObjectMap
from Products.ZenUtils.Utils import zenPath,prepId
from twisted.internet.utils import getProcessOutput
import re,os
from subprocess import *

class JavaAppMap(PythonPlugin):
    """Map JMX Client output table to model."""

    relname = "javaApps"
    modname = "ZenPacks.community.zenJavaApp.JavaApp"
    
    deviceProperties = PythonPlugin.deviceProperties + (
                    'zJmxUsername',
                    'zJmxPassword',
                    'zJavaAppPorts',
                    'manageIp',
                    )
    
    def queryRemote(self,server,port,username,password,mbean=None,attribute=None):
        binPath = zenPath('libexec')
        authstring = '-'
        deststring = server+":"+str(port)
        jarfile = binPath + "/cmdline-jmxclient"
        args = ['/usr/bin/java','-jar',jarfile,authstring,deststring]
        if mbean != None and attribute != None:
            args = ['/usr/bin/java','-jar',jarfile,authstring,deststring,mbean,attribute]
        output = Popen(args,stderr=STDOUT,stdout=PIPE).communicate()[0]
        return output  
    
    def getClientPorts(self,device,log):
        validPorts = []
        for port in device.zJavaAppPorts:
            log.info('Testing port %s for device %s', port, device.id)
            output = self.queryRemote(device.id,
                                      port,
                                      device.zJmxUsername,
                                      device.zJmxPassword)
            valid = False
            for line in output.split('\n'):
                if re.search('Connection refused',line) != None :
                    valid = False
                    break
                if re.search('Invalid credentials',line) != None :
                    valid = True
                    break
                if re.search('Authentication failed',line) != None :
                    valid = True
                    break
            if valid == True:
                validPorts.append(port)
        return validPorts
    
    def collect(self, device, log):
        results = []
        ports = self.getClientPorts(device,log)
        for port in ports:
            info = {}
            name = "java_"+port
            info['id'] = prepId(name)
            info['javaPort'] = port
            info['javaUser'] = device.zJmxUsername
            info['javaPass'] = device.zJmxPassword
            #info['javaAuth'] = True
            results.append(info)
        return results

    def process(self, device, results, log):
        log.info('finding plugin %s for device %s', self.name(), device.id)
        rm = self.relMap()
        for result in results:
            om = self.objectMap(result)
            rm.append(om)
        return rm

