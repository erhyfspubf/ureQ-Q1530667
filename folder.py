from qreature.interfaces import IQreatureFolder, INewQreatureFolderEvent
from zope.app.container.btree import BTreeContainer
from zope.app.component.site import SiteManagerContainer
from zope.interface import implements
from zope.event import notify
from zope.schema.fieldproperty import FieldProperty

class QreatureFolder(SiteManagerContainer, BTreeContainer):
    implements(IQreatureFolder)
    login = FieldProperty(IQreatureFolder['login'])
    password = FieldProperty(IQreatureFolder['password'])
    confirm_password = FieldProperty(IQreatureFolder['confirm_password'])
    email = FieldProperty(IQreatureFolder['email'])
    url = FieldProperty(IQreatureFolder['url'])
    about = FieldProperty(IQreatureFolder['about'])
    def __init__(self, login, password, confirm_password, email, url="http://www.qreature.ru",about=u''):
        self.login = login
        self.password = password
        self.confirm_password = confirm_password
        self.email = email
        self.url = url + "/" + str(login)
        self.about = about
        super(QreatureFolder, self).__init__()
    
        
    def setSiteManager(self, site_manager):
        """ This method called from object added handler (see handlers)
        Firstly, I install SiteManager
        After: all folders and utilities via firing our custom event"""
        super(QreatureFolder, self).setSiteManager(site_manager)
        notify(NewQreatureFolderEvent(self))
    
class NewQreatureFolderEvent(object):
    """ see interfaces. Its not a folder, but I put it here to avoid conflicts"""
    implements(INewQreatureFolderEvent)
    def __init__(self, site):
        self.object = site