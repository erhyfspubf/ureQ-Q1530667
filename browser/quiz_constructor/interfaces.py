# -*- coding: cp1251 -*-

from zope.interface import Interface, Attribute, implements
from zope.schema import Int,Bool
    

class IFirstTimeHelped(Interface):
    help = Bool(title=u'is it needx to show help or not')

        
class IResultsForConstructor(Interface):
    rows = Attribute(u'How many rows the results table will contains')
    list_results = Attribute(u'The List of results, for ResultIntervalForms')
    
class IQuestionsForConstructor(Interface):
    terms = Attribute(u'Term storage for CloneSelectWidget')
    question_was_removed = Bool(title = u'May be question was deleted')
class IPages(Interface):
    pass

class Pages(Int):
    implements(IPages)

class IQuizPages(Interface):
    """ """
    pages = Pages(title=u'Вопросов на странице:')
    
class ITexturedQuestionsQuiz(Interface):
    """ Constructor view, for the quiz providing this interface will render the text of the questions"""
class ITexturedAnswersQuiz(Interface):
    """ Constructor view, for the quiz providing this interface will render the text of the answers"""
class IQuizConstructor(Interface):
    """ """
    
class IAsyncDataManager(Interface):
    """ """
    def applyChanges(value):
        pass
    
    
class IQuizAsXMLView(Interface):
    pass