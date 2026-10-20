import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests

st.title("Reservoir plots")


#cache the data so the API is not called every time the page updates
@st.cache_data
def load_data():

    url = "https://biapi.nve.no/magasinstatistikk/api/Magasinstatistikk/HentOffentligData"

    response = requests.get(url, timeout=30)
    response.raise_for_status()

    df = pd.DataFrame(response.json())

    #norwegian column names => english
    df = df.rename(columns={
        "dato_Id": "date",
        "omrType": "area_type",
        "omrnr": "area_number",
        "iso_aar": "year",
        "iso_uke": "week",
        "fyllingsgrad": "fill_level",
        "kapasitet_TWh": "capacity_TWh",
        "fylling_TWh": "stored_energy_TWh",
        "neste_Publiseringsdato": "next_publication_date",
        "fyllingsgrad_forrige_uke": "fill_level_previous_week",
        "endring_fyllingsgrad": "change_in_fill_level"
    })

    #converting date column to datetime
    df["date"] = pd.to_datetime(df["date"])

    #sorting by date
    df = df.sort_values("date")

    return df


df = load_data()


#numerical variables used in the plots
plot_columns = [
    "fill_level",
    "capacity_TWh",
    "stored_energy_TWh",
    "fill_level_previous_week",
    "change_in_fill_level"
]


st.write(
    "Select an area type, reservoir area, variable and time period."
)


#select the type of reservoir area
selected_type = st.radio(
    "Select area type",
    ["NO", "EL", "VASS"],
    horizontal=True
)


#only keep data belonging to the selected area type
type_data = df[df["area_type"] == selected_type].copy()


#find the available area numbers for the selected type
areas = sorted(type_data["area_number"].unique())

selected_area = st.selectbox(
    "Select reservoir area",
    areas
)


#keep only the selected area
area_data = type_data[
    type_data["area_number"] == selected_area
].copy()


#variable selection
column_options = ["All columns"] + plot_columns

selected_column = st.selectbox(
    "Select variable",
    column_options
)


#convert dates into year and month values
area_data["month"] = area_data["date"].dt.to_period("M")

months = sorted(area_data["month"].unique())

month_labels = [str(month) for month in months]


#default is the first available month
selected_months = st.select_slider(
    "Select month range",
    options=month_labels,
    value=(month_labels[0], month_labels[0])
)


#convert selected values back to periods
start_month = pd.Period(selected_months[0], freq="M")
end_month = pd.Period(selected_months[1], freq="M")


#filter data according to the selected period
filtered_data = area_data[
    (area_data["month"] >= start_month) &
    (area_data["month"] <= end_month)
].copy()


#this part is creating the plot
fig, ax = plt.subplots(figsize=(12, 6))


if selected_column == "All columns":

    normalized_data = filtered_data[plot_columns].copy()

    columns_to_plot = []

    # normalize variables between 0 and 1
    for column in plot_columns:

        minimum = normalized_data[column].min()
        maximum = normalized_data[column].max()

        # only include variables that change in this period
        if maximum != minimum:

            normalized_data[column] = (
                normalized_data[column] - minimum
            ) / (
                maximum - minimum
            )

            columns_to_plot.append(column)


    for column in columns_to_plot:

        ax.plot(
            filtered_data["date"],
            normalized_data[column],
            label=column.replace("_", " ").title()
        )


    ax.set_title(
        f"Normalized Reservoir Variables - "
        f"{selected_type} Area {selected_area}"
    )

    ax.set_ylabel("Normalized value (0-1)")
    ax.set_ylim(0, 1.05)
    ax.legend()


else:

    ax.plot(
        filtered_data["date"],
        filtered_data[selected_column]
    )

    ax.set_title(
        f"{selected_column.replace('_', ' ').title()} - "
        f"{selected_type} Area {selected_area}"
    )

    ax.set_ylabel(
        selected_column.replace("_", " ").title()
    )


ax.set_xlabel("Date")
ax.grid(True)

fig.autofmt_xdate()

st.pyplot(fig)