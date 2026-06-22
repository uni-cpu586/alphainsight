# AlphaInsight Workspace Rules

## Execution Constraints
- **NO MOCK DATA / NO MOCK FALLBACKS**: All data processing pipelines (both `crawler.py` and `agent_processor.py`) are strictly prohibited from using any mock or hardcoded simulation data (including mock stock market data and mock news). If any data fetching or AI API call fails, the program must throw an exception and terminate immediately.
- **Stock Uncle Gemini Enforcement**: The `stock_uncle` module must always run using the Gemini API.
- **Other Modules Choices**: Other modules (English Professor, Market Linker) must run using either Gemini API (in `--mode gemini`) or local Ollama (in `--mode hybrid`).



