from __future__ import annotations

import hashlib
import streamlit as st


def _check_credentials(username: str, password: str) -> tuple[bool, str | None]:
    creds = st.secrets.get("credentials", {})
    user_entry = creds.get(username)
    if not user_entry:
        return False, None
    stored_hash = user_entry.get("password_hash")
    role = user_entry.get("role")
    if not stored_hash:
        return False, None
    pw_hash = hashlib.sha256(password.encode()).hexdigest()
    return (pw_hash == stored_hash, role)


def _login_page() -> tuple[str | None, str | None]:
    """Full-page dark banking login screen."""

    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

    .stApp {
        background: #0B0F1A;
        color: #E2E8F0;
    }

    #MainMenu, footer, header { visibility: hidden; }

    /* Centre the login card */
    .block-container {
        max-width: 440px !important;
        padding-top: 8vh !important;
    }

    /* Card */
    .login-card {
        background: #111827;
        border: 1px solid #1E2A3A;
        border-radius: 14px;
        padding: 2.5rem 2.5rem 2rem;
        position: relative;
        overflow: hidden;
    }
    .login-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, #0EA5E9, #6366F1);
    }

    /* Logo block */
    .login-logo {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 1.8rem;
    }
    .login-logo-icon {
        width: 36px; height: 36px;
        background: linear-gradient(135deg, #0EA5E9, #6366F1);
        border-radius: 8px;
        display: flex; align-items: center; justify-content: center;
        font-size: 1rem;
    }
    .login-logo-text {
        font-size: 1rem;
        font-weight: 600;
        color: #F1F5F9;
        letter-spacing: 0.04em;
    }
    .login-logo-sub {
        font-size: 0.68rem;
        color: #475569;
        letter-spacing: 0.1em;
        text-transform: uppercase;
    }

    /* Headings */
    .login-heading {
        font-size: 1.4rem;
        font-weight: 600;
        color: #F1F5F9;
        margin-bottom: 0.3rem;
        letter-spacing: -0.02em;
    }
    .login-sub {
        font-size: 0.82rem;
        color: #475569;
        margin-bottom: 1.8rem;
    }

    /* Field labels */
    .stTextInput label, .stCheckbox label {
        font-size: 0.78rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.06em !important;
        text-transform: uppercase !important;
        color: #64748B !important;
    }

    /* Inputs */
    .stTextInput input {
        background: #0F172A !important;
        border: 1px solid #1E2A3A !important;
        border-radius: 7px !important;
        color: #E2E8F0 !important;
        font-size: 0.9rem !important;
        padding: 0.55rem 0.9rem !important;
        transition: border-color 0.15s;
    }
    .stTextInput input:focus {
        border-color: #0EA5E9 !important;
        box-shadow: 0 0 0 3px rgba(14,165,233,0.12) !important;
    }

    /* Login button */
    .stFormSubmitButton > button {
        width: 100% !important;
        background: linear-gradient(135deg, #0EA5E9, #6366F1) !important;
        color: #fff !important;
        border: none !important;
        border-radius: 8px !important;
        font-size: 0.88rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.05em !important;
        padding: 0.65rem 1rem !important;
        margin-top: 0.5rem !important;
        transition: opacity 0.15s !important;
    }
    .stFormSubmitButton > button:hover { opacity: 0.9 !important; }

    /* Error */
    .stAlert {
        background: #1C0A0A !important;
        border: 1px solid #7F1D1D !important;
        border-left: 3px solid #F43F5E !important;
        border-radius: 7px !important;
        color: #FCA5A5 !important;
        font-size: 0.82rem !important;
    }

    /* Footer note */
    .login-footer {
        text-align: center;
        font-size: 0.72rem;
        color: #334155;
        margin-top: 1.5rem;
        letter-spacing: 0.04em;
    }

    /* Checkbox */
    .stCheckbox > label > div[data-testid="stMarkdownContainer"] p {
        font-size: 0.8rem !important;
        color: #64748B !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="login-card">
        <div class="login-logo">
            <div class="login-logo-icon">📈</div>
            <div>
                <div class="login-logo-text">FixedIncome</div>
                <div class="login-logo-sub">Portfolio Management</div>
            </div>
        </div>
        <div class="login-heading">Welcome back</div>
        <div class="login-sub">Sign in to access your portfolio dashboard</div>
    </div>
    """, unsafe_allow_html=True)

    # Check "remember me" cookie via query params as a lightweight persistence
    remembered_user = st.session_state.get("_remember_user", "")

    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("Username", value=remembered_user, placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="••••••••••")
        remember = st.checkbox("Keep me signed in", value=bool(remembered_user))
        submitted = st.form_submit_button("Sign In →")

        if submitted:
            if not username or not password:
                st.error("Please enter both username and password.")
                return None, None

            ok, role = _check_credentials(username, password)
            if ok:
                st.session_state["auth_user"] = username
                st.session_state["auth_role"] = role
                if remember:
                    st.session_state["_remember_user"] = username
                else:
                    st.session_state.pop("_remember_user", None)
                st.rerun()
            else:
                st.error("Invalid username or password. Please try again.")

    st.markdown("""
    <div class="login-footer">
        Secured · Internal use only · All activity is monitored and logged
    </div>
    """, unsafe_allow_html=True)

    return None, None


def render_sidebar_user_panel() -> None:
    """
    Call this at the TOP of the sidebar in any page that uses require_role().
    Renders a compact user profile card + logout button.
    """
    user = st.session_state.get("auth_user", "")
    role = st.session_state.get("auth_role", "")

    role_color = {"admin": "#F59E0B", "user": "#0EA5E9"}.get(role, "#64748B")
    role_label = role.capitalize() if role else "—"
    initials = "".join(p[0].upper() for p in user.split()[:2]) if user else "?"

    st.markdown(f"""
    <style>
    .user-card {{
        background: #0F172A;
        border: 1px solid #1E2A3A;
        border-radius: 10px;
        padding: 0.9rem 1rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 1.2rem;
    }}
    .user-avatar {{
        width: 34px; height: 34px;
        background: linear-gradient(135deg, #0EA5E9, #6366F1);
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 0.75rem;
        font-weight: 700;
        color: #fff;
        flex-shrink: 0;
    }}
    .user-name {{
        font-size: 0.85rem;
        font-weight: 600;
        color: #E2E8F0;
        line-height: 1.2;
    }}
    .user-role {{
        display: inline-block;
        font-size: 0.63rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: {role_color};
        background: {role_color}18;
        padding: 1px 7px;
        border-radius: 20px;
        margin-top: 2px;
    }}
    </style>
    <div class="user-card">
        <div class="user-avatar">{initials}</div>
        <div>
            <div class="user-name">{user}</div>
            <div class="user-role">{role_label}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("↩  Sign Out", use_container_width=True, key="logout_btn"):
        logout()


def login_widget() -> tuple[str | None, str | None]:
    """Legacy helper — kept for backwards compatibility."""
    if st.session_state.get("auth_user"):
        return st.session_state.get("auth_user"), st.session_state.get("auth_role")
    return _login_page()


def require_role(allowed_roles: list[str]) -> tuple[str, str]:
    user = st.session_state.get("auth_user")
    role = st.session_state.get("auth_role")

    if not user:
        _login_page()
        st.stop()

    if role not in allowed_roles:
        st.markdown("""
        <style>
        .stApp { background: #0B0F1A; color: #E2E8F0; }
        </style>
        """, unsafe_allow_html=True)
        st.error("⛔ Access denied: your role does not have permission to view this page.")
        if st.button("← Back / Logout"):
            logout()
        st.stop()

    return user, role


def logout() -> None:
    for k in ["auth_user", "auth_role"]:
        st.session_state.pop(k, None)
    try:
        st.rerun()
    except Exception:
        st.success("Signed out — please refresh the page.")
        st.stop()