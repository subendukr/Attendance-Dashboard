import streamlit as st

def render_footer():
    st.markdown("---")
    st.markdown(
        """
<div style="text-align:center; font-size:0.9rem; color:#808080; line-height:1.7;">
    <strong>Designed &amp; Deployed by:</strong> Subendu Kumar (Admin) <br>
    <strong>Support:</strong> +91 7488773716 &nbsp;│&nbsp;
    <a href="mailto:subendu.neelkamal110@gmail.com">
        subendu.neelkamal110@gmail.com
    </a>
</div>
""",
        unsafe_allow_html=True,
    )