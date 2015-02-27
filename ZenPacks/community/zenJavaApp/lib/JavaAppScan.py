import re,os,time,random
from subprocess import *
import cPickle as pickle
from Products.ZenUtils.Utils import zenPath
from JolokiaProxyHandler import *
import logging
log = logging.getLogger('zen.zenhub')

#def getInfo(self): return {'isJmx': False,'useAuth': False,'validAuth': False, 'isGood': False, 'protocol': ''}
def getExecOutput(args, timeout=15):
    '''periodically check process output'''
    log.debug('getting output for: %s with timeout: %s' % (' '.join(args), timeout))
    timed_out = False
    output = Popen(args, stderr=STDOUT, stdout=PIPE)
    while (output.poll() is None and timeout > 0):
        time.sleep(1)
        timeout -= 1
    if not timeout > 0:
        timed_out = True
        try: output.terminate()
        except: pass
    try: return output.communicate()[0].split("\n")  
    except: return []

class JavaAppScan(object):
    '''
        Identify JMX-capable ports
    '''
    def __init__(self, ipaddr=None, portrange='1000-50000', username=None, password=None, proxyhost='localhost', proxyport=8888, timeout=10, maxage=21600):
        self.ipaddr = ipaddr
        self.portrange = portrange
        self.username = username
        self.password = password
        self.cachefile = "/tmp/%s.%s.scan" % (ipaddr, portrange)
        self.maxage = maxage
        self.portdict = {}
        self.timeout = int(timeout)
        self.proxyhost = proxyhost
        self.proxyport = proxyport
        self.proxy = JolokiaProxyHandler(self.proxyhost, self.proxyport, self.timeout)
    
    def readCache(self):
        '''read dictionary from cache'''
        log.debug('reading cache from %s' % self.cachefile)
        with open(self.cachefile, 'rb') as fp: self.portdict = pickle.load(fp)
    
    def writeCache(self):
        '''write dictionary to cache'''
        log.debug('writing cache to %s' % self.cachefile)
        with open(self.cachefile, 'wb') as fp: pickle.dump(self.portdict, fp)
    
    def useCache(self):
        '''decide whether or not to use cache file'''
        log.debug('checking cache file %s' % self.cachefile)
        if os.path.isfile(self.cachefile):
            #cachemaxage = time.time() - self.maxage #- random.randint(0, self.maxage) # 12 hours
            cachedata = os.stat(self.cachefile)
            cacheage = time.time() - cachedata.st_mtime
            log.debug("cache age: %s max age: %s" % (cacheage, self.maxage))
            if cacheage > self.maxage: return False
            # go ahead and flush if running manually and greater than 1 minute old but less than 5
            #if cacheage > 30 and cacheage < 300 : return False
        return True
    
    def evalPorts(self):
        ''''''
        log.debug('evalPorts')
        if self.useCache() is True:
            try: 
                log.debug('reading cached data')
                self.readCache()
            # start over if needed
            except: 
                log.debug('error reading cache, rescanning')
                self.scanPorts(True)
                self.writeCache()
        else: 
            log.debug('cache doesn\'t exist or is too old, rescanning')
            self.scanPorts(True)
            self.writeCache()
    
    def scanPorts(self, eval=False):
        '''return list of open ports within range'''
        log.debug('scanning ports: %s on %s' % (self.portrange, self.ipaddr) )
        args = [zenPath('libexec', 'nmap'),'-sS','-p',self.portrange,self.ipaddr]
        lines = getExecOutput(args, self.timeout)
        for line in lines:
            info = line.split()
            if len(info) == 3:
                port, state, service = info
                port = port.split('/')[0]
                if state == "open":
                    if eval is True: self.portdict[port] = self.testPort(port)
                    else: self.portdict[port] = getInfo()
    
    def testPort(self, port):
        ''''''
        log.debug("testing connection to port: %s" % port)
        start = time.time()
        status = self.proxy.connectEval(self.ipaddr, port, self.username, self.password)
        log.debug("port %s test completed in %0.1fs" % (port, (time.time() - start)))
        return status
    
    def beanExists(self, port, mbean, protocol=None):
        '''decide whether a given mbean exists'''
        self.proxy.checkConnect(self.ipaddr, port, self.username, self.password, protocol)
        searchresult = self.proxy.proxy.request(type='search', mbean=mbean)
        if 'value' in searchresult.keys() and len(searchresult['value']) > 0: return True
        return False
    
    def getBeanAttributeValues(self, port, mbean, attributes, protocol=None):
        '''return list of values for given mbeans'''
        result = {}
        self.proxy.checkConnect(self.ipaddr, port, self.username, self.password, protocol)
        for attr in attributes:
            output = self.proxy.proxy.request(type='read', mbean=mbean, attribute=attr)
            if 'value' in output.keys(): result[attr] = output['value']
        return result
