"""
User Management

Loads users from data/users.csv and performs
user authentication.

This module is responsible only for user
management and authentication.
"""

from pathlib import Path

import pandas as pd

from auth.hashing import verify_password


# ==========================================================
# USER DATABASE
# ==========================================================

DATA_FOLDER = Path("data")

USERS_FILE = DATA_FOLDER / "users.csv"


# ==========================================================
# LOAD USERS
# ==========================================================


def load_users():
    """
    Load all users.

    Returns
    -------
    pandas.DataFrame
    """

    if not USERS_FILE.exists():
        raise FileNotFoundError(f"User database not found:\n{USERS_FILE}")

    users = pd.read_csv(USERS_FILE)

    if "Active" in users.columns:
        users["Active"] = users["Active"].astype(str).str.upper().eq("TRUE")

    return users


# ==========================================================
# FIND USER
# ==========================================================


def find_user(username):
    """
    Find a user by username.

    Returns
    -------
    pandas.Series | None
    """

    users = load_users()

    user = users[users["Username"].str.lower() == str(username).lower()]

    if user.empty:
        return None

    return user.iloc[0]


# ==========================================================
# USER EXISTS
# ==========================================================


def user_exists(username):
    """
    Check whether a username exists.
    """

    return find_user(username) is not None


# ==========================================================
# USER IS ACTIVE
# ==========================================================


def is_active(username):
    """
    Check whether a user is active.
    """

    user = find_user(username)

    if user is None:
        return False

    return bool(user["Active"])


# ==========================================================
# AUTHENTICATE USER
# ==========================================================


def authenticate_user(username, password):
    """
    Authenticate a user.

    Parameters
    ----------
    username : str

    password : str

    Returns
    -------
    pandas.Series | None
    """

    user = find_user(username)

    if user is None:
        return None

    if not user["Active"]:
        return None

    if not verify_password(password, user["Password"]):
        return None

    return user


# ==========================================================
# GET USER ROLE
# ==========================================================


def get_role(username):
    """
    Return user's role.
    """

    user = find_user(username)

    if user is None:
        return None

    return user["Role"]


# ==========================================================
# GET USER NAME
# ==========================================================


def get_name(username):
    """
    Return display name.
    """

    user = find_user(username)

    if user is None:
        return None

    return user["Name"]
