#python
import time
import logging
from urllib import urlencode

#zope
from Acquisition import aq_inner
from zope import component
from zope import interface
from zope import schema
from z3c.form import form, field, button
from zope import i18nmessageid

#cmf
from Products.CMFCore.utils import getToolByName

#plone
from plone.uuid.interfaces import IUUID
from plone.registry.interfaces import IRegistry
from Products.CMFPlone import PloneMessageFactory

#internal
from collective.etherpad.api import HTTPAPI
from collective.etherpad.settings import EtherpadEmbedSettings, EtherpadSettings
from plone.z3cform.layout import FormWrapper

logger = logging.getLogger('collective.etherpad')
_ = i18nmessageid.MessageFactory('collective.etherpad')
_p = PloneMessageFactory


class EtherpadSyncForm(form.Form):
    fields = field.Fields(interface.Interface)

    def __init__(self, context, request):
        super(EtherpadSyncForm, self).__init__(context, request)
        self.etherpad = None
        self.padID = None
        self.field = None

    @button.buttonAndHandler(_p(u"Save"))
    def handleEtherpadToPlone(self, action):
        self.save()

    def save(self):
        #get the content from etherpad
        html = self.etherpad.getHTML(padID=self.padID)
        if html and 'html' in html:
            self.field.set(self.context, html['html'], mimetype='text/html')


class EtherpadEditView(FormWrapper):
    """Implement etherpad for Archetypes content types"""
    form_instance_class = EtherpadSyncForm

    def __init__(self, context, request):
        super(EtherpadEditView, self).__init__(context, request)
        self.context = context
        self.request = request

        self.etherpad = None
        self.embed_settings = None
        self.etherpad_settings = None
        self.portal_state = None
        self.portal_registry = None

        self.field = None
        self.padID = None
        self.padName = None
        self.pads = []

        self.groupMapper = None
        self.groupID = None

        self.authorMapper = None
        self.authorName = None
        self.authorID = None

        self.sessionID = None
        self.validUntil = None

        self.etherpad_iframe_url = None
        self.form_instance = None

    def __call__(self):
        self.update()
        return self.index()

    def update(self):
        if self.portal_state is None:
            self.portal_state = component.getMultiAdapter(
                (self.context, self.request), name=u'plone_portal_state'
            )

        if self.portal_registry is None:
            self.portal_registry = component.getUtility(IRegistry)

        if self.embed_settings is None:
            self.embed_settings = {}
            registry = self.portal_registry
            self.embed_settings = registry.forInterface(EtherpadEmbedSettings)

        if self.etherpad_settings is None:
            registry = self.portal_registry
            self.etherpad_settings = registry.forInterface(EtherpadSettings)

        if self.etherpad is None:
            self.etherpad = HTTPAPI(self.context, self.request)
            self.etherpad.checkToken()
        if self.field is None:
            self.field = self.getEtherpadField()
        if self.padName is None:
            self.padName = IUUID(self.context)
            logger.debug('set padName to %s' % self.padName)

        #Portal maps the internal userid to an etherpad author.
        if self.authorMapper is None:
            mt = getToolByName(self.context, 'portal_membership')
            member = mt.getAuthenticatedMember()
            if member is not None:
                self.authorMapper = member.getId()
                if self.authorName is None:
                    self.authorName = member.getProperty("fullname")
        if self.authorID is None:
            author = self.etherpad.createAuthorIfNotExistsFor(
                authorMapper=self.authorMapper,
                name=self.authorName
            )
            if author:
                self.authorID = author['authorID']

        #Portal maps the internal userid to an etherpad group:
        if self.groupMapper is None:
            self.groupMapper = self.padName
        if self.groupID is None:
            group = self.etherpad.createGroupIfNotExistsFor(
                groupMapper=self.groupMapper
            )
            if group:
                self.groupID = group['groupID']

        #Portal creates a pad in the userGroup
        if self.padID is None:
            self.padID = '%s$%s' % (self.groupID, self.padName)
            self.etherpad.createGroupPad(
                groupID=self.groupID,
                padName=self.padName,
                text=self.context.Description(),
            )

        #Portal starts the session for the user on the group:
        if not self.validUntil:
            #24 hours in unix timestamp in seconds
            self.validUntil = str(int(time.time() + 24 * 60 * 60))
        if not self.sessionID:
            session = self.etherpad.createSession(
                groupID=self.groupID,
                authorID=self.authorID,
                validUntil=self.validUntil
            )
            if session:
                self.sessionID = session['sessionID']
            self._addSessionCookie()

        if self.etherpad_iframe_url is None:
            #TODO: made this configuration with language and stuff
            url = self.portal_state.portal_url()
            basepath = self.etherpad_settings.basepath
            query = {}  # self.embed_settings  # TODO: as dict
            for field in schema.getFields(EtherpadEmbedSettings):
                value = getattr(self.embed_settings, field)
                if value is not None:
                    query[field] = value
            query['lang'] = self.portal_state.language()
            equery = urlencode(query)
            equery = equery.replace('True', 'true').replace('False', 'false')
            url = "%s%sp/%s?%s" % (url, basepath, self.padID, equery)
            self.etherpad_iframe_url = url

        if self.form_instance is None:
            self.form_instance = self.form_instance_class(
                aq_inner(self.context), self.request
            )
            self.form_instance.__name__ = self.__name__
            self.form_instance.etherpad = self.etherpad
            self.form_instance.padID = self.padID
            self.form_instance.field = self.field
            FormWrapper.update(self)

    @property
    def portal(self):
        """To be overloaded in unit tests"""
        if not getattr(self, '_portal', None):
            self._portal = self.portal_state.portal()
        return self._portal

    def _getBasePath(self):
        """In case we are behind a proxy or if VHM remap our
        urls, take care to remap the cookie basepath too"""
        padvpath = "/".join(
            self.request.physicalPathToVirtualPath(
                self.portal.getPhysicalPath()
            )
        )

        padvpath += self.etherpad_settings.basepath
        padvpath = padvpath.replace('//', '/')
        if not padvpath.startswith('/'):
            padvpath = '/' + padvpath
        return padvpath

    def _addSessionCookie(self):
        logger.debug('setCookie("sessionID", "%s")' % self.sessionID)
        self.request.response.setCookie(
            'sessionID',
            self.sessionID,
            quoted=False,
            path=self._getBasePath(),
        )

    def getEtherpadField(self):
        return self.context.getPrimaryField()
