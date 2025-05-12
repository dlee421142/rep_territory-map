import pandas as pd
import streamlit as st
import plotly.express as px
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gspread_dataframe import get_as_dataframe

# --- Google Sheets auth ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
client = gspread.authorize(creds)

# --- Load data ---
sheet = client.open("Rep Mapping by State / Zip Code")
df = get_as_dataframe(sheet.worksheet("Rep Territory Summary")).dropna()

# --- Clean ---
df = df.dropna(subset=["Zip", "Rep"])
df["Zip"] = df["Zip"].astype(str).str.zfill(5)

# --- UI ---
st.set_page_config(page_title="Rep Territory Map", layout="wide")
st.title("📍 Live Rep Territory Map")

rep_options = sorted(df["Rep"].dropna().unique())
selected_reps = st.multiselect("Filter by Rep", rep_options, default=rep_options)

filtered_df = df[df["Rep"].isin(selected_reps)]

fig = px.choropleth(
    filtered_df,
    geojson="https://raw.githubusercontent.com/OpenDataDE/State-zip-code-GeoJSON/master/state-zip-code.geojson",
    locations="Zip",
    color="Rep",
    featureidkey="properties.ZCTA5CE10",
    scope="usa",
    title="Rep Territories by ZIP Code",
)

fig.update_geos(fitbounds="locations", visible=False)
st.plotly_chart(fig, use_container_width=True)
