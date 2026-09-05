"""
ui_theme.py
-----------
Shared visual styling for the FraudGuard app: one CSS injection function,
plus small helpers for the metric cards, badges, and section headers used
across every page. Kept separate from app.py so the page logic stays
readable and the agents remain untouched.
"""

import streamlit as st

# ---------------------------------------------------------------------
# Palette - dark, "security operations center" feel
# ---------------------------------------------------------------------
BG = "#0B0F1A"
PANEL = "#121A2C"
PANEL_BORDER = "#232C42"
TEXT = "#E7EAF3"
MUTED = "#8993A8"
PRIMARY = "#8B5CF6"
PRIMARY_SOFT = "rgba(139, 92, 246, 0.14)"
BLUE = "#3B82F6"
GREEN = "#22C55E"
GREEN_SOFT = "rgba(34, 197, 94, 0.14)"
AMBER = "#F59E0B"
AMBER_SOFT = "rgba(245, 158, 11, 0.14)"
RED = "#EF4444"
RED_SOFT = "rgba(239, 68, 68, 0.14)"


def inject_css():
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }}

        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header[data-testid="stHeader"] {{
            background: transparent;
        }}

        .stApp {{
            background: radial-gradient(circle at 15% 0%, #141c33 0%, {BG} 45%);
        }}

        .block-container {{
            padding-top: 1.6rem;
            padding-bottom: 2.5rem;
            max-width: 1400px;
        }}

        /* ---------------- Sidebar ---------------- */
        section[data-testid="stSidebar"] {{
            background: linear-gradient(180deg, #0E1424 0%, #0A0E19 100%);
            border-right: 1px solid {PANEL_BORDER};
        }}
        section[data-testid="stSidebar"] .block-container {{
            padding-top: 1.4rem;
        }}
        /* Streamlit wraps every element (each button, each markdown call)
           in its own block with a default vertical gap. That's fine in
           the main content area but makes a list of nav buttons look
           like it has a huge gap between each link, especially once the
           sidebar is the only thing on screen on a phone. Collapse it
           down to a small, consistent gap instead. */
        section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {{
            gap: 0.15rem;
        }}
        section[data-testid="stSidebar"] div[data-testid="stElementContainer"] {{
            margin-bottom: 0;
        }}

        .brand-row {{
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 4px 6px 18px 6px;
            margin-bottom: 10px;
            border-bottom: 1px solid {PANEL_BORDER};
        }}
        .brand-icon {{
            width: 38px; height: 38px;
            border-radius: 10px;
            background: linear-gradient(135deg, {PRIMARY} 0%, #6D28D9 100%);
            display: flex; align-items: center; justify-content: center;
            font-size: 19px;
            box-shadow: 0 4px 14px rgba(139, 92, 246, 0.35);
            flex-shrink: 0;
        }}
        .brand-title {{
            font-weight: 800; font-size: 17px; color: {TEXT}; line-height: 1.1;
        }}
        .brand-sub {{
            font-size: 11.5px; color: {MUTED}; margin-top: 1px;
        }}

        /* Sidebar nav buttons */
        section[data-testid="stSidebar"] .stButton {{
            margin: 0 0 3px 0;
        }}
        section[data-testid="stSidebar"] .stButton button {{
            width: 100%;
            text-align: left;
            justify-content: flex-start;
            background: transparent;
            border: 1px solid transparent;
            color: {MUTED};
            font-weight: 500;
            font-size: 14.5px;
            padding: 9px 14px;
            border-radius: 9px;
            margin: 0;
            min-height: 0;
            transition: all 0.15s ease;
        }}
        section[data-testid="stSidebar"] .stButton button:hover {{
            background: {PANEL};
            color: {TEXT};
            border-color: {PANEL_BORDER};
        }}
        section[data-testid="stSidebar"] .stButton button:focus:not(:active) {{
            color: {TEXT};
        }}
        /* Active nav item: rendered as plain HTML (not a real st.button),
           styled to match the button's exact box so the list doesn't
           jump around depending on which page is selected. */
        .nav-item-active {{
            width: 100%;
            box-sizing: border-box;
            text-align: left;
            background: linear-gradient(135deg, {PRIMARY} 0%, #7C3AED 100%);
            color: white;
            font-weight: 600;
            font-size: 14.5px;
            padding: 9px 14px;
            border-radius: 9px;
            margin: 0 0 3px 0;
            box-shadow: 0 4px 14px rgba(139, 92, 246, 0.3);
            white-space: pre;
        }}

        .sidebar-status-box {{
            background: {PANEL};
            border: 1px solid {PANEL_BORDER};
            border-radius: 12px;
            padding: 14px 16px;
            margin-top: 10px;
        }}
        .sidebar-status-box .label {{
            font-size: 10.5px; letter-spacing: 0.06em; color: {MUTED};
            text-transform: uppercase; font-weight: 700; margin-bottom: 8px;
        }}
        .status-dot {{
            display: inline-block; width: 8px; height: 8px; border-radius: 50%;
            background: {GREEN}; margin-right: 7px;
            box-shadow: 0 0 8px {GREEN};
        }}
        .sidebar-status-box .row {{
            font-size: 12.5px; color: {TEXT}; margin: 6px 0;
        }}
        .sidebar-status-box .muted {{
            color: {MUTED}; font-size: 11.5px;
        }}

        /* ---------------- Headers ---------------- */
        .page-header {{
            display: flex; align-items: center; justify-content: space-between;
            margin-bottom: 22px;
        }}
        .page-header-left {{ display: flex; align-items: center; gap: 14px; }}
        .page-icon {{
            width: 46px; height: 46px; border-radius: 12px;
            background: {PRIMARY_SOFT};
            display: flex; align-items: center; justify-content: center;
            font-size: 22px;
            border: 1px solid rgba(139, 92, 246, 0.3);
        }}
        .page-title {{ font-size: 26px; font-weight: 800; color: {TEXT}; line-height: 1.2; }}
        .page-subtitle {{ font-size: 13.5px; color: {MUTED}; margin-top: 1px; }}

        /* ---------------- Metric cards ---------------- */
        .metric-card {{
            background: linear-gradient(155deg, {PANEL} 0%, #0F1626 100%);
            border: 1px solid {PANEL_BORDER};
            border-radius: 14px;
            padding: 18px 20px;
            height: 100%;
            transition: transform 0.15s ease, border-color 0.15s ease;
        }}
        .metric-card:hover {{
            border-color: rgba(139, 92, 246, 0.4);
            transform: translateY(-1px);
        }}
        .metric-top {{
            display: flex; align-items: center; justify-content: space-between;
            margin-bottom: 14px;
        }}
        .metric-label {{
            font-size: 11px; letter-spacing: 0.07em; color: {MUTED};
            text-transform: uppercase; font-weight: 700;
        }}
        .metric-icon {{
            width: 34px; height: 34px; border-radius: 9px;
            display: flex; align-items: center; justify-content: center;
            font-size: 16px; flex-shrink: 0;
        }}
        .metric-value {{
            font-size: 26px; font-weight: 800; color: {TEXT}; line-height: 1;
            margin-bottom: 8px;
        }}
        .metric-delta {{ font-size: 12px; font-weight: 600; }}
        .metric-delta.up {{ color: {GREEN}; }}
        .metric-delta.down {{ color: {RED}; }}
        .metric-delta.neutral {{ color: {MUTED}; }}

        /* ---------------- Panels ---------------- */
        .panel {{
            background: {PANEL};
            border: 1px solid {PANEL_BORDER};
            border-radius: 14px;
            padding: 20px 22px;
            height: 100%;
        }}
        .panel-title {{
            font-size: 15.5px; font-weight: 700; color: {TEXT};
            margin-bottom: 2px;
        }}
        .panel-sub {{ font-size: 12px; color: {MUTED}; margin-bottom: 14px; }}

        /* ---------------- Badges ---------------- */
        .badge {{
            display: inline-block;
            padding: 3px 11px;
            border-radius: 6px;
            font-size: 11.5px;
            font-weight: 700;
            letter-spacing: 0.02em;
        }}
        .badge-block {{ background: {RED_SOFT}; color: {RED}; }}
        .badge-flag {{ background: {AMBER_SOFT}; color: {AMBER}; }}
        .badge-approve {{ background: {GREEN_SOFT}; color: {GREEN}; }}

        .risk-pill {{
            display: inline-block; padding: 2px 10px; border-radius: 6px;
            font-size: 12px; font-weight: 700; font-variant-numeric: tabular-nums;
        }}
        .risk-low {{ background: {GREEN_SOFT}; color: {GREEN}; }}
        .risk-med {{ background: {AMBER_SOFT}; color: {AMBER}; }}
        .risk-high {{ background: {RED_SOFT}; color: {RED}; }}

        /* ---------------- Alert rows ---------------- */
        .alert-row {{
            display: flex; align-items: center; gap: 12px;
            padding: 11px 4px;
            border-bottom: 1px solid {PANEL_BORDER};
        }}
        .alert-row:last-child {{ border-bottom: none; }}
        .alert-meta {{ flex: 1; }}
        .alert-txn {{ font-size: 13.5px; font-weight: 600; color: {TEXT}; }}
        .alert-amt {{ font-size: 12px; color: {MUTED}; }}
        .alert-time {{ font-size: 11.5px; color: {MUTED}; white-space: nowrap; }}

        /* ---------------- Misc ---------------- */
        hr {{ border-color: {PANEL_BORDER} !important; }}

        div[data-testid="stDataFrame"] {{
            border: 1px solid {PANEL_BORDER};
            border-radius: 10px;
            overflow: hidden;
        }}

        .stTabs [data-baseweb="tab-list"] {{
            gap: 4px;
            background: {PANEL};
            padding: 4px;
            border-radius: 10px;
            border: 1px solid {PANEL_BORDER};
        }}
        .stTabs [data-baseweb="tab"] {{
            border-radius: 7px;
            color: {MUTED};
            font-weight: 600;
            font-size: 13.5px;
        }}
        .stTabs [aria-selected="true"] {{
            background: {PRIMARY} !important;
            color: white !important;
        }}

        .stButton button[kind="primary"] {{
            background: linear-gradient(135deg, {PRIMARY} 0%, #7C3AED 100%);
            border: none;
            font-weight: 600;
            box-shadow: 0 4px 14px rgba(139, 92, 246, 0.3);
        }}

        div[data-testid="stMetricValue"] {{ color: {TEXT}; }}

        /* ---------------- Mobile responsiveness ---------------- */
        @media (max-width: 768px) {{
            /* Sidebar opens as a full overlay on top of the page rather
               than pushing content aside on a narrow screen. A shadow
               makes that read as a deliberate drawer, not a glitch. */
            section[data-testid="stSidebar"][aria-expanded="true"] {{
                box-shadow: 8px 0 24px rgba(0,0,0,0.55);
            }}
            .block-container {{
                padding-left: 0.9rem;
                padding-right: 0.9rem;
                padding-top: 1rem;
            }}
            .page-title {{ font-size: 20px; }}
            .page-subtitle {{ font-size: 12.5px; }}
            .page-icon {{ width: 38px; height: 38px; font-size: 18px; }}
            .page-header {{ gap: 10px; margin-bottom: 16px; }}

            /* Dashboard's 5 KPI cards: instead of 5 full-width rows
               stacked one under another (a lot of scrolling for very
               little information density), lay them out 2-across like
               a phone home screen, with the 5th card spanning both
               columns on its own row since 5 doesn't split evenly. */
            div[data-testid="stElementContainer"]:has(.kpi-row-marker)
                + div[data-testid="stLayoutWrapper"] div[data-testid="stHorizontalBlock"] {{
                display: grid !important;
                grid-template-columns: 1fr 1fr;
                gap: 10px;
            }}
            div[data-testid="stElementContainer"]:has(.kpi-row-marker)
                + div[data-testid="stLayoutWrapper"] div[data-testid="stColumn"] {{
                width: 100% !important;
                min-width: 0 !important;
                flex: none !important;
            }}
            div[data-testid="stElementContainer"]:has(.kpi-row-marker)
                + div[data-testid="stLayoutWrapper"] div[data-testid="stColumn"]:last-child {{
                grid-column: 1 / -1;
            }}

            .metric-card {{ padding: 14px 14px; }}
            .metric-value {{ font-size: 21px; margin-bottom: 4px; }}
            .metric-label {{ font-size: 10px; }}
            .metric-icon {{ width: 28px; height: 28px; font-size: 14px; }}
            .metric-top {{ margin-bottom: 8px; }}

            .panel {{ padding: 16px 16px; }}
            .panel-title {{ font-size: 14.5px; }}

            /* Any other two-column row (Risk Distribution / Trend,
               Recent Alerts / Recent Transactions, the New Transaction
               form, etc.) already stacks to full width automatically -
               just tighten the gap between the stacked panels so it
               doesn't feel like separate unrelated sections. */
            div[data-testid="stHorizontalBlock"] {{
                gap: 0.6rem;
            }}
        }}

        .footer-note {{
            text-align: center; color: {MUTED}; font-size: 12px;
            padding-top: 28px; margin-top: 10px;
        }}

        .empty-state {{
            text-align: center; padding: 50px 20px; color: {MUTED};
        }}
        .empty-state .emoji {{ font-size: 40px; margin-bottom: 10px; }}

        .agent-card {{
            background: {PANEL};
            border: 1px solid {PANEL_BORDER};
            border-radius: 14px;
            padding: 18px 20px;
            margin-bottom: 12px;
        }}
        .agent-num {{
            display: inline-flex; align-items: center; justify-content: center;
            width: 26px; height: 26px; border-radius: 7px;
            background: {PRIMARY_SOFT}; color: {PRIMARY};
            font-size: 12.5px; font-weight: 800; margin-right: 10px;
        }}
        .agent-name {{ font-size: 15px; font-weight: 700; color: {TEXT}; }}
        .agent-desc {{ font-size: 12.5px; color: {MUTED}; margin-top: 4px; margin-left: 36px; }}

        /* ---------------- Pipeline trace (New Transaction page) ---------------- */
        .trace-step {{
            display: flex;
            gap: 16px;
            position: relative;
            padding-bottom: 4px;
        }}
        .trace-rail {{
            display: flex; flex-direction: column; align-items: center;
            flex-shrink: 0;
        }}
        .trace-dot {{
            width: 34px; height: 34px; border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            font-size: 16px; font-weight: 800;
            border: 2px solid {PANEL_BORDER};
            background: {PANEL};
            flex-shrink: 0;
            z-index: 1;
        }}
        .trace-dot.pass {{ border-color: {GREEN}; background: {GREEN_SOFT}; }}
        .trace-dot.warn {{ border-color: {AMBER}; background: {AMBER_SOFT}; }}
        .trace-dot.fail {{ border-color: {RED}; background: {RED_SOFT}; }}
        .trace-line {{
            width: 2px; flex: 1; min-height: 18px;
            background: {PANEL_BORDER};
            margin: 2px 0;
        }}
        .trace-card {{
            flex: 1;
            background: {PANEL};
            border: 1px solid {PANEL_BORDER};
            border-radius: 12px;
            padding: 14px 18px;
            margin-bottom: 14px;
        }}
        .trace-card-head {{
            display: flex; align-items: center; justify-content: space-between;
            margin-bottom: 6px;
        }}
        .trace-agent-name {{ font-size: 14.5px; font-weight: 700; color: {TEXT}; }}
        .trace-agent-file {{ font-size: 11px; color: {MUTED}; font-family: monospace; }}
        .trace-verdict {{ font-size: 13px; color: {MUTED}; line-height: 1.6; }}
        .trace-verdict b {{ color: {TEXT}; }}
        .trace-kv {{
            display: inline-flex; gap: 6px; align-items: center;
            background: rgba(255,255,255,0.03);
            border: 1px solid {PANEL_BORDER};
            border-radius: 7px;
            padding: 3px 10px;
            font-size: 12px;
            margin: 2px 6px 2px 0;
            color: {TEXT};
        }}
        .trace-kv .k {{ color: {MUTED}; }}

        .final-verdict-banner {{
            border-radius: 14px;
            padding: 22px 24px;
            margin: 6px 0 18px 0;
            display: flex;
            align-items: center;
            gap: 18px;
        }}
        .final-verdict-banner.approve {{ background: {GREEN_SOFT}; border: 1px solid rgba(34,197,94,0.35); }}
        .final-verdict-banner.flag {{ background: {AMBER_SOFT}; border: 1px solid rgba(245,158,11,0.35); }}
        .final-verdict-banner.block {{ background: {RED_SOFT}; border: 1px solid rgba(239,68,68,0.35); }}
        .final-verdict-icon {{ font-size: 34px; flex-shrink: 0; }}
        .final-verdict-title {{ font-size: 19px; font-weight: 800; color: {TEXT}; margin-bottom: 2px; }}
        .final-verdict-sub {{ font-size: 13px; color: {MUTED}; }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Note: Streamlit has no supported API to collapse the sidebar
    # programmatically after load (open GitHub issue since 2022), and
    # a JS click on the collapse button doesn't work because Streamlit
    # renders custom HTML/JS inside a sandboxed iframe with no access
    # to the parent document. The reliable fix is instead set once in
    # st.set_page_config(initial_sidebar_state="collapsed") in app.py,
    # so the app opens with the main content visible on any screen size
    # and the sidebar is one tap/click away via the "»" control.


def page_header(icon, title, subtitle):
    st.markdown(
        f"""
        <div class="page-header">
            <div class="page-header-left">
                <div class="page-icon">{icon}</div>
                <div>
                    <div class="page-title">{title}</div>
                    <div class="page-subtitle">{subtitle}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label, value, icon, icon_bg, icon_color, delta=None, delta_dir="neutral"):
    delta_html = ""
    if delta:
        arrow = {"up": "&uarr;", "down": "&darr;", "neutral": ""}[delta_dir]
        delta_html = f'<div class="metric-delta {delta_dir}">{arrow} {delta}</div>'
    return f"""
        <div class="metric-card">
            <div class="metric-top">
                <div class="metric-label">{label}</div>
                <div class="metric-icon" style="background:{icon_bg}; color:{icon_color};">{icon}</div>
            </div>
            <div class="metric-value">{value}</div>
            {delta_html}
        </div>
    """


def decision_badge(decision):
    decision = (decision or "").lower()
    if decision == "block":
        return '<span class="badge badge-block">BLOCKED</span>'
    if decision == "flag":
        return '<span class="badge badge-flag">FLAGGED</span>'
    if decision == "approve":
        return '<span class="badge badge-approve">APPROVED</span>'
    return f'<span class="badge">{decision.upper()}</span>'


def trace_step(icon, status, agent_name, filename, body_html, is_last=False):
    """
    One row in the agent pipeline trace: a colored dot + connecting line
    on the left, and a card with the agent's name and what it decided
    on the right. status is 'pass', 'warn', or 'fail'.
    """
    line_html = '<div class="trace-line"></div>' if not is_last else '<div style="width:2px;flex:1;min-height:6px;"></div>'
    return f"""
        <div class="trace-step">
            <div class="trace-rail">
                <div class="trace-dot {status}">{icon}</div>
                {line_html}
            </div>
            <div class="trace-card">
                <div class="trace-card-head">
                    <div class="trace-agent-name">{agent_name}</div>
                    <div class="trace-agent-file">{filename}</div>
                </div>
                <div class="trace-verdict">{body_html}</div>
            </div>
        </div>
    """


def final_verdict_banner(decision, headline, subtext):
    icon = {"approve": "\u2705", "flag": "\U0001F6A9", "block": "\U0001F6D1"}.get(decision, "\u2753")
    return f"""
        <div class="final-verdict-banner {decision}">
            <div class="final-verdict-icon">{icon}</div>
            <div>
                <div class="final-verdict-title">{headline}</div>
                <div class="final-verdict-sub">{subtext}</div>
            </div>
        </div>
    """


def risk_pill(score):
    try:
        score = float(score)
    except (TypeError, ValueError):
        return f'<span class="risk-pill">{score}</span>'
    if score >= 0.7:
        cls = "risk-high"
    elif score >= 0.4:
        cls = "risk-med"
    else:
        cls = "risk-low"
    return f'<span class="risk-pill {cls}">{score:.2f}</span>'
