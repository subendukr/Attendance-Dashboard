import streamlit as st

from utils.validation import validate_file
from utils.company_detector import detect_company
from services.upload_service import upload_service

from utils.repository import (
    ensure_repository,
    save_raw_workbook,
    workbook_exists,
    list_repository,
    add_metadata,
    update_metadata,
    load_metadata,
    delete_workbook,
    remove_metadata,
)
from services.attendance_service import attendance_service

from auth.layout import render_header

from auth.permissions import require_permission

require_permission("upload")


# ==========================================================
# CONSTANTS
# ==========================================================

MONTH_ORDER = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]

# ==========================================================
# INITIALIZE REPOSITORY
# ==========================================================

render_header(title="Neelkamal Steel Industry", subtitle="Attendance Analytics")

ensure_repository()
attendance_service.ensure_ready()

# ==========================================================
# LOAD REPOSITORY
# ==========================================================

repository = list_repository()


# ==========================================================
# SIDEBAR
# ==========================================================

with st.sidebar:
    st.header("📁 Repository")

    if repository:
        for workbook in repository:
            st.write(f"📄 {workbook.name}")

        st.caption(f"Total Repository Files : {len(repository)}")

    else:
        st.info("Repository is empty.")


# ==========================================================
# MULTI-WORKBOOK UPLOADER
# ==========================================================

uploaded_files = st.file_uploader(
    label="Select Attendance Workbook(s)",
    type=[
        "xlsx",
    ],
    accept_multiple_files=True,
    help=(
        "You may upload one or more monthly attendance workbooks in a single operation."
    ),
)


# ==========================================================
# CONTINUE ONLY IF FILES ARE SELECTED
# ==========================================================

if uploaded_files:
    st.success(f"{len(uploaded_files)} workbook(s) selected.")

    st.markdown("### 📂 Selected Workbooks")

    for index, workbook in enumerate(uploaded_files, start=1):
        company = detect_company(workbook.name)

        if company:
            st.success(f"**{index}.** 📄 {workbook.name}")

            st.caption(f"{company['full_name']}")

        else:
            st.error(f"**{index}.** 📄 {workbook.name}")

            st.caption("Unknown company")

    st.info(f"Total Selected : {len(uploaded_files)} workbook(s)")

    # ==========================================================
    # REPOSITORY SYNCHRONIZATION
    # ==========================================================

    st.markdown("### 💾 Repository Synchronization")

    new_files = []

    duplicate_files = []

    for index, workbook in enumerate(uploaded_files, start=1):
        if workbook_exists(workbook.name):
            duplicate_files.append(workbook.name)

            st.info(f"ℹ️ {workbook.name} already exists.")

            continue

        # ------------------------------------------
        # Save workbook
        # ------------------------------------------

        save_raw_workbook(workbook)

        # ------------------------------------------
        # Create upload metadata
        # ------------------------------------------

        add_metadata(
            filename=workbook.name,
            filesize_kb=round(getattr(workbook, "size", 0) / 1024, 2),
            status="Imported",
        )

        new_files.append(workbook.name)

        st.success(f"✅ {workbook.name} added to repository.")

    # ==========================================================
    # RELOAD REPOSITORY
    # ==========================================================

    repository = list_repository()

    # ==========================================================
    # REPOSITORY SUMMARY
    # ==========================================================

    st.info(
        f"""
Repository Files : {len(repository)}

New Files Added : {len(new_files)}

Duplicate Files : {len(duplicate_files)}
"""
    )

    # ==========================================================
    # VALIDATE REPOSITORY
    # ==========================================================

    st.markdown("### ✅ Repository Validation")

    valid_files = []

    invalid_files = []

    for workbook in repository:
        status, message = validate_file(workbook)

        if status:
            valid_files.append(workbook)

            st.success(f"✅ {workbook.name}")

        else:
            invalid_files.append(workbook)

            st.error(f"❌ {workbook.name}")

            st.caption(message)

    # ==========================================================
    # VALIDATION SUMMARY
    # ==========================================================

    st.info(
        f"""
Repository Files : {len(repository)}

Valid Workbooks : {len(valid_files)}

Invalid Workbooks : {len(invalid_files)}
"""
    )

    # ==========================================================
    # CONTINUE ONLY IF VALID WORKBOOKS EXIST
    # ==========================================================

    if not valid_files:
        st.warning("No valid attendance workbooks were found.")

        st.stop()

    # ==========================================================
    # PROCESS REPOSITORY
    # ==========================================================

    st.markdown("### ⚙️ Repository Processing")

    with st.spinner("Processing attendance workbooks..."):
        daily, monthly, summary = upload_service.process_workbooks(valid_files)

    # ==========================================================
    # UPDATE PROCESSING METADATA
    # ==========================================================

    for workbook in summary:
        update_metadata(
            filename=workbook["Filename"],
            employees=workbook["Employees"],
            departments=workbook["Departments"],
            daily_records=workbook["DailyRecords"],
            monthly_records=workbook["MonthlyRecords"],
        )

    # ==========================================================
    # PROCESSING COMPLETE
    # ==========================================================

    st.success(
        f"""
✅ Repository processed successfully.

Workbooks Processed : {len(valid_files)}

Repository Size : {len(repository)}
"""
    )

    st.balloons()

    # ==========================================================
    # IMPORT SUMMARY
    # ==========================================================

    imported_months = [
        month for month in MONTH_ORDER if month in monthly["Month"].astype(str).unique()
    ]

    st.markdown("### 📊 Import Summary")

    st.info(
        f"""
Departments      : {monthly["Department"].nunique()}

Employees        : {monthly["EmpCode"].nunique()}

Repository Files : {len(repository)}

Months Imported  : {", ".join(imported_months)}

Daily Records    : {len(daily):,}

Monthly Records  : {len(monthly):,}
"""
    )

    # ==========================================================
    # IMPORT METRICS
    # ==========================================================

    st.markdown("### 📈 Repository Statistics")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Employees", monthly["EmpCode"].nunique())

    col2.metric("Months", len(imported_months))

    col3.metric("Departments", monthly["Department"].nunique())

    col4.metric("Daily Records", f"{len(daily):,}")

    # ==========================================================
    # MONTHLY DATASET PREVIEW
    # ==========================================================

    st.divider()

    st.subheader("📅 Monthly Dataset Preview")

    monthly_columns = [
        "EmpCode",
        "Name",
        "Department",
        "Designation",
        "Year",
        "Month",
        "Present",
        "Absent",
        "Leave",
        "PaidDays",
        "WorkHrs",
        "OvTim",
    ]

    st.dataframe(monthly[monthly_columns], width="stretch", hide_index=True, height=450)

    # ==========================================================
    # DAILY DATASET PREVIEW
    # ==========================================================

    st.divider()

    st.subheader("🗓 Daily Dataset Preview")

    daily_columns = [
        "EmpCode",
        "Name",
        "Department",
        "Date",
        "Status",
        "Shift",
        "InTime",
        "OutTime",
        "WorkHrs",
        "OTHrs",
    ]

    st.dataframe(daily[daily_columns], width="stretch", hide_index=True, height=350)

# ==========================================================
# UPLOAD HISTORY
# ==========================================================

st.divider()

st.subheader("📜 Upload History")

history = load_metadata()

if history.empty:
    st.info("No upload history available.")

else:
    history = history.sort_values("UploadedOn", ascending=False)

    st.dataframe(history, width="stretch", hide_index=True, height=300)

st.divider()

if st.button("🔄 Rebuild Repository", width="stretch"):
    with st.spinner("Rebuilding repository..."):
        daily, monthly, summary = upload_service.rebuild_repository()

        for workbook in summary:
            update_metadata(
                filename=workbook["Filename"],
                employees=workbook["Employees"],
                departments=workbook["Departments"],
                daily_records=workbook["DailyRecords"],
                monthly_records=workbook["MonthlyRecords"],
            )

    st.success("Repository rebuilt successfully.")

    st.rerun()

# ==========================================================
# REPOSITORY MANAGEMENT
# ==========================================================

st.divider()

st.subheader("🗂 Repository Management")

repository = list_repository()

if repository:
    for workbook in repository:
        col1, col2 = st.columns([8, 1])

        with col1:
            st.write(f"📄 {workbook.name}")

        with col2:
            if st.button("🗑", key=f"delete_{workbook.name}"):
                success, message = delete_workbook(workbook.name)

                if success:
                    remove_metadata(workbook.name)

                    st.success(message)

                    st.rerun()

                else:
                    st.error(message)
