import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests

from scipy.fft import dct, idct
from sklearn.neighbors import LocalOutlierFactor


#main title for the page
st.title("Weather analysis")

st.write(
    "This page analyses historical weather data from Open-Meteo "
    "using SPC outlier detection for precipitation and LOF "
    "anomaly detection for temperature."
)


#loads the sampled electricity area locations
@st.cache_data
def load_electricity_locations():

    import geopandas as gpd
    from shapely.geometry import Point

    electricity_areas = gpd.read_file(
        "data/shapefiles/electricity_areas/Budområder.shp"
    )

    #converts the shapefile to longitude and latitude
    electricity_areas = electricity_areas.to_crs(
        epsg=4326
    )

    def sample_random_points(
        region_geometry,
        n=1000,
        seed=42
    ):

        np.random.seed(seed)

        min_x, min_y, max_x, max_y = (
            region_geometry.bounds
        )

        points = []

        while len(points) < n:

            random_point = Point(
                np.random.uniform(
                    min_x,
                    max_x
                ),
                np.random.uniform(
                    min_y,
                    max_y
                )
            )

            if region_geometry.contains(
                random_point
            ):
                points.append(
                    random_point
                )

        return points


    electricity_locations = []

    for region in [
        "NO 1",
        "NO 2",
        "NO 3",
        "NO 4",
        "NO 5"
    ]:

        selected_region = electricity_areas[
            electricity_areas["budomr"] == region
        ]

        region_geometry = (
            selected_region
            .geometry
            .union_all()
        )

        points = sample_random_points(
            region_geometry,
            n=1000,
            seed=42
        )

        region_locations = pd.DataFrame({
            "region": region,
            "longitude": [
                point.x for point in points
            ],
            "latitude": [
                point.y for point in points
            ]
        })

        electricity_locations.append(
            region_locations
        )

    return pd.concat(
        electricity_locations,
        ignore_index=True
    )


electricity_locations = load_electricity_locations()


#loads sampled locations for the VASS regions
@st.cache_data
def load_vass_locations():

    import geopandas as gpd
    from shapely.geometry import Point

    nve_regions = gpd.read_file(
        "data/shapefiles/nve_regions/NVE_Region.shp",
        encoding="utf-8"
    )

    nve_regions = nve_regions.to_crs(
        epsg=4326
    )

    def sample_random_points(
        region_geometry,
        n=1000,
        seed=42
    ):

        np.random.seed(seed)

        min_x, min_y, max_x, max_y = (
            region_geometry.bounds
        )

        points = []

        while len(points) < n:

            random_point = Point(
                np.random.uniform(
                    min_x,
                    max_x
                ),
                np.random.uniform(
                    min_y,
                    max_y
                )
            )

            if region_geometry.contains(
                random_point
            ):
                points.append(
                    random_point
                )

        return points


    #combines the NVE subregions into the three VASS areas
    precipitation_regions = {
        "East": nve_regions[
            nve_regions["REGION"].isin(
                ["RS", "RØ"]
            )
        ].geometry.union_all(),

        "West": nve_regions[
            nve_regions["REGION"] == "RV"
        ].geometry.union_all(),

        "North": nve_regions[
            nve_regions["REGION"].isin(
                ["RM", "RN"]
            )
        ].geometry.union_all()
    }


    vass_locations = []

    for region_name, region_geometry in (
        precipitation_regions.items()
    ):

        points = sample_random_points(
            region_geometry,
            n=1000,
            seed=42
        )

        region_locations = pd.DataFrame({
            "region": region_name,
            "longitude": [
                point.x for point in points
            ],
            "latitude": [
                point.y for point in points
            ]
        })

        vass_locations.append(
            region_locations
        )

    return pd.concat(
        vass_locations,
        ignore_index=True
    )


vass_locations = load_vass_locations()


#loads one set of sampled locations covering all of Norway
@st.cache_data
def load_norway_locations():

    import geopandas as gpd
    from shapely.geometry import Point

    electricity_areas = gpd.read_file(
        "data/shapefiles/electricity_areas/Budområder.shp"
    )

    electricity_areas = electricity_areas.to_crs(
        epsg=4326
    )

    norway_geometry = (
        electricity_areas
        .geometry
        .union_all()
    )

    np.random.seed(42)

    min_x, min_y, max_x, max_y = (
        norway_geometry.bounds
    )

    points = []

    while len(points) < 1000:

        random_point = Point(
            np.random.uniform(
                min_x,
                max_x
            ),
            np.random.uniform(
                min_y,
                max_y
            )
        )

        if norway_geometry.contains(
            random_point
        ):
            points.append(
                random_point
            )

    return pd.DataFrame({
        "region": "Norway",
        "longitude": [
            point.x for point in points
        ],
        "latitude": [
            point.y for point in points
        ]
    })


norway_locations = load_norway_locations()


#loads the Magasinstatistikk data so the weather selector uses the same areas
@st.cache_data
def load_reservoir_areas():

    url = (
        "https://biapi.nve.no/magasinstatistikk/"
        "api/Magasinstatistikk/HentOffentligData"
    )

    response = requests.get(
        url,
        timeout=30
    )

    response.raise_for_status()

    df = pd.DataFrame(
        response.json()
    )

    df = df.rename(columns={
        "omrType": "area_type",
        "omrnr": "area_number"
    })

    return df


reservoir_areas = load_reservoir_areas()


#downloads hourly ERA5 weather data for one sampled location
@st.cache_data
def get_weather_data(
    area_type,
    area_number,
    start_date,
    end_date
):

    #uses the selected Magasinstatistikk area to find the matching weather region
    if area_type == "EL":

        region = f"NO {int(area_number)}"

        region_locations = electricity_locations[
            electricity_locations["region"] == region
        ].reset_index(drop=True)


    elif area_type == "VASS":

        vass_mapping = {
            1: "East",
            2: "West",
            3: "North"
        }

        region = vass_mapping.get(
            int(area_number)
        )

        if region is None:
            return pd.DataFrame()

        region_locations = vass_locations[
            vass_locations["region"] == region
        ].reset_index(drop=True)


    elif area_type == "NO":

        region = "Norway"

        region_locations = (
            norway_locations
            .reset_index(drop=True)
        )


    else:

        return pd.DataFrame()


    if region_locations.empty:
        return pd.DataFrame()

    #uses one sampled location from the selected region
    location = region_locations.iloc[0]

    latitude = location["latitude"]
    longitude = location["longitude"]

    url = (
        "https://archive-api.open-meteo.com/v1/archive"
    )

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": str(start_date),
        "end_date": str(end_date),
        "hourly": "temperature_2m,precipitation",
        "models": "era5",
        "timezone": "UTC"
    }

    response = requests.get(
        url,
        params=params,
        timeout=60
    )

    response.raise_for_status()

    weather_json = response.json()

    weather_df = pd.DataFrame(
        weather_json["hourly"]
    )

    weather_df["time"] = pd.to_datetime(
        weather_df["time"]
    )

    weather_df["region"] = region
    weather_df["latitude"] = latitude
    weather_df["longitude"] = longitude

    return weather_df


#lets the user choose the same area type used for Magasinstatistikk
selected_type = st.radio(
    "Select area type",
    ["NO", "EL", "VASS"],
    horizontal=True,
    index=1
)


#only keeps Magasinstatistikk areas belonging to the selected type
type_data = reservoir_areas[
    reservoir_areas["area_type"] == selected_type
].copy()


#finds the available area numbers for the selected type
available_areas = sorted(
    type_data["area_number"].unique()
)


#lets the user choose which electricity area to analyse
selected_area = st.selectbox(
    "Select reservoir area",
    available_areas
)


#shows which geographic weather region is connected to the selection
if selected_type == "EL":

    selected_region = (
        f"NO {int(selected_area)}"
    )

elif selected_type == "VASS":

    vass_mapping = {
        1: "East",
        2: "West",
        3: "North"
    }

    selected_region = vass_mapping.get(
        int(selected_area),
        "Unknown"
    )

else:

    selected_region = "Norway"


st.caption(
    f"Weather region used: {selected_region}"
)


#lets the user select the time period
start_date = st.date_input(
    "Start date",
    value=pd.Timestamp(
        "2024-01-01"
    ).date()
)

end_date = st.date_input(
    "End date",
    value=pd.Timestamp(
        "2024-12-31"
    ).date()
)


if start_date > end_date:

    st.error(
        "The start date must be before the end date."
    )

    st.stop()


#downloads the weather data
try:

    weather_df = get_weather_data(
        selected_type,
        selected_area,
        start_date,
        end_date
    )

except requests.RequestException as error:

    st.error(
        f"Could not download Open-Meteo data: {error}"
    )

    st.stop()


if weather_df.empty:

    st.error(
        "No weather data was found."
    )

    st.stop()


#creates the two weather analysis tabs
spc_tab, lof_tab = st.tabs(
    [
        "Outlier / SPC",
        "Anomaly / LOF"
    ]
)


#this is the SPC outlier tab
with spc_tab:

    st.subheader(
        "Precipitation outlier analysis"
    )

    st.write(
        "The precipitation data is filtered using the "
        "discrete cosine transform (DCT) before SPC boundaries "
        "are used to identify unusual observations."
    )


    #creates daily average precipitation
    daily_precipitation = (
        weather_df
        .set_index("time")["precipitation"]
        .resample("D")
        .mean()
        .reset_index()
    )


    #parameters used for the SPC analysis
    cutoff = st.slider(
        "DCT frequency cutoff",
        min_value=1,
        max_value=50,
        value=10,
        step=1
    )


    n_std = st.slider(
        "Number of robust standard deviations",
        min_value=1.0,
        max_value=5.0,
        value=3.0,
        step=0.5
    )


    precipitation_values = (
        daily_precipitation[
            "precipitation"
        ]
        .to_numpy()
    )


    #transforms the precipitation signal
    precipitation_dct = dct(
        precipitation_values,
        norm="ortho"
    )


    filtered_dct = (
        precipitation_dct.copy()
    )


    #removes low frequency components
    filtered_dct[:cutoff] = 0


    satv = idct(
        filtered_dct,
        norm="ortho"
    )


    daily_precipitation["SATV"] = satv


    #calculates robust statistics using median and MAD
    satv_median = np.median(
        satv
    )


    mad = np.median(
        np.abs(
            satv - satv_median
        )
    )


    robust_std = (
        1.4826 * mad
    )


    lower_boundary = (
        satv_median
        - n_std * robust_std
    )


    upper_boundary = (
        satv_median
        + n_std * robust_std
    )


    #identifies outliers using the SATV values
    daily_precipitation["outlier"] = (
        (
            daily_precipitation["SATV"]
            < lower_boundary
        )
        |
        (
            daily_precipitation["SATV"]
            > upper_boundary
        )
    )


    center_line = (
        daily_precipitation[
            "precipitation"
        ]
        - daily_precipitation["SATV"]
    )


    upper_curve = (
        center_line
        + upper_boundary
    )


    lower_curve = (
        center_line
        + lower_boundary
    )


    #creates the precipitation plot
    fig1, ax1 = plt.subplots(
        figsize=(12, 5)
    )


    ax1.plot(
        daily_precipitation["time"],
        daily_precipitation[
            "precipitation"
        ],
        label="Average precipitation"
    )


    ax1.plot(
        daily_precipitation["time"],
        upper_curve,
        linestyle="--",
        label="Upper SPC boundary"
    )


    ax1.plot(
        daily_precipitation["time"],
        lower_curve,
        linestyle="--",
        label="Lower SPC boundary"
    )


    outliers = daily_precipitation[
        daily_precipitation["outlier"]
    ]


    ax1.scatter(
        outliers["time"],
        outliers["precipitation"],
        label="Outliers",
        zorder=3
    )


    ax1.set_title(
        f"Precipitation SPC Analysis - {selected_region}"
    )

    ax1.set_xlabel("Date")
    ax1.set_ylabel(
        "Precipitation (mm)"
    )

    ax1.legend()
    ax1.grid(True)


    st.pyplot(
        fig1
    )


    #shows a short summary of the SPC analysis
    st.write(
        f"Detected outliers: **{len(outliers)}**  \n"
        f"DCT cutoff: **{cutoff}**  \n"
        f"Robust standard deviations: **{n_std}**"
    )


#this is the LOF anomaly tab

with lof_tab:

    st.subheader(
        "Temperature anomaly analysis"
    )

    st.write(
        "Local Outlier Factor is used to detect unusual "
        "temperature values compared with nearby observations."
    )


    #creates daily average temperature
    daily_temperature = (
        weather_df
        .set_index("time")["temperature_2m"]
        .resample("D")
        .mean()
        .reset_index()
    )


    #lets the user choose the expected proportion of anomalies
    outlier_proportion = st.slider(
        "Proportion of anomalies",
        min_value=0.01,
        max_value=0.10,
        value=0.01,
        step=0.01,
        format="%.2f"
    )


    temperature_values = (
        daily_temperature[
            "temperature_2m"
        ]
        .to_numpy()
        .reshape(-1, 1)
    )


    lof = LocalOutlierFactor(
        contamination=outlier_proportion
    )


    labels = lof.fit_predict(
        temperature_values
    )


    daily_temperature["anomaly"] = (
        labels == -1
    )


    anomalies = daily_temperature[
        daily_temperature["anomaly"]
    ]


    #creates the temperature plot
    fig2, ax2 = plt.subplots(
        figsize=(12, 5)
    )


    ax2.plot(
        daily_temperature["time"],
        daily_temperature[
            "temperature_2m"
        ],
        label="Average temperature"
    )


    ax2.scatter(
        anomalies["time"],
        anomalies["temperature_2m"],
        label="LOF anomalies",
        zorder=3
    )


    ax2.set_title(
        f"Temperature LOF Analysis - {selected_region}"
    )

    ax2.set_xlabel("Date")
    ax2.set_ylabel(
        "Temperature (°C)"
    )

    ax2.legend()
    ax2.grid(True)


    st.pyplot(
        fig2
    )


    #shows a short summary of the LOF analysis
    st.write(
        f"Detected anomalies: **{len(anomalies)}**  \n"
        f"Outlier proportion: **{outlier_proportion:.2%}**"
    )


#information about the weather data source
with st.expander(
    "Data source"
):

    st.write(
        "Historical hourly weather data is retrieved from "
        "the Open-Meteo Historical Weather API using the "
        "ERA5 reanalysis model. The analysis uses temperature "
        "and precipitation data from one sampled location "
        "inside the selected Magasinstatistikk area."
    )