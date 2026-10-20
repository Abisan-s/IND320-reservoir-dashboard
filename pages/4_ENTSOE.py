import streamlit as st
from pymongo import MongoClient

#main name for the 4th page
st.title("ENTSO-E Cross border transfers")

#make sure that the mongodb is connected to streamlit
mongo_uri = st.secrets["MONGODB_URI"]

client = MongoClient(mongo_uri)

db = client["ind320"]
collection = db["entsoe_transfers"]

#short explanation about what this page contains
st.write(
    "This page will show cross-border electricity transfers "
    "between Norway and neighbouring countries."
)

#splits the page into two columns
left_column, right_column = st.columns(2)


#left side
with left_column:
    st.subheader("Yearly transfer")

    #lets the user choose which connection they want to see
    connection = st.radio(
        "Select connection",
        ["Norway - Sweden", "Norway - Denmark", "Norway - Germany"]
    )

    #choose which year they want to see
    year = st.selectbox(
        "Select year",
        [2025, 2026]
    )

    #temporary message until entsoe token and data is connected
    st.info(
        "The pie chart will be displayed here soon."
    )


#right side
with right_column:
    st.subheader("Monthly transfer")

    # lets the user choose one or more months
    months = st.pills(
        "Select months",
        [
            "January", "February", "March",
            "April", "May", "June",
            "July", "August", "September",
            "October", "November", "December"
        ],
        selection_mode="multi"
    )

    #temporary message until entose token and data is connected
    st.info(
        "The line plot will be displayed soon"
    )


#just a small expander that gives information about where the data comes from
with st.expander("Data source"):
    st.write(
        "Data source: ENTSO-E Transparency Platform. "
        "Cross border electricity transfer data will be "
        "retrieved through the ENTSO-E web API."
    )