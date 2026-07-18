from utils.cache import (
    get_roles as cached_load_roles,
    clear_cache,
)

from utils.repository import (
    save_roles as repository_save_roles,
)


def load_roles():
    """
    Load role definitions from the repository.
    """
    return cached_load_roles()


def save_roles(roles):
    """
    Persist role definitions through the repository.
    """
    result = repository_save_roles(roles)

    clear_cache()

    return result


def get_roles():
    """
    Return a list of available roles.
    """
    return list(load_roles().keys())


def role_exists(role):
    """
    Check whether a role exists.
    """
    return role in load_roles()


def get_permissions(role):
    """
    Return permission dictionary for the specified role.
    """
    roles = load_roles()
    return roles.get(role, {})


def has_permission(role, permission):
    """
    Check whether a role has a particular permission.
    """
    permissions = get_permissions(role)
    return permissions.get(permission, False)