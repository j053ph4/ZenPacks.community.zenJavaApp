################################################################################
#
# This program is part of the zenJavaApplication Zenpack for Zenoss.
# This program can be used under the GNU General Public License version 2
# You can find full information here: http://www.zenoss.com/oss
#
################################################################################
from Products.ZenModel.DeviceComponent import DeviceComponent
from Products.ZenModel.ManagedEntity import ManagedEntity
from Products.ZenModel.ZenossSecurity import ZEN_CHANGE_DEVICE
from Products.ZenRelations.RelSchema import ToManyCont, ToOne

class JavaApp(DeviceComponent, ManagedEntity):
    """
    JavaApp models a java application server as a device component
    """
    meta_type = portal_type = "JavaApp"
    
    javaPort = ''
    javaUser = ''
    javaPass = ''
    javaAuth = True
    status = 1

    _properties = ManagedEntity._properties + (
        {'id':'javaPort', 'type':'string', 'mode':''},         
        {'id':'javaUser', 'type':'string', 'mode':''},
        {'id':'javaPass', 'type':'string', 'mode':''},
        {'id':'javaAuth', 'type':'boolean', 'mode':''},
        {'id':'status', 'type':'int', 'mode':''},
    )
    
    _relations = ManagedEntity._relations + (
        ('javaHost', ToOne(ToManyCont,
            'Products.ZenModel.Device.Device',
            'javaApp',
            ),
        ),
    )

    factory_type_information = ({
        'actions': ({
            'id': 'perfConf',
            'name': 'Template',
            'action': 'objTemplates',
            'permissions': (ZEN_CHANGE_DEVICE,),
        },),
    },)
    
    isUserCreatedFlag = True
    
    def isUserCreated(self):
        return self.isUserCreatedFlag
    
    def viewName(self):
        return self.javaPort
    
    titleOrId = name = viewName

    def primarySortKey(self):
        return self.javaPort

    def getStatus(self):
        self.status = 0
        return self.status
    
    def device(self):
        return self.javaHost()
    
    def manage_deleteComponent(self, REQUEST=None):
        url = None
        if REQUEST is not None:
            url = self.device().javaApps.absolute_url()
        self.getPrimaryParent()._delObject(self.id)
        if REQUEST is not None:
            REQUEST['RESPONSE'].redirect(url)
