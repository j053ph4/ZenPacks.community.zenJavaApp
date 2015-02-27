from Products.DataCollector.plugins.CollectorPlugin import CollectorPlugin
from Products.DataCollector.plugins.DataMaps import ObjectMap
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
    
    def getAttribute(self, mbean, attribute, port, protocol, log):
        '''return single-valued mbean attribute'''
        try: return self.scan.getBeanAttributeValues(port=port, 
                                                     mbean=mbean, 
                                                     attributes=[attribute], 
                                                     protocol=protocol)[attribute]
        except: return None
    
    def getMBeans(self, port, mbean, log):
        ''''''
        #log.debug("getting %s MBeans for %s" % (mbean, port))
        output = []
        result = self.scan.proxy.get(self.scan.ipaddr, port, self.scan.username, self.scan.password, mbean)
        for r in result:
            data = {'fullpath' : str(r['fullname']), 'mbean': '', 'enabled': True}
            if 'name' in r.keys():  data ['mbean'] = str(r['name'])
            else: data ['mbean'] = str(r['fullname'])
            for k,v in r.items():
                k = str(k)
                if k in ['fullname', 'name']: continue
                data[k] = str(v)
            output.append(data)
        return output
    
    def getClientInfo(self, mbean, port, log):
        ''' create objectMap data for a given port'''
        #log.debug('getClientInfo for %s' % port)
        output = []
        beans = self.getMBeans(port, mbean, log)
        counter = 0
        for info in beans:
            name = "%s_%s" % (info['mbean'], port)
            name = re.sub('[^A-Za-z0-9]+', '_', name)
            if len(name) >=127:
                name = name[:126]+'_%s' % counter
                counter +=1
            info['id'] = prepId(name)
            info['user'] = self.scan.username
            info['password'] = self.scan.password
            info['protocol'] = self.scan.portdict[port]['protocol']
            info['auth'] = self.scan.portdict[port]['useAuth']
            info['port'] = port
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
        for port, status in self.scan.portdict.items():
            if type(self.searchMBean) == list:
                for bean in self.searchMBean:
                    testMBean = '%s:*' % bean.split(':')[0]
                    if status['isGood'] is True and self.scan.beanExists(port, testMBean) is True:
                        output += self.getClientInfo(bean, port, log)
            else:
                testMBean = '%s:*' % self.searchMBean.split(':')[0]
                if status['isGood'] is True and self.scan.beanExists(port, testMBean) is True:
                    output += self.getClientInfo(self.searchMBean, port, log)
        return output
    
    def process(self, device, results, log):
        #log.info("got %s results" % len(results))
        log.info("The plugin %s returned %s results." % (self.name(), len(results)))
        #self.scan =  None
        if len(results) == 0: return None
        rm = self.relMap()
        for result in results:
            enabled = result['enabled']
            result.pop('enabled')
            om = self.objectMap(result)
            om.setJavaapp = ''
            om.setIpservice = ''
            om.monitor = enabled 
            rm.append(om)
            log.debug(om)
        return rm

