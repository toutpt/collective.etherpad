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
        self.archetypes_fieldname = None

    @button.buttonAndHandler(_p(u"Save"))
    def handleEtherpadToPlone(self, action):
        self.save()

    def save(self):
        #get the content from etherpad
        field = self.context.getField(self.archetypes_fieldname)
        html = self.etherpad.getHTML(padID=self.padID)
        if html and 'html' in html:
            field.set(self.context, html['html'], mimetype='text/html')


class EtherpadEditView(FormWrapper):
    """Implement etherpad for Archetypes content types"""

    def __init__(self, context, request):
        super(EtherpadEditView, self).__init__(context, request)
        self.context = context
        self.request = request

        self.etherpad = None
        self.embed_settings = None
        self.etherpad_settings = None
        self.portal_state = None
        self.portal_registry = None

        self.fieldname = None
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
            embed_settings = registry.forInterface(EtherpadEmbedSettings)
            for field in schema.getFields(EtherpadEmbedSettings):
                value = getattr(embed_settings, field)
                if value is not None:
                    self.embed_settings[field] = value

        if self.etherpad_settings is None:
            registry = self.portal_registry
            self.etherpad_settings = registry.forInterface(EtherpadSettings)

        if self.etherpad is None:
            self.etherpad = HTTPAPI(self.context, self.request)
            self.etherpad.checkToken()
        if self.fieldname is None:
            self.fieldname = self.getEtherpadFieldName()
        if self.padName is None:
            self.padName = IUUID(self.context)
            logger.info('set padName to %s' % self.padName)

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
            query['lang'] = self.portal_state.language()
            encoded_query = urlencode(query)
            url = "%s%sp/%s?%s" % (url, basepath, self.padID, encoded_query)
            self.etherpad_iframe_url = url

        if self.form_instance is None:
            self.form_instance = EtherpadSyncForm(
                aq_inner(self.context), self.request
            )
            self.form_instance.__name__ = self.__name__
            self.form_instance.etherpad = self.etherpad
            self.form_instance.padID = self.padID
            self.form_instance.archetypes_fieldname = self.fieldname
            FormWrapper.update(self)

    def _addSessionCookie(self):
        logger.info('setCookie("sessionID", "%s")' % self.sessionID)
        self.request.response.setCookie(
            'sessionID',
            self.sessionID,
            quoted=False,
            path=self.etherpad_settings.basepath,
        )

    def getEtherpadFieldName(self):
        primary = self.context.getPrimaryField()
        if primary:
            return primary.getName()
