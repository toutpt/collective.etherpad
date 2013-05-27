#python
import json
import logging
from urllib import urlopen, urlencode

#zope
from zope import component
from zope import interface

#plone
from plone.registry.interfaces import IRegistry

#internal
from collective.etherpad.settings import EtherpadSettings
from Products.CMFCore.interfaces._content import ISiteRoot
from zope.component.hooks import getSite

logger = logging.getLogger('collective.etherpad')


class IEtherpadLiteClient(interface.Interface):

    def createGroup():
        """creates a new group

        -> {code: 0, message:"ok", data: {groupID: g.s8oes9dhwrvt0zif}}"""

    def createGroupIfNotExistsFor(groupMapper):
        """this functions helps you to map your application group ids to
        etherpad lite group ids

        -> {code: 0, message:"ok", data: {groupID: g.s8oes9dhwrvt0zif}}
        """

    def deleteGroup(groupID):
        """this functions helps you to map your application group ids to
        etherpad lite group ids

        -> {code: 0, message:"ok", data: null}
           {code: 1, message:"groupID does not exist", data: null}
        """

    def listPads(groupID):
        """returns all pads of this group

        -> {code: 0, message:"ok", data: {padIDs :
                ["g.s8oes9dhwrvt0zif$test", "g.s8oes9dhwrvt0zif$test2"]}
           {code: 1, message:"groupID does not exist", data: null}
        """

    def createGroupPad(groupID, padName, text=""):
        """create a pad in this group

        -> {code: 0, message:"ok", data: null}
           {code: 1, message:"pad does already exist", data: null}
           {code: 1, message:"groupID does not exist", data: null}
        """

    def listAllGroups():
        """list all existing groups

        -> {code: 0, message:"ok",
            data: {groupIDs: ["g.mKjkmnAbSMtCt8eL", "g.3ADWx6sbGuAiUmCy"]}}
           {code: 0, message:"ok", data: {groupIDs: []}}
        """

    def createAuthor(name=None):
        """Create a new author

        -> {code: 0, message:"ok", data: {authorID: "a.s8oes9dhwrvt0zif"}}
        """

    def createAuthorIfNotExistsFor(authorMapper, name=None):
        """this functions helps you to map your application author ids to
        etherpad lite author ids

        -> {code: 0, message:"ok", data: {authorID: "a.s8oes9dhwrvt0zif"}}
        """

    def listPadsOfAuthor(authorID):
        """returns an array of all pads this author contributed to

        -> {code: 0, message:"ok",
            data: {padIDs: [
                "g.s8oes9dhwrvt0zif$test",
                "g.s8oejklhwrvt0zif$foo"
            ]}}
           {code: 1, message:"authorID does not exist", data: null}
        """

    def getAuthorName(authorID):
        """
        Returns the Author Name of the author

        ->{code: 0, message:"ok", data: {authorName: "John McLear"}}

        -> can't be deleted cause this would involve scanning all the pads
           where this author was
        """

    # Sessions can be created between a group and an author. This allows an
    # author to access more than one group. The sessionID will be set as a
    # cookie to the client and is valid until a certain date. The session
    # cookie can also contain multiple comma-seperated sessionIDs,
    # allowing a user to edit pads in different groups at the same time.
    # Only users with a valid session for this group, can access group pads.
    # You can create a session after you authenticated the user at
    # your web application, to give them access to the pads.
    # You should save the sessionID of this session and delete it
    # after the user logged out.

    def createSession(groupID, authorID, validUntil):
        """creates a new session. validUntil is an unix timestamp in seconds

        ->{code: 0, message:"ok", data: {sessionID: "s.s8oes9dhwrvt0zif"}}
          {code: 1, message:"groupID doesn't exist", data: null}
          {code: 1, message:"authorID doesn't exist", data: null}
          {code: 1, message:"validUntil is in the past", data: null}
        """

    def deleteSession(sessionID):
        """deletes a session

        ->{code: 1, message:"ok", data: null}
          {code: 1, message:"sessionID does not exist", data: null}
        """

    def getSessionInfo(sessionID):
        """returns informations about a session

        ->{code: 0, message:"ok", data: {
              authorID: "a.s8oes9dhwrvt0zif",
              groupID: g.s8oes9dhwrvt0zif, validUntil: 1312201246}}
          {code: 1, message:"sessionID does not exist", data: null}
        """

    def listSessionsOfGroup(groupID):
        """returns all sessions of a group

        ->{"code":0,"message":"ok","data":{"s.oxf2ras6lvhv2132":{
                "groupID":"g.s8oes9dhwrvt0zif",
                "authorID":"a.akf8finncvomlqva",
                "validUntil":2312905480}}}
          {code: 1, message:"groupID does not exist", data: null}
        """

    def listSessionsOfAuthor(authorID):
        """returns all sessions of an author

        ->{"code":0,"message":"ok","data":{"s.oxf2ras6lvhv2132":{
               "groupID":"g.s8oes9dhwrvt0zif","authorID":"a.akf8finncvomlqva",
               "validUntil":2312905480}}}
          {code: 1, message:"authorID does not exist", data: null}
        """

    #Pad content can be updated and retrieved through the API

    def getText(padID, rev=None):
        """returns the text of a pad

        ->{code: 0, message:"ok", data: {text:"Welcome Text"}}
          {code: 1, message:"padID does not exist", data: null}
        """

    def setText(padID, text):
        """sets the text of a pad

        ->{code: 0, message:"ok", data: null}
          {code: 1, message:"padID does not exist", data: null}
          {code: 1, message:"text too long", data: null}
        """

    def getHTML(padID, rev=None):
        """returns the text of a pad formatted as HTML

        ->{code: 0, message:"ok", data: {html:"Welcome Text<br>More Text"}}
          {code: 1, message:"padID does not exist", data: null}
        """

    #Chat#

    def getChatHistory(padID, start=None, end=None):
        """returns

        a part of the chat history, when start and end are given
        the whole chat histroy, when no extra parameters are given
        -> {"code":0,"message":"ok","data":{"messages":[
               {"text":"foo","userId":"a.foo","time":1359199533759,
                "userName":"test"},
               {"text":"bar","userId":"a.foo","time":1359199534622,
                "userName":"test"}]}
           }
          {code: 1, message:"start is higher or equal to the current chatHead",
           data: null}
          {code: 1, message:"padID does not exist", data: null}
        """

    def getChatHead(padID):
        """returns the chatHead (last number of the last chat-message)
        of the pad

        {code: 0, message:"ok", data: {chatHead: 42}}
        {code: 1, message:"padID does not exist", data: null}
        """

    #Pad#
    # Group pads are normal pads, but with the name schema GROUPID$PADNAME.
    # A security manager controls access of them and its forbidden for normal
    # pads to include a $ in the name.

    def createPad(padID, text=None):
        """creates a new (non-group) pad. Note that if you need to create a
        group Pad, you should call createGroupPad.

        ->{code: 0, message:"ok", data: null}
          {code: 1, message:"pad does already exist", data: null}
        """

    def getRevisionsCount(padID):
        """returns the number of revisions of this pad

        ->{code: 0, message:"ok", data: {revisions: 56}}
          {code: 1, message:"padID does not exist", data: null}
        """

    def padUsersCount(padID):
        """returns the number of user that are currently editing this pad

        ->{code: 0, message:"ok", data: {padUsersCount: 5}}
        """

    def padUsers(padID):
        """returns the list of users that are currently editing this pad

        ->{code: 0, message:"ok",
           data: {padUsers: [
               {colorId:"#c1a9d9","name":"username1","timestamp":1345228793126,
                "id":"a.n4gEeMLsvg12452n"},
               {"colorId":"#d9a9cd","name":"Hmmm","timestamp":1345228796042,
                "id":"a.n4gEeMLsvg12452n"}]}}
          {code: 0, message:"ok", data: {padUsers: []}}
        """

    def deletePad(padID):
        """deletes a pad

        ->{code: 0, message:"ok", data: null}
          {code: 1, message:"padID does not exist", data: null}
        """

    def getReadOnlyID(padID):
        """returns the read only link of a pad

        ->{code: 0, message:"ok", data: {readOnlyID: "r.s8oes9dhwrvt0zif"}}
          {code: 1, message:"padID does not exist", data: null}
        """

    def setPublicStatus(padID=None, publicStatus=None):
        """sets a boolean for the public status of a pad

        ->{code: 0, message:"ok", data: null}
          {code: 1, message:"padID does not exist", data: null}
        """

    def getPublicStatus(padID=None):
        """return true of false

        ->{code: 0, message:"ok", data: {publicStatus: true}}
          {code: 1, message:"padID does not exist", data: null}
        """

    def setPassword(padID=None, password=None):
        """returns ok or a error message

        ->{code: 0, message:"ok", data: null}
          {code: 1, message:"padID does not exist", data: null}
        """

    def isPasswordProtected(padID=None):
        """
        returns true or false

        ->{code: 0, message:"ok", data: {passwordProtection: true}}
          {code: 1, message:"padID does not exist", data: null}
        """

    def listAuthorsOfPad(padID=None):
        """returns an array of authors who contributed to this pad

        ->{code: 0, message:"ok", data: {authorIDs :
              ["a.s8oes9dhwrvt0zif", "a.akf8finncvomlqva"]
          }
          {code: 1, message:"padID does not exist", data: null}
        """

    def getLastEdited(padID=None):
        """returns the timestamp of the last revision of the pad

        ->{code: 0, message:"ok", data: {lastEdited: 1340815946602}}
          {code: 1, message:"padID does not exist", data: null}
        """

    def sendClientsMessage(padID=None, msg=None):
        """sends a custom message of type msg to the pad

        ->{code: 0, message:"ok", data: {}}
          {code: 1, message:"padID does not exist", data: null}
        """

    def checkToken():
        """returns ok when the current api token is valid

        ->{"code":0,"message":"ok","data":null}
          {"code":4,"message":"no or wrong API Key","data":null}
        """

    def listAllPads():
        """lists all pads on this epl instance

        ->{code: 0, message:"ok", data: ["testPad", "thePadsOfTheOthers"]}
        """


class HTTPAPI(object):
    """implement IEtherpadLiteClient using HTTP API"""
    interface.implements(IEtherpadLiteClient)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.uri = None
        self.apikey = None
        self._registry = None
        self._settings = None
        self._portal_url = None

    def update(self):
        if self._registry is None:
            self._registry = component.getUtility(IRegistry)
        if self._settings is None:
            self._settings = self._registry.forInterface(EtherpadSettings)
        if self._portal_url is None:
            #code stolen to plone.api
            closest_site = getSite()
            if closest_site is not None:
                for potential_portal in closest_site.aq_chain:
                    if ISiteRoot in interface.providedBy(potential_portal):
                        self._portal_url = potential_portal.absolute_url()
        if self.uri is None:
            basepath = self._settings.basepath
            apiversion = self._settings.apiversion
            self.uri = '%s%sapi/%s/' % (self._portal_url, basepath, apiversion)
            logger.debug(self.uri)
        if self.apikey is None:
            self.apikey = self._settings.apikey

    def _get_api(self, method):
        self.update()

        def _callable(**kwargs):
            kwargs['apikey'] = self.apikey
            url = self.uri + method + '?' + urlencode(kwargs)
            logger.debug('call %s(%s)' % (method, kwargs))
            flike = urlopen(url)
            content = flike.read()
            logger.debug('-> %s' % content)
            result = json.loads(content)
            if result['code'] == 0:
                if result['message'] != 'ok':
                    logger.debug('message: %s' % result['message'])
                if 'data' in result:
                    return result['data']
            else:
                logger.error('code = %(code)s, message = %(message)s' % result)

        return _callable

    def __getattribute__(self, name):
        if name in IEtherpadLiteClient.names():
            return self._get_api(name)
        return object.__getattribute__(self, name)
