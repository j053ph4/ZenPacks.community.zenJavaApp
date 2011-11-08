from zope.component import adapts
from zope.interface import implements
from Products.Zuul.infos import ProxyProperty
from Products.Zuul.infos.component import ComponentInfo
from ZenPacks.community.zenJavaApp.JavaApp import JavaApp
from ZenPacks.community.zenJavaApp.interfaces import IJavaAppInfo

class JavaAppInfo(ComponentInfo):
    implements(IJavaAppInfo)
    adapts(JavaApp)
    javaPort = ProxyProperty("javaPort")
    javaUser = ProxyProperty("javaUser")
    javaPass = ProxyProperty("javaPass")
    javaAuth = ProxyProperty("javaAuth")

    
    
