from Products.Zuul.form import schema
from Products.Zuul.interfaces.component import IComponentInfo
from Products.Zuul.utils import ZuulMessageFactory as _t

class IJavaAppInfo(IComponentInfo):
    javaPort = schema.Text(title=u"Port")
    javaUser = schema.Text(title=u"User",readonly=False,group='Details')
    javaPass = schema.Text(title=u"Password",readonly=False,group='Details')




