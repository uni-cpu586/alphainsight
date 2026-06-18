import os
import json
import argparse
import requests
from dotenv import load_dotenv

# Load env variables from .env if present
load_dotenv()

def read_skill_prompt(skill_name):
    # Try to load the system prompt from SKILL.md
    base_dir = os.path.dirname(os.path.dirname(__file__))
    skill_path = os.path.join(base_dir, ".agents", "skills", skill_name, "SKILL.md")
    
    if os.path.exists(skill_path):
        with open(skill_path, "r", encoding="utf-8") as f:
            content = f.read()
            # Extract prompt content (skip frontmatter if exists)
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    return parts[2].strip()
            return content.strip()
    else:
        print(f"Warning: SKILL.md for {skill_name} not found. Using simple default prompt.")
        return f"You are a helpful AI acting as {skill_name}."

# --- MOCK GENERATOR FOR FALLBACKS ---
def generate_mock_processed_insights(raw_data):
    today = raw_data.get("date", "2026-06-18")
    stock_market = raw_data.get("stock_market", {})
    net_buy_sell = stock_market.get("net_buy_sell_rank", {})
    news_list = raw_data.get("news", [])
    
    # Extract top names
    foreign_buy_name = net_buy_sell.get("foreign_investors", [{}])[0].get("stock_name", "長榮航")
    trust_buy_name = net_buy_sell.get("investment_trust", [{}])[0].get("stock_name", "聯電")
    dealer_buy_name = net_buy_sell.get("dealer", [{}])[0].get("stock_name", "群創")
    
    mock_processed = {
        "date": today,
        "stock_uncle_insight": {
            "market_sentiment": f"肖年仔！今天大戶看起來很保守，外資大買【{foreign_buy_name}】，但融資在高檔。短線自營商狂買【{dealer_buy_name}】只是在跟權證對沖避險，別傻傻追進去！",
            "top_brokerages_analysis": [
                {
                    "branch_name": "凱基台北",
                    "action": f"大買【{dealer_buy_name}】",
                    "uncle_logic": f"凱基台北操作極短線，這波是『隔日沖』。明天開高大概就會看到大單往下砸，想跟單的自己皮繃緊一點，別被割韭菜了。"
                },
                {
                    "branch_name": "美商高盛",
                    "action": f"敲進【{foreign_buy_name}】",
                    "uncle_logic": f"高盛這隻大金牛通常是幫長線基金代操，今天大買【{foreign_buy_name}】代表這檔股票在低檔有支撐，是利多潛伏型的布局，可以留意拉回時的波段機會。"
                },
                {
                    "branch_name": "元大投信",
                    "action": f"建倉【{trust_buy_name}】",
                    "uncle_logic": f"投信最近這幾天連買【{trust_buy_name}】，看來是在為季底作帳行情做準備。這檔屬於波段鎖碼型，跟著投信的成本區走問題不大。"
                }
            ],
            "overall_strategy": "自營叔叔真心建議：持股成數先收縮到三成左右。明天開盤前半小時如果大盤成交量縮水，就代表追高意願不足，多看少動才是股市生存之道啦！"
        },
        "english_professor_news": [],
        "market_linker_insight": {
            "violence_connection": f"【大腦暴力聯結】今天清晨路透社報導美股科技股的最新利多，提到 AI 晶片需求依然旺盛。這正好合理解釋了為什麼早盤外資大買半導體權值股【{trust_buy_name}】，且特定分點在低檔提早收貨。自營叔叔分析的『主力潛伏布局』，背後其實是國際半導體供應鏈板塊的利多傳導。建議肖年仔多注意今晚美股開盤後相關板塊的表現，這會直接決定明早台股開盤的氣勢！"
        }
    }
    
    # Process news list mock
    for item in news_list:
        title = item.get("title", "News Title")
        summary = item.get("summary", "News summary.")
        full_text = item.get("full_text", summary)
        
        # Split full text into sentences
        import re
        sentences = [s.strip() + "." for s in re.split(r'\. ', full_text) if s.strip()]
        # Remove trailing period if doubled
        sentences = [s[:-1] if s.endswith("..") else s for s in sentences]
        
        # Determine which mock translation dictionary to use
        is_news_1 = "Biden" in full_text or "export" in title.lower() or "US tightens" in title
        
        if is_news_1:
            mock_translations = {
                "The Biden administration on Thursday announced a sweeping set of new export controls designed to restrict China's access to advanced semiconductor technology and high-end artificial intelligence chip accelerators.": 
                "拜登政府週四宣布了一套全面的新出口管制措施，旨在限制中國獲取先進半導體技術和高端人工智慧晶片加速器。",
                "The rules, which expand on restrictions implemented last October, are aimed at preventing the use of Western AI technology in military applications.":
                "這些規則擴展了去年十月實施的限制，旨在防止將西方人工智慧技術用於軍事用途。",
                "According to the Department of Commerce, these measures are essential to protect national security interests.":
                "根據美國商務部的說法，這些措施對於保護國家安全利益至關重要。",
                "However, the restrictions are expected to have a significant impact on global chipmakers, particularly those designing high-performance GPUs and accelerators for data centers.":
                "然而，這些限制預計將對全球晶片製造商產生重大影響，特別是那些設計用於數據中心的高性能 GPU 和加速器的廠商。",
                "Companies like Nvidia, AMD, and Intel will face tighter licensing requirements for shipping their products to specific regions.":
                "輝達（Nvidia）、超微（AMD）和英特爾（Intel）等公司將面臨更嚴格的許可要求，才能將其產品運送到特定地區。",
                "Industry analysts suggest this move will accelerate efforts by major tech hubs to build localized supply chains and design proprietary hardware alternatives.":
                "行業分析師表示，此舉將加速主要科技中心建立在地化供應鏈並設計自主硬體替代方案的努力。"
            }
        else:
            mock_translations = {
                "Shares in major technology companies rallied across global stock markets on Friday as cooling inflation data from both the United States and Europe eased investor concerns about aggressive interest rate hikes.":
                "由於美國和歐洲降溫的通膨數據緩解了投資人對激進升息的擔憂，主要科技公司的股價週五在全球股市中迎來反彈。",
                "The broad-based technology index gained over two percent, led by semiconductor companies and software service providers.":
                "在半導體公司 and 軟體服務提供商的帶領下，廣泛的科技指數上漲了超過 2%。",
                "Economic reports showed that consumer price indexes rose at a slower pace than anticipated last month, suggesting that central bank monetary policy is successfully curbing inflation without triggering a severe recession.":
                "經濟報告顯示，上個月消費者物價指數的上漲速度低於預期，這表明央行的貨幣政策成功遏制了通膨，而沒有引發嚴重的衰退。",
                "In Asian markets, tech-heavy exchanges in Taipei, Tokyo, and Seoul closed higher, tracking Wall Street's positive momentum.":
                "在亞洲市場，受華爾街利多勢頭的推動，台北、東京和首爾等科技股比重較高的交易所收盤走高。",
                "Analysts believe that if inflation continues to stabilize, central banks may pause their rate hikes later this year, creating a more favorable environment for high-growth tech companies.":
                "分析師認為，如果通膨繼續穩定，央行可能會在今年晚些時候暫停升息，從而為高成長的科技公司創造更有利的環境。"
            }
            
        translations = []
        for s in sentences:
            trans = ""
            for k, v in mock_translations.items():
                if k[:20] in s:
                    trans = v
                    break
            if not trans:
                # Fallback to general message
                trans = f"【白話翻譯】{s}（本句由教授提供之白話語境解析，幫助你深入理解科技產業大勢與句型脈絡）。"
            translations.append({"sentence": s, "translation": trans})

        # Use the entire full text as blind text for Level 1
        blind_text = full_text

        mock_processed["english_professor_news"].append({
            "news_id": item.get("id", "news_1"),
            "title": title,
            "source": item.get("source", "Yahoo Finance"),
            "link": item.get("link", "#"),
            "level1_blind": {
                "text": blind_text
            },
            "level2_keywords": [
                {"word": "rallied", "ipa": "/ˈræl.id/", "meaning": "（價格等）回升，止跌回升", "example": "The stock market rallied after the inflation report was released."},
                {"word": "restricting", "ipa": "/rɪˈstrɪkt.ɪŋ/", "meaning": "限制，約束", "example": "The government is restricting export of advanced semiconductors."},
                {"word": "accelerators", "ipa": "/ækˈsel.ə.reɪ.tərz/", "meaning": "加速晶片（如 AI 運算 GPU）", "example": "Data centers require high-end AI accelerators to run LLMs."},
                {"word": "curb", "ipa": "/kɜːb/", "meaning": "控制，遏制", "example": "New regulations aim to curb illegal market activities."},
                {"word": "outlook", "ipa": "/ˈaʊt.lʊk/", "meaning": "前景，展望指引", "example": "The company adjusted its quarterly revenue outlook due to news."}
            ],
            "level2_context": "白話背景：這篇新聞在探討國際政經政策對核心科技產業（如晶片出口、通膨升息）造成的宏觀影響。這些變動會透過半導體與伺服器代工供應鏈，在幾天內迅速傳導至台灣股市，是主力資金調度的重要風向球。",
            "level3_translation": translations
        })
        
    return mock_processed


# --- CALL LLM APIs ---
def call_ollama(system_prompt, user_prompt, model="llama3"):
    url = "http://localhost:11434/api/chat"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "options": {
            "temperature": 0.3
        },
        "stream": False,
        "format": "json" # Ollama force JSON mode
    }
    
    try:
        response = requests.post(url, json=payload, timeout=120)
        if response.status_code == 200:
            content = response.json().get("message", {}).get("content", "")
            return json.loads(content)
        else:
            print(f"Ollama returned status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Failed to connect to local Ollama: {e}")
        return None

def call_gemini(system_prompt, user_prompt, api_key):
    # Use Gemini REST API directly
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={api_key}"
    
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": f"System Prompt/Role:\n{system_prompt}\n\nUser Request:\n{user_prompt}"}
                ]
            }
        ],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.3
        }
    }
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        if response.status_code == 200:
            result = response.json()
            # Parse Gemini text response
            text_response = result["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(text_response)
        else:
            print(f"Gemini API returned status code: {response.status_code}, error: {response.text}")
            return None
    except Exception as e:
        print(f"Gemini API call failed: {e}")
        return None


def run_processor(mode, ollama_model):
    base_dir = os.path.dirname(os.path.dirname(__file__))
    raw_data_path = os.path.join(base_dir, "data", "raw_data.json")
    
    # 1. Load Raw Data
    if not os.path.exists(raw_data_path):
        print(f"Error: {raw_data_path} not found. Please run crawler.py first.")
        return
        
    with open(raw_data_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)
        
    # Check if we should fallback to mock
    if mode == "mock":
        print("Running in MOCK mode. Generating simulated AI insights...")
        return generate_mock_processed_insights(raw_data)
        
    # Load character prompts
    uncle_sys = read_skill_prompt("stock-uncle")
    prof_sys = read_skill_prompt("english-professor")
    linker_sys = read_skill_prompt("market-linker")
    
    stock_market_str = json.dumps(raw_data["stock_market"], ensure_ascii=False)
    news_str = json.dumps(raw_data["news"], ensure_ascii=False)
    
    # Define tasks
    uncle_user = f"以下是今天的台股數據：{stock_market_str}。請根據你的自營叔叔角色設定，推論主力的操盤思維，並『嚴格』只輸出一個 JSON 物件，包含以下欄位：\n- market_sentiment (字串，一句話形容大戶今日情緒)\n- top_brokerages_analysis (陣列，每個分點一個物件，欄位包含 branch_name, action, uncle_logic)\n- overall_strategy (字串，叔叔給肖年仔的白話操作策略建議)"
    
    prof_user = f"以下是今日抓取的新聞原始資料：{news_str}。請特別針對每個新聞的 'full_text' 欄位（這是長篇新聞原文）進行分析與翻譯。請根據你的財經英語教授設定，針對每條新聞，『嚴格』只輸出一個 JSON 陣列，陣列中每個新聞包含以下欄位：\n- news_id (同 raw_data 的 id)\n- title (新聞英文標題)\n- source (新聞來源)\n- link (新聞連結)\n- level1_blind (包含 text 欄位，將整篇長篇新聞（full_text）完整放入作為盲讀與聽力文本)\n- level2_keywords (包含 5 個關鍵字物件陣列，每個物件欄位為 word, ipa, meaning, example)\n- level2_context (字串，該新聞的白話宏觀背景提示，不用字面翻譯)\n- level3_translation (陣列，請將整篇長篇 'full_text' 的每一句英文拆解，包含 sentence 與 translation 欄位，完成全文對應之繁體中文白話翻譯)"
    
    linker_user = f"今天晨間的台股數據為：{stock_market_str}；下午的國際財經新聞為：{news_str}。請根據你作為暴力聯結器的設定，進行跨市場大腦聯結推理，並『嚴格』只輸出一個 JSON 物件，包含以下欄位：\n- violence_connection (字串，約 200-350 字的精彩推理，探討兩者間的可能因果關係或主力暗度陳倉行為)"

    # Initialize results
    stock_uncle_insight = None
    english_professor_news = None
    market_linker_insight = None
    
    # Execute LLM calls
    if mode == "ollama":
        print(f"Calling local Ollama using model '{ollama_model}'...")
        print("1. Processing Stock Uncle...")
        stock_uncle_insight = call_ollama(uncle_sys, uncle_user, ollama_model)
        
        print("2. Processing English Professor...")
        english_professor_news = call_ollama(prof_sys, prof_user, ollama_model)
        
        print("3. Processing Market Linker...")
        market_linker_insight = call_ollama(linker_sys, linker_user, ollama_model)
        
    elif mode == "gemini":
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("Error: GEMINI_API_KEY not found in environment. Please add it to your .env file.")
            print("Falling back to MOCK mode...")
            return generate_mock_processed_insights(raw_data)
            
        print("Calling Google Gemini 1.5 Flash API...")
        print("1. Processing Stock Uncle...")
        stock_uncle_insight = call_gemini(uncle_sys, uncle_user, api_key)
        
        print("2. Processing English Professor...")
        english_professor_news = call_gemini(prof_sys, prof_user, api_key)
        
        print("3. Processing Market Linker...")
        market_linker_insight = call_gemini(linker_sys, linker_user, api_key)
        
    elif mode == "hybrid":
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("Error: GEMINI_API_KEY not found in environment, which is required for hybrid mode (Gemini).")
            print("Falling back to local Ollama for all agents...")
            return run_processor("ollama", ollama_model)
            
        print("Running in HYBRID mode (Ollama + Gemini):")
        # 1. Stock Uncle on Ollama (Local)
        print("1. Processing Stock Uncle using Local Ollama...")
        stock_uncle_insight = call_ollama(uncle_sys, uncle_user, ollama_model)
        
        # 2. English Professor & Market Linker on Gemini (Cloud)
        print("2. Processing English Professor using Google Gemini...")
        english_professor_news = call_gemini(prof_sys, prof_user, api_key)
        
        print("3. Processing Market Linker using Google Gemini...")
        market_linker_insight = call_gemini(linker_sys, linker_user, api_key)
        
    # Check if any LLM call failed. If so, fallback to mock to prevent crashes.
    if not stock_uncle_insight or not english_professor_news or not market_linker_insight:
        print("\n[Warning] One or more AI modules failed to respond or output valid JSON.")
        print("Ollama might not be running or model is not downloaded. Run 'ollama run llama3' first.")
        print("Falling back to MOCK mode for missing or all elements to guarantee output...")
        
        mock_data_res = generate_mock_processed_insights(raw_data)
        if not stock_uncle_insight:
            stock_uncle_insight = mock_data_res["stock_uncle_insight"]
        if not english_professor_news:
            english_professor_news = mock_data_res["english_professor_news"]
        if not market_linker_insight:
            market_linker_insight = mock_data_res["market_linker_insight"]
            
    import datetime
    today_str = datetime.date.today().isoformat()
    return {
        "date": raw_data.get("date", today_str),
        "stock_uncle_insight": stock_uncle_insight,
        "english_professor_news": english_professor_news,
        "market_linker_insight": market_linker_insight
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process raw data with AI Agents.")
    parser.add_argument("--mode", type=str, choices=["ollama", "gemini", "hybrid", "mock"], default="ollama",
                        help="AI mode: ollama (local), gemini (cloud API), hybrid (ollama + gemini), or mock (simulation)")
    parser.add_argument("--model", type=str, default="llama3",
                        help="Ollama model name (default: llama3)")
                        
    args = parser.parse_args()
    
    print(f"AlphaInsight AI Processor started. Mode: {args.mode}")
    result_data = run_processor(args.mode, args.model)
    
    if result_data:
        base_dir = os.path.dirname(os.path.dirname(__file__))
        
        # Write to frontend/data/processed_insights.json so frontend can access it
        frontend_data_dir = os.path.join(base_dir, "frontend", "data")
        os.makedirs(frontend_data_dir, exist_ok=True)
        
        output_file = os.path.join(frontend_data_dir, "processed_insights.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)
            
        print(f"\nProcessing completed successfully! Saved to: {output_file}")
