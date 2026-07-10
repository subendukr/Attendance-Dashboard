"""
Authentication Configuration

Loads role definitions and permissions from
config/roles.json.

This module is responsible only for role and
permission management.
"""

from pathlib import Path
import json


# ==========================================================
# CONFIG PATH
# ==========================================================

CONFIG_FOLDER = Path("config")

ROLES_FILE = CONFIG_FOLDER / "roles.json"


# ==========================================================
# LOAD ROLE CONFIGURATION
# ==========================================================


def load_roles():
    """
    Load role definitions from roles.json.

    Returns
    -------
    dict
        Dictionary containing all role permissions.
    """

    if not ROLES_FILE.exists():
        raise FileNotFoundError(f"Role configuration not found:\n{ROLES_FILE}")

    with open(ROLES_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


# ==========================================================
# GET ALL ROLES
# ==========================================================


def get_roles():
    """
    Return a list of available roles.
    """

    return list(load_roles().keys())


# ==========================================================
# ROLE EXISTS
# ==========================================================


def role_exists(role):
    """
    Check whether a role exists.
    """

    return role in load_roles()


# ==========================================================
# GET ROLE PERMISSIONS
# ==========================================================


def get_permissions(role):
    """
    Return permission dictionary
    for the specified role.

    Parameters
    ----------
    role : str

    Returns
    -------
    dict
    """

    roles = load_roles()

    return roles.get(role, {})


# ==========================================================
# CHECK PERMISSION
# ==========================================================


def has_permission(role, permission):
    """
    Check whether a role has a
    particular permission.

    Example
    -------
    has_permission(
        "Admin",
        "upload"
    )
    """

    permissions = get_permissions(role)

    return permissions.get(permission, False)
