#!/usr/bin/env python3
"""
完整的論文處理腳本
整合 arXiv 爬蟲和 AI 摘要生成功能
"""

import os
import sys
import json
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path

# 添加 src 目錄到 Python 路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# 本地模組
from src.crawler import ArxivCrawler
from src.ai import AISummarizer

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def get_today_date():
    """取得今日日期"""
    custom_date = os.getenv('CUSTOM_DATE', '').strip()
    if custom_date:
        try:
            datetime.strptime(custom_date, '%Y-%m-%d')
            return custom_date
        except ValueError:
            logger.warning(f"⚠️ 無效的日期格式: {custom_date}")
    
    return datetime.utcnow().strftime('%Y-%m-%d')

def save_papers_data(papers, date_str):
    """儲存論文資料到 JSON 檔案"""
    try:
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        
        # 轉換 datetime 物件為字串以便 JSON 序列化
        papers_for_json = []
        for paper in papers:
            paper_copy = paper.copy()
            paper_copy['published'] = paper['published'].isoformat()
            paper_copy['updated'] = paper['updated'].isoformat()
            papers_for_json.append(paper_copy)
        
        json_file = data_dir / f"{date_str}_papers.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(papers_for_json, f, ensure_ascii=False, indent=2)
        
        logger.info(f"💾 論文資料已儲存: {json_file}")
        
    except Exception as e:
        logger.error(f"❌ 儲存論文資料失敗: {e}")

def save_summary_report(summary, date_str):
    """儲存摘要報告到 Markdown 檔案"""
    try:
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        
        report_file = data_dir / f"{date_str}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        logger.info(f"📝 摘要報告已儲存: {report_file}")
        return report_file
        
    except Exception as e:
        logger.error(f"❌ 儲存摘要報告失敗: {e}")
        return None

def update_readme(reports_dir):
    """更新 README 文件"""
    try:
        if not reports_dir.exists():
            logger.warning("⚠️ data 目錄不存在")
            return
        
        # 找到所有報告文件
        md_files = sorted(
            list(reports_dir.glob("*.md")),
            key=lambda x: x.stem,
            reverse=True
        )
        
        if not md_files:
            logger.warning("⚠️ 沒有找到任何報告文件")
            return
        
        # 檢查是否有 README 範本
        template_path = Path("docs/readme_template.md")
        if template_path.exists():
            with open(template_path, 'r', encoding='utf-8') as f:
                template = f.read()
            
            # 生成報告連結
            report_links = []
            for md_file in md_files[:15]:  # 最多顯示 15 個
                date_str = md_file.stem
                link = f"- **{date_str}** 👉 [點擊查看報告](data/{md_file.name})"
                report_links.append(link)
            
            # 更新 README
            readme_content = template.format(
                report_list='\n'.join(report_links),
                last_update=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                total_reports=len(md_files)
            )
            
            with open("README.md", 'w', encoding='utf-8') as f:
                f.write(readme_content)
                
            logger.info("✅ README.md 更新完成")
        else:
            logger.info("ℹ️ 沒有找到 README 範本，跳過更新")
        
    except Exception as e:
        logger.error(f"❌ 更新 README 時發生錯誤: {e}")

def check_environment():
    """檢查環境設定"""
    logger.info("🔍 檢查環境設定...")
    
    issues = []
    
    # 檢查 API 金鑰
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        issues.append("❌ GOOGLE_API_KEY 未設定")
    else:
        logger.info("✅ GOOGLE_API_KEY 已設定")
    
    # 檢查設定檔
    config_file = Path("config/topics.yaml")
    if not config_file.exists():
        issues.append("⚠️ config/topics.yaml 不存在，將使用預設設定")
    else:
        logger.info("✅ topics.yaml 設定檔存在")
    
    # 檢查目錄結構
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    logger.info("✅ data 目錄已準備")
    
    if issues:
        for issue in issues:
            logger.warning(issue)
    
    return len(issues) == 0

def main():
    """主要函數"""
    try:
        logger.info("🚀 開始執行每日 ArXiv 論文處理")
        
        # 檢查環境
        env_ok = check_environment()
        
        # 取得目標日期
        target_date = get_today_date()
        logger.info(f"📅 處理日期: {target_date}")
        
        # 檢查是否強制更新
        force_update = os.getenv('FORCE_UPDATE', '').lower() == 'true'
        
        # 檢查是否已經有今日的報告
        data_dir = Path("data")
        existing_report = data_dir / f"{target_date}.md"
        if existing_report.exists() and not force_update:
            logger.info(f"📄 今日報告已存在: {existing_report}")
            logger.info("💡 使用 FORCE_UPDATE=true 來強制重新生成")
            return
        
        # 初始化爬蟲
        logger.info("🕷️ 初始化 ArXiv 爬蟲...")
        crawler = ArxivCrawler()
        
        # 爬取論文
        logger.info("📡 開始爬取論文...")
        papers = crawler.get_papers(target_date)
        
        if not papers:
            logger.warning("⚠️ 沒有找到任何論文")
            # 仍然生成一個空報告
            summarizer = AISummarizer()
            summary = summarizer._generate_empty_summary()
            save_summary_report(summary, target_date)
            update_readme(data_dir)
            logger.info("📝 已生成空報告")
            return
        
        logger.info(f"📊 成功獲取 {len(papers)} 篇論文")
        
        # 顯示類別統計
        category_stats = crawler.get_paper_categories_stats(papers)
        logger.info("📊 論文類別統計:")
        for category, count in list(category_stats.items())[:5]:
            logger.info(f"   {category}: {count} 篇")
        
        # 儲存原始論文資料
        save_papers_data(papers, target_date)
        
        # 初始化 AI 摘要生成器
        logger.info("🤖 初始化 AI 摘要生成器...")
        summarizer = AISummarizer()
        
        # 生成摘要
        logger.info("✍️ 開始生成摘要...")
        summary = summarizer.generate_summary(papers)
        
        # 儲存摘要報告
        report_file = save_summary_report(summary, target_date)
        
        if report_file:
            # 更新 README
            update_readme(data_dir)
            
            logger.info(f"🎉 處理完成！生成了包含 {len(papers)} 篇論文的摘要報告")
            logger.info(f"📁 報告檔案: {report_file}")
        else:
            logger.error("❌ 儲存報告失敗")
            sys.exit(1)
        
    except KeyboardInterrupt:
        logger.info("⚠️ 使用者中斷程式")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ 執行失敗: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
