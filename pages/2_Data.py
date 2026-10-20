import streamlit as st
import pandas as pd
import requests


st.title("Reservoir data")


#cache the data so the API is not called every time the page updates
@st.cache_data
def load_data():

    url = "https://biapi.nve.no/magasinstatistikk/api/Magasinstatistikk/HentOffentligData"

    response = requests.get(url, timeout=30)
    response.raise_for_status()

    #converting the API response into a dataframe
    df = pd.DataFrame(response.json())

    #renaming the column names from norwegian to english
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

    #converts the date column to datetime
    df["date"] = pd.to_datetime(df["date"])

    # sorts the data chronologically
    df = df.sort_values("date")

    return df


df = load_data()


st.write(
    "Select an area type below. The table contains one row for each "
    "column in the dataset. Reservoir variables are shown with small "
    "line charts for each available area number."
)


#lets the user choose the type of reservoir area
selected_type = st.radio(
    "Select area type",
    ["NO", "EL", "VASS"],
    horizontal=True
)


#only keeps data belonging to the selected area type
type_data = df[
    df["area_type"] == selected_type
].copy()


#finds all available area numbers for the selected type
area_numbers = sorted(
    type_data["area_number"].unique()
)


#variables where a line chart is meaningful
chart_columns = [
    "fill_level",
    "capacity_TWh",
    "stored_energy_TWh",
    "fill_level_previous_week",
    "change_in_fill_level"
]


#finding the earliest date for the selected area type
first_date = type_data["date"].min()

#defining the end of the first month
end_first_month = first_date + pd.DateOffset(months=1)


#selecting only rows from the first month
first_month = type_data[
    (type_data["date"] >= first_date) &
    (type_data["date"] < end_first_month)
].copy()


#shows which period is being used
st.write(
    f"First month: {first_date.date()} to {end_first_month.date()}"
)


#creates one row for each column from the dataset
table_rows = []

for column in df.columns:

    row = {
        "Column": column,
        "Data type": str(df[column].dtype)
    }

    #only reservoir measurement variables are shown as line charts
    if column in chart_columns:

        # creates one line chart for each available area number
        for area in area_numbers:

            area_data = first_month[
                first_month["area_number"] == area
            ]

            row[f"Area {area}"] = area_data[column].tolist()

    else:

        #other columns are still included,
        #but line charts are not useful for them
        for area in area_numbers:
            row[f"Area {area}"] = None

    table_rows.append(row)


#converting the rows into a dataframe
summary_table = pd.DataFrame(table_rows)


#configuration for the dataframe columns
column_config = {
    "Column": st.column_config.TextColumn(
        "Column"
    ),

    "Data type": st.column_config.TextColumn(
        "Data type"
    )
}


#adds a LineChartColumn for each available area
for area in area_numbers:

    column_config[f"Area {area}"] = st.column_config.LineChartColumn(
        f"Area {area}",
        help=f"Values from the first month for {selected_type} area {area}"
    )


#displaying the table
st.dataframe(
    summary_table,
    column_config=column_config,
    hide_index=True,
    use_container_width=True
)