from Products.DataCollector.plugins.CollectorPlugin import CollectorPlugin, PythonPlugin
from Products.DataCollector.plugins.DataMaps import ObjectMap, MultiArgs
from Products.ZenUtils.Utils import prepId
from ZenPacks.community.zenJavaApp.Definition import *
from ZenPacks.community.zenJavaApp.lib.JavaAppScan import *

__doc__ = """JavaAppMap

JavaAppMap detects JVMs on a per-port basis, collecting info such as Java Version and JMX protocol.
This version adds a relation to associated ipservices and osprocess components.

"""

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
                    )
    
    def collect(self, device, log):
        ''''''
        output = []
        log.info("collecting %s for %s." % (self.name(), device.id))
        self.scan = JavaAppScan(device.manageIp, device.zJavaAppPortRange, device.zJmxUsername, device.zJmxPassword,
                                device.zJolokiaProxyHost, device.zJolokiaProxyPort, device.zJavaAppScanTimeout)
        self.scan.evalPorts()
        for jmx in self.scan.portdict.values():
            name = "%s_%s" % (self.baseid, str(jmx.port))
            info = {'id': prepId(name),
                    'port': jmx.port,
                    'auth': jmx.auth,
                    'isWorking' : jmx.connected,
                    'protocol': jmx.protocol,
                    'parameters': None,
                    'user': None,
                    'password': None,
                    'javaversion': jmx.javaversion,
                    'vendorname': jmx.vendorname,
                    'vendorproduct': jmx.vendorproduct,
                    }
            if jmx.connected is True and jmx.auth is True:
                    info['user'] = jmx.user
                    info['password'] = jmx.password
            output.append(info)
        return output
    
    def process(self, device, results, log):
        ''''''
        log.info("The plugin %s returned %s results." % (self.name(), len(results)))
        rm = self.relMap()
        for result in results:
            om = self.objectMap(result)
            om.setFixedPasswords = ''
            om.setIpservice = om.port
            om.setOsprocess = 'blah'
            om.monitor = result['isWorking']
            prodKey = '%s' % result.get('vendorproduct')
            om.setProductKey = MultiArgs(prodKey, result.get('vendorname'))
            log.debug(om)
            rm.append(om)
        return rm

