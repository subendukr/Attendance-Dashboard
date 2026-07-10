"""
Password Hashing Utilities

Provides secure password hashing and verification
using bcrypt.

This module is responsible only for password
security operations.
"""

import bcrypt


# ==========================================================
# PASSWORD HASHING
# ==========================================================


def hash_password(password):
    """
    Generate a bcrypt hash for a password.

    Parameters
    ----------
    password : str

    Returns
    -------
    str
        Encoded bcrypt hash.
    """

    if not isinstance(password, str):
        raise TypeError("Password must be a string.")

    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


# ==========================================================
# PASSWORD VERIFICATION
# ==========================================================


def verify_password(password, password_hash):
    """
    Verify a password against a stored bcrypt hash.

    Parameters
    ----------
    password : str

    password_hash : str

    Returns
    -------
    bool
    """

    if not password or not password_hash:
        return False

    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))

    except Exception:
        return False


# ==========================================================
# HASH VALIDATION
# ==========================================================


def is_bcrypt_hash(value):
    """
    Check whether a string appears to be
    a valid bcrypt hash.

    Parameters
    ----------
    value : str

    Returns
    -------
    bool
    """

    if not isinstance(value, str):
        return False

    return (
        value.startswith("$2a$") or value.startswith("$2b$") or value.startswith("$2y$")
    )


# ==========================================================
# GENERATE HASH (CLI HELPER)
# ==========================================================

if __name__ == "__main__":
    password = input("Enter password: ")

    print()

    print("Password Hash:\n")

    print(hash_password(password))
