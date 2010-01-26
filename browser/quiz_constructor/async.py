from zif.jsonserver import MethodPublisher
from qreature.interfaces import IAnswerLeads, IAnswerDepends, IAnswerValue, IQreatureUtility, IQuizResult,IQreatureIntIds
from zope.component import adapts, getUtility,getMultiAdapter
from zope.security.proxy import removeSecurityProxy
from qreature.browser.quiz_constructor.interfaces import IAsyncDataManager
from zope.interface import implements, alsoProvides, Interface
from qreature.browser.events import CachedObjectChangedEvent
from zope.event import notify
from qreature.skin.interfaces import IQreatureSkin,ILeadedLayer,IScaleLayer,ISlotLayer
from zope.publisher.browser import TestRequest
from qreature.browser.interfaces import IQreatureGeneralVM
from qreature.browser.answer.interfaces import ILeadForAnswer,IRelationsForAnswer
from qreature.browser.quiz_constructor.interfaces import IQuestionsForConstructor
from zope.app.component.hooks import getSite
from zope.traversing.browser import absoluteURL
from qreature.quiz import AnswerLeads, AnswerDepends, AnswerValue
from zope.component import createObject,queryUtility
from zope.app.container.interfaces import INameChooser
from zope.lifecycleevent import ObjectCreatedEvent
import re

class AsyncDataManager(object):
    implements(IAsyncDataManager)
    def __init__(self,ob):
        self.ob = ob
    def applyChanges(self,value):
        raise NotImplementedError
    def deleteSelf(self):
        raise NotImplementedError
    def addSelf(self):
        raise NotImplementedError
    def generateHTTPrequest(self,layer):
        localEnv =  {
            'SERVER_URL':         'http://localhost:8080/++skin++Qreature',
            'HTTP_HOST':          'localhost:8080',
            'CONTENT_LENGTH':     '0',
            'GATEWAY_INTERFACE':  'TestFooInterface/1.0',
            }
        qreatureEnv =  {
            'SERVER_URL':         'http://91.189.177.18:11080/++skin++Qreature',
            'HTTP_HOST':          'www.qreature.ru',
            'CONTENT_LENGTH':     '0',
            'GATEWAY_INTERFACE':  'TestFooInterface/1.0',
            }
        http_req = TestRequest(None, qreatureEnv)
        alsoProvides(http_req,IQreatureSkin)
        alsoProvides(http_req,layer)
        return http_req
    
    def generateViewMock(self,intrfc):
        class Idle(object):
            pass
        i = Idle()
        alsoProvides(i,intrfc)
        alsoProvides(i,IQreatureGeneralVM)
        i.something_happened_with_da_first = True
        i_parent = Idle()
        alsoProvides(i_parent,IQuestionsForConstructor)
        i.__parent__ = i_parent
        return i
        
        
    def gimmeImprovedAction(self,site,request):
        url = absoluteURL(site,request)
        #remote
        r = re.compile(u'http://.*\+\+skin\+\+Qreature/qreature')
        url = r.sub(u'http://qreature.ru',url)
        def idle():
            return u'/'.join((url,u'constructor.html'))
        return idle
    
class AsyncLead(AsyncDataManager):
    adapts(IAnswerLeads)
    
    def applyChanges (self,value):
        self.ob.question_id = int(value)
    
    def deleteSelf(self):
        answer = self.ob.__parent__
        answer.__delitem__(self.ob.__name__)
        http_req = self.generateHTTPrequest(ILeadedLayer)
        i = self.generateViewMock(ILeadForAnswer)
        lead_for_answer = getMultiAdapter((answer, http_req, i,i),Interface, name=u'24AddingLeads')
        #lead_for_answer.gimmeAction = lambda: absoluteURL(getSite(),http_req) + '/constructor.html'
        lead_for_answer.gimmeAction = self.gimmeImprovedAction(getSite(), http_req)
        lead_for_answer.update()
        return lead_for_answer.render()
    
    def addSelf(self):
        http_req = self.generateHTTPrequest(ILeadedLayer)
        i = self.generateViewMock(ILeadForAnswer)
        lead_for_answer = getMultiAdapter((self.ob, http_req, i,i),Interface, name=u'40EditLeads')
        #lead_for_answer.gimmeAction = lambda: absoluteURL(getSite(),http_req) + '/constructor.html'
        lead_for_answer.gimmeAction = self.gimmeImprovedAction(getSite(), http_req)
        lead_for_answer.update()
        return lead_for_answer.render()
        
        
    
class AsyncDepend(AsyncDataManager):
    adapts(IAnswerDepends)
    
    def __init__(self,ob):
        self.ob = ob
        quiz = removeSecurityProxy(getSite())
        results = [r for r in quiz.values() if IQuizResult.providedBy(r)]
        notify(CachedObjectChangedEvent(results))
    
    def applyChanges (self,value):
        self.ob.result_id = int(value[0])
        self.ob.depend_value = int(value[1])
    
    def deleteSelf(self):
        answer = self.ob.__parent__
        answer.__delitem__(self.ob.__name__)
        #so. this answer may contain allready the add form. the only case, when add form must be rendered
        #is  the case, when the length of [depends] in current value equals to len of [results] - 1 (we just deleted one of depends)
        quiz = getSite()
        results = [r for r in quiz.values() if IQuizResult.providedBy(r)]
        depends = [d for d in answer.values() if IAnswerDepends.providedBy(d)]
        if len(results) - 1 != len(depends): return 1
        http_req  = self.generateHTTPrequest(ISlotLayer)
        i = self.generateViewMock(IRelationsForAnswer)
        depend_for_answer = getMultiAdapter((answer, http_req, i,i),Interface, name=u"23AddingDepends")
        #depend_for_answer.gimmeAction = lambda: absoluteURL(getSite(),http_req) + '/constructor.html'
        depend_for_answer.gimmeAction = self.gimmeImprovedAction(getSite(), http_req)
        depend_for_answer.update()
        return depend_for_answer.render()
    
    def addSelf(self):
        http_req  = self.generateHTTPrequest(ISlotLayer)
        i = self.generateViewMock(IRelationsForAnswer)
        
        depend_edit_for_answer = getMultiAdapter((self.ob, http_req, i,i),Interface, name=u"30EditDepends")
        #depend_edit_for_answer.gimmeAction = lambda: absoluteURL(getSite(),http_req) + '/constructor.html'
        depend_edit_for_answer.gimmeAction = self.gimmeImprovedAction(getSite(), http_req)
        depend_edit_for_answer.update()
        

        #so. this answer may contain allready the add form. the only case, when add form must be rendered
        #is  the case, when the length of [depends] in current answer is less than len of results
        quiz = getSite()
        answer = self.ob.__parent__
        results = [r for r in quiz.values() if IQuizResult.providedBy(r)]
        depends = [d for d in answer.values() if IAnswerDepends.providedBy(d)]
        
        depend_add_for_answer = getMultiAdapter((answer, http_req, i,i),Interface, name=u"23AddingDepends")
        #depend_add_for_answer.gimmeAction = lambda: absoluteURL(getSite(),http_req) + '/constructor.html'
        depend_add_for_answer.gimmeAction = self.gimmeImprovedAction(getSite(), http_req)
        depend_add_for_answer.update()
        if len(depends) == len(results):
            depend_add_for_answer.render = lambda : u''
        return u'\n'.join((depend_edit_for_answer.render(),depend_add_for_answer.render()))
    
class AsyncValue(AsyncDataManager):
    adapts(IAnswerValue)
    
    def applyChanges (self,value):
        self.ob.value = value
    
    def deleteSelf(self):
        answer = self.ob.__parent__
        answer.__delitem__(self.ob.__name__)
        http_req = self.generateHTTPrequest(IScaleLayer)
        i = self.generateViewMock(IRelationsForAnswer)
        value_for_answer = getMultiAdapter((answer, http_req, i,i),Interface, name=u"22AddingValue")
        #value_for_answer.gimmeAction = lambda: absoluteURL(getSite(),http_req) + '/constructor.html'
        value_for_answer.gimmeAction = self.gimmeImprovedAction(getSite(), http_req)
        value_for_answer.update()
        return value_for_answer.render()
    
    def addSelf(self):
        http_req = self.generateHTTPrequest(IScaleLayer)
        i = self.generateViewMock(IRelationsForAnswer)
        value_for_answer = getMultiAdapter((self.ob, http_req, i,i),Interface, name=u"20EditValue")
        #value_for_answer.gimmeAction = lambda: absoluteURL(getSite(),http_req) + '/constructor.html'
        value_for_answer.gimmeAction = self.gimmeImprovedAction(getSite(), http_req)
        value_for_answer.update()
        return value_for_answer.render()
        

class Async(MethodPublisher):
    
    def applyChanges(self,id_value, what_is_that=None):
        try:
            flatten = getUtility(IQreatureUtility, name="Flatten")
            id_value_list = [i for i in flatten(id_value)]
            if len(id_value_list) == 2:
                value = id_value_list[1]
            elif len(id_value_list) == 4:
                value = [id_value_list[1],id_value_list[3]]
            else:
                return -1   
            ob_id = int(id_value_list[0])
            quiz = removeSecurityProxy(self.context)
            sm = quiz.getSiteManager()
            ob = sm['intids'].getObject(int(ob_id))
            notify(CachedObjectChangedEvent([ob]))
            IAsyncDataManager(ob).applyChanges(value)
            return 1
        except:
            return (0-1)
    
    def addObject(self,id_obs_value, what_is_that=None):
        try:
            flatten = getUtility(IQreatureUtility, name="Flatten")
            id_obs_value_list = [i for i in flatten(id_obs_value)]
            if len(id_obs_value_list) == 3:
                value = id_obs_value_list[2]
            elif len(id_obs_value_list) == 6:
                value = [id_obs_value_list[2],id_obs_value_list[5]]
            else:
                return -1
            answer_id = int(id_obs_value_list[0])
            ob = id_obs_value_list[1]
            quiz = removeSecurityProxy(self.context)
            sm = quiz.getSiteManager()
            answer = removeSecurityProxy(sm['intids'].getObject(int(answer_id)))
            notify(CachedObjectChangedEvent([answer]))
            TYPE_OBJECT_MAP = {'lead':AnswerLeads,'depend':AnswerDepends, 'value':AnswerValue}
            if type(value) == type([]):
                ob = TYPE_OBJECT_MAP[ob](int(value[0]),int(value[1]))
            elif ob == 'value' or ob ==u'value':
                ob = TYPE_OBJECT_MAP[ob](unicode(value))
            else:
                ob = TYPE_OBJECT_MAP[ob](int(value))
            notify(ObjectCreatedEvent(ob))
            chooser = INameChooser(answer)
            name = chooser.chooseName(None, ob)
            
            if chooser.checkName(name, ob):
                answer[name] = ob
            else:
                return (0-1)
            return IAsyncDataManager(answer[name]).addSelf()
        except:
            return (0-1)

        
    def deleteObject(self,ob_id,what_is_that=None):
        try:
            quiz = removeSecurityProxy(self.context)
            sm = quiz.getSiteManager()
            ob = sm['intids'].getObject(int(ob_id))
            notify(CachedObjectChangedEvent([ob]))
            return IAsyncDataManager(ob).deleteSelf()   
        except:
            return (0-1)