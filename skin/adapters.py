from zope.component import adapts, getMultiAdapter
from zope.component import queryMultiAdapter
from zope.interface import alsoProvides, noLongerProvides
from qreature.interfaces import IQuiz,ISlotQuiz, IScaleQuiz,ILeadedQuiz,IQreatureSite
from qreature.skin.interfaces import ISlotLayer, IScaleLayer, ILeadedLayer,\
                                    IPublishedLayer, ICheckedLayer, IOpenResultsLayer,IOpenValuesLayer

from qreature.browser.user_quiz.interfaces import IPublished, IChecked
from zope.app.security.interfaces import IUnauthenticatedPrincipal
from qreature.skin.interfaces import IAdvertLayer
from multi_traverser.interfaces import IMultiTraverserClient
from zope.interface import implements
from qreature.browser.interfaces import IOpenResultsQuiz,IOpenValuesQuiz

class QreatureTraverser(object):
    implements(IMultiTraverserClient)
    adapts(IQreatureSite)
    priority = 30
    def __init__(self, context):
        self.context = context
    def publishTraverse(self, request, name,view):
        if view is None:
            view = queryMultiAdapter((self.context, request), name='main.html')
        principal = request.principal
        if IUnauthenticatedPrincipal.providedBy(principal):
            alsoProvides(request,IAdvertLayer)
        return view
    

class QuizTraverser(object):
    implements(IMultiTraverserClient)
    adapts(IQuiz)
    priority = 15
    def __init__(self, context):
        self.context = context
    def publishTraverse(self, request, name,view):
        """See zope.publisher.interfaces.IPublishTraverse"""
        site = self.context
        if ISlotQuiz.providedBy(site):
            alsoProvides(request, ISlotLayer)
            if IScaleLayer.providedBy(request):
                noLongerProvides(request, IScaleLayer)
        elif IScaleQuiz.providedBy(site):
            alsoProvides(request, IScaleLayer)
            if ISlotLayer.providedBy(request):
                noLongerProvides(request, ISlotLayer)
        else:
            alsoProvides(site, ISlotQuiz)
            alsoProvides(request, ISlotLayer)
            
        if ILeadedQuiz.providedBy(site):
            alsoProvides(request, ILeadedLayer)
        else:
            if ILeadedLayer.providedBy(request):
                noLongerProvides(request, ILeadedLayer)
                
        if IPublished.providedBy(site):
            alsoProvides(request, IPublishedLayer)
            
        if IChecked.providedBy(site):
            alsoProvides(request, ICheckedLayer)
        
        if IOpenValuesQuiz.providedBy(site) and IScaleQuiz.providedBy(site):
            alsoProvides(request,IOpenValuesLayer)
        
        if IOpenResultsQuiz.providedBy(site):
            alsoProvides(request, IOpenResultsLayer)
        
        if view is None:
            view = queryMultiAdapter((self.context, request), name=name)    
        
        if view is None:
            not_found = getMultiAdapter((self.context, request), name='not_found.html')
            return not_found
        
        return view