from Products.DataCollector.plugins.CollectorPlugin import CollectorPlugin
from Products.DataCollector.plugins.DataMaps import ObjectMap
from Products.ZenUtils.Utils import prepId
from ZenPacks.community.zenJavaApp.Definition import *
from ZenPacks.community.zenJavaApp.JavaAppScan import *
from Products.ZenModel.OSProcess import getProcessIdentifier

import re

class JavaAppMap(CollectorPlugin):
    """Map JMX Client output table to model."""
    
    constr = Construct(JavaAppDefinition)
    
    compname = "os"
    relname = constr.relname
    modname = constr.zenpackComponentModule
    baseid = constr.baseid
    transport = "python"

    deviceProperties = CollectorPlugin.deviceProperties + tuple([p[0] for p in JavaAppDefinition.packZProperties]) + (
                    'zJmxUsername',
                    'zJmxPassword',
                    'manageIp',
                    )
    
    def getProcessId(self, port, auth, log):
        """ 
            look for terracotta-related mbeans
        """
        log.debug("getProcessId for %s" % port)
        mbean = 'java.lang:type=Runtime'
        attribute = 'InputArguments'
        try:
            lines = self.scan.jmxQuery(port, auth, mbean, attribute)
            lines.remove(lines[0])
            args = " ".join(lines)[0:128]
            log.debug("found args: %s" % args)
            return args 
        except:
            pass
        return None
    
    def getGenType(self, port, auth, info, log):
        """ find number of currently connected clients
        """
        baseString = 'java.lang:type=MemoryPool,name='
        try:
            lines = self.scan.jmxQuery(port, auth)
            for line in lines:
                keyvals = line.split(',')
                if 'MemoryPool' in line:
                    name = keyvals[0].split('=')[1]
                    if 'Old Gen' in name:
                        info['oGen'] = baseString+name
                    if 'Perm Gen' in name:
                        info['pGen'] = baseString+name
                    if len(info['pGen']) > 0 and len(info['oGen']) > 0:
                        info['validGen'] = True
        except:
            pass
        return info

    def collect(self, device, log):
        self.scan = JavaAppScan(device.id, 
                                device.manageIp, 
                                device.zJavaAppPortRange, 
                                device.zJmxUsername, 
                                device.zJmxPassword)
        self.scan.evalPorts()
        #self.evalPorts(device,log)
        output = []
        for port in self.scan.portdict.keys():
            entry = self.scan.portdict[port]
            log.debug("got entry: %s" % entry)
            if entry['isJmx'] == True:
                auth = "%s:%s" %(device.zJmxUsername, device.zJmxPassword)
                log.debug('Testing for Oldgem/Permgem type at %s:%s' % (device.id, port))
                name = "%s_%s" % (self.baseid,str(port))
                info = {
                        'id': prepId(name),
                        'port': port,
                        'auth': entry['useAuth'],
                        'parameters': None,
                        'isWorking' : False,
                        'user': '',
                        'password': '',
                        'oGen': '',
                        'pGen': '',
                        'validGen': False
                        }
                if entry['useAuth'] == False: # authentication isn't needed
                    info['isWorking'] = True
                else:
                    if entry['validAuth'] == True: # we can use the zJmxPassword
                        info['user'] = device.zJmxUsername
                        info['password'] = device.zJmxPassword
                        info['isWorking'] = True
                    else:
                        info['isWorking'] = False # we don't know the username/password
                if info['isWorking'] == True:
                    info = self.getGenType(port,auth,info,log) # since it's working, lets find the Gen type
                    info['parameters'] = self.getProcessId(port, auth, log)
                output.append(info)
        return output
    
    def process(self, device, results, log):
        log.info("results: %s" % results)
        rm = self.relMap()
        for result in results:
            om = self.objectMap(result)
            om.setIpservice = om.port
            om.setOsprocess = om.parameters
            om.monitor = result['isWorking']
            rm.append(om)
            log.debug(om)
        return rm

