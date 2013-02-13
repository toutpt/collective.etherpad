import time
import logging
from zope import component
from Products.Five.browser import BrowserView
from collective.etherpad.api import IEtherpadLiteClient
from plone.uuid.interfaces import IUUID
from Products.CMFCore.utils import getToolByName
from AccessControl.unauthorized import Unauthorized

logger = logging.getLogger('collective.etherpad')


class EtherpadEditView(BrowserView):
    """Implement etherpad for Archetypes content types"""
    def __init__(self, context, request):
        self.etherpad = None
        self.embed_settings = None
        self.context = context
        self.request = request
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

    def __call__(self):
        self.update()
        return self.index()

    def update(self):
        """
        call checkToken({'apikey': u'PLONEAPIKEY'})
        -> {"code":0,"message":"ok","data":null}

        call createGroupIfNotExistsFor({
            'apikey': u'PLONEAPIKEY',
            'groupMapper': '0c6df6f80afc4ddab8424939ffb7d18d'
        })
        -> {"code":0,"message":"ok","data":{"groupID":"g.aDAO30LjIDJWvyTU"}}

        call createAuthorIfNotExistsFor({
            'authorMapper': 'admin', 'apikey': u'PLONEAPIKEY',
            'name': u'Jean-Michel FRANCOIS'
        })
        -> {"code":0,"message":"ok","data":{"authorID":"a.pocAeG7Fra31WvnO"}}

        call listPads({
            'apikey': u'PLONEAPIKEY', 'groupID': u'g.aDAO30LjIDJWvyTU'
        })
        -> {"code":0,"message":"ok","data":{
            "padIDs":["g.aDAO30LjIDJWvyTU$None"]
        }}

        call listSessionsOfGroup({
            'apikey': u'PLONEAPIKEY', 'groupID': u'g.aDAO30LjIDJWvyTU'
        })
        -> {"code":0,"message":"ok","data":{
            "s.9pNACwCQjSFYwcAF":{
                "groupID":"g.aDAO30LjIDJWvyTU",
                "authorID":"a.pocAeG7Fra31WvnO",
                "validUntil":1360774062
            }
            }}
        setCookie("s.9pNACwCQjSFYwcAF")
        """
        if self.etherpad is None:
            self.etherpad = component.getUtility(IEtherpadLiteClient)
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
            else:
                raise Unauthorized('you must be at least loggedin')
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
            self.padID = '%s?%s' % (self.groupID, self.padName)
            self.etherpad.createGroupPad(
                groupID=self.groupID,
                padName=self.padName,
                text=self.context.Description(),
            )

        #Portal starts the session for the user on the group:
        if not self.validUntil:
            #2 minutes in unix timestamp in seconds
            self.validUntil = str(int(time.time() + 2 * 60))
        if not self.sessionID:
            session = self.etherpad.createSession(
                groupID=self.groupID,
                authorID=self.authorID,
                validUntil=self.validUntil
            )
            if session:
                self.sessionID = session['sessionID']
#            res = self.etherpad.listSessionsOfGroup(groupID=self.groupID)
#            if res['code'] == 1:
#                nres = self.etherpad.createSession(
#                    groupID=self.groupID,
#                    authorID=self.authorID,
#                    validUntil=self.validUntil
#                )
#                self.sessionID = nres['data']['sessionID']
#            else:
#                #TODO: checkvalidUntil is > now
#                if res['data'] is not None:
#                    self.sessionID = res['data'].keys()[0]
#                else:
#                    nres = self.etherpad.createSession(
#                        groupID=self.groupID,
#                        authorID=self.authorID,
#                        validUntil=self.validUntil
#                    )
#                    self.sessionID = nres['data']['sessionID']
            self._addSessionCookie()

        if self.etherpad_iframe_url is None:
            #TODO: made this configuration with language and stuff
            url = "http://collective.etherpad.com/pad/p/%s" % self.padID
            self.etherpad_iframe_url = url

        # TODO: add embed_settings support

    def _addSessionCookie(self):
#        if not self.request.cookies.get("sessionID"):
#            logger.info('set cookie')
#            self.request.response.setCookie(
#                'sessionID', self.sessionID, path="/"
#            )
#            url = self.context.absolute_url() + '/etherpad_view'
#            self.request.response.redirect(url)
        logger.info('setCookie("sessionID", "%s")' % self.sessionID)
        self.request.response.setCookie(
            'sessionID',
            self.sessionID,
            quoted=False,
            path="/pad/",
        )

    def getEtherpadFieldName(self):
        primary = self.context.getPrimaryField()
        if not primary:
            return
        return primary.getName()
