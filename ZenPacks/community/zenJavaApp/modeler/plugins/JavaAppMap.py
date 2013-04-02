from Products.DataCollector.plugins.CollectorPlugin import PythonPlugin
from Products.DataCollector.plugins.DataMaps import ObjectMap
from Products.ZenUtils.Utils import zenPath,prepId
from ZenPacks.community.zenJavaApp.Definition import *
import re,os,time,random
from subprocess import *

class JavaAppScan():
    '''
        Identify JMX-capable ports
    '''
    jarFile = "%s/../../bin/cmdline-jmxclient-0.10.3.jar" % os.path.dirname(os.path.realpath(__file__))
    maxage = 43200 # max age in secs
    usingCache = False
    
    def __init__(self, device, ipaddr, portrange, username=None, password=None):
        self.device = device
        self.ipaddr = ipaddr
        self.portrange = portrange
        self.username = username
        self.password = password
        self.cachefile = "/tmp/%s.scan" % device
        self.portdict = {}

    def readCache(self):
        """
            read dictionary from cache
        """
        file = open(self.cachefile,'r')
        self.portdict = eval(file.readlines()[0].rstrip())
        
    def writeCache(self):
        """
            write dictionary to cache
        """
        file = open(self.cachefile,'w')
        file.write(str(self.portdict)+"\n")
        
    def checkCache(self):
        """
            check validity of cache file
        """
        if os.path.isfile(self.cachefile):
            cachemaxage = time.time() - self.maxage - random.randint(0,self.maxage) # 12 hours
            cachedata = os.stat(self.cachefile)
            cacheage = cachedata.st_mtime
            if cacheage > cachemaxage:
                self.usingCache = True
        if self.usingCache == True:
            self.readCache()
        else:
            self.scanPorts()

    def evalPorts(self):
        """
        """
        self.checkCache()
        if self.usingCache == False:
            for port in self.portdict.keys():
                self.testPort(port)
            self.writeCache()
            
    def testPort(self,port):
        """
            test whether query output is from JMX protocol
        """
        lines = self.jmxQuery(port, '-')
        for line in lines:
            if re.search('java\.lang:type=Memory',line) != None :
                self.portdict[port]['isJmx'] = True
            if re.search('Connection refused',line) != None :
                self.portdict[port]['isJmx'] = True
                self.portdict[port]['useAuth'] = True
            if re.search('Invalid credentials',line) != None :
                self.portdict[port]['isJmx'] = True
                self.portdict[port]['useAuth'] = True
            if re.search('Authentication failed',line) != None :
                self.portdict[port]['isJmx'] = True
                self.portdict[port]['useAuth'] = True
                
        if self.portdict[port]['isJmx'] == True and self.portdict[port]['useAuth'] == True:
            auth = "%s:%s" %(self.username, self.password)
            lines = self.jmxQuery(port, auth)
            for line in lines:
                if re.search('java\.lang:type=Memory',line) != None :
                    self.portdict[port]['validAuth'] = True
                    
    def getExecOutput(self,args,timeout=5):
        """
        """
        timed_out = False
        output = Popen(args,stderr=STDOUT,stdout=PIPE)
        lines = []
        while (output.poll() is None and timeout > 0):
            time.sleep(1)
            timeout -= 1
        if not timeout > 0:
            try:
                output.terminate()
            except:
                pass
            timed_out = True
        else:
            timed_out = False
        try:
            lines = output.communicate()[0].split("\n")  
        except:
            pass
        return lines

    def scanPorts(self):
        """
            return list of open ports within range
        """
        args = [zenPath('libexec', 'nmap'),'-sS','-p',self.portrange,self.ipaddr]
        lines = self.getExecOutput(args,30)
        for line in lines:
            info = line.split()
            #log.debug('port %s' % info)
            if len(info) == 3:
                port,state,service = info
                port = port.split('/')[0]
                if state == "open":
                    self.portdict[port] = {'isJmx': False, 'useAuth': False, 'validAuth': False}
                    
    def jmxQuery(self, port, auth, mbean='',attribute=''):
        """
            execute jmx query
        """
        deststring = '%s:%s' % (self.device,str(port))
        #jarfile = zenPath('libexec') + "/cmdline-jmxclient"
        args = ['/usr/bin/java','-jar',self.jarFile,auth,deststring,mbean,attribute]
        return self.getExecOutput(args) 


class JavaAppMap(PythonPlugin):
    """Map JMX Client output table to model."""
    
    constr = Construct(Definition)
    
    compname = "os"
    relname = constr.relname
    modname = constr.zenpackComponentModule
    baseid = constr.baseid

    deviceProperties = PythonPlugin.deviceProperties + (
                    'zJmxUsername',
                    'zJmxPassword',
                    'zJavaAppPortRange',
                    'manageIp',
                    )

    def getGenType(self, port, auth, info, log):
        """ find number of currently connected clients
        """
        baseString = 'java.lang:type=MemoryPool,name='
        try:
            lines = self.scan.jmxQuery(port, auth)
            for line in lines:
                keyvals = line.split(',')
                if re.search('MemoryPool',line) != None:
                    name = keyvals[0].split('=')[1]
                    if re.search('Old Gen',name) != None:
                        info['oGen'] = baseString+name
                        info['validGen'] = True
                    if re.search('Perm Gen',name) != None:
                        info['pGen'] = baseString+name
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
            if entry['isJmx'] == True:
                auth = "%s:%s" %(device.zJmxUsername, device.zJmxPassword)
                log.debug('Testing for Oldgem/Permgem type at %s:%s' % (device.id, port))
                #lines = self.scan.jmxQuery(port, auth)
                info = {}
                name = "%s_%s" % (self.baseid,str(port))
                info['id'] = prepId(name)
                info['port'] = port
                info['auth'] = entry['useAuth']
                if entry['useAuth'] == False: # authentication isn't needed
                    info['isWorking'] = True
                    info['user'] = ''
                    info['password'] = ''
                else:
                    if entry['validAuth'] == True: # we can use the zJmxPassword
                        info['user'] = device.zJmxUsername
                        info['password'] = device.zJmxPassword
                        info['isWorking'] = True
                    else:
                        info['isWorking'] = False # we don't know the username/password
                        
                if info['isWorking'] == True:
                    info = self.getGenType(port,auth,info,log) # since it's working, lets find the Gen type
                output.append(info)
        return output
    
    def process(self, device, results, log):
        log.info("results: %s" % results)
        rm = self.relMap()
        for result in results:
            om = self.objectMap(result)
            om.monitor = result['isWorking']
            rm.append(om)
        return rm

