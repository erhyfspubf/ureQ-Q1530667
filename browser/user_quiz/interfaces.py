from zope.interface import Interface, implements, Attribute
from zope.schema import Choice, Text
from zope.component import getUtility
from qreature.browser.interfaces import IQuizField
    
class IQuestionWidget(Interface):
    pass

class IAnswerWidget(Interface):
    pass

class IPreviousAnswersWidget(Interface):
    pass






class IQuestionBody(IQuizField):
    """ my own schema fields. used in 'DataManager' adapters"""
class QuestionBody(Text):
    implements(IQuestionBody)
    
    
class IAnswerChoice(IQuizField):
    """ my own schema fields. used in 'DataManager' adapters"""
class AnswerChoice(Choice):
    implements(IAnswerChoice)


class IPreviousAnswersChoice(IQuizField):
    """ my own schema fields. used in 'DataManager' adapters"""
class PreviousAnswersChoice(Choice):
    implements(IPreviousAnswersChoice)









class IQuizUnit(Interface):
    """ """
    question = QuestionBody(title=u'question', default=None,readonly=True)
    answer  = AnswerChoice(title=u'answer', vocabulary="Quiz Answers")
    
class IMultiPageQuizUnit(IQuizUnit):
    """ """    
    previous_answers = PreviousAnswersChoice(title=u'previous_answers', vocabulary="Quiz Answers")



class IMultiPageQuizForm(Interface):
    """ """
    
class ISinglePageQuizForm(Interface):
    """ """  
    

class IGroupPageQuizForm(Interface):
    pass


class IChecked(Interface):
    pass


class IPublished(Interface):
    pass


class IMultiPage(IChecked):
    """ implemented by the Quiz object itself"""

class ISinglePage(IChecked):
    """ implemented by the Quiz object itself"""

class IGroupPage(IChecked):
    """implemented by the Quiz object itself"""
  
class IResult(Interface):
    """ result view"""
    def calculate():
        """ """
    def calculate_for_slots():
        """ """
    def calculate_for_scale():
        """ """
    def getAnswers():
        """ """
    values = Attribute(u'Values')
    result = Attribute(u'Result')
    int_ids= Attribute(u'IntIds')    

class IOtherResult(Interface):
    pass