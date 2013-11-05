import re,os,time,random
from subprocess import *
import cPickle as pickle
from Products.ZenUtils.Utils import zenPath

class JavaAppScan():
    '''
        Identify JMX-capable ports
    '''
    jarFile = "%s/bin/cmdline-jmxclient-0.10.3.jar" % os.path.dirname(os.path.realpath(__file__))
    timeout = 30
    
    def __init__(self, device, ipaddr, portrange, username=None, password=None, maxage=43200, usingCache=False):
        self.device = device
        self.ipaddr = ipaddr
        self.portrange = portrange
        self.username = username
        self.password = password
        self.cachefile = "/tmp/%s.scan" % device
        self.maxage = maxage
        self.usingCache = usingCache
        self.portdict = {}

    def readCache(self):
        """
            read dictionary from cache
        """
        with open(self.cachefile, 'rb') as fp:
            self.portdict = pickle.load(fp)
        
    def writeCache(self):
        """
            write dictionary to cache
        """
        with open(self.cachefile, 'wb') as fp:
            pickle.dump(self.portdict, fp)

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
            try:
                self.readCache()
            except:
                self.scanPorts()
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
        self.portdict[port] = self.getInfo()
        lines = self.jmxQuery(port, '-')
        authfailed = ['Connection refused', 'does not have administration access', 'Invalid credentials', 'Authentication failed']
        for line in lines:
            # first check for open access
            if re.search('java\.lang:type=Memory',line) != None :
                self.portdict[port]['isJmx'] = True
            # auth failures also reveal a JMX port
            for a in authfailed:
                if re.search(a,line) != None :
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
        lines = self.getExecOutput(args,self.timeout)
        for line in lines:
            info = line.split()
            if len(info) == 3:
                port,state,service = info
                port = port.split('/')[0]
                if state == "open":
                    self.portdict[port] = self.getInfo()
    
    def getInfo(self):
        info = {
                'isJmx': False,
                'useAuth': False,
                'validAuth': False
                }
        return info

    def jmxQuery(self, port, auth, mbean='',attribute=''):
        """
            execute jmx query
        """
        deststring = '%s:%s' % (self.device,str(port))
        args = ['/usr/bin/java','-jar',self.jarFile,auth,deststring,mbean,attribute]
        return self.getExecOutput(args) 
