import pandas as pd


# ==========================================================
# Load Monthly Dataset
# ==========================================================


def load_monthly():
    from utils.repository import repo

    file = repo.storage.resolve("processed", "EmployeeMonthly.xlsx")

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
    from utils.repository import repo

    file = repo.storage.resolve("processed", "EmployeeDaily.xlsx")

    if not file.exists():
        raise FileNotFoundError(
            f"Processed file not found:\n{file}\n\n"
            "Please upload and process an attendance report first."
        )

    df = pd.read_excel(file)

    df["Date"] = pd.to_datetime(df["Date"])

    return df
