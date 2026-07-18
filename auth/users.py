from __future__ import annotations

import logging

from auth.hashing import verify_password
from utils.cache import get_users

logger = logging.getLogger(__name__)

def load_users():
    return get_users()


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

    logger.info("Loaded %d users.", len(users))
    logger.info("Usernames: %s", users["Username"].tolist())

    logger.info("Login attempt: '%s'", username)

    user = users[
        users["Username"] == username
    ]

    if user.empty:
        logger.warning("User not found.")
        return None

    logger.info("User found.")

    row = user.iloc[0]

    logger.info("User active: %s", row["Active"])

    if not bool(row["Active"]):
        logger.warning("User is inactive.")
        return None

    password_ok = verify_password(
        password,
        row["Password"],
    )

    logger.info("Password valid: %s", password_ok)

    if not password_ok:
        logger.warning("Password verification failed.")
        return None

    logger.info("Authentication successful.")

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