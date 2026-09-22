"""Eight-screen Streamlit dashboard entry point."""

import streamlit as st


# ------------------------------------------------------------
# PAGE CONFIGURATION
# ------------------------------------------------------------

st.set_page_config(
    page_title="Nifty 100 Analytics",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ------------------------------------------------------------
# HIDE STREAMLIT SIDEBAR
# ------------------------------------------------------------

st.markdown(
    """
    <style>
        [data-testid="stSidebar"] {
            display: none;
        }

        [data-testid="collapsedControl"] {
            display: none;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ------------------------------------------------------------
# HEADER
# ------------------------------------------------------------

st.title("Nifty 100 Analytics")

st.caption("Market-cap and stock-price data are simulated.")


# ------------------------------------------------------------
# SCREEN NAVIGATION
# ------------------------------------------------------------

choice = st.selectbox(
    "Screen",
    [
        "Home",
        "Company Profile",
        "Screener",
        "Peers",
        "Trends",
        "Sectors",
        "Capital Allocation",
        "Reports",
    ],
)


# ------------------------------------------------------------
# RENDER SELECTED SCREEN
# ------------------------------------------------------------

if choice == "Home":

    from src.dashboard.pages.home import render

    render()


elif choice == "Company Profile":

    from src.dashboard.pages.profile import render

    render()


elif choice == "Screener":

    from src.dashboard.pages.screener import render

    render()


elif choice == "Peers":

    from src.dashboard.pages.peers import render

    render()


elif choice == "Trends":

    from src.dashboard.pages.trends import render

    render()


elif choice == "Sectors":

    from src.dashboard.pages.sectors import render

    render()


elif choice == "Capital Allocation":

    from src.dashboard.pages.capital import render

    render()


elif choice == "Reports":

    from src.dashboard.pages.reports import render

    render()