import streamlit as st

st.title("The dummy page :)")

st.write(
    "This page is just a temporary page so i have 4 pages in this project. Most likely " \
    "it will be updated in the future"
)

st.write(
    "The application uses reservoir data from the reservoirs csv-file "
    "and provides interactive tables and plots for exploring "
    "the dataset as the user wish."
)

st.subheader("Per 29.09.26 there are 4 pages in the dashboard:")

st.write(
    """
    - **Home:** Introduction and navigation
    - **Data:** Overview of the imported reservoir data
    - **Plots:** Interactive visualization of reservoir variables
    - **Dummy page:** Basic information about the project (this site)
    """
)