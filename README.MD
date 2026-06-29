# 🤖 TradeBot - Simple Operational Guide

This project allows your free Gemini AI model to read your local TradingView Desktop screen using a hidden developer port (`9222`). It combines your live chart layout with market news to build a daily risk matrix without a paid subscription.

---

## 🛠️ The "Secret Link" Explained (http://127.0.0.1:9222/json)

* **What is it?** This is your computer's internal address (`localhost`). Port `9222` is a private data stream. 
* **What are you supposed to see?** If TradingView is running correctly in debug mode, opening that link in a browser tab will look like a page of code text (JSON) listing your open charts:
  ```json
  [
    {
      "title": "DELL 402.50 ▲ +1.20% | TradingView",
      "url": "[https://www.tradingview.com/chart/](https://www.tradingview.com/chart/)..."
    }
  ]