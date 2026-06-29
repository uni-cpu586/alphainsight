// AlphaInsight Frontend App Logic
// Uses dynamic DOM rendering, Web Speech API, and LocalStorage

document.addEventListener("DOMContentLoaded", () => {
    let insightData = null;
    let currentNewsIndex = 0;
    let audioPlayer = null;
    let saveTimeout = null;
    let hideStatusTimeout = null;
    let isSpeaking = false;

    // Stock Uncle Elements
    const uncleReportHeaderEl = document.getElementById("uncle-report-header");
    const buyerGroupsContainerEl = document.getElementById("buyer-groups-container");
    const strategiesContainerEl = document.getElementById("strategies-container");
    const uncleSummaryTextEl = document.getElementById("uncle-summary-text");
    const brokeragesListEl = document.getElementById("brokerages-list");
    
    // Linker Elements
    const linkerInsightEl = document.getElementById("linker-insight-text");
    const dateEl = document.getElementById("insight-date");
    
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
    fetch(`data/processed_insights.json?t=${Date.now()}`)
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

    // Text-to-Speech Edge TTS Audio Logic
    ttsPlayBtn.addEventListener("click", () => {
        if (!insightData) return;
        const news = insightData.english_professor_news[currentNewsIndex];
        if (!news) return;

        // Stop any current playback first
        stopSpeech();

        isSpeaking = true;
        
        // Dynamically load the pre-generated en-US-AndrewNeural mp3 file
        const audioSrc = `data/audio/news_${currentNewsIndex + 1}.mp3`;
        audioPlayer = new Audio(audioSrc);

        ttsPlayBtn.style.display = "none";
        ttsStopBtn.style.display = "inline-flex";

        audioPlayer.play().catch(err => {
            console.error("Failed to play Edge TTS audio file:", err);
            stopSpeech();
            alert("Edge TTS 音檔載入失敗，請確認後端處理器已正確執行並生成語音音檔。");
        });

        // Listen for playback completion to reset UI
        audioPlayer.onended = () => {
            stopSpeech();
        };

        audioPlayer.onerror = (e) => {
            console.error("Audio playback error:", e);
            stopSpeech();
        };
    });

    ttsStopBtn.addEventListener("click", () => {
        stopSpeech();
    });

    function stopSpeech() {
        isSpeaking = false;
        if (audioPlayer) {
            audioPlayer.pause();
            audioPlayer.currentTime = 0;
            audioPlayer = null;
        }
        resetSpeechUI();
    }

    function resetSpeechUI() {
        ttsPlayBtn.style.display = "inline-flex";
        ttsStopBtn.style.display = "none";
    }

    // Sandbox Notes & Vocabulary Bank Logic
    
    // Sandbox New Elements
    const sandboxNotification = document.getElementById("sandbox-notification");
    const btnCloseNotification = document.getElementById("btn-close-notification");
    const sandboxTabBtns = document.querySelectorAll(".sandbox-tab-btn");
    const sandboxPanels = document.querySelectorAll(".sandbox-panel");
    const btnConsolidateNow = document.getElementById("btn-consolidate-now");
    const btnExportVocab = document.getElementById("btn-export-vocab");
    const inputImportVocab = document.getElementById("input-import-vocab");
    const btnClearVocab = document.getElementById("btn-clear-vocab");
    const vocabListContainer = document.getElementById("vocab-list");
    const vocabCountEl = document.getElementById("vocab-count");
    
    // Quiz View Elements
    const quizSetupView = document.getElementById("quiz-setup-view");
    const quizActiveView = document.getElementById("quiz-active-view");
    const quizResultView = document.getElementById("quiz-result-view");
    const btnStartQuiz = document.getElementById("btn-start-quiz");
    const btnNextQuestion = document.getElementById("btn-next-question");
    const btnRestartQuiz = document.getElementById("btn-restart-quiz");
    const quizQuestionText = document.getElementById("quiz-question-text");
    const quizOptionsContainer = document.getElementById("quiz-options");
    const quizFeedbackText = document.getElementById("quiz-feedback-text");
    const quizCurrentNumEl = document.getElementById("quiz-current-num");
    const quizScoreNumEl = document.getElementById("quiz-score-num");
    const quizFinalScoreEl = document.getElementById("quiz-final-score");

    // Load Vocabulary Bank
    let vocabBank = [];
    try {
        const storedVocab = localStorage.getItem("alphainsight_vocab_bank");
        if (storedVocab) {
            vocabBank = JSON.parse(storedVocab);
        }
    } catch (e) {
        console.error("Failed to load vocabulary bank", e);
        vocabBank = [];
    }

    // Render Vocabulary Bank Function
    function renderVocabBank() {
        if (vocabCountEl) {
            vocabCountEl.textContent = vocabBank.length;
        }
        if (vocabListContainer) {
            if (vocabBank.length === 0) {
                vocabListContainer.innerHTML = '<p class="vocab-empty-msg">單字庫目前是空的。請在「筆記編輯」中寫下單字後歸檔，或點選匯入。</p>';
            } else {
                vocabListContainer.innerHTML = "";
                // Sort alphabetically by word
                const sortedVocab = [...vocabBank].sort((a, b) => a.word.localeCompare(b.word));
                sortedVocab.forEach(item => {
                    const chip = document.createElement("div");
                    chip.className = "vocab-chip";
                    chip.innerHTML = `
                        <span class="vocab-chip-word">${item.word}</span>
                        <span class="vocab-chip-meaning">${item.meaning}</span>
                    `;
                    vocabListContainer.appendChild(chip);
                });
            }
        }
    }

    // Parser for Sandbox Notes
    function parseNotesToVocabulary(notesText) {
        if (!notesText) return [];
        const lines = notesText.split('\n');
        const vocabList = [];
        for (let line of lines) {
            line = line.trim();
            if (!line) continue;
            // Matches English word/phrase at the start and Chinese translation at the end.
            // Accepts spaces, hyphens, colons, vertical bars as separators.
            // E.g., "go on a tear 勢不可擋" or "take a hit - 遭受打擊"
            const match = line.match(/^([a-zA-Z0-9\s'’,\-\?!()\/]+?)(?:\s*[\-–—:|]\s*|\s+)([^a-zA-Z0-9].*)$/);
            if (match) {
                vocabList.push({
                    word: match[1].trim(),
                    meaning: match[2].trim()
                });
            } else {
                // Fallback split by common separators
                const parts = line.split(/\s+-\s+|\s*:\s*|\s*\|\s*/);
                if (parts.length >= 2) {
                    vocabList.push({
                        word: parts[0].trim(),
                        meaning: parts.slice(1).join(' ').trim()
                    });
                }
            }
        }
        return vocabList;
    }

    // Save Vocabulary Bank
    function saveVocabBank() {
        localStorage.setItem("alphainsight_vocab_bank", JSON.stringify(vocabBank));
        renderVocabBank();
    }

    // Consolidate notes into Vocabulary Bank
    function consolidateNotes(isAuto = false) {
        const text = sandboxTextarea.value.trim();
        if (!text) {
            if (!isAuto) {
                alert("筆記內容為空，無可歸檔的單字。");
            }
            return false;
        }

        const newVocabItems = parseNotesToVocabulary(text);
        if (newVocabItems.length === 0) {
            if (!isAuto) {
                alert("未偵測到符合格式的單字！\n請確認每行輸入一個單字，格式如：\ngo on a tear 勢不可擋\nbear market - 空頭市場");
            }
            return false;
        }

        // Merge and deduplicate by word (case-insensitive)
        let addedCount = 0;
        newVocabItems.forEach(newItem => {
            const exists = vocabBank.some(item => item.word.toLowerCase() === newItem.word.toLowerCase());
            if (!exists) {
                vocabBank.push(newItem);
                addedCount++;
            }
        });

        // Save and clear active editor
        saveVocabBank();
        sandboxTextarea.value = "";
        localStorage.setItem("alphainsight_sandbox_note", "");
        
        if (!isAuto) {
            alert(`已成功解析並整理！\n成功歸檔 ${addedCount} 個新單字。`);
        }
        return true;
    }

    // Weekly Auto-Cleanup Check
    function checkWeeklyCleanup() {
        const now = Date.now();
        let lastCleanup = localStorage.getItem("alphainsight_last_cleanup");
        
        if (!lastCleanup) {
            // First time running the app, set timestamp and do nothing else
            localStorage.setItem("alphainsight_last_cleanup", now.toString());
            return;
        }

        const timeDiff = now - parseInt(lastCleanup, 10);
        const sevenDaysMs = 7 * 24 * 60 * 60 * 1000;

        if (timeDiff >= sevenDaysMs) {
            // It has been a week! Check if there's any content to consolidate
            const currentNote = localStorage.getItem("alphainsight_sandbox_note") || "";
            if (currentNote.trim()) {
                // Save old textarea value to check
                sandboxTextarea.value = currentNote;
                consolidateNotes(true);
            }
            
            // Show notification banner
            if (sandboxNotification) {
                sandboxNotification.style.display = "flex";
            }

            // Update last cleanup time
            localStorage.setItem("alphainsight_last_cleanup", now.toString());
        }
    }

    // Close Notification Event
    if (btnCloseNotification) {
        btnCloseNotification.addEventListener("click", () => {
            sandboxNotification.style.display = "none";
        });
    }

    // Load saved active note and render vocab list on startup
    const savedActiveNote = localStorage.getItem("alphainsight_sandbox_note");
    if (savedActiveNote && sandboxTextarea) {
        sandboxTextarea.value = savedActiveNote;
    }
    renderVocabBank();
    checkWeeklyCleanup();

    // Textarea Autosave Listener
    if (sandboxTextarea) {
        sandboxTextarea.addEventListener("input", () => {
            clearTimeout(saveTimeout);
            clearTimeout(hideStatusTimeout);
            
            saveStatusEl.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> 正在儲存...';
            saveStatusEl.classList.add("show");

            saveTimeout = setTimeout(() => {
                localStorage.setItem("alphainsight_sandbox_note", sandboxTextarea.value);
                saveStatusEl.innerHTML = '<i class="fa-solid fa-cloud-arrow-up"></i> 已即時儲存';
                
                hideStatusTimeout = setTimeout(() => {
                    saveStatusEl.classList.remove("show");
                }, 1500);
            }, 800);
        });
    }

    // Consolidate Button Listener
    if (btnConsolidateNow) {
        btnConsolidateNow.addEventListener("click", () => {
            consolidateNotes(false);
        });
    }

    // Export Vocabulary Button Listener
    if (btnExportVocab) {
        btnExportVocab.addEventListener("click", () => {
            if (vocabBank.length === 0) {
                alert("單字庫目前為空，沒有可匯出的內容。");
                return;
            }
            const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(vocabBank, null, 2));
            const downloadAnchor = document.createElement('a');
            downloadAnchor.setAttribute("href", dataStr);
            downloadAnchor.setAttribute("download", "alphainsight_vocab_bank.json");
            document.body.appendChild(downloadAnchor);
            downloadAnchor.click();
            downloadAnchor.remove();
        });
    }

    // Import Vocabulary Button Listener
    if (inputImportVocab) {
        inputImportVocab.addEventListener("change", (event) => {
            const file = event.target.files[0];
            if (!file) return;

            const reader = new FileReader();
            reader.onload = (e) => {
                try {
                    const imported = JSON.parse(e.target.result);
                    if (Array.isArray(imported)) {
                        let importedCount = 0;
                        imported.forEach(item => {
                            if (item.word && item.meaning) {
                                const exists = vocabBank.some(v => v.word.toLowerCase() === item.word.toLowerCase());
                                if (!exists) {
                                    vocabBank.push({
                                        word: item.word.trim(),
                                        meaning: item.meaning.trim()
                                    });
                                    importedCount++;
                                }
                            }
                        });
                        saveVocabBank();
                        alert(`成功匯入！\n從檔案匯入了 ${importedCount} 個新單字。`);
                    } else {
                        alert("匯入失敗：檔案格式不正確，必須是 JSON 陣列。");
                    }
                } catch (err) {
                    alert("匯入失敗：解析 JSON 檔案出錯。");
                }
                // Reset file input
                inputImportVocab.value = "";
            };
            reader.readAsText(file);
        });
    }

    // Clear Vocabulary Button Listener
    if (btnClearVocab) {
        btnClearVocab.addEventListener("click", () => {
            if (vocabBank.length === 0) return;
            if (confirm("您確定要清空所有的單字嗎？此動作將無法還原。")) {
                vocabBank = [];
                saveVocabBank();
                alert("已成功清空單字庫。");
            }
        });
    }

    // Sandbox Panel Tabs Toggle
    if (sandboxTabBtns) {
        sandboxTabBtns.forEach(btn => {
            btn.addEventListener("click", () => {
                const targetTab = btn.getAttribute("data-sandbox-tab");
                
                // Toggle active tab class
                sandboxTabBtns.forEach(b => b.classList.remove("active"));
                btn.classList.add("active");
                
                // Toggle active panel class
                sandboxPanels.forEach(panel => {
                    if (panel.id === `sandbox-panel-${targetTab}`) {
                        panel.classList.add("active");
                    } else {
                        panel.classList.remove("active");
                    }
                });

                // If switching to words, render them
                if (targetTab === "words") {
                    renderVocabBank();
                }
                
                // If switching to quiz, reset to setup view
                if (targetTab === "quiz") {
                    resetQuizUI();
                }
            });
        });
    }

    // --- Interactive Quiz Logic ---
    let quizQuestions = [];
    let currentQuestionIdx = 0;
    let quizScore = 0;
    let hasAnswered = false;

    function resetQuizUI() {
        if (quizSetupView && quizActiveView && quizResultView) {
            quizSetupView.style.display = "block";
            quizActiveView.style.display = "none";
            quizResultView.style.display = "none";
        }
    }

    // Helper to shuffle array
    function shuffleArray(array) {
        const arr = [...array];
        for (let i = arr.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [arr[i], arr[j]] = [arr[j], arr[i]];
        }
        return arr;
    }

    // Start Quiz Button Listener
    if (btnStartQuiz) {
        btnStartQuiz.addEventListener("click", () => {
            if (vocabBank.length < 4) {
                alert("您的單字庫中至少需要 4 個單字才能開始測驗！\n請先去筆記編輯區記錄一些單字並點選「整理並歸檔」。");
                return;
            }

            // Shuffle and pick up to 10 questions
            const shuffledBank = shuffleArray(vocabBank);
            quizQuestions = shuffledBank.slice(0, Math.min(10, shuffledBank.length));
            
            currentQuestionIdx = 0;
            quizScore = 0;

            quizSetupView.style.display = "none";
            quizResultView.style.display = "none";
            quizActiveView.style.display = "block";

            loadQuizQuestion();
        });
    }

    // Load Quiz Question
    function loadQuizQuestion() {
        hasAnswered = false;
        
        if (btnNextQuestion) btnNextQuestion.style.display = "none";
        if (quizFeedbackText) quizFeedbackText.style.display = "none";

        const currentQuestion = quizQuestions[currentQuestionIdx];
        if (quizCurrentNumEl) quizCurrentNumEl.textContent = currentQuestionIdx + 1;
        if (quizScoreNumEl) quizScoreNumEl.textContent = quizScore;
        
        if (quizQuestionText) {
            quizQuestionText.innerHTML = `「<span style="color:var(--neon-amber);">${currentQuestion.word}</span>」的中文意思是什麼？`;
        }

        // Distractors generation: pick 3 other words from vocabBank
        const otherWords = vocabBank.filter(item => item.word.toLowerCase() !== currentQuestion.word.toLowerCase());
        const shuffledDistractors = shuffleArray(otherWords);
        const pickedDistractors = shuffledDistractors.slice(0, 3);

        // Put correct answer and distractors together and shuffle
        const options = shuffleArray([
            { text: currentQuestion.meaning, isCorrect: true },
            ...pickedDistractors.map(d => ({ text: d.meaning, isCorrect: false }))
        ]);

        // Render options buttons
        if (quizOptionsContainer) {
            quizOptionsContainer.innerHTML = "";
            const optionLabels = ["A", "B", "C", "D"];
            options.forEach((opt, idx) => {
                const btn = document.createElement("button");
                btn.className = "quiz-option-btn";
                btn.innerHTML = `
                    <span class="quiz-option-badge">${optionLabels[idx]}</span>
                    <span>${opt.text}</span>
                `;
                
                // Add click listener
                btn.addEventListener("click", () => handleAnswerSelect(opt.isCorrect, btn));
                quizOptionsContainer.appendChild(btn);
            });
        }
    }

    // Handle Option Selection
    function handleAnswerSelect(isCorrect, selectedBtn) {
        if (hasAnswered) return;
        hasAnswered = true;

        // Show feedback and Next button
        if (btnNextQuestion) {
            btnNextQuestion.style.display = "inline-flex";
            if (currentQuestionIdx === quizQuestions.length - 1) {
                btnNextQuestion.innerHTML = '查看結果 <i class="fa-solid fa-square-check"></i>';
            } else {
                btnNextQuestion.innerHTML = '下一題 <i class="fa-solid fa-arrow-right"></i>';
            }
        }

        // Highlight correct and incorrect options
        const optionBtns = quizOptionsContainer.querySelectorAll(".quiz-option-btn");
        
        // Find correct option index in DOM to highlight
        const correctQuestionObj = quizQuestions[currentQuestionIdx];
        optionBtns.forEach(btn => {
            const textContent = btn.querySelector("span:last-child").textContent;
            if (textContent === correctQuestionObj.meaning) {
                btn.classList.add("correct");
            }
        });

        if (isCorrect) {
            quizScore++;
            if (quizScoreNumEl) quizScoreNumEl.textContent = quizScore;
            
            selectedBtn.classList.add("correct");
            if (quizFeedbackText) {
                quizFeedbackText.style.display = "block";
                quizFeedbackText.className = "quiz-feedback correct";
                quizFeedbackText.innerHTML = '<i class="fa-solid fa-circle-check"></i> 答對了！太棒了！';
            }
        } else {
            selectedBtn.classList.add("incorrect");
            if (quizFeedbackText) {
                quizFeedbackText.style.display = "block";
                quizFeedbackText.className = "quiz-feedback incorrect";
                quizFeedbackText.innerHTML = `<i class="fa-solid fa-circle-xmark"></i> 答錯了！正確答案是：${correctQuestionObj.meaning}`;
            }
        }
    }

    // Next Question Button Listener
    if (btnNextQuestion) {
        btnNextQuestion.addEventListener("click", () => {
            currentQuestionIdx++;
            if (currentQuestionIdx < quizQuestions.length) {
                loadQuizQuestion();
            } else {
                // Show final result view
                if (quizActiveView) quizActiveView.style.display = "none";
                if (quizResultView) {
                    quizResultView.style.display = "block";
                    if (quizFinalScoreEl) {
                        const scorePercent = Math.round((quizScore / quizQuestions.length) * 100);
                        quizFinalScoreEl.textContent = scorePercent;
                    }
                }
            }
        });
    }

    // Restart Quiz Button Listener
    if (btnRestartQuiz) {
        btnRestartQuiz.addEventListener("click", () => {
            resetQuizUI();
            if (btnStartQuiz) btnStartQuiz.click();
        });
    }

    // View Tab Selection Logic
    const viewBtns = document.querySelectorAll(".view-tab-btn");
    const appMainEl = document.querySelector(".app-main");

    if (viewBtns && appMainEl) {
        // Load default/saved view from localStorage or default to "morning"
        let savedView = localStorage.getItem("alphainsight_preferred_view") || "morning";
        if (savedView === "all") {
            savedView = "morning";
        }
        
        // Function to apply a view
        const applyView = (view) => {
            // Stop speech when view changes
            stopSpeech();

            // Remove all view classes from appMainEl
            appMainEl.classList.remove("view-morning", "view-english", "view-night", "view-sandbox");
            
            // Add selected view class
            appMainEl.classList.add(`view-${view}`);
            
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
