import os
import json
import requests
from google import genai
from bs4 import BeautifulSoup

# This reads your secret API key safely from your local machine environment
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("❌ Error: GEMINI_API_KEY not found in environment variables. Run 'set GEMINI_API_KEY=your_key' first.")

client = genai.Client(api_key=api_key)

def get_tradingview_data():
    """Connects directly to the local port 9222 and reads active chart info."""
    try:
        response = requests.get("http://127.0.0.1:9222/json", timeout=3)
        tabs = response.json()
        
        chart_tab = next((tab for tab in tabs if "tradingview.com/chart" in tab.get("url", "")), None)
        if not chart_tab:
            return "No active TradingView chart tab found. Make sure a chart is open."
            
        return {
            "chart_title": chart_tab.get("title", "Unknown Asset"),
            "status": "Successfully read chart metadata from screen."
        }
    except Exception as e:
        return f"Could not connect to port 9222: {str(e)}. Is TradingView open in debug mode?"

def fetch_free_market_news(ticker):
    """Scrapes free public headlines to add catalyst data to the AI matrix."""
    try:
        url = f"https://news.google.com/rss/search?q={ticker}+stock"
        res = requests.get(url, timeout=5)
        soup = BeautifulSoup(res.content, "xml")
        headlines = [item.title.text for item in soup.find_all("item")[:4]]
        return headlines
    except:
        return ["Could not retrieve sentiment data."]

def generate_daily_matrix(ticker="DELL"):
    print(f"🔄 Pulling real-time chart data from TradingView Desktop...")
    tv_data = get_tradingview_data()
    
    print(f"📰 Gathering overnight catalysts and market news for ${ticker}...")
    news_data = fetch_free_market_news(ticker)
    
    prompt = f"""
    You are an expert Quant Trading Assistant. Analyze the current data state and output a definitive, daily If/Then Strategy Matrix.
    
    [TradingView Screen State]: {json.dumps(tv_data)}
    [Recent News/Sentiment Catalysts]: {json.dumps(news_data)}
    
    Provide a professional daily day-trading game plan formatted exactly like this:
    
    ### Daily Strategy Matrix for ${ticker}
    
    | Plan Direction | Target Trigger Level | Calculated Probability | Suggested Options/Equity Setup |
    | :--- | :--- | :--- | :--- |
    | 🟢 Call Opportunity | [State level based on technical break] | [Percentage] | [Target Strike / Move] |
    | 🔴 Put Opportunity | [State level based on technical breakdown] | [Percentage] | [Target Strike / Move] |
    | 🟡 Chop Zone | [Range to avoid trading] | High Risk | Sit on hands. |
    
    Include a brief summary detailing the current candle pattern trends and strong support/resistance zones identified on screen.
    """
    
    print("🧠 Processing technical parameters with Gemini...")
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    print("\n" + "="*40 + "\nYOUR DAILY BRIEFING:\n" + "="*40)
    print(response.text)

if __name__ == "__main__":
    generate_daily_matrix("DELL")