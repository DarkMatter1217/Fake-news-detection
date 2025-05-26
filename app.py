import streamlit as st
import sys
import os
import time

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.auth import setup_authenticator, check_authentication, is_admin, logout_user
from config.database import get_database_engine

# Page configuration
st.set_page_config(
    page_title="Fake News Detector",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize database
get_database_engine()

# Enhanced CSS
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .stApp {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .main-header {
        font-size: 3.5rem;
        font-weight: 700;
        color: #ffffff;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 0 4px 8px rgba(0,0,0,0.3);
    }
    
    .dropdown-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        margin: 2rem 0;
        text-align: center;
    }
    
    .dropdown-title {
        font-size: 2rem;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 1rem;
    }
    
    .login-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 3rem;
        box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        margin: 2rem 0;
    }
    
    .login-header {
        font-size: 2rem;
        font-weight: 600;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 15px;
        padding: 1rem 2rem;
        font-weight: 600;
        font-size: 1.1rem;
        width: 100%;
        margin-top: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
    
    .stSelectbox > div > div > select {
        border-radius: 15px;
        border: 2px solid #667eea;
        padding: 1rem;
        font-size: 1.1rem;
        font-weight: 500;
        background: white;
        color: #2c3e50;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""",
    unsafe_allow_html=True,
)


def main():
    """Main application function"""

    # Only clear authentication on first load, not every time
    if "app_started" not in st.session_state:
        # Clear only authentication, keep other session state
        auth_keys = ["authentication_status", "name", "username"]
        for key in auth_keys:
            if key in st.session_state:
                del st.session_state[key]

        st.session_state["app_started"] = True
        st.session_state["authentication_status"] = None

    # Check if user is already logged in
    is_authenticated, name, username = check_authentication()

    if is_authenticated:
        # User is logged in, show dashboard
        if is_admin():
            show_admin_dashboard()
        else:
            show_user_dashboard()
    else:
        # User not logged in, show login flow
        show_login_flow()


def show_login_flow():
    """Show the login flow: role selection → credentials"""

    # Check if role is selected
    if (
        "selected_role" not in st.session_state
        or st.session_state.selected_role is None
    ):
        show_role_selection()
    else:
        show_login_form()


def show_role_selection():
    """Show role selection dropdown"""

    st.markdown(
        '<h1 class="main-header">🔍 Fake News Detector</h1>', unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown(
            """
        <div class="dropdown-container">
            <div class="dropdown-title">🔑 Select Your Role</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Role selection
        role = st.selectbox(
            "Choose your role:",
            ["Select Role", "👤 User", "👨‍💼 Admin", "💬 Feedback"],
            key="role_selector",
        )

        def set_role():
            if role == "👤 User":
                st.session_state.selected_role = "user"
            elif role == "👨‍💼 Admin":
                st.session_state.selected_role = "admin"
            elif role == "💬 Feedback (No Login)":
                st.session_state.selected_role = "feedback"

        if role != "Select Role":
            st.button("🚀 Continue", key="continue_btn", on_click=set_role)


def show_login_form():
    """Show login form based on selected role"""

    role = st.session_state.get("selected_role")

    if role == "feedback":
        show_feedback_page()
        return

    # Show login form for user or admin
    st.markdown(
        '<h1 class="main-header">🔍 Fake News Detector</h1>', unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        if role == "user":
            st.markdown(
                """
            <div class="login-container">
                <div class="login-header">👤 User Login</div>
            </div>
            """,
                unsafe_allow_html=True,
            )
        else:  # admin
            st.markdown(
                """
            <div class="login-container">
                <div class="login-header">👨‍💼 Admin Login</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        # Setup authentication
        authenticator, config = setup_authenticator()

        if authenticator is None:
            st.error("Authentication system not available")
            return

        try:
            # Show login form
            authenticator.login("main", key=f"{role}_login_form")

            # Handle authentication
            if st.session_state.get("authentication_status") is True:
                # Check if user has correct role
                if role == "admin" and not is_admin():
                    st.error("❌ Admin privileges required!")
                    return

                st.success("✅ Login successful! Redirecting...")
                time.sleep(1)
                st.rerun()

            elif st.session_state.get("authentication_status") is False:
                st.error("❌ Username/password is incorrect")

            elif st.session_state.get("authentication_status") is None:
                # Show credentials
                if role == "user":
                    with st.expander("🎯 Demo User Credentials"):
                        st.info("""
                        **Regular User:**
                        - Username: `testuser`
                        - Password: `test123`
                        
                        **Your Account:**
                        - Username: `Prabhjot`
                        - Password: `prabhjot123`
                        """)
                else:  # admin
                    with st.expander("🎯 Demo Admin Credentials"):
                        st.info("""
                        **Admin User:**
                        - Username: `admin`
                        - Password: `admin123`
                        
                        **Your Admin Account:**
                        - Username: `Prabhjot`
                        - Password: `prabhjot123`
                        """)

        except Exception as e:
            st.error(f"Authentication error: {e}")

    # Back button
    def go_back():
        st.session_state.selected_role = None
        if "authentication_status" in st.session_state:
            del st.session_state.authentication_status

    st.button("🔙 Back to Role Selection", key="back_to_roles", on_click=go_back)


def show_feedback_page():
    """Show feedback page without login"""

    st.markdown(
        '<h1 class="main-header">🔍 Fake News Detector</h1>', unsafe_allow_html=True
    )
    st.markdown("## 💬 Feedback Form")
    st.markdown("Share your thoughts and help us improve our service!")

    try:
        from pages.feedback import show_feedback_form

        show_feedback_form(require_login=False)
    except ImportError:
        st.error("Feedback module not available")

    def go_back_feedback():
        st.session_state.selected_role = None

    st.button(
        "🔙 Back to Role Selection", key="back_from_feedback", on_click=go_back_feedback
    )


def show_user_dashboard():
    """Show user dashboard"""

    st.markdown(
        '<h1 class="main-header">🔍 Fake News Detector</h1>', unsafe_allow_html=True
    )

    # User info and logout
    is_authenticated, name, username = check_authentication()

    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(
            f"""
        <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
            <h3 style="color: white; margin: 0;">👤 Welcome, {name}!</h3>
            <p style="color: rgba(255,255,255,0.8); margin: 0; font-size: 0.9rem;">Role: User</p>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with col2:

        def handle_logout():
            logout_user()
            st.session_state.selected_role = None

        st.button("🚪 Logout", key="user_logout", on_click=handle_logout)

    st.markdown("---")

    # User features
    user_pages = {
        "🔍 Fake News Detector": "fake_news_detector",
        "📰 Current News": "current_news",
        "💬 Feedback": "feedback",
        "📞 Contact Us": "contact",
    }

    selected_page = st.selectbox(
        "Choose a feature:", list(user_pages.keys()), key="user_nav"
    )
    page_key = user_pages[selected_page]

    route_to_page(page_key, require_login=True)


def show_admin_dashboard():
    """Show admin dashboard"""

    st.markdown(
        '<h1 class="main-header">🔍 Fake News Detector - Admin Panel</h1>',
        unsafe_allow_html=True,
    )

    # Admin info and logout
    is_authenticated, name, username = check_authentication()

    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(
            f"""
        <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
            <h3 style="color: white; margin: 0;">👨‍💼 Welcome, {name}!</h3>
            <p style="color: rgba(255,255,255,0.8); margin: 0; font-size: 0.9rem;">Role: Administrator</p>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with col2:

        def handle_admin_logout():
            logout_user()
            st.session_state.selected_role = None

        st.button("🚪 Logout", key="admin_logout", on_click=handle_admin_logout)

    st.markdown("---")

    # Admin features
    admin_pages = {
        "📊 Admin Dashboard": "admin_dashboard",
        "🔍 Fake News Detector": "fake_news_detector",
        "📰 Current News": "current_news",
        "💬 Feedback": "feedback",
        "📞 Contact Us": "contact",
    }

    selected_page = st.selectbox(
        "Choose a feature:", list(admin_pages.keys()), key="admin_nav"
    )
    page_key = admin_pages[selected_page]

    route_to_page(page_key, require_login=True)


def route_to_page(page_key, require_login=True):
    """Route to the appropriate page"""
    try:
        if page_key == "admin_dashboard":
            from pages.admin_dashboard import show_admin_dashboard

            show_admin_dashboard()
        elif page_key == "fake_news_detector":
            from pages.fake_news_detector import show_fake_news_detector

            show_fake_news_detector()
        elif page_key == "current_news":
            from pages.current_news import show_current_news

            show_current_news()
        elif page_key == "feedback":
            from pages.feedback import show_feedback_form

            show_feedback_form(require_login=require_login)
        elif page_key == "contact":
            from pages.contact import show_contact

            show_contact()
    except ImportError as e:
        st.error(f"Page module not found: {e}")
    except Exception as e:
        st.error(f"Error loading page: {e}")


if __name__ == "__main__":
    main()
