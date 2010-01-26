# -*- coding: cp1251 -*-
from z3c.form import button, form
from qreature.interfaces import  IScaleQuiz, ISlotQuiz
from zope.component import getUtility,adapter
from zope.interface import alsoProvides, noLongerProvides
from zope.security.proxy import removeSecurityProxy
from zope.traversing.browser.absoluteurl import absoluteURL
from zope.app.pagetemplate import ViewPageTemplateFile
from qreature.interfaces import IQuizAnswer, IQuizContainer, IAnswerLeads, IAnswerValue,IQuizResult, IQuizQuestion,IAnswerDepends
from qreature.browser.user_quiz.interfaces import ISinglePage, IMultiPage,IGroupPage, IPublished
#from zope.app.intid.interfaces import IIntIds
from qreature.interfaces import IQreatureIntIds
from qreature.interfaces import ILeadedQuiz
from zope.event import notify
from qreature.interfaces import IQuiz
from zope.app.container.interfaces import IContainerModifiedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from zope.annotation.interfaces import IAnnotations
from BTrees.IOBTree import IOBTree
from qreature.interfaces import IQreatureUtility
from qreature.browser.qreature_views import QreaturePrefixedButton
from qreature.browser.events import CachedObjectChangedEvent,CleanCacheEvent
from qreature.browser.result.result_interval import INTERVAL_KEY
from pagable.interfaces import IPagableAction
from zope.interface import implements

class DeleteButton(QreaturePrefixedButton,form.Form):
    template = ViewPageTemplateFile('templates/one_button_form.pt')
    implements(IPagableAction)
    def __init__(self, context, request, view, manager):
        self.context = context
        self.request = request
        self.__parent__= view
        self.manager = manager
        
    def update(self):
        self.buttons['delete'].actionFactory = deleteButtonActionFactory
        super(DeleteButton,self).update()
        
    buttons = button.Buttons(button.ImageButton
                         (name='delete',title=u'Delete',image=u'delete.jpg'))               

            
    @button.handler(buttons['delete'])
    def handleDelete(self, action):
        parent = self.context.__parent__
        #if the Quiz is deleted: invalidate all
        if IQuiz.providedBy(self.context):
            notify(CleanCacheEvent(self.context))
            parent.__delitem__(self.context.__name__)
            return self.request.response.redirect(self.request.URL)
        notify(CachedObjectChangedEvent([self.context]))
        parent.__delitem__(self.context.__name__)
        
def deleteButtonActionFactory (request, imgSubmit):
    action = button.ImageButtonAction(request, imgSubmit)
    message = u'Удаляем?'
    action.onclick = u"return confirm('" + message + "')"
    return action




    

PAGES_KEY = 'pages'

class QuizAction(object):
    implements(IPagableAction)
    button_title = u''
    template = ViewPageTemplateFile('templates/one_button_form.pt')
    def __init__(self, context,request,view,manager):
        self.context = removeSecurityProxy(context)
        self.request = request
        self.__parent__ = view
        self.manager = manager
    
    def swapInterface(self,i):
        quiz = removeSecurityProxy(self.context)
        if i.providedBy(quiz): noLongerProvides(quiz, i)
        else: alsoProvides(quiz, i)

    @property
    def site_url(self):
        return absoluteURL(self.context,self.request) + '/main.html'


class CheckButton(QuizAction,QreaturePrefixedButton,form.Form):  
    """ """
    
    
    buttons = button.Buttons(button.ImageButton
                             (name='check',title=u'Check',image=u'check.jpg'))
    
    
    @button.handler(buttons['check'])
    def check(self,action):
        checker = QuizChecker(self.context,self.request)
        response = checker.check()
        if response is None:
            self.status = checker.status


class QuizChecker(object):
    
    def __init__(self,context,request):
        self.context = context
        self.request = request
    
    
    def check(self):
        """ """
        self.context = removeSecurityProxy(self.context)
        
        flatten = getUtility(IQreatureUtility,name="Flatten")
        DEFINING_INTERFACES = [IScaleQuiz,ISlotQuiz,ILeadedQuiz,IScaleQuiz]
        DEFINING_CONTENT = ['values','depends','leads','intervals']
        CONTENT = ['results','questions','answers'] + DEFINING_CONTENT
        MESSAGES = [u'результатов',u'вопросов',u'ответов',u'баллов' ,u'влияний', u'перемещений',u'интервалов']
        
        KEY_MESSAGES = dict(zip(CONTENT,MESSAGES))

        results = [result for result in self.context.values() if IQuizResult.providedBy(result)]
        intervals = [IAnnotations(removeSecurityProxy(result)).get(INTERVAL_KEY)
                      for result in results]
        intervals = [interval for interval in intervals if interval is not None]
        questions = [question for question in self.context.values() if IQuizQuestion.providedBy(question)]
        
        def extract_nested_objects(parents,interface):
            objects = [[object for object in parent.values() if interface.providedBy(object)] \
                   for parent in parents]
            objects = [ob for ob in flatten(objects)]
            return objects
        
        answers = extract_nested_objects(questions, IQuizAnswer)
        leads = extract_nested_objects(answers, IAnswerLeads)
        depends = extract_nested_objects(answers, IAnswerDepends)
        values = extract_nested_objects(answers, IAnswerValue)
        
        KEY_ITEMS = dict(zip(CONTENT,[results,questions,answers,values,depends,leads,intervals]))
        
        DEFINING_KEYS_INTERFACES = dict(zip(DEFINING_CONTENT,DEFINING_INTERFACES))
        
        
        def clean_unneded(interface,key):
            if not interface.providedBy(self.context):
                KEY_ITEMS.pop(key)
                KEY_MESSAGES.pop(key)
                
        for key,interface in DEFINING_KEYS_INTERFACES.items():
            clean_unneded(interface,key)
            

        #check if we have all in place: all res, ques, ans etc
        if self.check_content(KEY_ITEMS, KEY_MESSAGES): return
        
        
        if 'leads' in KEY_ITEMS.keys() and self.check_leads(KEY_ITEMS): return
        
        #if i am here: all checks are performed. if any checks is fail:
           
        # --------- MultiPage for Leaded Quiz ------------------------------------
        if ILeadedQuiz.providedBy(self.context):
            unpublish(self.context,has_mistakes=False)
            alsoProvides(self.context,IMultiPage)
            return self.request.response.redirect(self.request.URL)
        
        # --------- SinglePage for  Quiz with small questions number ------------
        pages = IAnnotations(removeSecurityProxy(self.context)).get(PAGES_KEY)
        if pages is None:
            pages = len(KEY_ITEMS['questions'])
        if len(KEY_ITEMS['questions']) <= pages:
            unpublish(self.context,has_mistakes=False)
            alsoProvides(self.context,ISinglePage)
            return self.request.response.redirect(self.request.URL)
        # --------- GroupPage for  Quiz with large questions number ------------
        else:
            unpublish(self.context,has_mistakes=False)
            alsoProvides(self.context,IGroupPage)
            return self.request.response.redirect(self.request.URL)
                
    
    def error(self,message):
        unpublish(self.context)
        self.status = message
        return True
        
    
    def content_error(self, message):
        unpublish(self.context)
        message = u"<div><b>Ошибка!</b></div><div>Не хватает " + message + u"</div>"
        self.status = message
        return True
    
    def check_content(self, KEY_ITEMS, KEY_MESSAGES):
        # check for presence of all elements: results,answers,questions
        for key,item in KEY_ITEMS.items():
            # check for presence
            if len(item) ==0:
                return self.content_error(KEY_MESSAGES[key])
        
        # each question must have answers:
        questions = KEY_ITEMS.get('questions')
        for q in questions:
            if len(q.values()) == 0:
                return self.content_error(KEY_MESSAGES['answers'])
        #check Scale schema
        values = KEY_ITEMS.get('values')
        if values is not None:
            #each answer must have value!
            if len(KEY_ITEMS['answers']) != len(values):
                return self.content_error(KEY_MESSAGES['values'])
            if len(KEY_ITEMS['results']) != len(KEY_ITEMS['intervals']):
                return self.content_error(KEY_MESSAGES['intervals'])
                    

       
    def check_leads(self, key_items):

        int_ids = getUtility(IQreatureIntIds, context = self.context)
        
        leads = key_items['leads']
        questions = key_items['questions']
        
        if len(leads) == 0: 
            message = u"<div><b>Ошибка!</b></div><div>Не созданы перемещения!</div>\
            <div>Если вы не хотите делать тест с перемещениями - отключите их кнопкой сверху.</div>"
            return self.error(message)
        
        leads_map = {}
        for l in leads:
            leads_map[l] = l.question_id

        question_map = {}
        for q in questions:
            question_map[int_ids.getId(q)] = q 
        
        start_question = []
        for question in questions:
            q = int_ids.getId(question)
            if not q in leads_map.values():
                start_question.append(q)
        
        if len(start_question)>1:
            message = u"<div><b>Ошибка!</b></div><div>Несколько вопросов не указано в перемещениях</div>\
            <div>Должен быть только один вопрос не указанный в перемещениях. Это тот вопрос, который станет первым</div>"
            message += u'<div><b>Следующие вопросы не указаны в перемещениях:</b></div>'
            for q in start_question:
                message += u'<div>' + question_map[q].title + u'</div>'
            return self.error(message)
        
        
        if len(start_question) ==0:
            message = u"<div><b>Ошибка!</b></div><div>Один вопрос не должен быть указан в перемещении.</div>\
            <div> Этот вопрос будет первым.</div>"
            return self.error(message)
         
        
        real_start_question = int_ids.getObject(start_question[0])        
        
        
        last_questions = question_map.values()
           
        for l in leads_map.keys():
            q = l.__parent__.__parent__
            if q in last_questions:
                last_questions.remove(q)
        
        #now, we have only last questions (which lead to result, in lead questions)
        #REMEMBER, they are not ids!  they are objects
        if len(last_questions) == 0:
            message =u"<div><b>Ошибка!</b></div><div>Тупик в перемещениях</div>"
            return self.error(message)
        
        #so. it need to proove the 3 things:
        #1)each question,  except start and last has a lead IN IT
        #2)each question,  except start and last has a lead ON IT (It looks like this unneded because thi allready excepts by start_question check)
        #3)there are no loops Qi->Qg->Qi.
        
        
        def not_in_last_not_in_start(q):
            if (not q in last_questions) and (not q == real_start_question):
                return True
            else: return False
        
        #1.
        for q in question_map.values():
            if not_in_last_not_in_start(q):
                for a in q.values():
                    if IQuizAnswer.providedBy(a):
                        if not a.has_key('lead'):
                            err = u'<div><b>Ошибка!</b></div><div>Ответ ' + unicode(a.title) + u' должен содержать перемещение</div>'
                            message = err
                            return self.error(message)

        #3.
        for lead,target_question_id  in leads_map.items():
            
            target_question = question_map[target_question_id]
            question = lead.__parent__.__parent__
            for i,v in question_map.items():
                if question == v: question_id = i
            #now i have question, quiestion_id and target_question, target_question_id,
            #changing in outer cycle. It looks like flying in one direction:
            # q,q_id --> t,t_id
            #start one more cycle. Fly throug all leads, and check another direction:
            #q, q_id  <-- t, t_id
            for lead,lead_id in leads_map.items():
                if lead.__parent__.__parent__ == target_question \
                and lead_id == question_id:
                    #this condition equals to True means i have a closure.
                    #it only need to check is it any way to exit this closure.
                    #the exit is possible if question or target_question
                    #has inside of their answers other leads!
                    other_leads_in_parent = [[l for l in answer.values() if IAnswerLeads.providedBy(l)]\
                                             for answer in question.values() if IQuizAnswer.providedBy(answer)]
                    other_leads_in_target = [[l for l in answer.values() if IAnswerLeads.providedBy(l)]\
                                             for answer in target_question.values() if IQuizAnswer.providedBy(answer)]
                    print "---------------------------"
                    print len(other_leads_in_parent)
                    print len(other_leads_in_target)
                    if (len(other_leads_in_parent) > 1) or (len(other_leads_in_target) >1):continue 
                    if target_question == question:
                        err = u'<div><b>Ошибка!</b></div><div>Вопрос ' + unicode(question.title) + \
                            u' перемещает сам на себя </div>'
                    else:
                        err = u'<div><b>Ошибка!</b></div><div>Вопрос ' + unicode(question.title) + u' и вопрос ' + \
                            unicode(target_question.title) + u' перемещают друг на друга </div>'
                    message = err
                    return self.error(message)
        
        #Some more things to check:
        
        l_q = []
        for key,value in question_map.items():
            if value in last_questions:
                l_q.append(key)  
                    
        #install graf
        
        annotations = IAnnotations(removeSecurityProxy(self.context))
        graf = annotations.get(key=GRAF_KEY, default=False)
        if graf:
            for key,value in graf.items():
                if value == FIRST_QUESTION_KEY:
                    graf.__delitem__(key)
                if value == LAST_QUESTION_KEY:
                    graf.__delitem__(key)
        else:
            graf = IOBTree()
        
        graf[start_question[0]] = FIRST_QUESTION_KEY
        for q in l_q:
            graf[q] = LAST_QUESTION_KEY
        annotations[GRAF_KEY] = graf
        
        return False
        
    
FIRST_QUESTION_KEY = 'first'
LAST_QUESTION_KEY = 'last'    
IDLE_ANSWER_KEY = 'idle_answer'
GRAF_KEY = 'graf'

def unpublish(ob,has_mistakes=True):
    """ clean all interfaces fro quiz. if has mistakes"""
    quiz = ob
    while not IQuiz.providedBy(quiz):
        quiz = quiz.__parent__
    quiz = removeSecurityProxy(quiz)
    noLongerProvides(quiz,ISinglePage)
    noLongerProvides(quiz,IMultiPage)
    noLongerProvides(quiz,IGroupPage)
    if has_mistakes:
        noLongerProvides(quiz,IPublished)
    
    
    
@adapter(IQuizContainer, IContainerModifiedEvent)
def unpublishCauseChildren(ob,event):
    unpublish(ob)
    
       
@adapter(IQuizContainer,IObjectModifiedEvent)
def unpublishCauseAttribute(ob,event):
    unpublish(ob)
    
@adapter(IAnswerLeads,IObjectModifiedEvent)
def unpublishCauseLead(ob,event):
    unpublish(ob)
    

class PublishButton(QuizAction,QreaturePrefixedButton,form.Form):  
    """ """
    buttons = button.Buttons(button.ImageButton
                             (name='publish',title=u'Publish',image=u'publish.jpg'))
    
    @button.handler(buttons['publish'])
    def publish(self, action):
        self.swapInterface(IPublished)
        if IPublished.providedBy(self.context):
            status = u'Доступ к тесту открыт'
        else:
            return self.request.response.redirect(self.request.URL)
        self.status = status
        notify(CleanCacheEvent(self.context))
