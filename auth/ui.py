"""
Authentication User Interface
"""

import base64
from pathlib import Path

import streamlit as st

from auth.users import authenticate_user
from auth.session import login, current_name, current_role, current_user


# ==========================================================
# LOGIN BACKGROUND
# ==========================================================

def get_image_base64(image_path):
    """Convert an image file to base64 for CSS background use."""

    image_path = Path(image_path)

    if not image_path.exists():
        return None

    return base64.b64encode(
        image_path.read_bytes()
    ).decode("utf-8")


# ==========================================================
# LOGIN FORM
# ==========================================================

def render_login():

    # ------------------------------------------------------
    # Resolve the image relative to the project root.
    #
    # auth/ui.py
    #      ↓
    # project root
    #      ↓
    # assets/login_cover.png
    # ------------------------------------------------------

    project_root = Path(__file__).resolve().parent.parent

    image_path = project_root / "assets" / "login_cover.png"

    image_base64 = get_image_base64(image_path)

    # ======================================================
    # LOGIN PAGE CSS
    # ======================================================

    if image_base64:

        st.markdown(
            f"""
            <style>

            /* ==================================================
               HIDE STREAMLIT SIDEBAR ON LOGIN PAGE
            ================================================== */

            section[data-testid="stSidebar"] {{
                display: none !important;
            }}

            [data-testid="stSidebarCollapsedControl"] {{
                display: none !important;
            }}


            /* ==================================================
               REMOVE SIDEBAR SPACE
            ================================================== */

            [data-testid="stAppViewContainer"] {{
                margin-left: 0 !important;
                background: transparent !important;
            }}

            [data-testid="stMain"] {{
                background: transparent !important;
            }}


            /* ==================================================
               FULL LOGIN PAGE BACKGROUND
            ================================================== */

            .stApp {{
                min-height: 100vh;

                background-image:
                    linear-gradient(
                        rgba(4, 14, 27, 0.28),
                        rgba(4, 14, 27, 0.28)
                    ),
                    url("data:image/png;base64,{image_base64}");

                /*
                 * The original cover image is a wide
                 * panoramic image.
                 *
                 * "cover" automatically scales it to
                 * fill the available browser viewport.
                 */
                background-size: cover;

                background-position: center center;

                background-repeat: no-repeat;

                background-attachment: fixed;
            }}


            /* ==================================================
               STREAMLIT HEADER
            ================================================== */

            header[data-testid="stHeader"] {{
                background: transparent !important;
            }}


            /* ==================================================
               MAIN CONTENT
            ================================================== */

            .block-container {{
                max-width: 100% !important;

                min-height: 100vh;

                padding-top: 0 !important;

                padding-bottom: 0 !important;

                padding-left: 1rem !important;

                padding-right: 1rem !important;
            }}


            /* ==================================================
               LOGIN LAYOUT
            ================================================== */

            .login-wrapper {{
                width: 100%;

                min-height: 100vh;

                display: flex;

                flex-direction: column;

                align-items: center;

                justify-content: flex-start;
            }}


            /* ==================================================
               LOGIN TITLE
            ================================================== */

            .login-title {{
                text-align: center;

                color: #ffffff;

                font-size: 40px;

                line-height: 1.2;

                font-weight: 700;

                margin-top: 10vh;

                margin-bottom: 28px;

                text-shadow:
                    0 2px 8px rgba(0, 0, 0, 0.75);
            }}


            /* ==================================================
               LOGIN FORM CARD
            ================================================== */

            [data-testid="stForm"] {{
                width: 100%;

                background:
                    rgba(8, 20, 34, 0.84);

                border:
                    1px solid
                    rgba(255, 255, 255, 0.20);

                border-radius: 16px;

                padding:
                    32px 36px 30px 36px;

                box-shadow:
                    0 20px 60px
                    rgba(0, 0, 0, 0.55);

                backdrop-filter: blur(8px);

                -webkit-backdrop-filter: blur(8px);
            }}


            /* ==================================================
               FORM LABELS
            ================================================== */

            [data-testid="stForm"] label {{
                color: #ffffff !important;

                font-weight: 500 !important;
            }}


            /* ==================================================
               INPUT FIELDS
            ================================================== */

            [data-testid="stForm"] input {{
                background-color:
                    rgba(35, 49, 68, 0.90) !important;

                color: #ffffff !important;

                border:
                    1px solid
                    rgba(255, 255, 255, 0.16) !important;

                border-radius: 9px !important;

                min-height: 46px !important;
            }}


            [data-testid="stForm"] input:focus {{
                border-color:
                    #2384ff !important;

                box-shadow:
                    0 0 0 1px
                    #2384ff !important;
            }}


            [data-testid="stForm"] input::placeholder {{
                color:
                    rgba(255, 255, 255, 0.50) !important;
            }}


            /* ==================================================
               LOGIN BUTTON
            ================================================== */

            [data-testid="stFormSubmitButton"] button {{
                width: 100%;

                min-height: 48px;

                border-radius: 8px;

                background:
                    #1683f7;

                color:
                    #ffffff;

                border:
                    none;

                font-size:
                    16px;

                font-weight:
                    600;

                transition:
                    background 0.2s ease;
            }}


            [data-testid="stFormSubmitButton"] button:hover {{
                background:
                    #086ed9;

                color:
                    #ffffff;
            }}


            /* ==================================================
               LOGIN HINT
            ================================================== */

            .login-hint {{
                color:
                    rgba(255, 255, 255, 0.58);

                font-size:
                    13px;

                margin-top:
                    4px;

                margin-bottom:
                    16px;
            }}


            /* ==================================================
               ERROR / SUCCESS MESSAGES
            ================================================== */

            [data-testid="stForm"] .stAlert {{
                margin-top: 10px;
            }}


            /* ==================================================
               DESKTOP LOGIN WIDTH
            ================================================== */

            @media (min-width: 1000px) {{

                [data-testid="stForm"] {{
                    max-width: 560px;

                    margin-left: auto;

                    margin-right: auto;
                }}

            }}


            /* ==================================================
               TABLET
            ================================================== */

            @media (max-width: 999px) {{

                .login-title {{
                    margin-top: 8vh;

                    font-size: 36px;
                }}

                [data-testid="stForm"] {{
                    max-width: 620px;

                    margin-left: auto;

                    margin-right: auto;
                }}

            }}


            /* ==================================================
               MOBILE
            ================================================== */

            @media (max-width: 768px) {{

                .block-container {{
                    padding-left: 0.75rem !important;

                    padding-right: 0.75rem !important;
                }}

                .login-title {{
                    margin-top: 5vh;

                    margin-bottom: 22px;

                    font-size: 30px;
                }}

                [data-testid="stForm"] {{
                    padding:
                        25px 20px 24px 20px;

                    border-radius: 12px;
                }}

                .stApp {{
                    background-position:
                        center center;
                }}

            }}


            /* ==================================================
               VERY SMALL SCREENS
            ================================================== */

            @media (max-width: 480px) {{

                .login-title {{
                    font-size: 21px;

                    margin-top: 4vh;
                }}

                [data-testid="stForm"] {{
                    padding:
                        22px 16px 20px 16px;
                }}

            }}

            </style>
            """,
            unsafe_allow_html=True,
        )

    else:

        st.warning(
            "Login background image not found: "
            "assets/login_cover.png"
        )


    # ==========================================================
    # LOGIN CONTENT
    # ==========================================================

    # Use a centered Streamlit column.
    #
    # Because the sidebar is hidden, this uses the
    # complete browser width.

    left, center, right = st.columns(
        [1, 2, 1]
    )

    with center:

        # ------------------------------------------------------
        # TITLE
        # ------------------------------------------------------

        st.markdown(
            """
            <div class="login-title">
                Attendance Management Dashboard
            </div>
            """,
            unsafe_allow_html=True,
        )


        # ------------------------------------------------------
        # LOGIN FORM
        # ------------------------------------------------------

        with st.form(
            "login_form",
            clear_on_submit=False
        ):

            username = st.text_input(
                "Username",
                placeholder="Enter your username",
            )

            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your password",
            )

            st.markdown(
                """
                <div class="login-hint">
                    Press <b>Enter</b> after entering
                    your password to login.
                </div>
                """,
                unsafe_allow_html=True,
            )

            submitted = st.form_submit_button(
                "Sign In  ↪",
                width="stretch",
            )


            # ==================================================
            # LOGIN VALIDATION
            # ==================================================

            if submitted:

                # --------------------------------------------------
                # USERNAME VALIDATION
                # --------------------------------------------------

                if not username.strip():

                    st.error(
                        "Please enter your username."
                    )

                    return


                # --------------------------------------------------
                # PASSWORD VALIDATION
                # --------------------------------------------------

                if not password:

                    st.error(
                        "Please enter your password."
                    )

                    return


                # --------------------------------------------------
                # AUTHENTICATE USER
                # --------------------------------------------------

                user = authenticate_user(
                    username,
                    password
                )


                # --------------------------------------------------
                # INVALID LOGIN
                # --------------------------------------------------

                if user is None:

                    st.error(
                        "Invalid username or password."
                    )

                    return


                # --------------------------------------------------
                # CREATE LOGIN SESSION
                # --------------------------------------------------

                login(user)


                # --------------------------------------------------
                # SUCCESS
                # --------------------------------------------------

                st.success(
                    f"Welcome {user['Name']}"
                )


                # --------------------------------------------------
                # RELOAD APPLICATION
                # --------------------------------------------------

                st.rerun()


# ==========================================================
# AUTHENTICATION STATUS
# ==========================================================

def render_auth_status():

    st.success(
        "Successfully Signed In"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "User",
            current_user()
        )

    with col2:

        st.metric(
            "Name",
            current_name()
        )

    with col3:

        st.metric(
            "Role",
            current_role()
        )

    st.info(
        "Navigation will be added in the next step."
    )