from Products.Zuul.form import schema
from Products.Zuul.interfaces.component import IComponentInfo
from Products.Zuul.utils import ZuulMessageFactory as _t

class IJavaAppInfo(IComponentInfo):
    javaPort = schema.Text(title=u"Port",readonly=True,group='Details')
    javaUser = schema.Text(title=u"User",group='Details')
    javaPass = schema.Password(title=u"Password",group='Details')
    javaAuth = schema.Bool(title=u"Authenticate",group='Details')



