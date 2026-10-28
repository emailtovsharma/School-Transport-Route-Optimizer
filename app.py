import math
import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

# Configure Streamlit page layout
st.set_page_config(
    page_title="School Transport Inquiry Finder",
    layout="wide",
    page_icon="🚌",
)

st.title("🚌 School Transport Pickup & Route Finder")
st.write(
    "Enter a parent's coordinates and select the student category to instantly"
    " find the nearest pickup point across all 15 routes."
)


# Haversine distance calculation in kilometers
def calculate_distance(lat1, lon1, lat2, lon2):
  R = 6371.0
  lat1_rad, lon1_rad = math.radians(lat1), math.radians(lon1)
  lat2_rad, lon2_rad = math.radians(lat2), math.radians(lon2)
  dlat = lat2_rad - lat1_rad
  dlon = lon2_rad - lon1_rad
  a = (
      math.sin(dlat / 2) ** 2
      + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
  )
  return R * 2 * math.asin(math.sqrt(a))


# Load and cache all 15 sheets from Data_location_001.xlsx
@st.cache_data
def load_all_routes():
  excel_path = r"Sample_Route_Data.xlsx"
  xls = pd.ExcelFile(excel_path)
  combined = []

  for sheet in xls.sheet_names:
    df = pd.read_excel(excel_path, sheet_name=sheet)
    df = df.dropna(subset=["Latitude", "Longitude"]).copy()
    df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")
    df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")
    df = df.dropna(subset=["Latitude", "Longitude"])

    # Determine category based on sheet naming ((S) vs (J))
    sheet_upper = sheet.upper()
    if "(S)" in sheet_upper or "S " in sheet_upper:
      cat = "Senior"
    elif "(J)" in sheet_upper or "J " in sheet_upper or ")J" in sheet_upper:
      cat = "Junior"
    else:
      cat = "Senior" if "S" in sheet_upper else "Junior"

    df["Route_Name"] = sheet.strip()
    df["Category"] = cat
    df["Stop_Name"] = (
        df["Address"].astype(str)
        if "Address" in df.columns
        else df["Student's Name"].astype(str)
    )
    combined.append(df)

  return pd.concat(combined, ignore_index=True)


try:
  df_all_stops = load_all_routes()
  st.sidebar.success(
      f"Successfully loaded {len(df_all_stops)} stops across 15 routes!"
  )
except Exception as e:
  st.error(
      f"Could not load `Data_location_001.xlsx`. Make sure it is in the same"
      f" folder. Error: {e}"
  )
  df_all_stops = pd.DataFrame()

# --- SIDEBAR INPUT CONTROLS ---
st.sidebar.header("Parent Inquiry Controls")
parent_lat = st.sidebar.number_input(
    "Parent Latitude", value=30.6900, format="%.6f"
)
parent_lon = st.sidebar.number_input(
    "Parent Longitude", value=76.8580, format="%.6f"
)
category_option = st.sidebar.radio(
    "Student Category Filter", ["Senior", "Junior", "All"]
)

# Filter stops based on selected category
if category_option in ["Junior", "Senior"]:
  filtered_df = df_all_stops[df_all_stops["Category"] == category_option]
else:
  filtered_df = df_all_stops

# Compute nearest pickup point
min_dist = float("inf")
nearest_row = None

if not filtered_df.empty:
  for _, row in filtered_df.iterrows():
    d = calculate_distance(
        parent_lat, parent_lon, row["Latitude"], row["Longitude"]
    )
    if d < min_dist:
      min_dist = d
      nearest_row = row

# --- UI LAYOUT (Results & Map) ---
col1, col2 = st.columns([1, 2])

with col1:
  st.subheader("Match Summary")
  if nearest_row is not None:
    st.info(f"**Active Filter:** {category_option} Routes")
    st.success(
        f"**Matched Route:** {nearest_row['Route_Name']}\n\n"
        f"**Nearest Stop / Address:** {nearest_row['Stop_Name']}\n\n"
        f"**Direct Distance:** {min_dist:.2f} km"
    )

    father_contact = nearest_row.get("Father's Contact", "N/A")
    if pd.notna(father_contact):
      st.caption(f"Contact on Record: {father_contact}")
  else:
    st.warning("No matching stops found for this selection.")
with col2:
  st.subheader("Interactive Route Map")
  m = folium.Map(location=[parent_lat, parent_lon], zoom_start=13)

  # Plot Parent Residence Marker (Red House)
  folium.Marker(
      [parent_lat, parent_lon],
      popup="Parent Residence",
      icon=folium.Icon(color="red", icon="home", prefix="fa"),
  ).add_to(m)

  # Plot all stops in the filtered category
  for _, row in filtered_df.iterrows():
    is_match = (
        nearest_row is not None
        and row["Latitude"] == nearest_row["Latitude"]
        and row["Longitude"] == nearest_row["Longitude"]
    )
    folium.CircleMarker(
        [row["Latitude"], row["Longitude"]],
        radius=7 if is_match else 4,
        popup=f"<b>{row['Route_Name']}</b><br>{row['Stop_Name']}",
        color="green" if is_match else "blue",
        fill=True,
        fill_color="green" if is_match else "blue",
        fill_opacity=0.8,
    ).add_to(m)

  # Draw dashed green line from parent to nearest stop
  if nearest_row is not None:
    folium.PolyLine(
        [
            [parent_lat, parent_lon],
            [nearest_row["Latitude"], nearest_row["Longitude"]],
        ],
        color="green",
        weight=4,
        dash_array="5,5",
        tooltip=f"{min_dist:.2f} km to {nearest_row['Route_Name']}",
    ).add_to(m)

  st_folium(m, width="100%", height=500)