from zope.publisher.browser import BrowserView
from zope.app.basicskin.standardmacros import StandardMacros as BaseMacros
from zope.app.pagetemplate import ViewPageTemplateFile
from zc import resourcelibrary

class QreatureMacros(BrowserView):
    template = ViewPageTemplateFile('./templates/qreature.pt')
    def __getitem__(self, key):
        resourcelibrary.need('mochikit.Base')
        resourcelibrary.need('mochikit.Iter')
        resourcelibrary.need('mochikit.DOM')
        resourcelibrary.need('mochikit.Style')
        resourcelibrary.need('mochikit.Color')
        resourcelibrary.need('mochikit.Position')
        resourcelibrary.need('mochikit.Visual')
        resourcelibrary.need('skin')
        return self.template.macros[key]



class StandardQreatureMacros(BaseMacros):
    """ """
    macro_pages = ('qreature_macros',)
    
    


class PaidMacros(BrowserView):
    template = ViewPageTemplateFile('./templates/paid.pt')
    def __getitem__(self, key):
        return self.template.macros[key]



class StandardPaidMacros(BaseMacros):
    """ """
    macro_pages = ('paid_macros',)