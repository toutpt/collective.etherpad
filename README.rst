Introduction
============

This addon integrate etherpad_ into the Plone CMS. It is a way to get 
Collaborating in really real-time on document.

About Etherpad
==============

Etherpad is an Open Source online editor providing collaborative editing
in really real-time powered by Node.js

How to install
==============

This addon can be installed as any other Plone addons. Please follow the
official documentation_.

You must install etherpad-lite and configure it. If you want to deploy it
using buildout you can referer to the provided buildout of this addon
on github. It is important that your etherpad is on the same domain as your
Plone site (using a reserved path) to let cookies working properly and so
your users being authenticated in Plone to be authenticated in etherpad.

How to configure
================

A set of configuration is available on the configuration registry of Plone
(/portal_registry). You should review theses settings and integrate them
in your site policy.

Credits
=======

Companies
---------

|makinacom|_

* `Planet Makina Corpus <http://www.makina-corpus.org>`_
* `Contact Makina Corpus <mailto:python@makina-corpus.org>`_

Authors

* JeanMichel FRANCOIS aka toutpt <toutpt@gmail.com>

.. |makinacom| image:: http://depot.makina-corpus.org/public/logo.gif
.. _makinacom:  http://www.makina-corpus.com
.. _etherpad: http://etherpad.org/
.. _documentation: http://plone.org/documentation/kb/installing-add-ons-quick-how-to

