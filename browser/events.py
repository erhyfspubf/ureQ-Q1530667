from qreature.browser.interfaces import ICachedObjectChangedEvent,ICleanCacheEvent, IQuizPublishedEvent
from zope.interface import implements
from qreature.browser.interfaces import IResultShown

class CachedObjectChangedEvent(object):
    implements(ICachedObjectChangedEvent)
    def __init__(self, ob):
        self.ob = ob
        
class CleanCacheEvent(object):
    implements(ICleanCacheEvent)
    def __init__(self, ob):
        self.ob = ob
        
class ResultShown(object):
    implements(IResultShown)
    def __init__(self,result):
        self.result = result
        
class QuizPublishedEvent(object):
    implements(IQuizPublishedEvent)
    def __init__(self, quiz):
        self.quiz = quiz