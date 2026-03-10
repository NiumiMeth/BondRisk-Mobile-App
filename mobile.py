"""
mobile.py — Shared PWA + mobile-responsive layer for the Bond Portfolio app.

Import and call at the top of each page:
    import mobile
    mobile.inject_pwa_tags(page_title="Bond Portfolio Manager", page_color="#0B0F1A")
    mobile.inject_mobile_css()

For maturity alerts:
    mobile.check_and_alert_maturities(portfolio_df, valuation_date)
"""
from __future__ import annotations

import os
import smtplib
import ssl
from datetime import date, datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import pandas as pd
import streamlit as st


# ── PART 1: PWA META TAGS ────────────────────────────────────────────────────
# Injected into the <head> via st.markdown. Gives iOS/Android the signals needed
# to install the app on the home screen and run it full-screen.

APP_ICONS = {
    # Base64-encoded 192×192 and 512×512 PNGs would go here in production.
    # For Community Cloud we use an emoji favicon as a fallback — the browser
    # will still show the theme colour and title on the splash screen.
    "192": "https://raw.githubusercontent.com/streamlit/streamlit/develop/lib/streamlit/static/favicon.png",
    "512": "https://raw.githubusercontent.com/streamlit/streamlit/develop/lib/streamlit/static/favicon.png",
}

def inject_pwa_tags(
    page_title: str = "Bond Portfolio",
    page_color: str = "#0B0F1A",
    description: str = "Fixed Income Portfolio Manager",
):
    """
    Inject PWA-enabling meta tags so:
    - iOS Safari shows "Add to Home Screen" with correct icon + title + full-screen mode
    - Android Chrome shows the install prompt and themed splash screen
    - Both platforms hide the browser chrome when launched from home screen
    """
    st.markdown(f"""
    <!-- ── PWA Meta Tags ── -->
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="{page_title}">
    <meta name="application-name" content="{page_title}">
    <meta name="theme-color" content="{page_color}">
    <meta name="description" content="{description}">
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover">

    <!-- Apple touch icon (shows on iOS home screen) -->
    <link rel="apple-touch-icon" href="{APP_ICONS['192']}">
    <link rel="apple-touch-icon" sizes="192x192" href="{APP_ICONS['192']}">
    <link rel="apple-touch-icon" sizes="512x512" href="{APP_ICONS['512']}">

    <!-- iOS splash screens (shown while app loads from home screen) -->
    <meta name="apple-mobile-web-app-status-bar-style" content="black">

    <!-- Android manifest inline hint -->
    <meta name="mobile-web-app-capable" content="yes">

    <!-- Prevent phone number detection formatting -->
    <meta name="format-detection" content="telephone=no">

    <!-- Open Graph (looks good when shared via WhatsApp / Slack) -->
    <meta property="og:title" content="{page_title}">
    <meta property="og:description" content="{description}">
    <meta property="og:type" content="website">

    <!-- ── iOS safe-area support (notch / home indicator padding) ── -->
    <style>
    /* Respect iPhone notch and home indicator */
    .block-container {{
        padding-left: max(2.5rem, env(safe-area-inset-left)) !important;
        padding-right: max(2.5rem, env(safe-area-inset-right)) !important;
        padding-bottom: max(4rem, env(safe-area-inset-bottom)) !important;
    }}
    /* Fix Streamlit's own header overlap on iOS full-screen */
    header[data-testid="stHeader"] {{
        padding-top: env(safe-area-inset-top) !important;
    }}
    </style>
    """, unsafe_allow_html=True)


# ── PART 2: MOBILE-RESPONSIVE CSS ────────────────────────────────────────────
# Injected after the page's own theme CSS. Uses media queries to reflow layout
# for screens narrower than 768px (phones) and 1024px (tablets).

MOBILE_CSS = """
<style>
/* ═══════════════════════════════════════════════════════
   MOBILE RESPONSIVE OVERRIDES
   Breakpoints: 768px = phone, 1024px = tablet
   ═══════════════════════════════════════════════════════ */

/* ── Tablet (≤1024px) ── */
@media screen and (max-width: 1024px) {

    /* KPI grid: 2×2 instead of 1×4 */
    .kpi-grid {
        grid-template-columns: repeat(2, 1fr) !important;
        gap: .75rem !important;
    }

    /* Charts: stack vertically */
    [data-testid="column"] {
        min-width: 100% !important;
    }

    /* Block container less padding */
    .block-container {
        padding: 1rem 1.25rem 3rem !important;
    }

    /* Header: reduce font size */
    .dash-title { font-size: 1.2rem !important; }
    .dash-logo  { font-size: .85rem !important; }
}

/* ── Phone (≤768px) ── */
@media screen and (max-width: 768px) {

    /* KPI grid: single column on very small screens */
    .kpi-grid {
        grid-template-columns: 1fr 1fr !important;
        gap: .5rem !important;
    }
    .kpi-card { padding: .9rem 1rem !important; }
    .kpi-value { font-size: 1rem !important; }
    .kpi-label { font-size: .62rem !important; }

    /* Header: stack vertically */
    .dash-header {
        flex-direction: column !important;
        align-items: flex-start !important;
        gap: .4rem !important;
        padding: 1rem 0 .75rem !important;
    }
    .dash-title { font-size: 1.1rem !important; }

    /* Admin header */
    .admin-header {
        flex-direction: column !important;
        gap: .4rem !important;
    }

    /* Block container: tight padding */
    .block-container {
        padding: .75rem .9rem 5rem !important;
    }

    /* Sidebar: on mobile Streamlit renders it as a drawer.
       We allow the native Streamlit drawer behaviour on phones
       (override the always-visible CSS only on desktop widths).
       The sidebar open/close button becomes the primary nav. */
    section[data-testid="stSidebar"] {
        transform: unset !important;    /* let Streamlit handle show/hide */
        visibility: visible !important;
        width: 85vw !important;         /* takes most of the screen when open */
        max-width: 320px !important;
        z-index: 999 !important;
    }

    /* Make sidebar toggle button larger and easier to tap */
    [data-testid="collapsedControl"] button,
    button[data-testid="baseButton-header"] {
        min-width: 44px !important;
        min-height: 44px !important;
    }

    /* Tabs: smaller text, scrollable */
    .stTabs [data-baseweb="tab-list"] {
        overflow-x: auto !important;
        -webkit-overflow-scrolling: touch !important;
        flex-wrap: nowrap !important;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: .75rem !important;
        padding: .5rem .8rem !important;
        white-space: nowrap !important;
    }

    /* Tables: horizontal scroll */
    [data-testid="stDataFrameContainer"] {
        overflow-x: auto !important;
        -webkit-overflow-scrolling: touch !important;
    }

    /* Buttons: bigger tap targets */
    .stButton > button,
    .stDownloadButton > button {
        min-height: 44px !important;
        font-size: .85rem !important;
        padding: .6rem 1rem !important;
    }

    /* Number inputs: larger on mobile */
    .stNumberInput input,
    .stTextInput input {
        font-size: 16px !important;   /* prevents iOS auto-zoom on focus */
        min-height: 44px !important;
    }

    /* Select boxes */
    .stSelectbox > div > div {
        min-height: 44px !important;
        font-size: 16px !important;
    }

    /* Multiselect */
    .stMultiSelect > div > div {
        font-size: 16px !important;
    }

    /* Date input */
    .stDateInput input {
        font-size: 16px !important;
        min-height: 44px !important;
    }

    /* Charts: ensure they don't overflow */
    .js-plotly-plot {
        max-width: 100% !important;
        overflow: hidden !important;
    }

    /* Metrics: stack */
    [data-testid="metric-container"] {
        padding: .4rem !important;
    }
    [data-testid="stMetricValue"] {
        font-size: 1rem !important;
    }

    /* Upload preview stats */
    .upload-stats-grid {
        grid-template-columns: repeat(3, 1fr) !important;
    }

    /* Section labels */
    .section-label { font-size: .62rem !important; }

    /* Expander headers */
    .streamlit-expanderHeader { font-size: .8rem !important; }

    /* Alert banner */
    .alert-banner { font-size: .76rem !important; padding: .5rem .75rem !important; }

    /* Admin mono labels */
    .info-mono { font-size: .7rem !important; }

    /* Bottom navigation bar (mobile only) */
    .mobile-nav-bar {
        display: flex !important;
    }
}

/* ── Bottom nav bar: hidden on desktop, shown on mobile ── */
.mobile-nav-bar {
    display: none;
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: #080C14;
    border-top: 1px solid #1E2A3A;
    padding: .5rem 0;
    padding-bottom: max(.5rem, env(safe-area-inset-bottom));
    z-index: 1000;
    justify-content: space-around;
    align-items: center;
}
.mobile-nav-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2px;
    color: #475569;
    font-size: .6rem;
    font-weight: 500;
    letter-spacing: .04em;
    text-transform: uppercase;
    min-width: 44px;
    min-height: 44px;
    justify-content: center;
    cursor: pointer;
    border-radius: 8px;
    transition: color .12s;
}
.mobile-nav-item.active { color: #0EA5E9; }
.mobile-nav-item .nav-icon { font-size: 1.1rem; }

/* ── Touch-friendly hover states ── */
@media (hover: none) {
    /* Remove hover effects on touch devices — they get "stuck" */
    .stButton > button:hover { background: #0EA5E9 !important; }
    .nav-link:hover { background: transparent !important; color: #94A3B8 !important; }
}

/* ── Prevent text size adjustment on orientation change ── */
html {
    -webkit-text-size-adjust: 100%;
    text-size-adjust: 100%;
}

/* ── Smooth scrolling ── */
html { scroll-behavior: smooth; }

/* ── Better touch scrolling on iOS ── */
[data-testid="stAppViewContainer"],
[data-testid="stVerticalBlock"] {
    -webkit-overflow-scrolling: touch;
}
</style>
"""

def inject_mobile_css():
    """Inject responsive CSS overrides. Call after the page's own theme CSS."""
    st.markdown(MOBILE_CSS, unsafe_allow_html=True)


def inject_mobile_nav(active_page: str = "portfolio"):
    """
    Render a fixed bottom navigation bar — visible only on mobile screens.
    active_page: 'portfolio' | 'pricer' | 'deepdive'
    """
    pages = [
        ("portfolio", "📊", "Dashboard"),
        ("pricer",    "⚙️",  "Pricer"),
        ("deepdive",  "🔍", "Deep-Dive"),
    ]
    items_html = ""
    for key, icon, label in pages:
        active_cls = "active" if key == active_page else ""
        items_html += f"""
        <div class="mobile-nav-item {active_cls}">
            <span class="nav-icon">{icon}</span>
            <span>{label}</span>
        </div>"""

    st.markdown(f"""
    <div class="mobile-nav-bar">
        {items_html}
    </div>
    """, unsafe_allow_html=True)


# ── PART 3: MATURITY ALERT SYSTEM ────────────────────────────────────────────
# Checks portfolio for bonds maturing within a threshold and sends email alerts.
# Configure via Streamlit secrets or environment variables.
#
# To enable: add to .streamlit/secrets.toml:
#   [alerts]
#   smtp_host     = "smtp.gmail.com"
#   smtp_port     = 587
#   smtp_user     = "your@gmail.com"
#   smtp_password = "your-app-password"
#   alert_to      = "trader@yourbank.com"
#   alert_days    = 30          # alert when maturity within this many days
#   yield_threshold = 0.005    # alert when yield moves more than 50bps

DEFAULT_ALERT_DAYS = 30
YIELD_MOVE_THRESHOLD = 0.005   # 50 bps


def _get_alert_config() -> dict | None:
    """Read alert config from Streamlit secrets or env vars. Returns None if not configured."""
    try:
        cfg = st.secrets.get("alerts", {})
        if cfg.get("smtp_host") and cfg.get("smtp_user") and cfg.get("alert_to"):
            return dict(cfg)
    except Exception:
        pass
    # Fallback to environment variables
    host = os.environ.get("ALERT_SMTP_HOST")
    user = os.environ.get("ALERT_SMTP_USER")
    to   = os.environ.get("ALERT_TO")
    if host and user and to:
        return {
            "smtp_host":     host,
            "smtp_port":     int(os.environ.get("ALERT_SMTP_PORT", 587)),
            "smtp_user":     user,
            "smtp_password": os.environ.get("ALERT_SMTP_PASSWORD", ""),
            "alert_to":      to,
            "alert_days":    int(os.environ.get("ALERT_DAYS", DEFAULT_ALERT_DAYS)),
            "yield_threshold": float(os.environ.get("ALERT_YIELD_THRESHOLD", YIELD_MOVE_THRESHOLD)),
        }
    return None


def _send_email(cfg: dict, subject: str, html_body: str) -> bool:
    """Send an HTML email via SMTP. Returns True on success."""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = cfg["smtp_user"]
        msg["To"]      = cfg["alert_to"]
        msg.attach(MIMEText(html_body, "html"))

        context = ssl.create_default_context()
        with smtplib.SMTP(cfg["smtp_host"], int(cfg["smtp_port"])) as server:
            server.ehlo()
            server.starttls(context=context)
            server.login(cfg["smtp_user"], cfg["smtp_password"])
            server.sendmail(cfg["smtp_user"], cfg["alert_to"], msg.as_string())
        return True
    except Exception as e:
        st.warning(f"Alert email could not be sent: {e}")
        return False


def _build_maturity_email(maturing: pd.DataFrame, alert_days: int, valuation_date) -> str:
    """Build HTML email body for maturity alert."""
    rows_html = ""
    for _, row in maturing.iterrows():
        mat_date  = pd.Timestamp(row["Maturity Date"]).date()
        days_left = (pd.Timestamp(mat_date) - pd.Timestamp(valuation_date)).days
        face      = f"{float(row.get('Maturity Value', 0)):,.0f}"
        isin      = row.get("ISIN", "—")
        deal      = row.get("Deal No.", "—")
        coupon    = f"{float(row.get('Coupon', 0)) * 100:.2f}%" if row.get("Coupon") else "—"
        urgency_color = "#F43F5E" if days_left <= 7 else "#F59E0B" if days_left <= 14 else "#FCD34D"
        rows_html += f"""
        <tr>
            <td style="padding:10px 12px;border-bottom:1px solid #1E2A3A;font-family:monospace;color:#E2E8F0;">{isin}</td>
            <td style="padding:10px 12px;border-bottom:1px solid #1E2A3A;color:#94A3B8;">{deal}</td>
            <td style="padding:10px 12px;border-bottom:1px solid #1E2A3A;color:#94A3B8;">{str(mat_date)}</td>
            <td style="padding:10px 12px;border-bottom:1px solid #1E2A3A;font-weight:600;color:{urgency_color};">{days_left} days</td>
            <td style="padding:10px 12px;border-bottom:1px solid #1E2A3A;color:#E2E8F0;">{face}</td>
            <td style="padding:10px 12px;border-bottom:1px solid #1E2A3A;color:#94A3B8;">{coupon}</td>
        </tr>"""

    total_face = sum(float(r.get("Maturity Value", 0)) for _, r in maturing.iterrows())
    now_str    = datetime.now().strftime("%d %b %Y %H:%M")

    return f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
    <body style="margin:0;padding:0;background:#0B0F1A;font-family:'DM Sans',Arial,sans-serif;">
      <div style="max-width:640px;margin:0 auto;padding:24px 16px;">

        <!-- Header -->
        <div style="background:#111827;border:1px solid #1E2A3A;border-radius:12px;
                    padding:24px 28px;margin-bottom:16px;position:relative;overflow:hidden;">
          <div style="position:absolute;top:0;left:0;right:0;height:3px;
                      background:linear-gradient(90deg,#F59E0B,#EF4444);"></div>
          <div style="display:flex;align-items:center;gap:12px;margin-bottom:8px;">
            <span style="background:rgba(245,158,11,.15);color:#F59E0B;border:1px solid rgba(245,158,11,.3);
                         border-radius:6px;padding:4px 10px;font-size:11px;font-weight:700;
                         letter-spacing:.08em;text-transform:uppercase;">⚠ Maturity Alert</span>
          </div>
          <div style="font-size:20px;font-weight:700;color:#F1F5F9;margin-bottom:4px;">
            {len(maturing)} Bond{'s' if len(maturing) > 1 else ''} Maturing Within {alert_days} Days
          </div>
          <div style="font-size:13px;color:#64748B;">
            Valuation date: {str(valuation_date)} · Alert generated: {now_str}
          </div>
        </div>

        <!-- Summary stats -->
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:16px;">
          <div style="background:#111827;border:1px solid #1E2A3A;border-radius:10px;padding:16px;text-align:center;">
            <div style="font-size:22px;font-weight:700;color:#F1F5F9;font-family:monospace;">{len(maturing)}</div>
            <div style="font-size:11px;color:#475569;text-transform:uppercase;letter-spacing:.08em;margin-top:2px;">Bonds</div>
          </div>
          <div style="background:#111827;border:1px solid rgba(245,158,11,.25);border-radius:10px;padding:16px;text-align:center;">
            <div style="font-size:22px;font-weight:700;color:#F59E0B;font-family:monospace;">{total_face:,.0f}</div>
            <div style="font-size:11px;color:#475569;text-transform:uppercase;letter-spacing:.08em;margin-top:2px;">Total Face Value</div>
          </div>
          <div style="background:#111827;border:1px solid #1E2A3A;border-radius:10px;padding:16px;text-align:center;">
            <div style="font-size:22px;font-weight:700;color:#F43F5E;font-family:monospace;">
              {min((pd.Timestamp(r["Maturity Date"]) - pd.Timestamp(valuation_date)).days for _, r in maturing.iterrows())}
            </div>
            <div style="font-size:11px;color:#475569;text-transform:uppercase;letter-spacing:.08em;margin-top:2px;">Soonest (days)</div>
          </div>
        </div>

        <!-- Table -->
        <div style="background:#111827;border:1px solid #1E2A3A;border-radius:12px;overflow:hidden;margin-bottom:16px;">
          <table style="width:100%;border-collapse:collapse;">
            <thead>
              <tr style="background:#0F172A;">
                <th style="padding:10px 12px;text-align:left;font-size:10px;font-weight:600;
                           letter-spacing:.1em;text-transform:uppercase;color:#475569;">ISIN</th>
                <th style="padding:10px 12px;text-align:left;font-size:10px;font-weight:600;
                           letter-spacing:.1em;text-transform:uppercase;color:#475569;">Deal No.</th>
                <th style="padding:10px 12px;text-align:left;font-size:10px;font-weight:600;
                           letter-spacing:.1em;text-transform:uppercase;color:#475569;">Maturity</th>
                <th style="padding:10px 12px;text-align:left;font-size:10px;font-weight:600;
                           letter-spacing:.1em;text-transform:uppercase;color:#475569;">Days Left</th>
                <th style="padding:10px 12px;text-align:left;font-size:10px;font-weight:600;
                           letter-spacing:.1em;text-transform:uppercase;color:#475569;">Face Value</th>
                <th style="padding:10px 12px;text-align:left;font-size:10px;font-weight:600;
                           letter-spacing:.1em;text-transform:uppercase;color:#475569;">Coupon</th>
              </tr>
            </thead>
            <tbody>{rows_html}</tbody>
          </table>
        </div>

        <!-- Footer -->
        <div style="text-align:center;font-size:11px;color:#334155;padding-top:8px;">
          Bond Portfolio Manager · Automated Alert · Do not reply to this email
        </div>
      </div>
    </body>
    </html>
    """


def check_and_alert_maturities(
    df: pd.DataFrame,
    valuation_date,
    force: bool = False,
) -> list[str]:
    """
    Check portfolio for bonds maturing soon and send an email alert.

    - Only sends once per calendar day per session (cached in session_state).
    - Shows an in-app banner regardless of email config.
    - Returns list of alert messages shown.

    Args:
        df:              Valued portfolio DataFrame (must have Maturity Date, Maturity Value, ISIN).
        valuation_date:  The valuation date (date or Timestamp).
        force:           If True, bypass the once-per-day guard and always send.
    """
    if df is None or df.empty:
        return []

    cfg        = _get_alert_config()
    alert_days = int(cfg["alert_days"]) if cfg else DEFAULT_ALERT_DAYS
    val_ts     = pd.Timestamp(valuation_date)
    today_str  = str(val_ts.date())
    session_key = f"_alert_sent_{today_str}"

    # Find maturing bonds
    try:
        days_to_mat = (pd.to_datetime(df["Maturity Date"]) - val_ts).dt.days
        maturing    = df[days_to_mat.between(0, alert_days)].copy()
    except Exception:
        return []

    messages = []

    if maturing.empty:
        return []

    # ── In-app banner (always shown) ──
    total_face = float(maturing["Maturity Value"].sum())
    min_days   = int((pd.to_datetime(maturing["Maturity Date"]) - val_ts).dt.days.min())
    urgency    = "🔴" if min_days <= 7 else "🟡"
    banner_msg = (
        f"{urgency} **{len(maturing)} bond(s)** maturing within **{alert_days} days** — "
        f"Total face value: **{total_face:,.0f}** · Soonest: **{min_days} days**"
    )
    messages.append(banner_msg)

    # ── Email alert (once per day) ──
    if cfg and (force or not st.session_state.get(session_key)):
        subject   = f"⚠ Maturity Alert — {len(maturing)} bond(s) due within {alert_days} days [{today_str}]"
        html_body = _build_maturity_email(maturing, alert_days, val_ts.date())
        sent      = _send_email(cfg, subject, html_body)
        if sent:
            st.session_state[session_key] = True
            messages.append(f"📧 Alert email sent to {cfg['alert_to']}")

    return messages


def render_alert_banner(messages: list[str]):
    """Render in-app alert banners for each message returned by check_and_alert_maturities."""
    for msg in messages:
        if msg.startswith("📧"):
            st.markdown(
                f'<div style="background:rgba(14,165,233,0.08);border:1px solid rgba(14,165,233,0.2);'
                f'border-left:3px solid #0EA5E9;border-radius:6px;padding:.5rem 1rem;'
                f'font-size:.78rem;color:#7DD3FC;margin-bottom:.5rem;">{msg}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="alert-banner">{msg}</div>',
                unsafe_allow_html=True,
            )


# ── ALERT SETTINGS UI ────────────────────────────────────────────────────────
def render_alert_settings_panel():
    """
    Render an alert configuration panel (for use in admin/settings pages).
    Shows current config status and lets user test the alert.
    """
    cfg = _get_alert_config()
    configured = cfg is not None

    status_color = "#10B981" if configured else "#F59E0B"
    status_text  = "Configured" if configured else "Not configured"
    status_icon  = "✓" if configured else "⚠"

    st.markdown(f"""
    <div style="background:#111827;border:1px solid #1E2A3A;border-radius:10px;
                padding:1.25rem 1.5rem;margin-bottom:1rem;position:relative;overflow:hidden;">
        <div style="position:absolute;top:0;left:0;right:0;height:2px;
                    background:linear-gradient(90deg,#F59E0B,#EF4444);"></div>
        <div style="display:flex;justify-content:space-between;align-items:flex-start;">
            <div>
                <div style="font-size:.68rem;font-weight:600;letter-spacing:.1em;
                            text-transform:uppercase;color:#475569;margin-bottom:.25rem;">Email Alerts</div>
                <div style="font-size:.9rem;color:#E2E8F0;">Maturity &amp; Yield Move Notifications</div>
            </div>
            <div style="background:rgba({('16,185,129' if configured else '245,158,11')},.1);
                        border:1px solid rgba({('16,185,129' if configured else '245,158,11')},.25);
                        border-radius:6px;padding:3px 10px;font-size:.72rem;font-weight:600;
                        color:{status_color};">{status_icon} {status_text}</div>
        </div>
    """, unsafe_allow_html=True)

    if configured:
        st.markdown(f"""
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:.75rem;margin-top:.75rem;">
            <div>
                <div style="font-size:.65rem;color:#475569;text-transform:uppercase;letter-spacing:.08em;">Send To</div>
                <div style="font-family:monospace;color:#94A3B8;font-size:.82rem;margin-top:2px;">{cfg['alert_to']}</div>
            </div>
            <div>
                <div style="font-size:.65rem;color:#475569;text-transform:uppercase;letter-spacing:.08em;">Alert Window</div>
                <div style="font-family:monospace;color:#94A3B8;font-size:.82rem;margin-top:2px;">{cfg.get('alert_days', DEFAULT_ALERT_DAYS)} days</div>
            </div>
            <div>
                <div style="font-size:.65rem;color:#475569;text-transform:uppercase;letter-spacing:.08em;">SMTP Host</div>
                <div style="font-family:monospace;color:#94A3B8;font-size:.82rem;margin-top:2px;">{cfg['smtp_host']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="font-size:.78rem;color:#64748B;margin-top:.6rem;line-height:1.5;">
            To enable email alerts, add an <code>[alerts]</code> section to
            <code>.streamlit/secrets.toml</code>. See the README for the full config schema.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    if configured:
        if st.button("🧪 Send Test Alert Now", use_container_width=True):
            test_df = pd.DataFrame([{
                "ISIN": "TEST000000001", "Deal No.": "TEST-001",
                "Maturity Date": pd.Timestamp(date.today()) + pd.Timedelta(days=5),
                "Maturity Value": 1_000_000, "Coupon": 0.055,
            }])
            msgs = check_and_alert_maturities(test_df, date.today(), force=True)
            if any("📧" in m for m in msgs):
                st.success("Test alert sent successfully.")
            else:
                st.error("Test alert failed — check your SMTP credentials.")
