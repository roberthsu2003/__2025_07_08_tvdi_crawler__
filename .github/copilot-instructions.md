# Copilot AI Coding Agent Instructions

## 專案架構與核心知識
- 本專案為多模組 Python 股票爬蟲工具，重點模組集中於 `lesson6/`，包含：
  - `index.py`：主程式進入點
  - `wantgoo.py`：爬蟲核心邏輯
  - `stock_gui.py`：GUI 介面
  - `run.py`：快速啟動腳本
  - `.copilot/`：AI/自動化相關設定與知識庫
- 其他 lessonX/ 目錄為教學或範例，主開發聚焦於 lesson6/

## 關鍵開發流程
- **安裝依賴**：
  - 需 Python 3.8+，安裝依賴：`pip install crawl4ai twstock`
- **初始化 Copilot/AI 環境**：
  - 執行 `python3 lesson6/setup_copilot.py` 產生/更新 AI context
- **啟動主程式**：
  - CLI：`python3 lesson6/index.py`
  - GUI：`python3 lesson6/stock_gui.py`
- **測試**：
  - 主要測試檔：`lesson6/test_copilot_config.py`

## 專案慣例與模式
- **AI/自動化設定**：
  - `.copilot/` 目錄下有 `instructions.md`, `knowledge.md`, `project.yml` 等，供 AI 參考專案結構、知識、行為規範
  - `setup_ai_context.py` 會動態產生 `context.json`，供 Copilot/AI 使用
- **資料流**：
  - 爬蟲資料流：`wantgoo.py` 取得資料 → `index.py`/`stock_gui.py` 處理與顯示
- **命名慣例**：
  - 以 `wantgoo` 命名爬蟲相關模組
  - 測試檔以 `test_` 開頭
- **外部依賴**：
  - 主要依賴 `crawl4ai`, `twstock`，如需擴充請先檢查 `requirements.txt`

## 重要檔案/目錄
- `lesson6/`：主開發目錄
- `lesson6/.copilot/`：AI/自動化設定
- `lesson6/wantgoo.py`：爬蟲核心
- `lesson6/stock_gui.py`：GUI 介面
- `lesson6/setup_copilot.py`：Copilot/AI context 初始化
- `lesson6/test_copilot_config.py`：AI 設定測試

## 其他注意事項
- 請優先維護 lesson6/ 相關模組，其他 lessonX/ 僅供參考
- 任何自動化/AI 相關規則請同步更新 `.copilot/` 內對應檔案
- 若有疑問，請參考 lesson6/README.md 及 .copilot/README.md

---
如需更動架構、慣例，請先檢查 `.copilot/` 及 `README.md`，確保一致性。
