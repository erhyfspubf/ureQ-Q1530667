# -*- coding: cp1251 -*-

from zope.component import getAdapters,getMultiAdapter, getUtility
from qreature.interfaces import IAnswerDepends,IQuizResult
from qreature.skin.interfaces import ISlotLayer, IScaleLayer
from qreature.quiz import AnswerDepends
from z3c.form import field
from qreature.interfaces import IAnswerLeads
from qreature.quiz import AnswerLeads
from qreature.interfaces import IAnswerValue
from qreature.quiz import AnswerValue
from z3c.form.form import AddForm, EditForm
from zope.traversing.browser import absoluteURL
from zope.app.container.interfaces import INameChooser
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from z3c.form import button
from qreature.interfaces import IQuizAnswer,IQuiz
from qreature.quiz import QuizAnswer
from zope.interface import implements, Interface
from qreature.browser.qreature_views import QreatureAddForm,QreatureEditForm
from zope.contentprovider.interfaces import IContentProvider
from zope.security.proxy import removeSecurityProxy
from qreature.browser.qreature_views import QreatureEditableView,QreatureContentTitle,QreatureView,QreaturePicturedView
from qreature.browser.answer.interfaces import IRelationsForAnswer,ILeadForAnswer, IInlineAddForm,IInlineEditForm,IInlineForm
from zope.app.component.hooks import getSite
from qreature.browser.quiz_constructor.interfaces import ITexturedAnswersQuiz
from qreature.browser.qreature_views import QreaturePrefixedButton
from zope.event import notify
from qreature.browser.events import CachedObjectChangedEvent
from zope.lifecycleevent import ObjectCreatedEvent
#from zope.app.intid.interfaces import IIntIds
from qreature.interfaces import IQreatureIntIds
from pagable.interfaces import IPagableAction
from qreature.browser.answer.clone_select_widget import answerLeadWidgetFactory
from qreature.browser.quiz_constructor.interfaces import IQuestionsForConstructor
from zc.resourcelibrary import resourcelibrary
import re

def gimmeQuiz(context):
    while not IQuiz.providedBy(context):
        context = context.__parent__
    return context
    

class QuizAnswerAddForm(QreatureAddForm):
    
    fields = field.Fields(IQuizAnswer).omit('__parent__')
    form_name=u'Добавление ответа'
    button_name = u'Создать ответ'
    
    def create(self, data):
        return QuizAnswer(**data)
    def nextURL(self):
        url = super(QuizAnswerAddForm,self).nextURL()
        int_ids = getUtility(IQreatureIntIds)
        id = int_ids.getId(self.context.context)
        return url + u'#' + unicode(id)


class QuizAnswerEditForm(QreatureEditForm):
    fields = field.Fields(IQuizAnswer).omit('__parent__')
    form_name=u'Редактирование ответа'

    
class AnswerForConstructor(QreatureContentTitle ):
    """ """
    picture = "answer"
    css_class="answer"

class AnswerIdForConstructor(object):
    def render(self):
        int_ids = getUtility(IQreatureIntIds)
        id = int_ids.getId(self.context)
        return u'<a name="' + unicode(id) + u'"></a>'
      
class AnswerBodyForConstructor(QreaturePicturedView):
    render = ViewPageTemplateFile('templates/answer_body.pt')
    def __call__(self):
        self.update()
        return self.render()
    def gimmeId(self):
        return getUtility(IQreatureIntIds, context=self.context).getId(self.context)
    def update(self):
        quiz = getSite()
        if not ITexturedAnswersQuiz.providedBy(quiz):
            def nothing():
                return ''
            self.render = nothing
        else:
            resourcelibrary.need('mochikit.Base')
            resourcelibrary.need('mochikit.DOM')
            resourcelibrary.need('mochikit.Async')
            resourcelibrary.need('mochikit.JsonRpc')
            resourcelibrary.need('mochikit.Style')
            resourcelibrary.need('mochikit.Color')
            resourcelibrary.need('mochikit.Position')
            resourcelibrary.need('mochikit.Visual')
            resourcelibrary.need('answer')

    
class RelationsForAnswer(QreatureView,QreatureEditableView):
    
    render = ViewPageTemplateFile('./templates/relations_for_answer.pt')
    button_titles=False
    implements(IRelationsForAnswer)
    get_add = False
        
    def generateSequence(self,interface):
        return [relation for relation in self.context.values() if interface.providedBy(relation)]
        
    
    def generateRelations(self):
        if ISlotLayer.providedBy(self.request):
            return self.generateSequence(IAnswerDepends)
        elif IScaleLayer.providedBy(self.request):
            return self.generateSequence(IAnswerValue)
             
    def need_add(self,relations_length):
        if ISlotLayer.providedBy(self.request):
            quiz =getSite()
            results_length = len([result for result in quiz.values() if IQuizResult.providedBy(result)])
            if relations_length < results_length:
                return True
            return False
        else:
            if relations_length ==0:
                return True
            else:
                return False     
    def update(self):        
        relations = self.generateRelations()
        relations_length = len(relations)         
        
        #------------------------------------------
        self.viewlets = self.getEditForms(relations)
        if self.need_add(relations_length):
            self.viewlets.append(self.getAddForms())
        #---Handle, if some was added
        relations = self.generateRelations()        
        if len(relations) != relations_length:
            self.get_add = True
            self.update()
                     
    def getEditForms(self,relation_sequence):
        viewlet_sequence = []
        for relation in relation_sequence:
            rvm = getMultiAdapter((relation, self.request, self),IContentProvider, name=u'qreature.QreatureGeneralVM')
            rvm.update()
            viewlet_sequence.append(rvm)
        return viewlet_sequence
    
    def getAddForms(self):
        adding = getMultiAdapter((self.context, self.request, self),IContentProvider, name=u'qreature.QreatureGeneralVM')
        adding.update()
        adding.viewlets = [viewlet for viewlet in adding.viewlets if IInlineAddForm.providedBy(viewlet)]
        return adding
    
class LeadForAnswer(QreatureView,QreatureEditableView):
    
    render = ViewPageTemplateFile('./templates/lead_for_answer.pt')
    nothing = False
    button_titles=False
    something_happened_with_da_first = False
    first_widget = False
    implements(ILeadForAnswer)        
    
    def update(self):
        if removeSecurityProxy(self.context).has_key('lead'):
            #returns LeadEditForm
            lead = getMultiAdapter((self.context['lead'], self.request, self),IContentProvider, name=u'qreature.QreatureGeneralVM')
            lead.update()
            self.viewlets = [lead]
            #handle delete
            if not removeSecurityProxy(self.context).has_key('lead'):
                #self.cleanTermsStorage()
                if self.first_widget:
                    self.something_happened_with_da_first = True
                no_lead = getMultiAdapter((self.context, self.request, self),IContentProvider, name=u'qreature.QreatureGeneralVM')
                no_lead.update()
                no_lead.viewlets = [viewlet for viewlet in no_lead.viewlets if IInlineAddForm.providedBy(viewlet)]
                self.viewlets = [no_lead]
        else:
            no_lead = getMultiAdapter((self.context, self.request, self),IContentProvider, name=u'qreature.QreatureGeneralVM')
            no_lead.update()
            no_lead.viewlets = [viewlet for viewlet in no_lead.viewlets if IInlineAddForm.providedBy(viewlet)]
            self.viewlets = [no_lead]
            #handle add
            if removeSecurityProxy(self.context).has_key('lead'):
                #self.cleanTermsStorage()
                if self.first_widget:
                    self.something_happened_with_da_first = True
                lead = getMultiAdapter((self.context['lead'], self.request, self),IContentProvider, name=u'qreature.QreatureGeneralVM')
                lead.update()
                self.viewlets = [lead]
    
    def cleanTermsStorage(self):
        parent_viewlet = self
        while not IQuestionsForConstructor.providedBy(parent_viewlet):
            parent_viewlet = parent_viewlet.__parent__
        parent_viewlet.terms = None



def cleanResultIfDependsChange(depend):
    int_ids = getUtility(IQreatureIntIds, context=depend)
    result = int_ids.getObject(int(depend.result_id))
    notify(CachedObjectChangedEvent([result]))
    


class InlineForm(object):
    implements(IInlineForm, IPagableAction)
    template = ViewPageTemplateFile('./templates/inline_form.pt')
    def gimmeAction(self):
        r = re.compile(u'http://.*\+\+skin\+\+Qreature/qreature')
        url = r.sub(u'http://www.qreature.ru',unicode(self.request.URL))
        int_ids = getUtility(IQreatureIntIds)
        answer = self.context
        while not IQuizAnswer.providedBy(answer):
            answer = answer.__parent__
                
        answer_id = int_ids.getId(answer)
        return u'#'.join((url,unicode(answer_id)))


class InlineAddForm(InlineForm,QreaturePrefixedButton,AddForm):
    
    implements(IInlineAddForm)
    def __init__(self, context,request,view,manager):
        self.context = context
        self.request = request
        self.__parent__ = view
        self.manager = manager
    
    buttons = button.Buttons(button.ImageButton (name='add',title=u'Add',image=u'add.jpg'))
    
    
    @button.handler(buttons['add'])
    def handleAdd(self, action):
        #handle case for adding multiple depends. If one is added, no need to add it again
        if IRelationsForAnswer.providedBy(self.__parent__) and self.__parent__.get_add: return
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        obj = self.createAndAdd(data)
        if obj is not None:
            ob = self.context[self.obj_name]
            notify(CachedObjectChangedEvent([ob]))
            if IAnswerDepends.providedBy(ob):
                cleanResultIfDependsChange(ob)
            
    def update(self):
        super(InlineAddForm,self).update()
    
    def createAndAdd(self, data):
        obj = self.create(data)
        notify(ObjectCreatedEvent(obj))
        self.add(obj)
        return obj
    
    def add(self,object):
        chooser = INameChooser(self.context)
        self.obj_name = chooser.chooseName(None, object)
        if chooser.checkName(self.obj_name, object):
            self.context[self.obj_name] = object

    def nextURL(self):
        return self.request.URL

    
    def gimmeTip(self):
        raise NotImplementedError
            
from qreature.browser.actions import deleteButtonActionFactory

class InlineEditForm(InlineForm,QreaturePrefixedButton,EditForm):
    
    def __init__(self, context,request,view,manager):
        self.context = context
        self.request = request
        self.__parent__ = view
        self.manager = manager
    
    def update(self):
        self.buttons['delete'].actionFactory = deleteButtonActionFactory
        super(InlineEditForm,self).update()

    buttons = button.Buttons(button.ImageButton
                         (name='apply',title=u'Apply',image=u'apply.jpg')) + \
              button.Buttons(button.ImageButton
                         (name='delete',title=u'Delete',image=u'delete.jpg'))               
    
    @button.handler(buttons['apply'])
    def handleApply(self, action):
        super(InlineEditForm,self).handleApply(self,action)
        #clean viewlet first
        notify(CachedObjectChangedEvent([self.context]))
        ob = self.context
        if IAnswerDepends.providedBy(ob):
                cleanResultIfDependsChange(ob)
            
    @button.handler(buttons['delete'])
    def handleDelete(self, action):
        #clean viewlet first
        notify(CachedObjectChangedEvent([self.context]))
        ob = self.context
        if IAnswerDepends.providedBy(ob):
                cleanResultIfDependsChange(ob)
        #then delete
        parent = self.context.__parent__
        parent.__delitem__(self.context.__name__)





class AnswerDependsAddForm(InlineAddForm,QreaturePicturedView):
    fields = field.Fields(IAnswerDepends).omit('__parent__', '__name__')
    def create(self, data):
        return AnswerDepends(**data)
    @property
    def picture(self):
        return self.gimmePicturesUrls()['depends']
    
    def gimmeTip(self):
        return u'Добавляйте влияния:'
    @property
    def prefix(self):
        prefix = super(AnswerDependsAddForm,self).prefix
        return prefix + '.depend'

    
class AnswerDependsEditForm(InlineEditForm,QreaturePicturedView):
    fields = field.Fields(IAnswerDepends).omit('__parent__', '__name__')
    @property
    def picture(self):
        return self.gimmePicturesUrls()['depends']
    def gimmeTip(self):
        return u'Влияет:'
    @property
    def prefix(self):
        prefix = super(AnswerDependsEditForm,self).prefix
        return prefix + '.depend'


class AnswerValueAddForm(InlineAddForm,QreaturePicturedView):
    header = u'You can grant some points to user chosen wich answer'
    fields = field.Fields(IAnswerValue).omit('__parent__', '__name__')

    def create(self, data):
        return AnswerValue(**data)
    @property
    def picture(self):
        return self.gimmePicturesUrls()['value']
    
    def gimmeTip(self):
        return u'Добавляйте баллы:'
    @property
    def prefix(self):
        prefix = super(AnswerValueAddForm,self).prefix
        return prefix + '.value'
    

class AnswerValueEditForm(InlineEditForm,QreaturePicturedView):
    header = u'This answer will give the user points listed below:'
    fields = field.Fields(IAnswerValue).omit('__parent__', '__name__')
    @property
    def picture(self):
        return self.gimmePicturesUrls()['value']
    
    def gimmeTip(self):
        return u'Баллы этого ответа:'
    @property
    def prefix(self):
        prefix = super(AnswerValueEditForm,self).prefix
        return prefix + '.value'



class AnswerLeadsAddForm(InlineAddForm,QreaturePicturedView):
    
    _fields = field.Fields(IAnswerLeads).omit('__parent__', '__name__')
    
    def get_fields(self):
        self._fields['question_id'].widgetFactory = answerLeadWidgetFactory(self)
        return self._fields
    def set_fields(self,value):
        self._fields = value
    
    fields = property(get_fields,set_fields)
    
    def create(self, data):
        return AnswerLeads(**data)
    @property
    def picture(self):
        return self.gimmePicturesUrls()['lead']
    def gimmeTip(self):
        return u'Можно добавить перемещение:'
    @property
    def prefix(self):
        prefix = super(AnswerLeadsAddForm,self).prefix
        return prefix + '.lead'

    

class AnswerLeadsEditForm(InlineEditForm,QreaturePicturedView):
    header = u'This answer will lead the user, to the question listed below'
    
    _fields = field.Fields(IAnswerLeads).omit('__parent__', '__name__')
    
    def get_fields(self):
        self._fields['question_id'].widgetFactory = answerLeadWidgetFactory(self)
        return self._fields
    def set_fields(self,value):
        self._fields = value
    
    fields = property(get_fields,set_fields)
    
    @property
    def picture(self):
        return self.gimmePicturesUrls()['lead']
    def gimmeTip(self):
        return u'Перемещает:'
    @property
    def prefix(self):
        prefix = super(AnswerLeadsEditForm,self).prefix
        return prefix + '.lead'