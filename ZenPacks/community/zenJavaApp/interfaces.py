
'''
args: componentInterface,comopnentInterfaceproperties,componentIFacade,iFacadeMethodName
'''

from Products.Zuul.form import schema
from Products.Zuul.interfaces.component import IComponentInfo
from Products.Zuul.interfaces import IFacade

from Products.Zuul.utils import ZuulMessageFactory as _t

from Products.ZenModel.ZVersion import VERSION as ZENOSS_VERSION
from Products.ZenUtils.Version import Version
if Version.parse('Zenoss ' + ZENOSS_VERSION) >= Version.parse('Zenoss 4'):
    SingleLineText = schema.TextLine
    MultiLineText = schema.Text
else:
    SingleLineText = schema.Text
    MultiLineText = schema.TextLine


class IJavaAppInfo(IComponentInfo):
    isWorking = schema.Bool(title=_t(u'Available'))
    oGen = SingleLineText(title=_t(u'Old Gen'))
    user = SingleLineText(title=_t(u'User'))
    validGen = schema.Bool(title=_t(u'POST'))
    pGen = SingleLineText(title=_t(u'Perm Gen'))
    password = SingleLineText(title=_t(u'Password'))
    port = SingleLineText(title=_t(u'Port'))
    auth = schema.Bool(title=_t(u'Authenticate'))



class IzenJavaAppFacade(IFacade):
    def addJavaApp(self, ob, **kwargs):
        ''''''

