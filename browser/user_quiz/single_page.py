# -*- coding: cp1251 -*-

from z3c.form import field
from qreature.browser.user_quiz.interfaces import IQuizUnit,ISinglePageQuizForm
from qreature.interfaces import IQuizQuestion
from zope.component import getUtility
#from zope.app.intid.interfaces import IIntIds
from qreature.interfaces import IQreatureIntIds
from zope.traversing.browser.absoluteurl import absoluteURL
from zope.interface import implements
from qreature.browser.user_quiz.widgets import install_widget_factories
from qreature.browser.user_quiz.user_quiz import UserQuiz

class SinglePageQuizForm(UserQuiz):
    """ Form for the singlepage quiz. Has no content. Creates as plenty widgets,
    as many questions contained by quiz. Bind separate widget factory, for each widget."""
    implements(ISinglePageQuizForm)
    ignoreContext = True
    @property
    def fields(self):
        questions = []
        for q in self.context.values():
            if IQuizQuestion.providedBy(q):
                questions.append(q)
        questions.sort(key=lambda x: x.title)
        
        int_ids = getUtility(IQreatureIntIds, context = self.context)
        
        #Install fields for first question
        fields = field.Fields(IQuizUnit,prefix=str(int_ids.getId(questions[0])))
        questions = questions[1:]
        
        #append fields with another questions
        for question in questions:
            fields += field.Fields(IQuizUnit,prefix = str(int_ids.getId(question)))
        
        #assign widget factory for each field
        return install_widget_factories(fields,[])
    
    def gimmeAction(self):
        return absoluteURL(self.context, self.request) + '/result.html'