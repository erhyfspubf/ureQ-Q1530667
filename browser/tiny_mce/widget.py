from zope.component import adapter
from qreature.interfaces import IQreatureEditableTextArea
from qreature.skin.interfaces import IQreatureSkin
from z3c.form import widget
from z3c.form.browser.textarea import TextAreaWidget
from z3c.form.interfaces import DISPLAY_MODE,INPUT_MODE


"""HTML-Editor Widget using TinyMCE

$Id: widget.py 74087 2007-04-10 12:56:29Z dobe $
"""
__docformat__ = "reStructuredText"

try:
    from zc import resourcelibrary
    haveResourceLibrary = True
except ImportError:
    haveResourceLibrary = False


template = """%(widget_html)s<script type="text/javascript">
tinyMCE.init({ 
mode : "exact", %(options)s
elements : "%(name)s"
}
);
</script>
"""

OPT_PREFIX="mce_"
OPT_PREFIX_LEN = len(OPT_PREFIX)
MCE_LANGS=[]
import glob
import os

# initialize the language files
for langFile in glob.glob(
    os.path.join(os.path.dirname(__file__),'tiny_mce','langs') + '/??.js'):
    MCE_LANGS.append(os.path.basename(langFile)[:2])
                     

class TinyWidget(TextAreaWidget):


    """A WYSIWYG input widget for editing html which uses tinymce
    editor.

    >>> from zope.publisher.browser import TestRequest
    >>> from zope.schema import Text
    >>> field = Text(__name__='foo', title=u'on')
    >>> request = TestRequest(
    ...     form={'field.foo': u'Hello\\r\\nworld!'})

    By default, only the needed options to MCE are passed to
    the init method.
    
    >>> widget = TinyWidget(field, request)
    >>> print widget()
    <textarea cols="60" id="field.foo" name="field.foo" rows="15" >Hello
    world!</textarea><script type="text/javascript">
    tinyMCE.init({ 
    mode : "exact", 
    elements : "field.foo"
    }
    );
    </script>

    All variables defined on the object which start with ``mce_`` are
    passed to the init method. Python booleans are converted
    automatically to their js counterparts.

    For a complete list of options see:
    http://tinymce.moxiecode.com/tinymce/docs/reference_configuration.html

    >>> widget = TinyWidget(field, request)
    >>> widget.mce_theme="advanced"
    >>> widget.mce_ask=True
    >>> print widget()
    <textarea ...
    tinyMCE.init({
    mode : "exact", ask : true, theme : "advanced", 
    elements : "field.foo"
    }
    );
    </script>

    Also the string literals "true" and "false" are converted to js
    booleans. This is usefull for widgets created by zcml.
    
    >>> widget = TinyWidget(field, request)
    >>> widget.mce_ask='true'
    >>> print widget()
    <textarea ...
    mode : "exact", ask : true,
    ...
    </script>

    Languages are taken from the tiny_mce/langs directory (currently
    only the ones with an iso name are registered).

    >>> print MCE_LANGS
    ['ar', 'ca', 'cs', 'cy', 'da', 'de', 'el', 'en', 'es', 'fa', \
    'fi', 'fr', 'he', 'hu', 'is', 'it', 'ja', 'ko', 'nb', 'nl', \
    'nn', 'pl', 'pt', 'ru', 'si', 'sk', 'sv', 'th', 'tr', 'vi']

    If the language is found it is added to the mce options. To test
    this behaviour we simply set the language directly, even though it
    is a readonly attribute (don't try this at home)

    >>> request.locale.id.language='de'
    >>> print widget()
    <textarea ...
    mode : "exact", ask : true, language : "de", 
    ...
    </script>
    
    """
    
    def render(self):
        if haveResourceLibrary:
            resourcelibrary.need('tiny_mce')
        mceOptions = []
        for k in dir(self):
            if k.startswith(OPT_PREFIX):
                v = getattr(self,k,None)
                v = v==True and 'true' or v==False and 'false' or v
                if v in ['true','false']:
                    mceOptions.append('%s : %s' % (k[OPT_PREFIX_LEN:],v))
                elif v is not None:
                    mceOptions.append('%s : "%s"' % (k[OPT_PREFIX_LEN:],v))
        mceOptions = ', '.join(mceOptions)
        if mceOptions:
            mceOptions += ', '
        if self.request.locale.id.language in MCE_LANGS:
            mceOptions += ('language : "ru",')
        widget_html =  super(TinyWidget,self).render()
        return template % {"widget_html": widget_html,
                           "name": self.name,
                           "options": mceOptions}




@adapter(IQreatureEditableTextArea,IQreatureSkin)
def tinyWidget(field, request):
    """ makes the widget FieldsWidget"""
    return widget.FieldWidget(field,TinyWidget(request))