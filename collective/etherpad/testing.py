from plone.app.testing import *
import collective.etherpad


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
