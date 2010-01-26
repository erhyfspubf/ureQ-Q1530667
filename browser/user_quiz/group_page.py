# -*- coding: cp1251 -*-
from qreature.browser.user_quiz.interfaces import IGroupPageQuizForm,IMultiPageQuizUnit
from qreature.browser.user_quiz.widgets import install_widget_factories
from zope.interface import implements
from z3c.form import field
from qreature.interfaces import IQuizQuestion
from zope.component import getUtility
#from zope.app.intid.interfaces import IIntIds
from qreature.interfaces import IQreatureIntIds
from qreature.browser.user_quiz.interfaces import IQuizUnit
from zope.annotation.interfaces import IAnnotations
from qreature.browser.actions import PAGES_KEY
from zope.security.proxy import removeSecurityProxy
from zope.traversing.browser import absoluteURL
from qreature.browser.user_quiz.utilities import extract_answers,extract_previous_answers
from qreature.browser.user_quiz.user_quiz import UserQuiz

class GroupPageQuizForm(UserQuiz):
    implements(IGroupPageQuizForm)
    ignoreContext = True
        
    @property
    def fields(self):
        self.context = removeSecurityProxy(self.context)
        pages = IAnnotations(removeSecurityProxy(self.context)).get(PAGES_KEY)
        int_ids = getUtility(IQreatureIntIds, context = self.context)

        questions = [q for q in self.context.values() if IQuizQuestion.providedBy(q)]    
        questions.sort(key=lambda x: x.title)        
        questions = [int_ids.getId(question) for question in questions]
        
        if pages > len(questions):
            pages = len(questions)

        #how many pages?
        total_pages = divmod(len(questions),pages)
        if total_pages[1] != 0:
            total_pages =  total_pages[0]+ 1
        else:
            total_pages =  total_pages[0]
        
        #if it is not the first page
        if 'form.buttons.proceed' in self.request:
            answers = extract_answers(self.request)
            previous_answers = extract_previous_answers(self.request)
            #minus one because 1 answer is idle
            current_page = (len(answers) + len(previous_answers)) / pages
        #if it is first page
        else:
            answers = []
            current_page = 0
            
        #slice questions for this page only
        questions = questions[current_page*pages:(current_page+1)*pages]
        #check if it is last page
        if current_page + 1 == total_pages:
            self.gimmeAction = absoluteURL(self.context, self.request) + '/result.html'

            
                      
        #now i have questions for this page, and will use them for widget factory
        #i have also all received answers and will use em in widget factory 
        

        #Firstly, behavior looks like SinglePageQuiz:
        
        #Install fields for first question
        fields = field.Fields(IQuizUnit,prefix=str(questions[0]))
        questions = questions[1:]
        
        #append fields with another questions
        for question in questions:
            fields += field.Fields(IQuizUnit,prefix = str(question))
            
        #and now add previous answer field:
        fields += field.Fields(IMultiPageQuizUnit['previous_answers'])
        return install_widget_factories(fields, answers)
    
    def gimmeAction(self):
        """ called from template. this method is changed, when the last questions,
        to lead the user to result"""
        return self.request.URL
        
        
        