from auth.session import current_company


def is_global_user():
    """
    Returns True for users that can access all companies.
    """
    return current_company() == "ALL"


def show_company_column():
    """
    Company column should only be shown to global users.
    """
    return is_global_user()
