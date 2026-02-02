import streamlit as st
import pandas as pd
import numpy as np

# ---------- GLOBAL THEME (fonts, colors) ----------
PRIMARY_COLOR = "#0F766E"  # teal
BG_COLOR = "#0B1120"       # dark navy
CARD_BG = "#020617"        # slightly darker
TEXT_COLOR = "#E5E7EB"     # light gray
ACCENT_COLOR = "#FBBF24"   # warm accent

st.markdown(
    f"""
    <style>
    html, body, [class*="css"] {{
        background-color: {BG_COLOR};
        color: {TEXT_COLOR};
        font-family: "Inter", system-ui, -apple-system, BlinkMacSystemFont,
                     "Segoe UI", sans-serif;
    }}
    .block-container {{
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }}
    h1, h2, h3, h4 {{
        color: {TEXT_COLOR};
        font-weight: 700;
        letter-spacing: 0.02em;
    }}
    div[data-testid="stMetricValue"] {{
        color: {ACCENT_COLOR} !important;
        font-weight: 700;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Intro copy ----------
st.title("🦄 Global Unicorn Companies Analytics")

st.markdown(
    """
This dashboard answers four core questions about unicorn startups:

- **What** is the current unicorn landscape in terms of count, valuation, and time to reach unicorn status?  
- **Why** are certain industries and regions leading in value creation?  
- **How** do funding, valuation efficiency, and investor patterns differ across the ecosystem?  
- **What actions** can founders, investors, and ecosystem builders take next?

Use the sidebar navigation to switch between:

1. **Overview & Growth Trends** – high‑level size, timing, and industry mix.  
2. **Valuation & Funding** – valuation distribution, ROI, and industry comparisons.  
3. **Locations & Investors** – geographic hubs, key investors, and a detailed company list.
"""
)

#-----Share utilities------
def to_snake(name):
    name = name.strip().replace(' ($B)','')
    name = name.lower()
    name = name.replace(' ','_')
    return name

def get_metadata():
  df = pd.read_csv('companies_metadata.csv')[['Company','Funding','Year Founded']]
  df.columns = ['company','funding','year_founded']
  df['funding'] = df['funding'].apply(lambda x: x if x!='Unknown' else np.nan)
  df['funding'] = df['funding'].str.replace('$','').str.replace('B','').str.replace('M','').astype(float)
  return df

@st.cache_data
def load_data():
    df = pd.read_csv('./unicorns_companies.csv')
    df.columns = df.columns.map(to_snake)
    df['valuation'] = df['valuation'].str.replace('$', '').astype(float)
    df['date_joined'] = pd.to_datetime(df['date_joined'])
    df['date_joined'] = df['date_joined'].dt.year
    df.loc[df['company']=='LinkSure Network', 'investors'] = (
        'Bank of China Group Investment, China Merchants Innovation '
        'Investment Management, and Hopu Fund'
    )
    df['investors'] = df['investors'].fillna(df['industry'])
    df.loc[df['investors'] == df['industry'], 'industry'] = df['city']
    df.loc[df['industry'] == df['investors'], 'industry'] = df['city']
    df.loc[df['city'] == df['industry'], 'city'] = df['country']
    df['industry'] = df['industry'].str.capitalize()
    df['city'] = df['city'].str.title()
    df['country'] = df['country'].str.title()
    df['company'] = df['company'].str.title()
    metadata = get_metadata()
    metadata['company'] = metadata['company'].str.title()
    df = pd.merge(
        df,
        metadata,
        how='left',
        on='company'
    )

    if "continent" not in df.columns:
        country_to_continent = {
            "United States": "North America",
            "Canada": "North America",
            "Mexico": "North America",
            "Brazil": "South America",
            "Argentina": "South America",
            "United Kingdom": "Europe",
            "Germany": "Europe",
            "France": "Europe",
            "Spain": "Europe",
            "Sweden": "Europe",
            "China": "Asia",
            "India": "Asia",
            "Japan": "Asia",
            "South Korea": "Asia",
            "Singapore": "Asia",
            "Australia": "Oceania",
            "New Zealand": "Oceania",
            "South Africa": "Africa",
            "Nigeria": "Africa",
        }
        df["continent"] = df["country"].map(country_to_continent).fillna("Other")
    return df

if "unicorns_df" not in st.session_state:
    try:
        st.session_state["unicorns_df"] = load_data()
    except Exception as e:
        st.error(f"Error loading data: {e}")