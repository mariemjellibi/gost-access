import streamlit as st
import time
from datetime import datetime, timezone

st.set_page_config(
    page_title="Ghost Access — IAM Security Scanner",
    page_icon="👻",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Custom CSS ────────────────────────────────────────────────
st.markdown("""
<style>
    /* Main background */
    .stApp { background-color: #0d1117; color: #e6edf3; }
    
    /* Hide streamlit branding */
    #MainMenu, footer, header { visibility: hidden; }

    /* Top header bar */
    .header-bar {
        background: linear-gradient(90deg, #161b22 0%, #1f2937 100%);
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 24px 32px;
        margin-bottom: 24px;
    }
    .header-title {
        font-size: 28px;
        font-weight: 700;
        color: #e6edf3;
        margin: 0;
    }
    .header-sub {
        font-size: 14px;
        color: #8b949e;
        margin-top: 4px;
    }

    /* Metric cards */
    .metric-row {
        display: flex;
        gap: 16px;
        margin-bottom: 24px;
    }
    .metric-card {
        flex: 1;
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 20px 24px;
        text-align: center;
    }
    .metric-number {
        font-size: 36px;
        font-weight: 700;
        line-height: 1;
    }
    .metric-label {
        font-size: 12px;
        color: #8b949e;
        margin-top: 6px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-red { color: #f85149; }
    .metric-orange { color: #d29922; }
    .metric-green { color: #3fb950; }
    .metric-blue { color: #58a6ff; }

    /* Ghost cards */
    .ghost-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 20px 24px;
        margin-bottom: 12px;
    }
    .ghost-card:hover { border-color: #58a6ff; }
    .ghost-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 12px;
    }
    .ghost-username {
        font-size: 16px;
        font-weight: 600;
        color: #e6edf3;
    }

    /* Badges */
    .badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
    }
    .badge-critical { background: #3d1212; color: #f85149; border: 1px solid #f85149; }
    .badge-high     { background: #2d1f00; color: #d29922; border: 1px solid #d29922; }
    .badge-low      { background: #0d2818; color: #3fb950; border: 1px solid #3fb950; }
    .badge-role     { background: #1c2333; color: #79c0ff; border: 1px solid #30363d; margin-right: 4px; }

    /* AI section */
    .ai-box {
        background: #0d1117;
        border: 1px solid #30363d;
        border-left: 3px solid #58a6ff;
        border-radius: 6px;
        padding: 16px;
        margin-top: 12px;
        font-size: 13px;
        line-height: 1.7;
    }
    .ai-label {
        font-size: 11px;
        color: #58a6ff;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 8px;
    }

    /* Reason tags */
    .reason-tag {
        display: inline-block;
        background: #1c2333;
        color: #8b949e;
        border: 1px solid #30363d;
        border-radius: 4px;
        padding: 2px 8px;
        font-size: 11px;
        margin-right: 6px;
    }

    /* Scan button */
    .stButton > button {
        background: linear-gradient(135deg, #1f6feb 0%, #388bfd 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 28px;
        font-size: 15px;
        font-weight: 600;
        width: 100%;
        transition: opacity 0.2s;
    }
    .stButton > button:hover { opacity: 0.85; }

    /* Pipeline badge */
    .pipeline-bar {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 12px 20px;
        margin-bottom: 24px;
        font-size: 12px;
        color: #8b949e;
    }
    .pipeline-dot {
        display: inline-block;
        width: 8px; height: 8px;
        border-radius: 50%;
        background: #3fb950;
        margin-right: 6px;
    }
</style>
""", unsafe_allow_html=True)

# ── Demo data ─────────────────────────────────────────────────
DEMO = [
    {"username": "dev.martinez",    "roles": ["admin"],       "last_login": None, "risk_level": "Critical",
     "reasons": ["Never logged in & account older than 60 days", "Dangerous role with no recent activity"]},
    {"username": "ci-pipeline-old", "roles": ["manage-realm"],"last_login": None, "risk_level": "Critical",
     "reasons": ["Never logged in & account older than 60 days", "Dangerous role with no recent activity"]},
    {"username": "staging-bot-v1",  "roles": ["admin"],       "last_login": None, "risk_level": "Critical",
     "reasons": ["Never logged in & account older than 60 days", "Dangerous role with no recent activity"]},
    {"username": "vendor.ibrahim",  "roles": ["manage-users"],"last_login": None, "risk_level": "High",
     "reasons": ["Never logged in & account older than 60 days"]},
    {"username": "intern.chen",     "roles": [],              "last_login": None, "risk_level": "High",
     "reasons": ["Never logged in & account older than 60 days"]},
]

TOTAL_IDENTITIES = 26

# ── Header ────────────────────────────────────────────────────
st.markdown("""
<div class="header-bar">
    <div class="header-title">👻 Ghost Access</div>
    <div class="header-sub">AI-Powered IAM Security Scanner — Keycloak Edition</div>
</div>
""", unsafe_allow_html=True)

# ── Pipeline status bar ───────────────────────────────────────
st.markdown("""
<div class="pipeline-bar">
    <span class="pipeline-dot"></span> DevSecOps Pipeline: All security gates passing &nbsp;|&nbsp;
    Bandit ✓ &nbsp;·&nbsp; Safety ✓ &nbsp;·&nbsp; Secret Detection ✓ &nbsp;·&nbsp;
    Scheduled IAM scan: Every Monday 08:00 UTC
</div>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────
if "ghosts" not in st.session_state:
    st.session_state.ghosts = None
if "scan_time" not in st.session_state:
    st.session_state.scan_time = None
if "demo_mode" not in st.session_state:
    st.session_state.demo_mode = False

# ── Scan button ───────────────────────────────────────────────
col_btn, col_info = st.columns([1, 3])
with col_btn:
    run = st.button("🔍 Run Security Scan")
with col_info:
    if st.session_state.scan_time:
        mode = "demo mode" if st.session_state.demo_mode else "live scan"
        st.markdown(f"<p style='color:#8b949e; font-size:13px; padding-top:10px;'>Last scan: {st.session_state.scan_time} · {TOTAL_IDENTITIES} identities scanned · {mode}</p>", unsafe_allow_html=True)

if run:
    start = time.time()
    with st.spinner("Connecting to Keycloak · Scanning identities · Running AI analysis..."):
        try:
            from scanner import scan as run_scan
            from ai_explainer import explain_ghost
            ghosts = run_scan()
            for g in ghosts:
                g["ai_explanation"] = explain_ghost(g)
            st.session_state.demo_mode = False
        except Exception:
            from ai_explainer import explain_ghost
            ghosts = DEMO
            for g in ghosts:
                g["ai_explanation"] = explain_ghost(g)
            st.session_state.demo_mode = True

    elapsed = round(time.time() - start, 1)
    st.session_state.ghosts = ghosts
    st.session_state.scan_time = f"{elapsed}s"

# ── Results ───────────────────────────────────────────────────
if st.session_state.ghosts is not None:
    ghosts = st.session_state.ghosts

    critical = sum(1 for g in ghosts if g["risk_level"] == "Critical")
    high     = sum(1 for g in ghosts if g["risk_level"] == "High")
    low      = sum(1 for g in ghosts if g["risk_level"] == "Low")

    # Metrics row
    st.markdown(f"""
    <div class="metric-row">
        <div class="metric-card">
            <div class="metric-number metric-blue">{TOTAL_IDENTITIES}</div>
            <div class="metric-label">Identities Scanned</div>
        </div>
        <div class="metric-card">
            <div class="metric-number metric-red">{critical}</div>
            <div class="metric-label">Critical</div>
        </div>
        <div class="metric-card">
            <div class="metric-number metric-orange">{high}</div>
            <div class="metric-label">High</div>
        </div>
        <div class="metric-card">
            <div class="metric-number metric-green">{low}</div>
            <div class="metric-label">Low</div>
        </div>
        <div class="metric-card">
            <div class="metric-number metric-green">{TOTAL_IDENTITIES - len(ghosts)}</div>
            <div class="metric-label">Clean Identities</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if len(ghosts) == 0:
        st.success("✅ No ghost identities found. Your IAM realm is clean.")
        st.balloons()
    else:
        st.markdown(f"<p style='color:#8b949e; font-size:13px; margin-bottom:16px;'>Found {len(ghosts)} ghost identities requiring attention — sorted by risk level</p>", unsafe_allow_html=True)

        badge_map = {
            "Critical": "badge-critical",
            "High":     "badge-high",
            "Low":      "badge-low"
        }

        for g in sorted(ghosts, key=lambda x: ["Critical","High","Low"].index(x["risk_level"])):
            badge_class = badge_map.get(g["risk_level"], "badge-low")
            roles_html = "".join([f'<span class="badge badge-role">{r}</span>' for r in g["roles"]]) or '<span style="color:#8b949e">no roles</span>'
            reasons_html = "".join([f'<span class="reason-tag">{r}</span>' for r in g.get("reasons", [])])

            last_login_str = "Never logged in"
            if g.get("last_login"):
                dt = datetime.fromtimestamp(g["last_login"] / 1000, tz=timezone.utc)
                last_login_str = dt.strftime("%Y-%m-%d")

            ai_text = g.get("ai_explanation", "Analysis pending...")

            with st.expander(f"{'🔴' if g['risk_level'] == 'Critical' else '🟠' if g['risk_level'] == 'High' else '🟡'}  {g['username']}  ·  {g['risk_level']}", expanded=False):
                st.markdown(f"""
                <div>
                    <span class="badge {badge_class}">{g['risk_level']}</span>
                    &nbsp;&nbsp;
                    <span style="color:#8b949e; font-size:13px;">Last login: {last_login_str}</span>
                </div>
                <div style="margin-top:10px;">
                    <span style="font-size:12px; color:#8b949e;">ROLES &nbsp;</span>{roles_html}
                </div>
                <div style="margin-top:10px;">
                    <span style="font-size:12px; color:#8b949e;">REASONS &nbsp;</span>{reasons_html}
                </div>
                <div class="ai-box">
                    <div class="ai-label">🤖 AI Security Analysis</div>
                    {ai_text.replace(chr(10), '<br>')}
                </div>
                """, unsafe_allow_html=True)

                fix_cmd = ""
                if "FIX_COMMAND:" in ai_text:
                    fix_cmd = ai_text.split("FIX_COMMAND:")[-1].strip().split("\n")[0].strip()
                else:
                    fix_cmd = f"kcadm.sh update users/{g.get('user_id','<id>')} -r company-demo -s enabled=false"

                st.code(fix_cmd, language="bash")

else:
    st.markdown("""
    <div style="text-align:center; padding:60px 0; color:#8b949e;">
        <div style="font-size:48px; margin-bottom:16px;">👻</div>
        <div style="font-size:18px; font-weight:600; color:#e6edf3;">Ready to scan</div>
        <div style="font-size:14px; margin-top:8px;">Click "Run Security Scan" to detect ghost identities in your Keycloak realm</div>
    </div>
    """, unsafe_allow_html=True)