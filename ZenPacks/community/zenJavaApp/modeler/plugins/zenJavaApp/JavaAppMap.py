from Products.DataCollector.plugins.CollectorPlugin import CollectorPlugin, PythonPlugin
from Products.DataCollector.plugins.DataMaps import ObjectMap
from Products.ZenUtils.Utils import prepId
from ZenPacks.community.zenJavaApp.Definition import *
from ZenPacks.community.zenJavaApp.lib.JavaAppScan import *
from Products.ZenModel.OSProcessMatcher import buildObjectMapData

__doc__ = """JavaAppMap

JavaAppMap detects JVMs on a per-port basis, collecting info such as Java Version and JMX protocol.
This version adds a relation to associated ipservices and osprocess components.

"""

VENDORSEARCH = {
    'Oracle': {
        'search':'amx:*',
        'jvmvendor': [ 
            {'bean':'amx:pp=/J2EEDomain,type=J2EEServer,name=server,j2eeType=J2EEServer', 'attributes': ['serverVersion']},
            {'bean':'amx:j2eeType=J2EEServer,name=server', 'attributes': ['serverVersion']},
            ]
        },
    'Red Hat': {
        'search':'jboss.ws:*',
        'jvmvendor': [ 
            {'bean':'jboss.as:management-root=server', 'attributes': ['productName', 'productVersion']},
            {'bean':'jboss.system:type=Server', 'attributes': ['VersionName', 'VersionNumber']},
            ]
        },
    'Apache': {
        'search':'Catalina:*',
        'jvmvendor': [{'bean':'Catalina:type=Server', 'attributes': ['serverInfo']},]
        },
    'Terracotta': {
        'search':'org.terracotta.internal:*',
        'jvmvendor': [{'bean':'org.terracotta.internal:type=Terracotta Server,name=Terracotta Server', 'attributes': ['Version']},]
        },   
}

JAVAVERSION = {'bean':'java.lang:type=Runtime', 'attributes': ['VmName', 'VmVendor', 'VmVersion']}
JAVAPROC = {'bean':'java.lang:type=Runtime', 'attributes': ['InputArguments']}
JAVAPID = {'bean':'java.lang:type=Runtime', 'attributes': ['Name']}



class JavaAppMap(PythonPlugin):
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
                    'osProcessClassMatchData',
                    )
    
    def getJVMVendorName(self, port, protocol, log):
        ''''''
        for vendor in VENDORSEARCH.keys():
            if self.scan.beanExists(port, VENDORSEARCH[vendor]['search'], protocol) is True: return vendor
        return 'UNKNOWN'
    
    def getJVMVendorVersion(self, port, protocol, vendor, log):
        '''determine what version of Java is running'''
        if vendor in VENDORSEARCH.keys():
            for data in VENDORSEARCH[vendor]['jvmvendor']:
                result = self.scan.getBeanAttributeValues(port, data['bean'],data['attributes'], protocol)
                log.debug("result: %s" % result)
                if len(result.values()) > 0:  return ' '.join(result.values())
        return 'UNKNOWN'
    
    def getJavaVersion(self, port, protocol, log):
        '''determine what version of Java is running'''
        result = self.scan.getBeanAttributeValues(port, JAVAVERSION['bean'], JAVAVERSION['attributes'], protocol)
        if len(result.values()) > 0:  return ' '.join(result.values())
        else: return 'UNKNOWN'
    
    def collect(self, device, log):
        ''''''
        log.info("collecting %s for %s." % (self.name(), device.id))
        matchData = device.osProcessClassMatchData
        self.scan = JavaAppScan(device.manageIp, device.zJavaAppPortRange, device.zJmxUsername, device.zJmxPassword,
                                device.zJolokiaProxyHost, device.zJolokiaProxyPort, device.zJavaAppScanTimeout)
        self.scan.evalPorts()
        output = []
        for port, status in self.scan.portdict.items():
            if status['isJmx'] is True:
                #log.debug("processing JMX port %s" % port)
                name = "%s_%s" % (self.baseid, str(port))
                info = {'id': prepId(name),
                        'port': port,
                        'auth': status['useAuth'],
                        'isWorking' : status['isGood'],
                        'protocol': status['protocol'],
                        'parameters': None,
                        'user': None,
                        'password': None,
                        }
                if status['isGood'] is True:
                    if status['useAuth'] is True:
                        info['user'] = device.zJmxUsername
                        info['password'] = device.zJmxPassword
                    info['javaversion'] = self.getJavaVersion(port, status['protocol'], log)
                    info['vendorname'] = self.getJVMVendorName(port, status['protocol'], log)
                    info['vendorproduct'] = self.getJVMVendorVersion(port, status['protocol'], info['vendorname'], log)
                output.append(info)
        return output
    
    def process(self, device, results, log):
        ''''''
        #print "PROCESS"
        log.info("The plugin %s returned %s results." % (self.name(), len(results)))
        #self.scan =  None
        rm = self.relMap()
        if not results or results is None or len(results) == 0:
            #print "RETURNING NONE"
            #log.info("RETURNING NONE")
            return None #return rm.append(self.objectMap({}))
        for result in results:
            om = self.objectMap(result)
            om.setFixedPasswords = ''
            om.setIpservice = om.port
            om.setOsprocess = 'blah'
            om.monitor = result['isWorking']
            rm.append(om)
            log.debug(om.id)
        return rm

