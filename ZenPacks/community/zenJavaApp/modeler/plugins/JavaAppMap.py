######################################################################
#
# JavaAppMap modeler plugin
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

    def queryRemote(self,server,port,log):
        binPath = zenPath('libexec')
        authstring = '-'
        deststring = server+":"+str(port)
        jarfile = binPath + "/cmdline-jmxclient"
        args = '/usr/bin/java -jar '+jarfile+' '+authstring+' '+deststring
        try:
          output = Popen([args],stdout=PIPE,stderr=STDOUT,shell=True)
          return output.communicate()
        except Exception as e:
          return False

    def getClientPorts(self,device,log):
        validPorts = []
        for jmxPort in device.zJavaAppPorts:
            log.info('Testing port %s for device %s', jmxPort, device.id)
            output = self.queryRemote(device.id, jmxPort, log)
            valid = False
            needAuth = True
            if output != False :
              for line in output:
                if re.search('Connection refused',line) != None :
                    valid = False
                    break
                log.debug(line)
                if re.search('java\.lang:type=Memory',line) != None :
                    valid = True
                    break
                if re.search('Invalid credentials',line) != None :
                    valid = True
                    break
                if re.search('Authentication failed',line) != None :
                    valid = True
                    break
                if re.search('java\.lang:type=Memory',line) != None :
                    valid = True
                    needAuth = False
                    break
            if valid == True:
                log.info('JMX client found on port %s',jmxPort)
                validPorts.append((jmxPort,needAuth))
        return validPorts

    def collect(self, device, log):
        results = []
        jmxPorts = self.getClientPorts(device,log)
        for jmxPort,needAuth in jmxPorts:
            log.info('creating component for port %s',jmxPort)
            info = {}
            name = "java_"+jmxPort
            info['id'] = prepId(name)
            info['javaPort'] = jmxPort
            info['javaUser'] = device.zJmxUsername
            info['javaPass'] = device.zJmxPassword
            info['javaAuth'] = needAuth
            results.append(info)
        return results

    def process(self, device, results, log):
        log.info('finding plugin %s for device %s', self.name(), device.id)
        rm = self.relMap()
        for result in results:
            om = self.objectMap(result)
            rm.append(om)
        return rm

