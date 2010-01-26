# -*- coding: cp1251 -*-
from z3c.form import field
from zope.interface import implements
from qreature.browser.user_quiz.interfaces import IMultiPageQuizForm,IMultiPageQuizUnit
from zope.component import getUtility
#from zope.app.intid.interfaces import IIntIds
from qreature.interfaces import IQreatureIntIds
from zope.traversing.browser.absoluteurl import absoluteURL
from zope.annotation.interfaces import IAnnotations
from zope.security.proxy import removeSecurityProxy
from qreature.browser.actions import FIRST_QUESTION_KEY, LAST_QUESTION_KEY,GRAF_KEY
from qreature.browser.user_quiz.widgets import install_widget_factories
from qreature.browser.user_quiz.utilities import extract_answers
from qreature.browser.user_quiz.user_quiz import UserQuiz

class MultiPageQuizForm(UserQuiz):
    """ If quiz questions have any leads - the quiz is multipage"""
    implements(IMultiPageQuizForm)
    ignoreContext = True
    @property
    def fields(self):
        self.context = removeSecurityProxy(self.context)
        int_ids = getUtility(IQreatureIntIds, context = self.context)
        annotations = IAnnotations(removeSecurityProxy(self.context))
        graf = annotations.get(GRAF_KEY)
        
        #this means it is not first question
        if 'form.buttons.proceed' in self.request:
            answers = extract_answers(self.request)
            #actually it is only one answer
            received_answer = int_ids.getObject(int(answers[0]))
            question_id = received_answer['lead'].question_id
            
            if question_id in graf.keys()and graf[question_id] == LAST_QUESTION_KEY:
                self.gimmeAction = absoluteURL(self.context, self.request) + '/result.html'
                     
        #first question
        else:
            for i in graf.items():
                if i[1] == FIRST_QUESTION_KEY:
                    question_id = i[0]
            #it need to install idle answer
            answers = []
                    
        fields = field.Fields(IMultiPageQuizUnit, prefix = str(question_id))
        return install_widget_factories(fields, answers)
                
    
    def gimmeAction(self):
        """ called from template. this method is changed, when the last questions,
        to lead the user to result"""
        return self.request.URL
