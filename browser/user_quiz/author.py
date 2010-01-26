from qreature.interfaces import IQreatureFolder,IQuiz
from qreature.browser.user_quiz.interfaces import IPublished
from zope.traversing.browser import absoluteURL
from qreature.browser.qreature_views import QreaturePicturedView
from zope.security.proxy import removeSecurityProxy

class Authored(object):
    """ a marker view, for which Authored viewlet is shown"""
    
    
class AuthorInfo(QreaturePicturedView):
    
    folder = None
    quizes = None
    other_quizes = False
    
    
    def update(self):
        site = self.context
        while not IQuiz.providedBy(site):
            site = site.__parent__
        quiz = removeSecurityProxy(site)
        self.folder = removeSecurityProxy(site.__parent__)
        self.quizes = [q for q in self.folder.values() if IPublished.providedBy(q) and not (q is quiz)]
        if len(self.quizes) != 0: self.other_quizes = True
    
    @property
    def icon(self):
        pictures = self.gimmePicturesUrls()
        return pictures['qreature_icon']
    
    @property
    def user(self):
        pictures = self.gimmePicturesUrls()
        return pictures['user']
    
    def gimmeQuizes(self):
        quizes = []
        for quiz in self.quizes:
                quiz_url = absoluteURL(quiz,self.request) + '/go.html'
                quizes.append({'title':quiz.title, 'url':quiz_url})        
        return quizes