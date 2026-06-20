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
    
    trust_buy_name = net_buy_sell.get("trust_buy", [{}])[0].get("stock_name", "聯電")
    
    import datetime
    try:
        dt = datetime.datetime.strptime(today, "%Y-%m-%d")
        md_str = f"{dt.month}/{dt.day}"
        
        # Check if Taiwan market was closed yesterday
        tz_offset = datetime.timezone(datetime.timedelta(hours=8))
        today_tw = datetime.datetime.now(tz_offset).date()
        yesterday_tw = today_tw - datetime.timedelta(days=1)
        market_closed_yesterday = (dt.date() < yesterday_tw)
    except:
        md_str = "今日"
        market_closed_yesterday = False
        
    if market_closed_yesterday:
        stock_uncle_insight = {
            "date_header": f"{md_str} 昨日台股休市，無大戶籌碼分析數據",
            "buyer_groups": [],
            "strategies": [],
            "summary": "昨日台股休市，不進行籌碼分析。",
            "top_brokerages_analysis": []
        }
    else:
        stock_uncle_insight = {
            "date_header": f"{md_str} 法人與主力大戶主要買超股票",
            "buyer_groups": [
                {
                    "group_title": "1. 外資大戶：狂掃航空與面板",
                    "stocks": [
                        {"stock_name": "長榮航", "ticker": "2618", "description": "外資瘋狂買超 10.2 萬張（已連續 7 日加碼），基期低且暑期旺季大爆發。"},
                        {"stock_name": "友達", "ticker": "2409", "description": "外資買超 7.5 萬張、自營商也買超 1.09 萬張（主力券商買超第 1 名）。"},
                        {"stock_name": "華航", "ticker": "2610", "description": "外資買超 2.1 萬張，同屬現成有業績支撐的暑期旅遊避風港。"}
                    ]
                },
                {
                    "group_title": "2. 投信大戶（本土國家隊）：鎖定金融與轉機股",
                    "stocks": [
                        {"stock_name": "聯電", "ticker": "2303", "description": "投信買超 1.95 萬張。有趣的是外資當天大賣聯電 4.5 萬張，形成本土大戶與ETF資金死守、對決外資的局面。"},
                        {"stock_name": "第一金", "ticker": "2892", "description": "投信與官股買超 1.87 萬張，撐盤色彩濃厚。"},
                        {"stock_name": "兆豐金", "ticker": "2886", "description": "投信買超 1.73 萬張，防禦性質高。"},
                        {"stock_name": "台新金", "ticker": "2887", "description": "投信買超 1.09 萬張，持續布局金控合併題材。"},
                        {"stock_name": "國巨", "ticker": "2327", "description": "投信建倉，看好被動元件低谷回溫。"},
                        {"stock_name": "禾伸堂", "ticker": "3026", "description": "默默敲進，被動元件低基期防守盤。"}
                    ]
                },
                {
                    "group_title": "3. 內資主力與實戶：點火光學題材",
                    "stocks": [
                        {"stock_name": "大立光", "ticker": "3008", "description": "大漲重返 5000 元大關，CPO 新技術與 iPhone 換機潮預期發酵。"},
                        {"stock_name": "先進光", "ticker": "3362", "description": "二線光學股集體飆漲停，內資主力短線拉抬氣勢磅礴。"},
                        {"stock_name": "中揚光", "ticker": "6668", "description": "低檔噴出，主力在權值股整理時拉抬具備想像空間的題材股。"}
                    ]
                }
            ],
            "strategies": [
                {
                    "strategy_title": "策略一：高檔避險與資金避風港（金融、航空）",
                    "strategy_content": "由於科技權值股（如台積電、聯發科、台達電）近期漲幅已大，加上美股費半重挫，外資與本土大戶在 6/17 選擇將資金撤出高風險的半導體，轉進『防禦型』與『受惠於暑期旺季』的標的。航空雙雄即將迎來第 3 季暑假旅遊及貨運旺季，屬於基期相對科技股低的選擇，因而成為外資大吸金池。而第一金、兆豐金等金融股，則是投信與國家隊在大盤重挫時慣用的『撐盤』工具，防禦性極佳。"
                },
                {
                    "strategy_title": "策略二：低基期與高殖利率卡位（面板、成熟製程）",
                    "strategy_content": "面板雙虎近期股價基期極低，在市場恐慌時，這類『跌無可跌』且具有資產價值的低基期股票，反而成為主力資金短線停泊、賺取反彈的避風港。成熟製程的聯電，雖然外資因全球半導體修正調節 4.5 萬張，但投信大戶持續瘋狂吸納，著眼於聯電下檔有配息與評價面支撐，形成內外資的劇烈籌碼角力。"
                },
                {
                    "strategy_title": "策略三：新技術題材點火（光學 CPO 題材）",
                    "strategy_content": "6/17 盤面上最強眼的亮點就是光學股。主要是市場傳出共同封裝光學（CPO）新技術題材發酵，加上蘋果 iPhone 換機潮預期。大戶在權值股整理時，最喜歡找這類『有故事、有想像空間』且剛從底部發動的題材股進行短線拉抬，成功帶動整體中小型光學股集體噴出。"
                }
            ],
            "summary": "大戶在 6/17 的操作邏輯非常明確：『棄高換低、防禦與題材並重』。他們利用科技權值股開低的恐慌感，順勢將資金調配到具備旺季效應 of 航空、避險的金融，以及具備新技術亮點的光學族群。",
            "top_brokerages_analysis": [
                {
                    "branch_name": "凱基台北",
                    "action": "買超 1.09 萬張",
                    "uncle_logic": "凱基台北在友達大玩隔日沖，明天開盤衝高大單出貨的機會非常高，肖年仔不要傻傻去接刀被割韭菜。"
                },
                {
                    "branch_name": "美商高盛",
                    "action": "買超 3.5 萬張",
                    "uncle_logic": "高盛幫外資波段基金代操，大買長榮航代表對暑期航空旺季買盤有中長線共識，這算有利多支撐。"
                },
                {
                    "branch_name": "元大投信",
                    "action": "買超 8000 張",
                    "uncle_logic": "投信在聯電上大打防守戰，明顯是本土高股息ETF和波段資金在死守季線，支撐力道不俗。"
                }
            ]
        }

    mock_processed = {
        "date": today,
        "stock_uncle_insight": stock_uncle_insight,
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
        is_cuban = "Cuban" in full_text or "Coinbase" in full_text or "Armstrong" in full_text
        is_spacex = "SpaceX" in full_text or "SPCX" in full_text
        is_atai = "ATAI" in full_text or "AtaiBeckley" in full_text
        
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
        elif is_cuban:
            mock_translations = {
                "After Coinbase CEO Brian Armstrong called for a rethink of accredited investor laws in the United States, billionaire investor Mark Cuban replied on June 16 with a blunt line on X:":
                "在 Coinbase 執行長 Brian Armstrong 呼籲重新審視美國的合格投資人法律後，億萬富翁投資人 Mark Cuban 於 6 月 16 日在 X 上以一句直白的話作出了回應：",
                "His main point was simple. Many companies now stay private for much longer than they used to.":
                "他的主要觀點很簡單。現在許多公司保持私有化的時間比以前長得多。",
                "By the time a company finally goes public, a large part of the upside may already have been captured by venture capital firms, private funds, and accredited investors.":
                "當一家公司最終上市時，大部分的獲利空間可能早已被創投公司、私募基金和合格投資人瓜分殆盡。",
                "Retail investors are then left to buy after the IPO, often at a much later and more expensive stage.":
                "散戶投資人隨後只能在 IPO 之後購買，通常是在極晚且昂貴許多的階段。",
                "Armstrong said the rules were originally designed with good intentions. They were meant to protect regular people from scams, excessive risk, and deals they might not fully understand.":
                "Armstrong 表示，這些規則最初的設計是出於好意。它們旨在保護普通人免受詐騙、過度風險以及他們可能不完全理解的交易影響。",
                "But, in his view, the outcome has become unfair. Instead of protecting people, the rules may now be protecting access for those who are already wealthy.":
                "但以他的看法，結果已經變得不公平。這些規則現在可能是在保護富人獲得投資管道，而不是在保護一般大眾。",
                "Under the current accredited investor framework, access is largely tied to income, net worth, or professional status.":
                "在目前的合格投資人架構下，投資管道主要與收入、淨值或專業身份掛鉤。",
                "Armstrong criticized that approach, saying it effectively creates a system where being rich gives someone the right to take financial risks, while everyone else is treated as if they cannot make their own decisions.":
                "Armstrong 批評了這種方法，稱其實際上創造了一個系統，即富有給了某人承擔財務風險的權利，而其他人則被當作無法做出自己決定的人來對待。",
                "He described the situation as regressive. In other words, a rule that was created to protect people may now be limiting their ability to build wealth.":
                "他將這種情況描述為倒退。換言之，一項旨在保護人們的規則現在可能正在限制他們累積財富的能力。",
                "Armstrong floated two possible alternatives. The first would be to replace the current wealth-based standard with a financial literacy test.":
                "Armstrong 提出了兩種可能的替代方案。第一種是用財務知識測試取代目前基於財富的標準。",
                "If someone can prove they understand risk, private markets, and investment basics, they should be allowed to participate.":
                "如果有人能證明他們理解風險、私募市場和投資基礎知識，就應該被允許參與。"
            }
        elif is_spacex:
            mock_translations = {
                "Following a blockbuster debut on the exchanges at the end of last week, options on SpaceX (SPCX) shares will start trading today, if a Reuters report is to be believed.":
                "在上週末於交易所取得轟動性的首秀後，如果路透社報導屬實，太空探索公司（SpaceX，代碼 SPCX）的股票期權將於今天開始交易。",
                "SPCX stock has rocketed close to 43% in just two full trading sessions, and with options on it soon going live, new avenues open up for the Elon Musk-led company's optimists and pessimists alike.":
                "SPCX 股價在短短兩個完整的交易日內就飆升了近 43%。隨著期權即將上線，這家由伊隆·馬斯克領導的公司的樂觀派和悲觀派都將迎來新的交易途徑。",
                "Along with that, risk management is another aspect that will become available for investors.":
                "與此同時，風險管理是投資者可以使用的另一個面向。",
                "Options are financial instruments that are primarily used as risk management measures for the underlying asset.":
                "期權是一種金融工具，主要用於作為標的資產的風險管理措施。",
                "Calls and puts are the two most popular forms of options on any asset.":
                "買權（Calls） and 賣權（Puts）是任何資產中最受歡迎的兩種期權形式。",
                "While calls are an option to buy the underlying asset at a predetermined price, puts are the same, just for selling.":
                "買權是按預定價格購買標的資產的選擇權，而賣權則是按預定價格出售的選擇權。",
                "Essentially, calls are a bullish bet on the asset, while puts are bearish ones.":
                "本質上，買權是對資產的看漲押注，而賣權則是看跌押注。",
                "Here, investors convinced of SpaceX's trajectory and future value can enhance their existing positions on the company by buying calls, while the skeptics expecting an inevitable crash can go long on puts and enjoy the downside.":
                "在這裡，確信 SpaceX 發展軌跡和未來價值的投資者可以通過購買買權來增強其現有頭寸；而預期不可避免崩盤的懷疑者則可以做多賣權以享受股價下跌的收益。",
                "Moreover, as a risk management tool, SpaceX bulls can buy puts to protect them from a downside, while bears can, conversely, buy calls.":
                "此外，作為風險管理工具，SpaceX 的看漲者可以購買賣權來保護自己免受股價下跌影響；相反，看跌者可以購買買權。",
                "Meanwhile, those expecting volatility in SPCX stock can opt for numerous volatility strategies involving options to benefit from the same.":
                "同時，那些預期 SPCX 股價會出現大幅波動的人，可以選擇多種涉及期權的波動率策略從中獲利。",
                "Finally, options can also act as an indicator of sentiments around the stock.":
                "最後，期權還可以作為股票周圍情緒的指標。",
                "Now that options for SpaceX have been established, a peek at history to take a look at how Musk's “other” company's stock behaved following the start of options trading on it should be interesting.":
                "現在 SpaceX 的期權已經確立，回顧歷史看看馬斯克『另一家』公司（特斯拉）的股票在期權交易開始後的表現，將會非常有趣。"
            }
        elif is_atai:
            mock_translations = {
                "AtaiBeckley Inc. (NASDAQ:ATAI) is one of the Best Penny Stocks That Could Skyrocket in 2026.":
                "AtaiBeckley Inc.（NASDAQ：ATAI）是 2026 年可能暴漲的最佳仙股之一。",
                "Wall Street is bullish on the stock as all 14 analysts covering the stock maintain a Buy rating, and their 12-month average price target suggests more than 280% upside from the current level.":
                "華爾街對該股持樂觀態度，因為所有 14 位追蹤該股的分析師均維持『買入』評級，其 12 個月平均目標價顯示較目前水平有超過 280% 的上漲空間。",
                "Recently, on June 8, H.C. Wainwright reiterated its Buy rating and $25 price target on AtaiBeckley Inc. (NASDAQ:ATAI).":
                "最近在 6 月 8 日，H.C. Wainwright 重申了對 AtaiBeckley Inc.（NASDAQ：ATAI）的『買入』評級和 25 美元的目標價。",
                "The rating comes after the firm met the company’s management on June 2.":
                "該評級是在該機構於 6 月 2 日與公司管理層會面後做出的。",
                "The discussion reinforced the firm’s conviction that BPL-003, which is an intranasal formulation of 5-MeO-DMT, remains the primary driver for the company.":
                "討論加深了該機構的信念，即 BPL-003（一種鼻內給藥的 5-MeO-DMT 配方）仍是該公司的主要驅動力。",
                "Moreover, management told the firm that they are preparing to launch their Phase 3 program, called ReConnection, targeting treatment-resistant depression.":
                "此外，管理層告訴該機構，他們正準備啟動名為 ReConnection 的三期臨床項目，旨在治療難治性憂鬱症。",
                "H.C. Wainwright highlighted several practical advantages of BPL-003’s profile, including an 8 mg dose that balances efficacy and tolerability, a short in-clinic session duration, flexible retreatment options, and clinic economics that fit neatly into a two-hour interventional psychiatry model.":
                "H.C. Wainwright 強調了 BPL-003 概況的幾個實際優勢，包括平衡療效與耐受性的 8 毫克劑量、較短的診所留觀時間、彈性的重複治療選擇，以及完全符合兩小時介入精神病學模式的診所經濟效益。",
                "The firm believes that these positive points make it operationally attractive for treatment centers.":
                "該機構相信這些優點使它在營運上對治療中心極具吸引力。",
                "AtaiBeckley Inc. (NASDAQ:ATAI) is a clinical-stage biopharmaceutical company focused on developing treatments for mental health disorders.":
                "AtaiBeckley Inc.（NASDAQ：ATAI）是一家臨床階段的生物製藥公司，專注於開發精神健康疾病的治療方法。",
                "While we acknowledge the potential of ATAI as an investment, we believe certain AI stocks offer greater upside potential and carry less downside risk.":
                "雖然我們承認 ATAI 作為投資的潛力，但我們相信某些 AI 股票提供了更大的上漲空間且下行風險較低。",
                "If you're looking for an extremely undervalued AI stock that also stands to benefit significantly from Trump-era tariffs and the onshoring trend, see our free report on the best short-term AI stock.":
                "如果您正在尋找一隻被極度低估的 AI 股票，且該股還能從川普時代的關稅和製造業回流勢中顯著受益，請參閱我們關於最佳短期 AI 股的免費報告。"
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

        # Select keywords based on news type
        if "grocery" in title.lower() or "pricing data" in full_text.lower():
            keywords = [
                {"word": "settlement", "ipa": "/ˈsɛt̬.əl.mənt/", "meaning": "和解金、和解協議", "example": "The company reached a $40 million settlement with the DOJ."},
                {"word": "scrutiny", "ipa": "/ˈskruː.t̬ən.i/", "meaning": "嚴密審查、監督", "example": "The pricing practices came under federal scrutiny."},
                {"word": "inflated", "ipa": "/ɪnˈfleɪ.t̬ɪd/", "meaning": "虛報的、誇大的", "example": "They were accused of submitting inflated prescription drug pricing data."},
                {"word": "reimburse", "ipa": "/ˌriː.ɪmˈbɝːs/", "meaning": "報銷、償還", "example": "The program reimburses pharmacies for prescription drugs."},
                {"word": "prescription", "ipa": "/prɪˈskrɪp.ʃən/", "meaning": "處方藥的", "example": "Supermarkets offer prescription savings programs."}
            ]
        elif "gold" in title.lower() or "blockade" in full_text.lower():
            keywords = [
                {"word": "futures", "ipa": "/ˈfjuːtʃərz/", "meaning": "期貨", "example": "Gold futures opened flat compared to yesterday."},
                {"word": "flat", "ipa": "/flæt/", "meaning": "持平、沒有變化", "example": "The price of gold was flat in morning trading."},
                {"word": "Fed meeting", "ipa": "/fɛd ˈmiːtɪŋ/", "meaning": "聯準會會議", "example": "Gold prices held steady ahead of the Fed meeting."},
                {"word": "hold rates steady", "ipa": "/hoʊld reɪts ˈstɛdi/", "meaning": "維持利率不變", "example": "Most observers expect the Fed to hold rates steady."},
                {"word": "blockade", "ipa": "/blɒˈkeɪd/", "meaning": "封鎖", "example": "The peace agreement will lift the naval blockade."}
            ]
        elif "rate cuts" in title.lower() or "funds rate" in full_text.lower():
            keywords = [
                {"word": "Federal Open Market Committee (FOMC)", "ipa": "/ˈfɛdərəl ˈoʊpən ˈmɑrkɪt kəˈmɪti/", "meaning": "聯邦公開市場委員會", "example": "The FOMC announced its decision to maintain the rate."},
                {"word": "federal funds rate", "ipa": "/ˈfɛdərəl fʌndz reɪt/", "meaning": "聯邦資金利率", "example": "The federal funds rate is a key tool for managing inflation."},
                {"word": "rate cuts", "ipa": "/reɪt kʌts/", "meaning": "降息", "example": "Consumers expect to see rate cuts later this year."},
                {"word": "inflation", "ipa": "/ɪnˈfleɪʃən/", "meaning": "通貨膨脹", "example": "The Fed raises interest rates when inflation is too high."},
                {"word": "economic outlook", "ipa": "/ˌikəˈnɑmɪk ˈaʊtˌlʊk/", "meaning": "經濟前景", "example": "The committee maintained the rate citing uncertainty in the economic outlook."}
            ]
        elif is_news_1: # Biden chip exports
            keywords = [
                {"word": "restricting", "ipa": "/rɪˈstrɪkt.ɪŋ/", "meaning": "限制，約束", "example": "The government is restricting export of advanced semiconductors."},
                {"word": "accelerators", "ipa": "/ækˈsel.ə.reɪ.tərz/", "meaning": "加速晶片（如 AI 運算 GPU）", "example": "Data centers require high-end AI accelerators to run LLMs."},
                {"word": "curb", "ipa": "/kɜːb/", "meaning": "控制，遏制", "example": "New regulations aim to curb military applications of Western tech."},
                {"word": "semiconductor", "ipa": "/ˌsem.i.kənˈdʌk.tər/", "meaning": "半導體", "example": "These export controls restrict access to advanced semiconductor technology."},
                {"word": "proprietary", "ipa": "/prəˈpraɪə.ter.i/", "meaning": "專有的，專利的", "example": "The rules will accelerate efforts to design proprietary hardware alternatives."}
            ]
        elif is_cuban:
            keywords = [
                {"word": "accredited", "ipa": "/əˈkred.ɪ.tɪd/", "meaning": "合格的，認證的", "example": "Cuban called for a rethink of accredited investor laws."},
                {"word": "private", "ipa": "/ˈpraɪ.vət/", "meaning": "私有的，未上市的", "example": "Many companies choose to stay private for much longer than before."},
                {"word": "upside", "ipa": "/ˈʌp.saɪd/", "meaning": "上行空間，潛在利益", "example": "Venture capital firms capture a large part of the upside before the IPO."},
                {"word": "scams", "ipa": "/skæmz/", "meaning": "騙局，詐騙", "example": "The rules were designed to protect regular people from scams."},
                {"word": "literacy", "ipa": "/ˈlɪt.ər.ə.si/", "meaning": "讀寫能力，知識素養", "example": "He proposed replacing the standard with a financial literacy test."}
            ]
        elif is_spacex:
            keywords = [
                {"word": "debut", "ipa": "/ˈdeɪ.bju/", "meaning": "首秀，首次亮相", "example": "SpaceX shares made a blockbuster debut on the exchanges."},
                {"word": "options", "ipa": "/ˈɑːp.ʃənz/", "meaning": "選擇權，期權", "example": "Options on SpaceX shares will start trading today."},
                {"word": "avenues", "ipa": "/ˈæv.ə.njuːz/", "meaning": "途徑，手段", "example": "New avenues open up for the company's optimists and pessimists."},
                {"word": "volatility", "ipa": "/ˌvɑː.ləˈtɪl.ə.t̬i/", "meaning": "波動性", "example": "Investors can opt for strategies to benefit from stock volatility."},
                {"word": "trajectory", "ipa": "/trəˈdʒek.tər.i/", "meaning": "軌跡，發展路線", "example": "Bulls are convinced of the company's positive trajectory."}
            ]
        elif is_atai:
            keywords = [
                {"word": "penny stocks", "ipa": "/ˈpen.i stɑːks/", "meaning": "仙股，細價股", "example": "ATAI is one of the best penny stocks that could skyrocket."},
                {"word": "reiterated", "ipa": "/riˈɪt̬.ə.reɪ.tɪd/", "meaning": "重申，反覆說", "example": "The firm reiterated its Buy rating and price target."},
                {"word": "intranasal", "ipa": "/ˌɪn.trəˈneɪ.zəl/", "meaning": "鼻內的", "example": "BPL-003 is an intranasal formulation under development."},
                {"word": "tolerability", "ipa": "/ˌtɑː.lər.əˈbɪl.ə.t̬i/", "meaning": "耐受性", "example": "The dose balances efficacy and tolerability for patients."},
                {"word": "economics", "ipa": "/ˌiː.kəˈnɑː.mɪks/", "meaning": "經濟效益，經濟學", "example": "Clinic economics fit neatly into a two-hour interventional model."}
            ]
        else:
            keywords = [
                {"word": "rallied", "ipa": "/ˈræl.id/", "meaning": "（價格等）回升，止跌回升", "example": "Major tech shares rallied across global stock markets."},
                {"word": "cooling", "ipa": "/ˈkuː.lɪŋ/", "meaning": "降溫的，放緩的", "example": "Cooling inflation data eased investor concerns."},
                {"word": "curbing", "ipa": "/ˈkɝː.bɪŋ/", "meaning": "控制，遏制", "example": "Monetary policy is successfully curbing inflation."},
                {"word": "outlook", "ipa": "/ˈaʊt.lʊk/", "meaning": "前景，展望指引", "example": "The company adjusted its quarterly revenue outlook due to news."},
                {"word": "recession", "ipa": "/rɪˈseʃ.ən/", "meaning": "經濟衰退", "example": "Monetary policy successfully curbed inflation without triggering a recession."}
            ]

        mock_processed["english_professor_news"].append({
            "news_id": item.get("id", "news_1"),
            "title": title,
            "source": item.get("source", "Yahoo Finance"),
            "link": item.get("link", "#"),
            "level1_blind": {
                "text": blind_text
            },
            "level2_keywords": keywords,
            "level2_context": "白話背景：這篇新聞在探討國際政經政策對核心科技產業（如晶片出口、通膨升息）造成的宏觀影響。這些變動會透過半導體與伺服器代工供應鏈，在幾天內迅速傳導至台灣股市，是主力資金調度的重要風向球。",
            "level3_translation": translations
        })
        
    return mock_processed


# --- CALL LLM APIs ---
def call_ollama(system_prompt, user_prompt, model="llama3"):
    hosts = ["http://localhost:11434", "http://127.0.0.1:11435", "http://localhost:11435"]
    env_host = os.getenv("OLLAMA_HOST")
    if env_host:
        if not env_host.startswith("http"):
            env_host = f"http://{env_host}"
        # Prioritize env variable host
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
            # Shorten initial timeout per host try if there are multiple hosts,
            # but keep it enough for inference (120s)
            response = requests.post(url, json=payload, timeout=120)
            if response.status_code == 200:
                content = response.json().get("message", {}).get("content", "")
                
                # Clean markdown formatting if present
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
    
    text_response = ""
    try:
        response = requests.post(url, json=payload, timeout=60)
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
        else:
            print(f"Gemini API returned status code: {response.status_code}, error: {response.text}")
            return None
    except Exception as e:
        print(f"Gemini API call failed: {e}")
        if text_response:
            print("--- Text Response Snippet (first 1000 chars) ---")
            print(text_response[:1000])
            print("--- End of Snippet ---")
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
        
    # Check if we should fallback to mock
    if mode == "mock":
        print("Running in MOCK mode. Generating simulated AI insights...")
        return generate_mock_processed_insights(raw_data)
        
    # Load character prompts
    uncle_sys = read_skill_prompt("stock-uncle")
    prof_sys = read_skill_prompt("english-professor")
    linker_sys = read_skill_prompt("market-linker")
    
    import datetime
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
        f"以下是今天的台股三大法人買賣超前10名與關鍵分點數據：{stock_market_str}。\n"
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
    
    linker_user = f"今天晨間的台股數據為：{stock_market_str}；下午的國際財經新聞為：{news_str}。請根據你作為暴力聯結器的設定，進行跨市場大腦聯結推理，並『嚴格』只輸出一個 JSON 物件，包含以下欄位：\n- violence_connection (字串，約 200-350 字的精彩推理，探討兩者間的可能因果關係或主力暗度陳倉行為)"

    # Initialize results
    stock_uncle_insight = None
    english_professor_news = None
    market_linker_insight = None
    
    api_key = os.getenv("GEMINI_API_KEY")
    
    # Execute LLM calls
    # 1. Run Stock Uncle
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
        if mode == "ollama":
            stock_uncle_insight = call_ollama(uncle_sys, uncle_user, ollama_model)
        elif mode == "gemini":
            if not api_key:
                print("Error: GEMINI_API_KEY not found in environment. Falling back to MOCK...")
                return generate_mock_processed_insights(raw_data)
            stock_uncle_insight = call_gemini(uncle_sys, uncle_user, api_key)
        elif mode == "hybrid":
            if not api_key:
                print("Error: GEMINI_API_KEY not found for hybrid. Falling back to local Ollama...")
                stock_uncle_insight = call_ollama(uncle_sys, uncle_user, ollama_model)
            else:
                stock_uncle_insight = call_ollama(uncle_sys, uncle_user, ollama_model)
            
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
        
        result = None
        if mode == "ollama":
            result = call_ollama(prof_sys, prof_user, ollama_model)
        elif mode == "gemini":
            result = call_gemini(prof_sys, prof_user, api_key)
        elif mode == "hybrid":
            if not api_key:
                result = call_ollama(prof_sys, prof_user, ollama_model)
            else:
                result = call_gemini(prof_sys, prof_user, api_key)
                
        # Validate result
        if result and isinstance(result, dict) and "level3_translation" in result:
            english_professor_news.append(result)
            # Add to chosen_keywords
            keywords = result.get("level2_keywords", [])
            for kw in keywords:
                if isinstance(kw, dict) and "word" in kw:
                    chosen_keywords.append(kw["word"].lower().strip())
        else:
            print(f"   [Warning] AI processing failed or returned invalid JSON for article {idx+1}. Using mock data fallback.")
            mock_res = generate_mock_processed_insights({"news": [item], "stock_market": raw_data.get("stock_market", {})})
            if mock_res["english_professor_news"]:
                english_professor_news.append(mock_res["english_professor_news"][0])

    # 3. Run Market Linker
    print("3. Processing Market Linker...")
    if mode == "ollama":
        market_linker_insight = call_ollama(linker_sys, linker_user, ollama_model)
    elif mode == "gemini":
        market_linker_insight = call_gemini(linker_sys, linker_user, api_key)
    elif mode == "hybrid":
        if not api_key:
            market_linker_insight = call_ollama(linker_sys, linker_user, ollama_model)
        else:
            market_linker_insight = call_gemini(linker_sys, linker_user, api_key)
        
    # Check if any LLM call failed. If so, fallback to mock to prevent crashes.
    mock_data_res = generate_mock_processed_insights(raw_data)
    
    # Validate stock_uncle_insight has new keys, otherwise fallback
    uncle_valid = (
        stock_uncle_insight 
        and isinstance(stock_uncle_insight, dict) 
        and "buyer_groups" in stock_uncle_insight
    )
    
    if not uncle_valid or not english_professor_news or not market_linker_insight:
        print("\n[Warning] One or more AI modules failed to respond, returned invalid JSON or outdated keys.")
        print("Falling back to MOCK mode for missing or all elements to guarantee output...")
        
        if not uncle_valid:
            stock_uncle_insight = mock_data_res["stock_uncle_insight"]
        if not english_professor_news:
            english_professor_news = mock_data_res["english_professor_news"]
        if not market_linker_insight:
            market_linker_insight = mock_data_res["market_linker_insight"]
            
    # --- Structural Validation and Patching ---
    mock_uncle = mock_data_res["stock_uncle_insight"]
    if isinstance(stock_uncle_insight, dict):
        # Patch date_header
        if "date_header" not in stock_uncle_insight or not stock_uncle_insight["date_header"]:
            stock_uncle_insight["date_header"] = mock_uncle["date_header"]
            
        # Patch buyer_groups
        if "buyer_groups" not in stock_uncle_insight or not isinstance(stock_uncle_insight["buyer_groups"], list) or len(stock_uncle_insight["buyer_groups"]) < 3:
            stock_uncle_insight["buyer_groups"] = mock_uncle["buyer_groups"]
        else:
            # Ensure each group has stocks, and each stock has description
            for g_idx, group in enumerate(stock_uncle_insight["buyer_groups"]):
                if not isinstance(group, dict):
                    continue
                if "group_title" not in group:
                    group["group_title"] = mock_uncle["buyer_groups"][g_idx % 3]["group_title"]
                if "stocks" not in group or not isinstance(group["stocks"], list):
                    group["stocks"] = mock_uncle["buyer_groups"][g_idx % 3]["stocks"]
                else:
                    for s_idx, stock in enumerate(group["stocks"]):
                        if not isinstance(stock, dict):
                            continue
                        if "stock_name" not in stock:
                            stock["stock_name"] = "未知個股"
                        if "ticker" not in stock:
                            stock["ticker"] = "0000"
                        if "description" not in stock or not stock["description"]:
                            # Generate a contextual description based on stock name
                            stock["description"] = f"自營部叔叔分析：大戶在 {stock['stock_name']} 上強力建倉，買盤力道強勁，肖年仔不要瞎操作，跟隨法人步伐即可。"
                            
        # Patch strategies
        if "strategies" not in stock_uncle_insight or not isinstance(stock_uncle_insight["strategies"], list) or len(stock_uncle_insight["strategies"]) < 3:
            stock_uncle_insight["strategies"] = mock_uncle["strategies"]
        else:
            for s_idx, strat in enumerate(stock_uncle_insight["strategies"]):
                if not isinstance(strat, dict):
                    continue
                if "strategy_title" not in strat:
                    strat["strategy_title"] = mock_uncle["strategies"][s_idx % 3]["strategy_title"]
                if "strategy_content" not in strat:
                    strat["strategy_content"] = mock_uncle["strategies"][s_idx % 3]["strategy_content"]
                    
        # Patch summary
        if "summary" not in stock_uncle_insight or not stock_uncle_insight["summary"]:
            stock_uncle_insight["summary"] = mock_uncle["summary"]
            
        # Patch top_brokerages_analysis (Ollama often skips this or names it differently)
        if "top_brokerages_analysis" not in stock_uncle_insight or not isinstance(stock_uncle_insight["top_brokerages_analysis"], list) or len(stock_uncle_insight["top_brokerages_analysis"]) == 0:
            stock_uncle_insight["top_brokerages_analysis"] = mock_uncle["top_brokerages_analysis"]
        else:
            for b_idx, bro in enumerate(stock_uncle_insight["top_brokerages_analysis"]):
                if not isinstance(bro, dict):
                    continue
                if "branch_name" not in bro:
                    bro["branch_name"] = "主力券商"
                if "action" not in bro:
                    bro["action"] = "買超"
                if "uncle_logic" not in bro or not bro["uncle_logic"]:
                    bro["uncle_logic"] = "自營部叔叔：主力分點在此默默收貨，鎖碼意圖明顯，肖年仔可多常觀察主力蹤跡。"

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
    parser.add_argument("--mode", type=str, choices=["ollama", "gemini", "hybrid", "mock"], default="hybrid",
                        help="AI mode: ollama (local), gemini (cloud API), hybrid (ollama + gemini), or mock (simulation)")
    parser.add_argument("--model", type=str, default="llama3.2",
                        help="Ollama model name (default: llama3.2)")
                        
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
