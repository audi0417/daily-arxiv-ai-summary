# 每日 ArXiv 論文智慧摘要

🤖 基於 AI 的 ArXiv 論文自動抓取與摘要生成系統

## ✨ 功能特色

- 🔍 **自動抓取** - 每日自動爬取指定領域的 ArXiv 最新論文
- 🧠 **AI 摘要** - 使用 Google Gemini API 生成繁體中文摘要
- 📊 **去重處理** - 自動過濾重複論文，僅處理新發布內容
- 🎯 **主題靈活** - 可輕鬆調整研究領域和關鍵字
- 📝 **美化輸出** - 產生格式化的 Markdown 報告
- ⚡ **自動化** - GitHub Actions 定時執行，無需手動操作

## 🚀 快速開始

### 1. Fork 本專案到您的 GitHub

### 2. 設定 API 金鑰和變數

前往您的 GitHub 儲存庫 → Settings → Secrets and variables

#### Secrets (機密資料)
- `GOOGLE_API_KEY`: 您的 Google Gemini API 金鑰

#### Variables (公開變數)
- `LANGUAGE`: `Traditional Chinese` (輸出語言)
- `MODEL_NAME`: `gemini-2.0-flash-exp` (使用的模型)
- `EMAIL`: 您的 Email (用於 Git commit)
- `NAME`: 您的姓名 (用於 Git commit)

### 3. 自訂研究主題

編輯 `config/topics.yaml` 檔案來設定您感興趣的研究領域：

```yaml
# 主要搜尋的 ArXiv 類別
categories:
  - cs.AI        # 人工智慧
  - cs.LG        # 機器學習
  - cs.CV        # 電腦視覺
  - cs.CL        # 計算語言學

# 關鍵字過濾 (可選)
keywords:
  include:
    - transformer
    - deep learning
    - neural network
  exclude:
    - survey
    - review
```

### 4. 啟用 GitHub Actions

- 前往 Actions 頁籤
- 啟用 workflows
- 系統將自動在每日 UTC 16:30 (台灣時間 00:30) 執行

## 📁 專案結構

```
daily-arxiv-ai-summary/
├── .github/workflows/
│   └── daily_update.yml     # GitHub Actions 工作流程
├── config/
│   └── topics.yaml          # 主題設定檔
├── src/
│   ├── crawler/             # 論文爬蟲模組
│   ├── processor/           # 資料處理模組
│   ├── ai/                  # AI 增強模組
│   ├── generator/           # 報告生成模組
│   └── utils/               # 工具模組
├── templates/               # 範本檔案
├── data/                    # 產生的資料檔案
└── README.md
```

## 🔧 進階設定

### 修改執行時間

編輯 `.github/workflows/daily_update.yml` 中的 cron 設定：

```yaml
on:
  schedule:
    - cron: "30 16 * * *"  # UTC 時間，台灣時間請加8小時
```

### 自訂 AI 提示詞

修改 `src/ai/prompts.py` 來調整 AI 分析的角度和格式。

### 增加新的論文來源

在 `src/crawler/sources.py` 中新增其他學術資料庫的爬蟲。

## 📊 輸出格式

每日生成的報告包含：

- **一句話摘要**: 論文核心貢獻的簡潔描述
- **研究動機**: 問題背景與研究目的
- **方法介紹**: 提出的技術或方法
- **實驗結果**: 主要發現與成果
- **結論**: 研究的意義與影響
- **繁體中文摘要**: 原文摘要的中文翻譯

## 🤝 貢獻指南

歡迎提交 Issue 和 Pull Request！

1. Fork 專案
2. 建立特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交變更 (`git commit -m '新增驚人功能'`)
4. 推送分支 (`git push origin feature/amazing-feature`)
5. 開啟 Pull Request

## 📄 授權條款

本專案採用 Apache License 2.0 - 詳見 [LICENSE](LICENSE) 檔案

## ⚠️ 注意事項

- Google Gemini 免費版 API 每分鐘限制 15 次請求
- 如果沒有新論文更新，請檢查 ArXiv 是否有發布新內容
- 建議定期檢查 API 用量避免超出額度

## 💡 常見問題

**Q: 如何更改關注的研究領域？**
A: 編輯 `config/topics.yaml` 檔案中的 categories 欄位。

**Q: 可以修改摘要的語言嗎？**
A: 可以，在 GitHub Variables 中修改 `LANGUAGE` 變數。

**Q: 如何調整 AI 模型？**
A: 修改 `MODEL_NAME` 變數，支援所有 Google Gemini 模型。

---

如有任何問題，請隨時開啟 Issue 討論！ 🚀