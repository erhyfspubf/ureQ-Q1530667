# -*- coding: cp1251 -*-
from zope.viewlet.interfaces import IViewletManager
from zope.interface import Interface, Attribute
from zope.schema import Bool, TextLine, URI, Text


class IQreatureSiteVM(IViewletManager):
    """ returns some usefull viewlets"""

class IQreatureFolderVM(IViewletManager):
    """ returns some usefull viewlets"""

class IQreatureGeneralVM(IViewletManager):
    """ returns some usefull viewlets"""
    
class IQreatureButtonsMenuVM(IViewletManager):
    """ Buttons in the top of the window. Usually - links for IAdding"""

class IQreatureView(Interface):
    """ This is a common class for views and viewlets for this package.
    The viewlets can contain other viewlets"""
    
    nothing = Attribute(u'Bolean value, indicated is there something to render')
    
    viewlets = Attribute(u'Viewlet manager, containing viewlets to be rendered.')
    
    def update():
        """ call this prior to rendering"""
    def render():
        """ call this to render the template"""
    def gimmeViewlets():
        """Templates call this method to render viewlets"""

class IQreaturePicturedView(Interface):
    """ Templates of this view will contain some images."""
    def gimmePicturesUrls():
        """ return url of image for <image> tag"""
        
class IQreatureEditableView(Interface):
    """ View, for wich is possible to call Actions viewlet
    Actions viewlet contains other viewlets: Preview, Edit, Delete
    """
    button_titles = Bool(title=u'Does this view need button_titles for actions buttons?')





class IQreatureActions(Interface):
    """This is a viewlet, registered for above view, containing buttons viewlets """
    
class IQreatureAddForm(Interface):
    """ """

class IQreatureEditForm(Interface):
    """ """

    
    

class IQreaturePictureLink(Interface):
    """ """
    show_title = Bool(title=u'False or True')
    title=TextLine(title=u'Title')
    image=URI(title=u'Image for <mage src=')
    url=URI(title=u'url to go to')
    def gimmeLink():
        """ returns {'url':...,'image':...,'title':...}"""
        
class IQuizField(Interface):
    pass

class IQreatureContentTitle(Interface):
    """ """
    
class IQreaturePrefixedButton(Interface):
    """ Each button widget must have its unique Id. This id is got from prefix,
    which is a id from IntIds for the context object of the button"""
    prefix = Attribute(u'The prefix of the button')
    
class ICachedObjectChangedEvent(Interface):
    pass

class ICleanCacheEvent(Interface):
    pass

from zope.schema import Object,Bool
from qreature.interfaces import IQuiz

class IPreviewForm(Interface):
    """ Display form for Quiz container with the button to pass the quiz
    and source code widget"""
    quiz = Object(IQuiz)
    source = Bool(title=u'Neeed source widget or not')
    need_button = Bool(title=u'Neeed button or not')
    def do_i_need_source_widget():
        """ use self.quiz and self.source attributes"""
    def gimmeForm():
        """ return form without html header and use-macro directive"""
    values = Attribute(u'values for OpenValuesWidget')
   
class ISourceCode(Interface):
    source = Text(title=u'HTML Код для блога или сайта')
    
class IAdditionalAdjustment(Interface):
    need_values = Bool(title=u"Показывать набранные баллы")
    need_results = Bool(title=u"Показать другие результаты")
    quiz = Attribute(u'Quiz')
    subscribe_on_to_comments = Bool(title=u'Присылать комментарии на email')
class IOpenResultsQuiz(Interface):
    """ Quiz, which additionaly show all the rest results for the user. """
class IOpenValuesQuiz(Interface):
    """ Quiz, which shows the values, which user get"""
class ICommentSubscriberQuiz(Interface):
    """ Quiz, on which comments it is possible to suscribe via email"""

class IQreatureLogin(Interface):
    """ login form with password reminder"""

from qreature.interfaces import check_email

    
class ILoginEmail(Interface):
    login = TextLine(title=u'Логин', required = False)
    email = TextLine(title=u'email',constraint=check_email, required = False)
    
    
class IResultShown(Interface):
    """ """
    
class IVolatileStorage(Interface):
    """ This is a simple ramcache"""
    
class IQuizPublishedEvent(Interface):
    """ This is an event"""
    quiz = Attribute(u'Quiz')
    
class ITagManager(Interface):
    tags = Text(title=u'Список тегов')
    quiz = Attribute(u'Quiz')
    
class IPaidQuiz(Interface):
    """ """