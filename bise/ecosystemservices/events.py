import logging

logger = logging.getLogger("bise.ecosystemservices.events")


def handle_checkout_event(event):
    """ Copy local roles from baseline to wc
    """
    original = event.object
    wc = event.working_copy
    # {
    # 'admin': ['Owner'],
    # 'tibi_countryrep': [u'Contributor', u'Reader'],
    # 'tibi_eea_rep': [u'Reviewer', u'Reader'],
    # 'tibi_etc_rep': [u'Editor', u'Reader']
    # }
    # copy all local roles, but filter out local roles

    logger.info("Copying local roles from original to working copy")
    for user, roles in original.__ac_local_roles__.items():
        roles = [r for r in roles if r != 'Owner']
        if roles:
            ex = wc.__ac_local_roles__.get(user, [])
            roles = list(set(roles + ex))
            wc.__ac_local_roles__[user] = roles
            wc._p_changed = True
