from Products.ZenModel.OSComponent import OSComponent
from Products.ZenModel.ZenPackPersistence import ZenPackPersistence
from Products.ZenModel.ManagedEntity import ManagedEntity
from Products.ZenRelations.RelSchema import *

'''
args:  classname,classname,properties,_properties,relname,sortkey,viewname
'''

class JavaApp(OSComponent, ManagedEntity, ZenPackPersistence):
    '''
    	basic Component class
    '''
    
    portal_type = meta_type = 'JavaApp'
    
    isWorking = False
    oGen = 'java.lang:type=MemoryPool,name=CMS Old Gen'
    user = None
    validGen = False
    pGen = 'java.lang:type=MemoryPool,name=CMS Perm Gen'
    password = None
    port = '80'
    auth = False

    _properties = (
    {'id': 'isWorking', 'type': 'boolean','mode': '', 'switch': 'None' },
    {'id': 'oGen', 'type': 'string','mode': '', 'switch': 'None' },
    {'id': 'user', 'type': 'string','mode': '', 'switch': 'None' },
    {'id': 'validGen', 'type': 'boolean','mode': '', 'switch': 'None' },
    {'id': 'pGen', 'type': 'string','mode': '', 'switch': 'None' },
    {'id': 'password', 'type': 'string','mode': '', 'switch': 'None' },
    {'id': 'port', 'type': 'string','mode': '', 'switch': 'None' },
    {'id': 'auth', 'type': 'boolean','mode': '', 'switch': 'None' },

    )
    
    _relations = OSComponent._relations + (
        ('os', ToOne(ToManyCont, 'Products.ZenModel.OperatingSystem', 'javaApps')),
        )

    isUserCreatedFlag = True
    def isUserCreated(self):
        return self.isUserCreatedFlag
        
    def statusMap(self):
        self.status = 0
        return self.status
    
    def getStatus(self):
        return self.statusMap()
    
    def primarySortKey(self):
        return self.port
    
    def viewName(self):
        return self.port
    
    name = titleOrId = viewName


