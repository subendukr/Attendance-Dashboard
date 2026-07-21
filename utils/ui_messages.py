import streamlit as st

def show_no_data_message():
    st.info(
        """
## 📂 No Attendance Data Available

No processed attendance repository exists yet.

### To get started:
Please contact the HR Department to upload the Monthly and Daily Attendance records.

### Contact:
* 📞 +91 7488773716 │ +91 7091210806
* 📧 subendu.neelkamal110@gmail.com │ neelkamal.steels@yahoo.com
"""
    )
    st.stop()