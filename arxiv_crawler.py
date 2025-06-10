#!/usr/bin/env python3
"""
ArXiv 論文爬蟲模組
用於從 arXiv API 獲取最新論文資訊
"""

import os
import re
import time
import logging
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from urllib.parse import urlencode
import yaml

logger = logging.getLogger(__name__)

class ArxivCrawler:
    """ArXiv 論文爬蟲"""
    
    def __init__(self, config_path: str = "config/topics.yaml"):
        """
        初始化爬蟲
        
        Args:
            config_path: 設定檔路徑
        """
        self.base_url = "http://export.arxiv.org/api/query"
        self.config = self._load_config(config_path)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ArXiv-Daily-Summary/1.0 (https://github.com/audi0417/daily-arxiv-ai-summary)'
        })
        
    def _load_config(self, config_path: str) -> Dict:
        """載入設定檔"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            logger.info(f"✅ 成功載入設定檔: {config_path}")
            return config
        except FileNotFoundError:
            logger.warning(f"⚠️ 設定檔不存在: {config_path}，使用預設設定")
            return self._get_default_config()
        except Exception as e:
            logger.error(f"❌ 載入設定檔失敗: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """取得預設設定"""
        return {
            'categories': ['cs.AI', 'cs.LG', 'cs.CV', 'cs.CL'],
            'limits': {
                'max_papers_per_day': 50,
                'max_papers_per_category': 10
            },
            'date_filter': {
                'recent_days': 3,
                'include_weekends': True
            },
            'keywords': {
                'include': [
                    'transformer', 'attention', 'deep learning', 
                    'neural network', 'machine learning'
                ]
            }
        }
    
    def _build_search_query(self, categories: List[str], date_from: str) -> str:
        """
        建構 arXiv 搜尋查詢
        
        Args:
            categories: 論文類別列表
            date_from: 起始日期 (YYYYMMDD)
            
        Returns:
            搜尋查詢字串
        """
        # 建構類別查詢
        cat_queries = [f"cat:{cat}" for cat in categories]
        cat_query = " OR ".join(cat_queries)
        
        # 建構日期查詢
        date_query = f"submittedDate:[{date_from}* TO *]"
        
        # 結合查詢
        full_query = f"({cat_query}) AND {date_query}"
        
        logger.info(f"🔍 搜尋查詢: {full_query}")
        return full_query
    
    def _parse_paper_entry(self, entry: ET.Element) -> Optional[Dict]:
        """
        解析單篇論文資訊
        
        Args:
            entry: XML entry 元素
            
        Returns:
            論文資訊字典
        """
        try:
            # 基本資訊
            paper_id = entry.find('{http://www.w3.org/2005/Atom}id').text
            arxiv_id = paper_id.split('/')[-1]
            
            title = entry.find('{http://www.w3.org/2005/Atom}title').text.strip()
            title = re.sub(r'\s+', ' ', title)  # 清理多餘空格
            
            summary = entry.find('{http://www.w3.org/2005/Atom}summary').text.strip()
            summary = re.sub(r'\s+', ' ', summary)  # 清理多餘空格
            
            # 作者資訊
            authors = []
            for author in entry.findall('{http://www.w3.org/2005/Atom}author'):
                name = author.find('{http://www.w3.org/2005/Atom}name').text
                authors.append(name)
            
            # 類別資訊
            categories = []
            for cat in entry.findall('{http://arxiv.org/schemas/atom}primary_category'):
                categories.append(cat.get('term'))
            for cat in entry.findall('{http://arxiv.org/schemas/atom}category'):
                cat_term = cat.get('term')
                if cat_term not in categories:
                    categories.append(cat_term)
            
            # 日期資訊
            published_raw = entry.find('{http://www.w3.org/2005/Atom}published').text
            published = datetime.fromisoformat(published_raw.replace('Z', '+00:00'))
            
            updated_raw = entry.find('{http://www.w3.org/2005/Atom}updated').text
            updated = datetime.fromisoformat(updated_raw.replace('Z', '+00:00'))
            
            # PDF 連結
            pdf_url = None
            for link in entry.findall('{http://www.w3.org/2005/Atom}link'):
                if link.get('title') == 'pdf':
                    pdf_url = link.get('href')
                    break
            
            return {
                'arxiv_id': arxiv_id,
                'title': title,
                'authors': authors,
                'summary': summary,
                'categories': categories,
                'published': published,
                'updated': updated,
                'pdf_url': pdf_url,
                'arxiv_url': f"https://arxiv.org/abs/{arxiv_id}"
            }
            
        except Exception as e:
            logger.error(f"❌ 解析論文資訊失敗: {e}")
            return None
    
    def _filter_papers_by_keywords(self, papers: List[Dict]) -> List[Dict]:
        """
        根據關鍵字過濾論文
        
        Args:
            papers: 論文列表
            
        Returns:
            過濾後的論文列表
        """
        if 'keywords' not in self.config:
            return papers
        
        keywords_config = self.config['keywords']
        include_keywords = keywords_config.get('include', [])
        exclude_keywords = keywords_config.get('exclude', [])
        
        filtered_papers = []
        
        for paper in papers:
            text_to_search = f"{paper['title']} {paper['summary']}".lower()
            
            # 檢查包含關鍵字
            if include_keywords:
                has_include_keyword = any(
                    keyword.lower() in text_to_search 
                    for keyword in include_keywords
                )
                if not has_include_keyword:
                    continue
            
            # 檢查排除關鍵字
            if exclude_keywords:
                has_exclude_keyword = any(
                    keyword.lower() in text_to_search 
                    for keyword in exclude_keywords
                )
                if has_exclude_keyword:
                    continue
            
            filtered_papers.append(paper)
        
        logger.info(f"🔍 關鍵字過濾: {len(papers)} → {len(filtered_papers)}")
        return filtered_papers
    
    def _apply_limits(self, papers: List[Dict]) -> List[Dict]:
        """
        應用論文數量限制
        
        Args:
            papers: 論文列表
            
        Returns:
            限制後的論文列表
        """
        limits = self.config.get('limits', {})
        max_papers = limits.get('max_papers_per_day', 50)
        
        if len(papers) > max_papers:
            # 按發布時間排序，取最新的
            papers_sorted = sorted(papers, key=lambda x: x['published'], reverse=True)
            papers = papers_sorted[:max_papers]
            logger.info(f"📊 應用論文數量限制: {max_papers}")
        
        return papers
    
    def get_papers(self, target_date: Optional[str] = None) -> List[Dict]:
        """
        獲取指定日期的論文
        
        Args:
            target_date: 目標日期 (YYYY-MM-DD)，預設為今日
            
        Returns:
            論文列表
        """
        if target_date is None:
            target_date = datetime.utcnow().strftime('%Y-%m-%d')
        
        # 計算搜尋日期範圍
        target_dt = datetime.strptime(target_date, '%Y-%m-%d')
        recent_days = self.config.get('date_filter', {}).get('recent_days', 3)
        start_date = target_dt - timedelta(days=recent_days)
        date_from = start_date.strftime('%Y%m%d')
        
        logger.info(f"🔍 搜尋日期範圍: {start_date.strftime('%Y-%m-%d')} 到 {target_date}")
        
        # 取得類別列表
        categories = self.config.get('categories', ['cs.AI', 'cs.LG'])
        logger.info(f"📚 搜尋類別: {categories}")
        
        # 建構搜尋查詢
        search_query = self._build_search_query(categories, date_from)
        
        # 執行搜尋
        papers = self._search_papers(search_query)
        
        if not papers:
            logger.warning("⚠️ 沒有找到任何論文")
            return []
        
        logger.info(f"📄 找到 {len(papers)} 篇論文")
        
        # 應用過濾條件
        papers = self._filter_papers_by_keywords(papers)
        papers = self._apply_limits(papers)
        
        logger.info(f"✅ 最終獲得 {len(papers)} 篇論文")
        return papers
    
    def _search_papers(self, query: str, max_results: int = 100) -> List[Dict]:
        """
        執行 arXiv 搜尋
        
        Args:
            query: 搜尋查詢
            max_results: 最大結果數量
            
        Returns:
            論文列表
        """
        params = {
            'search_query': query,
            'max_results': max_results,
            'sortBy': 'submittedDate',
            'sortOrder': 'descending'
        }
        
        url = f"{self.base_url}?{urlencode(params)}"
        
        try:
            logger.info(f"🌐 發送請求到 arXiv API...")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # 解析 XML 回應
            root = ET.fromstring(response.content)
            
            # 檢查是否有錯誤
            for message in root.findall('.//{http://www.w3.org/2005/Atom}title'):
                if 'Error' in message.text:
                    logger.error(f"❌ arXiv API 錯誤: {message.text}")
                    return []
            
            # 解析論文條目
            papers = []
            entries = root.findall('{http://www.w3.org/2005/Atom}entry')
            
            for entry in entries:
                paper = self._parse_paper_entry(entry)
                if paper:
                    papers.append(paper)
            
            # API 請求限制：每 3 秒最多 1 次請求
            time.sleep(3)
            
            return papers
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ 網路請求失敗: {e}")
            return []
        except ET.ParseError as e:
            logger.error(f"❌ XML 解析失敗: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ 搜尋論文時發生未知錯誤: {e}")
            return []
    
    def get_paper_categories_stats(self, papers: List[Dict]) -> Dict[str, int]:
        """
        取得論文類別統計
        
        Args:
            papers: 論文列表
            
        Returns:
            類別統計字典
        """
        stats = {}
        for paper in papers:
            for category in paper['categories']:
                stats[category] = stats.get(category, 0) + 1
        
        return dict(sorted(stats.items(), key=lambda x: x[1], reverse=True))
