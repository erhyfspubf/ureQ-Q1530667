from zope.viewlet.manager import ViewletManagerBase
from zope.component import getAdapters,getUtility
from zope.viewlet.interfaces import IViewlet
from qreature.interfaces import IVMCache
#from zope.app.intid.interfaces import IIntIds
from qreature.interfaces import IQreatureIntIds
from qreature.interfaces import IQuiz,IRamDirty,ICacheCleaner
from zope.interface import alsoProvides
from zope.security.proxy import removeSecurityProxy
from zope.event import notify
from qreature.browser.events import CachedObjectChangedEvent
from qreature.browser.answer.interfaces import ILeadForAnswer
from qreature.browser.quiz_constructor.interfaces import IQuestionsForConstructor
from qreature.skin.interfaces import ILeadedLayer

class QreatureButtonsMenuVM(ViewletManagerBase):
    def sort(self, viewlets):
        return sorted(viewlets)


class QreatureSiteVM(ViewletManagerBase):
    def sort(self, viewlets):
        return sorted(viewlets)

class QreatureFolderVM(ViewletManagerBase):
    def sort(self, viewlets):
        return sorted(viewlets)



class QreatureGeneralVM(ViewletManagerBase):
    
    def sort(self, viewlets):
        return sorted(viewlets)
    
    def render(self):
        """See zope.contentprovider.interfaces.IContentProvider"""
        #handle delete action here:
        if len(self.viewlets) == 0:
            return ''
        #handle delete action of inline form context
        #if context is deleted, it need to update not self.viewlets, but the view for which
        #this manager collects the viewlets. Actually it will be LeadForAnswer view
        #It will work for depends also!!!!! need to change a little
        if self.context.__name__ is None:
            if ILeadForAnswer.providedBy(self.__parent__):
                self.__parent__.something_happened_with_da_first = True
            self.__parent__.update()
            notify(CachedObjectChangedEvent([self.__parent__.context]))
            return self.__parent__.render()
            
            
        cache = getUtility(IVMCache, context=self.context)
        int_ids = getUtility(IQreatureIntIds, context=self.context)
        if IQuiz.providedBy(self.context):
            #ob_id = 'quiz'
            quiz = removeSecurityProxy(self.context)
            viewlets = [viewlet.render() for viewlet in self.viewlets]
            #the cache will be cleaned by the event system, when the quiz will be published
            #but if it will not be published, the ram will contain this viewlets until the 
            #system shut down.
            #so, it need to add this quiz to ICacheCleaner utility of qreature site
            #to clean the RAM later. So, it need to mark the quiz also as RAMDirty
            if not IRamDirty.providedBy(quiz):
                cache_cleaner = getUtility(ICacheCleaner, context=self.context)
                cache_cleaner.addCache(quiz)
                alsoProvides(quiz, IRamDirty)
        else:
            ob_id = int_ids.getId(self.context)
        
            view = str(type(self.__parent__))
            viewlets = []
            viewlet_names = zip(self.names,self.viewlets)
            for name,viewlet in viewlet_names:
                KEY = {str(name):view}
                render = cache.query(ob_id, key=KEY, default=False)
                if not render:
                    render = viewlet.render()
                    cache.set(render, ob_id, key=KEY)
                viewlets.append(render)
        return u'\n'.join([viewlet for viewlet in viewlets])
    
    def update(self):
        """See zope.contentprovider.interfaces.IContentProvider"""
        
        OTHER_MANAGER_KEYS = ["form.buttons.scale_button", "form.buttons.slots_button",
                              "form.buttons.lead_button","form.buttons.text_button_questions",
                              "form.buttons.text_button_answers","form.buttons.quiz_pages"]
        for key in OTHER_MANAGER_KEYS:
            no_need_update = self.request.get(key, default=False)
            if no_need_update:
                self.viewlets = []
                return
            
        
        self.__updated = True
        # Find all content providers for the region
        viewlets = getAdapters(
            (self.context, self.request, self.__parent__, self),IViewlet)

        viewlets = self.filter(viewlets)
        viewlets = self.sort(viewlets)

        # Just use the viewlets from now on
        self.viewlets = [viewlet for name, viewlet in viewlets]
        self.names = [name for name,viewlet in viewlets]
        # Update all viewlets and Handle Delete action
        for viewlet in self.viewlets:
            viewlet.update()
            if self.context.__name__ is None:
                #handle case when the first lead viewlet must be updated
                if IQuestionsForConstructor.providedBy(self.__parent__):
                    if ILeadedLayer.providedBy(self.request):
                        self.__parent__.question_was_removed = True
                self.viewlets = []
                break