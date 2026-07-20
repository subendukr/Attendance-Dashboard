from io import BytesIO

import pandas as pd


# ==========================================================
# Export DataFrame to Excel
# ==========================================================

def dataframe_to_excel(
    df: pd.DataFrame,
) -> bytes:
    """
    Convert a DataFrame into an Excel workbook
    stored in memory.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame to export.

    Returns
    -------
    bytes
        Excel workbook as bytes.
    """

    buffer = BytesIO()

    df.to_excel(buffer, index=False, engine="openpyxl")

    return buffer.getvalue()

# ==========================================================
# Export DataFrame to CSV
# ==========================================================

def dataframe_to_csv(
    df: pd.DataFrame,
) -> bytes:
    """
    Convert a DataFrame into UTF-8 encoded CSV bytes.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame to export.

    Returns
    -------
    bytes
        CSV file encoded as UTF-8.
    """

    return df.to_csv(index=False).encode("utf-8")