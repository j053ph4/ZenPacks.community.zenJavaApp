'''
args:  compFacade,compClass,facadeName,iFacadeName,facadeMethodName, createMethod, singular
'''

import os,re
import logging
log = logging.getLogger('zen.zenJavaAppFacade')

from zope.interface import implements
from Products.Zuul.facades import ZuulFacade
from Products.Zuul.utils import ZuulMessageFactory as _t
from JavaApp import *
from .interfaces import *

class zenJavaAppFacade(ZuulFacade):
    implements(IzenJavaAppFacade)
    
    def addJavaApp(self, ob, **kwargs):
    	target = ob
    
        from Products.ZenUtils.Utils import prepId
        from ZenPacks.community.zenJavaApp.JavaApp import JavaApp
        import re
        cid = 'javaapp' 
        for k,v in kwargs.iteritems():
            if type(v) != bool:
                cid += str(v)
        cid = re.sub('[^A-Za-z0-9]+', '_', cid)
        id = prepId(cid)
        component = JavaApp(id)
        relation = target.os.javaApps
        relation._setObject(component.id, component)
        component = relation._getOb(component.id)
        for k,v in kwargs.iteritems():
            setattr(component,k,v) 
        
    
    
    

    	return True, _t("Added Java Application for device " + target.id)

