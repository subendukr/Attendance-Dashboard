from io import BytesIO


# ==========================================================
# Export DataFrame to Excel
# ==========================================================


def dataframe_to_excel(df):
    """
    Convert a pandas DataFrame to an Excel file stored
    in memory and return the bytes.

    Parameters
    ----------
    df : pandas.DataFrame

    Returns
    -------
    bytes
    """

    buffer = BytesIO()

    df.to_excel(buffer, index=False, engine="openpyxl")

    return buffer.getvalue()
