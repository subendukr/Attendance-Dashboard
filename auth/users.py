from __future__ import annotations

from auth.hashing import verify_password
from utils.repository import (
    load_users as repository_load_users,
)


def load_users():
    return repository_load_users()


def find_user(username):
    users = load_users()
    return users[users["Username"] == username]


def user_exists(username):
    return not find_user(username).empty


def is_active(username):
    users = load_users()
    user = users[users["Username"] == username]
    if user.empty:
        return False
    return bool(user.iloc[0]["Active"])


def authenticate_user(username, password):
    """
    Authenticate a user.

    Returns
    -------
    pandas.Series | None
        Authenticated user record if credentials are valid,
        otherwise None.
    """

    users = load_users()

    user = users[
        users["Username"] == username
    ]

    if user.empty:
        return None

    row = user.iloc[0]

    if not bool(row["Active"]):
        return None

    if not verify_password(
        password,
        row["Password"],
    ):
        return None

    return row


def get_role(username):
    users = load_users()
    user = users[users["Username"] == username]
    if user.empty:
        return None
    return user.iloc[0]["Role"]


def get_name(username):
    users = load_users()
    user = users[users["Username"] == username]
    if user.empty:
        return None
    return user.iloc[0]["Name"]