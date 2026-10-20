import streamlit as st

st.title("The dummy page :)")

st.write(
    "This page is just a temporary page so i have 5 pages in this project. Most likely " \
    "it will be updated in the future"
)

st.write(
    "The application now uses API-data to get the information about the reservoirs "
    "and provides interactive tables and plots for exploring "
    "the dataset as the user wish."
)

st.subheader("Last updated 20.10.26 and there are currently 5 pages in the dashboard:")

st.write(
    """
    - **Home:** Introduction and navigation
    - **Data:** Overview of the imported reservoir data
    - **Plots:** Interactive visualization of reservoir variables
    - **ENTSOE:** Will be used to retrieve cross-border electricity transfer data between Norway and neighbouring countries
    - **Dummy page:** Basic information about the project (this site)
    """
)