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
        # 設置重試參數
        self.max_retries = 3
        self.retry_delay = 5
        
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
            'categories': ['cs.AI', 'cs.LG', 'cs.CV', 'cs.CL', 'cs.NE', 'cs.IR', 'cs.HC', 'stat.ML', 'stat.AP', 'math.OC'],
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
                    'neural network', 'machine learning', 'artificial intelligence'
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
            # 定義命名空間
            namespaces = {
                'atom': 'http://www.w3.org/2005/Atom',
                'arxiv': 'http://arxiv.org/schemas/atom'
            }
            
            # 基本資訊
            id_elem = entry.find('atom:id', namespaces)
            if id_elem is None:
                return None
            
            paper_id = id_elem.text
            arxiv_id = paper_id.split('/')[-1]
            
            # 標題
            title_elem = entry.find('atom:title', namespaces)
            title = title_elem.text.strip() if title_elem is not None else "未知標題"
            title = re.sub(r'\s+', ' ', title)  # 清理多餘空格
            
            # 摘要
            summary_elem = entry.find('atom:summary', namespaces)
            summary = summary_elem.text.strip() if summary_elem is not None else "無摘要"
            summary = re.sub(r'\s+', ' ', summary)  # 清理多餘空格
            
            # 作者資訊
            authors = []
            for author in entry.findall('atom:author', namespaces):
                name_elem = author.find('atom:name', namespaces)
                if name_elem is not None:
                    authors.append(name_elem.text)
            
            # 類別資訊
            categories = []
            
            # 主要類別
            primary_cat = entry.find('arxiv:primary_category', namespaces)
            if primary_cat is not None:
                categories.append(primary_cat.get('term'))
            
            # 所有類別
            for cat in entry.findall('atom:category', namespaces):
                cat_term = cat.get('term')
                if cat_term and cat_term not in categories:
                    categories.append(cat_term)
            
            # 日期資訊
            published_elem = entry.find('atom:published', namespaces)
            if published_elem is not None:
                published_raw = published_elem.text
                published = datetime.fromisoformat(published_raw.replace('Z', '+00:00'))
            else:
                published = datetime.now()
            
            updated_elem = entry.find('atom:updated', namespaces)
            if updated_elem is not None:
                updated_raw = updated_elem.text
                updated = datetime.fromisoformat(updated_raw.replace('Z', '+00:00'))
            else:
                updated = published
            
            # PDF 連結
            pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
            
            # 檢查是否有評論
            comment_elem = entry.find('arxiv:comment', namespaces)
            comment = comment_elem.text if comment_elem is not None else None
            
            return {
                'arxiv_id': arxiv_id,
                'title': title,
                'authors': authors,
                'summary': summary,
                'categories': categories,
                'published': published,
                'updated': updated,
                'pdf_url': pdf_url,
                'arxiv_url': f"https://arxiv.org/abs/{arxiv_id}",
                'comment': comment
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
        
        if not include_keywords and not exclude_keywords:
            return papers
        
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
        執行 arXiv 搜尋，支持重試機制
        
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
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"🌐 發送請求到 arXiv API (嘗試 {attempt + 1}/{self.max_retries})...")
                
                # 使用更長的超時時間
                response = self.session.get(url, timeout=60)
                response.raise_for_status()
                
                # 檢查回應是否為空
                if not response.content:
                    logger.warning("⚠️ 收到空回應")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay)
                        continue
                    else:
                        return []
                
                # 解析 XML 回應
                try:
                    root = ET.fromstring(response.content)
                except ET.ParseError as e:
                    logger.error(f"❌ XML 解析失敗: {e}")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay)
                        continue
                    else:
                        return []
                
                # 檢查是否有錯誤訊息
                total_results_elem = root.find('.//{http://a9.com/-/spec/opensearch/1.1/}totalResults')
                if total_results_elem is not None:
                    total_results = int(total_results_elem.text)
                    logger.info(f"📊 arXiv 回報總結果數: {total_results}")
                
                # 解析論文條目
                papers = []
                namespaces = {
                    'atom': 'http://www.w3.org/2005/Atom',
                    'arxiv': 'http://arxiv.org/schemas/atom'
                }
                
                entries = root.findall('atom:entry', namespaces)
                logger.info(f"📄 解析到 {len(entries)} 個條目")
                
                for entry in entries:
                    paper = self._parse_paper_entry(entry)
                    if paper:
                        papers.append(paper)
                
                # API 請求限制：每 3 秒最多 1 次請求
                time.sleep(3)
                
                logger.info(f"✅ 成功解析 {len(papers)} 篇論文")
                return papers
                
            except requests.exceptions.Timeout:
                logger.warning(f"⚠️ 請求超時 (嘗試 {attempt + 1})")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    logger.error("❌ 所有重試都超時")
                    
            except requests.exceptions.ConnectionError as e:
                logger.warning(f"⚠️ 連接錯誤 (嘗試 {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    logger.error("❌ 所有重試都連接失敗")
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"❌ 網路請求失敗 (嘗試 {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    logger.error("❌ 所有網路請求都失敗")
                    
            except Exception as e:
                logger.error(f"❌ 搜尋論文時發生未知錯誤 (嘗試 {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    logger.error("❌ 所有嘗試都失敗")
        
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
