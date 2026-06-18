import json
import datetime
import os

def generate_mock_raw_data():
    today_str = datetime.date.today().isoformat()
    
    mock_data = {
        "date": today_str,
        "stock_market": {
          "net_buy_sell_rank": {
            "foreign_investors": [
              {"rank": 1, "stock_name": "台積電", "ticker": "2330", "net_buy_shares": 4500000},
              {"rank": 2, "stock_name": "聯發科", "ticker": "2454", "net_buy_shares": 850000},
              {"rank": 3, "stock_name": "鴻海", "ticker": "2317", "net_buy_shares": -1200000}
            ],
            "investment_trust": [
              {"rank": 1, "stock_name": "世芯-KY", "ticker": "3661", "net_buy_shares": 300000},
              {"rank": 2, "stock_name": "長榮", "ticker": "2603", "net_buy_shares": 1500000},
              {"rank": 3, "stock_name": "創意", "ticker": "3443", "net_buy_shares": -200000}
            ],
            "dealer": [
              {"rank": 1, "stock_name": "群創", "ticker": "3481", "net_buy_shares": -4000000},
              {"rank": 2, "stock_name": "群益證", "ticker": "6005", "net_buy_shares": 1800000},
              {"rank": 3, "stock_name": "友達", "ticker": "2409", "net_buy_shares": -2500000}
            ]
          },
          "key_brokerage_branches": [
            {"branch_name": "美商高盛", "action": "buy", "target": "台積電", "shares": 1800000},
            {"branch_name": "凱基台北", "action": "buy", "target": "世芯-KY", "shares": 250000},
            {"branch_name": "摩根大通", "action": "sell", "target": "鴻海", "shares": -1500000},
            {"branch_name": "富邦台北", "action": "sell", "target": "創意", "shares": -180000}
          ]
        },
        "news": [
          {
            "id": "news_1",
            "title": "US tightens chip exports to AI sector targeting advanced accelerators",
            "source": "Reuters",
            "link": "https://www.reuters.com/technology/us-tightens-chip-exports-ai-sector-targeting-advanced-accelerators-2026-06",
            "summary": "The US administration announced new rules restricting exports of advanced AI microchips and accelerators to curb military developments, affecting major global chip manufacturers.",
            "full_text": "The Biden administration on Thursday announced a sweeping set of new export controls designed to restrict China's access to advanced semiconductor technology and high-end artificial intelligence chip accelerators. The rules, which expand on restrictions implemented last October, are aimed at preventing the use of Western AI technology in military applications. According to the Department of Commerce, these measures are essential to protect national security interests. However, the restrictions are expected to have a significant impact on global chipmakers, particularly those designing high-performance GPUs and accelerators for data centers. Companies like Nvidia, AMD, and Intel will face tighter licensing requirements for shipping their products to specific regions. Industry analysts suggest this move will accelerate efforts by major tech hubs to build localized supply chains and design proprietary hardware alternatives.",
            "published": today_str + "T08:00:00Z"
          },
          {
            "id": "news_2",
            "title": "Tech stocks rally as inflation concerns ease globally",
            "source": "Bloomberg",
            "link": "https://www.bloomberg.com/news/articles/2026-06/tech-stocks-rally-as-inflation-concerns-ease-globally",
            "summary": "Global markets saw an upward trend today as positive economic indicators eased inflation worries, driving technology stock prices higher across US and Asian exchanges.",
            "full_text": "Shares in major technology companies rallied across global stock markets on Friday as cooling inflation data from both the United States and Europe eased investor concerns about aggressive interest rate hikes. The broad-based technology index gained over two percent, led by semiconductor companies and software service providers. Economic reports showed that consumer price indexes rose at a slower pace than anticipated last month, suggesting that central bank monetary policy is successfully curbing inflation without triggering a severe recession. In Asian markets, tech-heavy exchanges in Taipei, Tokyo, and Seoul closed higher, tracking Wall Street's positive momentum. Analysts believe that if inflation continues to stabilize, central banks may pause their rate hikes later this year, creating a more favorable environment for high-growth tech companies.",
            "published": today_str + "T06:30:00Z"
          }
        ]
    }
    return mock_data

def save_mock_data(output_path):
    data = generate_mock_raw_data()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Mock raw data successfully saved to: {output_path}")

if __name__ == "__main__":
    # If run directly, write to standard raw_data path
    default_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "raw_data.json")
    save_mock_data(default_path)
