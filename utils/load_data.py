import pandas as pd


# ==========================================================
# Load Monthly Dataset
# ==========================================================


def load_monthly():
    from utils.repository import repo

    relative_path = "processed/EmployeeMonthly.xlsx"

    if not repo.storage.exists(relative_path):
        raise FileNotFoundError(
            "Processed monthly dataset not found.\n\n"
            "Please upload and process an attendance report first."
        )

    return repo.storage.load_dataframe(relative_path)


# ==========================================================
# Load Daily Dataset
# ==========================================================


def load_daily():
    from utils.repository import repo

    relative_path = "processed/EmployeeDaily.xlsx"

    if not repo.storage.exists(relative_path):
        raise FileNotFoundError(
            "Processed daily dataset not found.\n\n"
            "Please upload and process an attendance report first."
        )

    df = repo.storage.load_dataframe(relative_path)

    df["Date"] = pd.to_datetime(df["Date"])

    return df
