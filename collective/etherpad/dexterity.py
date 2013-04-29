# there are no import of archetypes in .archetypes just the way fields are
# retrieved
from collective.etherpad import archetypes


class EtherpadSyncForm(archetypes.EtherpadSyncForm):

    def save(self):
        #get the content from etherpad
        import pdb;pdb.set_trace()
        field = self.context.getField(self.archetypes_fieldname)
        html = self.etherpad.getHTML(padID=self.padID)
        if html and 'html' in html:
            field.set(self.context, html['html'], mimetype='text/html')


class EtherpadEditView(archetypes.EtherpadEditView):
    """Implement etherpad for Archetypes content types"""

    def getEtherpadFieldName(self):
        import pdb;pdb.set_trace()
        primary = self.context.getPrimaryField()
        if primary:
            return primary.getName()
