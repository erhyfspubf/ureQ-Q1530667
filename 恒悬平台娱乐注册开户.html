# -*- coding: cp1251 -*-

from qreature.interfaces import IQreatureFolder, INewQreatureFolderEvent, IQreatureSite,\
 INewQreatureSiteEvent,IQuiz, IQuizResult,IQuizAnswer,IAnswerLeads,IAnswerDepends
from qreature.interfaces import INewQuizEvent, IQuizQuestion,IQreatureComment
from zope.component import adapter, getUtility,queryUtility
from zope.app.container.interfaces import IObjectAddedEvent,IObjectRemovedEvent,IObjectModifiedEvent
from qreature.utilities import QreatureCatalog
from zope.app.catalog.text import TextIndex
from zope.app.catalog.field import FieldIndex
from zope.index.text.interfaces import ISearchableText
from zope.app.authentication.principalfolder import PrincipalFolder
from zope.app.authentication.authentication import PluggableAuthentication
from zope.app.authentication.interfaces import IPluggableAuthentication
from zope.app.security.interfaces import IAuthentication
from zope.app.component.site import LocalSiteManager  
from zope.app.authentication.principalfolder import IInternalPrincipalContainer
from zope.app.authentication.interfaces import ICredentialsPlugin
from zope.app.authentication.session import SessionCredentialsPlugin
from zope.app.authentication.principalfolder import InternalPrincipal
from zope.app.securitypolicy.role import LocalRole
from zope.app.securitypolicy.interfaces import IRole
from zope.app.authentication.interfaces import IAuthenticatedPrincipalCreated
from zope.app.securitypolicy.interfaces import IRolePermissionManager,IPrincipalRoleManager,IPrincipalPermissionManager    
from zope.component import createObject
from qreature.interfaces import IScaleQuiz
from zope.interface import alsoProvides
from qreature.utilities import JustRegisteredCredentialPlugin
from captcha.explorer import CaptchaExplorer
from countable.explorer import CounterExplorer
from zope.app.component.hooks import getSite
from qreature.interfaces import IQreatureUtility
from zope.app.cache.ram import RAMCache
from qreature.interfaces import IVMCache
from zope.security.proxy import removeSecurityProxy
from qreature.utilities import CacheCleaner
from qreature.interfaces import ICacheCleaner
from qreature.interfaces import IQreatureIntIds
from zope.app.intid import IntIds
from qreature.interfaces import IQreatureCatalog,IQreatureIntIdRemovedEvent
from zope.interface import implements
from qreature.browser.events import CachedObjectChangedEvent
from countable.interfaces import ICounterExplorer



@adapter(IQreatureSite, IObjectAddedEvent)
def setQreatureSiteSiteManager(site, event):
    """ When da site is created, first of all it need to set up SiteManager
    so call the overriden setSiteManager with zope`s library site manager
    implementation as parameter"""
    site.setSiteManager(LocalSiteManager(site))


@adapter(IQreatureFolder, IObjectAddedEvent)
def setQreatureFolderSiteManager(site, event):
    """ When da site is created, first of all it need to set up SiteManager
    so call the overriden setSiteManager with zope`s library site manager
    implementation as parameter"""
    site.setSiteManager(LocalSiteManager(site))
    
    
@adapter(IQuiz, IObjectAddedEvent)
def setQreatureSiteManager(site, event):
    """ When da site is created, first of all it need to set up SiteManager
    so call the overriden setSiteManager with zope`s library site manager
    implementation as parameter"""
    site.setSiteManager(LocalSiteManager(site))
    
@adapter(INewQreatureSiteEvent)
def setQreatureSiteUtilities(event):
    """ This is a handler for custom event.
    All object hierarchies and site-level utilities are created here"""
    site = event.object
    sm = site.getSiteManager()
    site_intids = IntIds()
    sm['intids'] = site_intids
    sm.registerUtility(site_intids, IQreatureIntIds)
 
    #Security
    pau = PluggableAuthentication()
    sm['pau'] = pau
    sm.registerUtility(pau, IPluggableAuthentication)
    sm.registerUtility(pau, IAuthentication)
    
    principal_folder = PrincipalFolder(prefix = u'qreature')
    pau.__setitem__('PrincipalFolder', principal_folder)
    sm.registerUtility(principal_folder, IInternalPrincipalContainer)
    
    session_credentials = SessionCredentialsPlugin()
    pau.__setitem__('Session Credentials', session_credentials)
    just_registered_credentials = JustRegisteredCredentialPlugin()
    pau.__setitem__('Just Registered Credentials', just_registered_credentials)
    
    sm.registerUtility(session_credentials, ICredentialsPlugin, 'Session Credentials')
    sm.registerUtility(just_registered_credentials, ICredentialsPlugin, 'Just Registered Credentials')
    
    pau.authenticatorPlugins = []
    pau.authenticatorPlugins.append(u'PrincipalFolder')
    pau.credentialsPlugins = []
    pau.credentialsPlugins.append(u'Session Credentials')
    pau.credentialsPlugins.append(u'Just Registered Credentials')

    
    catalog = QreatureCatalog()
    sm['catalog'] = catalog
    sm.registerUtility(catalog, IQreatureCatalog)
    text_index = TextIndex(
        interface=ISearchableText,
        field_name='getSearchableText',
        field_callable=True
        )
    catalog[u'fulltext'] = text_index
    
    field_index = FieldIndex(
    interface=IQreatureComment,
        field_name='title',
        field_callable=False
        )
    catalog[u'comments'] = field_index
    
    
    field_index = FieldIndex(
    interface=IQuiz,
        field_name='title',
        field_callable=False
        )
    catalog[u'quizes'] = field_index
    
    field_index = FieldIndex(
    interface=IQreatureFolder,
        field_name='login',
        field_callable=False
        )
    catalog[u'users'] = field_index
    
    captha_explorer = CaptchaExplorer()
    #do not need registration
    sm['captcha_explorer'] = captha_explorer
    
    counter_explorer = CounterExplorer()
    #do not need registration
    sm['counter_explorer'] = counter_explorer
    
    cache_cleaner = CacheCleaner()
    sm['cache_cleaner'] = cache_cleaner
    sm.registerUtility(cache_cleaner, ICacheCleaner)

@adapter(INewQreatureFolderEvent)
def setQreatureFolderUtilities(event):
    """ This is a handler for custom event.
    All object hierarchies and site-level utilities are created here"""
    site = event.object
    sm = site.getSiteManager()
    
    internal_principal = InternalPrincipal(site.login, site.password, u'owner')
    quiz_site = site.__parent__
    quiz_site_manager = quiz_site.getSiteManager()
    quiz_site_pau = quiz_site_manager['pau']
    quiz_site_pf = quiz_site_pau['PrincipalFolder']
    quiz_site_pf.__setitem__(site.__name__, internal_principal)
    
    role = LocalRole(u'Quiz Creator',u'Registerde user, able to create and edit quizes')
    sm['role'] = role
    sm.registerUtility(role, IRole, site.__name__)
    
    role_perm_manager = IRolePermissionManager(site)
    role_perm_manager.grantPermissionToRole("qreature.edit_quiz", site.__name__)
    


@adapter(INewQuizEvent)
def setQuizUtilities(event):
    """ This is a handler for custom event.
    All object hierarchies and site-level utilities are created here"""
    site = event.object
    sm = site.getSiteManager()
    site_intids = IntIds()
    sm['intids'] = site_intids
    sm.registerUtility(site_intids, IQreatureIntIds)
    
    vm_cache = RAMCache()
    sm['VMCache'] = vm_cache
    sm.registerUtility(vm_cache, IVMCache)
    
    
    #slot quiz for the first time
    alsoProvides(site, IScaleQuiz)
    
    


    
@adapter(IAuthenticatedPrincipalCreated)
def grantRoleToQuizEditor(event):
    """"""
    pau = event.authentication
    sm = pau.__parent__
    site = sm.__parent__
    print "this is a site"
    print site
    if IQreatureSite.providedBy(site):
        quiz_folder_name = unicode((event.info.id).split('qreature').pop())    
        print "this is a folder name"
        print quiz_folder_name
        editor_role = getUtility(IRole, quiz_folder_name, site[quiz_folder_name])
        print "this is a role"
        print editor_role
        princ_role_manager = IPrincipalRoleManager(site[quiz_folder_name])
        princ_role_manager.assignRoleToPrincipal(editor_role.id, event.info.id)
        princ_perm = IPrincipalPermissionManager(site)
        princ_perm.grantPermissionToPrincipal('qreature.idle_perm', event.principal.id)
        print "this is a princ_role_manager"
        print princ_role_manager
        print "princ_perm"
        print princ_perm


            



        
@adapter(IQreatureFolder,IObjectRemovedEvent)
def cleanPrincipal(folder, event):
    site = folder.__parent__
    sm = site.getSiteManager()
    pf = sm['pau']['PrincipalFolder']
    pf.__delitem__(str(folder.login))
    
@adapter(IQreatureFolder,IObjectModifiedEvent)
def changePassword(folder,event):
    site = folder.__parent__
    sm = removeSecurityProxy(site.getSiteManager())
    pau = sm['pau']
    pf = pau['PrincipalFolder']
    principal = pf[folder.login]
    principal.password = folder.password   

@adapter(ICacheCleaner , IObjectAddedEvent)
def init_cache_cleaner(cleaner,event):
    cleaner.init()
    
    


#The below are 2 handlers, which I use to register objects by my IntId utility and index
#them in Catalog.
#The purpose of this stupid idea: to register objects and index them only with nearest IntId utility
#The only way to do it is override IIntIds interface with IQreatureIntIds and register IntId utility
#under this interface.
#The handlers below, are copy pasted from zope.app.intid and zope.app.catalog packages
#with the little adjustment: not all IntId utilities are called, but the nearest one   

from zope.location.interfaces import ILocation
from zope.app.keyreference.interfaces import IKeyReference
from zope.event import notify
from zope.app.intid.interfaces import IntIdRemovedEvent


class QreatureIntIdRemovedEvent(IntIdRemovedEvent):
    implements(IQreatureIntIdRemovedEvent)

@adapter(ILocation, IObjectRemovedEvent)
def removeQreatureIntIdSubscriber(ob, event):
    """A subscriber to ObjectRemovedEvent
    Removes the unique ids registered for the object in Only one!
    id utility.
    """
    #the trick here is to use not the ob, but the ob.__parent__
    #if ob is inside the site: thats ok
    #if ob is site itself: it is registered in the above site
    #thats why i use ob.__parent__ here
    int_id = queryUtility(IQreatureIntIds, context=ob.__parent__)
    if int_id is None: return
    key = IKeyReference(ob, None)
    # Register only objects that adapt to key reference
    if key is not None:
        # Do not need notify the catalogs. Only one of them!
        for v in int_id.__parent__.values():
            if IQreatureCatalog.providedBy(v):
                id = int_id.queryId(ob)
                if id is not None:
                    v.unindex_doc(id)
        notify(QreatureIntIdRemovedEvent(ob, event))
        try:
            int_id.unregister(key)
        except KeyError:
            pass


from zope.app.component.interfaces import ISiteManagementFolder
from zope.app.intid.interfaces import IIntIds

@adapter(ILocation, IObjectAddedEvent)
def addQreatureIntIdSubscriber(ob, event):
    """A subscriber to ObjectAddedEvent

    Registers the object added in only one unique id utility and fires
    an event for the catalog.
    """
    int_id = queryUtility(IQreatureIntIds, context=ob)
    if int_id is None: return
    #there are the cases when it is not need to register objects:
    #SiteManagementFolder, IntIds utility
    if IIntIds.providedBy(ob) or ISiteManagementFolder.providedBy(ob):return
    key = IKeyReference(ob, None)
    # Register only objects that adapt to key reference
    if key is not None:
        int_id.register(key)
        # Do not need to notify the catalogs only one of them if it is in same site_manager.
        for v in int_id.__parent__.values():
            if IQreatureCatalog.providedBy(v):
                v.index_doc(int_id.getId(ob), ob)
            

def qreatureReindexDocSubscriber(event):
    """A subscriber to ObjectModifiedEvent"""
    ob = event.object
    cat =queryUtility(IQreatureCatalog, context=ob)
    if cat is None: return
    int_id = getUtility(IQreatureIntIds, context=ob)
    if cat.__parent__ is int_id.__parent__:
        id = int_id.queryId(ob)
        if id is not None:
            cat.index_doc(id, ob)

            
@adapter(IQreatureIntIdRemovedEvent)
def removeIdsHolders(event):
    """ some object stores id of another objects. Actually they are:
        leads are storing question ids.
        depends are storing result ids"""
    leads = depends = False
    ob = event.object
    if IQuizQuestion.providedBy(ob):
        leads = True
    if IQuizResult.providedBy(ob):
        depends = True
    
    if not (leads or depends): return   
    
    #this means somewhat deleted outside the quiz
    quiz = getSite()
    if not IQuiz.providedBy(quiz): return
    
    int_ids = getUtility(IQreatureIntIds, context=ob)
    ob_id = int_ids.getId(ob)
    
    
    if leads:
        interface = IAnswerLeads
        attr = 'question_id' 
    if depends:
        interface = IAnswerDepends
        attr = 'result_id'
        
        
    items = [[[l for l in a.values() if interface.providedBy(l)]
                      for a in q.values() if IQuizAnswer.providedBy(a)]
                      for q in quiz.values() if IQuizQuestion.providedBy(q)]
    flatten = getUtility(IQreatureUtility, name="Flatten")
    items = flatten(items)
    
    for item in items:
        if getattr(item, attr) == ob_id:
            #notify(CachedObjectChangedEvent([item]))
            item.__parent__.__delitem__(item.__name__)

from qreature.quiz import AnswerValue
            
@adapter(IQuizAnswer,IObjectAddedEvent)
def addAnswerValue(answer,event):
    value = AnswerValue(u'0')
    answer['value'] = value
    
    
    

@adapter(IQreatureComment,IObjectAddedEvent)
def countComments(object,event):
    ce = getUtility(ICounterExplorer,context=object)
    ce.incrementCounter(object,'comments')

    
@adapter(IQreatureComment,IObjectRemovedEvent)
def discountComments(object,event):
    ce = getUtility(ICounterExplorer,context=object)
    ce.decrementCounter(object,'comments')
