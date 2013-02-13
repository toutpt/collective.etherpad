from zope import schema
from zope import interface


class EtherpadSettings(interface.Interface):
    """This is the schema for etherpad service configuration"""

    basepath = schema.ASCIILine(
        title=u"Etherpad PATH",
        default="/pad/",
    )

    apiversion = schema.ASCIILine(
        title=u"Etherpad API PATH",
        default="1.2",
    )

    apikey = schema.TextLine(title=u"API KEY")


class EtherpadEmbedSettings(interface.Interface):
    showLineNumbers = schema.Bool(
        title=u"showLineNumbers",
        default=True,
    )

    showControls = schema.Bool(
        title=u"showControls",
        default=True,
    )

    showChat = schema.Bool(
        title=u"showChat",
        default=True,
    )

    useMonospaceFont = schema.Bool(
        title=u"useMonospaceFont",
        default=False,
    )

    alwaysShowChat = schema.Bool(
        title=u"alwaysShowChat",
        default=True,
    )
