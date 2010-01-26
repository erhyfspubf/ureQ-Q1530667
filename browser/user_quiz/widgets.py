# -*- coding: cp1251 -*-
from zope.component import getMultiAdapter, getUtility, adapter, adapts
from z3c.form.browser.radio import RadioWidget
from z3c.form import interfaces, widget
from zope.app.component.hooks import getSite
from zope.schema.vocabulary import SimpleVocabulary
#from zope.app.intid.interfaces import IIntIds
from qreature.interfaces import IQreatureIntIds
from qreature.browser.user_quiz.interfaces import IQuestionBody,IAnswerWidget,\
    IAnswerChoice, IPreviousAnswersChoice,IPreviousAnswersWidget,IQuestionWidget
from qreature.skin.interfaces import IQreatureSkin, IPaidSkin
from z3c.form.browser.text import TextWidget
from zope.interface import implements
from z3c.form.browser.checkbox import CheckBoxWidget
from qreature.interfaces import IQuizAnswer
from z3c.form.interfaces import IFieldWidget
from qreature.browser.user_quiz.utilities import extract_previous_answers#,install_idle_answer
from qreature.browser.user_quiz.interfaces import IMultiPageQuizUnit


class AnswerWidget(RadioWidget):
    """ This is a Choice widget constructed from the answer dictionary,
    but with the answer removed, which are not childrens of the current questions."""
    implements(IAnswerWidget)
    def updateTerms(self):
        if self.terms is None:
            self.terms = getMultiAdapter(
                (self.context, self.request, self.form, self.field, self),
                interfaces.ITerms)
        #I need only answers inside current question
        required_terms = []
        int_ids = getUtility(IQreatureIntIds, context=getSite())
        for term in self.terms:
            if term.value.__parent__ == int_ids.getObject(int(self.prefix)):
                required_terms.append(term)
        required_terms.sort(key= lambda x: x.value.title)
        self.terms = SimpleVocabulary(required_terms)
        return self.terms
    
class QuestionWidget(TextWidget):
    """ empty for now"""
    implements(IQuestionWidget)
    

class PreviousAnswersWidget(CheckBoxWidget):
    """ Hidden checkbox widget, containing previous answers of user, passing the quiz"""
    implements(IPreviousAnswersWidget)




@adapter(IQuestionBody,IQreatureSkin)
def questionWidget(field, request):
    """ makes the widget FieldsWidget"""
    return widget.FieldWidget(field,QuestionWidget(request))  




@adapter(IAnswerChoice,IQreatureSkin)
def answerWidget(field, request):
    """ makes the widget FieldsWidget"""
    return widget.FieldWidget(field,AnswerWidget(request))  

    
@adapter(IPreviousAnswersChoice,IQreatureSkin)
def previousAnswersWidget(field, request):
        """ makes the widget FieldsWidget"""
        #field.mode = interfaces.HIDDEN_MODE
        return widget.FieldWidget(field,PreviousAnswersWidget(request)) 




@adapter(IQuestionBody,IPaidSkin)
def paidQuestionWidget(field, request):
    """ makes the widget FieldsWidget"""
    return widget.FieldWidget(field,QuestionWidget(request))  




@adapter(IAnswerChoice,IPaidSkin)
def paidAnswerWidget(field, request):
    """ makes the widget FieldsWidget"""
    return widget.FieldWidget(field,AnswerWidget(request))  

    
@adapter(IPreviousAnswersChoice,IPaidSkin)
def paidPreviousAnswersWidget(field, request):
        """ makes the widget FieldsWidget"""
        #field.mode = interfaces.HIDDEN_MODE
        return widget.FieldWidget(field,PreviousAnswersWidget(request)) 


class QuizWidgetFactory(object):
    """ base class for singlepage quiz widgets. obtain the value of the widget
    by reading appropriate z3c.form Field prefix. The prefix is installed by the form"""
    def __init__(self, prefix):
        self.prefix = prefix
        site = getSite()
        self.int_ids = getUtility(IQreatureIntIds, context=site)
        self.question = self.int_ids.getObject(int(prefix))
        
    def getValue(self):
        """ virtual"""
        raise NotImplementedError

    def installValue(self, field, request):
        self.widget = getMultiAdapter((field, request), IFieldWidget)
        self.widget.prefix = self.prefix
        value = self.getValue()
        def gimmeValue():
            return value
        self.widget.extract = gimmeValue
        
    def gimmeWidget(self, field, request):
        self.installValue(field,request)
        return self.widget



class QuizAnswerWidgetFactory(QuizWidgetFactory):
    """ first answer in question"""
    def getValue(self):
        answers = []
        for a in self.question.values():
            if IQuizAnswer.providedBy(a):
                answers.append(a)
        answers.sort(key=lambda x: x.title)
        answers.reverse()
        init_answer = answers.pop()
        #return [init_answer]
        return [str(self.int_ids.getId(init_answer))]

class QuizQuestionWidgetFactory(QuizWidgetFactory):
    """ id for answer"""
    def getValue(self):
        return self.question.body



class QuizPreviousAnswerWidgetFactory(object):
    
    def __init__(self, received_answers):
        #i get here idle answer, if it is first page
        #or received answer if it is not
        #or received answers if it is GroupPage
        self.received_answers = received_answers

    def gimmeWidget(self,field, request):
        widget = getMultiAdapter((field, request), IFieldWidget)
        previous_answers = extract_previous_answers(request)     
        previous_answers += self.received_answers
        def gimmeValue():
            return previous_answers
        widget.extract = gimmeValue
        return widget
    
    
def install_widget_factories(fields, answers):
    for f in fields.values():
            if f.field == IMultiPageQuizUnit['answer']:
                factory = QuizAnswerWidgetFactory(f.prefix)
                f.widgetFactory = factory.gimmeWidget
            if f.field == IMultiPageQuizUnit['question']:
                factory = QuizQuestionWidgetFactory(f.prefix)
                f.widgetFactory = factory.gimmeWidget
            if f.field == IMultiPageQuizUnit['previous_answers']:
                factory = QuizPreviousAnswerWidgetFactory(answers)
                f.widgetFactory = factory.gimmeWidget
    return fields