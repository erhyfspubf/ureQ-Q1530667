# -*- coding: cp1251 -*-
from qreature.interfaces import IVMCache
from qreature.interfaces import IQreatureIntIds
from qreature.interfaces import IQuiz,IRamDirty,ICacheCleaner,IQuizResult,IAnswerDepends, IAnswerLeads,IAnswerValue
from zope.component import adapter, getUtility
from qreature.browser.interfaces import ICachedObjectChangedEvent,ICleanCacheEvent
from zope.interface import noLongerProvides
from zope.security.proxy import removeSecurityProxy
from qreature.interfaces import IQuizQuestion,ILeadedQuiz, IQreatureUtility, IQuizAnswer
from zope.app.container.interfaces import IObjectAddedEvent,IObjectRemovedEvent
from zope.app.component.hooks import getSite
from zope.event import notify
from qreature.browser.events import CachedObjectChangedEvent, CleanCacheEvent
from qreature.interfaces import ISlotQuiz,IQreatureNews
from qreature.interfaces import IQreatureComment
from countable.interfaces import ICounterHolder
from qreature.browser.interfaces import ICommentSubscriberQuiz
from goog.gmail.gmailer import IGMailer
from zc.async.job import Job
from zc.async.interfaces import IQueue
from qreature.browser.interfaces import IResultShown,IQuizPublishedEvent
from countable.interfaces import ICounterExplorer

@adapter(ICachedObjectChangedEvent)
def clean_viewlets_tree(event):
    ob = event.ob
    if len(ob) ==0:return
    int_ids = getUtility(IQreatureIntIds, context=ob[0])
    cache = getUtility(IVMCache, context=ob[0])
    while not IQuiz.providedBy(ob[0]):
        ids = [int_ids.queryId(o) for o in ob]
        [cache.invalidate(id) for id in ids if id is not None]
        ob = [o.__parent__ for o in ob]
        cleaned_ob = []
        for o in ob:
            if not o in cleaned_ob:
                cleaned_ob.append(o)
        ob = cleaned_ob

        
@adapter(ICleanCacheEvent)
def clean_cache(event):
    ob = removeSecurityProxy(event.ob)
    cache = getUtility(IVMCache, context=ob)
    cache.invalidateAll()
    #unmark the quiz
    noLongerProvides(ob,IRamDirty)
    #remove it from cache_cleaner
    cache_cleaner = getUtility(ICacheCleaner, context=ob.__parent__)
    cache_cleaner.removeCache(ob)

    

#it need to destroy chached lead viewlets in RAM
#it need also reupdate first lead viewlet, cause from it contents, all over leads viewlets are filled via javascript
#reupdating implemented in manager, during updating QuestionsForConstructor viewlet, and during rendering
#there are two cases: first catched in manager.render() it catch the deletion of lead by removeIDSHolders event
#when the lead viewlet is allready updated, but the context is deleted. it need to reupdate it to show AddForm
#second case is


@adapter(IQuizQuestion,IObjectAddedEvent)
def cleanLeadsAtAdding(question,event):
    cleanLeads()
    
@adapter(IQuizQuestion,IObjectRemovedEvent)
def cleanLeadsAtDeleting(question,event):
    cleanLeads()


def cleanLeads():
    site = getSite()
    if not ILeadedQuiz.providedBy(site): return
    flatten = getUtility(IQreatureUtility, name="Flatten")
    answers = [[a for a in q.values() if IQuizAnswer.providedBy(a)] for q in site.values() if IQuizQuestion.providedBy(q)]
    answers = [a for a in flatten(answers)]
    #add forms
    answers_to_clean = []
    #edit forms
    leads_to_clean = []
    for a in answers:
        if a.has_key('lead'):
            leads_to_clean.append(a['lead'])
        else:
            answers_to_clean.append(a)
    notify(CachedObjectChangedEvent(answers_to_clean))
    notify(CachedObjectChangedEvent(leads_to_clean))

@adapter(IQuizQuestion,IObjectRemovedEvent)
def cleanRAMForQuestion(ob,event):  
    notify(CachedObjectChangedEvent([ob]))
    
@adapter(IQuizAnswer,IObjectRemovedEvent)
def cleanRAMForAnswer(ob,event):
    notify(CachedObjectChangedEvent([ob]))

@adapter(IQuizResult,IObjectRemovedEvent)
def cleanRAMForResult(ob,event):
    site = getSite()
    if ISlotQuiz.providedBy(site):
        notify(CleanCacheEvent(site))
    notify(CachedObjectChangedEvent([ob]))
    
    
@adapter(IAnswerDepends,IObjectRemovedEvent)
def cleanRAMForDepends(ob,event):
    notify(CachedObjectChangedEvent([ob]))
    
@adapter(IAnswerValue,IObjectRemovedEvent)
def cleanRAMForValue(ob,event):
    notify(CachedObjectChangedEvent([ob]))
    
@adapter(IAnswerLeads,IObjectRemovedEvent)
def cleanRAMForLead(ob,event):
    notify(CachedObjectChangedEvent([ob]))
    
@adapter(IQreatureComment, IObjectAddedEvent)
def commentToEmail(comment,event):
    """ so. the idea is to get the root object in thread. Possible it could be IQuiz or IQreatureNews.
    The shortes way to get the root is to look for ICounterHolder object. Check then, is it EmailSubscriptable or not."""
    parent = comment.__parent__
    print '-----------------------------'
    while not ICounterHolder.providedBy(parent):
        parent = parent.__parent__
    if ICommentSubscriberQuiz.providedBy(parent):
        quiz = parent
        folder = quiz.__parent__
        email = folder.email
        message = u"В вашем тесте: " + quiz.title + u' кто-то под именем: ' + comment.title + u' оставил следующий комментарий: '
        
    elif IQreatureNews.providedBy(parent):
        email = u'aganzha@yandex.ru'
        message = comment.title + u' оставил следующий комментарий: '
    
    else: return
    
    message = u''.join((message,comment.body))
    gmailer = getUtility(IGMailer, context = parent)    
    queue = IQueue(gmailer)
    job = queue.put(Job(gmailer.send_email,email, u'Новый комментарий', message, sender=u'www.qreature.ru'))


@adapter(IResultShown)
def countResults(event):
    ce = getUtility(ICounterExplorer,context=event.result)
    int_ids = getUtility(IQreatureIntIds, context = event.result)
    res_id = int_ids.getId(event.result)
    print '************the key which goes to explorer**************'
    print res_id
    ce.incrementCounter(event.result,res_id)
    
@adapter(IQuizPublishedEvent)
def doPostPublishRoutine(event):
    pass