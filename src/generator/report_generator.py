"""
報告生成器
將處理後的論文資料生成美化的 Markdown 報告
"""

import os
from pathlib import Path
from typing import List, Dict
from datetime import datetime
from jinja2 import Template
from collections import Counter


class ReportGenerator:
    """報告生成器類別"""
    
    def __init__(self):
        """初始化生成器"""
        self.template = self._get_report_template()
        print("📝 報告生成器初始化完成")
    
    def _get_report_template(self) -> Template:
        """取得報告範本"""
        template_str = """
# 每日 ArXiv 論文智慧摘要: {{ date }}

> 🤖 由 AI 自動生成的論文摘要報告
> 
> 📊 本日共處理 {{ total_papers }} 篇論文
> 
> 🕒 生成時間: {{ generation_time }}

---

{% for paper in papers %}
## [{{ paper.title }}]({{ paper.entry_id }})

**📝 一句話摘要**
{{ paper.AI.tldr }}

**👥 作者:** {{ paper.authors | join(', ') }}
**🏷️ 類別:** {{ paper.categories | join(', ') }}
**📅 發布日期:** {{ paper.published[:10] }}
{% if paper.AI.keywords %}**🔍 關鍵詞:** {{ paper.AI.keywords | join(', ') }}{% endif %}
{% if paper.AI.difficulty %}**⭐ 技術難度:** {{ paper.AI.difficulty }}{% endif %}

[**📄 論文連結**]({{ paper.entry_id }}) | [**📑 PDF 下載**]({{ paper.pdf_url }})

### 🎯 研究動機
{{ paper.AI.motivation }}

### 🔬 方法介紹  
{{ paper.AI.method }}

### 📈 實驗結果
{{ paper.AI.result }}

### 💡 研究結論
{{ paper.AI.conclusion }}

### 📋 繁體中文摘要
> {{ paper.AI.summary_zh }}

---

{% endfor %}

## 📊 本日統計

- **論文總數:** {{ total_papers }}
- **主要類別:** {{ main_categories | join(', ') }}
- **平均作者數:** {{ avg_authors | round(1) }}

## 🔗 相關連結

- [ArXiv 官網](https://arxiv.org/)
- [專案 GitHub](https://github.com/audi0417/daily-arxiv-ai-summary)

---

*本報告由 AI 自動生成，如有任何問題請提交 Issue。*
"""
        return Template(template_str)
    
    def _extract_statistics(self, papers: List[Dict]) -> Dict:
        """提取論文統計資訊"""
        if not papers:
            return {
                'total_papers': 0,
                'main_categories': [],
                'avg_authors': 0
            }
        
        # 統計類別分布
        all_categories = []
        for paper in papers:
            all_categories.extend(paper.get('categories', []))
        
        category_counter = Counter(all_categories)
        main_categories = [cat for cat, _ in category_counter.most_common(5)]
        
        # 計算平均作者數
        total_authors = sum(len(paper.get('authors', [])) for paper in papers)
        avg_authors = total_authors / len(papers) if papers else 0
        
        return {
            'total_papers': len(papers),
            'main_categories': main_categories,
            'avg_authors': avg_authors
        }
    
    def generate_report(self, papers: List[Dict], output_file: Path, date: str) -> bool:
        """生成 Markdown 報告"""
        try:
            print(f"📝 開始生成 {date} 的論文報告")
            
            # 提取統計資訊
            stats = self._extract_statistics(papers)
            
            # 準備範本資料
            template_data = {
                'date': date,
                'papers': papers,
                'generation_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                **stats
            }
            
            # 渲染範本
            report_content = self.template.render(**template_data)
            
            # 確保輸出目錄存在
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 寫入檔案
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            print(f"✅ 報告生成完成: {output_file}")
            return True
            
        except Exception as e:
            print(f"❌ 生成報告時發生錯誤: {e}")
            return False