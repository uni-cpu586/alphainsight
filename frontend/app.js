// AlphaInsight Frontend App Logic
// Uses dynamic DOM rendering, Web Speech API, and LocalStorage

document.addEventListener("DOMContentLoaded", () => {
    let insightData = null;
    let currentNewsIndex = 0;
    let speechUtterance = null;
    let saveTimeout = null;
    let hideStatusTimeout = null;
    let isSpeaking = false;
    let currentSpeechIndex = 0;
    let currentSentences = [];
    let cachedVoices = [];

    // DOM Elements
    const dateEl = document.getElementById("insight-date");

    // Pre-cache voices
    function loadVoices() {
        if (typeof window !== "undefined" && window.speechSynthesis) {
            cachedVoices = window.speechSynthesis.getVoices();
        }
    }
    loadVoices();
    if (typeof window !== "undefined" && window.speechSynthesis) {
        window.speechSynthesis.onvoiceschanged = () => {
            loadVoices();
        };
    }

    // Stock Uncle Elements
    const uncleReportHeaderEl = document.getElementById("uncle-report-header");
    const buyerGroupsContainerEl = document.getElementById("buyer-groups-container");
    const strategiesContainerEl = document.getElementById("strategies-container");
    const uncleSummaryTextEl = document.getElementById("uncle-summary-text");
    const brokeragesListEl = document.getElementById("brokerages-list");
    
    // Linker Elements
    const linkerInsightEl = document.getElementById("linker-insight-text");
    
    // English Section Elements
    const newsSelectorEl = document.getElementById("news-selector");
    const btnL1 = document.getElementById("btn-level1");
    const btnL2 = document.getElementById("btn-level2");
    const btnL3 = document.getElementById("btn-level3");
    const panelL1 = document.getElementById("panel-level1");
    const panelL2 = document.getElementById("panel-level2");
    const panelL3 = document.getElementById("panel-level3");
    
    // Level 1 Elements
    const blindPassageEl = document.getElementById("blind-passage");
    const ttsPlayBtn = document.getElementById("tts-play-btn");
    const ttsStopBtn = document.getElementById("tts-stop-btn");
    const peekBtn = document.getElementById("peek-btn");
    
    // Level 2 Elements
    const profContextEl = document.getElementById("prof-context");
    const keywordsContainerEl = document.getElementById("keywords-container");
    
    // Level 3 Elements
    const interactivePassageEl = document.getElementById("interactive-passage");
    const translationContentEl = document.getElementById("translation-content");
    
    // Sandbox Elements
    const sandboxTextarea = document.getElementById("sandbox-textarea");
    const saveStatusEl = document.getElementById("save-status");

    // Initialize App: Load JSON Data
    fetch("data/processed_insights.json")
        .then(response => {
            if (!response.ok) {
                throw new Error("processed_insights.json not found");
            }
            return response.json();
        })
        .then(data => {
            insightData = data;
            renderDashboard();
        })
        .catch(err => {
            console.error("Error loading insights:", err);
            // Show errors gracefully
            if (uncleReportHeaderEl) {
                uncleReportHeaderEl.textContent = "無法載入最新資料，請確保已經跑過 Python 腳本產生 JSON 檔案。";
            }
            if (linkerInsightEl) {
                linkerInsightEl.textContent = "讀取失敗，資料庫未就緒。";
            }
            if (blindPassageEl) {
                blindPassageEl.textContent = "資料載入失敗。";
            }
            
            // Clear loading spinners and show errors
            if (buyerGroupsContainerEl) {
                buyerGroupsContainerEl.innerHTML = "<div class='loading-spinner'>資料載入失敗</div>";
            }
            if (strategiesContainerEl) {
                strategiesContainerEl.innerHTML = "<div class='loading-spinner'>資料載入失敗</div>";
            }
            if (brokeragesListEl) {
                brokeragesListEl.innerHTML = "<div class='loading-spinner'>資料載入失敗</div>";
            }
            if (newsSelectorEl) {
                newsSelectorEl.innerHTML = "<div class='loading-spinner'>資料載入失敗</div>";
            }
        });

    // Main Render Function
    function renderDashboard() {
        // Render Meta
        dateEl.textContent = insightData.date || new Date().toLocaleDateString('zh-TW');

        // 1. Render Stock Uncle
        const uncleData = insightData.stock_uncle_insight;
        if (uncleData) {
            // Render report header (or date_header)
            if (uncleReportHeaderEl) {
                uncleReportHeaderEl.textContent = uncleData.date_header || "法人與主力大戶主要買超股票";
            }

            // Render buyer groups
            if (buyerGroupsContainerEl) {
                buyerGroupsContainerEl.innerHTML = "";
                if (uncleData.buyer_groups && uncleData.buyer_groups.length > 0) {
                    uncleData.buyer_groups.forEach(group => {
                        const groupCard = document.createElement("div");
                        groupCard.className = "buyer-group-card";
                        
                        let stocksHtml = "";
                        if (group.stocks && group.stocks.length > 0) {
                            group.stocks.forEach(stock => {
                                stocksHtml += `
                                    <div class="buyer-stock-item">
                                        <span class="buyer-stock-name">${stock.stock_name} (${stock.ticker})</span>
                                        <span class="buyer-stock-desc">${stock.description}</span>
                                    </div>
                                `;
                            });
                        } else {
                            stocksHtml = "<div class='buyer-stock-item'>無特定個股分析</div>";
                        }

                        groupCard.innerHTML = `
                            <h4 class="buyer-group-title">${group.group_title}</h4>
                            <div class="buyer-stocks-list">
                                ${stocksHtml}
                            </div>
                        `;
                        buyerGroupsContainerEl.appendChild(groupCard);
                    });
                } else {
                    buyerGroupsContainerEl.innerHTML = "<div class='loading-spinner'>今日無分組數據</div>";
                }
            }

            // Render strategies
            if (strategiesContainerEl) {
                strategiesContainerEl.innerHTML = "";
                if (uncleData.strategies && uncleData.strategies.length > 0) {
                    uncleData.strategies.forEach(strategy => {
                        const strategyCard = document.createElement("div");
                        strategyCard.className = "strategy-card";
                        strategyCard.innerHTML = `
                            <h4 class="strategy-title">${strategy.strategy_title}</h4>
                            <p class="strategy-content">${strategy.strategy_content}</p>
                        `;
                        strategiesContainerEl.appendChild(strategyCard);
                    });
                } else {
                    strategiesContainerEl.innerHTML = "<div class='loading-spinner'>今日無操盤策略推導</div>";
                }
            }

            // Render summary
            if (uncleSummaryTextEl) {
                uncleSummaryTextEl.textContent = uncleData.summary || "棄高換低、防禦與題材並重。";
            }
            
            // Render brokerages list (retained as supplement)
            if (brokeragesListEl) {
                brokeragesListEl.innerHTML = "";
                if (uncleData.top_brokerages_analysis && uncleData.top_brokerages_analysis.length > 0) {
                    uncleData.top_brokerages_analysis.forEach(item => {
                        const isSell = item.action.includes("賣") || item.action.includes("sell") || item.action.includes("出貨");
                        const actionClass = isSell ? "action-sell" : "action-buy";
                        
                        const card = document.createElement("div");
                        card.className = "brokerage-card";
                        card.innerHTML = `
                            <div class="brokerage-card-meta">
                                <span class="brokerage-name">${item.branch_name}</span>
                                <span class="brokerage-action ${actionClass}">${item.action}</span>
                            </div>
                            <p class="uncle-logic-text">${item.uncle_logic}</p>
                        `;
                        brokeragesListEl.appendChild(card);
                    });
                } else {
                    brokeragesListEl.innerHTML = `<div class="loading-spinner">今日無特殊分點進出分析</div>`;
                }
            }
        }

        // 2. Render Market Linker
        const linkerData = insightData.market_linker_insight;
        if (linkerData) {
            linkerInsightEl.textContent = linkerData.violence_connection;
        }

        // 3. Render English Professor News
        const newsList = insightData.english_professor_news;
        if (newsList && newsList.length > 0) {
            // Render News Selector Tabs
            newsSelectorEl.innerHTML = "";
            newsList.forEach((news, idx) => {
                const tab = document.createElement("button");
                tab.className = `news-tab ${idx === 0 ? 'active' : ''}`;
                tab.textContent = news.title.length > 30 ? news.title.substring(0, 27) + "..." : news.title;
                tab.title = news.title;
                tab.addEventListener("click", () => {
                    // Stop any speaking speech
                    stopSpeech();
                    
                    // Switch tab
                    document.querySelectorAll(".news-tab").forEach(t => t.classList.remove("active"));
                    tab.classList.add("active");
                    currentNewsIndex = idx;
                    renderNewsItem(idx);
                });
                newsSelectorEl.appendChild(tab);
            });

            // Render first news item
            renderNewsItem(0);
        } else {
            newsSelectorEl.innerHTML = "<div class='loading-spinner'>今日無英語新聞修煉資料</div>";
        }
    }

    // Render specific news item details
    function renderNewsItem(idx) {
        const news = insightData.english_professor_news[idx];
        if (!news) return;

        // Reset peek states
        blindPassageEl.classList.add("blur-effect");
        peekBtn.innerHTML = '<i class="fa-regular fa-eye"></i> 暫時解鎖文字 (馬賽克)';

        // Level 1: Blind text
        blindPassageEl.textContent = news.level1_blind.text;

        // Level 2: Context & Keywords
        profContextEl.textContent = news.level2_context;
        keywordsContainerEl.innerHTML = "";
        if (news.level2_keywords && news.level2_keywords.length > 0) {
            news.level2_keywords.forEach(kw => {
                const cardWrapper = document.createElement("div");
                cardWrapper.className = "keyword-card-wrapper";
                cardWrapper.innerHTML = `
                    <div class="keyword-card-inner">
                        <div class="keyword-card-front">
                            <h5>${kw.word}</h5>
                            <span>${kw.ipa}</span>
                        </div>
                        <div class="keyword-card-back">
                            <p>${kw.meaning}</p>
                            <span>${kw.example}</span>
                        </div>
                    </div>
                `;
                cardWrapper.addEventListener("click", () => {
                    cardWrapper.classList.toggle("flipped");
                });
                keywordsContainerEl.appendChild(cardWrapper);
            });
        }

        // Level 3: Full translation interactive sentences
        interactivePassageEl.innerHTML = "";
        translationContentEl.innerHTML = "<em>點擊上面的英文句子獲得教授的中文白話產業解讀。</em>";
        
        if (news.level3_translation && news.level3_translation.length > 0) {
            news.level3_translation.forEach((transItem, sIdx) => {
                const sentenceSpan = document.createElement("span");
                sentenceSpan.className = "interactive-sentence";
                sentenceSpan.textContent = transItem.sentence + " ";
                sentenceSpan.setAttribute("data-translation", transItem.translation);
                
                sentenceSpan.addEventListener("click", () => {
                    // Highlight selected sentence
                    document.querySelectorAll(".interactive-sentence").forEach(s => s.classList.remove("selected"));
                    sentenceSpan.classList.add("selected");
                    
                    // Display translation
                    translationContentEl.innerHTML = `
                        <strong>英文句：</strong><br>${transItem.sentence}<br><br>
                        <strong>教授翻譯與背景：</strong><br><span style="color:var(--neon-blue);">${transItem.translation}</span>
                    `;
                });
                
                interactivePassageEl.appendChild(sentenceSpan);
            });
        }
    }

    // Level Switcher Tabs Logic
    const levelBtns = [btnL1, btnL2, btnL3];
    const panels = [panelL1, panelL2, panelL3];

    levelBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            const level = btn.getAttribute("data-level");
            
            // Toggle active button
            levelBtns.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            
            // Toggle active panel
            panels.forEach(p => p.classList.remove("active"));
            document.getElementById(`panel-level${level}`).classList.add("active");
            
            // If switching away from L1, stop speech
            if (level !== "1") {
                stopSpeech();
            }
        });
    });

    // Level 1: Peek button toggler
    peekBtn.addEventListener("click", () => {
        if (blindPassageEl.classList.contains("blur-effect")) {
            blindPassageEl.classList.remove("blur-effect");
            peekBtn.innerHTML = '<i class="fa-regular fa-eye-slash"></i> 重新蓋上馬賽克';
        } else {
            blindPassageEl.classList.add("blur-effect");
            peekBtn.innerHTML = '<i class="fa-regular fa-eye"></i> 暫時解鎖文字 (馬賽克)';
        }
    });

    // Text-to-Speech Speech Synthesis Logic
    function speakSentence() {
        if (!isSpeaking) return;
        
        if (currentSpeechIndex >= currentSentences.length) {
            stopSpeech();
            return;
        }

        const textToSpeak = currentSentences[currentSpeechIndex];
        speechUtterance = new SpeechSynthesisUtterance(textToSpeak);
        speechUtterance.lang = "en-US";
        speechUtterance.rate = 0.9; // Slightly slower for better learning

        // Find the Microsoft Edge Natural "Andrew" voice
        const andrewVoice = cachedVoices.find(v => 
            v.name.includes("en-US-AndrewNeural")
        ) || cachedVoices.find(v => 
            v.name.toLowerCase().includes("andrew") && 
            (v.name.toLowerCase().includes("natural") || v.name.toLowerCase().includes("online"))
        ) || cachedVoices.find(v => 
            v.name.toLowerCase().includes("andrew")
        ) || cachedVoices.find(v => 
            v.name.toLowerCase().includes("natural") && v.lang.startsWith("en")
        ) || cachedVoices.find(v => 
            v.lang.startsWith("en")
        );

        if (andrewVoice) {
            speechUtterance.voice = andrewVoice;
        }

        speechUtterance.onend = () => {
            if (isSpeaking) {
                currentSpeechIndex++;
                speakSentence();
            }
        };

        speechUtterance.onerror = (e) => {
            console.error("SpeechSynthesis error:", e);
            if (isSpeaking) {
                currentSpeechIndex++;
                setTimeout(speakSentence, 100);
            } else {
                stopSpeech();
            }
        };

        window.speechSynthesis.speak(speechUtterance);
    }

    ttsPlayBtn.addEventListener("click", () => {
        if (!insightData) return;
        const news = insightData.english_professor_news[currentNewsIndex];
        if (!news) return;

        // Stop any current speech first
        stopSpeech();

        isSpeaking = true;
        currentSpeechIndex = 0;
        currentSentences = news.level1_blind.text
            .split(/(?<=\.|\?|\!)\s+/)
            .map(s => s.trim())
            .filter(s => s.length > 0);

        if (currentSentences.length === 0) return;

        ttsPlayBtn.style.display = "none";
        ttsStopBtn.style.display = "inline-flex";

        speakSentence();
    });

    ttsStopBtn.addEventListener("click", () => {
        stopSpeech();
    });

    function stopSpeech() {
        isSpeaking = false;
        if (typeof window !== "undefined" && window.speechSynthesis) {
            window.speechSynthesis.cancel();
        }
        resetSpeechUI();
    }

    function resetSpeechUI() {
        ttsPlayBtn.style.display = "inline-flex";
        ttsStopBtn.style.display = "none";
    }

    // Sandbox Note LocalStorage auto-save
    // Load saved note
    const savedNote = localStorage.getItem("alphainsight_sandbox_note");
    if (savedNote) {
        sandboxTextarea.value = savedNote;
    }

    sandboxTextarea.addEventListener("input", () => {
        // Debounce saving to localStorage to prevent massive writes
        clearTimeout(saveTimeout);
        clearTimeout(hideStatusTimeout);
        
        saveStatusEl.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> 正在儲存...';
        saveStatusEl.classList.add("show");

        saveTimeout = setTimeout(() => {
            localStorage.setItem("alphainsight_sandbox_note", sandboxTextarea.value);
            saveStatusEl.innerHTML = '<i class="fa-solid fa-cloud-arrow-up"></i> 已即時儲存至本機';
            
            // Hide indicator after a brief moment
            hideStatusTimeout = setTimeout(() => {
                saveStatusEl.classList.remove("show");
            }, 1500);
        }, 800);
    });

    // View Tab Selection Logic
    const viewBtns = document.querySelectorAll(".view-tab-btn");
    const appMainEl = document.querySelector(".app-main");

    if (viewBtns && appMainEl) {
        // Load default/saved view from localStorage or default to "all"
        const savedView = localStorage.getItem("alphainsight_preferred_view") || "all";
        
        // Function to apply a view
        const applyView = (view) => {
            // Stop speech when view changes
            stopSpeech();

            // Remove all view classes from appMainEl
            appMainEl.classList.remove("view-morning", "view-english", "view-night", "view-sandbox");
            
            // Add selected view class if not 'all'
            if (view !== "all") {
                appMainEl.classList.add(`view-${view}`);
            }
            
            // Update active states on buttons
            viewBtns.forEach(btn => {
                if (btn.getAttribute("data-view") === view) {
                    btn.classList.add("active");
                } else {
                    btn.classList.remove("active");
                }
            });
            
            // Save selection
            localStorage.setItem("alphainsight_preferred_view", view);
        };

        // Initialize view
        applyView(savedView);

        // Add event listeners
        viewBtns.forEach(btn => {
            btn.addEventListener("click", () => {
                const view = btn.getAttribute("data-view");
                applyView(view);
            });
        });
    }
});
