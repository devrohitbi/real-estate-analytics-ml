import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="Real Estate AI Insights", layout="wide")

# 2. Load Data
@st.cache_data
def load_data():
    df = pd.read_csv('Cleaned_Real_Estate_Market_Intelligence.csv')
    
    # Age Correction
    if df['age'].max() <= 1.5:
        df['age'] = (df['age'] * 100).round(0)
    
    # Cluster Mapping
    def map_clusters(x):
        if x == 0: return "💎 Premium Buyers"
        if x == 1: return "💰 Budget Conscious"
        return "📈 Investment Focused"
    df['Segment_Name'] = df['KMeans_Cluster'].apply(map_clusters)
    
    # Data Cleaning
    df['Buying Reason'] = df['acquisition_purpose'].astype(str).replace({
        '0': '🏠 Residential', '1': '💰 Investment', '0.0': '🏠 Residential', '1.0': '💰 Investment'
    })
    df['Loan Status'] = df['loan_applied'].astype(str).replace({
        '0': '❌ No', '1': '✅ Yes', 'False': '❌ No', 'True': '✅ Yes'
    })
    df['Client Category'] = df['client_type'].astype(str).replace({
        '0': '👤 Individual', '1': '🏢 Corporate', '0.0': '👤 Individual', '1.0': '🏢 Corporate'
    })
    
    # COORDINATES MAPPING
    coords = {
        'country_Australia': {'lat': -25.27, 'lon': 133.77},
        'country_UAE': {'lat': 23.42, 'lon': 53.84},
        'country_USA': {'lat': 37.09, 'lon': -95.71},
        'country_India': {'lat': 20.59, 'lon': 78.96},
        'country_UK': {'lat': 55.37, 'lon': -3.43},
        'country_Canada': {'lat': 56.13, 'lon': -106.34},
        'country_Germany': {'lat': 51.16, 'lon': 10.45},
        'country_France': {'lat': 46.22, 'lon': 2.21}
    }
    
    def assign_lat(row):
        for c, val in coords.items():
            if row.get(c) == 1 or row.get(c) == True: return val['lat']
        return 20.0
    def assign_lon(row):
        for c, val in coords.items():
            if row.get(c) == 1 or row.get(c) == True: return val['lon']
        return 0.0

    df['latitude'] = df.apply(assign_lat, axis=1)
    df['longitude'] = df.apply(assign_lon, axis=1)
    return df

df = load_data()

# 3. Sidebar Navigation
st.sidebar.title("🎯 Navigation")
page = st.sidebar.radio("Go to:", 
    ["1. Buyer Segmentation Overview", 
     "2. Investor Behaviour Dashboard", 
     "3. Geographic Buyer Analysis", 
     "4. Segment Insights Panel"])

st.sidebar.markdown("---")
st.sidebar.header("🔍 Filter Controls")

country_cols = sorted([col for col in df.columns if col.startswith('country_')])
region_cols = sorted([col for col in df.columns if col.startswith('region_')])
selected_country = st.sidebar.selectbox("Select Country", options=["All Countries"] + country_cols)

if selected_country != "All Countries":
    temp_df = df[(df[selected_country] == 1) | (df[selected_country] == True)]
    active_regions = [col for col in region_cols if temp_df[col].any()]
    selected_region = st.sidebar.selectbox("Select Region", options=["All Regions"] + active_regions)
else:
    selected_region = st.sidebar.selectbox("Select Region", options=["All Regions"] + region_cols)

selected_purpose = st.sidebar.multiselect("Buying Reason", options=df['Buying Reason'].unique(), default=df['Buying Reason'].unique())
selected_client = st.sidebar.multiselect("Client Category", options=df['Client Category'].unique(), default=df['Client Category'].unique())
selected_segment = st.sidebar.multiselect("Select Segments", options=sorted(df['Segment_Name'].unique()), default=sorted(df['Segment_Name'].unique()))

f_df = df.copy()
if selected_country != "All Countries":
    f_df = f_df[(f_df[selected_country] == 1) | (f_df[selected_country] == True)]
if selected_region != "All Regions":
    f_df = f_df[(f_df[selected_region] == 1) | (f_df[selected_region] == True)]

f_df = f_df[
    (f_df['Buying Reason'].isin(selected_purpose)) &
    (f_df['Client Category'].isin(selected_client)) &
    (f_df['Segment_Name'].isin(selected_segment))
]

# ==========================================
# PAGE 1: OVERVIEW (Main Project Title)
# ==========================================
if page == "1. Buyer Segmentation Overview":
    st.markdown("# 🏙️ Real Estate AI Insights")
    st.subheader("Buyer Segmentation Analysis")
    st.markdown("---")
    c1, c2 = st.columns([1.5, 1], gap="large") 
    with c1:
        fig_pie = px.pie(f_df, names='Segment_Name', hole=0.4, title="Market Share per Segment")
        fig_pie.update_traces(textposition='outside', textinfo='label+percent')
        st.plotly_chart(fig_pie, use_container_width=True)
    with c2:
        st.subheader("Demographic: Average Age")
        fig_age = px.bar(f_df.groupby('Segment_Name')['age'].mean().reset_index(), 
                         x='Segment_Name', y='age', color='Segment_Name',
                         labels={'age': 'Age (Years)', 'Segment_Name': 'Buyer Group'})
        st.plotly_chart(fig_age, use_container_width=True)

# ==========================================
# PAGE 2: INVESTOR BEHAVIOUR (Enhanced Labels)
# ==========================================
elif page == "2. Investor Behaviour Dashboard":
    st.title("💰 Investor Behaviour & Financial Profile")
    col1, col2 = st.columns(2)
    with col1:
        fig1 = px.bar(f_df, x="Segment_Name", color="Buying Reason", barmode="group",
                      title="Investment Purpose by Buyer Segment",
                      labels={'Segment_Name': 'Buyer Groups', 'count': 'Number of Buyers', 'Buying Reason': 'Reason'})
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        fig2 = px.histogram(f_df, x="Segment_Name", color="Loan Status", barmode="group",
                            title="Loan Application Status (Yes/No)",
                            labels={'Segment_Name': 'Buyer Groups', 'count': 'Total Applications', 'Loan Status': 'Applied for Loan?'})
        st.plotly_chart(fig2, use_container_width=True)

# ==========================================
# PAGE 3: GEOGRAPHIC BUYER ANALYSIS (Restored)
# ==========================================
elif page == "3. Geographic Buyer Analysis":
    st.title("🌎 Geographic Buyer Intelligence")
    
    if selected_country == "All Countries" or f_df.empty:
        c_lat, c_lon, zoom_level = 20, 0, 1
    else:
        c_lat = f_df['latitude'].mean()
        c_lon = f_df['longitude'].mean()
        zoom_level = 3.5

    fig_globe = px.scatter_geo(
        f_df, lat='latitude', lon='longitude', color='Segment_Name',
        projection="orthographic",
        hover_data=['Buying Reason', 'Client Category', 'age'],
        title=f"Global Buyer Footprint: {selected_country}"
    )
    fig_globe.update_geos(showcountries=True, countrycolor="white", showland=True, landcolor="forestgreen",
                          showocean=True, oceancolor="royalblue", projection_rotation=dict(lon=c_lon, lat=c_lat, roll=0),
                          projection_scale=zoom_level)
    fig_globe.update_layout(height=600, margin={"r":0,"t":50,"l":0,"b":0})
    st.plotly_chart(fig_globe, use_container_width=True)

    st.markdown("---")
    st.subheader("📍 Regional Market Composition")
    g_col1, g_col2 = st.columns(2)
    with g_col1:
        st.markdown("*Buyer Concentration*")
        st.plotly_chart(px.histogram(f_df, x="Segment_Name", color="Segment_Name", template="plotly_white"), use_container_width=True)
    with g_col2:
        st.markdown("*Strategic Intent (Category & Purpose)*")
        st.plotly_chart(px.sunburst(f_df, path=['Client Category', 'Buying Reason'], color='Client Category'), use_container_width=True)

# ==========================================
# PAGE 4: INSIGHTS PANEL
# ==========================================
elif page == "4. Segment Insights Panel":
    st.title("📈 Detailed Buyer Data Panel")
    st.dataframe(f_df[['Segment_Name', 'age', 'Buying Reason', 'Loan Status', 'Client Category']].head(100), use_container_width=True)