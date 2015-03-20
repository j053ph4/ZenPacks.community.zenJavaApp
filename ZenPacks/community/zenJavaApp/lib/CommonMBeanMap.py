from Products.DataCollector.plugins.CollectorPlugin import CollectorPlugin
from Products.DataCollector.plugins.DataMaps import ObjectMap, MultiArgs
from Products.ZenUtils.Utils import prepId
from ZenPacks.community.zenJavaApp.lib.JavaAppScan import *
from ZenPacks.community.zenJavaApp.Definition import *
import re

class CommonMBeanMap(CollectorPlugin):
    """Map JMX Client output table to model."""
    compname = "os"
    baseid = ''
    transport = "python"
    
    deviceProperties = CollectorPlugin.deviceProperties + tuple([p[0] for p in JavaAppDefinition.packZProperties]) + (
                    'zJmxUsername',
                    'zJmxPassword',
                    'manageIp',
                    )
    
    testMBean = ''
    searchMBean = ''
    
    def getClientInfo(self, jmx, mbean, log):
        ''' create objectMap data for a given port'''
        output = []
        beans = self.scan.proxy.search(mbean)
        counter = 0
        for info in beans:
            name = "%s_%s" % (info['mbean'], jmx.port)
            name = re.sub('[^A-Za-z0-9]+', '_', name)
            if len(name) >=127:
                name = name[:126]+'_%s' % counter
                counter +=1
            info.update({'id': prepId(name),
                    'user': jmx.user,
                    'password': jmx.password,
                    'protocol': jmx.protocol,
                    'auth': jmx.auth,
                    'port': jmx.port,
                    'enabled': jmx.connected,
                    'javaversion': jmx.javaversion,
                    'vendorname': jmx.vendorname,
                    'vendorproduct': jmx.vendorproduct,
                    })
            output.append(info)
        return output
    
    def collect(self, device, log):
        ''''''
        log.info("collecting %s for %s." % (self.name(), device.id))
        self.scan = JavaAppScan(device.manageIp, device.zJavaAppPortRange, 
                                device.zJmxUsername, device.zJmxPassword,
                                device.zJolokiaProxyHost, device.zJolokiaProxyPort,
                                device.zJavaAppScanTimeout)
        self.scan.evalPorts()
        output = []
        for jmx in self.scan.portdict.values():
            # use these connection parameters
            self.scan.proxy.setJMX(jmx)
            # process differently if search bean is a list of beans to search
            if type(self.searchMBean) == list:
                for bean in self.searchMBean:
                    search = '%s:*' % bean.split(':')[0]
                    if jmx.connected is True and self.scan.proxy.beanExists(search) is True:
                        output += self.getClientInfo(jmx, bean, log)
            else:
                search = '%s:*' % self.searchMBean.split(':')[0]
                if jmx.connected is True and self.scan.proxy.beanExists(search) is True:
                    output += self.getClientInfo(jmx, self.searchMBean, log)
        return output
    
    
    def preprocess(self, result, log):
        '''optional method before creating object map'''
        return result
        
    def postprocess(self, result, om, log):
        '''optional method before appending to relmap'''
        return om
    
    def process(self, device, results, log):
        ''''''
        log.info("The plugin %s returned %s results." % (self.name(), len(results)))
        # trying to be sneaky here
        self.device = device
        klass = self.modname.split('.')[-1]
        if len(results) == 0: return None
        rm = self.relMap()
        for result in results:
            result = self.preprocess(result, log)
            enabled = result['enabled']
            result.pop('enabled')
            om = self.objectMap(result)
            om.setJavaapp = ''
            om.setIpservice = ''
            #prodKey = '%s %s' % (result.get('vendorproduct'), klass)
            prodKey = result.get('vendorproduct')
            om.setProductKey = MultiArgs(prodKey, result.get('vendorname'))
            om.monitor = enabled 
            om = self.postprocess(result, om, log)
            rm.append(om)
            log.debug(om)
        return rm

