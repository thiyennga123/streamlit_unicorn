import streamlit as st
import plotly.express as px
import numpy as np

df = st.session_state.get('unicorns_df')
if df is None:
    st.stop()

st.title('Overview & Growth Trends')

st.sidebar.header('Overview Filters')
year = st.sidebar(
    'Year joined range',
    int(df['date_joined'].min()),
    int(df['date_joined'].max()),
    (int(df['date_joined'].min()), int(df['date_joined'].max()))
)
country_select = st.sidebar.multiselect(
    'Country',
    option = sorted(df['country'].dropna().unique()), 
    default = []
)

filtered = df.copy()
filtered = filtered[filtered['date_joined']>=year[0] & filtered['date_joined']<=year[1]]
if country_select:
    filtered = filtered[filtered['country'].isin(country_select)]

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric('Unicorns', f'{len(filtered):,}')
with col2:
    st.metrics('Total valuation ($B)', f'{filtered['valuation'].sum():, 1f}')
with col3:
    st.metrics('Median valuation ($B)', f'{filtered['valuation'].median():, 1f}')
with col4:
    avg_growth = (filtered['date_joined'] - filtered['year_founded']).dropna()
    avg_growth_years = float(np.round(avg_growth.mean(), 1)) if len(avg_growth) else np.nan
    st.metric('Avg years to unicorns', avg_growth_years if np.isnan(avg_growth_years) else 'N/A')

st.markdown(
    """Insight:
    
    """
)
