import logging
from Products.DCWorkflow.utils import modifyRolesForPermission
from AccessControl.PermissionMapping import getPermissionMapping


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

    # We grant "Delete objects" permission on the wc, to Contributor, to allow
    # canceling checkouts
    perm = 'Delete objects'
    pm = set(getPermissionMapping(perm, wc, st=tuple))
    pm.add('Contributor')
    modifyRolesForPermission(wc, perm, tuple(pm))
