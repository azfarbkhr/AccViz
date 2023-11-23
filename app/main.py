import streamlit as st
from utils import load_data, Total_FTP, generate_pnl

st.set_page_config(
    page_title="AccViz: Financial Data Visualization",
    page_icon="$$",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("AccViz: Financial Data Visualization")

# Load data
gl, chart_of_accounts, territory, calendar = load_data()

# Tabs for each sheet
tab1, tab2, tab3, tab4 = st.tabs(["General Ledger", "Chart of Accounts", "Territory", "Profit and Loss Statement"])

with tab1:
    st.write(Total_FTP(gl))
    st.write("General Ledger")
    st.dataframe(gl)

with tab2:
    st.write("Chart of Accounts")
    st.dataframe(chart_of_accounts)

with tab3:
    st.write("Territory")
    st.dataframe(territory)

with tab4:
    st.write(generate_pnl(gl))
