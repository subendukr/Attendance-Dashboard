import pandas as pd
from pathlib import Path


# ==========================================================
# Load Monthly Dataset
# ==========================================================


def load_monthly():

    file = Path("data/processed/EmployeeMonthly.xlsx")

    if not file.exists():
        raise FileNotFoundError(
            f"Processed file not found:\n{file}\n\n"
            "Please upload and process an attendance report first."
        )

    return pd.read_excel(file)


# ==========================================================
# Load Daily Dataset
# ==========================================================


def load_daily():

    file = Path("data/processed/EmployeeDaily.xlsx")

    if not file.exists():
        raise FileNotFoundError(
            f"Processed file not found:\n{file}\n\n"
            "Please upload and process an attendance report first."
        )

    df = pd.read_excel(file)

    df["Date"] = pd.to_datetime(df["Date"])

    return df
