"""
FraudGuard - Agent-Based Financial Fraud Detection and Prevention System
CPE 310 Group 13

Run with:
    streamlit run app.py

This app is a UI shell around the team's six agent files. It does not
change any agent logic -- it only calls the same functions every pair
already wrote and tested:

    data_cleaning_agent.py   map_paysim_row, clean_transaction
    pattern_agent.py         spot_pattern            (ml_score)
    rule_checking_agent.py   rule_checking_agent      (rules_verdict)
    decision_agent.py        make_decision            (final_decision)
    action_agent.py          take_action               (action_taken)
    learning_agent.py        learning_agent            (batch evaluation)

Pages:
    Dashboard            overview: KPIs, risk distribution, trend, recent
                         alerts / transactions (built from session history)
    New Transaction      live simulation - one transaction through all
                         five per-transaction agents, shown step by step
    Transactions         full session transaction log with filters
    Fraud Alerts         every flagged/blocked transaction, alert-style
    Model Evaluation     batch evaluation through all SIX agents
                         (including the Learning Agent) against a labelled
                         PaySim-style sample, with a confusion matrix and a
                         recommended ML_SCORE_THRESHOLD
    Agent Architecture   a plain-language map of the six-agent pipeline
    System Audit         the Action Agent's raw audit log
    Settings             demo accounts + session reset
"""

import io
import random
from datetime import datetime

import pandas as pd
import streamlit as st

from action_agent import get_action_log, take_action
from data_cleaning_agent import clean_transaction, map_paysim_row, reset_seen_transactions
from decision_agent import ML_SCORE_THRESHOLD, make_decision
from learning_agent import CURRENT_ML_SCORE_THRESHOLD, learning_agent
from pattern_agent import spot_pattern
from rule_checking_agent import rule_checking_agent

import ui_theme

# =======================================================================
# Page config + theme
# =======================================================================
st.set_page_config(
    page_title="FraudGuard - Fraud Detection System",
    page_icon="\U0001F6E1\uFE0F",
    layout="wide",
    initial_sidebar_state="collapsed",
)
ui_theme.inject_css()

# =======================================================================
# Built-in PaySim-shaped sample, used only when no CSV is uploaded on
# the Model Evaluation page. actual_fraud mirrors PaySim's isFraud column.
# =======================================================================
SAMPLE_BATCH_ROWS = [
    {"step": 1, "type": "PAYMENT", "amount": 9839.64, "nameOrig": "C1231006815",
     "oldbalanceOrg": 170136.0, "newbalanceOrig": 160296.36, "nameDest": "M1979787155",
     "oldbalanceDest": 0.0, "newbalanceDest": 0.0, "isFraud": 0},
    {"step": 1, "type": "TRANSFER", "amount": 181.0, "nameOrig": "C1305486145",
     "oldbalanceOrg": 181.0, "newbalanceOrig": 0.0, "nameDest": "C553264065",
     "oldbalanceDest": 0.0, "newbalanceDest": 0.0, "isFraud": 1},
    {"step": 1, "type": "CASH_OUT", "amount": 181.0, "nameOrig": "C840083671",
     "oldbalanceOrg": 181.0, "newbalanceOrig": 0.0, "nameDest": "C38997010",
     "oldbalanceDest": 21182.0, "newbalanceDest": 0.0, "isFraud": 1},
    {"step": 5, "type": "TRANSFER", "amount": 229133.94, "nameOrig": "C905080434",
     "oldbalanceOrg": 229133.94, "newbalanceOrig": 0.0, "nameDest": "C476402209",
     "oldbalanceDest": 0.0, "newbalanceDest": 0.0, "isFraud": 1},
    {"step": 10, "type": "PAYMENT", "amount": 4024.36, "nameOrig": "C1900366749",
     "oldbalanceOrg": 4024.36, "newbalanceOrig": 0.0, "nameDest": "M1655451712",
     "oldbalanceDest": 0.0, "newbalanceDest": 0.0, "isFraud": 0},
    {"step": 12, "type": "CASH_OUT", "amount": 341558.86, "nameOrig": "C724331414",
     "oldbalanceOrg": 341558.86, "newbalanceOrig": 0.0, "nameDest": "C1650180099",
     "oldbalanceDest": 0.0, "newbalanceDest": 341558.86, "isFraud": 1},
    {"step": 20, "type": "DEBIT", "amount": 2875.1, "nameOrig": "C1900228700",
     "oldbalanceOrg": 5325.0, "newbalanceOrig": 2449.9, "nameDest": "C1350338152",
     "oldbalanceDest": 25136.0, "newbalanceDest": 28011.1, "isFraud": 0},
    {"step": 30, "type": "PAYMENT", "amount": 5250.13, "nameOrig": "C1444526120",
     "oldbalanceOrg": 40000.0, "newbalanceOrig": 34749.87, "nameDest": "M773518316",
     "oldbalanceDest": 0.0, "newbalanceDest": 0.0, "isFraud": 0},
    {"step": 40, "type": "TRANSFER", "amount": 900000.0, "nameOrig": "C1912850431",
     "oldbalanceOrg": 900000.0, "newbalanceOrig": 0.0, "nameDest": "C998823152",
     "oldbalanceDest": 0.0, "newbalanceDest": 0.0, "isFraud": 1},
    {"step": 50, "type": "CASH_IN", "amount": 12000.0, "nameOrig": "C1029346655",
     "oldbalanceOrg": 8000.0, "newbalanceOrig": 20000.0, "nameDest": "C1029346656",
     "oldbalanceDest": 5000.0, "newbalanceDest": 0.0, "isFraud": 0},
]


def run_pipeline(paysim_row, row_index):
    """Runs one transaction through the five per-transaction agents, in order."""
    txn = clean_transaction(map_paysim_row(paysim_row, row_index))
    txn = spot_pattern(txn)
    txn = rule_checking_agent(txn)
    txn = make_decision(txn)
    txn = take_action(txn)
    return txn


# =======================================================================
# Session state
# =======================================================================
if "accounts" not in st.session_state:
    st.session_state.accounts = {
        "Amaka Johnson": {"id": "C1000001", "balance": 500000.0},
        "Tunde Bakare": {"id": "C1000002", "balance": 250000.0},
        "Chidi Okafor": {"id": "C1000003", "balance": 1000000.0},
    }
if "active_account" not in st.session_state:
    st.session_state.active_account = "Amaka Johnson"
if "history" not in st.session_state:
    st.session_state.history = []
if "step_counter" not in st.session_state:
    st.session_state.step_counter = 1
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"
if "last_batch_report" not in st.session_state:
    st.session_state.last_batch_report = None
if "last_batch_df" not in st.session_state:
    st.session_state.last_batch_df = None


# =======================================================================
# Sidebar navigation
# =======================================================================
NAV_ITEMS = [
    ("Dashboard", "\U0001F3E0"),
    ("New Transaction", "\u2795"),
    ("Transactions", "\U0001F4CB"),
    ("Fraud Alerts", "\U0001F514"),
    ("Model Evaluation", "\U0001F9EA"),
    ("Agent Architecture", "\U0001F578\uFE0F"),
    ("System Audit", "\U0001F4C4"),
    ("Settings", "\u2699\uFE0F"),
]

with st.sidebar:
    st.markdown(
        """
        <div class="brand-row">
            <div class="brand-icon">\U0001F6E1\uFE0F</div>
            <div>
                <div class="brand-title">FraudGuard</div>
                <div class="brand-sub">Fraud Detection System</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    n_alerts = sum(1 for t in st.session_state.history if t["final_decision"] in ("flag", "block"))

    for label, icon in NAV_ITEMS:
        is_active = st.session_state.page == label
        badge = f"  ({n_alerts})" if label == "Fraud Alerts" and n_alerts else ""
        button_label = f"{icon}   {label}{badge}"
        if is_active:
            # Rendered as static HTML, not a real button, so the active
            # item never needs its own wrapper div (and the gap that
            # would come with it) - it's just a styled row.
            st.markdown(
                f'<div class="nav-item-active">{button_label}</div>',
                unsafe_allow_html=True,
            )
        else:
            if st.button(button_label, key=f"nav_{label}", width="stretch"):
                st.session_state.page = label
                st.rerun()

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    blocked_ct = sum(1 for t in st.session_state.history if t["final_decision"] == "block")
    st.markdown(
        f"""
        <div class="sidebar-status-box">
            <div class="label">System Status</div>
            <div class="row"><span class="status-dot"></span>All Systems Operational</div>
            <div class="row muted" style="margin-top:10px;">Model Version</div>
            <div class="row">1.0.0</div>
            <div class="row muted" style="margin-top:10px;">Session Transactions</div>
            <div class="row">{len(st.session_state.history)} processed, {blocked_ct} blocked</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

page = st.session_state.page


# =======================================================================
# Helpers shared across pages
# =======================================================================
def time_ago(iso_timestamp):
    try:
        then = datetime.fromisoformat(iso_timestamp)
    except (ValueError, TypeError):
        return ""
    delta = datetime.now() - then
    seconds = int(delta.total_seconds())
    if seconds < 5:
        return "just now"
    if seconds < 60:
        return f"{seconds}s ago"
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes} min ago" if minutes == 1 else f"{minutes} minutes ago"
    hours = minutes // 60
    return f"{hours}h ago"


def history_df():
    if not st.session_state.history:
        return pd.DataFrame()
    return pd.DataFrame(st.session_state.history)


# =======================================================================
# DASHBOARD
# =======================================================================
if page == "Dashboard":
    ui_theme.page_header(
        "\U0001F4CA", "Dashboard", "Real-time overview of fraud detection system"
    )

    hist = st.session_state.history
    total = len(hist)
    approved = sum(1 for t in hist if t["final_decision"] == "approve")
    flagged = sum(1 for t in hist if t["final_decision"] == "flag")
    blocked = sum(1 for t in hist if t["final_decision"] == "block")
    detection_rate = round(100 * (flagged + blocked) / total, 1) if total else 0.0

    st.markdown('<div class="kpi-row-marker"></div>', unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown(
            ui_theme.metric_card(
                "Total Transactions", f"{total:,}", "\U0001F504",
                ui_theme.PRIMARY_SOFT, ui_theme.PRIMARY,
            ),
            unsafe_allow_html=True,
        )
    with c2:
        pct = round(100 * approved / total, 1) if total else 0
        st.markdown(
            ui_theme.metric_card(
                "Approved", f"{approved:,}", "\u2705",
                ui_theme.GREEN_SOFT, ui_theme.GREEN,
                delta=f"{pct}% of total", delta_dir="neutral",
            ),
            unsafe_allow_html=True,
        )
    with c3:
        pct = round(100 * flagged / total, 1) if total else 0
        st.markdown(
            ui_theme.metric_card(
                "Flagged", f"{flagged:,}", "\U0001F6A9",
                ui_theme.AMBER_SOFT, ui_theme.AMBER,
                delta=f"{pct}% of total", delta_dir="neutral",
            ),
            unsafe_allow_html=True,
        )
    with c4:
        pct = round(100 * blocked / total, 1) if total else 0
        st.markdown(
            ui_theme.metric_card(
                "Blocked", f"{blocked:,}", "\U0001F6E1\uFE0F",
                ui_theme.RED_SOFT, ui_theme.RED,
                delta=f"{pct}% of total", delta_dir="neutral",
            ),
            unsafe_allow_html=True,
        )
    with c5:
        st.markdown(
            ui_theme.metric_card(
                "Detection Rate", f"{detection_rate}%", "\U0001F4C8",
                ui_theme.PRIMARY_SOFT, ui_theme.PRIMARY,
            ),
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 1.6])

    with col_left:
        st.markdown(
            """
            <div class="panel">
                <div class="panel-title">Risk Score Distribution</div>
                <div class="panel-sub">Across all session transactions</div>
            """,
            unsafe_allow_html=True,
        )
        if total:
            low = sum(1 for t in hist if t["ml_score"] < 0.4)
            med = sum(1 for t in hist if 0.4 <= t["ml_score"] < 0.7)
            high = sum(1 for t in hist if t["ml_score"] >= 0.7)
            import plotly.graph_objects as go

            fig = go.Figure(
                data=[
                    go.Pie(
                        labels=["Low Risk (0 - 0.4)", "Medium Risk (0.4 - 0.7)", "High Risk (0.7 - 1.0)"],
                        values=[low, med, high],
                        hole=0.68,
                        marker=dict(colors=[ui_theme.GREEN, ui_theme.AMBER, ui_theme.RED]),
                        textinfo="none",
                        sort=False,
                    )
                ]
            )
            fig.update_layout(
                showlegend=False,
                margin=dict(t=10, b=10, l=10, r=10),
                height=230,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                annotations=[
                    dict(
                        text=f"{round(100*low/total)}%<br><span style='font-size:11px;color:{ui_theme.MUTED}'>Low Risk</span>",
                        x=0.5, y=0.5, font=dict(size=22, color=ui_theme.TEXT), showarrow=False,
                    )
                ],
            )
            st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

            for label, count, color in [
                ("Low Risk (0 - 0.4)", low, ui_theme.GREEN),
                ("Medium Risk (0.4 - 0.7)", med, ui_theme.AMBER),
                ("High Risk (0.7 - 1.0)", high, ui_theme.RED),
            ]:
                st.markdown(
                    f"""
                    <div style="display:flex; align-items:center; justify-content:space-between; padding:6px 2px;">
                        <div style="display:flex; align-items:center; gap:8px; font-size:13px; color:{ui_theme.TEXT};">
                            <span style="width:9px;height:9px;border-radius:50%;background:{color};display:inline-block;"></span>
                            {label}
                        </div>
                        <div style="font-size:13px; font-weight:700; color:{ui_theme.TEXT};">{count}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                """
                <div class="empty-state">
                    <div class="emoji">\U0001F4CA</div>
                    Send a transaction to see risk distribution
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown(
            """
            <div class="panel">
                <div class="panel-title">Transaction Trend</div>
                <div class="panel-sub">This session, in submission order</div>
            """,
            unsafe_allow_html=True,
        )
        if total:
            df = history_df().reset_index(drop=True)
            df["order"] = range(1, len(df) + 1)
            df["is_flagged"] = (df["final_decision"] == "flag").astype(int)
            df["is_blocked"] = (df["final_decision"] == "block").astype(int)
            df["cum_flagged"] = df["is_flagged"].cumsum()
            df["cum_blocked"] = df["is_blocked"].cumsum()

            import plotly.graph_objects as go

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df["order"], y=df["order"], mode="lines+markers", name="Transactions",
                line=dict(color=ui_theme.BLUE, width=2.5), marker=dict(size=5),
            ))
            fig.add_trace(go.Scatter(
                x=df["order"], y=df["cum_flagged"], mode="lines+markers", name="Flagged",
                line=dict(color=ui_theme.AMBER, width=2.5), marker=dict(size=5),
            ))
            fig.add_trace(go.Scatter(
                x=df["order"], y=df["cum_blocked"], mode="lines+markers", name="Blocked",
                line=dict(color=ui_theme.RED, width=2.5), marker=dict(size=5),
            ))
            fig.update_layout(
                height=290,
                margin=dict(t=10, b=10, l=10, r=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, font=dict(color=ui_theme.MUTED)),
                xaxis=dict(title="Transaction #", gridcolor=ui_theme.PANEL_BORDER, color=ui_theme.MUTED),
                yaxis=dict(title="Cumulative count", gridcolor=ui_theme.PANEL_BORDER, color=ui_theme.MUTED),
            )
            st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
        else:
            st.markdown(
                """
                <div class="empty-state" style="padding-top:80px;">
                    <div class="emoji">\U0001F4C8</div>
                    No transactions yet this session
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

    col_a, col_b = st.columns([1, 1.6])

    with col_a:
        st.markdown(
            """
            <div class="panel">
                <div class="panel-title">Recent Alerts</div>
                <div class="panel-sub">Flagged and blocked transactions</div>
            """,
            unsafe_allow_html=True,
        )
        alerts = [t for t in reversed(hist) if t["final_decision"] in ("flag", "block")][:5]
        if alerts:
            for t in alerts:
                badge_class = "badge-block" if t["final_decision"] == "block" else "badge-flag"
                badge_text = "HIGH RISK" if t["ml_score"] >= 0.7 else t["final_decision"].upper()
                st.markdown(
                    f"""
                    <div class="alert-row">
                        <span class="badge {badge_class}">{badge_text}</span>
                        <div class="alert-meta">
                            <div class="alert-txn">{t['transaction_id']}</div>
                            <div class="alert-amt">\u20A6{t['amount']:,.2f}</div>
                        </div>
                        <div class="alert-time">{time_ago(t.get('action_timestamp',''))}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            n_active = sum(1 for t in hist if t["final_decision"] in ("flag", "block"))
            st.markdown(
                f"<div style='padding-top:10px; color:{ui_theme.RED}; font-size:13px; font-weight:600;'>{n_active} active alert{'s' if n_active != 1 else ''}</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """
                <div class="empty-state">
                    <div class="emoji">\u2705</div>
                    No alerts yet — all clear
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

    with col_b:
        st.markdown(
            """
            <div class="panel">
                <div class="panel-title">Recent Transactions</div>
                <div class="panel-sub">Latest activity across all accounts</div>
            """,
            unsafe_allow_html=True,
        )
        recent = list(reversed(hist))[:6]
        if recent:
            rows_html = ""
            for t in recent:
                rows_html += f"""
                <tr>
                    <td style="padding:9px 6px; font-size:12.5px; color:{ui_theme.TEXT}; font-weight:600;">{t['transaction_id']}</td>
                    <td style="padding:9px 6px; font-size:12.5px; color:{ui_theme.MUTED};">{t['sender_id']}</td>
                    <td style="padding:9px 6px; font-size:12.5px; color:{ui_theme.MUTED};">{t['receiver_id']}</td>
                    <td style="padding:9px 6px; font-size:12.5px; color:{ui_theme.TEXT};">\u20A6{t['amount']:,.2f}</td>
                    <td style="padding:9px 6px;">{ui_theme.risk_pill(t['ml_score'])}</td>
                    <td style="padding:9px 6px;">{ui_theme.decision_badge(t['final_decision'])}</td>
                </tr>
                """
            st.markdown(
                f"""
                <table style="width:100%; border-collapse:collapse;">
                    <thead>
                        <tr style="border-bottom:1px solid {ui_theme.PANEL_BORDER};">
                            <th style="text-align:left; padding:6px; font-size:11px; color:{ui_theme.MUTED}; text-transform:uppercase;">Transaction</th>
                            <th style="text-align:left; padding:6px; font-size:11px; color:{ui_theme.MUTED}; text-transform:uppercase;">From</th>
                            <th style="text-align:left; padding:6px; font-size:11px; color:{ui_theme.MUTED}; text-transform:uppercase;">To</th>
                            <th style="text-align:left; padding:6px; font-size:11px; color:{ui_theme.MUTED}; text-transform:uppercase;">Amount</th>
                            <th style="text-align:left; padding:6px; font-size:11px; color:{ui_theme.MUTED}; text-transform:uppercase;">Risk</th>
                            <th style="text-align:left; padding:6px; font-size:11px; color:{ui_theme.MUTED}; text-transform:uppercase;">Decision</th>
                        </tr>
                    </thead>
                    <tbody>{rows_html}</tbody>
                </table>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """
                <div class="empty-state">
                    <div class="emoji">\U0001F4B3</div>
                    No transactions yet — try New Transaction
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)


# =======================================================================
# NEW TRANSACTION  (Live Simulation)
# =======================================================================
elif page == "New Transaction":
    ui_theme.page_header(
        "\u2795", "New Transaction", "Submit a transaction and watch all five agents process it, one by one"
    )

    form_col, info_col = st.columns([1.15, 1])

    with form_col:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown(
            f'<div class="panel-title">Transaction details</div>'
            f'<div class="panel-sub">This is what the Data Cleaning Agent will receive</div>',
            unsafe_allow_html=True,
        )

        sender_name = st.selectbox(
            "Sending account", list(st.session_state.accounts.keys()),
            index=list(st.session_state.accounts.keys()).index(st.session_state.active_account),
        )
        st.session_state.active_account = sender_name
        sender = st.session_state.accounts[sender_name]

        st.markdown(
            f"""
            <div style="font-size:12.5px; color:{ui_theme.MUTED}; margin:-4px 0 14px 0;">
                Available balance: <b style="color:{ui_theme.TEXT};">\u20A6{sender['balance']:,.2f}</b>
            </div>
            """,
            unsafe_allow_html=True,
        )

        destination_type = st.radio(
            "Send to",
            ["Another FraudGuard account (internal)", "An external account (outside the bank)"],
        )
        if destination_type.startswith("Another"):
            other_names = [n for n in st.session_state.accounts if n != sender_name]
            receiver_name = st.selectbox("Recipient", other_names)
            receiver_id = st.session_state.accounts[receiver_name]["id"]
            receiver_type_label = "internal"
        else:
            if "external_ref" not in st.session_state:
                st.session_state.external_ref = "M" + str(random.randint(1000000, 9999999))
            receiver_id = st.session_state.external_ref
            receiver_type_label = "external"
            st.caption(f"External account reference: {receiver_id}")

        amount = st.number_input(
            "Amount (NGN)", min_value=1.0, max_value=sender["balance"], step=100.0
        )
        hour = st.slider(
            "Hour of day", 0, 23, datetime.now().hour,
            help="The Rule Checking Agent flags transactions between 12:00 AM and 4:59 AM as an odd-hour risk signal.",
        )
        st.caption(
            f"Rule Checking Agent will see this as **{'an odd hour (12am–4:59am)' if hour <= 4 else 'a normal hour'}**, "
            f"and this amount as **{'a large transaction (≥ ₦100,000)' if amount >= 100000 else 'a normal-sized transaction'}**."
        )

        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
        send_clicked = st.button("Send Transaction", type="primary")
        st.markdown("</div>", unsafe_allow_html=True)

    with info_col:
        st.markdown(
            f"""
            <div class="panel" style="height:100%;">
                <div class="panel-title">What happens when you click Send</div>
                <div class="panel-sub">Every transaction passes through the same five agents, in this order</div>
                <div style="margin-top:6px; font-size:13px; color:{ui_theme.MUTED}; line-height:2.3;">
                    <b style="color:{ui_theme.TEXT};">1. Data Cleaning</b> — validates format, IDs, and duplicates<br>
                    <b style="color:{ui_theme.TEXT};">2. Pattern Spotting</b> — Random Forest model scores fraud risk (0–1)<br>
                    <b style="color:{ui_theme.TEXT};">3. Rule Checking</b> — checks blacklists, large amounts, drained balances, odd hours<br>
                    <b style="color:{ui_theme.TEXT};">4. Decision</b> — combines the ML score and rule verdict into one call<br>
                    <b style="color:{ui_theme.TEXT};">5. Action</b> — approves, flags for review, or blocks and logs it
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if send_clicked:
        new_balance = sender["balance"] - amount
        forced_time = datetime(2026, 1, 1, hour, 0, 0)

        paysim_row = {
            "step": st.session_state.step_counter,
            "type": "TRANSFER" if receiver_type_label == "internal" else "CASH_OUT",
            "amount": amount,
            "nameOrig": sender["id"],
            "oldbalanceOrg": sender["balance"],
            "newbalanceOrig": new_balance,
            "nameDest": receiver_id,
            "oldbalanceDest": 0.0,
            "newbalanceDest": amount if receiver_type_label == "internal" else 0.0,
        }

        mapped = map_paysim_row(paysim_row, st.session_state.step_counter)
        mapped["timestamp"] = forced_time.strftime("%Y-%m-%d %H:%M:%S")

        cleaned = clean_transaction(mapped)
        after_pattern = spot_pattern(dict(cleaned))
        after_rules = rule_checking_agent(dict(after_pattern))
        after_decision = make_decision(dict(after_rules))
        result = take_action(dict(after_decision))
        st.session_state.step_counter += 1

        # ---- Live-looking, agent-by-agent pipeline trace ----
        st.markdown("<div style='height:22px'></div>", unsafe_allow_html=True)
        st.markdown(
            f'<div class="panel-title" style="margin-bottom:2px;">Agent Pipeline Trace</div>'
            f'<div class="panel-sub" style="margin-bottom:16px;">Transaction {result["transaction_id"]} — \u20A6{amount:,.2f} from {sender_name}</div>',
            unsafe_allow_html=True,
        )

        step_placeholders = [st.empty() for _ in range(5)]
        import time as _time

        # Step 1: Data Cleaning
        step_placeholders[0].markdown(
            ui_theme.trace_step(
                "\u2713" if cleaned["is_clean"] else "\u2717",
                "pass" if cleaned["is_clean"] else "fail",
                "1. Data Cleaning Agent", "data_cleaning_agent.py",
                (
                    f'Validated transaction ID, sender/receiver IDs, amount, balance and timestamp format. '
                    f'Result: <b>{"clean, all fields valid" if cleaned["is_clean"] else "rejected — malformed or duplicate data"}</b> '
                    f'<span class="trace-kv"><span class="k">is_clean</span> {cleaned["is_clean"]}</span>'
                ),
            ),
            unsafe_allow_html=True,
        )
        _time.sleep(0.35)

        # Step 2: Pattern Spotting
        ml_score = after_pattern["ml_score"]
        ml_status = "fail" if ml_score >= 0.7 else ("warn" if ml_score >= 0.4 else "pass")
        step_placeholders[1].markdown(
            ui_theme.trace_step(
                "\U0001F9E0", ml_status,
                "2. Pattern Spotting Agent", "pattern_agent.py",
                (
                    f'Ran the trained Random Forest model on this transaction\'s amount, balances, and type. '
                    f'Fraud likelihood: {ui_theme.risk_pill(ml_score)} '
                    f'<span style="color:{ui_theme.MUTED};">({"high" if ml_score>=0.7 else "medium" if ml_score>=0.4 else "low"} risk)</span>'
                ),
            ),
            unsafe_allow_html=True,
        )
        _time.sleep(0.35)

        # Step 3: Rule Checking
        triggered = after_rules["rules_triggered"]
        rules_verdict = after_rules["rules_verdict"]
        rules_status = {"block": "fail", "flag": "warn", "clear": "pass"}[rules_verdict]
        rule_labels = {
            "blacklisted_account": "sender or receiver is blacklisted",
            "large_amount": "amount is ≥ ₦100,000",
            "account_fully_drained": "transaction empties the sender's balance",
            "odd_hour_transaction": "sent between 12:00 AM–4:59 AM",
        }
        if triggered:
            triggered_html = "".join(
                f'<span class="trace-kv">\u26A0\uFE0F {rule_labels.get(r, r)}</span>' for r in triggered
            )
        else:
            triggered_html = f'<span class="trace-kv">no rules triggered</span>'
        step_placeholders[2].markdown(
            ui_theme.trace_step(
                "\U0001F4CB", rules_status,
                "3. Rule Checking Agent", "rule_checking_agent.py",
                (
                    f'Checked against 4 fixed rules (blacklist, large amount, drained balance, odd hour). '
                    f'Rules verdict: <b>{rules_verdict.upper()}</b><br>{triggered_html}'
                ),
            ),
            unsafe_allow_html=True,
        )
        _time.sleep(0.35)

        # Step 4: Decision
        final_decision = after_decision["final_decision"]
        decision_status = {"block": "fail", "flag": "warn", "approve": "pass"}[final_decision]
        step_placeholders[3].markdown(
            ui_theme.trace_step(
                "\u2696\uFE0F", decision_status,
                "4. Decision Agent", "decision_agent.py",
                (
                    f'Combined the ML score ({ml_score:.2f}) and rules verdict (<b>{rules_verdict}</b>) '
                    f'against the threshold ({ML_SCORE_THRESHOLD}). Final decision: {ui_theme.decision_badge(final_decision)}'
                ),
            ),
            unsafe_allow_html=True,
        )
        _time.sleep(0.35)

        # Step 5: Action
        action_status = {"blocked": "fail", "flagged_for_review": "warn", "approved": "pass"}[result["action_taken"]]
        step_placeholders[4].markdown(
            ui_theme.trace_step(
                "\U0001F6E1\uFE0F", action_status,
                "5. Action Agent", "action_agent.py",
                (
                    f'{result["action_message"]}<br>'
                    f'<span class="trace-kv"><span class="k">action_taken</span> {result["action_taken"]}</span>'
                    f'<span class="trace-kv"><span class="k">alert_raised</span> {result["alert_raised"]}</span>'
                ),
                is_last=True,
            ),
            unsafe_allow_html=True,
        )

        # ---- Final verdict banner + account effect ----
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

        if final_decision == "approve":
            sender["balance"] = new_balance
            st.markdown(
                ui_theme.final_verdict_banner(
                    "approve", "Transaction approved",
                    f"\u20A6{amount:,.2f} sent to {receiver_id}. New balance: \u20A6{sender['balance']:,.2f}",
                ),
                unsafe_allow_html=True,
            )
        elif final_decision == "flag":
            st.markdown(
                ui_theme.final_verdict_banner(
                    "flag", "Flagged for verification",
                    "This transaction was suspicious enough to require extra verification before it can proceed.",
                ),
                unsafe_allow_html=True,
            )
            st.info("Enter the 6-digit verification code sent to the account holder (demo code: **123456**).")
            code = st.text_input("Verification code", max_chars=6)
            if code:
                if code == "123456":
                    sender["balance"] = new_balance
                    result["transaction_status"] = "approved_after_verification"
                    st.success(f"Verified — \u20A6{amount:,.2f} sent. New balance: \u20A6{sender['balance']:,.2f}")
                else:
                    st.error("Incorrect code. Transaction blocked and logged.")
                    result["final_decision"] = "block"
                    result["action_taken"] = "blocked_failed_verification"
                    result["transaction_status"] = "blocked"
        else:
            st.markdown(
                ui_theme.final_verdict_banner(
                    "block", "Transaction blocked",
                    "This transaction was not allowed to proceed. It has been logged in System Audit and raised as a fraud alert.",
                ),
                unsafe_allow_html=True,
            )

        st.session_state.history.append(result)

        with st.expander("View raw transaction dictionary (as passed between agents)"):
            st.json(result)


# =======================================================================
# TRANSACTIONS
# =======================================================================
elif page == "Transactions":
    ui_theme.page_header("\U0001F4CB", "Transactions", "Full session transaction log")

    hist = st.session_state.history
    if not hist:
        st.markdown(
            """
            <div class="panel">
                <div class="empty-state">
                    <div class="emoji">\U0001F4B3</div>
                    No transactions yet. Go to New Transaction to try one.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        df = history_df()

        fc1, fc2, fc3 = st.columns([1, 1, 2])
        with fc1:
            decision_filter = st.multiselect(
                "Decision", ["approve", "flag", "block"], default=["approve", "flag", "block"]
            )
        with fc2:
            sort_desc = st.checkbox("Newest first", value=True)
        with fc3:
            search = st.text_input("Search transaction / account ID", "")

        filtered = df[df["final_decision"].isin(decision_filter)]
        if search:
            mask = (
                filtered["transaction_id"].str.contains(search, case=False, na=False)
                | filtered["sender_id"].str.contains(search, case=False, na=False)
                | filtered["receiver_id"].str.contains(search, case=False, na=False)
            )
            filtered = filtered[mask]
        if sort_desc:
            filtered = filtered.iloc[::-1]

        col1, col2, col3 = st.columns(3)
        col1.markdown(ui_theme.metric_card("Approved", str((df["final_decision"] == "approve").sum()), "\u2705", ui_theme.GREEN_SOFT, ui_theme.GREEN), unsafe_allow_html=True)
        col2.markdown(ui_theme.metric_card("Flagged", str((df["final_decision"] == "flag").sum()), "\U0001F6A9", ui_theme.AMBER_SOFT, ui_theme.AMBER), unsafe_allow_html=True)
        col3.markdown(ui_theme.metric_card("Blocked", str((df["final_decision"] == "block").sum()), "\U0001F6E1\uFE0F", ui_theme.RED_SOFT, ui_theme.RED), unsafe_allow_html=True)

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

        display_df = filtered[[
            "transaction_id", "sender_id", "receiver_id", "receiver_type",
            "amount", "ml_score", "rules_verdict", "final_decision",
            "action_taken", "timestamp",
        ]].rename(columns={
            "transaction_id": "Transaction ID", "sender_id": "From", "receiver_id": "To",
            "receiver_type": "Type", "amount": "Amount (NGN)", "ml_score": "Risk Score",
            "rules_verdict": "Rules Verdict", "final_decision": "Decision",
            "action_taken": "Action Taken", "timestamp": "Timestamp",
        })
        st.dataframe(display_df, width="stretch", hide_index=True, height=420)

        csv_buffer = io.StringIO()
        filtered.to_csv(csv_buffer, index=False)
        st.download_button(
            "Download filtered results as CSV", csv_buffer.getvalue(),
            file_name="transactions.csv", mime="text/csv",
        )


# =======================================================================
# FRAUD ALERTS
# =======================================================================
elif page == "Fraud Alerts":
    ui_theme.page_header("\U0001F514", "Fraud Alerts", "Every flagged and blocked transaction this session")

    hist = st.session_state.history
    alerts = [t for t in reversed(hist) if t["final_decision"] in ("flag", "block")]

    if not alerts:
        st.markdown(
            """
            <div class="panel">
                <div class="empty-state">
                    <div class="emoji">\u2705</div>
                    No alerts — every transaction so far has been clean.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        col1, col2 = st.columns(2)
        col1.markdown(ui_theme.metric_card("Flagged", str(sum(1 for a in alerts if a['final_decision']=='flag')), "\U0001F6A9", ui_theme.AMBER_SOFT, ui_theme.AMBER), unsafe_allow_html=True)
        col2.markdown(ui_theme.metric_card("Blocked", str(sum(1 for a in alerts if a['final_decision']=='block')), "\U0001F6E1\uFE0F", ui_theme.RED_SOFT, ui_theme.RED), unsafe_allow_html=True)
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

        for t in alerts:
            severity = "HIGH RISK" if t["ml_score"] >= 0.7 else ("MEDIUM RISK" if t["ml_score"] >= 0.4 else "LOW RISK")
            badge_class = "badge-block" if t["final_decision"] == "block" else "badge-flag"
            with st.expander(f"{t['transaction_id']}  —  \u20A6{t['amount']:,.2f}  —  {t['final_decision'].upper()}"):
                st.markdown(
                    f"""
                    <div style="display:flex; gap:8px; margin-bottom:12px;">
                        <span class="badge {badge_class}">{severity}</span>
                        {ui_theme.decision_badge(t['final_decision'])}
                    </div>
                    <div style="font-size:13.5px; color:{ui_theme.TEXT}; line-height:2;">
                        Sender: <b>{t['sender_id']}</b><br>
                        Receiver: <b>{t['receiver_id']}</b> ({t['receiver_type']})<br>
                        Timestamp: <b>{t['timestamp']}</b><br>
                        ML fraud score: {ui_theme.risk_pill(t['ml_score'])}<br>
                        Rules triggered: <b>{', '.join(t['rules_triggered']) if t['rules_triggered'] else 'none'}</b><br>
                        Rules verdict: <b>{t['rules_verdict']}</b><br>
                        Action taken: <b>{t['action_taken']}</b>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


# =======================================================================
# MODEL EVALUATION  (Batch evaluation through all six agents)
# =======================================================================
elif page == "Model Evaluation":
    ui_theme.page_header(
        "\U0001F9EA", "Model Evaluation",
        "Batch-test all six agents against labelled PaySim-style data"
    )

    st.markdown(
        f"""
        <div class="panel" style="margin-bottom:18px;">
            <div class="panel-title">How this works</div>
            <div class="panel-sub" style="margin-bottom:0;">
                Every row is run through the Data Cleaning, Pattern Spotting, Rule Checking, Decision
                and Action agents, exactly like a real transaction. The Learning Agent then compares
                each final_decision to the row's real <code>isFraud</code> label and reports a confusion
                matrix plus a recommended ML_SCORE_THRESHOLD (current default: {ML_SCORE_THRESHOLD}).
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "Upload a PaySim CSV sample (must include an isFraud column). "
        "If no file is uploaded, a small built-in sample is used instead.",
        type=["csv"],
    )
    max_rows = st.slider("Max rows to evaluate", 10, 2000, 200, step=10)

    if uploaded_file is not None:
        df_in = pd.read_csv(uploaded_file)
        source_label = uploaded_file.name
    else:
        df_in = pd.DataFrame(SAMPLE_BATCH_ROWS)
        source_label = "built-in sample (10 rows, not from the real Kaggle dataset)"

    df_in = df_in.head(max_rows)
    st.caption(f"Evaluating **{len(df_in)}** rows from: {source_label}")

    if st.button("Run batch through all six agents", type="primary"):
        reset_seen_transactions()
        decided_batch = []
        progress = st.progress(0.0)

        for i, (_, row) in enumerate(df_in.iterrows()):
            paysim_row = row.to_dict()
            txn = run_pipeline(paysim_row, i)
            txn["actual_fraud"] = bool(paysim_row.get("isFraud", 0))
            decided_batch.append(txn)
            progress.progress((i + 1) / len(df_in))

        result_df = pd.DataFrame(decided_batch)
        st.session_state.last_batch_df = result_df
        st.session_state.last_batch_report = learning_agent(decided_batch, CURRENT_ML_SCORE_THRESHOLD)

    report = st.session_state.last_batch_report
    result_df = st.session_state.last_batch_df

    if report is not None and result_df is not None:
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        m = report["metrics"]

        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(ui_theme.metric_card("True Positive", str(m["true_positive"]), "\u2705", ui_theme.GREEN_SOFT, ui_theme.GREEN, "Caught fraud"), unsafe_allow_html=True)
        c2.markdown(ui_theme.metric_card("False Positive", str(m["false_positive"]), "\u26A0\uFE0F", ui_theme.AMBER_SOFT, ui_theme.AMBER, "False alarm"), unsafe_allow_html=True)
        c3.markdown(ui_theme.metric_card("True Negative", str(m["true_negative"]), "\u2705", ui_theme.GREEN_SOFT, ui_theme.GREEN, "Correctly cleared"), unsafe_allow_html=True)
        c4.markdown(ui_theme.metric_card("False Negative", str(m["false_negative"]), "\u274C", ui_theme.RED_SOFT, ui_theme.RED, "Missed fraud"), unsafe_allow_html=True)

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

        col_left, col_right = st.columns([1, 1])
        with col_left:
            st.markdown(
                f"""
                <div class="panel">
                    <div class="panel-title">Rates</div>
                    <div style="margin-top:10px; font-size:14px; color:{ui_theme.TEXT}; line-height:2.2;">
                        False positive rate: <b>{m['false_positive_rate']}</b><br>
                        False negative rate: <b>{m['false_negative_rate']}</b>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col_right:
            st.markdown(
                f"""
                <div class="panel">
                    <div class="panel-title">Learning Agent recommendation</div>
                    <div style="margin-top:10px; font-size:14px; color:{ui_theme.TEXT}; line-height:2.2;">
                        Current ML_SCORE_THRESHOLD: <b>{report['old_threshold']}</b><br>
                        Recommended new threshold: <b>{report['new_threshold']}</b><br>
                        <span style="color:{ui_theme.MUTED}; font-size:12.5px;">{report['reason']}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        st.markdown('<div class="panel"><div class="panel-title">Decision breakdown</div>', unsafe_allow_html=True)
        st.bar_chart(result_df["final_decision"].value_counts())
        st.markdown("</div>", unsafe_allow_html=True)

        with st.expander("See per-transaction results"):
            st.dataframe(
                result_df[[
                    "transaction_id", "amount", "ml_score", "rules_verdict",
                    "final_decision", "action_taken", "actual_fraud",
                ]],
                width="stretch",
                hide_index=True,
            )

        csv_buffer = io.StringIO()
        result_df.to_csv(csv_buffer, index=False)
        st.download_button(
            "Download full results as CSV", csv_buffer.getvalue(),
            file_name="batch_evaluation_results.csv", mime="text/csv",
        )


# =======================================================================
# AGENT ARCHITECTURE
# =======================================================================
elif page == "Agent Architecture":
    ui_theme.page_header("\U0001F578\uFE0F", "Agent Architecture", "How the six agents work together")

    agents = [
        ("1", "Data Cleaning Agent", "Validates and repairs the raw transaction (formats, duplicates, missing fields) and marks it is_clean before anything else runs.", "data_cleaning_agent.py"),
        ("2", "Pattern Spotting Agent", "Runs a trained Random Forest model on the transaction's PaySim features and produces ml_score, a 0-1 fraud likelihood.", "pattern_agent.py"),
        ("3", "Rule Checking Agent", "Applies fixed rules — blacklisted accounts, large amounts, drained balances, odd-hour activity — and produces a rules_verdict.", "rule_checking_agent.py"),
        ("4", "Decision Agent", "Combines ml_score and rules_verdict into one final_decision: approve, flag, or block.", "decision_agent.py"),
        ("5", "Action Agent", "Carries out final_decision: approves, flags for review, or blocks and raises an alert. Also keeps the audit log.", "action_agent.py"),
        ("6", "Learning Agent", "Runs periodically on a labelled batch, compares final_decision to real outcomes, and recommends a new ML_SCORE_THRESHOLD.", "learning_agent.py"),
    ]

    for num, name, desc, filename in agents:
        st.markdown(
            f"""
            <div class="agent-card">
                <div><span class="agent-num">{num}</span><span class="agent-name">{name}</span>
                    <span style="float:right; font-size:11.5px; color:{ui_theme.MUTED}; font-family:monospace;">{filename}</span>
                </div>
                <div class="agent-desc">{desc}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="panel">
            <div class="panel-title">Pipeline flow</div>
            <div style="margin-top:12px; font-size:13.5px; color:{ui_theme.MUTED}; text-align:center; letter-spacing:0.02em;">
                Data Cleaning &nbsp;&rarr;&nbsp; Pattern Spotting &nbsp;&rarr;&nbsp; Rule Checking &nbsp;&rarr;&nbsp; Decision &nbsp;&rarr;&nbsp; Action
            </div>
            <div style="margin-top:8px; font-size:12.5px; color:{ui_theme.MUTED}; text-align:center;">
                Learning Agent runs separately, on batches of already-decided transactions, to tune the threshold used by the Decision Agent.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =======================================================================
# SYSTEM AUDIT
# =======================================================================
elif page == "System Audit":
    ui_theme.page_header("\U0001F4C4", "System Audit", "Raw audit log recorded by the Action Agent")

    log = get_action_log()
    if not log:
        st.markdown(
            """
            <div class="panel">
                <div class="empty-state">
                    <div class="emoji">\U0001F4C4</div>
                    No audit entries yet. Every processed transaction is logged here automatically.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        log_df = pd.DataFrame(log).iloc[::-1]
        st.dataframe(log_df, width="stretch", hide_index=True, height=460)
        csv_buffer = io.StringIO()
        log_df.to_csv(csv_buffer, index=False)
        st.download_button(
            "Download audit log as CSV", csv_buffer.getvalue(),
            file_name="audit_log.csv", mime="text/csv",
        )


# =======================================================================
# SETTINGS
# =======================================================================
elif page == "Settings":
    ui_theme.page_header("\u2699\uFE0F", "Settings", "Demo accounts and session controls")

    st.markdown('<div class="panel"><div class="panel-title">Demo Accounts</div>', unsafe_allow_html=True)
    for name, acc in st.session_state.accounts.items():
        st.markdown(
            f"""
            <div style="display:flex; justify-content:space-between; padding:10px 4px; border-bottom:1px solid {ui_theme.PANEL_BORDER}; font-size:14px;">
                <div style="color:{ui_theme.TEXT};">{name} <span style="color:{ui_theme.MUTED}; font-size:12px;">({acc['id']})</span></div>
                <div style="color:{ui_theme.TEXT}; font-weight:700;">\u20A6{acc['balance']:,.2f}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="panel"><div class="panel-title">Session</div>', unsafe_allow_html=True)
    st.caption("Resets balances, transaction history, and audit log. Model and agent logic are unaffected.")
    if st.button("Reset session", type="primary"):
        st.session_state.accounts = {
            "Amaka Johnson": {"id": "C1000001", "balance": 500000.0},
            "Tunde Bakare": {"id": "C1000002", "balance": 250000.0},
            "Chidi Okafor": {"id": "C1000003", "balance": 1000000.0},
        }
        st.session_state.history = []
        st.session_state.step_counter = 1
        st.session_state.last_batch_report = None
        st.session_state.last_batch_df = None
        from action_agent import clear_action_log
        clear_action_log()
        reset_seen_transactions()
        st.success("Session reset.")
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


st.markdown(
    '<div class="footer-note">FraudGuard v1.0.0 &nbsp;|&nbsp; AI-Powered Fraud Detection System &nbsp;|&nbsp; CPE 310 Group 13</div>',
    unsafe_allow_html=True,
)
