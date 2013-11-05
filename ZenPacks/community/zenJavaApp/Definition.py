from ZenPacks.community.ConstructionKit.BasicDefinition import *
from ZenPacks.community.ConstructionKit.Construct import *

DATA = {
        'version' : Version(2, 2, 0),
        'zenpackbase': "zenJavaApp",
        'packZProperties' : [ ('zJavaAppPortRange', '1000-50000', 'string'), ],
        'component' : 'JavaApp',
        'componentData' : {
                          'singular': 'Java Application',
                          'plural': 'Java Applications',
                          'properties': { 
                                        'port' : addProperty('Port','Basic','80'),
                                        'auth': addProperty('Authenticate','Authentication', False, ptype='boolean'),
                                        'user' : addProperty('User','Authentication'),
                                        'password' : addProperty('Password','Authentication',ptype='password'),
                                        'oGen' : addProperty('Old Gen','Gen','java.lang:type=MemoryPool,name=CMS Old Gen'),
                                        'pGen' : addProperty('Perm Gen','Gen','java.lang:type=MemoryPool,name=CMS Perm Gen'),
                                        'isWorking' :  addProperty('Available','Operational',False, ptype='boolean'),
                                        'validGen' : addProperty('Valid Gen','Operational',False, ptype='boolean'),
                                        'parameters': addProperty('Parameters'),
                                        },
                          },
        }

JavaAppDefinition = type('JavaAppDefinition', (BasicDefinition,), DATA)

addDefinitionSelfComponentRelation(JavaAppDefinition,
                          'javaapp', ToOne, 'ZenPacks.community.zenJavaApp.JavaApp','port',
                          'ipservice',  ToOne, 'Products.ZenModel.IpService', 'port',
                          'IP Service', 'port')

addDefinitionSelfComponentRelation(JavaAppDefinition,
                          'javaapp', ToOne, 'ZenPacks.community.zenJavaApp.JavaApp','parameters',
                          'osprocess',  ToOne, 'Products.ZenModel.OSProcess', 'parameters',
                          'OS Process', 'id')
