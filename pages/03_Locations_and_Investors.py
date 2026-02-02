import pandas as pd
import streamlit as st
import plotly.express as px
import numpy as np
from scipy import stats
from scipy.stats import ttest_ind
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(
    page_title='Locations and Investors',
    page_icon='📍',
    layout='wide'
)

df = st.session_state.get('unicorns_df')
if df is None:
    st.stop()

st.title('Locations and Investors')

st.sidebar.header('Location Filters')

country_sel = st.sidebar.multiselect(
    "Country", options=sorted(df["country"].dropna().unique()), default=[]
)

filtered = df.copy()
if country_sel:
    filtered = filtered[filtered["country"].isin(country_sel)]

st.markdown(
    """### **Unicorn Hub by Geography**
    """
)

city_industry_counts = (
        filtered
        .groupby(['city', 'industry'])
        .size()
        .reset_index(name='count')
    )

city_industry_counts_fig = px.treemap(
    city_industry_counts,
    path=['city', 'industry'],
    values='count',
    title='City-Industry Unicorn Hubs'
)
st.plotly_chart(city_industry_counts_fig)

st.markdown("""
**Insight**: Larger blocks in the treemap highlight countries and industries where unicorn activity is concentrated.  
**Action**: Use these hubs as priority locations for expansion, hiring, or ecosystem partnership.
""")

st.markdown("""
### **Top City-Industry Hubs**""")

st.dataframe(city_industry_counts.sort_values('city', ascending=False).head(15).reset_index(drop=True))


st.markdown("""
### **Top Investors**""")

num_inv = st.selectbox(
        'Number of investors to display',
        options=[5,10,15,20]
        )

col1, col2 = st.columns([2,1])
with col1:
    all_investors = filtered['investors'].str.split(', ').explode().str.strip().value_counts().sort_values(ascending=False)
    top_investors = all_investors.head(num_inv).reset_index()
    top_investors.columns = ['Investor','Count']
    top_investors_fig_barv = px.bar(
    top_investors,
    x="Investor",
    y="Count",
    title=f"Top {num_inv} Investors",
    labels={"Investor": "Investor", "Count": "Number of Investors"},
    )
    top_investors_fig_barv.update_layout(xaxis_tickangle=-25)
    st.plotly_chart(top_investors_fig_barv, use_container_width=True)
with col2:
    st.dataframe(top_investors.reset_index(drop=True))
st.markdown("""
**Insight**: Investors with the highest counts are central players in the unicorn ecosystem and often shape funding norms and valuations.  
**Action**: Use this list to identify potential lead investors or syndicate partners, or to map where your pipeline overlap with top funds.
""")

st.markdown("""
### **Detailed Unicorn List**""")
col1, col2, col3 = st.columns(3)
with col1:
    country_sel=st.selectbox('Country', options= ['All'] + sorted(filtered['country'].dropna().unique()))
with col2:
    city_sel=st.selectbox('City', options= ['All'] + sorted(filtered['city'].dropna().unique()))
with col3:
    industry_sel=st.selectbox('Industry', options= ['All'] + sorted(filtered['industry'].dropna().unique()))

detail = filtered.copy()
if country_sel != 'All':
    detail = detail[detail['country']==country_sel]
if city_sel != 'All':
    detail = detail[detail['city']==city_sel]
if industry_sel != 'All':
    detail = detail[detail['industry']==industry_sel]

cols = ['company', 'country', 'city', 'industry', 'valuation', 'funding', 'year_founded', 'date_joined']
st.dataframe(detail[cols].sort_values('valuation', ascending=False)
)

st.markdown("""
**Insight**: This filtered table shows the list of companies matching your industry and geographic criteria.  
**Action**: Use this list to have overall information for access, assessment, or partnership dicussion.
""")
