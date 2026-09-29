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
    "This dashboard presents the reservoir data from the IND320 project. This is just the start and " \
    "i will try to make this site better by each assignment"
)

# sidebar information that tells to navigate between the pages
st.sidebar.title("Navigation")
st.sidebar.write("Use the menu to navigate between the pages.")