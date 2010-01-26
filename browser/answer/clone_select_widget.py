from zope.component import getMultiAdapter, adapts
from z3c.form.browser.select import SelectWidget
from z3c.form.widget import FieldWidget
from qreature.browser.quiz_constructor.interfaces import IQuestionsForConstructor
from zope.interface import implements
from qreature.browser.answer.interfaces import IAnswerLeadWidget, ILeadForAnswer

class AnswerLeadWidget(SelectWidget):
    implements(IAnswerLeadWidget)
    terms_storage = None
    your_holder = None
    i_am_first_widget = False
    klass = 'answer_lead'
    
    def updateTerms(self):
        #if terms not yet stored: catch them and store
        terms = getattr(self.terms_storage, 'terms',None)
        if terms is None or self.your_holder.something_happened_with_da_first:
            #calling 'super' also means that self.terms will be install from dynamic dictionary
            self.terms_storage.terms = super(AnswerLeadWidget,self).updateTerms()
            self.i_am_first_widget = True
            self.your_holder.first_widget = True
        else:
            #do not look up for dynamic dict. just take the terms from terms_storage
            self.terms = terms
        return self.terms
    
    def update(self):
        """See z3c.form.interfaces.IWidget."""
        
        #update terms
        super(SelectWidget, self).update()
        self.items = []
        
        if (not self.required or self.prompt) and self.multiple is None:
            message = self.noValueMessage
            if self.prompt:
                message = self.promptMessage
            self.items.append({
                'id': self.id + '-novalue',
                'value': self.noValueToken,
                'content': message,
                'selected': self.value == []
                })
        
        for count, term in enumerate(self.terms):
            selected = self.isSelected(term)
            if selected or self.i_am_first_widget:
                id = '%s-%i' % (self.id, count)
                content = term.title
                self.items.append(
                    {'id':id, 'value':term.token, 'content':content,
                     'selected':selected})

def answerLeadWidgetFactory(viewlet):
    #so. the idea is to update terms for answer widget only once.
    #may be, when i construct the first widget i can store _terms in 
    #above (higher level) viewlets
    #the common viewlet for all leads is QuestionsForConstructor
    while not IQuestionsForConstructor.providedBy(viewlet):
        if ILeadForAnswer.providedBy(viewlet):
            holder = viewlet
        viewlet = viewlet.__parent__
    def factory(field,request):
        answer_lead_widget = AnswerLeadWidget(request)
        #I just add the QuestionsForConstructor to each widget
        answer_lead_widget.terms_storage = viewlet
        answer_lead_widget.your_holder = holder
        return FieldWidget(field, answer_lead_widget)
    return factory
        