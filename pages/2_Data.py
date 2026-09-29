import streamlit as st
import pandas as pd


st.title("Reservoir data")


# cache the data so the csv-fil is not read every time, saves time
@st.cache_data
def load_data():
    df = pd.read_csv("data/reservoirs.csv")

    # copying the name changes from the notebook. norwegian => english
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

    # converting date column from text to datetime 
    df["date"] = pd.to_datetime(df["date"])

    # chronologically sorting
    df = df.sort_values("date")

    return df



df = load_data()


st.write(
    "The table below contains one row for each column in the imported dataset. "
    "For numerical variables, the line chart shows values from the first month "
    "of the dataset."
)


# finding the earliest date in the dataset so i can use it
first_date = df["date"].min()

# defining the end of the first month to know where to end it
end_first_month = first_date + pd.DateOffset(months=1)

# selecting only rows from the first month 
first_month = df[
    (df["date"] >= first_date) &
    (df["date"] < end_first_month)
]


# this part shows which period is being used
st.write(
    f"First month: {first_date.date()} to {end_first_month.date()}"
)


# this part creates one row for each column from the dataset
table_rows = []

for column in df.columns:

    # Numerical columns can be shown as small line charts
    if pd.api.types.is_numeric_dtype(df[column]):
        values = first_month[column].tolist()

    else:
        # Text and date columns are still included,
        # but a line chart is not meaningful for these columns
        values = None

    table_rows.append({
        "Column": column,
        "Data type": str(df[column].dtype),
        "First month": values
    })


# converting the rows into a dataframe using dataframe
summary_table = pd.DataFrame(table_rows)


# displaying the table
st.dataframe(
    summary_table,
    column_config={
        "Column": st.column_config.TextColumn(
            "Column"
        ),

        "Data type": st.column_config.TextColumn(
            "Data type"
        ),

        "First month": st.column_config.LineChartColumn(
            "First month",
            help="Values from the first month of the dataset"
        )
    },
    hide_index=True,
    use_container_width=True
)