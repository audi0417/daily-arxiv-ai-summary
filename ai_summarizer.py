#!/usr/bin/env python3
"""
AI 摘要生成模組
使用 Google Gemini API 生成論文摘要
"""

import os
import logging
import json
import time
from typing import List, Dict, Optional
import google.generativeai as genai
from datetime import datetime

logger = logging.getLogger(__name__)

class AISummarizer:
    """AI 摘要生成器"""
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-2.0-flash-exp"):
        """
        初始化 AI 摘要生成器
        
        Args:
            api_key: Google API 金鑰
            model_name: 模型名稱
        """
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        self.model_name = model_name
        self.language = os.getenv('LANGUAGE', 'Traditional Chinese')
        
        if not self.api_key:
            logger.warning("⚠️ GOOGLE_API_KEY 未設定，將跳過 AI 摘要生成")
            self.model = None
            return
        
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
            logger.info(f"✅ AI 模型初始化成功: {self.model_name}")
        except Exception as e:
            logger.error(f"❌ AI 模型初始化失敗: {e}")
            self.model = None
    
    def _create_summary_prompt(self, papers: List[Dict]) -> str:
        """
        創建摘要生成提示詞
        
        Args:
            papers: 論文列表
            
        Returns:
            提示詞
        """
        papers_text = ""
        for i, paper in enumerate(papers, 1):
            authors_str = ", ".join(paper['authors'][:3])  # 最多顯示3位作者
            if len(paper['authors']) > 3:
                authors_str += " et al."
            
            papers_text += f"""
論文 {i}:
標題: {paper['title']}
作者: {authors_str}
類別: {', '.join(paper['categories'])}
摘要: {paper['summary'][:500]}...
arXiv ID: {paper['arxiv_id']}
連結: {paper['arxiv_url']}

---
"""
        
        prompt = f"""
你是一位專業的學術論文分析師，請為以下 {len(papers)} 篇 arXiv 論文生成一份專業的中文摘要報告。

論文資料:
{papers_text}

請按照以下格式生成報告，使用繁體中文：

# 每日 ArXiv 論文智慧摘要: {datetime.now().strftime('%Y-%m-%d')}

> 🤖 由 AI 自動生成的論文摘要報告
> 
> 📊 本日共處理 {len(papers)} 篇論文
> 
> 🕒 生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📈 重點趨勢分析

[分析當前AI/ML領域的主要趨勢，約100-150字]

## 🔥 今日亮點論文

[選出2-3篇最有影響力或創新性的論文，每篇用以下格式]

### 📄 [論文標題]
- **作者**: [作者名單]
- **類別**: [論文類別]
- **arXiv ID**: [ID]
- **創新點**: [簡述論文的主要創新點或貢獻，50-80字]
- **影響**: [說明對該領域的潛在影響，30-50字]
- **🔗 [閱讀原文](arXiv連結)**

## 🏷️ 分類摘要

[按論文類別分組摘要，每個類別包含]

### [類別名稱] ({該類別論文數量}篇)

- **[論文標題]** - [一句話描述核心貢獻] ([arXiv ID](連結))
- **[論文標題]** - [一句話描述核心貢獻] ([arXiv ID](連結))

## 📊 本日統計

- **論文總數**: {len(papers)}
- **主要類別**: [列出前3個最多論文的類別]
- **熱門關鍵字**: [基於論文標題和摘要提取的熱門技術關鍵字]

## 🔮 技術展望

[基於今日論文，簡述技術發展趨勢和未來方向，約80-100字]

---

## 📋 完整論文列表

[列出所有論文的基本資訊]

### 人工智慧 (AI)
1. **[論文標題]** - [作者] ([arXiv ID](連結))

### 機器學習 (ML)  
1. **[論文標題]** - [作者] ([arXiv ID](連結))

[依此類推其他類別]

---

## 🔗 相關連結

- [ArXiv 官網](https://arxiv.org/)
- [專案 GitHub](https://github.com/audi0417/daily-arxiv-ai-summary)

---

*本報告由 AI 自動生成，如有任何問題請提交 Issue。*

請確保內容專業、準確，並突出論文的技術創新點和實際應用價值。摘要應該有助於研究人員快速了解當前領域的發展動態。
"""
        return prompt
    
    def generate_summary(self, papers: List[Dict]) -> str:
        """
        生成論文摘要
        
        Args:
            papers: 論文列表
            
        Returns:
            生成的摘要
        """
        if not self.model:
            logger.warning("⚠️ AI 模型未初始化，生成預設摘要")
            return self._generate_default_summary(papers)
        
        if not papers:
            logger.warning("⚠️ 沒有論文資料，生成空摘要")
            return self._generate_empty_summary()
        
        try:
            logger.info(f"🤖 使用 {self.model_name} 生成 {len(papers)} 篇論文的摘要...")
            
            prompt = self._create_summary_prompt(papers)
            
            # 生成摘要（增加重試機制）
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = self.model.generate_content(
                        prompt,
                        generation_config=genai.types.GenerationConfig(
                            temperature=0.7,
                            max_output_tokens=4000,
                        )
                    )
                    
                    if response.text:
                        logger.info("✅ AI 摘要生成成功")
                        return response.text
                    else:
                        logger.warning(f"⚠️ AI 回應為空 (嘗試 {attempt + 1}/{max_retries})")
                        
                except Exception as e:
                    logger.error(f"❌ AI 生成失敗 (嘗試 {attempt + 1}/{max_retries}): {e}")
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)  # 指數退避
                    
            logger.error("❌ AI 摘要生成失敗，使用預設摘要")
            return self._generate_default_summary(papers)
            
        except Exception as e:
            logger.error(f"❌ AI 摘要生成時發生錯誤: {e}")
            return self._generate_default_summary(papers)
    
    def _generate_default_summary(self, papers: List[Dict]) -> str:
        """
        生成預設摘要（當 AI 不可用時）
        
        Args:
            papers: 論文列表
            
        Returns:
            預設摘要
        """
        today = datetime.now().strftime('%Y-%m-%d')
        
        # 統計類別
        category_stats = {}
        for paper in papers:
            for cat in paper['categories']:
                category_stats[cat] = category_stats.get(cat, 0) + 1
        
        top_categories = sorted(category_stats.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # 生成論文列表
        papers_list = ""
        for i, paper in enumerate(papers, 1):
            authors_str = ", ".join(paper['authors'][:2])
            if len(paper['authors']) > 2:
                authors_str += " et al."
            
            papers_list += f"{i}. **{paper['title']}** - {authors_str} ([{paper['arxiv_id']}]({paper['arxiv_url']}))\n"
        
        summary = f"""# 每日 ArXiv 論文智慧摘要: {today}

> 🤖 由系統自動生成的論文摘要報告
> 
> 📊 本日共處理 {len(papers)} 篇論文
> 
> 🕒 生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📢 系統狀態

✅ 論文爬蟲運行正常  
⚠️ AI 摘要功能暫時不可用，顯示基本資訊

### 🔧 設定檢查

- **API 金鑰**: {'❌ 未設定或無效' if not self.api_key else '⚠️ 設定但無法使用'}
- **模型名稱**: {self.model_name}
- **輸出語言**: {self.language}

---

## 📊 本日統計

- **論文總數**: {len(papers)}
- **主要類別**: {', '.join([f"{cat} ({count}篇)" for cat, count in top_categories])}

## 📋 完整論文列表

{papers_list}

---

## 🚀 下一步

1. 設定有效的 GOOGLE_API_KEY 以啟用 AI 摘要功能
2. 檢查 API 配額和網路連線
3. 確認模型名稱設定正確

## 🔗 相關連結

- [ArXiv 官網](https://arxiv.org/)
- [專案 GitHub](https://github.com/audi0417/daily-arxiv-ai-summary)

---

*本報告由系統自動生成，AI 摘要功能需要設定 API 金鑰後才能使用。*
"""
        return summary
    
    def _generate_empty_summary(self) -> str:
        """
        生成空摘要（當沒有論文時）
        
        Returns:
            空摘要
        """
        today = datetime.now().strftime('%Y-%m-%d')
        
        return f"""# 每日 ArXiv 論文智慧摘要: {today}

> 🤖 由系統自動生成的論文摘要報告
> 
> 📊 本日共處理 0 篇論文
> 
> 🕒 生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📢 系統狀態

✅ 系統運行正常  
⚠️ 本日沒有找到符合條件的新論文

### 可能原因

1. **週末或假日** - arXiv 通常在工作日發布新論文
2. **搜尋條件過於嚴格** - 可能需要調整關鍵字或類別設定
3. **網路連線問題** - 無法正常存取 arXiv API

### 🔧 建議檢查

- 確認網路連線正常
- 檢查 `config/topics.yaml` 中的設定
- 嘗試放寬搜尋條件

---

## 📊 本日統計

- **論文總數**: 0
- **搜尋類別**: 已設定
- **關鍵字過濾**: 已啟用

## 🔗 相關連結

- [ArXiv 官網](https://arxiv.org/)
- [專案 GitHub](https://github.com/audi0417/daily-arxiv-ai-summary)

---

*本報告由系統自動生成，明日將繼續嘗試抓取新論文。*
"""
