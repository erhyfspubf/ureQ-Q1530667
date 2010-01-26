from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from qreature.interfaces import IQuiz,IQreatureFolder
from zope.app.component.hooks import getSite
from zope.traversing.browser import absoluteURL

class Advert(object):
    render = ViewPageTemplateFile('templates/advert.pt')
    def __call_(self):
        self.update()
        return self.render()
    def update(self):
        pass
    def more(self):
        site = getSite()
        if IQuiz.providedBy(site):
            site = site.__parent__.__parent__
        elif IQreatureFolder.providedBy(site):
            site = site.__parent__
        return absoluteURL(site, self.request) + '/advert.html'
        
        
    

class Adverted(object):
    """ a marker view, for which Advert viewlet is shown"""
