# -*- coding: cp1251 -*-
from zope.traversing.browser import absoluteURL
from qreature.interfaces import IQreatureSite, IQreatureNews
from zope.component import getMultiAdapter,getUtility
from zope.viewlet.interfaces import IContentProvider
from zope.dublincore.interfaces import IZopeDublinCore
from z3c.form import field
from zope.app.pagetemplate import ViewPageTemplateFile
from qreature.site import QreatureNews
from zope.viewlet.interfaces import IViewletManager
from countable.interfaces import ICounterExplorer
from pagable.interfaces import IPagableView
from zope.interface import implements, Interface
from commentable.interfaces import IComment
#from zope.app.intid.interfaces import IIntIds
from qreature.interfaces import IQreatureIntIds
from qreature.browser.qreature_views import QreatureEditableView,\
                                QreaturePicturedView
from qreature.browser.actions import DeleteButton
from z3c.form import button
from qreature.browser.user_quiz.interfaces import IPublished
from qreature.interfaces import IQreatureCatalog
from qreature.browser.site.interfaces import ISiteView
from zope.app.applicationcontrol.interfaces import IServerControl
from zc.async.tretiy3 import BeforeShutDownEvent
from zope.event import notify
from lovely.tag.interfaces import ITaggingEngine

class MyQreatures(object):
    def myQreatures(self):
        request = self.request
        quiz_folder_name = unicode((request.principal.id).split('qreature').pop())
        site = self.context
        while not IQreatureSite.providedBy(site):
            site = site.__parent__
        url = absoluteURL(site[quiz_folder_name], self.request) + '/main.html'
        return request.response.redirect(url)

from zope.publisher.interfaces.browser import IBrowserPublisher


class IndexView(object):
    def __init__(self,context,request):
        self.context = context
        self.request = request
        traverser = getMultiAdapter((self.context,self.request),IBrowserPublisher)
        self.main = traverser.publishTraverse(request, 'main.html')
    def __call__(self):
        return self.main.__call__()
    
    

class Site(object):
    implements(IPagableView, ISiteView)
    items_on_page = 10
    request_range = 1
    reverse = True
    
    def __call__(self):
        self.update()
        return self.render()
    
    def update(self):
        pass
    
    render= ViewPageTemplateFile('./templates/site.pt')
    
    def sequence(self):
        newses = [news for news in self.context.values() if IQreatureNews.providedBy(news)]
        newses.sort(key=lambda x: IZopeDublinCore(x).created)
        return newses
    
    def filter(self, item):
        return True
        
    def gimmeNews(self):
        for one_news in self.sequence():
            if IQreatureNews.providedBy(one_news):
                news_vm = getMultiAdapter((one_news, self.request, self),IContentProvider, name=u'qreature.QreatureSiteVM')
                news_vm.update()
                yield news_vm


from commentable.interfaces import IHeadView

def created(context):
        created = IZopeDublinCore(context).created
        created = unicode(created)
        created = created.split(u'.')
        created.reverse()
        created = created.pop()
        return created


class News(object):
    implements(IHeadView)
    rolled = True
    root = False
    def created(self):
        return created(self.context)

class NewsCommentableView(News):
    def created(self):
        return created(self.context)
    @property
    def content(self):
        return u'<H1>' + self.context.title + u'</H1>' + self.context.body


class Admin(object):
    
    site_url = ''
    
    def __call__(self):
        self.update()
        return self.render()
    render = ViewPageTemplateFile('./templates/admin.pt')
    
    def update(self):
        self.site_url = absoluteURL(self.context,self.request)
    
    def gimmeAddNewsUrl(self):
        return self.site_url + '/+/AddQreatureNews.html'
    
    def gimmeCommentsUrl(self):
        return self.site_url + '/comments.html'
        
    def gimmeCommentsCount(self):
        cat = getUtility(IQreatureCatalog, context=self.context)
        comments_count = cat['comments'].documentCount()
        return comments_count
    
    def gimmeUsersUrl(self):
        return self.site_url + '/users.html'
    
    def gimmeUsersCount(self):
        cat = getUtility(IQreatureCatalog, context=self.context)
        comments_count = cat['users'].documentCount()
        return comments_count
        
    def gimmeQuizesUrl(self):
        return self.site_url + '/quizes.html'
    
    def gimmeQuizesCount(self):
        cat = getUtility(IQreatureCatalog, context=self.context)
        quizes_count = cat['quizes'].documentCount()
        return quizes_count

class Comments(QreatureEditableView):
    
    implements(IPagableView)
    
    button_titles = False
    
    render = ViewPageTemplateFile('./templates/comments.pt')
    request_range = 1
    items_on_page = 10
    reverse = True
    
    def sequence(self):
        cat = getUtility(IQreatureCatalog, context=self.context)
        int_ids = getUtility(IQreatureIntIds, context=self.context)
        comments = cat['comments'].apply((None,None))
        comments = [int_ids.getObject(comment) for comment in comments]
        comments.sort(key=lambda x: IZopeDublinCore(x).created)
        return comments
    
    
    def update(self):
        pass
    
    def filter(self,item):
        return True
    
    def __call__(self):
        self.update()
        return self.render()
    
    def gimmeComments(self):
        for comment in self.sequence():
            commentable = comment
            while IComment.providedBy(commentable):
                commentable = commentable.__parent__
            url = absoluteURL(commentable,self.request) + '/thread.html'
            created = created = IZopeDublinCore(comment).created
            actions = getMultiAdapter((comment,self.request,self),
                                         IViewletManager,name="qreature.QreatureSiteVM")
            actions.update()
            yield {'title':comment.title,'body':comment.body,
                   'actions':actions,'created':created,'url':url}
            
class DeleteCommentButton(DeleteButton):
        
        
    buttons = button.Buttons(button.ImageButton
                         (name='delete',title=u'Delete',image=u'delete.jpg'))               

            
    @button.handler(buttons['delete'])
    def handleDelete(self, action):
        parent = self.context.__parent__
        parent.__delitem__(self.context.__name__)
        return self.request.response.redirect(self.request.URL)
        
        
class Users(object):
    render = ViewPageTemplateFile('./templates/users.pt')
    def __call__(self):
        self.update()
        return self.render()
    
    implements(IPagableView)
    items_on_page = 10
    reverse = True
    request_range = 1
    def sequence(self):
        cat = getUtility(IQreatureCatalog, context=self.context)
        int_ids = getUtility(IQreatureIntIds, context=self.context)
        users = cat['users'].apply((None,None))
        users = [int_ids.getObject(user) for user in users]
        users.sort(key=lambda x: IZopeDublinCore(x).created)
        return users
    def update(self):
        pass
    
    def filter(self,item):
        return True
    def gimmeUsers(self):
        for user in self.sequence():
            created =  IZopeDublinCore(user).created
            yield {'title':user.login,'url':user.url,
                   'email':user.email,'created':created}
        
    
class Quizes(QreaturePicturedView):
    render = ViewPageTemplateFile('./templates/quizes.pt')
    def __call__(self):
        self.update()
        return self.render()
    
    items_on_page = 10
    reverse = True
    request_range = 1
    implements(IPagableView)
    sequence = None
    
    @property
    def quiz_icon(self):
        return self.gimmePicturesUrls()['qreature_icon']
    @property
    def user_icon(self):
        return self.gimmePicturesUrls()['user']
    

    
    def __init__(self, *args, **kwargs):
        super(Quizes,self).__init__(*args,**kwargs)
        self.install_sequence()
    
    
    def update(self):
        #for sure :)
        if self.sequence is None:
            self.install_sequence()
    
    def install_sequence(self):
        tag = self.request.get('tagname')
        int_ids = getUtility(IQreatureIntIds, context=self.context)
        
        if tag is not None:
            engine = getUtility(ITaggingEngine, context=self.context, name=u'QuizTaggingEngine')
            quizes_ids = sorted(engine.getItems(tags=(tag,)))
        else:
            cat = getUtility(IQreatureCatalog, context=self.context)
            quizes_ids = cat['quizes'].apply((None,None))
            
        quizes = [int_ids.queryObject(quiz) for quiz in quizes_ids]
        quizes = [q for q in quizes if q is not None]
        quizes.sort(key=lambda x: IZopeDublinCore(x).created)
        def sequence():
            return quizes
        self.sequence = sequence
    
    def filter(self,item):
        if IPublished.providedBy(item):return True
        return False
    
    def gimmeQuizes(self):
        for quiz in self.sequence():
            quiz_url = absoluteURL(quiz,self.request) + '/go.html'
            quiz_body =  getMultiAdapter((quiz, self.request),Interface, name="preview.html")
            quiz_body.source = False
            quiz_body.quiz = quiz
            quiz_body.update()
            yield {'quiz_body':quiz_body,'author':quiz.__parent__.login}

from z3c.form import form

class QreatureNewsAddForm(form.AddForm):
    fields = field.Fields(IQreatureNews).omit('__parent__','__name__')
    form_name = u'Добавление комментария'
    button_name = u'Добавить новость'
    template = ViewPageTemplateFile('../templates/qreature_form.pt')
    def nextURL(self):
        site = self.context.context
        site_url = absoluteURL(site, self.request)+ u'/admin.html'
        return site_url
    def create(self, data):
        return QreatureNews(**data)
    def add(self, object):
        ob = self.context.add(object)
        self._finishedAdd = True
        return ob

    
class CommentCounter(object):
    def gimmeCounter(self):
        ce = getUtility(ICounterExplorer,context=self.context)
        counter = ce.getCounter(self.context,'comments')
        return counter




from z3c.form import form
from qreature.browser.actions import QuizAction
from qreature.interfaces import ICacheCleaner

def cleanViewletsCaches(context):
    cache_cleaner = getUtility(ICacheCleaner, context=context)
    cache_cleaner.cleanCaches()

def cleanCountersCaches(context):
    counter_explorer = getUtility(ICounterExplorer, context=context)
    counter_explorer.invalidateAll()
    
def cleanEmptyTags(context):
    engine = getUtility(ITaggingEngine, context=context, name=u'QuizTaggingEngine')
    tags = engine.getTags()
    for tag in tags:
        items = sorted(engine.getItems(tags=[tag]))
        if  items == []:
            engine.delete(tag=tag)
    
    
        
class CleanCacheButton(QuizAction,form.Form):
    button_title = u'Чистить RAM'
    buttons = button.Buttons(button.ImageButton
                             (name='clean_cache',title=u'CleanCache',image=u'clean_cache.jpg'))
    @button.handler(buttons['clean_cache'])
    def clean(self,action):
        cleanViewletsCaches(self.context)
        cleanCountersCaches(self.context)
        #cleanEmptyTags(self.context)


class BeforeSwitchOffButton(QuizAction,form.Form):
    button_title = u'Чистить RAM'
    buttons = button.Buttons(button.ImageButton
                             (name='before_switch_off',title=u'BeforeSwitchOff',image=u'before_switch_off.jpg'))
    
    
    @button.handler(buttons['before_switch_off'])
    def before_switch_off(self,action):
        cleanViewletsCaches(self.context)
        cleanCountersCaches(self.context)
        cleanEmptyTags(self.context)
        #thats for zc.async to deactivate dispatcher
        notify(BeforeShutDownEvent())
        sc = getUtility(IServerControl)
        sc.restart()
        

class DynamicSiteMap(object):
    def gimmeURL(self):
        cat = getUtility(IQreatureCatalog, context=self.context)
        int_ids = getUtility(IQreatureIntIds, context=self.context)
        quizes = cat['quizes'].apply((None,None))
        quizes = [int_ids.getObject(quiz) for quiz in quizes]
        for quiz in quizes:
            if IPublished.providedBy(quiz):
                loc = absoluteURL(quiz,self.request) + '/go.html'
                loc = loc[:7] + 'www.' + loc[7:]
                created = IZopeDublinCore(quiz).created
                created = unicode(created)
                created = created.split(u'.')
                created.reverse()
                created = created.pop()
                created = created.split(u' ')
                created.reverse()
                lastmod = created.pop()
                changefreq= "weekly"
                priority="0.5"
                yield {'loc':loc,'lastmod':lastmod,'changefreq':changefreq,'priority':priority}