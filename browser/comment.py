# -*- coding: cp1251 -*-
from qreature.browser.qreature_views import QreatureAddForm
from qreature.interfaces import IQreatureComment
from z3c.form import field
from qreature.site import QreatureComment
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.component import getMultiAdapter
from zope.viewlet.interfaces import IViewletManager
from zope.traversing.browser import absoluteURL
from commentable.interfaces import ICommentable
from zope.dublincore.interfaces import IZopeDublinCore
from qreature.browser.actions import DeleteButton
from z3c.form import button
from zope.dublincore.interfaces import IZopeDublinCore
from zope.component import getUtility
from countable.interfaces import ICounterExplorer


class QreatureCommentAddForm(QreatureAddForm):
    fields = field.Fields(IQreatureComment).omit('__parent__','__name__')
    form_name = u'Добавление комментария'
    button_name = u'Добавить комментарий'
    template = ViewPageTemplateFile('./templates/qreature_comment_add_form.pt')
    
    def create(self, data):
        return QreatureComment(**data)
    
    def add(self, object):
        ob = self.context.add(object)
        self._finishedAdd = True
        return ob

    def nextURL(self):
        context = self.context.context
        request = self.request
        while not ICommentable.providedBy(context):
            context=context.__parent__
        thread_url = absoluteURL(context, request)+ u'/thread.html'
        return thread_url
    
    def gimmeParent(self):
        vm = getMultiAdapter((self.context.context,self.request,self),IViewletManager, name="commentable.CommentableViewVM")
        vm.update()
        return vm

    def render(self):
        if self._finishedAdd:
            self.request.response.redirect(self.nextURL())
            return ""
        return super(QreatureCommentAddForm, self).render()
    



class CommentCommentableView(object):
    @property
    def content(self):
        return u'<H1>' + self.context.title + u'</H1>' + self.context.body
    def created(self):
        created = IZopeDublinCore(self.context).created
        created = unicode(created)
        created = created.split(u'.')
        created.reverse()
        created = created.pop()
        return created
    
    


class QuizCommentableView(object):
    @property
    def content(self):
        return u'<H1>' + self.context.title + u'</H1>' + self.context.body
    def created(self):
        created = IZopeDublinCore(self.context).created
        created = unicode(created)
        created = created.split(u'.')
        created.reverse()
        created = created.pop()
        return created
    
class CommentCounter(object):
    def gimmeCounter(self):
        ce = getUtility(ICounterExplorer,context=self.context)
        counter = ce.getCounter(self.context,'comments')
        return counter
    

class DeleteCommentButton(DeleteButton):        
    buttons = button.Buttons(button.ImageButton
                         (name='delete',title=u'Delete',image=u'delete.jpg'))               

    @button.handler(buttons['delete'])
    def handleDelete(self, action):
        parent = self.context.__parent__
        parent.__delitem__(self.context.__name__)
        return self.request.response.redirect(self.request.URL)