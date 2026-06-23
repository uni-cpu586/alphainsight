# -*- coding: utf-8 -*-
import os
import json
import argparse
import time
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

# --- CALL LLM APIs ---
def call_gemini(system_prompt, user_prompt, api_key):
    # Use Gemini REST API directly
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    
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
    
    max_retries = 5
    backoff_factor = 2
    max_sleep_time = 30.0  # Limit max sleep time per retry to 30 seconds
    request_timeout = 60   # Limit single request timeout to 60 seconds
    
    for attempt in range(max_retries):
        text_response = ""
        try:
            response = requests.post(url, json=payload, timeout=request_timeout)
            if response.status_code == 200:
                result = response.json()
                # Parse Gemini text response
                text_response = result["candidates"][0]["content"]["parts"][0]["text"]
                
                # Clean markdown formatting if present
                cleaned = text_response.strip()
                if cleaned.startswith("```json"):
                    cleaned = cleaned[7:]
                elif cleaned.startswith("```"):
                    cleaned = cleaned[3:]
                if cleaned.endswith("```"):
                    cleaned = cleaned[:-3]
                cleaned = cleaned.strip()
                
                return json.loads(cleaned)
            elif response.status_code in [429, 500, 502, 503, 504]:
                retry_delay = 5.0
                if response.status_code == 429:
                    try:
                        err_data = response.json()
                        details = err_data.get("error", {}).get("details", [])
                        for detail in details:
                            if detail.get("@type") == "type.googleapis.com/google.rpc.RetryInfo":
                                delay_str = detail.get("retryDelay", "5s")
                                if delay_str.endswith("s"):
                                    retry_delay = float(delay_str[:-1])
                                else:
                                    retry_delay = float(delay_str)
                                break
                    except Exception:
                        pass
                
                sleep_time = min(retry_delay * (backoff_factor ** attempt), max_sleep_time)
                if attempt < max_retries - 1:
                    print(f"Gemini API returned status code {response.status_code}. Retrying in {sleep_time:.2f} seconds (Attempt {attempt+1}/{max_retries})...")
                    time.sleep(sleep_time)
                else:
                    print(f"Gemini API returned status code {response.status_code} on final attempt.")
            else:
                print(f"Gemini API returned status code: {response.status_code}, error: {response.text}")
                return None
        except Exception as e:
            print(f"Gemini API call failed: {e}")
            if text_response:
                print("--- Text Response Snippet (first 1000 chars) ---")
                print(text_response[:1000])
                print("--- End of Snippet ---")
            
            sleep_time = min(5.0 * (backoff_factor ** attempt), max_sleep_time)
            if attempt < max_retries - 1:
                print(f"Retrying in {sleep_time:.2f} seconds...")
                time.sleep(sleep_time)
            else:
                return None
    return None

def call_ollama(system_prompt, user_prompt, model="llama3.2"):
    hosts = ["http://localhost:11434", "http://127.0.0.1:11435", "http://localhost:11435"]
    env_host = os.getenv("OLLAMA_HOST")
    if env_host:
        if not env_host.startswith("http"):
            env_host = f"http://{env_host}"
        hosts.insert(0, env_host)
        
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
    
    last_err = None
    for host in hosts:
        url = f"{host.rstrip('/')}/api/chat"
        try:
            response = requests.post(url, json=payload, timeout=120)
            if response.status_code == 200:
                content = response.json().get("message", {}).get("content", "")
                
                cleaned = content.strip()
                if cleaned.startswith("```json"):
                    cleaned = cleaned[7:]
                elif cleaned.startswith("```"):
                    cleaned = cleaned[3:]
                if cleaned.endswith("```"):
                    cleaned = cleaned[:-3]
                cleaned = cleaned.strip()
                
                try:
                    return json.loads(cleaned)
                except Exception as e:
                    print(f"Ollama JSON parse failed: {e}")
                    print(f"Content snippet (first 1000 chars): {content[:1000]}")
                    raise e
            else:
                print(f"Ollama host {host} returned status: {response.status_code}")
        except Exception as e:
            last_err = e
            continue
            
    print(f"Failed to connect to local Ollama on all hosts {hosts}. Last error: {last_err}")
    return None

def run_processor(mode, ollama_model):
    if mode not in ["gemini", "hybrid"]:
        raise ValueError("Only 'gemini' and 'hybrid' modes are allowed. Mock and pure Ollama modes are strictly disabled.")

    base_dir = os.path.dirname(os.path.dirname(__file__))
    raw_data_path = os.path.join(base_dir, "data", "raw_data.json")
    
    # 1. Load Raw Data
    if not os.path.exists(raw_data_path):
        raise FileNotFoundError(f"Error: {raw_data_path} not found. Please run crawler.py first.")
        
    with open(raw_data_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)
        
    # Load previous processed insights if exists
    prev_insights = {}
    processed_insights_path = os.path.join(base_dir, "frontend", "data", "processed_insights.json")
    if os.path.exists(processed_insights_path):
        try:
            with open(processed_insights_path, "r", encoding="utf-8") as f:
                prev_insights = json.load(f)
        except Exception as e:
            print(f"Warning: Failed to load previous processed insights: {e}")
            
    # Check if Taiwan market was closed yesterday
    import datetime
    tz_offset = datetime.timezone(datetime.timedelta(hours=8))
    today_tw = datetime.datetime.now(tz_offset).date()
    yesterday_tw = today_tw - datetime.timedelta(days=1)
    
    raw_date_str = raw_data.get("date")
    try:
        raw_date = datetime.datetime.strptime(raw_date_str, "%Y-%m-%d").date()
    except Exception as e:
        print(f"Error parsing raw data date {raw_date_str}: {e}")
        raw_date = today_tw
        
    stock_market_date_str = raw_data.get("stock_market_date", raw_date_str)
    try:
        stock_market_date = datetime.datetime.strptime(stock_market_date_str, "%Y-%m-%d").date()
        market_closed_yesterday = (stock_market_date < yesterday_tw)
    except Exception as e:
        print(f"Error parsing stock market date {stock_market_date_str}: {e}")
        market_closed_yesterday = False
        
    # Load character prompts
    uncle_sys = read_skill_prompt("stock-uncle")
    prof_sys = read_skill_prompt("english-professor")
    linker_sys = read_skill_prompt("market-linker")
    
    date_str = raw_data.get("date", datetime.date.today().isoformat())
    try:
        dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        md_str = f"{dt.month}/{dt.day}"
    except:
        md_str = "今日"
        
    stock_market_str = json.dumps(raw_data["stock_market"], ensure_ascii=False)
    news_str = json.dumps(raw_data["news"], ensure_ascii=False)
    
    # Define tasks
    uncle_user = (
        f"以下是 {md_str} 的台股三大法人買賣超前10名與關鍵分點數據：{stock_market_str}。\n"
        f"同時結合今日國際新聞以提供宏觀視野：{news_str}。\n"
        f"請根據你的自營叔叔角色設定，推論主力大戶的操盤思維。\n"
        f"【重要注意事項】：\n"
        f"1. 『buyer_groups』與『top_brokerages_analysis』中的個股分析必須完全對應台股買賣超數據中的台灣股票（如長榮航、友達、華航、聯電、群創等），絕對不能包含國際新聞中的美股或外國公司（如 SpaceX, AtaiBeckley, Coinbase, Mark Cuban 等）！\n"
        f"2. 『buyer_groups』必須嚴格包含三個大戶分類且名稱必須如下：\n"
        f"   - 『1. 外資大戶：[描述買超主題]』\n"
        f"   - 『2. 投信大戶（本土國家隊）：[描述買超主題]』\n"
        f"   - 『3. 內資主力與實戶：[描述買超主題]』\n"
        f"3. 請在股票描述中寫出叔叔對該檔股票大戶動向的毒舌白話解說，並包含買超張數/天數描述（可從張數數據中除以 1000 換算為張數，或進行合理估計，如長榮航買超 10.2 萬張）。\n"
        f"你必須『嚴格』只輸出一個 JSON 物件（不要包裹在 ```json 代碼塊中），且包含以下欄位：\n"
        f"- date_header (字串，標題，如「{md_str} 法人與主力大戶主要買超股票」)\n"
        f"- buyer_groups (陣列，包含 3 個上述的主力大戶分類，每個分組物件包含 group_title 與 stocks 陣列 [每個股票包含 stock_name, ticker, description])\n"
        f"- strategies (陣列，包含至少 3 個操盤邏輯策略，每個策略物件包含 strategy_title 與 strategy_content)\n"
        f"- summary (字串，叔叔給肖年仔的操盤總結)\n"
        f"- top_brokerages_analysis (陣列，每個分點一個物件，欄位包含 branch_name, action, uncle_logic)"
    )
    
    linker_user = f"{md_str} 的台股數據為：{stock_market_str}；下午的國際財經新聞為：{news_str}。請根據你作為暴力聯結器的設定，進行跨市場大腦聯結推理，並『嚴格』只輸出一個 JSON 物件，包含以下欄位：\n- violence_connection (字串，約 200-350 字的精彩推理，探討兩者間的可能因果關係或主力暗度陳倉行為)"

    # Initialize results
    stock_uncle_insight = None
    english_professor_news = None
    market_linker_insight = None
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables. Gemini API key is required to run the processor.")
    
    # Execute LLM calls
    # 1. Run Stock Uncle (Always run with gemini as requested)
    print("1. Processing Stock Uncle...")
    if market_closed_yesterday:
        print("   - Yesterday was a market holiday or weekend. Skipping Stock Uncle AI processing. Reusing previous report...")
        stock_uncle_insight = prev_insights.get("stock_uncle_insight")
        if not stock_uncle_insight:
            stock_uncle_insight = {
                "date_header": f"{raw_date.month}/{raw_date.day} 昨日台股休市，無大戶籌碼分析數據",
                "buyer_groups": [],
                "strategies": [],
                "summary": "昨日台股休市，且無歷史資料可用。",
                "top_brokerages_analysis": []
            }
    else:
        stock_uncle_insight = call_gemini(uncle_sys, uncle_user, api_key)
        if not stock_uncle_insight:
            raise RuntimeError("Failed to get response or parse JSON from Gemini API for Stock Uncle module.")
            
    # 2. Run English Professor article-by-article
    print("2. Processing English Professor (article by article)...")
    english_professor_news = []
    chosen_keywords = []
    for idx, item in enumerate(raw_data["news"]):
        print(f"   - Processing article {idx+1}/{len(raw_data['news'])}: {item.get('title')[:40]}...")
        single_news_str = json.dumps(item, ensure_ascii=False)
        
        avoid_clause = ""
        if chosen_keywords:
            avoid_clause = f"且挑選的核心單字絕對不能與以下先前已選的單字重複：{', '.join(chosen_keywords)}。"
            
        prof_user = (
            f"以下是今日抓取的一篇新聞原始資料：{single_news_str}。\n"
            f"請根據你的留美財經科技教授設定，針對這條新聞，『嚴格』只輸出一個 JSON 物件（不要包裹在 ```json 代碼塊中），包含以下欄位：\n"
            f"- news_id (對應原始資料中的 id 欄位)\n"
            f"- title (新聞英文標題)\n"
            f"- source (新聞來源)\n"
            f"- link (新聞連結)\n"
            f"- level1_blind (包含 text 欄位，將這篇長篇新聞（full_text 欄位）的內容完整放入作為盲讀與聽力文本)\n"
            f"- level2_keywords (包含 5 個關鍵字物件陣列，從文章中挑選 5 個核心產業單字，每個物件欄位為 word, ipa, meaning, example。{avoid_clause})\n"
            f"- level2_context (字串，該新聞的白話宏觀背景提示，不用直接翻譯，而是以中文解釋其產業與政經背景脈絡)\n"
            f"- level3_translation (陣列，請將整篇長篇 'full_text' 的每一句英文拆解，包含 sentence 與 translation 欄位，完成全文對應之繁體中文白話翻譯。務必完成每一句的翻譯，不可為空字串！)\n\n"
            f"【極重要 JSON 格式規範】：\n"
            f"1. 請確保輸出的整個 JSON 格式合法且可被解析。\n"
            f"2. 所有的字串欄位（如 title、meaning、example、translation、level2_context 等）如果包含引號，請務必改用中文的「」與『』代替（切勿直接使用未逸出的半形雙引號 \")，否則會導致 JSON 解析器崩潰。"
        )
        
        if mode == "gemini":
            result = call_gemini(prof_sys, prof_user, api_key)
        else: # hybrid mode -> run other with local ollama
            result = call_ollama(prof_sys, prof_user, ollama_model)
            if not result:
                print("Warning: Ollama call failed. Falling back to Gemini API...")
                result = call_gemini(prof_sys, prof_user, api_key)
            
        if not result:
            raise RuntimeError(f"Failed to get response or parse JSON from AI for English Professor article {idx+1} in mode {mode}.")
            
        # Validate result
        if isinstance(result, dict) and "level3_translation" in result:
            english_professor_news.append(result)
            keywords = result.get("level2_keywords", [])
            for kw in keywords:
                if isinstance(kw, dict) and "word" in kw:
                    chosen_keywords.append(kw["word"].lower().strip())
        else:
            raise RuntimeError(f"Invalid JSON format or missing required fields from AI for English Professor article {idx+1}. Result: {result}")

    # 3. Run Market Linker
    print("3. Processing Market Linker...")
    if mode == "gemini":
        market_linker_insight = call_gemini(linker_sys, linker_user, api_key)
    else: # hybrid mode -> run other with local ollama
        market_linker_insight = call_ollama(linker_sys, linker_user, ollama_model)
        if not market_linker_insight:
            print("Warning: Ollama call failed. Falling back to Gemini API...")
            market_linker_insight = call_gemini(linker_sys, linker_user, api_key)
        
    if not market_linker_insight:
        raise RuntimeError(f"Failed to get response or parse JSON from AI for Market Linker module in mode {mode}.")
        
    # --- Structural Validation ---
    if not isinstance(stock_uncle_insight, dict) or "buyer_groups" not in stock_uncle_insight:
        raise RuntimeError("Stock Uncle output is missing 'buyer_groups' or is not a valid object.")
    if not isinstance(market_linker_insight, dict) or "violence_connection" not in market_linker_insight:
        raise RuntimeError("Market Linker output is missing 'violence_connection' or is not a valid object.")

    # Ensure date_header exists dynamically
    if "date_header" not in stock_uncle_insight or not stock_uncle_insight["date_header"]:
        stock_uncle_insight["date_header"] = f"{md_str} 法人與主力大戶主要買超股票"

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
    parser.add_argument("--mode", type=str, choices=["gemini", "hybrid"], default="hybrid",
                        help="AI mode: gemini (all cloud API) or hybrid (stock_uncle on gemini, others on ollama)")
    parser.add_argument("--model", type=str, default="llama3.2",
                        help="Model name for hybrid mode (default: llama3.2)")
                        
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

        # Generate Audio Files using Edge TTS
        print("\nGenerating Microsoft Edge TTS en-US-AndrewNeural audio files...")
        audio_dir = os.path.join(frontend_data_dir, "audio")
        os.makedirs(audio_dir, exist_ok=True)
        
        import asyncio
        import edge_tts
        
        async def make_audios():
            for idx, news in enumerate(result_data.get("english_professor_news", [])):
                text = news.get("level1_blind", {}).get("text", "")
                if text:
                    audio_path = os.path.join(audio_dir, f"news_{idx+1}.mp3")
                    print(f" - Generating audio for article {idx+1}: {audio_path}")
                    communicate = edge_tts.Communicate(text, "en-US-AndrewNeural")
                    await communicate.save(audio_path)
                    
        try:
            asyncio.run(make_audios())
            print("Edge TTS Audio generation completed successfully!")
        except Exception as e:
            print(f"Warning: Failed to generate TTS audio: {e}")
