from ZenPacks.community.ConstructionKit.Construct import *
from Products.ZenModel.migrate.Migrate import Version
import os

class Definition():
    """
    """
    version = Version(2, 0, 0)
    zenpackroot = "ZenPacks.community" # ZenPack Root
    zenpackbase = "zenJavaApp" # ZenaPack Name
    cwd = os.path.dirname(os.path.realpath(__file__)) # ZenPack files directory
    #dictionary of components
    component = 'JavaApp'
    componentData = {
                  'singular': 'Java Application',
                  'plural': 'Java Applications',
                  'displayed': 'id', # component field in Event Console
                  'primaryKey': 'id',
                  'properties': { 
                        # Basic settings
                        'port' : addProperty('Port','Basic','80',optional='false'),
                        # Authentication
                        'auth': addProperty('Authenticate','Authentication', False, ptype='boolean'),
                        'user' : addProperty('User','Authentication'),
                        'password' : addProperty('Password','Authentication',ptype='password'),
                        # Misc
                        'oGen' : addProperty('Old Gen','Gen','java.lang:type=MemoryPool,name=CMS Old Gen'),
                        'pGen' : addProperty('Perm Gen','Gen','java.lang:type=MemoryPool,name=CMS Perm Gen'),
                        'isWorking' :  addProperty('Available','Operational',False, ptype='boolean'),
                        'validGen' : addProperty('POST','Operational',False, ptype='boolean'),
                        },
                  }
    
    packZProperties = [
        ('zJavaAppPortRange', '1000-50000', 'string'),
        ]
    #dictionary of datasources
    createDS = False
    cmdFile = None
    provided = False
    cycleTime = 300
    timeout = 60
    datapoints = []
