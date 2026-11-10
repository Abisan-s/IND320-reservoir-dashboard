import streamlit as st

# initial start for the streamlist page
st.set_page_config(
    page_title="IND320 dashboard",
    page_icon="🏞️",
    layout="wide"
)

# the title that is shown on the page
st.title("IND320 - Reservoir dashboard")

# description of what this site is
st.write(
    "The application now uses API-data to get the information about the reservoirs "
    "and provides interactive tables and plots for exploring "
    "the dataset as the user wish."
)

st.subheader("Last updated 10.11.26 and there are currently 6 pages in the dashboard:")

st.write(
    """
   - **app:** Introduction and navigation
   - **Data:** Overview of the imported reservoir data
   - **Plots:** Interactive visualization of reservoir variables
   - **Reservoir Analysis:** STL decomposition and spectrogram analysis of reservoir filling levels
   - **Weather Analysis:** SPC outlier analysis for precipitation and LOF anomaly detection for temperature
   - **ENTSOE:** Cross-border electricity transfer data between Norway and neighbouring countries

    """
)
# sidebar information that tells to navigate between the pages
st.sidebar.title("Navigation")
st.sidebar.write("Use the menu to navigate between the pages.")