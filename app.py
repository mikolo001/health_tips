import streamlit as st

st.set_page_config(
    page_title="HealthMate AI",
    page_icon="🩺",
    layout="wide"
)

assistant_page = st.Page(
    "pages/health_ass.py",
    title="Health Assistant",
    icon="💬",
    default=True
)

analyst_page = st.Page(
    "pages/health_analyst.py",
    title="Health Data Analyst",
    icon="📊"
)

navigation = st.navigation(
    [assistant_page, analyst_page],
    position="sidebar"
)

with st.sidebar:
    st.divider()
    st.caption("HealthMate AI")
    st.caption("AI-powered health information and analytics")

navigation.run()
