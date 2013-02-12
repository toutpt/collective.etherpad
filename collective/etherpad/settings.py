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
