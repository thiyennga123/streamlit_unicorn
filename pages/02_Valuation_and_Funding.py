import pandas as pd
import streamlit as st
import plotly.express as px
import numpy as np
from scipy import stats
from scipy.stats import ttest_ind
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(
    page_title='Valuation and Funding',
    page_icon='💰',
    layout='wide'
)

df = st.session_state.get('unicorns_df')
if df is None:
    st.stop()

st.title('Valuation and Funding')

st.sidebar.header('Valuation Filters')

industry_sel = st.sidebar.multiselect(
    "Industry", options=sorted(df["industry"].dropna().unique()), default=[]
)

country_sel = st.sidebar.multiselect(
    "country", options=sorted(df["country"].dropna().unique()), default=[]
)

filtered = df.copy()

if industry_sel:
    filtered = filtered[filtered["industry"].isin(industry_sel)]
if country_sel:
    filtered = filtered[filtered["country"].isin(country_sel)]

st.markdown(
    """
    ### **Valuation Distribution**
    """
)

bins = [0,1,2,5,10,20,50,100,500]
labels = ['1-2B','2-5B','5-10B','10-20B','20-50B','50-100B','100-500B','500B+']
filtered['valuation_bands'] = pd.cut(filtered['valuation'], bins = bins, labels = labels)
band_counts = filtered['valuation_bands'].value_counts().sort_index()
band_df = band_counts.reset_index()
band_df.columns = ['valuation_band','count']

col_1, col_2 = st.columns(2)
with col_1:
    fig_bar = px.bar(
        band_df,
        y='count',
        x='valuation_band',
        orientation='v',
        title='Unicorn Count by Valuation Band',
        labels = {'count':'Number of Unicorns','valuation_band':'Valuation Band'},
        color_discrete_sequence=['#ae8bdf']
    )
    st.plotly_chart(fig_bar, use_container_width=True)
with col_2:
    fig_pie = px.pie(
        band_df,
        values='count',
        names='valuation_band',
        title='Unicorn Count by Valuation Band',
        labels = {'count':'Number of Unicorns','valuation_band':'Valuation Band'},
        color_discrete_sequence=px.colors.sequential.Purp
    )
    st.plotly_chart(fig_pie)

skew_value = stats.skew(filtered['valuation'].values)
st.caption(f'Valuation skewness (positive = right-skewed): {skew_value:.2f}')

st.markdown(
    """
    **Insight**: Most unicorns cluster in the lower valuation bands, with a long right-tail of very large companies, 
    as indicated by the positive skew.  
    **Action**: When benchmarking a company, compare it to its valuation band peers instead of only to extreme outliers.
    """
)

st.markdown(
    """
    ### **Top Unicorns by Valuation and ROI**
    """
)

top_valuation = filtered.nlargest(5, 'valuation')[['company', 'country', 'industry', 'valuation']]

filtered['roi'] = filtered['valuation']/filtered['funding']
filtered = filtered.replace([np.inf, -np.inf], np.nan)
filtered_valid_roi = filtered.dropna(subset=["roi"])
top_roi = filtered_valid_roi.nlargest(5, 'roi')[['company', 'country', 'industry', 'roi']]

tab_1, tab_2 = st.tabs(['Top by Valuation', 'Top by ROI'])
with tab_1:
    col_1, col_2 = st.columns([2,1])
    with col_1:
        fig_top_val = px.bar(
            top_valuation.sort_values('valuation'),
            x='valuation',
            y='company',
            orientation='h',
            title='Top 10 Unicorns by Valuation',
            labels={'valuation': 'Valuation ($B)', 'company':'Company'},
            color_discrete_sequence=['#ae8bdf']
        )
        st.plotly_chart(fig_top_val, use_container_width=True)
    with col_2:
        st.dataframe(top_valuation.reset_index(drop=True))
        height=300
with tab_2:
    col_1, col_2 = st.columns([2,1])
    with col_1:
        fig_top_roi = px.bar(
            top_roi.sort_values('roi'),
            x='roi',
            y='company',
            orientation='h',
            title='Top 10 Unicorns by ROI',
            labels={'roi': 'ROI', 'company':'Company'},
            color_discrete_sequence=['#ae8bdf']
        )
        st.plotly_chart(fig_top_roi, use_container_width=True)
    with col_2:
        st.dataframe(top_roi.reset_index(drop=True))
        height=300

st.markdown(
    """
    **Insight**: Some of Unicorns appears in both lists; others are large but capital-inefficient, or small but extremely effecient.  
    **Action**: Use ROI to shortlist capital efficient companies for investment or operational benchmark, 
    not just the biggest names by valuation.
    """
)

st.markdown(
    """
    ### **Valuation over Time by Industry**
    """
)

years = st.slider(
    "Year joined range",
    int(filtered["date_joined"].min()),
    int(filtered["date_joined"].max()),
    (int(filtered["date_joined"].min()), int(filtered["date_joined"].max())))
filtered_2 = filtered[(filtered["date_joined"] >= years[0]) & (filtered["date_joined"] <= years[1])]

tab_1, tab_2 = st.tabs(['Heatmap', 'Trend Line'])
with tab_1:
    st.markdown(
    """
    **Total Unicorn Valuation by Industry and Year**
    """
    )

    val_by_ind_year = filtered_2.groupby(['date_joined','industry'])['valuation'].sum().reset_index()
    fig_val_by_ind_year_heatmap = px.density_heatmap(
        val_by_ind_year,
        x='date_joined',
        y='industry',
        z='valuation',
        color_continuous_scale='purp',
        labels={'date_joined': 'Year', "valuation": "Valuation ($B)" , 'industry': 'Industry'},
    )
    st.plotly_chart(fig_val_by_ind_year_heatmap, use_container_width=True)
    
with tab_2:
    fig_val_by_ind_year_line = px.line(
    val_by_ind_year,
    x='date_joined',
    y='valuation',
    color='industry',
    title='Total Unicorn Valuation by Industry over Years',
    labels={'date_joined': 'Year', 'valuation': 'Valuation ($B)', 'industry': 'Industry'},
    markers=True
    )
    st.plotly_chart(fig_val_by_ind_year_line, use_container_width=True)

st.markdown(
    """
    **Insight**: Industries with rapid increase of total valuation are where capital and expectations are shifting over time.  
    **Action**: Align sector focus and hiring with industries whose valuation is accelerating in your target regions and year range.
    """
)

st.markdown(
    """### **Hypothesis Testing: Compare Industries**
    """
)

col_1, col_2 = st.columns(2)
industries = sorted(filtered['industry'].dropna().unique())
with col_1:
    ind_1=st.selectbox(
        'Industry A',
        industries,
        index=industries.index('Artificial Intelligence') if 'Artificial Intelligence' in industries else 1
        )
with col_2:
    ind_2=st.selectbox(
        'Industry B',
        industries,
        index= 0 if industries[0] != ind_1 else 1
        )
if ind_1==ind_2:
    st.info('Please select two different industries to run the t-test')
else:
    tmp = df.copy()
    tmp['roi'] = tmp['valuation']/tmp['funding']
    tmp = tmp.replace([np.inf, -np.inf], np.nan)
    tmp['years_to_unicorn'] = tmp['date_joined'] - tmp['year_founded']
    metrics = {
        'Mean valuation ($B)': 'valuation',
        'ROI': 'roi',
        'Years to unicorn': 'years_to_unicorn'
    }
    result = []
    alpha = 0.05
    for label, col in metrics.items():
        industry1 = tmp.loc[tmp['industry']==ind_1, col].dropna()
        industry2 = tmp.loc[tmp['industry']==ind_2, col].dropna()
        t_stat, p_value = ttest_ind(industry1, industry2, equal_var=False)
        sig = 'yes' if p_value < alpha else 'no'
        result.append({
            'Metrics': label,
            f'{ind_1} mean': round(float(industry1.mean()), 2),
            f'{ind_2} mean': round(float(industry2.mean()), 2),
            't_stat': round(float(t_stat),3),
            'p_value': float(p_value),
            'significant': sig
            })
    st.dataframe(pd.DataFrame(result), width="stretch")
    if sig == 'yes':
        st.success(f'At least one metric shows a statistically significant difference between {ind_1} and {ind_2}')
        st.markdown("""
        **Action**: When choosing between industries, look which specific metrics (valuation level, efficiency, or speed) is significant
        and align with your strategy. For example, prefer the industry with higher ROI if you care about capital efficiency.
        """)
    else:
        st.info(f'For valuation level, there is no significant diference between {ind_1} and {ind_2} at alpha = 0.05')
        st.markdown(
        """**Action**: For these two industries, do not prioritize purely on valuation levels. 
        Let other factors such as growth velocity, capital efficiency drive your investment decisions.
        """
        )


st.markdown(
    """### **Similar Unicorns by Industry Profile**
    """
)

industry_encoded = pd.get_dummies(filtered['industry'])
similarity_matrix = cosine_similarity(industry_encoded)
def recommend_similary(company_name, df, similarity_matrix, n=5):
  idx = df[df['company']==company_name].index[0]
  similar_indices = np.argsort(similarity_matrix[idx])[::-1][:n]
  return df.loc[similar_indices,['company', 'country','industry','valuation']]

company_options=sorted(filtered['company'].unique())
selected_company = st.selectbox('Select a unicorn to find similar companies',
    options=company_options,
    index=company_options.index('Stripe') if 'Stripe' in company_options else 0
    )

n_recs = st.slider('Number of default companies', 3, 10)
recs = recommend_similary(selected_company, filtered, similarity_matrix, n_recs)

col1, col2 = st.columns([1,2])
with col1:
    st.metric('Selected unicorns', selected_company)
    st.metric('Industry', filtered.loc[filtered['company']==selected_company, 'industry'].iloc[0])
    st.metric('Valuation ($B)', filtered.loc[filtered['company']==selected_company, 'valuation'].iloc[0])
with col2:
    st.dataframe(recs.reset_index(drop=True))

st.markdown(
    """**Insight**: Similar companies often share investor profile, business models, or market dynamics.  
    **Action**: Use this list to build peer group for valuation benchmarking, partnership outreach, or competitive analysis
    around the selected unicorn.
    """
)
