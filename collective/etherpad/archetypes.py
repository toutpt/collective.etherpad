import time
from zope import component
from Products.Five.browser import BrowserView
from collective.etherpad.api import IEtherpadLiteClient
from plone.uuid.interfaces import IUUID
from Products.CMFCore.utils import getToolByName
from AccessControl.unauthorized import Unauthorized


class EtherpadView(BrowserView):
    """Implement etherpad for Archetypes content types"""
    def __init__(self, context, request):
        self.etherpad = None
        self.embed_settings = None
        self.context = context
        self.request = request
        self.fieldname = None
        self.padId = None
        self.pads = []

        self.groupMapper = None
        self.groupID = None

        self.authorMapper = None
        self.authorName = None
        self.authorID = None

        self.sessionID = None
        self.validUntil = None

        self.etherpad_iframe_url = None

    def __call__(self):
        self.update()
        return self.index()

    def update(self):
        if self.etherpad is None:
            self.etherpad = component.getUtility(IEtherpadLiteClient)
            res = self.etherpad.checkToken()
            if res['code'] == 4:
                raise ValueError(res['message'])
        if self.fieldname is None:
            self.fieldname = self.getEtherpadFieldName()
        if self.padId is None:
            self.padID = IUUID(self.context)

        if self.groupMapper is None:
            # here I don't who can collaborate, so we use uuid as group
            self.groupMapper = IUUID(self.context)
        if self.groupID is None:
            res = self.etherpad.createGroupIfNotExistsFor(groupMapper=self.groupMapper)
            if res['code'] == 0 and res['message'] == 'ok':
                self.groupID = res['data']['groupID']

        if self.authorMapper is None:
            mt = getToolByName(self.context, 'portal_membership')
            member = mt.getAuthenticatedMember()
            if member is not None:
                self.authorMapper = member.getId()
                if self.authorName is None:
                    self.authorName = member.getProperty("fullname")
            else:
                raise Unauthorized('you must be at least loggedin')
        if self.authorID is None:
            res = self.etherpad.createAuthorIfNotExistsFor(authorMapper=self.authorMapper,name=self.authorName)
            self.authorID = res['data']['authorID']

        #should we create a new pad ?
        if not self.pads:
            res = self.etherpad.listPads(groupID=self.groupID)
            if res['code'] == 0:
                self.pads = res['data']['padIDs']
            if not self.pads:
                self.etherpad.createGroupPad(groupID=self.groupID, padName=self.padId, text=self.context.Description())

        if not self.validUntil:
            #24 hours in unix timestamp in seconds
            self.validUntil = str(int(time.time() + 86400))
        if not self.sessionID:
            res = self.etherpad.listSessionsOfGroup(groupID=self.groupID)
            if res['code'] == 1:
                nres = self.etherpad.createSession(groupID=self.groupID, authodID=self.authorID, validUntil=self.validUntil)
                self.sessionID = nres['data']['sessionID']
            else:
                #TODO: checkvalidUntil is > now
                if res['data'] is not None:
                    self.sessionID = res['data'].keys()[0]
                else:
                    nres = self.etherpad.createSession(groupID=self.groupID, authorID=self.authorID, validUntil=self.validUntil)
                    self.sessionID = nres['data']['sessionID']
            self._addSessionCookie()

        if self.etherpad_iframe_url is None:
            url = "http://collective.etherpad.com/pad/p/%s" % self.padID
            self.etherpad_iframe_url = url

        # TODO: add embed_settings support

    def _addSessionCookie(self):
        if not self.request.cookies.get("sessionID"):
#            options = {}
#            options['domain'] = "localhost:9001"
            #self.request.response.setCookie('sessionID', self.sessionID)
            self.request.setCookie('sessionID', self.sessionID)
            url = self.context.absolute_url() + '/etherpad_view'
            self.request.response.redirect(url)

    def getEtherpadFieldName(self):
        primary = self.context.getPrimaryField()
        if not primary:
            return
        return primary.getName()
