import unittest2 as unittest
from collective.etherpad.tests import base


class IntegrationTestSetup(base.IntegrationTestCase):
    """We tests the setup (install) of the addons. You should check all
    stuff in profile are well activated (browserlayer, js, content types, ...)
    """

    def test_browserlayer(self):
        from plone.browserlayer import utils
        from collective.etherpad import layer
        self.assertIn(layer.Layer, utils.registered_layers())

    def test_types(self):
        types = self.portal.portal_types
        for _type in ('Document', 'News Item', 'Event', 'Topic'):
            actions = types.listActions(object=_type)
            found = False
            for action in actions:
                if action.id == 'etherpad':
                    found = True
                    self.assertEqual(action.title, 'Etherpad')
                    self.assertEqual(action.category, 'object')
                    self.assertEqual(action.condition, '')
                    self.assertEqual(action.visible, True)
                    self.assertEqual(
                         action.action.text,
                         'string:${object_url}/etherpad_edit'
                    )
                    self.assertEqual(len(action.permissions), 1)
                    self.assertEqual(
                        action.permissions[0], 'Modify portal content'
                    )
            self.assertTrue(found)

    def test_registry(self):
        from collective.etherpad.settings import EtherpadEmbedSettings
        from collective.etherpad.settings import EtherpadSettings
        registry = self.portal.portal_registry
        embed_settings = registry.forInterface(EtherpadEmbedSettings)
        settings = registry.forInterface(EtherpadSettings)

        self.assertEqual(embed_settings.showLineNumbers, True)
        self.assertEqual(embed_settings.showControls, True)
        self.assertEqual(embed_settings.showChat, True)
        self.assertEqual(embed_settings.useMonospaceFont, False)
        self.assertEqual(embed_settings.alwaysShowChat, True)

        self.assertEqual(settings.basepath, '/pad/')
        self.assertEqual(settings.apiversion, '1.2')
        self.assertEqual(settings.apikey, None)


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
