from zif.jsonserver import MethodPublisher
from zope.component import getUtility
from qreature.interfaces import IQuizAnswer, IQreatureIntIds
from zope.event import notify        
from qreature.browser.events import CachedObjectChangedEvent

class Async(MethodPublisher):
    """ """
    def flashEditAnswer(self,id_body):
        try:
            int_ids = getUtility(IQreatureIntIds)
            ob = int_ids.getObject(int(id_body[0]))
            if not IQuizAnswer.providedBy(ob): return (0-1)
            ob.body = id_body[1]
            notify(CachedObjectChangedEvent([ob]))
            return 1
        except:
            return (0-1)
        