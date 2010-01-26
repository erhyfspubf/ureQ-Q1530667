from zope.app.container.btree import BTreeContainer
from zope.interface import implements
from qreature.interfaces import IQuizContainer,IQuiz, IQuizResult, IQuizQuestion, IQuizAnswer, IAnswerDepends
from qreature.interfaces import IAnswerLeads,INewQuizEvent
from qreature.interfaces import IAnswerValue
from zope.schema.fieldproperty import FieldProperty
from persistent import Persistent
from zope.app.component.site import SiteManagerContainer
from zope.event import notify
from pagable.interfaces import IPagableRelative

class QuizContainer(BTreeContainer):
    implements(IQuizContainer,IPagableRelative)
    title = FieldProperty(IQuizContainer['title'])
    body = FieldProperty(IQuizContainer['body'])
    def __init__(self, title, body):
        self.title = title
        self.body = body
        super(QuizContainer, self).__init__()
    
class Quiz(SiteManagerContainer,QuizContainer):
    implements(IQuiz)
    def setSiteManager(self, site_manager):
        """ This method called from object added handler (see handlers)
        Firstly, I install SiteManager
        After: all folders and utilities via firing our custom event"""
        super(Quiz, self).setSiteManager(site_manager)
        notify(NewQuizEvent(self))
        
class NewQuizEvent(object):
    """ see interfaces. Its not a folder, but I put it here to avoid conflicts"""
    implements(INewQuizEvent)
    def __init__(self, site):
        self.object = site
    
class QuizResult(QuizContainer):
    implements(IQuizResult)
    
class QuizQuestion(QuizContainer):
    implements(IQuizQuestion)
    
class QuizAnswer(QuizContainer):
    implements(IQuizAnswer)
    
class AnswerDepends(Persistent):
    implements(IAnswerDepends)
    __name__ = __parent__ = None
    result_id = FieldProperty(IAnswerDepends['result_id'])
    depend_value = FieldProperty(IAnswerDepends['depend_value'])
    def __init__(self, result_id, depend_value):
        self.result_id = result_id
        self.depend_value = depend_value
        super(AnswerDepends, self).__init__()
        
class AnswerLeads(Persistent):
    implements(IAnswerLeads)
    __name__ = __parent__ =  None
    question_id = FieldProperty(IAnswerLeads['question_id'])
    def __init__(self, question_id):
        self.question_id = question_id
        super(AnswerLeads, self).__init__()
        
    
class AnswerValue(Persistent):
    implements(IAnswerValue)
    __name__ = __parent__ = None
    value = FieldProperty(IAnswerValue['value'])
    def __init__(self, value):
        self.value = value
        super(AnswerValue, self).__init__()    
    