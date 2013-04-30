from datetime import datetime
import unittest2 as unittest
from collective.etherpad.tests import base, fake
from collective.etherpad.archetypes import EtherpadEditView, EtherpadSyncForm


class UnitTestArchetypes(base.UnitTestCase):
    """Lets test the api module"""

    def setUp(self):
        super(UnitTestArchetypes, self).setUp()
        self.context = fake.FakeContext()
        self.request = fake.FakeRequest()
        self.view = EtherpadEditView(self.context, self.request)
        self.load_fake()

    def load_fake(self):
        self.view.etherpad = fake.FakeEtherpad()
        self.view.embed_settings = fake.FakeEtherpadEmbedSettings()
        self.view.etherpad_settings = fake.FakeEtherpadSettings()
        self.view.portal_state = fake.FakePortalState()
        self.view.portal_registry = fake.FakeRegistry()
        self.view.padName = 'UUID03295830259'
        self.view.authorMapper = 'toutpt'
        self.view.form_instance = fake.FakeEtherpadSyncForm()
        self.view._portal = fake.FakePortal()

    def test_update(self):
        self.view.update()
        self.assertEqual(self.view.field.getName(), 'text')
        url = 'http://nohost.com/pad/p/g.aDAO30LjIDJWvyTU$UUID03295830259'
        url += '?lang=fr&alwaysShowChat=true&useMonospaceFont=false'
        url += '&showChat=true&showControls=true&showLineNumbers=true'
        self.assertEqual(self.view.etherpad_iframe_url, url)
        self.assertEqual(self.view.authorID, 'a.pocAeG7Fra31WvnO')
        self.assertEqual(self.view.groupID, 'g.aDAO30LjIDJWvyTU')
        self.assertEqual(self.view.sessionID, 's.lHo0Q9krIb1OCFOI')
        self.assertEqual(self.view.padID, 'g.aDAO30LjIDJWvyTU$UUID03295830259')
        validUntil = self.view.validUntil
        self.assertTrue(validUntil.isdigit())
        validUntil_datetime = datetime.fromtimestamp(int(validUntil))
        now = datetime.now()
        self.assertTrue(validUntil_datetime > now)

        cookies = self.view.request.response.cookies
        self.assertIn('sessionID', cookies)
        session = cookies['sessionID']
        self.assertEqual(session['path'], '/plone/pad/')
        self.assertEqual(session['quoted'], False)
        self.assertEqual(session['value'], 's.lHo0Q9krIb1OCFOI')


class IntegrationTestArchetypes(base.IntegrationTestCase):
    """Here we test integration with Plone, not with etherpad"""

    def setUp(self):
        super(IntegrationTestArchetypes, self).setUp()
        self.view = EtherpadEditView(self.document, self.request)
        self.view.etherpad = fake.FakeEtherpad()

    def test_update(self):
        self.view.update()
        #lets check plone related dependencies are well loaded
        self.assertIsNotNone(self.view.portal_state)
        self.assertIsNotNone(self.view.portal_registry)
        self.assertIsNotNone(self.view.embed_settings)
        self.assertIsNotNone(self.view.etherpad_settings)
        self.assertEqual(self.view.authorMapper, 'test_user_1_')
        uid = self.document.UID()
        self.assertEqual(self.view.padName, uid)
        self.assertEqual(self.view.groupMapper, uid)
        padID = 'g.aDAO30LjIDJWvyTU$%s' % uid
        self.assertEqual(self.view.padID, padID)

        #replay the unittest here
        self.assertEqual(self.view.field.getName(), 'text')
        url = 'http://nohost/plone/pad/p/' + padID
        url += '?lang=en&alwaysShowChat=true&useMonospaceFont=false'
        url += '&showChat=true&showControls=true&showLineNumbers=true'
        self.assertEqual(self.view.etherpad_iframe_url, url)
        self.assertEqual(self.view.authorID, 'a.pocAeG7Fra31WvnO')
        self.assertEqual(self.view.groupID, 'g.aDAO30LjIDJWvyTU')
        self.assertEqual(self.view.sessionID, 's.lHo0Q9krIb1OCFOI')
        validUntil = self.view.validUntil
        self.assertTrue(validUntil.isdigit())
        validUntil_datetime = datetime.fromtimestamp(int(validUntil))
        now = datetime.now()
        self.assertTrue(validUntil_datetime > now)

        cookies = self.view.request.response.cookies
        self.assertIn('sessionID', cookies)
        session = cookies['sessionID']
        self.assertEqual(session['path'], '/plone/pad/')
        self.assertEqual(session['quoted'], False)
        self.assertEqual(session['value'], 's.lHo0Q9krIb1OCFOI')

    def test_EtherpadSyncForm(self):
        form = EtherpadSyncForm(self.document, self.request)
        etherpad = fake.FakeEtherpad()
        etherpad.pads['mypad'] = {'html': 'my html'}
        form.padID = 'g.aDAO30LjIDJWvyTU$mypad'
        html = self.document.getText()
        self.assertEqual(html, '')
        form.etherpad = etherpad
        form.padID = 'mypad'
        form.field = self.document.getField('text')
        form.save()

        html = self.document.getText()
        self.assertEqual(html, 'my html')


class VHMIntegrationTestArchetypes(base.IntegrationTestCase):
    """Here we test integration with Plone, not with etherpad"""

    def setUp(self):
        super(VHMIntegrationTestArchetypes, self).setUp()

        def wrapped(*args, **kw):
            sp = getattr(self, 'subpath', None)
            if sp == "/":
                return []
            if sp == "/foo":
                return ["foo"]
            return self.request.old_physicalPathToVirtualPath(
                *args, **kw)
        setattr(self.request,
                'old_physicalPathToVirtualPath',
                self.request.physicalPathToVirtualPath)
        setattr(self.request,
                'physicalPathToVirtualPath',
                wrapped)

    def tearDown(self):
        setattr(self.request,
                'physicalPathToVirtualPath',
                self.request.old_physicalPathToVirtualPath)

    def test_getBasePath(self):
        view = EtherpadEditView(self.document, self.request)
        view.etherpad = fake.FakeEtherpad()
        view.update()
        # plone in mounted on / on the proxy
        self.subpath = '/'
        self.assertEqual(
            view._getBasePath(), '/pad/')
        # plone in mounted on /foo on the proxy
        self.subpath = '/foo'
        self.assertEqual(
            view._getBasePath(), '/foo/pad/')


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
