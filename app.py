import streamlit as st
from scanner import scan
from ai_explainer import explain_ghost

st.set_page_config(page_title="Ghost Access", layout="wide")
st.title("👻 Ghost Access – AI Identity Detector")
st.markdown("Scans Keycloak for ghost identities and explains risks with AI.")

DEMO = [
    {"username": "john.smith", "roles": ["admin"], "last_login": 1680000000000, "risk_level": "Critical", "reasons": ["Inactive >60 days", "Dangerous role"]},
    {"username": "ci-bot-v1", "roles": ["manage-realm"], "last_login": None, "risk_level": "Critical", "reasons": ["Never logged in", "Dangerous role"]},
    {"username": "intern_2024", "roles": ["production-group"], "last_login": 1670000000000, "risk_level": "High", "reasons": ["Inactive >60 days"]}
]

if 'ghosts' not in st.session_state:
    st.session_state.ghosts = None

if st.button("🔍 Run Scan", type="primary"):
    with st.spinner("Scanning and analyzing with AI..."):
        try:
            ghosts = scan()
            for g in ghosts:
                g["ai_explanation"] = explain_ghost(g)
            st.session_state.ghosts = ghosts
        except Exception:
            st.warning("Keycloak unreachable – using demo data.")
            st.session_state.ghosts = DEMO
            for g in st.session_state.ghosts:
                g["ai_explanation"] = explain_ghost(g)

if st.session_state.ghosts is not None:
    ghosts = st.session_state.ghosts
    if len(ghosts) == 0:
        st.success("✅ No ghosts found.")
        st.balloons()
    else:
        st.subheader(f"👤 {len(ghosts)} Ghost Identities Detected")
        colors = {"Critical": "🔴", "High": "🟠", "Low": "🟡"}
        for g in ghosts:
            with st.expander(f"{colors.get(g['risk_level'],'⚪')} {g['username']} – {g['risk_level']}"):
                st.write(f"**Roles:** {', '.join(g['roles'])}")
                st.write(f"**Last Login:** {g.get('last_login', 'Never')}")
                st.markdown("---")
                st.markdown("**AI Analysis:**")
                st.code(g.get("ai_explanation", ""))
else:
    st.info("Click 'Run Scan' to begin.")