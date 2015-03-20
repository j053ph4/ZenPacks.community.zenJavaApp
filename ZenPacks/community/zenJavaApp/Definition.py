from ZenPacks.community.ConstructionKit.BasicDefinition import *
from ZenPacks.community.ConstructionKit.Construct import *

ROOT = "ZenPacks.community"
BASE = "zenJavaApp"
VERSION = Version(3, 0, 0)

'''
generic dictionary usable by any JMX MBEAN
'''

def getMBeanDef(version, root, base, component, singular, plural): 
    '''basic class definition for Tomcat MBeans'''
    data = getBasicDefinitionData(version, root, base, component, singular, plural)
    data['componentData']['singular'] = singular
    data['componentData']['plural'] = plural
    data['componentData']['displayed'] = 'id'
    data['componentData']['primaryKey'] = 'id'
    data['componentData']['properties'] = { 
                                  'port' : addProperty('Port'),
                                  'auth': addProperty('Authenticate', default=False, ptype='boolean'),
                                  'user' : addProperty('User'),
                                  'password' : addProperty('Password', ptype='password'),
                                  'mbean': addProperty('MBean',optional=False),
                                  'fullpath': addProperty('Path'),
                                  'protocol': addProperty('Protocol'),
                                  'eventClass' : getEventClass('/Perf/Java'),
                                  'productKey' : getProductClass('Java'),
                                  }
    return data

def addMBeanRelations(definition):
    '''basic relations to JavaApp and IpService'''
    relname = '%ss' %  definition.component.lower()
    module = '%s.%s.%s' % (definition.zenpackroot, definition.zenpackbase, definition.component)
    
    addDefinitionSelfComponentRelation(definition, relname, ToMany, module, 'port', 
                            'javaapp', ToOne, 'ZenPacks.community.zenJavaApp.JavaApp', 'port', 
                            'Java App', 'id')
    addDefinitionSelfComponentRelation(definition, relname, ToMany, module, 'port', 
                              'ipservice',  ToOne, 'Products.ZenModel.IpService', 'port',
                              'IP Service', 'port')

'''
We need to patch this method from the ZenJMX ZenPack 
so that individual datasources can be disabled dynamically
'''
from ZenPacks.zenoss.ZenJMX.services.ZenJMXConfigService import *

def _createDeviceProxy(self, device):
    #log.debug("patched _createDeviceProxy")
    deviceConfig = JMXDeviceConfig(device)
    deviceConfig.thresholds += device.getThresholdInstances(
        JMXDataSource.sourcetype)

    for template in device.getRRDTemplates():
        for ds in self._getDataSourcesFromTemplate(template):
            ds_conf = self._get_ds_conf(device, None, template, ds)
            if ds_conf is not None:
                deviceConfig.add(ds_conf)

    for component in device.getMonitoredComponents():
        deviceConfig.thresholds += component.getThresholdInstances(
            JMXDataSource.sourcetype)

        for template in component.getRRDTemplates():
            for ds in self._getDataSourcesFromTemplate(template):
                ds_conf = JMXDataSourceConfig(device, component, template, ds)
                #log.info("CHECKING DS: %s: %s is %s %s" % (ds.id, component.id, ds_conf.enabled, type(ds_conf.enabled)))
                if ds_conf is not None and str(ds_conf.enabled) ==  "True":  deviceConfig.add(ds_conf)
                #else: 
                    #log.info("EXCLUDING DS: %s: %s is %s" % (ds.id, component.id, ds_conf.enabled))

    # Don't both returning a proxy if there are no datasources.
    if not len(deviceConfig.jmxDataSourceConfigs.keys()):
        return None

    return deviceConfig

ZenJMXConfigService._createDeviceProxy = _createDeviceProxy


'''
We patch this method so that we use the 
"getPassword" method on password properties
'''
def copyProperties(self, device, ds):
    """
    copy the properties from the datasouce and set them
    as attributes
    """
    #log.debug("patched copyProperties")
    for prop in ds._properties:
        propName = prop['id']
        if 'password' in propName.lower() or prop['type'] == 'password':
            #log.info("getting password property for %s: %s" % (ds.id,propName))
            value = getattr(ds, propName)
            # it's a TALES attribute
            if str(value).find('$') >= 0:
                try:
                    # test if its a ConstructionKit object with getPassword method
                    # get just the referenced property id
                    id = value.split('/')[-1].replace('}','')
                    value = device.getPassword(id)
                except: 
                    # must be a built-in zProperty
                    value = talesEval('string:%s' % (value,), device)
        else:
            value = getattr(ds, propName)
            if str(value).find('$') >= 0:
                value = talesEval('string:%s' % (value,), device)
        # this is for handling boolean TALES for attribute property
        if 'auth' in propName:
            if value and value is not None: 
                value = str(value).lower().capitalize()
                value = bool(eval(value))
                #log.info("evaluating property %s: %s: %s %s" % (ds.id, propName, value, type(value)))
            else:
                value = False
        setattr(self, propName, value)

JMXDataSourceConfig.copyProperties = copyProperties


JDATA = getMBeanDef(VERSION, ROOT, BASE, 'JavaApp','JVM', 'JVMs' )
JDATA['packZProperties'] = [
                            ('zJavaAppPortRange', '1000-50000', 'string'),
                            ('zJavaAppScanTimeout', 5, 'int'),
                            ('zJolokiaProxyHost', 'localhost', 'string'),
                            ('zJolokiaProxyPort', 8888, 'int')
                            ]
JDATA['componentData']['displayed'] = 'id'
JDATA['componentData']['primaryKey'] = 'id'
JDATA['componentData']['properties'].pop('mbean')
JDATA['componentData']['properties']['parameters'] = addProperty('Parameters')
JDATA['componentData']['properties']['javaversion'] = addProperty('Java Version', optional=False)
JDATA['componentData']['properties']['vendorname'] = addProperty('JVM Vendor')
JDATA['componentData']['properties']['vendorproduct'] = addProperty('JVM Version', optional=False)

JavaAppDefinition = type('JavaAppDefinition', (BasicDefinition,), JDATA)


addDefinitionSelfComponentRelation(JavaAppDefinition,
                          'javaapp', ToOne, '%s.%s.%s' % (ROOT, BASE, 'JavaApp'),'parameters',
                          'osprocess',  ToOne, 'Products.ZenModel.OSProcess', 'displayName',
                          'OS Process', 'displayName')

# change the method for "setOsprocess" to set based on connected IpService->OsProcess

addDefinitionSelfComponentRelation(JavaAppDefinition,
                          'javaapp', ToOne, '%s.%s.%s' % (ROOT, BASE, 'JavaApp'),'port',
                          'ipservice',  ToOne, 'Products.ZenModel.IpService', 'port',
                          'IP Service', 'port')

# too hard to try to parse the java command line args b/c of the 128 character path limit, so go by common port
def setOsprocess(ob, name=''): 
    # first find the ipservice object
    #log.info("setting osprocess for %s" % ob.id)
    ipsvc = ob.findDeviceComponent(ob.device(), 'IpService', 'port', ob.port)
    # now see if the ipservice has a linked osprocess
    if ipsvc is not None:
        osproc = None
        if len(ipsvc.osprocess()) > 0: osproc = ipsvc.osprocess()[0]
        # if so, link it to the javaapp
        if osproc is not None: ob.setCustomRelation(osproc,'osprocess', 'javaapp')
    
JavaAppDefinition.componentMethods.append(setOsprocess)

#JavaApp.setOsprocess = setOsprocess

########### MEMORY POOL ###########
JavaMemoryPoolDefinition = type('JavaMemoryPoolDefinition', (BasicDefinition,), 
                                getMBeanDef(VERSION, ROOT, BASE, 'JavaMemoryPool','JVM Memory Pool', 'JVM Memory Pools' ))
addMBeanRelations(JavaMemoryPoolDefinition)

########### GARBAGE COLLECTOR ###########
JavaGarbageCollectorDefinition = type('JavaGarbageCollectorDefinition', (BasicDefinition,), 
                                      getMBeanDef(VERSION, ROOT, BASE, 'JavaGarbageCollector','JVM GC', 'JVM GCs'))
addMBeanRelations(JavaGarbageCollectorDefinition)

