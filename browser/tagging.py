# -*- coding: cp1251 -*-
from qreature.browser.qreature_views import QreatureForm
from z3c.form import form, field, button
from qreature.browser.interfaces import ITagManager, ICleanCacheEvent 
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from qreature.interfaces import IQuiz,IQreatureIntIds, IQreatureSite, IQuizResult
from zope.interface import implements
from zope.component import adapts, getUtility
from lovely.tag.interfaces import ITagging
from zope.security.proxy import removeSecurityProxy
from lovely.tag.browser.tag import ITaggingEngine, normalize
from zope.cachedescriptors.property import Lazy
from zope.component import adapter
from zc.resourcelibrary import resourcelibrary
from zc.async.tretiy3 import IHourPingEvent


class TagManagerViewlet(QreatureForm, form.Form):
    def __init__(self,context,request,view,manager):
        self.context = context
        self.request = request
        self.__parent__ = view
        self.manager = manager
        resourcelibrary.need('mochikit.Base')
        resourcelibrary.need('mochikit.DOM')
        resourcelibrary.need('qreature.browser')
    
    _fields = field.Fields(ITagManager).omit('quiz')
    
    tagsGenerated = False
    
    def get_fields(self):
        """ This method must return fields"""
        return self._fields
    
    def set_fields(self,value):
        """ This method must return fields"""
        self._fields = value
    
    fields = property(get_fields,set_fields)
    
    template = ViewPageTemplateFile('./templates/tag_manager.pt')
    
    form_name = u'Дополнительные настройки'
    
    buttons = button.Buttons(button.ImageButton
                             (name='addTag',title=u'Apply',image=u'apply.jpg'))
    
    @button.handler(buttons['addTag'])
    def handleChange(self, action):
        data, errors = self.extractData()
        if 'tags' not in data.keys(): return
        ITagManager(self.context).setTags(data['tags'])
        self.status = u'Спасибо'
        
    button_name = u'Применить'
    
    @Lazy
    def getCloud(self):
        engine = getUtility(ITaggingEngine, context=self.context, name=u'QuizTaggingEngine')
        cloud = engine.getCloud()
        return normalize(cloud, 50, 6)
    
class TagManager(object):
    implements(ITagManager)
    adapts(IQuiz)
    def __init__(self,context):
        self.quiz = removeSecurityProxy(context)
        self.tagging = ITagging(self.quiz)
    @property
    def tags(self):
        return u' '.join(self.tagging.getTags())
    
    def setTags(self,tag_string):
        tags = tag_string.split(u' ')
        tags = [tag.lower() for tag in tags if tag != u'']
        #i want to check, if this tagable will receive any new tag
        #the angry user could push the buttons up to 1000 times with the same tag values
        #if there will be no any new tag for the tagable in this values - do not update!
        #do not disturb frequency!
        old_tags = [t for t in self.tagging.getTags()]
        new_tags = False
        for t in tags:
            if t not in old_tags:
                new_tags = True
        if new_tags:
            self.tagging.update(self.quiz.__parent__.login, tags)
        #one more case. it is possible, when the user delete one or more tags.
        #this means the tags are in old, but it is less new tags than old. Update also
        else:
            if len(tags) < len(old_tags):
                self.tagging.update(self.quiz.__parent__.login, tags)

class TagCloud(object):
    #local
    #quizes_page = u'http://localhost:8080/++skin++Qreature/qreature/quizes.html'
    #remote
    quizes_page = u'http://www.qreature.ru/quizes.html'
    
    render = ViewPageTemplateFile('./templates/tag_cloud.pt')
    @Lazy
    def getCloud(self):
        engine = getUtility(ITaggingEngine, context=self.context, name=u'QuizTaggingEngine')
        cloud = engine.getCloud()
        return normalize(cloud, 50, 6)
    

#all the same but for admin!
class TagManagerAdminViewlet(TagManagerViewlet):
    
    buttons = button.Buttons(button.ImageButton
                             (name='Add',title=u'Add',image=u'add.jpg')) + \
            button.Buttons(button.ImageButton
                             (name='Delete',title=u'Delete',image=u'delete.jpg'))
            
    @button.handler(buttons['Add'])
    def handleAdd(self, action):
        data, errors = self.extractData()
        if 'tags' not in data.keys(): return
        ITagManager(self.context).setTags(data['tags'])
        
    @button.handler(buttons['Delete'])
    def handleDelete(self, action):
        data, errors = self.extractData()
        if 'tags' not in data.keys(): return
        context = self.context
        while not IQreatureSite.providedBy(context):
            context = context.__parent__
        engine = getUtility(ITaggingEngine, context=context, name=u'QuizTaggingEngine')
        tags = engine.getTags()
        engine.delete(tag=data['tags'])
    

class TagAdminManager(TagManager):
    implements(ITagManager)
    adapts(IQuizResult)
    def __init__(self, context):
        self.quiz = removeSecurityProxy(context.__parent__)
        self.tagging = ITagging(self.quiz)

@adapter(IHourPingEvent)
def cleanEmptyTags(event):
    """ """
    pass
#    context = event.ob
#    engine = getUtility(ITaggingEngine, context=context, name=u'QuizTaggingEngine')
#    tags = engine.getTags()
#    for tag in tags:
#        if sorted(engine.getItems(tags=[tag])) == []:
#            engine.delete(tag=tag)