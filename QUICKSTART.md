# 🚀 快速開始指南

歡迎使用每日 ArXiv 論文智慧摘要系統！這個指南將幫助您在 5 分鐘內設定完成。

## ⚡ 三步驟快速設定

### 步驟 1: Fork 專案
點擊右上角的 **Fork** 按鈕，將專案複製到您的 GitHub 帳號。

### 步驟 2: 取得 Google API 金鑰
1. 前往 [Google AI Studio](https://aistudio.google.com/)
2. 登入 Google 帳號
3. 點擊 **Get API Key** → **Create API Key**
4. 複製 API 金鑰

### 步驟 3: 設定 GitHub Variables 和 Secrets

前往您的專案 → **Settings** → **Secrets and variables** → **Actions**

#### 設定 Secrets (機密資料)
點擊 **New repository secret**：
- **Name**: `GOOGLE_API_KEY`
- **Secret**: 貼上您的 API 金鑰

#### 設定 Variables (公開變數)
點擊 **Variables** 頁籤 → **New repository variable**，逐一新增：

| 變數名稱 | 建議值 |
|---------|-------|
| `LANGUAGE` | `Traditional Chinese` |
| `MODEL_NAME` | `gemini-2.0-flash-exp` |
| `EMAIL` | 您的郵箱地址 |
| `NAME` | 您的姓名 |

## ✅ 啟用自動化

1. 前往 **Actions** 頁籤
2. 點擊 **I understand my workflows, go ahead and enable them**
3. 完成！系統將在每日台灣時間 00:30 自動執行

## 🎯 自訂研究主題

編輯 `config/topics.yaml` 檔案來設定您感興趣的領域：

```yaml
categories:
  - cs.AI        # 人工智慧
  - cs.LG        # 機器學習
  - cs.CV        # 電腦視覺
  - cs.CL        # 自然語言處理
```

[完整 ArXiv 類別列表](https://arxiv.org/category_taxonomy)

## 🧪 測試運行

手動觸發工作流程來測試：

1. 前往 **Actions** → **每日 ArXiv 論文智慧摘要更新**
2. 點擊 **Run workflow**
3. 選擇選項後點擊 **Run workflow**
4. 等待 2-5 分鐘查看結果

## 📊 查看結果

成功執行後，您會在 `data/` 目錄中看到：
- `YYYY-MM-DD.md` - 格式化的論文報告
- `YYYY-MM-DD.jsonl` - 原始資料
- 更新的 README.md

## ⚙️ 進階設定

### 修改執行時間
編輯 `.github/workflows/daily_update.yml`:
```yaml
schedule:
  - cron: "30 16 * * *"  # UTC 時間
```

### 調整論文數量
在 `config/topics.yaml` 中：
```yaml
limits:
  max_papers_per_day: 50
```

### 關鍵字過濾
```yaml
keywords:
  include:
    - transformer
    - deep learning
  exclude:
    - survey
    - review
```

## 🔧 故障排除

### 常見問題

**❌ 沒有生成報告**
- 檢查 API 金鑰是否正確
- 確認 Actions 已啟用
- 查看 Actions 執行日誌

**❌ API 錯誤**
- 確認 Google API 金鑰有效
- 檢查 API 用量是否超限

**❌ 沒有新論文**
- 檢查 ArXiv 是否有新論文發布
- 嘗試強制更新選項

### 檢查執行日誌
1. 前往 **Actions** 頁籤
2. 點擊最新的執行記錄
3. 展開各個步驟查看詳細日誌

## 📞 取得幫助

如果遇到問題：

1. 📖 查看 [詳細設定指南](docs/setup.md)
2. 🔍 搜尋 [已知問題](https://github.com/audi0417/daily-arxiv-ai-summary/issues)
3. 💬 [提交新的 Issue](https://github.com/audi0417/daily-arxiv-ai-summary/issues/new)

## 🎉 完成！

設定完成後，您將每天自動收到：
- 📚 精選論文摘要
- 🧠 AI 智慧分析
- 🔍 繁體中文翻譯
- 📊 統計報告

享受您的個人 AI 論文助理！ 🤖✨

---

**提示**: 第一次執行可能需要較長時間，後續執行會更快。建議先手動測試一次確保設定正確。