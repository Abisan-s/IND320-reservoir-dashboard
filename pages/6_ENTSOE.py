import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pymongo import MongoClient


#main name for the 4th page
st.title("ENTSO-E Cross border transfers")


# connect streamlit to mongodb using secrets
mongo_uri = st.secrets["MONGODB_URI"]

client = MongoClient(mongo_uri)

db = client["ind320"]
collection = db["entsoe_transfers"]


#load entsoe data from mongodb and cache it to save time and resources
@st.cache_data
def load_entsoe_data():

    data = list(
        collection.find(
            {},
            {"_id": 0}
        )
    )

    df = pd.DataFrame(data)

    if not df.empty:
        df["datetime"] = pd.to_datetime(df["datetime"])

    return df


df = load_entsoe_data()


#short explanation about what this page contains
st.write(
    "This page shows cross-border electricity transfers "
    "between Norway and neighbouring countries using data "
    "from the ENTSO-E transparency website."
)


#double check to make sure that data was loaded
if df.empty:

    st.error("No ENTSO-E data was found in MongoDB.")
    st.stop()


#available connections from mongodb
available_connections = sorted(
    df["connection"].unique()
)


#available years from mongodb
available_years = sorted(
    df["datetime"].dt.year.unique()
)


#splits the page into two columns
left_column, right_column = st.columns([1, 1.2])

#leftside - yearly data

with left_column:

    st.subheader("Yearly transfer")


    #this lets the user choose which connection they want to see
    connection = st.radio(
        "Select connection",
        available_connections
    )


    #choose which year they want to see
    year = st.selectbox(
        "Select year",
        available_years
    )


    #filtering selected connection and year
    yearly_data = df[
        (df["connection"] == connection) &
        (df["datetime"].dt.year == year)
    ].copy()


    if yearly_data.empty:

        st.warning(
            "No data is available for this connection and year."
        )

    else:

        #calculates total flow for each direction
        yearly_summary = (
            yearly_data
            .groupby("direction")["flow_mw"]
            .sum()
        )

        fig1, ax1 = plt.subplots(
            figsize=(7, 7)
        )

        ax1.pie(
            yearly_summary.values,
            labels=yearly_summary.index,
            autopct="%1.1f%%"
        )

        ax1.set_title(
            f"Yearly electricity transfer - {connection} ({year})"
        )

        st.pyplot(fig1)

#right side - monthly data

with right_column:

    st.subheader("Monthly transfer")


    #lets the user choose one or more months
    first_half = st.pills(
        "Select months",
        [
            "January", "February", "March",
            "April", "May", "June"
        ],
        selection_mode="multi",
        key="months_first_half"
    )

    second_half = st.pills(
        "",
        [
            "July", "August", "September",
            "October", "November", "December"
        ],
        selection_mode="multi",
        key="months_second_half"
    )

    months = first_half + second_half


    #data for selected connection and year
    monthly_data = df[
        (df["connection"] == connection) &
        (df["datetime"].dt.year == year)
    ].copy()

    monthly_data["month"] = monthly_data[
        "datetime"
    ].dt.month_name()


    #filter selected months
    if months:

        monthly_data = monthly_data[
            monthly_data["month"].isin(months)
        ]


        if monthly_data.empty:

            st.warning(
                "No data is available for the selected months."
            )

        else:

            # sort data before plotting
            monthly_data = monthly_data.sort_values(
                "datetime"
            )


            # line plot
            fig2, ax2 = plt.subplots(
                figsize=(10, 5)
            )


            # creates one line for each direction
            for direction, group in monthly_data.groupby(
                "direction"
            ):

                group = group.sort_values(
                    "datetime"
                )

                ax2.plot(
                    group["datetime"],
                    group["flow_mw"],
                    label=direction
                )


            ax2.set_title(
                f"Electricity flow - {connection} ({year})"
            )

            ax2.set_xlabel("Date")
            ax2.set_ylabel("Flow (MW)")

            ax2.legend()
            ax2.grid(True)

            fig2.autofmt_xdate()

            st.pyplot(fig2)

    else:

        st.info(
            "Select one or more months to display the line plot."
        )


#information about where the data comes from
with st.expander("Data source"):

    st.write(
        "Data source: ENTSO-E Transparency Platform. "
        "The cross-border electricity transfer data is retrieved "
        "through the ENTSO-E web API, processed with Spark and "
        "stored in MongoDB before being displayed in this Streamlit app."
    )