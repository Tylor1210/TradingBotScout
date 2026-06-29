import os
import json
import requests
from google import genai
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Automatically load your local private API key
load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    raise ValueError("❌ Error: GEMINI_API_KEY not found. Make sure your .env file is saved correctly.")

client = genai.Client(api_key=api_key)

def fetch_free_market_news(ticker):
    """Scrapes free public headlines using a standard browser user-agent header."""
    try:
        url = f"https://news.google.com/rss/search?q={ticker}+stock"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        res = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(res.content, "xml")
        headlines = [item.title.text for item in soup.find_all("item")[:5]]
        return headlines
    except Exception as e:
        return [f"Could not retrieve sentiment data: {str(e)}"]

def generate_daily_matrix():
    # Bypasses the broken Windows port by letting you type the stock directly!
    ticker = input("💱 Enter the stock ticker you want to analyze (e.g. GOOGL, DELL, SPY): ").upper().strip()
    if not ticker:
        ticker = "GOOGL"

    print(f"\n📰 Gathering overnight catalysts and market news for ${ticker}...")
    news_data = fetch_free_market_news(ticker)
    
    prompt = f"""
    You are an expert Quant Trading Assistant. Analyze the current market context and headlines for ${ticker} 
    and output a definitive, daily If/Then Strategy Matrix for day-trading.
    
    [Recent News/Sentiment Catalysts for {ticker}]: {json.dumps(news_data)}
    
    Provide a professional daily day-trading game plan formatted exactly like this:
    
    ### Daily Strategy Matrix for ${ticker}
    
    | Plan Direction | Target Trigger Level | Calculated Probability | Suggested Options/Equity Setup |
    | :--- | :--- | :--- | :--- |
    | 🟢 Call Opportunity | [State key upside breakout trigger level] | [Percentage] | [Target Strike / Move] |
    | 🔴 Put Opportunity | [State key downside breakdown trigger level] | [Percentage] | [Target Strike / Move] |
    | 🟡 Chop Zone | [Range to avoid trading] | High Risk | Sit on hands. |
    
    Include a clear summary detailing expected intraday support/resistance zones and volatility catalysts based on the news sentiment.
    """
    
    print("🧠 Processing market metrics with Gemini...")
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    print("\n" + "="*40 + "\nYOUR DAILY BRIEFING:\n" + "="*40)
    print(response.text)

if __name__ == "__main__":
    generate_daily_matrix()