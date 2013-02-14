

def uninstall(portal, reinstall=False):
    """We uninstall things that are not handles by quickinstaller"""
    if not reinstall:
        # lets remove action on content types
        types = portal.portal_types
        for _type in ('Document', 'News Item', 'Event', 'Topic'):
            _typeinfo = getattr(types, _type, None)
            if _typeinfo:
                action_info = _typeinfo.getActionObject('object/etherpad')
                if action_info:
                    actions = _typeinfo.listActions()
                    indexes = [(a.category, a.id) for a in actions]
                    index = indexes.index(('object', 'etherpad'))
                    _typeinfo.deleteActions((index, ))
