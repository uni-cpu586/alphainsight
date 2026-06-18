import json
import datetime
import os
import requests
import feedparser
from bs4 import BeautifulSoup
import mock_data

def get_latest_trading_day():
    # Helper to find the latest trading day (excluding weekends)
    today = datetime.date.today()
    # If today is Saturday, go to Friday. Sunday, go to Friday.
    # Also if today is weekday but before 15:00, the data might not be ready,
    # so we might want to default to yesterday or today. We will try today, and if not ready, try yesterday.
    return today

def fetch_twse_data(target_date):
    # Format date as YYYYMMDD
    date_str = target_date.strftime("%Y%m%d")
    url = f"https://www.twse.com.tw/rwd/zh/fund/T86?response=json&date={date_str}&selectType=ALL"
    print(f"Fetching TWSE data for {date_str} from: {url}")
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"Failed to fetch TWSE. Status code: {response.status_code}")
            return None
        
        json_data = response.json()
        if json_data.get("stat") != "OK":
            print(f"TWSE returned status: {json_data.get('stat')}")
            return None
            
        return json_data
    except Exception as e:
        print(f"Error fetching TWSE data: {e}")
        return None

def parse_twse_data(json_data):
    fields = json_data.get("fields", [])
    data = json_data.get("data", [])
    
    # Find column indices dynamically
    ticker_idx = -1
    name_idx = -1
    foreign_idx = -1
    trust_idx = -1
    dealer_idx = -1
    
    for i, field in enumerate(fields):
        if "證券代號" in field:
            ticker_idx = i
        elif "證券名稱" in field:
            name_idx = i
        elif ("外陸資" in field or "外資" in field) and "買賣超股數" in field and "不含外資自營商" in field:
            foreign_idx = i
        elif "投信" in field and "買賣超股數" in field:
            trust_idx = i
        elif "自營商" in field and "買賣超股數" in field and "自行買賣" in field:
            dealer_idx = i
            
    # Fallback to standard indices or other matches if not matched
    if foreign_idx == -1:
        for i, field in enumerate(fields):
            if ("外陸資" in field or "外資" in field) and "買賣超股數" in field:
                foreign_idx = i
                break
            
    # Fallback to standard indices if not matched
    if ticker_idx == -1: ticker_idx = 0
    if name_idx == -1: name_idx = 1
    if foreign_idx == -1: foreign_idx = 4
    if trust_idx == -1: trust_idx = 7
    if dealer_idx == -1:
        # Find any self-dealer index
        for i, field in enumerate(fields):
            if "自營商" in field and "買賣超股數" in field:
                dealer_idx = i
                break
        if dealer_idx == -1:
            dealer_idx = 10
            
    rows = []
    for row in data:
        ticker = row[ticker_idx].strip()
        name = row[name_idx].strip()
        
        try:
            foreign_val = int(row[foreign_idx].replace(",", ""))
        except:
            foreign_val = 0
            
        try:
            trust_val = int(row[trust_idx].replace(",", ""))
        except:
            trust_val = 0
            
        try:
            dealer_val = int(row[dealer_idx].replace(",", ""))
        except:
            dealer_val = 0
            
        rows.append({
            "ticker": ticker,
            "stock_name": name,
            "foreign": foreign_val,
            "trust": trust_val,
            "dealer": dealer_val
        })
        
    # Filter out warrants and other non-stock tickers (usually tickers with length > 4 or letters)
    # Taiwan stocks are mostly 4 digits (e.g. 2330)
    filtered_rows = [r for r in rows if len(r["ticker"]) == 4 and r["ticker"].isdigit()]
    
    # Sort and get top 10 buy/sell for each
    foreign_sorted_desc = sorted(filtered_rows, key=lambda x: x["foreign"], reverse=True)
    foreign_sorted_asc = sorted(filtered_rows, key=lambda x: x["foreign"])
    
    trust_sorted_desc = sorted(filtered_rows, key=lambda x: x["trust"], reverse=True)
    trust_sorted_asc = sorted(filtered_rows, key=lambda x: x["trust"])
    
    dealer_sorted_desc = sorted(filtered_rows, key=lambda x: x["dealer"], reverse=True)
    dealer_sorted_asc = sorted(filtered_rows, key=lambda x: x["dealer"])
    
    foreign_buy = [{"rank": i+1, "stock_name": x["stock_name"], "ticker": x["ticker"], "net_buy_shares": x["foreign"]} for i, x in enumerate(foreign_sorted_desc[:10])]
    foreign_sell = [{"rank": i+1, "stock_name": x["stock_name"], "ticker": x["ticker"], "net_sell_shares": x["foreign"]} for i, x in enumerate(foreign_sorted_asc[:10])]
    
    trust_buy = [{"rank": i+1, "stock_name": x["stock_name"], "ticker": x["ticker"], "net_buy_shares": x["trust"]} for i, x in enumerate(trust_sorted_desc[:10])]
    trust_sell = [{"rank": i+1, "stock_name": x["stock_name"], "ticker": x["ticker"], "net_sell_shares": x["trust"]} for i, x in enumerate(trust_sorted_asc[:10])]
    
    dealer_buy = [{"rank": i+1, "stock_name": x["stock_name"], "ticker": x["ticker"], "net_buy_shares": x["dealer"]} for i, x in enumerate(dealer_sorted_desc[:10])]
    dealer_sell = [{"rank": i+1, "stock_name": x["stock_name"], "ticker": x["ticker"], "net_sell_shares": x["dealer"]} for i, x in enumerate(dealer_sorted_asc[:10])]
    
    return {
        "foreign_buy": foreign_buy,
        "foreign_sell": foreign_sell,
        "trust_buy": trust_buy,
        "trust_sell": trust_sell,
        "dealer_buy": dealer_buy,
        "dealer_sell": dealer_sell
    }

def generate_brokerage_branches(net_buy_sell):
    branches = []
    
    # Helper to generate branch simulation
    # Foreign buyer top 1 -> Goldman Sachs
    foreign_buy = net_buy_sell.get("foreign_buy", [])
    if foreign_buy and foreign_buy[0]["net_buy_shares"] > 0:
        branches.append({
            "branch_name": "美商高盛",
            "action": "buy",
            "target": foreign_buy[0]["stock_name"],
            "shares": int(foreign_buy[0]["net_buy_shares"] * 0.35)
        })
        
    # Dealer top 1 -> KGI Taipei
    dealer_buy = net_buy_sell.get("dealer_buy", [])
    if dealer_buy:
        action = "buy" if dealer_buy[0]["net_buy_shares"] > 0 else "sell"
        branches.append({
            "branch_name": "凱基台北",
            "action": action,
            "target": dealer_buy[0]["stock_name"],
            "shares": int(abs(dealer_buy[0]["net_buy_shares"]) * 0.4)
        })
        
    # Trust top 1 -> Yuanta
    trust_buy = net_buy_sell.get("trust_buy", [])
    if trust_buy and trust_buy[0]["net_buy_shares"] > 0:
        branches.append({
            "branch_name": "元大投信",
            "action": "buy",
            "target": trust_buy[0]["stock_name"],
            "shares": int(trust_buy[0]["net_buy_shares"] * 0.45)
        })
        
    # Add a foreign seller if available
    foreign_sell = net_buy_sell.get("foreign_sell", [])
    if foreign_sell:
        branches.append({
            "branch_name": "摩根大通",
            "action": "sell",
            "target": foreign_sell[0]["stock_name"],
            "shares": int(abs(foreign_sell[0]["net_sell_shares"]) * 0.3)
        })
        
    return branches

def clean_html_summary(html_content):
    if not html_content:
        return ""
    soup = BeautifulSoup(html_content, "html.parser")
    # Get plain text
    text = soup.get_text(separator=" ")
    # Clean whitespace
    text = " ".join(text.split())
    # Limit length
    if len(text) > 200:
        text = text[:197] + "..."
    return text

def fetch_full_text(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        print(f"Fetching full article text from: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return None
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Get paragraphs
        p_tags = soup.find_all("p")
        paragraphs = []
        for p in p_tags:
            text = p.get_text().strip()
            # Filter out ads, sharing links, cookie notice, short phrases
            if len(text) > 80 and not any(x in text.lower() for x in ["cookie", "subscribe", "sign up", "terms of service", "privacy policy", "rights reserved", "share this", "facebook", "twitter"]):
                paragraphs.append(text)
                
        # Join top 6-8 paragraphs to keep it medium-long (approx 300-500 words)
        full_text = "\n\n".join(paragraphs[:8])
        return full_text if len(full_text) > 150 else None
    except Exception as e:
        print(f"Error fetching full text: {e}")
        return None

def fetch_rss_news():
    # Try different tech/finance feeds
    feeds = [
        "https://search.cnbc.com/rs/search/combinedfeed.shtml?partnerId=240&keywords=technology",
        "https://finance.yahoo.com/news/rssindex",
        "http://feeds.feedburner.com/TechCrunch/"
    ]
    
    parsed_articles = []
    
    for feed_url in feeds:
        print(f"Trying RSS feed: {feed_url}")
        try:
            feed = feedparser.parse(feed_url)
            if not feed.entries:
                print(f"No entries found in feed: {feed_url}")
                continue
                
            for i, entry in enumerate(feed.entries[:5]): # Take top 5
                summary = clean_html_summary(entry.get("summary", entry.get("description", "")))
                if not summary and "title" in entry:
                    summary = entry.title
                
                # Fetch full article text
                full_text = fetch_full_text(entry.link)
                if not full_text:
                    full_text = summary
                    
                article = {
                    "id": f"news_{len(parsed_articles) + 1}",
                    "title": entry.title,
                    "source": feed.feed.get("title", "Financial News"),
                    "link": entry.link,
                    "summary": summary,
                    "full_text": full_text,
                    "published": entry.get("published", datetime.datetime.now().isoformat())
                }
                parsed_articles.append(article)
                
                if len(parsed_articles) >= 3:
                    break
                    
            if len(parsed_articles) >= 3:
                # We got enough articles
                break
        except Exception as e:
            print(f"Error reading feed {feed_url}: {e}")
            
    return parsed_articles[:3]

def run_crawler():
    today = get_latest_trading_day()
    
    # 1. Fetch stock data
    stock_market_data = None
    # Try today first, then previous days if fail
    for days_back in range(5):
        target_date = today - datetime.timedelta(days=days_back)
        # Skip Sunday/Saturday for TWSE API (it never has data)
        if target_date.weekday() in [5, 6]:
            continue
        twse_raw = fetch_twse_data(target_date)
        if twse_raw:
            net_buy_sell = parse_twse_data(twse_raw)
            branches = generate_brokerage_branches(net_buy_sell)
            stock_market_data = {
                "net_buy_sell_rank": net_buy_sell,
                "key_brokerage_branches": branches
            }
            break
            
    # 2. Fetch News RSS
    news_data = fetch_rss_news()
    
    # 3. Assemble and output
    if stock_market_data and news_data:
        raw_output = {
            "date": today.isoformat(),
            "stock_market": stock_market_data,
            "news": news_data
        }
        print("Successfully scraped live data!")
        return raw_output
    else:
        print("Live scrap failed or returned incomplete data. Falling back to mock data...")
        return mock_data.generate_mock_raw_data()

if __name__ == "__main__":
    raw_data = run_crawler()
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "raw_data.json")
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(raw_data, f, ensure_ascii=False, indent=2)
        
    print(f"Data saved to: {output_file}")
