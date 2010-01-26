# -*- coding: cp1251 -*-
from zope.app.container.interfaces import IContainer, IContained
from zope.app.component.interfaces import IPossibleSite
from zope.schema import TextLine, Text,Password, Choice,Object, Id, URI, Bytes
from zope.interface import Interface, Invalid, invariant,implements,Attribute
from zope.app.container.constraints import containers
import re
from zope.app.component.hooks import getSite
from zope.app.file.interfaces import IImage
from zope.app.cache.interfaces.ram import IRAMCache


class IQreatureSite(IContainer, IPossibleSite):
    def setSiteManager(self):
        """ """
mail_regex = r"[a-zA-Z0-9._%-]+@([a-zA-Z0-9-]+\.)*[a-zA-Z]{2,4}"
login_regex = r"[a-zA-Z0-9._%-]"
check_email = re.compile(mail_regex).match    
check_login = re.compile(login_regex).match


class IQreatureFolder(IContainer, IPossibleSite):
    containers('qreature.interfaces.IQreatureSite')
    login = TextLine(title=u'Логин', constraint=check_login,required=True)
    password = Password(title=u'Пароль',required=True)
    confirm_password = Password(title=u'Пароль еще раз',required=True)
    email = TextLine(title=u'email', constraint=check_email, required=True)
    @invariant
    def passwordMatching(quiz_folder):
        if quiz_folder.password != quiz_folder.confirm_password:
            raise Invalid("Passwords don`t match")
    @invariant
    def loginMatching(quiz_folder):
        """ """
        site = getSite()
        if site.has_key(quiz_folder.login):
            raise Invalid("Login exists!")
    url = URI(title=u'URL блога или сайта', default = "http://www.qreature.ru")
    about = Text(title=u'Информация о себе', default = u'',required=False)
    

    def setSiteManager(self):
        """ """


class IQreatureEditableTextArea(Interface):
    """ """
class QreatureEditableTextArea(Text):
    """ """
    implements(IQreatureEditableTextArea)

class IQuizContainer(IContainer):
    title = TextLine(title=u'Название', required=True)
    body = QreatureEditableTextArea(title=u'Содержание', default=u'', required=True)

class IQuiz(IQuizContainer,IPossibleSite):
    containers('qreature.interfaces.IQreatureFolder')
    
class IQuizResult(IQuizContainer):
    containers('qreature.interfaces.IQuiz')
    
    
class IQuizQuestion(IQuizContainer):
    containers('qreature.interfaces.IQuiz')
    
class IQuizAnswer(IQuizContainer):
    containers('qreature.interfaces.IQuizQuestion')
    
class IAnswerDepends(IContained):
    containers('qreature.interfaces.IQuizAnswer')
    result_id = Choice(title=u'Влияние',vocabulary="Quiz Results")
    depend_value = Choice(vocabulary="Percentage")
    

class IAnswerLeads(IContained):
    containers('qreature.interfaces.IQuizAnswer')
    question_id = Choice(title=u'Перемещение',vocabulary="Quiz Leads")

class INewQreatureFolderEvent(Interface):
    """ """
    
class INewQreatureSiteEvent(Interface):
    """ """
    
class INewQuizEvent(Interface):
    """ """


def check_value(value):
    try:
        int(value)
    except ValueError:
        return False
    return True
        
    
    
class IAnswerValue(Interface):
    value = TextLine(title=u'Баллы',constraint=check_value)


class IScaleQuiz(Interface):
    pass

class ISlotQuiz(Interface):
    pass

class IQreatureAvatar(IImage):
    """ """

class IQreaturePrincipalInfo(Interface):
    uri = Id(title=u'веб адресс', required=False)
    about = Text(title=u'о себе', required=False)
    avatar = Object(title=u'аватар', schema=IQreatureAvatar)
    
class IQreatureNews(IContainer):
    title = TextLine(title=u'news title',required=True)
    body = Text(title = u'news body',required=True)
    
class IQreatureComment(IContainer):
    title = TextLine(title=u'автор',required=True)
    body = Text(title=u'комментарий',required=True)
    

class ILeadedQuiz(Interface):
    """ Quiz with leads"""
    
class IQreatureUtility(Interface):
    """ just some usefull functions. called by name"""
    
    
class IVMCache(IRAMCache):
    """ RAM Cache for storing viewlets rendered content"""
    
class IRamDirty(Interface):
    """ Marker for Quiz, which add viewlets to RAM"""
class ICacheCleaner(IRAMCache):
    """ Utility which stores ids of quizes which store their viewlets in VMCache
    Used to clean VMCache of this quizes"""
    int_ids = Attribute(u'IIntIds utility')
    def cleanCaches():
        """ clean VMCaches of the objects in self storage"""
    def addCache(quiz_id):
        """ adds VM to storage"""
    def init():
        """ install an empty list to RAM"""
        
class IQreatureIntIds(Interface):
    """ marker interface for my IntId utilities"""

class IQreatureIntIdRemovedEvent(Interface):
    """ """
    
class IQreatureCatalog(Interface):
    """ marker interface for my Catalog"""
    
class IQreatureTaggable(Interface):
    """ I have to use my own adapter for ITaggable, because my IntIds utilities are twisted :)
        Hope i could simply inherit it from lovely.tag.tagging.Tagging and overwrite some methods"""
        
class IQuizAsXML(Interface):
    download = TextLine(title=u'скачать тест в виде xml',required=False)
    upload = Bytes(required=False)
    def generateXML(quiz):
        """ """
    def generateQuiz(file_upload):
        """ """