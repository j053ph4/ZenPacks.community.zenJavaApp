from pyjolokia import Jolokia, JolokiaError
import pprint
import traceback
#import sys, os, re, pexpect
import logging
log = logging.getLogger('zen.zenhub')

def getInfo(): return {'isJmx': False,'useAuth': True,'validAuth': False, 'isGood': False, 'protocol': 'RMI'}


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
    
    def connectEval(self, host=None, port=None, user=None, password=None, protocol=None):
        ''''''
        data = {
                'isJmx': False,
                'useAuth': True,
                'validAuth': False, 
                'isGood': False, 
                'protocol': None
                }
        #print "evaluating %s:%s with u:%s and p:%s" % (host, port, user, password)
        self.connect(host, port, user, password, protocol)
        return self.jmx.getData()
    
    def reset(self):
        ''''''
        #print 'resetting'
        self.proxy.proxy(url='', user='', password='')
        self.jmx = None
    
    def connect(self, host=None, port=None, user=None, password=None, protocol=None):
        ''' connect to jmx via proxy'''
        self.reset()
        #print "connecting to %s: %s" % (host, port)
        self.jmx = JMXConnect(host, port, user, password, protocol)
        self._connect(protocol)
        #print "COMPLETE"
        #self.jmx.info()
    
    def _connect(self, protocol=None):
        #print "_connect: %s" % str(protocol)
        if protocol is not None:
            #print "setting url"
            self.jmx.setURL(protocol)
            #print "set proxy url to %s" % self.jmx.url
            self.proxy.proxy(url=self.jmx.url, user=self.jmx.user, password=self.jmx.password)
            #print "Testing connected"
            self.jmx.connected = self.isConnected()
        else:
            protocol = self.findProtocol()
            if protocol is not None: self._connect(protocol)
            else:
                self.jmx.url = ''
                self.jmx.connected = False
                self.jmx.protocol = None
                self.proxy.proxy(url='', user='', password='')
    
    def findProtocol(self):
        '''try to determine what protocol a remote host uses'''
        #print "findProtocol"
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
        #print "isConnected"
        if self.jmx.result is None: self.testConnection()
        if self.jmx.result is not None and self.jmx.result['status'] == 200: return True
        return False
    
    def testConnection(self):
        '''try to find mbeans that should be on any JVM'''
        #print "testConnection"
        self.jmx.result = None
        try:  self.jmx.result = self.proxy.request(type='search', mbean='java.lang:*')
        except: pass
    
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
    
    def parseResult(self, result):
        ''''''
        output = []
        if 'value' in result.keys():
            if type(result['value']) is list:
                for bean in result['value']:  output.append(self.parseData(bean))
        return output
    
    def parseDictToList(self, result):
        '''return list of dictionaries describing attributes of MBean path'''
        output = []
        if type(result) == dict:
            for k, v in result.items():
                info = self.parseData(k)
                info['value'] = v
                output.append(info)
        return output
    
    def get(self, host=None, port=None, user=None, password=None, mbean=None, attribute=None, task='search', protocol=None):
        ''''''
        self.checkConnect(host, port, user, password, protocol)
        #if self.jmx is None or self.jmx.connected is False: self.connect(host, port, user, password, protocol)
        try:
            if attribute is not None: result = self.proxy.request(type=task, mbean=mbean, attribute=attribute)
            else:  result = self.proxy.request(type=task, mbean=mbean)
            return self.parseResult(result)
        except: return []
    
    def checkConnect(self, host=None, port=None, user=None, password=None, protocol=None):
        '''decide whether to start new connection'''
        new = False
        if self.jmx is None: new = True 
        else:
            if self.jmx.connected is False: new = True 
            else:
                if self.jmx.host != host:  new = True
                if self.jmx.port != port:  new = True
        if new is True: self.connect(host, port, user, password, protocol)


class JMXConnect(object):
    ''' object to contain connection properties'''
    host=None
    port=None
    username = None
    password = None
    protocol=''
    connected = False
    url = ''
    proxy = None
    result = None
    protocolURLs = {
                    'RMI' : 'service:jmx:rmi:///jndi/rmi://%s/jmxrmi',
                    'REMOTING-JMX' : 'service:jmx:remoting-jmx://%s',
                    'JMXMP' : 'service:jmx:jmxmp://%s'
    }
    
    def __init__(self, host=None, port=None, user=None, password=None, protocol=None, connected=False):
        ''''''
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.protocol = protocol
        self.connected = connected
    
    def info(self):
        print 'host: %s' % self.host
        print 'port: %s' % self.port
        print 'protocol: %s' % self.protocol
        print 'connected: %s' % self.connected
    
    def getData(self):
        '''return data dictionary describing this connection'''
        data = getInfo()
        data['isGood'] = self.connected
        data['protocol'] = self.protocol
        data['validAuth'] = self.connected
        if self.protocol is not None: data['isJmx'] = True
        return data
    
    def setURL(self, protocol='RMI'):
        ''''''
        addr = '%s:%s' % (self.host, self.port)
        self.url  = self.protocolURLs[protocol] % addr
    
