# there are no import of archetypes in .archetypes just the way fields are
# retrieved
from z3c.form import button
from zope import schema
from collective.etherpad import archetypes
from plone.dexterity.schema import SCHEMA_CACHE
from plone.app.textfield.interfaces import IRichText


class EtherpadSyncForm(archetypes.EtherpadSyncForm):

    def save(self):
        context_schema = SCHEMA_CACHE.get(self.context.portal_type)
        fields = schema.getFields(context_schema)
        for name in fields:
            field = fields[name]
            if IRichText.providedBy(field):
                break

        html = self.etherpad.getHTML(padID=self.padID)
        if html and 'html' in html:
            field.set(self.context, html['html'], mimetype='text/html')


class EtherpadEditView(archetypes.EtherpadEditView):
    """Implement etherpad for Archetypes content types"""
    form_instance_class = EtherpadSyncForm

    def getEtherpadFieldName(self):
        context_schema = SCHEMA_CACHE.get(self.context.portal_type)
        fields = schema.getFields(context_schema)
        for name in fields:
            field = fields[name]
            if IRichText.providedBy(field):
                break
        return name
