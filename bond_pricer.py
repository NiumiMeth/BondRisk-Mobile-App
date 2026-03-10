from __future__ import annotations

from datetime import date
from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile

import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import auth
import mobile

st.set_page_config(
    page_title="Bond Pricer — Admin",
    layout="wide",
    page_icon="⚙️",
    initial_sidebar_state="expanded",
)

auth.require_role(["admin"])

# ── PWA + MOBILE ──────────────────────────────────────────────────────────────
mobile.inject_pwa_tags(
    page_title="Bond Pricer — Admin",
    page_color="#07090F",
    description="Admin Bond Pricer & Yield Shock Analysis",
)
mobile.inject_mobile_css()

# ── ADMIN THEME ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
}

.stApp {
    background: #07090F;
    color: #CBD5E1;
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 2.5rem 4rem; max-width: 1700px; }

/* ── Admin top bar ── */
.admin-bar {
    background: #0D1117;
    border-bottom: 1px solid #1A2332;
    padding: 0.85rem 0;
    margin-bottom: 1.8rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.admin-bar-left {
    display: flex;
    align-items: center;
    gap: 1.2rem;
}
.admin-badge {
    background: #92400E;
    color: #FCD34D;
    font-size: 0.62rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    padding: 3px 10px;
    border-radius: 4px;
    border: 1px solid #B45309;
}
.admin-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.1rem;
    font-weight: 600;
    color: #F1F5F9;
    letter-spacing: -0.01em;
}
.admin-subtitle {
    font-size: 0.72rem;
    color: #475569;
    letter-spacing: 0.04em;
}

/* ── Section headers ── */
.sec-header {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin: 1.6rem 0 0.8rem;
}
.sec-header-line {
    flex: 1;
    height: 1px;
    background: #1A2332;
}
.sec-header-text {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #475569;
    white-space: nowrap;
}
.sec-header-accent {
    width: 6px; height: 6px;
    background: #D97706;
    border-radius: 50%;
    flex-shrink: 0;
}

/* ── KPI cards ── */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0.75rem;
    margin-bottom: 1.5rem;
}
.kpi-card {
    background: #0D1117;
    border: 1px solid #1A2332;
    border-radius: 8px;
    padding: 1.1rem 1.3rem;
    position: relative;
    overflow: hidden;
}
.kpi-card::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #D97706, #92400E);
}
.kpi-label {
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #475569;
    margin-bottom: 0.45rem;
}
.kpi-value {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.4rem;
    font-weight: 500;
    color: #F1F5F9;
    letter-spacing: -0.02em;
    line-height: 1.2;
}
.kpi-delta-pos { font-size: 0.73rem; color: #10B981; margin-top: 0.25rem; }
.kpi-delta-neg { font-size: 0.73rem; color: #F43F5E; margin-top: 0.25rem; }
.kpi-delta-neu { font-size: 0.73rem; color: #475569; margin-top: 0.25rem; }

/* ── Shock control panel ── */
.shock-panel {
    background: #0D1117;
    border: 1px solid #1A2332;
    border-left: 3px solid #D97706;
    border-radius: 8px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1.5rem;
}
.shock-panel-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #D97706;
    margin-bottom: 0.9rem;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent;
    border-bottom: 1px solid #1A2332;
    gap: 0;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #475569;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.75rem;
    font-weight: 500;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    padding: 0.65rem 1.4rem;
    border-bottom: 2px solid transparent;
    border-radius: 0;
}
.stTabs [aria-selected="true"] {
    background: transparent !important;
    color: #FCD34D !important;
    border-bottom: 2px solid #D97706 !important;
}
.stTabs [data-baseweb="tab-panel"] { padding-top: 1.5rem; }

/* ── Inputs ── */
.stNumberInput input, .stTextInput input, .stDateInput input {
    background: #0D1117 !important;
    border: 1px solid #1A2332 !important;
    border-radius: 6px !important;
    color: #E2E8F0 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.88rem !important;
}
.stNumberInput input:focus, .stTextInput input:focus {
    border-color: #D97706 !important;
    box-shadow: 0 0 0 2px rgba(217,119,6,0.15) !important;
}
.stSelectbox > div > div {
    background: #0D1117 !important;
    border: 1px solid #1A2332 !important;
    border-radius: 6px !important;
    color: #E2E8F0 !important;
}
label {
    font-size: 0.72rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    color: #475569 !important;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    background: #0D1117;
    border: 1px dashed #1A2332;
    border-radius: 8px;
}
[data-testid="stFileUploader"]:hover {
    border-color: #D97706;
}

/* ── Buttons ── */
.stButton > button {
    background: #92400E;
    color: #FCD34D;
    border: 1px solid #B45309;
    border-radius: 6px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    padding: 0.5rem 1.2rem;
}
.stButton > button:hover {
    background: #B45309;
    color: #FEF3C7;
}
.stDownloadButton > button {
    background: transparent;
    color: #D97706;
    border: 1px solid #92400E;
    border-radius: 6px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.06em;
}
.stDownloadButton > button:hover {
    background: rgba(217,119,6,0.08);
    color: #FCD34D;
}

/* ── Dataframe ── */
[data-testid="stDataFrameContainer"] {
    background: #0D1117;
    border: 1px solid #1A2332;
    border-radius: 8px;
}

/* ── Metrics ── */
[data-testid="metric-container"] { background: transparent !important; }
[data-testid="metric-container"] label {
    color: #475569 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.65rem !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #F1F5F9 !important;
    font-family: 'IBM Plex Mono', monospace !important;
}
[data-testid="stMetricDelta"] svg { display: none; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #050709 !important;
    border-right: 1px solid #1A2332 !important;
    min-width: 260px !important;
    width: 260px !important;
    transform: none !important;
    visibility: visible !important;
}
section[data-testid="stSidebar"] {
    transform: none !important;
    visibility: visible !important;
}
[data-testid="collapsedControl"] {
    background: #07090F !important;
    border-right: 1px solid #1A2332 !important;
    color: #334155 !important;
}
[data-testid="collapsedControl"]:hover {
    background: #0D1117 !important;
    color: #475569 !important;
}

/* ── Alerts ── */
.stAlert {
    background: #1A1400 !important;
    border: 1px solid #92400E !important;
    border-left: 3px solid #D97706 !important;
    border-radius: 6px !important;
    font-size: 0.82rem !important;
}

/* ── Info box ── */
.info-mono {
    background: #0D1117;
    border: 1px solid #1A2332;
    border-left: 3px solid #3B82F6;
    border-radius: 6px;
    padding: 0.55rem 1rem;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.75rem;
    color: #64748B;
    margin: 0.6rem 0 1rem;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: #07090F; }
::-webkit-scrollbar-thumb { background: #1A2332; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ── CHART THEME ───────────────────────────────────────────────────────────────
ADMIN_CHART = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="IBM Plex Mono", color="#64748B", size=10),
    margin=dict(l=0, r=0, t=32, b=0),
    xaxis=dict(showgrid=False, zeroline=False, color="#334155",
               linecolor="#1A2332", tickfont=dict(size=9)),
    yaxis=dict(showgrid=True, gridcolor="#0F1923", zeroline=False,
               color="#334155", tickfont=dict(size=9)),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#64748B", size=9),
                bordercolor="#1A2332", borderwidth=1),
)

EXPECTED_COLUMNS = [
    "Port. Index", "Instrument", "Deal No.", "ISIN",
    "Initial Inv Date", "Maturity Date", "Coupon",
    "Maturity Value", "YTM", "Yield", "Market value", "Duration",
]

# ── UI HELPERS ────────────────────────────────────────────────────────────────
def sec_header(text: str) -> None:
    st.markdown(f"""
    <div class="sec-header">
        <div class="sec-header-accent"></div>
        <div class="sec-header-text">{text}</div>
        <div class="sec-header-line"></div>
    </div>
    """, unsafe_allow_html=True)

def kpi_card(label, value, delta=None, positive_is_good=True):
    if delta is None:
        delta_html = '<div class="kpi-delta-neu">—</div>'
    else:
        pos = delta >= 0
        good = pos if positive_is_good else not pos
        cls = "kpi-delta-pos" if good else "kpi-delta-neg"
        sign = "+" if pos else ""
        delta_html = f'<div class="{cls}">{sign}{delta:,.2f}</div>'
    return f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {delta_html}
    </div>"""

def fmt(n, d=2): return f"{n:,.{d}f}"

# ── CALCULATIONS (all unchanged) ─────────────────────────────────────────────
def parse_number(value):
    if pd.isna(value): return np.nan
    text = str(value).strip().replace(",", "")
    if text == "": return np.nan
    try: return float(text)
    except ValueError: return np.nan

def parse_rate(value):
    if pd.isna(value): return np.nan
    text = str(value).strip()
    if text == "": return np.nan
    has_percent = "%" in text
    text = text.replace("%", "").replace(",", "")
    try: number = float(text)
    except ValueError: return np.nan
    if has_percent or number > 1: return number / 100.0
    return number

def clean_columns(df):
    df = df.copy()
    df.columns = [str(col).strip() for col in df.columns]
    return df.rename(columns={"Maturity Value ": "Maturity Value"})

def load_portfolio(uploaded_file):
    file_name = uploaded_file.name.lower()
    df = pd.read_csv(uploaded_file) if file_name.endswith(".csv") else pd.read_excel(uploaded_file)
    df = clean_columns(df)
    missing = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError("Missing columns: " + ", ".join(missing))
    df = df[EXPECTED_COLUMNS].copy()
    df = df.dropna(how="all")
    df["ISIN"] = df["ISIN"].astype(str).str.strip()
    df = df[df["ISIN"].notna() & (df["ISIN"] != "") & (df["ISIN"] != "nan")].copy()
    df["Initial Inv Date"] = pd.to_datetime(df["Initial Inv Date"], dayfirst=True, errors="coerce")
    df["Maturity Date"] = pd.to_datetime(df["Maturity Date"], dayfirst=True, errors="coerce")
    for col in ["Maturity Value", "Market value", "Duration"]:
        df[col] = df[col].map(parse_number)
    df["Coupon"] = df["Coupon"].map(parse_rate)
    df["YTM"] = df["YTM"].map(parse_rate)
    df["Yield"] = df["Yield"].map(parse_rate)
    df = df.dropna(subset=["Initial Inv Date", "Maturity Date", "Maturity Value", "Coupon", "YTM", "Yield"])
    return df

def get_future_coupon_dates(maturity_date, valuation_date):
    dates = []
    current = pd.Timestamp(maturity_date).normalize()
    valuation_date = pd.Timestamp(valuation_date).normalize()
    while current > valuation_date:
        dates.append(current)
        current = current - pd.DateOffset(months=6)
    return sorted(dates)

def build_valuation_table(face_value, coupon_rate, annual_yield, maturity_date, valuation_date):
    coupon_dates = get_future_coupon_dates(maturity_date, valuation_date)
    if not coupon_dates:
        empty = pd.DataFrame(columns=["Cash Flow Date","Coupon CF","Principal CF","Total CF","Exponent (n + frac)","Discount Factor","PV"])
        return empty, 0.0, 0.0, 0.0, 0.0
    next_coupon = coupon_dates[0]
    days_to_next_coupon = max((next_coupon - valuation_date).days, 0)

    # Use ACTUAL days in the coupon period (prev_coupon → next_coupon) as denominator
    # This matches the Actual/Actual convention used in excel_price_actual_actual.
    # For semi-annual bonds this is typically 181-184 days, NOT always 182.
    prev_coupon = next_coupon - pd.DateOffset(months=6)
    period_days = (next_coupon - pd.Timestamp(prev_coupon).normalize()).days
    period_days = period_days if period_days > 0 else 182  # fallback safety
    frac = days_to_next_coupon / float(period_days)
    period_coupon = face_value * coupon_rate / 2.0
    rows = []
    dirty_price = 0.0
    for index, cash_date in enumerate(coupon_dates):
        exponent = index + frac
        coupon_cf = period_coupon
        principal_cf = face_value if cash_date == coupon_dates[-1] else 0.0
        total_cf = coupon_cf + principal_cf
        discount_factor = (1 + annual_yield / 2.0) ** exponent
        pv = total_cf / discount_factor
        dirty_price += pv
        rows.append({"Cash Flow Date": cash_date.date(), "Coupon CF": coupon_cf,
                     "Principal CF": principal_cf, "Total CF": total_cf,
                     "Exponent (n + frac)": exponent, "Discount Factor": discount_factor, "PV": pv})
    accrued_interest = period_coupon * (1.0 - frac)
    accrued_interest = max(0.0, min(accrued_interest, period_coupon))
    clean_price = dirty_price - accrued_interest
    return pd.DataFrame(rows), dirty_price, clean_price, accrued_interest, frac

def get_coupon_window(settlement_date, maturity_date, frequency=2):
    months = int(12 / frequency)
    settlement = pd.Timestamp(settlement_date).normalize()
    maturity = pd.Timestamp(maturity_date).normalize()
    if settlement >= maturity:
        raise ValueError("Settlement must be earlier than maturity.")
    next_coupon = maturity
    while True:
        prev_coupon = next_coupon - pd.DateOffset(months=months)
        if prev_coupon <= settlement < next_coupon:
            return prev_coupon, next_coupon
        next_coupon = prev_coupon

def excel_price_actual_actual(settlement_date, maturity_date, coupon_rate, annual_yield, redemption=100.0, frequency=2):
    settlement = pd.Timestamp(settlement_date).normalize()
    maturity = pd.Timestamp(maturity_date).normalize()
    if settlement >= maturity: return 0.0, 0.0, 0.0
    prev_coupon, next_coupon = get_coupon_window(settlement, maturity, frequency)
    e = (next_coupon - prev_coupon).days
    a = (settlement - prev_coupon).days
    dsc = (next_coupon - settlement).days
    if e <= 0: return 0.0, 0.0, 0.0
    coupon_per_100 = 100.0 * coupon_rate / frequency
    discount_base = max(1.0 + annual_yield / frequency, 1e-8)
    n = 0
    current = maturity
    while current > settlement:
        n += 1
        current = current - pd.DateOffset(months=int(12 / frequency))
    if n <= 0: return 0.0, 0.0, 0.0
    exponent = (n - 1) + (dsc / e)
    pv_red_plus_coupon = (redemption + coupon_per_100) / (discount_base ** exponent)
    pv_intermediate = sum(coupon_per_100 / (discount_base ** ((k - 1) + (dsc / e))) for k in range(1, n))
    accrued_100 = coupon_per_100 * (a / e)
    clean_price_100 = pv_red_plus_coupon + pv_intermediate - accrued_100
    return clean_price_100, accrued_100, clean_price_100 + accrued_100

def run_portfolio_valuation(df, valuation_date):
    output = df.copy()
    cp100, ai100, p100, cv, fv, iiv, bv, gl = [], [], [], [], [], [], [], []
    for _, row in output.iterrows():
        face = float(row["Maturity Value"])
        purchase_date = pd.Timestamp(row["Initial Inv Date"])
        maturity_date = pd.Timestamp(row["Maturity Date"])
        coupon_rate = float(row["Coupon"])
        purchased_ytm = float(row["YTM"])
        selling_ytm = float(row["Yield"])
        c100, a100, f100 = excel_price_actual_actual(valuation_date, maturity_date, coupon_rate, selling_ytm)
        c100 = round(c100, 4); a100 = round(a100, 4); f100 = round(c100 + a100, 4)
        ip100, _, _ = excel_price_actual_actual(purchase_date, maturity_date, coupon_rate, purchased_ytm)
        ip100 = round(ip100, 4)
        init_value = ip100 * (face / 100.0)
        total_days = max((maturity_date - purchase_date).days, 1)
        elapsed = min(max((pd.Timestamp(valuation_date) - purchase_date).days, 0), total_days)
        book_val = (((face - init_value) / total_days) * elapsed) + init_value
        cp100.append(c100); ai100.append(a100); p100.append(f100)
        cv.append(c100 * face / 100); fv.append(f100 * face / 100)
        iiv.append(init_value); bv.append(book_val)
        gl.append(c100 * face / 100 - book_val)
    output["Clean Price"] = cp100; output["Accrued Int"] = ai100; output["Price 100%"] = p100
    output["Clean Value"] = cv; output["Full Value"] = fv; output["Initial Inv Value"] = iiv
    output["Book Value"] = bv; output["Gain/Loss"] = gl
    return output

def run_yield_shock_analysis(valued_df, valuation_date, shock_bps):
    output = valued_df.copy()
    shock_rate = shock_bps / 10000.0
    sy, bcp, bai, bp, bcv, bfv, bgl, scp, sai, sp2, scv, sfv, sgl = ([] for _ in range(13))
    for _, row in output.iterrows():
        y_base = float(row["Yield"])
        y_shocked = max(-0.99, y_base + shock_rate)
        face = float(row["Maturity Value"])
        c_b, a_b, f_b = excel_price_actual_actual(valuation_date, row["Maturity Date"], float(row["Coupon"]), y_base)
        c_b = round(c_b,4); a_b = round(a_b,4); f_b = round(c_b+a_b,4)
        c_s, a_s, f_s = excel_price_actual_actual(valuation_date, row["Maturity Date"], float(row["Coupon"]), y_shocked)
        c_s = round(c_s,4); a_s = round(a_s,4); f_s = round(c_s+a_s,4)
        sy.append(y_shocked)
        bcp.append(c_b); bai.append(a_b); bp.append(f_b)
        bcv.append(c_b*face/100); bfv.append(f_b*face/100); bgl.append(c_b*face/100 - float(row["Book Value"]))
        scp.append(c_s); sai.append(a_s); sp2.append(f_s)
        scv.append(c_s*face/100); sfv.append(f_s*face/100); sgl.append(c_s*face/100 - float(row["Book Value"]))
    output["Yield (Base)"] = output["Yield"]; output["Yield (Shocked)"] = sy
    output["Price 100 (Base)"] = bp; output["Price 100 (Shocked)"] = sp2
    output["Price 100 Delta"] = output["Price 100 (Shocked)"] - output["Price 100 (Base)"]
    output["Clean Price (Base)"] = bcp; output["Clean Price (Shocked)"] = scp
    output["Clean Price Delta"] = output["Clean Price (Shocked)"] - output["Clean Price (Base)"]
    output["Clean Value (Base)"] = bcv; output["Clean Value (Shocked)"] = scv
    output["Clean Value Delta"] = output["Clean Value (Shocked)"] - output["Clean Value (Base)"]
    output["Full Value (Base)"] = bfv; output["Full Value (Shocked)"] = sfv
    output["Full Value Delta"] = output["Full Value (Shocked)"] - output["Full Value (Base)"]
    output["Accrued Int (Base)"] = bai; output["Accrued Int (Shocked)"] = sai
    output["Accrued Interest Delta"] = output["Accrued Int (Shocked)"] - output["Accrued Int (Base)"]
    output["Gain/Loss vs Book (Base)"] = bgl; output["Gain/Loss vs Book (Shocked)"] = sgl
    output["Gain/Loss Delta"] = output["Gain/Loss vs Book (Shocked)"] - output["Gain/Loss vs Book (Base)"]
    return output

def aggregate_shock_by_isin(shock_df):
    grouped = (
        shock_df.groupby("ISIN", as_index=False)
        .agg(Positions=("Deal No.","count"), Face_Value=("Maturity Value","sum"),
             Book_Value=("Book Value","sum"),
             Price100_Base=("Price 100 (Base)","mean"), Price100_Shocked=("Price 100 (Shocked)","mean"),
             CleanPrice_Base=("Clean Price (Base)","mean"), CleanPrice_Shocked=("Clean Price (Shocked)","mean"),
             Clean_Base=("Clean Value (Base)","sum"), Clean_Shocked=("Clean Value (Shocked)","sum"),
             Full_Base=("Full Value (Base)","sum"), Full_Shocked=("Full Value (Shocked)","sum"),
             Accrued_Base=("Accrued Int (Base)","mean"), Accrued_Shocked=("Accrued Int (Shocked)","mean"),
             GL_Base=("Gain/Loss vs Book (Base)","sum"), GL_Shocked=("Gain/Loss vs Book (Shocked)","sum"))
        .sort_values("ISIN")
    )
    grouped["Price100_Delta"] = grouped["Price100_Shocked"] - grouped["Price100_Base"]
    grouped["CleanPrice_Delta"] = grouped["CleanPrice_Shocked"] - grouped["CleanPrice_Base"]
    grouped["Clean_Delta"] = grouped["Clean_Shocked"] - grouped["Clean_Base"]
    grouped["Full_Delta"] = grouped["Full_Shocked"] - grouped["Full_Base"]
    grouped["Accrued_Delta"] = grouped["Accrued_Shocked"] - grouped["Accrued_Base"]
    grouped["GL_Delta"] = grouped["GL_Shocked"] - grouped["GL_Base"]
    return grouped

def aggregate_by_isin(valued_df):
    grouped = (
        valued_df.groupby("ISIN", as_index=False)
        .agg(Positions=("Deal No.","count"), Face_Value=("Maturity Value","sum"),
             Clean_Value=("Clean Value","sum"), Full_Value=("Full Value","sum"),
             Book_Value=("Book Value","sum"), Gain_Loss=("Gain/Loss","sum"),
             Input_Market_Value=("Market value","max"))
        .sort_values("ISIN")
    )
    grouped["Clean_minus_Book"] = grouped["Clean_Value"] - grouped["Book_Value"]
    grouped["Full_minus_Book"] = grouped["Full_Value"] - grouped["Book_Value"]
    return grouped

def to_excel_bytes(summary_df, detail_df, shock_position_df, shock_isin_df):
    try:
        import openpyxl
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            summary_df.to_excel(writer, index=False, sheet_name="ISIN Summary")
            detail_df.to_excel(writer, index=False, sheet_name="Position Details")
            shock_position_df.to_excel(writer, index=False, sheet_name="Shock Position")
            shock_isin_df.to_excel(writer, index=False, sheet_name="Shock ISIN")
        return buffer.getvalue(), "bond_pricer_output.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    except ModuleNotFoundError:
        buffer = BytesIO()
        with ZipFile(buffer, mode="w", compression=ZIP_DEFLATED) as zf:
            zf.writestr("isin_summary.csv", summary_df.to_csv(index=False))
            zf.writestr("position_details.csv", detail_df.to_csv(index=False))
            zf.writestr("shock_position.csv", shock_position_df.to_csv(index=False))
            zf.writestr("shock_isin.csv", shock_isin_df.to_csv(index=False))
        return buffer.getvalue(), "bond_pricer_output.zip", "application/zip"

# ── CHART RENDERERS ───────────────────────────────────────────────────────────
def render_portfolio_visuals(shock_df):
    plot_df = (
        shock_df.groupby("ISIN", as_index=False)["Gain/Loss Delta"]
        .sum().sort_values("Gain/Loss Delta", key=lambda s: s.abs(), ascending=False)
    )
    if plot_df.empty: return

    c1, c2 = st.columns([1.6, 1])
    with c1:
        colors = np.where(plot_df["Gain/Loss Delta"] >= 0, "#10B981", "#F43F5E")
        fig = go.Figure(go.Bar(
            x=plot_df["ISIN"], y=plot_df["Gain/Loss Delta"],
            marker=dict(color=colors, line=dict(color="#07090F", width=1)),
            hovertemplate="<b>%{x}</b><br>G/L Δ: %{y:,.2f}<extra></extra>",
        ))
        fig.add_hline(y=0, line_color="#1A2332", line_width=1)
        fig.update_layout(
            **{k: v for k, v in ADMIN_CHART.items() if k not in ("legend",)},
            title=dict(text="GAIN / LOSS DELTA BY ISIN", font=dict(size=10, color="#475569",
                       family="IBM Plex Mono"), x=0),
            height=260, showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with c2:
        fig2 = go.Figure(go.Pie(
            labels=plot_df["ISIN"], values=plot_df["Gain/Loss Delta"].abs(),
            hole=0.6, textinfo="label+percent",
            marker=dict(
                colors=["#D97706","#B45309","#92400E","#78350F","#F59E0B","#FBBF24"],
                line=dict(color="#07090F", width=2)
            ),
            textfont=dict(family="IBM Plex Mono", size=9, color="#94A3B8"),
            hovertemplate="<b>%{label}</b><br>%{value:,.2f}<br>%{percent}<extra></extra>",
        ))
        fig2.update_layout(
            **{k: v for k, v in ADMIN_CHART.items() if k not in ("xaxis","yaxis","legend")},
            title=dict(text="SHOCK IMPACT SHARE", font=dict(size=10, color="#475569",
                       family="IBM Plex Mono"), x=0),
            height=260,
            legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#64748B", size=8),
                        orientation="v", x=1.02),
            margin=dict(l=0, r=80, t=32, b=0),
        )
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

def render_isin_visuals(isin_df, selected_isin):
    if isin_df.empty: return
    chart_df = isin_df.copy()
    chart_df["Deal No."] = chart_df["Deal No."].astype(str)

    c1, c2 = st.columns([1.4, 1])
    with c1:
        colors = np.where(chart_df["Gain/Loss Delta"] >= 0, "#10B981", "#F43F5E")
        fig = go.Figure(go.Bar(
            x=chart_df["Deal No."], y=chart_df["Gain/Loss Delta"],
            marker=dict(color=colors, line=dict(color="#07090F", width=1)),
            hovertemplate="Deal %{x}<br>G/L Δ: %{y:,.2f}<extra></extra>",
        ))
        fig.add_hline(y=0, line_color="#1A2332", line_width=1)
        fig.update_layout(
            **{k: v for k, v in ADMIN_CHART.items() if k not in ("legend",)},
            title=dict(text=f"DEAL-LEVEL G/L DELTA — {selected_isin}",
                       font=dict(size=10, color="#475569", family="IBM Plex Mono"), x=0),
            height=250, showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with c2:
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=chart_df["Maturity Date"], y=chart_df["Yield (Base)"] * 100,
            mode="lines+markers", name="Base",
            line=dict(color="#3B82F6", width=2),
            marker=dict(size=5), hovertemplate="%{x}<br>Base: %{y:.4f}%<extra></extra>",
        ))
        fig2.add_trace(go.Scatter(
            x=chart_df["Maturity Date"], y=chart_df["Yield (Shocked)"] * 100,
            mode="lines+markers", name="Shocked",
            line=dict(color="#D97706", width=2, dash="dot"),
            marker=dict(size=5), hovertemplate="%{x}<br>Shocked: %{y:.4f}%<extra></extra>",
        ))
        fig2.update_layout(
            **{k: v for k, v in ADMIN_CHART.items() if k not in ("xaxis",)},
            title=dict(text="BASE vs SHOCKED YIELD", font=dict(size=10, color="#475569",
                       family="IBM Plex Mono"), x=0),
            xaxis=dict(showgrid=False, zeroline=False, color="#334155",
                       type="date", tickfont=dict(size=9)),
            height=250,
        )
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    # ── Admin top bar ──
    st.markdown("""
    <div class="admin-bar">
        <div class="admin-bar-left">
            <div class="admin-badge">⚙ Admin</div>
            <div>
                <div class="admin-title">Bond Portfolio Pricer</div>
                <div class="admin-subtitle">Semi-annual pricing · Yield shock analysis · Admin access only</div>
            </div>
        </div>
        <div style="font-family:'IBM Plex Mono',monospace;font-size:.7rem;color:#334155;letter-spacing:.06em;">
            RESTRICTED ACCESS
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Sidebar ──────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("""
        <style>
        [data-testid="stSidebar"] > div:first-child { padding: 1.2rem 1rem 2rem; }
        .sb-label {
            font-family: 'IBM Plex Mono', monospace;
            font-size: .6rem;
            font-weight: 600;
            letter-spacing: .14em;
            text-transform: uppercase;
            color: #334155;
            margin-bottom: .4rem;
            padding-left: 2px;
        }
        .sb-nav-link {
            display: flex; align-items: center; gap: 8px;
            padding: .45rem .75rem;
            border-radius: 6px;
            font-size: .78rem;
            color: #64748B;
            margin-bottom: 2px;
            cursor: pointer;
        }
        .sb-nav-link.active {
            background: rgba(217,119,6,.1);
            color: #FCD34D;
            border: 1px solid rgba(217,119,6,.2);
        }
        .sb-divider { border: none; border-top: 1px solid #1A2332; margin: .9rem 0; }
        [data-testid="stSidebar"] .stButton > button {
            background: transparent !important;
            border: 1px solid #1A2332 !important;
            color: #475569 !important;
            font-size: .72rem !important;
            width: 100% !important;
            border-radius: 6px !important;
            font-family: 'IBM Plex Mono', monospace !important;
        }
        [data-testid="stSidebar"] .stButton > button:hover {
            border-color: #F43F5E !important;
            color: #F43F5E !important;
        }
        </style>
        """, unsafe_allow_html=True)

        auth.render_sidebar_user_panel()

        st.markdown("""
        <div class="sb-label" style="margin-bottom:.5rem;">Navigation</div>
        <div class="sb-nav-link active"><span>⚙️</span> Bond Pricer</div>
        <div class="sb-nav-link"><span>📊</span> Portfolio Dashboard</div>
        <div class="sb-nav-link"><span>🔍</span> Bond Deep-Dive</div>
        <hr class="sb-divider"/>
        """, unsafe_allow_html=True)

        st.markdown('<div class="sb-label">Valuation Date</div>', unsafe_allow_html=True)
        valuation_date = st.date_input("", value=date.today(), label_visibility="collapsed")

        st.markdown('<hr class="sb-divider"/>', unsafe_allow_html=True)
        st.markdown('<div class="sb-label">Upload Portfolio</div>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader("CSV / Excel", type=["csv","xlsx","xls"],
                                          label_visibility="collapsed")

        st.markdown('<hr class="sb-divider"/>', unsafe_allow_html=True)
        st.markdown('<div class="sb-label">Yield Shock</div>', unsafe_allow_html=True)
        shock_pct = st.number_input(
            "Parallel shift (%)", min_value=-10.0, max_value=10.0,
            value=0.0, step=0.05, format="%.2f",
            label_visibility="visible",
            help="e.g. 0.50 = +50 bps parallel shift",
        )
        shock_bps = int(round(shock_pct * 100))
        st.markdown(f"""
        <div style="font-family:'IBM Plex Mono',monospace;font-size:.72rem;color:#D97706;
                    background:rgba(217,119,6,.08);border:1px solid rgba(217,119,6,.2);
                    border-radius:5px;padding:.4rem .75rem;margin-top:.3rem;">
            {shock_pct:+.2f}% &nbsp;|&nbsp; {shock_bps:+d} bps
        </div>
        """, unsafe_allow_html=True)

    # ── Gate ──
    if not uploaded_file:
        st.markdown("""
        <div style="text-align:center;padding:6rem 2rem;color:#334155;">
            <div style="font-family:'IBM Plex Mono',monospace;font-size:2rem;margin-bottom:1rem;color:#1A2332;">⚙</div>
            <div style="font-family:'IBM Plex Mono',monospace;font-size:.9rem;color:#475569;margin-bottom:.4rem;">
                No portfolio loaded
            </div>
            <div style="font-size:.78rem;color:#334155;">Upload a CSV or Excel file using the sidebar to begin pricing.</div>
        </div>
        """, unsafe_allow_html=True)
        return

    try:
        portfolio_df = load_portfolio(uploaded_file)
    except Exception as e:
        st.error(f"Could not read file: {e}")
        return

    if portfolio_df.empty:
        st.warning("No valid bond rows found after cleaning.")
        return

    valuation_timestamp = pd.Timestamp(valuation_date)
    valued_df = run_portfolio_valuation(portfolio_df, valuation_timestamp)
    summary_df = aggregate_by_isin(valued_df)

    shock_position_df = run_yield_shock_analysis(
        valued_df=valued_df,
        valuation_date=valuation_timestamp,
        shock_bps=float(shock_bps),
    )
    shock_isin_df = aggregate_shock_by_isin(shock_position_df)

    # ── Portfolio KPIs ──
    total_book        = float(shock_position_df["Book Value"].sum())
    total_full_base   = float(shock_position_df["Full Value (Base)"].sum())
    total_full_shock  = float(shock_position_df["Full Value (Shocked)"].sum())
    total_clean_base  = float(shock_position_df["Clean Value (Base)"].sum())
    total_clean_shock = float(shock_position_df["Clean Value (Shocked)"].sum())
    total_gl_base     = float(shock_position_df["Gain/Loss vs Book (Base)"].sum())
    total_gl_shock    = float(shock_position_df["Gain/Loss vs Book (Shocked)"].sum())
    n_positions       = len(shock_position_df)
    n_isins           = shock_position_df["ISIN"].nunique()

    sec_header("Portfolio Overview")
    st.markdown(f"""
    <div class="kpi-grid">
        {kpi_card("Book Value", fmt(total_book))}
        {kpi_card("Full Value — Shocked", fmt(total_full_shock),
                  delta=total_full_shock - total_full_base)}
        {kpi_card("Clean Value — Shocked", fmt(total_clean_shock),
                  delta=total_clean_shock - total_clean_base)}
        {kpi_card("G/L vs Book — Shocked", fmt(total_gl_shock),
                  delta=total_gl_shock - total_gl_base)}
    </div>
    """, unsafe_allow_html=True)

    # Secondary row
    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Positions", str(n_positions))
    r2.metric("ISINs", str(n_isins))
    r3.metric("Full Value — Base", fmt(total_full_base))
    r4.metric("G/L — Base", fmt(total_gl_base))

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tab1, tab2 = st.tabs([
        "  Portfolio — Shock Impact  ",
        "  ISIN Drill-Down  ",
    ])

    portfolio_cols = [
        "Port. Index","Instrument","Deal No.","ISIN","Initial Inv Date","Maturity Date",
        "Maturity Value","Coupon","Yield (Base)","Yield (Shocked)",
        "Price 100 (Base)","Price 100 (Shocked)","Price 100 Delta",
        "Clean Price (Base)","Clean Price (Shocked)","Clean Price Delta",
        "Accrued Int (Base)","Accrued Int (Shocked)","Accrued Interest Delta",
        "Full Value (Base)","Full Value (Shocked)","Full Value Delta",
        "Clean Value (Base)","Clean Value (Shocked)","Clean Value Delta",
        "Book Value","Gain/Loss vs Book (Base)","Gain/Loss vs Book (Shocked)","Gain/Loss Delta",
    ]
    num_fmt = {
        "Maturity Value":"{:,.2f}","Price 100 (Base)":"{:,.4f}","Price 100 (Shocked)":"{:,.4f}",
        "Price 100 Delta":"{:,.4f}","Clean Price (Base)":"{:,.4f}","Clean Price (Shocked)":"{:,.4f}",
        "Clean Price Delta":"{:,.4f}","Full Value (Base)":"{:,.2f}","Full Value (Shocked)":"{:,.2f}",
        "Full Value Delta":"{:,.2f}","Clean Value (Base)":"{:,.2f}","Clean Value (Shocked)":"{:,.2f}",
        "Clean Value Delta":"{:,.2f}","Book Value":"{:,.2f}","Gain/Loss vs Book (Base)":"{:,.2f}",
        "Gain/Loss vs Book (Shocked)":"{:,.2f}","Gain/Loss Delta":"{:,.2f}",
    }

    def color_delta(v):
        if isinstance(v, float):
            return "color: #10B981" if v >= 0 else "color: #F43F5E"
        return ""

    with tab1:
        sec_header("Shock Impact Visuals")
        render_portfolio_visuals(shock_position_df)

        sec_header("All Positions")
        styled = (shock_position_df[portfolio_cols]
                  .style.format(num_fmt, na_rep="—")
                  .applymap(color_delta, subset=["Gain/Loss Delta","Full Value Delta","Clean Value Delta"]))
        st.dataframe(styled, use_container_width=True, height=380)

        dl_bytes, dl_name, dl_mime = to_excel_bytes(
            summary_df=summary_df, detail_df=valued_df,
            shock_position_df=shock_position_df[portfolio_cols],
            shock_isin_df=shock_isin_df,
        )
        st.download_button("📥 Export Results", data=dl_bytes,
                           file_name=dl_name, mime=dl_mime)

    with tab2:
        sec_header("ISIN Aggregated Impact")
        isin_display = shock_isin_df.rename(columns={
            "Clean_Base":"Clean Value (Base)","Clean_Shocked":"Clean Value (Shocked)",
            "Clean_Delta":"Clean Value Delta",
        })
        isin_fmt = {
            "Face_Value":"{:,.2f}","Book_Value":"{:,.2f}","Price100_Base":"{:,.4f}",
            "Price100_Shocked":"{:,.4f}","Price100_Delta":"{:,.4f}",
            "CleanPrice_Base":"{:,.4f}","CleanPrice_Shocked":"{:,.4f}","CleanPrice_Delta":"{:,.4f}",
            "Clean Value (Base)":"{:,.2f}","Clean Value (Shocked)":"{:,.2f}","Clean Value Delta":"{:,.2f}",
            "Full_Base":"{:,.2f}","Full_Shocked":"{:,.2f}","Full_Delta":"{:,.2f}",
            "GL_Base":"{:,.2f}","GL_Shocked":"{:,.2f}","GL_Delta":"{:,.2f}",
        }
        st.dataframe(
            isin_display.style.format(isin_fmt, na_rep="—")
                .applymap(color_delta, subset=["GL_Delta","Full_Delta","Clean Value Delta"]),
            use_container_width=True, height=300,
        )

        sec_header("ISIN Detail")
        isin_options = sorted(shock_position_df["ISIN"].unique().tolist())
        sel_isin = st.selectbox("Select ISIN", isin_options)
        sel_df = shock_position_df[shock_position_df["ISIN"] == sel_isin].copy()

        # ISIN KPIs
        i1, i2, i3, i4 = st.columns(4)
        i1.metric("Positions", str(len(sel_df)))
        i2.metric("Face Value", fmt(float(sel_df["Maturity Value"].sum())))
        i3.metric("G/L Δ (Shocked)", fmt(float(sel_df["Gain/Loss Delta"].sum())))
        i4.metric("Full Value Δ", fmt(float(sel_df["Full Value Delta"].sum())))

        render_isin_visuals(sel_df, sel_isin)

        isin_detail_cols = [
            "Deal No.","Initial Inv Date","Maturity Date","Maturity Value","Coupon",
            "Yield (Base)","Yield (Shocked)","Price 100 (Base)","Price 100 (Shocked)","Price 100 Delta",
            "Clean Price (Base)","Clean Price (Shocked)","Clean Price Delta",
            "Full Value (Base)","Full Value (Shocked)","Full Value Delta",
            "Clean Value (Base)","Clean Value (Shocked)","Clean Value Delta",
            "Book Value","Gain/Loss vs Book (Base)","Gain/Loss vs Book (Shocked)","Gain/Loss Delta",
        ]
        st.dataframe(
            sel_df[isin_detail_cols].style.format(num_fmt, na_rep="—")
                .applymap(color_delta, subset=["Gain/Loss Delta","Full Value Delta","Clean Value Delta"]),
            use_container_width=True, height=300,
        )

        sec_header("Cash-Flow Table")
        deal_options = sel_df["Deal No."].astype(str).tolist()
        dc1, dc2 = st.columns([1, 1])
        with dc1:
            sel_deal = st.selectbox("Deal No.", deal_options)
        with dc2:
            basis = st.selectbox("Pricing Basis", ["Base Yield", "Shocked Yield"])

        sel_row = sel_df[sel_df["Deal No."].astype(str) == sel_deal].iloc[0]
        rate = float(sel_row["Yield (Base)"]) if basis == "Base Yield" else float(sel_row["Yield (Shocked)"])

        calc_table, dirty, clean, accrued, frac = build_valuation_table(
            face_value=float(sel_row["Maturity Value"]),
            coupon_rate=float(sel_row["Coupon"]),
            annual_yield=rate,
            maturity_date=sel_row["Maturity Date"],
            valuation_date=valuation_timestamp,
        )

        cf1, cf2, cf3, cf4 = st.columns(4)
        cf1.metric("Face Value", fmt(float(sel_row["Maturity Value"])))
        cf2.metric("Dirty Value", fmt(dirty))
        cf3.metric("Accrued Interest", fmt(accrued))
        cf4.metric("Clean Value", fmt(clean))

        st.markdown(
            f'<div class="info-mono">frac = days_to_next / period_days = {frac:.6f} &nbsp;·&nbsp; '
            f'yield = {rate*100:.4f}% &nbsp;·&nbsp; '
            f'exponents: {frac:.4f}, {1+frac:.4f}, {2+frac:.4f} ...</div>',
            unsafe_allow_html=True
        )

        cf_fmt = {"Coupon CF":"{:,.4f}","Principal CF":"{:,.4f}","Total CF":"{:,.4f}",
                  "Discount Factor":"{:.8f}","PV":"{:,.4f}","Exponent (n + frac)":"{:.6f}"}
        st.dataframe(calc_table.style.format(cf_fmt, na_rep="—"),
                     use_container_width=True, height=320)

    # ── Mobile bottom nav ──
    mobile.inject_mobile_nav(active_page="pricer")


if __name__ == "__main__":
    main()
