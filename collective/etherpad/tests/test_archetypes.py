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

    def test_update(self):
        self.view.update()
        self.assertEqual(self.view.fieldname, 'text')
        url = 'http://nohost.com/pad/p/g.aDAO30LjIDJWvyTU$UUID03295830259'
        url += '?lang=fr'
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
        self.assertEqual(session['path'], '/pad/')
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
        self.assertEqual(self.view.fieldname, 'text')
        url = 'http://nohost/plone/pad/p/' + padID
        url += '?lang=en'
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
        self.assertEqual(session['path'], '/pad/')
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
        form.archetypes_fieldname = 'text'
        form.save()

        html = self.document.getText()
        self.assertEqual(html, 'my html')


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
