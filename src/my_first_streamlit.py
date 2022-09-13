# my_first_streamlit.py

import pandas as pd
import json
import streamlit as st
import plotly.express as px
import pydeck as pdk

# load in data
with open("./data/georef-switzerland-kanton.geojson") as response:
    geoj = json.load(response)
df = pd.read_csv("./data/renewable_power_plants_CH.csv")

#modify initial dataset
cantons_dict = {'TG':'Thurgau', 'GR':'Graubünden', 'LU':'Luzern', 'BE':'Bern', 'VS':'Valais',
                'BL':'Basel-Landschaft', 'SO':'Solothurn', 'VD':'Vaud', 'SH':'Schaffhausen', 'ZH':'Zürich',
                'AG':'Aargau', 'UR':'Uri', 'NE':'Neuchâtel', 'TI':'Ticino', 'SG':'St. Gallen', 'GE':'Genève',
                'GL':'Glarus', 'JU':'Jura', 'ZG':'Zug', 'OW':'Obwalden', 'FR':'Fribourg', 'SZ':'Schwyz',
                'AR':'Appenzell Ausserrhoden', 'AI':'Appenzell Innerrhoden', 'NW':'Nidwalden', 'BS':'Basel-Stadt'}

df["canton_long"]= df["canton"].map(cantons_dict, na_action=None)


#Title and Header
st.title("Welcome to my first streamlit App")
st.header("Clean Energy Sources in Switzerland")

#widgets checkbox (you can replace st.xx with st.sidebar.xx)
if st.checkbox("Show underlying data"):
    st.subheader("This is the dataset:")
    st.dataframe(data=df[df.lat.notna()])


# Subheader for location section
st.subheader("Location of Clean Energy Production")

# Setting up columns
left_column, middle_column, right_column = st.columns([3, 1, 1])

# Widgets: selectbox
sources = ["All"]+sorted(pd.unique(df['energy_source_level_2']))
source = left_column.selectbox("Select an energy source", sources)

# Flow control and plotting
if source == "All":
    reduced_df = df
else:
    reduced_df = df[df["energy_source_level_2"] == source]

# Streamlit Map for locations of clean energy production
st.map(reduced_df[reduced_df.lat.notna()], zoom=6.6)


# code from internet
view_state = pdk.ViewState(latitude=46.7,
                           longitude=8.3,
                           zoom=6.5,
                           pitch=0)

tooltip = {
    "html":
        "<b>Type:</b> {energy_source_level_2} <br/>"
        "<b>Name:</b> {project_name} <br/>",
    "style": {
        "backgroundColor": "steelblue",
        "color": "black",
    }
}

df_subset=df[df.lat.notna()].drop(columns=["energy_source_level_3","address"]).reset_index().dropna()
bio_layer = pdk.Layer(
    type='ScatterplotLayer',
    data=df_subset[df_subset.energy_source_level_2 == "Bioenergy"],
    get_position=["lon", "lat"],
    get_color=[45, 190, 37],
    get_line_color=[40, 80, 120],
    get_radius=750,
    pickable=True,
    onClick=True,
    filled=True,
    line_width_min_pixels=10,
    opacity=2,)

hydro_layer = pdk.Layer(
    type='ScatterplotLayer',
    data=df_subset[df_subset.energy_source_level_2 == "Hydro"],
    get_position=["lon", "lat"],
    get_color=[37, 150, 190],
    get_line_color=[40, 80, 120],
    get_radius=750,
    pickable=True,
    onClick=True,
    filled=True,
    line_width_min_pixels=10,
    opacity=2,)

solar_layer = pdk.Layer(
    type='ScatterplotLayer',
    data=df_subset[df_subset.energy_source_level_2 == "Solar"],
    get_position=["lon", "lat"],
    get_color=[248, 255, 63],
    get_line_color=[40, 80, 120],
    get_radius=750,
    pickable=True,
    onClick=True,
    filled=True,
    line_width_min_pixels=10,
    opacity=2,)

wind_layer = pdk.Layer(
    type='ScatterplotLayer',
    data=df_subset[df_subset.energy_source_level_2 == "Wind"],
    get_position=["lon", "lat"],
    get_color=[216, 39, 39],
    get_line_color=[40, 80, 120],
    get_radius=750,
    pickable=True,
    onClick=True,
    filled=True,
    line_width_min_pixels=10,
    opacity=2,)

pp = pdk.Deck(
    initial_view_state=view_state,
    map_provider='mapbox',
    map_style=pdk.map_styles.SATELLITE,
    layers=[
        bio_layer,
        hydro_layer,
        solar_layer,
        wind_layer,],
    tooltip=tooltip)

deckchart = st.pydeck_chart(pp)


# Plotly Choropleth Map
st.subheader("Total capacity renewable energies by canton")
fig = px.choropleth_mapbox(df.groupby("canton_long").electrical_capacity.sum().reset_index(),
                            geojson=geoj, color="electrical_capacity",
                            locations="canton_long", featureidkey="properties.kan_name",
                            labels={'electrical_capacity':'electrical_capacity [MW]'},
                            range_color=(0, 200),
                            color_continuous_scale="Viridis",  opacity=0.7,
                            center={"lat": 46.8, "lon": 8.25},
                            mapbox_style="carto-positron", zoom=6.8)

fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

# Change layout size
fig.update_layout(
    #barmode='stack',
    width=920,
    height=500,
    paper_bgcolor="white",)
st.plotly_chart(fig)

# Data source
url = "https://data.open-power-system-data.org/renewable_power_plants/2020-08-25"
st.write("Data Source:", url)