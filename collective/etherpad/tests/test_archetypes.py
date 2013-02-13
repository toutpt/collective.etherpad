from datetime import datetime
import unittest2 as unittest
from collective.etherpad.tests import base, fake
from collective.etherpad.archetypes import EtherpadEditView


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

    def test_update(self):
        self.view.update()
        self.assertEqual(self.view.fieldname, 'text')
        self.assertEqual(self.view.etherpad_iframe_url, 'http://nohost.com/pad/p/g.aDAO30LjIDJWvyTU?UUID03295830259?lang=fr')
        self.assertEqual(self.view.authorID, 'a.pocAeG7Fra31WvnO')
        self.assertEqual(self.view.groupID, 'g.aDAO30LjIDJWvyTU')
        self.assertEqual(self.view.sessionID, 's.lHo0Q9krIb1OCFOI')
        self.assertEqual(self.view.padID, 'g.aDAO30LjIDJWvyTU?UUID03295830259')
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


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
