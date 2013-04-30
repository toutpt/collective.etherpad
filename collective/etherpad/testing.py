from plone.app.testing import PloneWithPackageLayer
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting
import collective.etherpad


class DexterityLayer(PloneWithPackageLayer):
    def applyProfiles(self, portal):
        self.applyProfile(portal, 'plone.app.contenttypes:default')
        super(DexterityLayer, self).applyProfiles(portal)

    def setUpZCMLFiles(self):
        super(DexterityLayer, self).setUpZCMLFiles()
        import plone.app.contenttypes
        self.loadZCML("configure.zcml", package=plone.app.contenttypes)


FIXTURE = PloneWithPackageLayer(
    zcml_filename="configure.zcml",
    zcml_package=collective.etherpad,
    additional_z2_products=[],
    gs_profile_id='collective.etherpad:default',
    name="collective.etherpad:FIXTURE"
)


INTEGRATION = IntegrationTesting(
    bases=(FIXTURE,), name="collective.etherpad:Integration"
)

FUNCTIONAL = FunctionalTesting(
    bases=(FIXTURE,), name="collective.etherpad:Functional"
)


DEXTERITY_FIXTURE = DexterityLayer(
    zcml_filename="configure.zcml",
    zcml_package=collective.etherpad,
    additional_z2_products=[],
    gs_profile_id='collective.etherpad:default',
    name="collective.etherpad:DxFIXTURE"
)

DEXTERITY_INTEGRATION = IntegrationTesting(
    bases=(DEXTERITY_FIXTURE,), name="collective.etherpad:DxIntegration"
)
