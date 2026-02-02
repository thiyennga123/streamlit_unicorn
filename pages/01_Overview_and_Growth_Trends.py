import streamlit as st
import plotly.express as px
import numpy as np

st.set_page_config(
    page_title='Unicorn Overview and Growth Trends',
    page_icon='🦄',
    layout='wide'
)

df = st.session_state.get('unicorns_df')
if df is None:
    st.stop()

st.title('Overview & Growth Trends')

st.sidebar.header('Overview Filters')

st.sidebar.header("Overview filters")
years = st.sidebar.slider(
    "Year joined range",
    int(df["date_joined"].min()),
    int(df["date_joined"].max()),
    (int(df["date_joined"].min()), int(df["date_joined"].max())))

country_sel = st.sidebar.multiselect(
    "Country", options=sorted(df["country"].dropna().unique()), default=[]
)

filtered = df.copy()
filtered = filtered[(filtered["date_joined"] >= years[0]) & (filtered["date_joined"] <= years[1])]
if country_sel:
    filtered = filtered[filtered["country"].isin(country_sel)]

st.markdown("""
### **Overall**
""")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric('No. of Unicorns', f'{len(filtered):,}')
with col2:
    st.metric('Total Valuation ($B)', f"{filtered['valuation'].sum():,.1f}")
with col3:
    st.metric('Median Valuation ($B)', f"{filtered['valuation'].median():,.1f}")
with col4:
    avg_growth = (filtered["date_joined"] - filtered["year_founded"]).dropna()
    avg_growth_years = float(np.round(avg_growth.mean(), 1)) if len(avg_growth) else np.nan
    st.metric("Avg Years to Unicorns", avg_growth_years if not np.isnan(avg_growth_years) else "N/A")


st.markdown(
    """
    **Insight – What:** This snapshot shows the **overall size and maturity** of the unicorn universe for your selected years and countries.  
    **Action:** Use these KPIs to quickly benchmark the unicorn landscape against other datasets or time periods.
    """
)

st.markdown(
    """
    ### **Unicorn Creation over Time**
    """
)

unicorns_per_year = (
    filtered
    .groupby("date_joined")
    ["company"]
    .count()
    .reset_index()
)
unicorns_per_year.columns = ["year", "no_of_unicorns"]
unicorns_per_year['year'] = unicorns_per_year['year'].astype(str)
fig = px.line(unicorns_per_year, x="year", y="no_of_unicorns", labels={"year": "Year","no_of_unicorns": "No of Unicorns"}, 
    markers=True, color_discrete_sequence=['#ae8bdf'])
fig.update_xaxes(tickangle=0, tickformat="d")
st.plotly_chart(fig, use_container_width=True)

st.markdown("""
    **Insight - What**: Peaks and slowdowns indicate changing growth momentum in unicorn creation.   
    **Action:** Analyze peak years to uncover conditions that fueled unicorn formation.
    """)

# st.markdown(
#     """
#     **Number of Unicorns by Industry**
#     """
# )

# unicorns_per_industry = (
#     filtered
#     .groupby("industry")
#     ["company"]
#     .count()
#     .reset_index()
# )

# unicorns_per_industry.columns = ["industry", "no_of_unicorns"]
# unicorns_per_industry = unicorns_per_industry.sort_values(by="no_of_unicorns",ascending=True)
# unicorns_per_industry['industry'] = unicorns_per_industry['industry'].astype(str)
# fig = px.bar(unicorns_per_industry, x="no_of_unicorns", y="industry", orientation='h', labels={"no_of_unicorns": "No of Unicorns",
#     "industry":"Industry"}, color="industry", color_discrete_sequence=px.colors.qualitative.Pastel)
# st.plotly_chart(fig, use_container_width=True)

st.markdown(
    """### **Number of Unicorn by Continent**
    """
)

unicorn_cont_year=(filtered.groupby(['date_joined', 'continent']).size().reset_index())
unicorn_cont_year.columns = ["year", "continent", "no_of_unicorns"]
fig = px.line(unicorn_cont_year, x="year", y="no_of_unicorns", markers=True, labels={"no_of_unicorns": "No of Unicorns",
    "year":"Year", "continent":"Continent"}, color="continent", color_discrete_sequence=px.colors.qualitative.Pastel)
st.plotly_chart(fig, use_container_width=True)

st.markdown(
    """**Insight**: Different continents have its own regional strength supporting to the formation of unicorns.  
    **Action:** Use this view to prioritize scouting, hiring, expanding into regions with substained growth.
    """
)

st.markdown(
    """### **Top Investing Industry**
    """
)
recent_year=st.slider(
'Focused year for industry view', 
min_value=int((filtered['date_joined']).min()),
max_value=int((filtered['date_joined']).max()),
value=int((filtered['date_joined']).max())
)
recent=filtered[filtered['date_joined']==recent_year]

ind_value = (
    recent.groupby('industry')['valuation']
    .sum()
    .reset_index()
    .sort_values('valuation', ascending=False)
)

if not ind_value.empty:
    top_n=st.selectbox('Number of industries to display:', options=[5,10,15], index=0)
    ind_value_top = ind_value.head(top_n)
    col_a, col_b = st.columns([2,1])
    with col_a:
        fig_ind = px.bar(
            ind_value_top.sort_values('valuation'),
            x='valuation',
            y='industry',
            orientation='h',
            title=f'Top Industries by Valuation in {recent_year}',
            labels={'valuation': 'Total Valuation ($B)', 'industry':'Industry'}, 
            color_discrete_sequence=['#ae8bdf']
        )
        st.plotly_chart(fig_ind, use_container_width=True)
    with col_b:
        st.dataframe(
            ind_value_top.sort_values('valuation').reset_index(drop=True), height=300
        )
    st.markdown(f"""**Insight**: In {recent_year}, the leading industries by valuation reveal where **capital and growth expectation** are
        concented on.   
        **Action**: Target these industries for **deal flow, partnerships, or product offering** if they align with your strategy.
        """
    )
else: 
    st.info('No unicorns for the selected period.')


