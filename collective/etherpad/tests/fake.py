#FAKE implementation of interfaces
from ZPublisher.tests.testPublish import Request, Response
from zope import interface
from plone.app.textfield import RichText


class FakeModel(interface.Interface):
    text = RichText(title=u"text")


class FakeField(object):
    def __init__(self, context, name):
        self.name = name
        self.context = None

    def getName(self):
        return self.name

    def set(self, context, value, **kwargs):
        setattr(self.context, self.name, value)


class FakeAcquisition(object):
    def __init__(self):
        self.aq_explicit = None


class FakeContext(object):

    def __init__(self):
        self.id = "myid"
        self.title = "a title"
        self.description = "a description"
        self.creators = ["myself"]
        self.date = "a date"
        self.aq_inner = FakeAcquisition()
        self.aq_inner.aq_explicit = self
        self._modified = "modified date"
        self.remoteUrl = ''  # fake Link
        self.text = ""
        self.primary_field = FakeField(self, 'text')
        self.portal_type = "document"

    def getText(self):
        return self.text

    def getId(self):
        return self.id

    def Title(self):
        return self.title

    def Creators(self):
        return self.creators

    def Description(self):
        return self.description

    def Date(self):
        return self.date

    def modified(self):
        return self._modified

    def getPhysicalPath(self):
        return ('/', 'a', 'not', 'existing', 'path')

    def absolute_url(self):
        return "http://nohost.com/" + self.id

    def getPrimaryField(self):
        return self.primary_field


class FakeResponse(Response):
    def __init__(self):
        self.body = ""
        self.cookies = {}

    def setBody(self, a):
        self.body = a

    def setCookie(self, name, value, **kwargs):
        self.cookies[name] = {'value': value}
        self.cookies[name].update(kwargs)


class FakeRequest(Request):
    def __init__(self):
        self.response = FakeResponse()

    def physicalPathToVirtualPath(self, path):
        return path


class FakeRegistry(object):
    def __init__(self):
        self.configuration = {}

    def forInterface(self, schema, check=True, prefix=None):
        class Proxy:
            def __init__(self):
                self.foo = 'bar'
                self.boo = 'far'
        return Proxy()


class FakeEtherpadSettings(object):
    def __init__(self):
        self.basepath = '/pad/'
        self.apiversion = '1.2'
        self.apikey = 'PLONEAPIKEY'


class FakeEtherpadEmbedSettings(object):
    def __init__(self):
        self.showLineNumbers = True
        self.showControls = True
        self.showChat = True
        self.useMonospaceFont = False
        self.alwaysShowChat = True


class FakeEtherpad(object):

    def __init__(self):
        self.pads = {}

    def checkToken(self):
        return True

    def createAuthorIfNotExistsFor(self, authorMapper=None, name=None):
        return {"authorID": "a.pocAeG7Fra31WvnO"}

    def createGroupIfNotExistsFor(self, groupMapper=None):
        return {"groupID": "g.aDAO30LjIDJWvyTU"}

    def createGroupPad(self, groupID=None, padName=None, text=None):
        return

    def createSession(self, groupID=None, authorID=None, validUntil=None):
        return {"sessionID": "s.lHo0Q9krIb1OCFOI"}

    def getHTML(self, padID=None):
        return self.pads.get(padID, None)


class FakePortalState(object):
    def __init__(self):
        self._language = "fr"
        self._portal_url = "http://nohost.com"

    def language(self):
        return self._language

    def portal_url(self):
        return self._portal_url


class FakePortal(object):

    def getPhysicalPath(self):
        return ('plone',)


class FakeEtherpadSyncForm(object):
    def __init__(self):
        self.updated = False

    def index(self):
        return "index"

    def render(self):
        return "render"

    def update(self):
        self.udpated = True


class FakeFTI(object):

    def __init__(self, _schema):
        self.schema = _schema

    def lookupSchema(self):
        return self.schema
