import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px


DATA_URL = (
     "https://raw.githubusercontent.com/ZacTey/singaporecovid19/master/SingaporeCovid19April2020.csv"
)

st.title("Covid 19 cases in Singapore")
st.markdown("This application is a Streamlit dashboard that can be used "
            "to analyze a given dataset of Covid-19 cases in Singapore 🦠😷🚑")


@st.cache(persist=True)
def load_data(nrows):
    df = pd.read_csv(DATA_URL, error_bad_lines=False, nrows=nrows)
    df.dropna(subset=['latitude', 'longitude'], inplace=True)
    lowercase = lambda x: str(x).lower()
    df.rename(lowercase, axis="columns", inplace=True)
    df.rename(columns={"cluster_local": "location"}, inplace=True)
    df_area=pd.DataFrame(df['location'].value_counts())
    df['gender'].replace({'f': 'female','m': 'male'},inplace=True)
    return df

df = load_data(3200)

df_marking=df.drop_duplicates('location',keep='first')
df_marking.drop(df.columns.difference(['location','latitude','longitude']), 1, inplace=True)
df_marking.index.name = 'id'
df_marking.reset_index()
df_area=pd.DataFrame(df['location'].value_counts())
df_area.rename(columns={"location": "numbers"}, inplace=True)
df_area.index.name = 'location'
df_area.reset_index()
df_areamarking = (df_area.merge(df_marking, left_on='location', right_on='location')
          .reindex(columns=['location', 'latitude','longitude','numbers']))


st.header("Where are the Covid-19 clusters in Singapore?")
slider_tuple = st.slider("Total number of infected persons between:", 0, 200,(1,50))
df_mark=df_areamarking[ 
  (slider_tuple[0] <= df_areamarking['numbers'])  & (df_areamarking['numbers'] <= slider_tuple[1]) 
]
if df_mark.empty == True:
    st.markdown("Based on the loaded dataset, there are no total number of people in this range.")
    st.map(df_mark)
else:
    st.map(df_mark)
    ftitle = ("Total number of infected persons between %i and %i based on gender" % (slider_tuple[0],slider_tuple[1]))
    df_filtered=df[df['location'].isin(df_mark['location'])]
    f = px.histogram(df_filtered, x="gender",opacity=0.7,color="gender",title=ftitle)
    f.update_xaxes(title="Gender")
    f.update_yaxes(title="Number of Infected Persons")
    f.update_layout(
        autosize=False,
        width=500,
        height=500,
        hoverlabel=dict(
            bgcolor="white", 
            font_size=15, 
            font_family="Rockwell"
        )
    )
    st.plotly_chart(f)

if st.checkbox("Show raw data", False):
    st.subheader("Raw data by total number of infected persons between %i and %i" % (slider_tuple[0],slider_tuple[1]))
    st.write(df_mark)
    


st.header("Top 5 locations based on nationality")
select = st.selectbox('Nationality', ['Singaporean', 'Foreingners'])
df_sg = df[(df['nationality']=='singapore')]
df_notsg = df[(df['nationality']!='singapore')]
if select == 'Singaporean':
    df_sg=pd.DataFrame(df_sg['location'].value_counts())
    st.write(df_sg.head(5))
else:
    df_notsg=pd.DataFrame(df_notsg['location'].value_counts())
    st.write(df_notsg.head(5))  


st.header("Which area has the highest number of infected persons?")
midpoint = (np.average(df_marking["latitude"]), np.average(df_marking["longitude"]))
st.write(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state={
        "latitude": midpoint[0],
        "longitude": midpoint[1],
        "zoom": 11,
        "pitch": 50,
    },
    layers=[
        pdk.Layer(
        "HexagonLayer",
        data=df[['location', 'latitude', 'longitude']],
        get_position=["longitude", "latitude"],
        auto_highlight=True,
        radius=300,
        extruded=True,
        pickable=True,
        elevation_scale=6,
        elevation_range=[0, 1000],
        get_color='[200, 30, 0, 160]'
        ),
    ],
))
