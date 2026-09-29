import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("Reservoir plots")


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

# the reservoir variables (numerical) used in the plots
plot_columns = [
    "fill_level",
    "capacity_TWh",
    "stored_energy_TWh",
    "fill_level_previous_week",
    "change_in_fill_level"
]

st.write(
    "Use the options below to select a reservoir area, "
    "a variable and timeperiode."
)

# this is the area selection, where the user can select which area they wanna see
areas = sorted(df["area_number"].unique())

selected_area = st.selectbox(
    "Select reservoir area",
    areas
)


# this is important. here i keep only data from the selected area so that only that data occur
area_data = df[df["area_number"] == selected_area].copy()


column_options = ["All columns"] + plot_columns

selected_column = st.selectbox(
    "Select variable",
    column_options
)


# here the user can select what month they want to see

# this part converts every date into a year/month value
area_data["month"] = area_data["date"].dt.to_period("M")

# this part finds all the available months for the selected area 
months = sorted(area_data["month"].unique())

# converts the periods to strings (so the streamlit slider can read it)
month_labels = [str(month) for month in months]


# makeing a default selection as the first month in the dataset
selected_months = st.select_slider(
    "Select month range",
    options=month_labels,
    value=(month_labels[0], month_labels[0])
)


# this part converts the selected slider values back into monthly periods
start_month = pd.Period(selected_months[0], freq="M")
end_month = pd.Period(selected_months[1], freq="M")


# important! this part filters the dataset according to the selected moth
filtered_data = area_data[
    (area_data["month"] >= start_month) &
    (area_data["month"] <= end_month)
].copy()

# here we have the diffrent plots

fig, ax = plt.subplots(figsize=(12, 6))

if selected_column == "All columns":

    # this part copies the selected numerical columns
    normalized_data = filtered_data[plot_columns].copy()

    # normalizing every column between 0 and 1 so that variables with 
    # different scales are comparable.
    for column in plot_columns:
        minimum = normalized_data[column].min()
        maximum = normalized_data[column].max()

        if maximum != minimum:
            normalized_data[column] = (
                normalized_data[column] - minimum
            ) / (
                maximum - minimum
            )
        else:
            # if values are identical, use 0
            normalized_data[column] = 0

    # plotting all normalized columns
    for column in plot_columns:
        ax.plot(
            filtered_data["date"],
            normalized_data[column],
            label=column.replace("_", " ").title()
        )

    ax.set_title(
        f"Normalized Reservoir Variables - Area {selected_area}"
    )

    ax.set_ylabel("Normalized value")

    ax.legend()

else:

    # this part plots only the variables selected by the user
    ax.plot(
        filtered_data["date"],
        filtered_data[selected_column]
    )

    ax.set_title(
        f"{selected_column.replace('_', ' ').title()} "
        f"- Area {selected_area}"
    )

    ax.set_ylabel(
        selected_column.replace("_", " ").title()
    )

ax.set_xlabel("Date")
ax.grid(True)

fig.autofmt_xdate()

st.pyplot(fig)