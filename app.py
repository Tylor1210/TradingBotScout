import os
import json
import requests
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from google import genai
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Page configuration
st.set_page_config(page_title="TradeBot Quant Dashboard", layout="wide", initial_sidebar_state="expanded")

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("❌ GEMINI_API_KEY not found. Please check your local .env file setup.")
    st.stop()

client = genai.Client(api_key=api_key)

# Curated lists for auto-scanning
TOP_COMPANIES = ["GOOGL", "DELL", "SPY", "MSFT", "AMZN", "AAPL", "NVDA", "TSLA", "AMD", "META"]
VALUE_PENNY = ["IES", "IQE", "CWR", "HITI", "SOUN"]

def fetch_market_news(ticker):
    """Scrapes free public headlines using a standard browser user-agent header."""
    try:
        url = f"https://news.google.com/rss/search?q={ticker}+stock"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        res = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(res.content, "xml")
        headlines = [item.title.text for item in soup.find_all("item")[:4]]
        return " | ".join(headlines) if headlines else "No recent headlines found."
    except Exception:
        return "Sentiment stream temporarily unavailable."

def analyze_ticker_macro(ticker):
    news = fetch_market_news(ticker)
    
    prompt = f"""
    You are an institutional Quant Analyst. Analyze the multi-week trajectory for ${ticker}.
    Based on underlying market cycles and these recent headlines: {news}
    
    Return a strict, raw JSON object exactly with these keys. No markdown, no prose, no code blocks:
    {{
      "ticker": "{ticker}",
      "bias_7d": "BUY" or "SHORT" or "NEUTRAL",
      "prob_7d": 75,
      "bias_30d": "BUY" or "SHORT" or "NEUTRAL",
      "prob_30d": 80,
      "support_pivot": 140.50,
      "resistance_pivot": 155.20,
      "indicator_conditional": "If daily RSI breaks above 65, BUY probability climbs to 88%. If volume drops below 10-day average, expect a 12% drift toward support."
    }}
    """
    try:
        response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        clean_text = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(clean_text)
    except Exception:
        return {{
          "ticker": ticker, "bias_7d": "NEUTRAL", "prob_7d": 50, "bias_30d": "NEUTRAL", "prob_30d": 50,
          "support_pivot": 0.0, "resistance_pivot": 0.0, "indicator_conditional": "Error computing quantitative matrix thresholds."
        }}

# --- DASHBOARD UI LAYOUT ---
st.title("🤖 TradeBot Predictive Quant Dashboard")
st.subheader("Automated Multi-Horizon Trend Scouter & Expected Probability Matrix")

# Sidebar Selections
st.sidebar.header("🎯 Asset Intelligence Scouter")
scan_type = st.sidebar.radio("Select Scan Target Pool:", ["Top Liquid Traded", "Interesting Value / Penny Pools", "Custom Individual Check"])

selected_tickers = []
if scan_type == "Top Liquid Traded":
    selected_tickers = TOP_COMPANIES
elif scan_type == "Interesting Value / Penny Pools":
    selected_tickers = VALUE_PENNY
else:
    custom_in = st.sidebar.text_input("Enter custom tickers (comma separated):", "GOOGL, DELL")
    selected_tickers = [x.strip().upper() for x in custom_in.split(",")]

if st.sidebar.button("⚡ Execute Multi-Asset Quant Scan"):
    results = []
    progress_bar = st.progress(0)
    
    for idx, ticker in enumerate(selected_tickers):
        st.write(f"Scanning metrics for **${ticker}**...")
        analysis = analyze_ticker_macro(ticker)
        results.append(analysis)
        progress_bar.progress((idx + 1) / len(selected_tickers))
        
    df = pd.DataFrame(results)
    st.session_state['scan_data'] = df
    st.success("🎯 Multi-Asset Horizon Scan Completed Successfully!")

# Display Data Metrics Visually
if 'scan_data' in st.session_state:
    df = st.session_state['scan_data']
    
    st.markdown("### 📊 Active Structural Forecasts (7-Day vs 30-Day Horizons)")
    
    # Format and present clean, style-colored visual dataframes
    def color_bias(val):
        if val == 'BUY': return 'background-color: #2ecc71; color: black; font-weight: bold;'
        if val == 'SHORT': return 'background-color: #e74c3c; color: white; font-weight: bold;'
        return 'background-color: #f1c40f; color: black;'

    styled_df = df[['ticker', 'bias_7d', 'prob_7d', 'bias_30d', 'prob_30d', 'support_pivot', 'resistance_pivot']].style.applymap(color_bias, subset=['bias_7d', 'bias_30d'])
    st.dataframe(styled_df, use_container_width=True)
    
    st.markdown("---")
    st.markdown("### 🔍 Conditional Dynamic Inflection Points")
    
    for _, row in df.iterrows():
        with st.expander(f"📈 Threshold & Indicator Intersections for ${row['ticker']}"):
            col1, col2 = st.columns([1, 3])
            with col1:
                st.metric("Support Pivot", f"${row['support_pivot']}")
                st.metric("Resistance Pivot", f"${row['resistance_pivot']}")
            with col2:
                st.info(f"**Conditional Shift Triggers:**\n\n{row['indicator_conditional']}")
                
                # Visual Probability Dial Map
                fig = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = row['prob_30d'],
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': f"30-Day Horizon Trend Strength ({row['bias_30d']})"},
                    gauge = {
                        'axis': {'range': [0, 100]},
                        'bar': {'color': "#3498db"},
                        'steps': [
                            {'range': [0, 50], 'color': "#eeeeee"},
                            {'range': [50, 75], 'color': "#d5f5e3"},
                            {'range': [75, 100], 'color': "#2ecc71"}
                        ]
                    }
                ))
                fig.update_layout(height=200, margin=dict(l=10, r=10, t=40, b=10))
                st.plotly_chart(fig, use_container_width=True)
else:
    st.info("💡 Select your scanner directory profile on the left sidebar menu and click 'Execute Multi-Asset Quant Scan' to compile your clean UI data grid.")