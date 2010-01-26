### -*- coding: utf-8 -*- ############################################
### Author: Ilshad Habibullin, 2008 <astoon.net@gmail.com> ###########
######################################################################


from zope.publisher.browser import BrowserView
from zope.app.security.interfaces import ILogout
from zope.app.security.interfaces import IAuthentication
from zope.app.security.interfaces import IUnauthenticatedPrincipal
from zope.traversing.browser.absoluteurl import absoluteURL
from zope.interface import implements
from zope.component import getUtility
from zope.app.component.hooks import getSite
from qreature.interfaces import IQreatureSite

class Logout(BrowserView):
    
    implements(ILogout)

    def logout(self, dummyNextURL=None):
        request = self.request

        if not IUnauthenticatedPrincipal(request.principal, None):
            auth = getUtility(IAuthentication)
            ILogout(auth).logout(request)
            site = getSite()
            while not IQreatureSite.providedBy(site):
                site = site.__parent__
            site_url = absoluteURL(site, request)

            return request.response.redirect(site_url + '/main.html')

