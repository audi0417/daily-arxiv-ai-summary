# API 參考文件

本文件描述了專案中各個模組的 API 接口。

## 📚 核心模組

### ArxivCrawler

**路徑**: `src/crawler/arxiv_crawler.py`

#### 類別描述

```python
class ArxivCrawler:
    """ArXiv 論文爬蟲類別"""
```

#### 初始化

```python
def __init__(self, config: Dict)
```

**參數**:
- `config` (Dict): 配置字典，包含類別、關鍵字等設定

#### 主要方法

```python
def crawl_papers(self, target_date: str) -> List[Dict]
```

**功能**: 爬取指定日期的論文

**參數**:
- `target_date` (str): 目標日期，格式為 'YYYY-MM-DD'

**回傳**: 論文資料列表

---

### GeminiEnhancer

**路徑**: `src/ai/gemini_enhancer.py`

#### 類別描述

```python
class GeminiEnhancer:
    """Gemini AI 增強器類別"""
```

#### 主要方法

```python
def enhance_papers(self, papers: List[Dict]) -> List[Dict]
```

**功能**: 批量增強論文，加入 AI 分析

**參數**:
- `papers` (List[Dict]): 論文資料列表

**回傳**: 增強後的論文資料列表

```python
def enhance_paper(self, paper: Dict) -> Dict
```

**功能**: 增強單篇論文

**參數**:
- `paper` (Dict): 單篇論文資料

**回傳**: 增強後的論文資料

---

### DataProcessor

**路徑**: `src/processor/data_processor.py`

#### 主要方法

```python
def deduplicate_papers(self, papers: List[Dict]) -> List[Dict]
```

**功能**: 去除重複論文

```python
def filter_new_papers(self, papers: List[Dict], previous_files: List[Path]) -> List[Dict]
```

**功能**: 過濾出新論文

```python
def save_papers(self, papers: List[Dict], file_path: Path) -> bool
```

**功能**: 儲存論文資料到 JSONL 檔案

```python
def load_papers(self, file_path: Path) -> List[Dict]
```

**功能**: 從 JSONL 檔案載入論文資料

---

### ReportGenerator

**路徑**: `src/generator/report_generator.py`

#### 主要方法

```python
def generate_report(self, papers: List[Dict], output_file: Path, date: str) -> bool
```

**功能**: 生成 Markdown 報告

**參數**:
- `papers` (List[Dict]): 論文資料列表
- `output_file` (Path): 輸出檔案路徑
- `date` (str): 報告日期

**回傳**: 是否成功生成報告

---

## 📄 資料結構

### 論文資料結構

```python
{
    'id': str,                    # 論文 ID
    'title': str,                 # 標題
    'authors': List[str],         # 作者列表
    'summary': str,               # 摘要
    'categories': List[str],      # 類別列表
    'published': str,             # 發布日期 (ISO格式)
    'updated': str,               # 更新日期 (ISO格式)
    'pdf_url': str,               # PDF 連結
    'entry_id': str,              # ArXiv 條目 ID
    'primary_category': str,      # 主要類別
    'comment': str,               # 註解 (可選)
    'journal_ref': str,           # 期刊參考 (可選)
    'AI': Dict                    # AI 增強資料 (見下方)
}
```

### AI 增強資料結構

```python
{
    'tldr': str,                  # 一句話摘要
    'motivation': str,            # 研究動機
    'method': str,                # 方法介紹
    'result': str,                # 實驗結果
    'conclusion': str,            # 研究結論
    'summary_zh': str,            # 繁體中文摘要
    'keywords': List[str],        # 關鍵詞列表
    'difficulty': str             # 技術難度
}
```

### 配置檔案結構

**config/topics.yaml**:

```yaml
categories:                   # ArXiv 類別列表
  - cs.AI
  - cs.LG

keywords:                     # 關鍵字過濾
  include: []                 # 包含關鍵字
  exclude: []                 # 排除關鍵字

limits:                       # 數量限制
  max_papers_per_day: 50
  max_papers_per_category: 10

date_filter:                  # 日期過濾
  recent_days: 3
  include_weekends: true

ai_analysis:                  # AI 分析設定
  enable_keyword_scoring: true
  enable_related_papers: false
  enable_difficulty_assessment: true

output:                       # 輸出設定
  generate_pdf: false
  include_references: false
  detailed_author_info: false
```

---

## 🔧 工具函數

### setup_logger

**路徑**: `src/utils/logger.py`

```python
def setup_logger(name: str, log_file: Optional[Path] = None, level: int = logging.INFO) -> logging.Logger
```

**功能**: 設定統一的日誌記錄器

### ConfigLoader

**路徑**: `src/utils/config_loader.py`

```python
class ConfigLoader:
    def load_yaml(self, filename: str) -> Dict[str, Any]
    def get_env_config(self) -> Dict[str, str]
    def validate_config(self, config: Dict[str, Any]) -> bool
```

---

## 🌍 環境變數

| 變數名稱 | 類型 | 預設值 | 說明 |
|---------|------|--------|------|
| `GOOGLE_API_KEY` | str | 必填 | Google Gemini API 金鑰 |
| `MODEL_NAME` | str | `gemini-2.0-flash-exp` | 使用的 AI 模型 |
| `LANGUAGE` | str | `Traditional Chinese` | 輸出語言 |
| `CUSTOM_DATE` | str | 空字串 | 自訂日期 (YYYY-MM-DD) |
| `FORCE_UPDATE` | str | `false` | 是否強制更新 |

---

## 🧪 範例使用

### 基本使用流程

```python
from src.crawler.arxiv_crawler import ArxivCrawler
from src.ai.gemini_enhancer import GeminiEnhancer
from src.processor.data_processor import DataProcessor
from src.generator.report_generator import ReportGenerator

# 載入配置
config = {...}  # 從 topics.yaml 載入

# 初始化模組
crawler = ArxivCrawler(config)
enhancer = GeminiEnhancer()
processor = DataProcessor()
generator = ReportGenerator()

# 執行流程
papers = crawler.crawl_papers('2025-06-10')
unique_papers = processor.deduplicate_papers(papers)
enhanced_papers = enhancer.enhance_papers(unique_papers)
success = generator.generate_report(enhanced_papers, 'output.md', '2025-06-10')
```

### 自訂 AI 分析

```python
from src.ai.gemini_enhancer import GeminiEnhancer

enhancer = GeminiEnhancer()

# 修改提示詞 (需要繼承並覆寫 _create_analysis_prompt 方法)
class CustomEnhancer(GeminiEnhancer):
    def _create_analysis_prompt(self, paper):
        # 自訂提示詞邏輯
        return custom_prompt
```

這份 API 參考文件提供了專案各個模組的詳細接口說明，方便開發者理解和擴展功能。