# 設定指南

本文件將指導您如何設定和使用每日 ArXiv 論文智慧摘要系統。

## 📋 前置需求

- GitHub 帳號
- Google Cloud Platform 帳號（用於 Gemini API）
- 基本的 Git 和 GitHub 操作知識

## 🔧 詳細設定步驟

### 1. 取得 Google Gemini API 金鑰

1. 前往 [Google AI Studio](https://aistudio.google.com/)
2. 登入您的 Google 帳號
3. 點擊「Get API Key」
4. 創建新的 API 金鑰
5. 複製並安全保存此金鑰

### 2. Fork 專案

1. 前往 [專案頁面](https://github.com/audi0417/daily-arxiv-ai-summary)
2. 點擊右上角的「Fork」按鈕
3. 選擇您的 GitHub 帳號作為目標

### 3. 設定 GitHub Secrets 和 Variables

#### Secrets（機密資料）

前往您 Fork 的專案 → Settings → Secrets and variables → Actions

點擊「New repository secret」，加入以下機密資料：

- **名稱**: `GOOGLE_API_KEY`
- **值**: 您在步驟 1 取得的 API 金鑰

#### Variables（公開變數）

在同一頁面點擊「Variables」頁籤，然後點擊「New repository variable」，加入以下變數：

| 變數名稱 | 建議值 | 說明 |
|---------|-------|------|
| `LANGUAGE` | `Traditional Chinese` | 輸出語言 |
| `MODEL_NAME` | `gemini-2.0-flash-exp` | 使用的 AI 模型 |
| `EMAIL` | 您的郵箱地址 | Git commit 用 |
| `NAME` | 您的姓名 | Git commit 用 |

### 4. 自訂研究主題

編輯 `config/topics.yaml` 檔案來設定您感興趣的研究領域：

```yaml
categories:
  - cs.AI        # 人工智慧
  - cs.LG        # 機器學習
  - cs.CV        # 電腦視覺
  - cs.CL        # 自然語言處理
  # 更多類別請參考 ArXiv 分類系統

keywords:
  include:
    - transformer
    - deep learning
    - neural network
  exclude:
    - survey
    - review
```

### 5. 啟用 GitHub Actions

1. 前往您的專案 → Actions 頁籤
2. 點擊「I understand my workflows, go ahead and enable them」
3. 系統將自動在每日 UTC 16:30 (台灣時間 00:30) 執行

### 6. 測試運行

您可以手動觸發工作流程來測試：

1. 前往 Actions → 「每日 ArXiv 論文智慧摘要更新」
2. 點擊「Run workflow」
3. 可選擇自訂日期或強制更新
4. 點擊「Run workflow」按鈕

## 🛠️ 進階設定

### 修改執行時間

編輯 `.github/workflows/daily_update.yml` 檔案中的 cron 設定：

```yaml
schedule:
  - cron: "30 16 * * *"  # UTC 時間
```

### 自訂 AI 提示詞

修改 `src/ai/gemini_enhancer.py` 中的 `_create_analysis_prompt` 方法。

### 調整論文數量限制

在 `config/topics.yaml` 中設定：

```yaml
limits:
  max_papers_per_day: 50
  max_papers_per_category: 10
```

## ❗ 常見問題

### Q: 為什麼沒有生成報告？

A: 請檢查：
1. GitHub Actions 是否啟用
2. API 金鑰是否正確設定
3. 是否有新論文發布
4. 檢查 Actions 頁面的執行日誌

### Q: 如何更改關注的研究領域？

A: 編輯 `config/topics.yaml` 檔案中的 `categories` 部分。

### Q: 可以使用其他語言嗎？

A: 可以，在 GitHub Variables 中修改 `LANGUAGE` 變數。

### Q: API 用量會很大嗎？

A: 專案已經加入了節流機制，每次請求間隔 4 秒，符合 Google 免費版限制。

## 📞 支援

如果您遇到問題，請：

1. 查看 [GitHub Issues](https://github.com/audi0417/daily-arxiv-ai-summary/issues)
2. 提交新的 Issue 描述您的問題
3. 包含相關的錯誤訊息和設定資訊

祝您使用愉快！ 🚀