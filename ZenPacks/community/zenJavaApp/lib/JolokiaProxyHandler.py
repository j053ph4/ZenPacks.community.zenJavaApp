from pyjolokia import Jolokia, JolokiaError
import pprint
import traceback
#import sys, os, re, pexpect
import logging
log = logging.getLogger('zen.zenhub')

'''
dictionary of known vendor information like:

    COMPANY { search: 'PATH', jvmvendor : ['bean': 'PATH', 'attributes': [ATTRIBUTES] }
'''

VENDORSEARCH = {
    'Oracle': {
                'search':'amx:*',
                'name': 'Glassfish',
                'jvmvendor': [ 
                    {'bean':'amx:pp=/J2EEDomain,type=J2EEServer,name=server,j2eeType=J2EEServer', 'attributes': ['serverVersion']},
                    {'bean':'amx:j2eeType=J2EEServer,name=server', 'attributes': ['serverVersion']},
                    ]
                },
    'RedHat': {
                'name': 'JBoss',
                'search':'jboss.ws:*',
                'jvmvendor': [ 
                    {'bean':'jboss.as:management-root=server', 'attributes': ['productName', 'productVersion']},
                    {'bean':'jboss.system:type=Server', 'attributes': ['VersionName', 'VersionNumber']},
                    ]
                },
    'Apache': {
                'name': 'Tomcat',
                'search':'Catalina:*',
                'jvmvendor': [{'bean':'Catalina:type=Server', 'attributes': ['serverInfo']},]
                },
    'Terracotta': {
                'name': 'Terracotta',
                'search':'org.terracotta.internal:type=Terracotta Server,name=*',
                'jvmvendor': [{'bean':'org.terracotta.internal:type=Terracotta Server,name=Terracotta Server', 'attributes': ['Version']},]
                },
    'SiriusXM': {
                'name': 'Logsender',
                'search':'atxg:type=*,name=loggingChannel',
                'jvmvendor': [{'bean':'', 'attributes': []},]  
                },
    'Graylog': {
                'name': 'Graylog2',
                'search':'metrics:name=*',
                'jvmvendor': [{'bean':'', 'attributes': []},]
                },
    'Sun': {
            'name': 'JVM',
            'search':'java.lang:*',
            'jvmvendor': [{'bean':'java.lang:type=Runtime', 'attributes': ['vmName','vmVersion']},]
            },
}


class JMXConnect(object):
    ''' Container for connection attributes'''
    host=None
    port=None
    auth = True
    validAuth=False
    user = None
    password = None
    protocol = None
    connected = False
    url = ''
    proxy = None
    result = None
    javaversion = 'Unknown'
    vendorname = 'Unknown'
    vendorproduct = 'Java'
    
    def __init__(self, host=None, port=None, user=None, password=None, protocol=None, connected=False):
        ''''''
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.protocol = protocol
        self.connected = connected
    
    def status(self):
        '''return True if connection is good'''
        if self.result is not None and self.result['status'] == 200: return True
        return False
    
    def eval(self):
        '''if port is JMX but not connected, we assume we don't have the right auth info'''
        if self.protocol is not None:
            self.validAuth = self.connected
    
    def data(self):
        '''return data dictionary describing this connection'''
        return self.__dict__.items()
    
    def setURL(self, protocol='RMI'):
        '''build the correct URL for JMX queries depending on the protocol'''
        protocolURLs = {
                        'RMI' : 'service:jmx:rmi:///jndi/rmi://%s/jmxrmi',
                        'REMOTING-JMX' : 'service:jmx:remoting-jmx://%s',
                        'JMXMP' : 'service:jmx:jmxmp://%s'
                        }
        addr = '%s:%s' % (self.host, self.port)
        self.url  = protocolURLs[protocol] % addr
    
    def info(self):
        '''print out connection info'''
        for k, v in self.data(): print '%s: %s' % k,v

    
class JolokiaProxyHandler(object):
    """ Handler for jmxterm session """
    def __init__(self, proxyhost='localhost', proxyport=8888, timeout=5, debug=False):
        ''''''
        self.proxyhost = proxyhost
        self.proxyport = proxyport
        self.debug = debug
        self.proxyaddress = '%s:%s' % (self.proxyhost, self.proxyport)
        self.proxy = Jolokia('http://%s/jolokia/' % self.proxyaddress)
        self.proxy.timeout = timeout
        self.order = ['RMI','REMOTING-JMX','JMXMP']
        # these outputs indicate JMX available, but bad credentials
        self.jmxReplies = [
                           #'Connection refused', 
                           'Invalid credentials', 
                           'Authentication failed', 
                           'SecurityException', 
                           'does not have administration access', 
                           'com.sun.enterprise.security.LoginException',
                           ]
        self.jmx = None
    
    def reset(self):
        ''' reset the proxy parameters '''
        self.proxy.proxy(url='', user='', password='')
        self.jmx = None
    
    def connectEval(self, host=None, port=None, user=None, password=None, protocol=None):
        '''poll the connected port for info'''
        # establish the connection
        self.connect(host, port, user, password, protocol)
        # only return JMX port info
        if self.jmx.protocol is not None:
            # don't bother trying to get other info if we can't connect
            if self.jmx.connected is True:  self.getJVMDetails()
            return self.jmx
        return None
    
    def connect(self, host=None, port=None, user=None, password=None, protocol=None):
        ''' connect to jmx via proxy'''
        self.reset()
        self.jmx = JMXConnect(host, port, user, password, protocol)
        self._connect(protocol)
    
    def _connect(self, protocol=None):
        '''connect with or without known protocol'''
        if protocol is not None:
            self.jmx.setURL(protocol)
            self.proxy.proxy(url=self.jmx.url, user=self.jmx.user, password=self.jmx.password)
            self.jmx.connected = self.isConnected()
            self.jmx.eval()
        else:
            protocol = self.findProtocol()
            # if found, retry with the known protocol
            if protocol is not None: self._connect(protocol)
            # otherwise we couldn't find it so reset everything
            else: 
                #self.reset()
                self.jmx.url = ''
                self.jmx.connected = False
                self.jmx.protocol = None
                self.proxy.proxy(url='', user='', password='')
    
    def findProtocol(self):
        '''try to determine what protocol a remote host uses'''
        for protocol in self.order:
            if self.usesProtocol(protocol) is True: 
                self.jmx.protocol = protocol
                return protocol
        return None
    
    def usesProtocol(self, protocol=None):
        '''decide if the remote jmx agent supports the given protocol'''
        #print 'testing protocol: %s' % protocol
        self._connect(protocol)
        self.testConnection()
        if self.jmx.result  is not None and 'status' in self.jmx.result.keys():
            if self.jmx.result['status'] == 200:  return True
            else:
                if 'stacktrace' in self.jmx.result.keys():
                    for line in self.jmx.result['stacktrace'].split('\n'):
                        # any of these implies correct protocol even if wrong parameters were
                        for reply in self.jmxReplies:
                            if reply in str(line): return True
        return False
    
    def isConnected(self):
        '''determine whether remote host is available'''
        if self.jmx.result is None: self.testConnection()
        return self.jmx.status()
    
    def testConnection(self):
        '''Test JMX connection by looking for generic mbean'''
        self.jmx.result = None
        try:  self.jmx.result = self.proxy.request(type='search', mbean='java.lang:*')
        except: pass
    
    def checkConnect(self, host=None, port=None, user=None, password=None, protocol=None):
        '''decide whether to start new connection'''
        new = False
        # completely new connection
        if self.jmx is None: new = True 
        else:
            if self.jmx.connected is False: new = True 
            else:
                if self.jmx.host != host:  new = True
                if self.jmx.port != port:  new = True
        if new is True: self.connect(host, port, user, password, protocol)
    
    def setJMX(self, jmx):
        '''reuse a given JMXConnect object'''
        self.jmx = jmx
        self._connect(self.jmx.protocol)
    
    def getJVMDetails(self):
        ''''''
        self.jmx.javaversion = self.getJavaVersion()
        self.jmx.vendorname = self.getJVMVendorName()
        self.jmx.vendorproduct = self.getJVMVendorProduct(self.jmx.vendorname)
    
    def getJavaVersion(self):
        '''determine what version of Java is running'''
        result = self.getBeanAttributeValues('java.lang:type=Runtime', ['VmName', 'VmVendor', 'VmVersion'])
        if len(result.values()) > 0:  return str(' '.join(result.values()))
        else: return 'Unknown'
    
    def getJVMVendorName(self):
        '''determine who is the JVM vendor'''
        vendor = "Unknown"
        for v in VENDORSEARCH.keys():
            # skip identifying as Sun unless there's no alternative
            if v == 'Sun': continue
            if self.beanExists(VENDORSEARCH[v]['search']) is True: vendor = v
        if vendor == 'Unknown' and self.beanExists(VENDORSEARCH['Sun']['search']) is True: vendor = 'Sun'
        return vendor
    
    def getJVMVendorProduct(self, vendor='Unknown'):
        '''determine what version of Java is running'''
        product = "Java"
        if vendor in VENDORSEARCH.keys():
            for data in VENDORSEARCH[vendor]['jvmvendor']:
                result = self.getBeanAttributeValues(data['bean'], data['attributes'])
                product = VENDORSEARCH[vendor]['name']
                # try to get more details about the 
                if len(result.values()) > 0:  
                    version = str(' '.join(result.values()))
                    if product not in version: product = '%s %s' % (product, version)
                    else: product = version
        # return the generic name if we didn't find anything
        return product
    
    def beanExists(self, mbean=None):
        '''return True if mbean exists'''
        searchresult = self.proxy.request(type='search', mbean=mbean)
        if 'value' in searchresult.keys() and len(searchresult['value']) > 0: return True
        return False
    
    def getBeanAttributeValues(self, mbean=None, attributes=[]):
        '''return list of attribute values for a given mbean'''
        result = {}
        for attr in attributes:
            output = self.proxy.request(type='read', mbean=mbean, attribute=attr)
            if 'value' in output.keys(): result[attr] = output['value']
        return result
    
    def getAttribute(self, mbean, attribute):
        '''return single-valued mbean attribute'''
        try: return self.getBeanAttributeValues(mbean, [attribute])[attribute]
        except: return None
    
    def search(self, mbean):
        '''return parsed list of normalized mbean paths matching search'''
        #log.debug("getting %s MBeans for %s" % (mbean, port))
        output = []
        result = self.get(mbean)
        for r in result:
            data = {
                    'fullpath' : str(r['fullname']), 
                    'mbean': '',
                    } #, 'enabled': True}
            if 'name' in r.keys():  data ['mbean'] = str(r['name'])
            else: data ['mbean'] = str(r['fullname'])
            for k,v in r.items():
                k = str(k)
                if k in ['fullname', 'name']: continue
                data[k] = str(v)
            output.append(data)
        return output
    
    def get(self, mbean=None, attribute=None, task='search'):
        '''perform task with mbean and attribute'''
        try:
            if attribute is not None: result = self.proxy.request(type=task, mbean=mbean, attribute=attribute)
            else:  result = self.proxy.request(type=task, mbean=mbean)
            return self.parseResult(result)
        except: return []
    
    def parseResult(self, result):
        '''return a list of parsed result data dictionaries'''
        output = []
        if 'value' in result.keys():
            if type(result['value']) is list:
                for bean in result['value']:  output.append(self.parseData(bean))
        return output
    
    def parseData(self, data):
        '''return dictionary of output'''
        info = {'fullname' : data}
        start = data.find(':')+len(':')
        data = data[start:]
        keyvals = data.split(',')
        for kv in keyvals:
            k,v = kv.split('=')
            info[k] = v
        return info
    
    def parseDictToList(self, result):
        '''return list of dictionaries describing attributes of MBean path'''
        output = []
        if type(result) == dict:
            for k, v in result.items():
                info = self.parseData(k)
                info['value'] = v
                output.append(info)
        return output

