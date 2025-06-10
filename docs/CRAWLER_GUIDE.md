# ArXiv 論文爬蟲完整使用指南

## 🎯 功能概述

本系統現在具備完整的 arXiv 論文爬蟲功能，採用專業的模組化架構：

- 📡 **智能論文爬蟲** - 從 arXiv API 獲取最新 AI/ML 論文
- 🔍 **高級過濾系統** - 根據類別和關鍵字智能過濾
- 🤖 **AI 智能摘要** - 使用 Google Gemini 生成繁體中文摘要  
- 📊 **統計分析** - 提供論文類別和趨勢分析
- 🕒 **全自動化** - GitHub Actions 每日自動執行
- 📁 **專業架構** - 模組化設計，易於維護和擴展

## 🏗️ 項目架構

```
daily-arxiv-ai-summary/
├── src/                          # 核心源代碼
│   ├── crawler/                  # 論文爬蟲模組
│   │   ├── __init__.py          
│   │   └── arxiv_crawler.py     # ArXiv API 爬蟲實現
│   ├── ai/                       # AI 摘要模組
│   │   ├── __init__.py
│   │   └── summarizer.py        # Gemini AI 摘要生成
│   ├── processor/                # 資料處理模組
│   ├── generator/                # 報告生成模組
│   └── utils/                    # 工具函數
├── config/                       # 設定檔案
│   └── topics.yaml              # 論文類別和關鍵字設定
├── data/                         # 生成的報告和資料
│   ├── YYYY-MM-DD.md           # 每日摘要報告
│   └── YYYY-MM-DD_papers.json  # 原始論文資料
├── docs/                         # 文檔目錄
├── .github/workflows/           # GitHub Actions 配置
│   └── daily_update.yml        # 自動化工作流程
├── main.py                      # 主執行腳本
├── simple_main.py              # 簡化版腳本（向後兼容）
└── requirements.txt             # Python 依賴套件
```

## 🚀 核心模組說明

### 1. ArXiv 爬蟲模組 (`src/crawler/arxiv_crawler.py`)

**核心特性：**
- 🌐 **高效 API 接口** - 直接連接 arXiv.org API
- 📋 **智能解析** - 自動解析 XML 格式論文資料
- 🔍 **多維過濾** - 支援類別、關鍵字、日期範圍過濾
- ⚡ **性能優化** - 內建請求限流和錯誤處理
- 📊 **統計分析** - 提供論文類別分布統計

**支援的論文類別：**
```yaml
categories:
  - cs.AI        # 人工智慧
  - cs.LG        # 機器學習  
  - cs.CV        # 電腦視覺
  - cs.CL        # 自然語言處理
  - cs.NE        # 神經與演化計算
  - cs.IR        # 資訊檢索
  - cs.HC        # 人機互動
  - stat.ML      # 機器學習統計
  - stat.AP      # 應用統計
  - math.OC      # 最佳化與控制
```

### 2. AI 摘要模組 (`src/ai/summarizer.py`)

**核心特性：**
- 🤖 **Gemini Integration** - 使用最新 Google Gemini 2.0 Flash
- 🇹🇼 **繁體中文支援** - 專為台灣研究社群設計
- 🔄 **智能重試** - 自動處理 API 限制和錯誤
- 📝 **專業格式** - 生成結構化學術摘要報告
- 🛡️ **容錯機制** - API 不可用時提供基本摘要

**摘要報告包含：**
- 📈 重點趨勢分析
- 🔥 今日亮點論文  
- 🏷️ 分類摘要
- 📊 統計數據
- 🔮 技術展望
- 📋 完整論文列表

## ⚙️ 設定檔配置

### `config/topics.yaml` - 詳細設定

```yaml
# 要爬取的論文類別
categories:
  - cs.AI        # 人工智慧
  - cs.LG        # 機器學習
  - cs.CV        # 電腦視覺
  - cs.CL        # 計算語言學與自然語言處理
  - cs.NE        # 神經與演化計算

# 關鍵字過濾 (可選)
keywords:
  include:       # 必須包含的關鍵字
    - transformer
    - attention
    - deep learning
    - neural network
    - machine learning
    - artificial intelligence
    - computer vision
    - natural language processing
    - large language model
    - generative AI
    - diffusion model
    - reinforcement learning
  exclude:       # 要排除的關鍵字
    - survey only
    - review only

# 數量限制
limits:
  max_papers_per_day: 50          # 每日最大論文數
  max_papers_per_category: 10     # 每類別最大數量

# 日期過濾
date_filter:
  recent_days: 3                  # 處理最近 N 天的論文
  include_weekends: true          # 是否包含週末

# AI 分析設定
ai_analysis:
  enable_keyword_scoring: true    # 關鍵字重要性評分
  enable_difficulty_assessment: true  # 技術難度評估
```

## 🚀 使用方法

### 本地執行

1. **環境準備**
   ```bash
   # 克隆專案
   git clone https://github.com/audi0417/daily-arxiv-ai-summary.git
   cd daily-arxiv-ai-summary
   
   # 安裝依賴
   pip install -r requirements.txt
   ```

2. **設定環境變數**
   ```bash
   # 必要設定
   export GOOGLE_API_KEY="your_google_api_key_here"
   
   # 可選設定
   export MODEL_NAME="gemini-2.0-flash-exp"
   export LANGUAGE="Traditional Chinese"
   ```

3. **執行腳本**
   ```bash
   # 處理今日論文
   python main.py
   
   # 強制更新（即使已有報告）
   export FORCE_UPDATE=true
   python main.py
   
   # 處理指定日期
   export CUSTOM_DATE="2025-06-10"
   python main.py
   ```

### GitHub Actions 自動化

1. **設定 Repository Secrets**
   - 前往 `Settings` → `Secrets and variables` → `Actions`
   - 新增 `GOOGLE_API_KEY`

2. **設定 Repository Variables** (可選)
   - `MODEL_NAME`: 預設 `gemini-2.0-flash-exp`
   - `LANGUAGE`: 預設 `Traditional Chinese`
   - `EMAIL`: Git 提交者 email
   - `NAME`: Git 提交者名稱

3. **手動觸發**
   - 前往 `Actions` 標籤
   - 選擇 `📚 每日 ArXiv 論文智慧摘要更新`
   - 點擊 `Run workflow`

## 📊 輸出說明

### 生成的檔案

1. **`data/YYYY-MM-DD.md`** - 每日摘要報告
   - 📈 趨勢分析
   - 🔥 亮點論文
   - 🏷️ 分類摘要
   - 📊 統計數據

2. **`data/YYYY-MM-DD_papers.json`** - 原始論文資料
   - 完整論文資訊
   - 作者、摘要、連結
   - 類別和時間資訊

### 報告範例結構

```markdown
# 每日 ArXiv 論文智慧摘要: 2025-06-10

> 🤖 由 AI 自動生成的論文摘要報告
> 📊 本日共處理 25 篇論文

## 📈 重點趨勢分析
[AI 分析當前領域主要趨勢]

## 🔥 今日亮點論文
### 📄 [論文標題]
- **作者**: [作者列表]
- **創新點**: [技術創新描述]
- **影響**: [領域影響分析]

## 🏷️ 分類摘要
### 機器學習 (10篇)
- **論文標題** - 核心貢獻描述 ([arXiv:2501.XXXXX](連結))

## 📊 本日統計
- **論文總數**: 25
- **主要類別**: cs.LG (10篇), cs.AI (8篇), cs.CV (7篇)
- **熱門關鍵字**: transformer, attention, diffusion

## 🔮 技術展望
[基於本日論文的技術發展趨勢分析]
```

## 🔧 進階設定

### 自訂論文類別

編輯 `config/topics.yaml`：
```yaml
categories:
  - cs.AI        # 人工智慧
  - cs.LG        # 機器學習
  - physics.data-an  # 物理資料分析
  - q-bio.QM     # 量化生物學
```

### 調整關鍵字過濾

```yaml
keywords:
  include:
    - "your custom keywords"
    - "research area terms"
  exclude:
    - "unwanted terms"
```

### 修改數量限制

```yaml
limits:
  max_papers_per_day: 100    # 增加每日處理量
  max_papers_per_category: 20
```

## 🛡️ 錯誤處理

系統內建多層錯誤處理：

1. **網路連線問題** - 自動重試機制
2. **API 限制** - 智能等待和重試
3. **解析錯誤** - 跳過問題論文，繼續處理
4. **AI 服務不可用** - 自動降級到基本摘要

## 📈 性能優化

- ⚡ **並行處理** - 支援多線程論文處理
- 🗂️ **智能快取** - 避免重複請求
- 📊 **增量更新** - 只處理新論文
- 🔄 **斷點續傳** - 支援中斷後繼續

## 🤝 貢獻指南

1. Fork 專案
2. 創建功能分支
3. 提交變更
4. 創建 Pull Request

## 📄 授權

本專案採用 Apache 2.0 授權，詳見 [LICENSE](LICENSE) 檔案。

---

**專案維護者**: [@audi0417](https://github.com/audi0417)
**問題回報**: [GitHub Issues](https://github.com/audi0417/daily-arxiv-ai-summary/issues)
**功能建議**: [GitHub Discussions](https://github.com/audi0417/daily-arxiv-ai-summary/discussions)
