from __future__ import annotations

from datetime import date

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import streamlit as st
import mobile

# ── SHARED THEME ─────────────────────────────────────────────────────────────
DARK_THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: #0B0F1A; color: #E2E8F0; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 2.5rem 4rem; max-width: 1400px; }

[data-testid="stSidebar"] {
    background: #080C14 !important;
    border-right: 1px solid #1E2A3A !important;
    min-width: 260px !important;
}
[data-testid="collapsedControl"] {
    background: #0B0F1A !important;
    border-right: 1px solid #1E2A3A !important;
    color: #475569 !important;
}

.section-label {
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #475569;
    margin-bottom: 0.5rem;
}

/* Metric */
[data-testid="metric-container"] { background: transparent !important; }
[data-testid="metric-container"] label { color: #64748B !important; font-size: 0.72rem !important; letter-spacing: 0.06em !important; text-transform: uppercase !important; }
[data-testid="metric-container"] [data-testid="stMetricValue"] { color: #F1F5F9 !important; font-family: 'DM Mono', monospace !important; font-size: 1.3rem !important; }

/* Inputs */
.stTextInput input, .stNumberInput input, .stSelectbox > div > div {
    background: #0F172A !important;
    border: 1px solid #1E2A3A !important;
    border-radius: 7px !important;
    color: #E2E8F0 !important;
}
.stTextInput input:focus, .stNumberInput input:focus {
    border-color: #0EA5E9 !important;
    box-shadow: 0 0 0 3px rgba(14,165,233,0.1) !important;
}
label { color: #64748B !important; font-size: 0.78rem !important; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: transparent;
    border-bottom: 1px solid #1E2A3A;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #64748B;
    font-size: 0.82rem;
    font-weight: 500;
    border-bottom: 2px solid transparent;
    border-radius: 0;
}
.stTabs [aria-selected="true"] {
    background: transparent !important;
    color: #F1F5F9 !important;
    border-bottom: 2px solid #0EA5E9 !important;
}

/* Dataframe */
[data-testid="stDataFrameContainer"] {
    background: #0F172A;
    border: 1px solid #1E2A3A;
    border-radius: 8px;
}

/* Buttons */
.stButton > button {
    background: #0EA5E9;
    color: #fff;
    border: none;
    border-radius: 6px;
    font-size: 0.82rem;
    font-weight: 500;
    padding: 0.5rem 1.2rem;
}
.stButton > button:hover { background: #0284C7; }

/* Panel card */
.dd-panel {
    background: #111827;
    border: 1px solid #1E2A3A;
    border-radius: 10px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
    position: relative;
    overflow: hidden;
}
.dd-panel::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #0EA5E9, #6366F1);
}
.dd-panel-title {
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #475569;
    margin-bottom: 0.9rem;
}

/* Coupon pill */
.cp-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.45rem 0;
    border-bottom: 1px solid #1E2A3A;
    font-size: 0.82rem;
}
.cp-row:last-child { border-bottom: none; }
.cp-date { color: #94A3B8; font-family: 'DM Mono', monospace; font-size: 0.8rem; }
.cp-pill-paid {
    background: rgba(16,185,129,0.12);
    color: #10B981;
    border-radius: 20px;
    padding: 2px 10px;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}
.cp-pill-accruing {
    background: rgba(245,158,11,0.12);
    color: #F59E0B;
    border-radius: 20px;
    padding: 2px 10px;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}
.cp-pill-future {
    background: rgba(99,102,241,0.12);
    color: #818CF8;
    border-radius: 20px;
    padding: 2px 10px;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}
.cp-amount { color: #E2E8F0; font-family: 'DM Mono', monospace; font-size: 0.82rem; }

/* Info box */
.info-box {
    background: #0F172A;
    border: 1px solid #1E2A3A;
    border-left: 3px solid #0EA5E9;
    border-radius: 6px;
    padding: 0.6rem 1rem;
    font-size: 0.8rem;
    color: #94A3B8;
    margin-bottom: 1rem;
}

/* PnL summary rows */
.pnl-row {
    display: flex;
    justify-content: space-between;
    padding: 0.5rem 0;
    border-bottom: 1px solid #1E2A3A;
    font-size: 0.85rem;
}
.pnl-row:last-child { border-bottom: none; }
.pnl-label { color: #64748B; }
.pnl-value { font-family: 'DM Mono', monospace; color: #E2E8F0; }
.pnl-value.pos { color: #10B981; }
.pnl-value.neg { color: #F43F5E; }

/* Scrollbar */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #0B0F1A; }
::-webkit-scrollbar-thumb { background: #1E2A3A; border-radius: 4px; }
</style>
"""

CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans", color="#94A3B8", size=11),
    margin=dict(l=0, r=0, t=28, b=0),
    xaxis=dict(showgrid=False, zeroline=False, color="#475569"),
    yaxis=dict(showgrid=True, gridcolor="#1E2A3A", zeroline=False, color="#475569"),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#94A3B8", size=10)),
)

# ── CALCULATIONS (unchanged) ──────────────────────────────────────────────────
def get_future_coupon_dates(maturity_date, valuation_date):
    dates = []
    current = pd.Timestamp(maturity_date).normalize()
    valuation_date = pd.Timestamp(valuation_date).normalize()
    while current > valuation_date:
        dates.append(current)
        current = current - pd.DateOffset(months=6)
    return sorted(dates)


def get_coupon_schedule(maturity_date, issue_date, frequency=2):
    if pd.isna(maturity_date) or pd.isna(issue_date):
        return []
    maturity = pd.Timestamp(maturity_date).normalize()
    issue = pd.Timestamp(issue_date).normalize()
    if issue > maturity:
        return []
    months = int(12 / frequency)
    dates = []
    current = maturity
    while current >= issue:
        dates.append(current)
        current = current - pd.DateOffset(months=months)
    return sorted(dates)


def build_valuation_table(face_value, coupon_rate, annual_yield, maturity_date, valuation_date):
    coupon_dates = get_future_coupon_dates(maturity_date, valuation_date)
    if not coupon_dates:
        empty = pd.DataFrame(columns=[
            "Cash Flow Date", "Coupon CF", "Principal CF", "Total CF",
            "Exponent (n + frac)", "Discount Factor", "PV",
        ])
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
        rows.append({
            "Cash Flow Date": cash_date.date(),
            "Coupon CF": coupon_cf,
            "Principal CF": principal_cf,
            "Total CF": total_cf,
            "Exponent (n + frac)": exponent,
            "Discount Factor": discount_factor,
            "PV": pv,
        })

    accrued_interest = period_coupon * (1.0 - frac)
    accrued_interest = max(0.0, min(accrued_interest, period_coupon))
    clean_price = dirty_price - accrued_interest
    return pd.DataFrame(rows), dirty_price, clean_price, accrued_interest, frac


# ── CHART HELPERS ─────────────────────────────────────────────────────────────
def cashflow_timeline_chart(coupon_dates, face_value, coupon_rate, valuation_date):
    """Gantt-style cashflow bar chart."""
    val_ts = pd.Timestamp(valuation_date).normalize()
    period_coupon = face_value * coupon_rate / 2.0

    dates, amounts, colors, labels = [], [], [], []
    for d in coupon_dates:
        is_maturity = (d == coupon_dates[-1])
        amt = period_coupon + (face_value if is_maturity else 0)
        dates.append(d)
        amounts.append(amt)
        if d <= val_ts:
            colors.append("#10B981")
            labels.append("Paid")
        else:
            colors.append("#6366F1" if not is_maturity else "#0EA5E9")
            labels.append("Principal + Coupon" if is_maturity else "Coupon")

    fig = go.Figure()
    for d, a, c, l in zip(dates, amounts, colors, labels):
        fig.add_trace(go.Bar(
            x=[d], y=[a],
            marker_color=c, name=l,
            hovertemplate=f"<b>{d.date()}</b><br>{l}<br>{a:,.2f}<extra></extra>",
            showlegend=False,
        ))

    # Valuation date line
    fig.add_vline(x=val_ts.timestamp() * 1000, line_color="#F59E0B",
                  line_dash="dash", line_width=1.5,
                  annotation_text="Today", annotation_font_color="#F59E0B",
                  annotation_font_size=10)

    fig.update_layout(
        **{k: v for k, v in CHART_LAYOUT.items() if k not in ("legend", "xaxis")},
        title=dict(text="Cashflow Timeline", font=dict(size=12, color="#64748B")),
        height=220, barmode="overlay",
        xaxis=dict(showgrid=False, zeroline=False, color="#475569", type="date"),
    )
    return fig


def pv_bar_chart(calc_table):
    """PV contribution per cashflow date."""
    if calc_table.empty:
        return None
    fig = go.Figure(go.Bar(
        x=calc_table["Cash Flow Date"].astype(str),
        y=calc_table["PV"],
        marker=dict(
            color=calc_table["PV"],
            colorscale=[[0, "#1E2A3A"], [1, "#0EA5E9"]],
            showscale=False,
        ),
        hovertemplate="<b>%{x}</b><br>PV: %{y:,.2f}<extra></extra>",
    ))
    fig.update_layout(
        **{k: v for k, v in CHART_LAYOUT.items() if k != "legend"},
        title=dict(text="Present Value per Cash Flow", font=dict(size=12, color="#64748B")),
        height=220,
    )
    return fig


# ── MAIN DEEP-DIVE RENDERER ───────────────────────────────────────────────────
def show_deep_dive(selected_row: pd.Series, valuation_timestamp: pd.Timestamp) -> None:
    st.markdown(DARK_THEME_CSS, unsafe_allow_html=True)

    isin  = selected_row.get("ISIN", "")
    deal  = selected_row.get("Deal No.", "")
    instr = selected_row.get("Instrument", "")

    face         = float(selected_row.get("Maturity Value", 0.0))
    coupon       = float(selected_row.get("Coupon", 0.0))
    base_yield   = float(selected_row.get("Yield", 0.0))
    maturity_date = pd.Timestamp(selected_row.get("Maturity Date"))
    init_date    = pd.Timestamp(selected_row.get("Initial Inv Date"))
    purchased_ytm = float(selected_row.get("YTM", 0.0))

    val_ts = pd.Timestamp(valuation_timestamp).normalize()

    # ── Coupon schedule ──────────────────────────────────────────────────────
    schedule = get_coupon_schedule(maturity_date, init_date, frequency=2)
    if not schedule:
        st.info("No coupon schedule found — check dates.")
        return

    passed = [d for d in schedule if d <= val_ts]
    future = [d for d in schedule if d > val_ts]

    # ── Bond info panel ──────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="dd-panel">
        <div class="dd-panel-title">Bond Details</div>
        <div style="display:grid; grid-template-columns: repeat(4,1fr); gap:1rem;">
            <div>
                <div style="font-size:0.68rem;color:#475569;text-transform:uppercase;letter-spacing:.1em;margin-bottom:.2rem;">ISIN</div>
                <div style="font-family:'DM Mono',monospace;color:#E2E8F0;font-size:.9rem;">{isin}</div>
            </div>
            <div>
                <div style="font-size:0.68rem;color:#475569;text-transform:uppercase;letter-spacing:.1em;margin-bottom:.2rem;">Deal No.</div>
                <div style="font-family:'DM Mono',monospace;color:#E2E8F0;font-size:.9rem;">{deal}</div>
            </div>
            <div>
                <div style="font-size:0.68rem;color:#475569;text-transform:uppercase;letter-spacing:.1em;margin-bottom:.2rem;">Instrument</div>
                <div style="color:#94A3B8;font-size:.9rem;">{instr or "—"}</div>
            </div>
            <div>
                <div style="font-size:0.68rem;color:#475569;text-transform:uppercase;letter-spacing:.1em;margin-bottom:.2rem;">Investment Date</div>
                <div style="font-family:'DM Mono',monospace;color:#94A3B8;font-size:.9rem;">{str(init_date.date())}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Tabs ─────────────────────────────────────────────────────────────────
    tab_val, tab_schedule, tab_pnl = st.tabs([
        "  Valuation  ",
        "  Coupon Schedule  ",
        "  P&L Summary  ",
    ])

    # ── TAB 1: Valuation ─────────────────────────────────────────────────────
    with tab_val:
        vc1, vc2 = st.columns([1, 2])
        with vc1:
            y_input = st.number_input(
                "Base Yield (%)", value=round(base_yield * 100.0, 4), format="%.4f")
            shock_local = st.number_input(
                "Local Shift (bps)", min_value=-2000, max_value=2000, value=0, step=1)
        applied_yield = float(y_input) / 100.0 + shock_local / 10000.0

        calc_table, dirty_price, clean_price, accrued_interest, frac = build_valuation_table(
            face_value=face, coupon_rate=coupon, annual_yield=applied_yield,
            maturity_date=maturity_date, valuation_date=val_ts,
        )

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Face Value",       f"{face:,.2f}")
        k2.metric("Dirty Value",      f"{dirty_price:,.2f}")
        k3.metric("Accrued Interest", f"{accrued_interest:,.2f}")
        k4.metric("Clean Value",      f"{clean_price:,.2f}")

        st.markdown(f'<div class="info-box">First-period fraction: <code>{frac:.6f}</code> &nbsp;|&nbsp; Applied yield: <code>{applied_yield*100:.4f}%</code></div>', unsafe_allow_html=True)

        # Charts
        ch1, ch2 = st.columns(2)
        with ch1:
            st.plotly_chart(cashflow_timeline_chart(schedule, face, coupon, val_ts),
                            use_container_width=True, config={"displayModeBar": False})
        with ch2:
            pvc = pv_bar_chart(calc_table)
            if pvc:
                st.plotly_chart(pvc, use_container_width=True, config={"displayModeBar": False})

        # Cash-flow table
        st.markdown('<div class="section-label" style="margin-top:1rem;">Cash-Flow Table</div>', unsafe_allow_html=True)
        fmt = {"Coupon CF": "{:,.2f}", "Principal CF": "{:,.2f}",
               "Total CF": "{:,.2f}", "Discount Factor": "{:.6f}", "PV": "{:,.2f}"}
        st.dataframe(calc_table.style.format(fmt, na_rep="—"), use_container_width=True, height=300)

    # ── TAB 2: Coupon Schedule ────────────────────────────────────────────────
    with tab_schedule:
        coupon_amt = face * coupon / 2.0
        passed_after_purchase = [d for d in passed if d >= init_date]

        # Re-run valuation to get PV per cashflow date
        sched_table, _, _, _, _ = build_valuation_table(
            face_value=face, coupon_rate=coupon, annual_yield=base_yield,
            maturity_date=maturity_date, valuation_date=val_ts,
        )
        pv_lookup = {}
        if not sched_table.empty:
            for _, r in sched_table.iterrows():
                pv_lookup[str(r["Cash Flow Date"])] = float(r["PV"])

        summary_html = f"""
        <div class="dd-panel">
            <div class="dd-panel-title">Schedule Summary</div>
            <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;">
                <div>
                    <div style="font-size:.68rem;color:#475569;text-transform:uppercase;letter-spacing:.1em;">Total Coupons</div>
                    <div style="font-family:'DM Mono',monospace;font-size:1.4rem;color:#F1F5F9;margin-top:.2rem;">{len(schedule)}</div>
                </div>
                <div>
                    <div style="font-size:.68rem;color:#475569;text-transform:uppercase;letter-spacing:.1em;">Coupon per Period</div>
                    <div style="font-family:'DM Mono',monospace;font-size:1.4rem;color:#F1F5F9;margin-top:.2rem;">{coupon_amt:,.2f}</div>
                </div>
                <div>
                    <div style="font-size:.68rem;color:#475569;text-transform:uppercase;letter-spacing:.1em;">Paid</div>
                    <div style="font-family:'DM Mono',monospace;font-size:1.4rem;color:#10B981;margin-top:.2rem;">{len(passed_after_purchase)}</div>
                </div>
                <div>
                    <div style="font-size:.68rem;color:#475569;text-transform:uppercase;letter-spacing:.1em;">Upcoming</div>
                    <div style="font-family:'DM Mono',monospace;font-size:1.4rem;color:#818CF8;margin-top:.2rem;">{len(future)}</div>
                </div>
            </div>
        </div>
        """
        st.markdown(summary_html, unsafe_allow_html=True)

        st.markdown(
            '<div class="info-box">This is a <strong>fixed-rate bond</strong> — '            'coupon cash flow is identical every period (<code>Face × Rate ÷ 2</code>). '            'The <strong>PV</strong> column shows the discounted present value per payment, '            'which decreases for nearer dates due to time value of money.</div>',
            unsafe_allow_html=True
        )

        # Header row
        header_html = """<div style="display:flex;gap:.5rem;padding:.4rem 0;border-bottom:1px solid #334155;margin-bottom:.2rem;">
            <span style="color:#475569;font-size:.68rem;font-weight:600;letter-spacing:.08em;text-transform:uppercase;min-width:105px;">Date</span>
            <span style="color:#475569;font-size:.68rem;font-weight:600;letter-spacing:.08em;text-transform:uppercase;flex:1;">Type</span>
            <span style="color:#475569;font-size:.68rem;font-weight:600;letter-spacing:.08em;text-transform:uppercase;min-width:85px;text-align:right;">Coupon CF</span>
            <span style="color:#475569;font-size:.68rem;font-weight:600;letter-spacing:.08em;text-transform:uppercase;min-width:85px;text-align:right;">Principal CF</span>
            <span style="color:#475569;font-size:.68rem;font-weight:600;letter-spacing:.08em;text-transform:uppercase;min-width:85px;text-align:right;">Total CF</span>
            <span style="color:#475569;font-size:.68rem;font-weight:600;letter-spacing:.08em;text-transform:uppercase;min-width:85px;text-align:right;">PV</span>
            <span style="color:#475569;font-size:.68rem;font-weight:600;letter-spacing:.08em;text-transform:uppercase;min-width:80px;text-align:center;">Status</span>
        </div>"""

        rows_html = header_html
        for d in schedule:
            is_maturity  = (d == schedule[-1])
            is_paid      = d in passed_after_purchase
            is_accruing  = (not is_paid) and (len(future) > 0) and (d == future[0])
            coupon_cf    = coupon_amt
            principal_cf = face if is_maturity else 0.0
            total_cf     = coupon_cf + principal_cf
            pv_val       = pv_lookup.get(str(d.date()), None)
            pv_str       = f"{pv_val:,.2f}" if pv_val is not None else "—"
            total_color  = "#0EA5E9" if is_maturity else "#E2E8F0"

            if is_paid:
                pill = '<span class="cp-pill-paid">Paid</span>'
            elif is_accruing:
                pill = '<span class="cp-pill-accruing">Accruing</span>'
            else:
                pill = '<span class="cp-pill-future">Upcoming</span>'

            type_label = "Coupon + Principal" if is_maturity else "Coupon"
            rows_html += f"""<div class="cp-row" style="display:flex;gap:.5rem;">
                <span class="cp-date" style="min-width:105px;">{d.date().isoformat()}</span>
                <span style="color:#475569;font-size:.78rem;flex:1;">{type_label}</span>
                <span class="cp-amount" style="min-width:85px;text-align:right;">{coupon_cf:,.2f}</span>
                <span class="cp-amount" style="min-width:85px;text-align:right;">{principal_cf:,.2f}</span>
                <span class="cp-amount" style="min-width:85px;text-align:right;color:{total_color};">{total_cf:,.2f}</span>
                <span class="cp-amount" style="min-width:85px;text-align:right;color:#6366F1;">{pv_str}</span>
                <span style="min-width:80px;text-align:center;">{pill}</span>
            </div>"""

        st.markdown(
            f'<div class="dd-panel"><div class="dd-panel-title">Full Coupon Schedule</div>{rows_html}</div>',
            unsafe_allow_html=True
        )


    # ── TAB 3: P&L Summary ────────────────────────────────────────────────────
    with tab_pnl:
        coupon_amt = face * coupon / 2.0
        passed_after_purchase = [d for d in passed if d >= init_date]
        passed_interest  = coupon_amt * len(passed_after_purchase)
        future_interest  = coupon_amt * len(future)
        future_cashflows = future_interest
        if pd.Timestamp(maturity_date).normalize() in future:
            future_cashflows += face

        # Funding cost
        fc1, fc2 = st.columns([1, 3])
        with fc1:
            funding_rate_local = st.number_input(
                "Funding Rate (%)", value=0.0, step=0.01, format="%.4f")

        days_held = max((val_ts - pd.Timestamp(init_date)).days, 0)

        try:
            _, purchase_dirty, _, _, _ = build_valuation_table(
                face_value=face, coupon_rate=coupon, annual_yield=purchased_ytm,
                maturity_date=maturity_date, valuation_date=pd.Timestamp(init_date),
            )
            purchase_full_value = purchase_dirty
        except Exception:
            purchase_full_value = 0.0

        # Re-compute current dirty using applied_yield from tab_val (use base_yield here)
        try:
            _, dirty_now, _, accrued_now, _ = build_valuation_table(
                face_value=face, coupon_rate=coupon, annual_yield=base_yield,
                maturity_date=maturity_date, valuation_date=val_ts,
            )
        except Exception:
            dirty_now, accrued_now = 0.0, 0.0

        funding_cost = purchase_full_value * (funding_rate_local / 100.0) * (days_held / 365.0)
        net_pl = (dirty_now - purchase_full_value) + passed_interest - funding_cost
        net_pl_color = "pos" if net_pl >= 0 else "neg"

        # KPI row
        p1, p2, p3, p4 = st.columns(4)
        p1.metric("Purchase Full Value", f"{purchase_full_value:,.2f}")
        p2.metric("Current Dirty Value", f"{dirty_now:,.2f}")
        p3.metric("Days Held",           f"{days_held}")
        p4.metric("Funding Cost",        f"{funding_cost:,.2f}")

        st.markdown(f"""
        <div class="dd-panel" style="margin-top:.5rem;">
            <div class="dd-panel-title">P&L Breakdown</div>
            <div class="pnl-row"><span class="pnl-label">Coupon per payment</span><span class="pnl-value">{coupon_amt:,.2f}</span></div>
            <div class="pnl-row"><span class="pnl-label">Coupons received since purchase ({len(passed_after_purchase)})</span><span class="pnl-value">{passed_interest:,.2f}</span></div>
            <div class="pnl-row"><span class="pnl-label">Accrued interest (as of valuation)</span><span class="pnl-value">{accrued_now:,.2f}</span></div>
            <div class="pnl-row"><span class="pnl-label">Expected future coupon interest</span><span class="pnl-value">{future_interest:,.2f}</span></div>
            <div class="pnl-row"><span class="pnl-label">Expected future total cashflows (incl. principal)</span><span class="pnl-value">{future_cashflows:,.2f}</span></div>
            <div class="pnl-row"><span class="pnl-label">Funding cost ({days_held} days @ {funding_rate_local:.4f}%)</span><span class="pnl-value neg">{funding_cost:,.2f}</span></div>
            <div class="pnl-row" style="border-top:1px solid #334155;margin-top:.4rem;padding-top:.6rem;">
                <span style="color:#E2E8F0;font-weight:600;font-size:.9rem;">Net P&L</span>
                <span class="pnl-value {net_pl_color}" style="font-size:1.1rem;font-weight:600;">{net_pl:+,.2f}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ── STANDALONE ENTRY ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    st.set_page_config(page_title="Bond Deep Dive", layout="wide", page_icon="🔍",
                       initial_sidebar_state="expanded")
    mobile.inject_pwa_tags(page_title="Bond Deep-Dive", page_color="#0B0F1A")
    mobile.inject_mobile_css()
    st.markdown(DARK_THEME_CSS, unsafe_allow_html=True)

    st.markdown("""
    <div style="padding:1.5rem 0 1rem; border-bottom:1px solid #1E2A3A; margin-bottom:2rem;
                display:flex; align-items:center; justify-content:space-between;">
        <div style="font-size:.9rem;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:#94A3B8;">Fixed Income</div>
        <div style="font-size:1.4rem;font-weight:600;color:#F1F5F9;letter-spacing:-.02em;">Bond Deep-Dive</div>
        <div style="background:#0EA5E9;color:#fff;font-size:.7rem;font-weight:600;padding:3px 10px;border-radius:20px;letter-spacing:.06em;text-transform:uppercase;">Live</div>
    </div>
    """, unsafe_allow_html=True)

    if "selected_bond" in st.session_state:
        selected = st.session_state["selected_bond"]
        with st.sidebar:
            st.markdown('<div class="section-label">Valuation Date</div>', unsafe_allow_html=True)
            valuation_date = st.date_input("", value=date.today(), label_visibility="collapsed")
        show_deep_dive(selected, pd.Timestamp(valuation_date))
    else:
        st.markdown("""
        <div style="text-align:center;padding:5rem 2rem;color:#475569;">
            <div style="font-size:2.5rem;margin-bottom:1rem;">🔍</div>
            <div style="font-size:1rem;font-weight:500;color:#64748B;">No bond selected</div>
            <div style="font-size:.82rem;margin-top:.4rem;">Use the Portfolio Manager to open a deep-dive.</div>
        </div>
        """, unsafe_allow_html=True)
