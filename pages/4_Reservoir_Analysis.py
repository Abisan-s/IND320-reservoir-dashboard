import streamlit as st
import pandas as pd
import requests 
import matplotlib.pyplot as plt

from statsmodels.tsa.seasonal import STL
from scipy.signal import spectrogram


#main title for the reservoir analysis page
st.title("Reservoir analysis")

st.write(
    "This page contains time series analysis of the reservoir "
    "filling level using STL decomposition and a spectrogram."
)


#loads the reservoir data
@st.cache_data
def load_reservoir_data():

    url = "https://biapi.nve.no/magasinstatistikk/api/Magasinstatistikk/HentOffentligData"

    response = requests.get(
        url,
        timeout=30
    )

    response.raise_for_status()

    reservoir_data = response.json()

    df = pd.DataFrame(
        reservoir_data
    )
    
    #renames the columns to the english names
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

    #makes sure that the date column is datetime
    df["date"] = pd.to_datetime(
        df["date"]
    )

    return df


reservoir_df = load_reservoir_data()


#lets the user choose the type of reservoir area
selected_type = st.radio(
    "Select area type",
    ["NO", "EL", "VASS"],
    horizontal=True
)


#only keeps data from the selected area type
type_data = reservoir_df[
    reservoir_df["area_type"] == selected_type
].copy()


#available reservoir areas
available_areas = sorted(
    type_data["area_number"].unique()
)


#lets the user choose which reservoir area to analyse
selected_area = st.selectbox(
    "Select reservoir area",
    available_areas
)


#filters the data for the selected area
area_data = type_data[
    type_data["area_number"] == selected_area
].copy()

area_data = area_data.sort_values(
    "date"
)

area_data = area_data[
    ["date", "fill_level"]
].dropna()


#creates a weekly time series
reservoir_series = (
    area_data
    .groupby("date")["fill_level"]
    .mean()
    .sort_index()
    .asfreq("7D")
)

#fills possible small gaps in the weekly data
reservoir_series = reservoir_series.interpolate()


#creates the two analysis tabs
stl_tab, spectrogram_tab = st.tabs(
    [
        "STL decomposition",
        "Spectrogram"
    ]
)

#this is the STL tab part

with stl_tab:

    st.subheader("STL decomposition")

    st.write(
        "STL separates the reservoir filling level into "
        "trend, seasonal variation and residual variation."
    )


    #parameters for the STL decomposition
    seasonal_smoother = st.slider(
        "Seasonal smoother",
        min_value=7,
        max_value=51,
        value=13,
        step=2
    )


    trend_smoother = st.slider(
        "Trend smoother",
        min_value=53,
        max_value=151,
        value=53,
        step=2
    )


    robust = st.checkbox(
        "Use robust STL",
        value=True
    )


    #this part runs the STL decomposition
    stl = STL(
        reservoir_series,
        period=52,
        seasonal=seasonal_smoother,
        trend=trend_smoother,
        robust=robust
    )

    stl_result = stl.fit()


    #creates the STL plot
    stl_fig = stl_result.plot()

    stl_fig.set_size_inches(
        12,
        8
    )

    stl_fig.suptitle(
        f"STL Decomposition - Reservoir Area {selected_area}",
        y=1.02
    )

    st.pyplot(
        stl_fig
    )


    #small summary under plot
    st.write(
        f"Seasonal smoother: **{seasonal_smoother}**  \n"
        f"Trend smoother: **{trend_smoother}**  \n"
        f"Robust decomposition: **{robust}**"
    )

#this is the spectogram part 

with spectrogram_tab:

    st.subheader("Spectrogram")

    st.write(
        "The spectrogram shows how the frequency content "
        "of the reservoir filling level changes over time."
    )


    #parameter for the spectrogram window length
    window_length = st.slider(
        "Window length",
        min_value=32,
        max_value=256,
        value=128,
        step=16
    )


    #the overlap must always be smaller than the window length
    max_overlap = window_length - 1

    default_overlap = min(
        64,
        max_overlap
    )


    overlap = st.slider(
        "Window overlap",
        min_value=0,
        max_value=max_overlap,
        value=default_overlap,
        step=1
    )


    #calculates the spectrogram
    frequencies, times, power = spectrogram(
        reservoir_series.to_numpy(),
        fs=1,
        nperseg=window_length,
        noverlap=overlap
    )


    #creates the spectrogram plot
    spectrogram_fig, ax = plt.subplots(
        figsize=(12, 5)
    )

    mesh = ax.pcolormesh(
        times,
        frequencies,
        power,
        shading="auto"
    )

    ax.set_title(
        f"Spectrogram - Reservoir Area {selected_area}"
    )

    ax.set_xlabel("Time")
    ax.set_ylabel("Frequency")


    spectrogram_fig.colorbar(
        mesh,
        ax=ax,
        label="Power"
    )


    st.pyplot(
        spectrogram_fig
    )


    #small summary under the plot
    st.write(
        f"Window length: **{window_length}**  \n"
        f"Window overlap: **{overlap}**"
    )