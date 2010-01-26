from z3c.form.interfaces import IFormLayer
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.interface import Interface
from zope.viewlet.interfaces import IViewletManager

class ISlotLayer(Interface):
    pass

class IScaleLayer(Interface):
    pass

class ILeadedLayer(Interface):
    pass

class IQreatureSkin(IFormLayer, IDefaultBrowserLayer):
    pass

class IIconSelector(Interface):
    pass


class IPublishedLayer(Interface):
    pass


class ICheckedLayer(Interface):
    pass


class IAdvertLayer(Interface):
    pass

class IQreatureMenuVM(IViewletManager):
    def sort(self, viewlets):
        return sorted(viewlets)
    
class IOpenResultsLayer(Interface):
    pass
class IOpenValuesLayer(Interface):
    pass
    

    
class IQreatureLeftSideBarVM(IViewletManager):
    def sort(self, viewlets):
        return sorted(viewlets)
    
class IQreatureRightSideBarVM(IViewletManager):
    def sort(self, viewlets):
        return sorted(viewlets)
    
class IPaidSkin(IDefaultBrowserLayer, IFormLayer, IPublishedLayer):
    """ This is just to call paid requests via <script> tag"""

