from qreature.interfaces import IQreaturePrincipalInfo,IQreatureAvatar
from zope.interface import implements
from persistent import Persistent
from zope.schema.fieldproperty import FieldProperty
from zope.app.file.image import getImageInfo


class QuizPrincipalData(Persistent):
    __name__ = __parent__ = None
    implements(IQreaturePrincipalInfo)
    uri = FieldProperty(IQreaturePrincipalInfo['uri'])
    about = FieldProperty(IQreaturePrincipalInfo['about'])
    avatar = FieldProperty(IQreaturePrincipalInfo['avatar'])
    

class Avatar(object):
    implements(IQreatureAvatar)
    def __init__(self, data='', contentType=''):
        self.data = data
        self.contentType, self._width, self._height = getImageInfo(data)
        self.position = 0
    def write(self,data):
        if self.position==0:
            self.data = data
            self.position=len(data)
        else:
            self.data = self.data[:self.position] + data
    def seek(self,offset):
        self.position = offset
    def tell(self):
        return self.position
    def getImageSize(self):
        return (self._width, self._height)
    def getSize(self):
        return self.getImageSize()