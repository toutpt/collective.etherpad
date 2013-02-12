from zope import schema
from zope import interface


class EtherpadSettings(interface.Interface):
    """This is the schema for etherpad service configuration"""

    uri = schema.ASCIILine(
        title=u"Etherpad URI",
        default="http://localhost:9001/api/1.2/"
    )

    apikey = schema.TextLine(title=u"API KEY")

    #editstate = schema.List()
    #readonlystate = schema.List()


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

    userName = schema.ASCIILine(
        title=u"userName",
        default="unnamed"
    )

    alwaysShowChat = schema.Bool(
        title=u"alwaysShowChat",
        default=False,
    )

    lang = schema.ASCIILine(
        title=u"Lang",
        default="en",
    )
