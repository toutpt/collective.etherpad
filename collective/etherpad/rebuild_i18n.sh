#!/bin/sh
PRODUCTNAME='collective.etherpad'
I18NDOMAIN=$PRODUCTNAME

# Synchronise the .pot with the templates.
i18ndude rebuild-pot --pot locales/${PRODUCTNAME}.pot --create ${I18NDOMAIN} .
i18ndude rebuild-pot --pot locales/plone.pot --create plone .

# Synchronise the resulting .pot with the .po files
i18ndude sync --pot locales/${PRODUCTNAME}.pot locales/*/LC_MESSAGES/${PRODUCTNAME}.po
i18ndude sync --pot locales/plone.pot locales/*/LC_MESSAGES/plone.po
