from zope.interface import implements
from Products.Zuul.infos import ProxyProperty
from Products.Zuul.infos.component import ComponentInfo
from ZenPacks.community.zenJavaApp.interfaces import *

'''
args:  zenpack,compInfo,compInterface,infoProperties
'''

class JavaAppInfo(ComponentInfo):
    implements( IJavaAppInfo )
    isWorking = ProxyProperty('isWorking')
    oGen = ProxyProperty('oGen')
    user = ProxyProperty('user')
    validGen = ProxyProperty('validGen')
    pGen = ProxyProperty('pGen')
    password = ProxyProperty('password')
    port = ProxyProperty('port')
    auth = ProxyProperty('auth')


