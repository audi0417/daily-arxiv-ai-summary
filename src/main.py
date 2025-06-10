#!/usr/bin/env python3
"""
每日 ArXiv 論文智慧摘要 - 主要執行腳本
自動抓取、處理並生成論文摘要報告
"""

import os
import sys
import logging
import yaml
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional

# 新增專案根目錄到 Python 路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 修正導入路徑 - 使用相對導入
try:
    from crawler.arxiv_crawler import ArxivCrawler
    from processor.data_processor import DataProcessor
    from ai.gemini_enhancer import GeminiEnhancer
    from generator.report_generator import ReportGenerator
    from utils.config_loader import ConfigLoader
    from utils.logger import setup_logger
except ImportError:
    # 如果相對導入失敗，嘗試絕對導入
    sys.path.append(str(project_root / "src"))
    from crawler.arxiv_crawler import ArxivCrawler
    from processor.data_processor import DataProcessor
    from ai.gemini_enhancer import GeminiEnhancer
    from generator.report_generator import ReportGenerator
    from utils.config_loader import ConfigLoader
    from utils.logger import setup_logger


class DailyArxivUpdater:
    """每日 ArXiv 更新器主類別"""
    
    def __init__(self):
        """初始化更新器"""
        self.logger = setup_logger("DailyArxivUpdater")
        self.config = ConfigLoader()
        
        # 載入主題設定
        self.topics_config = self._load_topics_config()
        
        # 初始化各個模組
        self.crawler = ArxivCrawler(self.topics_config)
        self.processor = DataProcessor()
        self.ai_enhancer = GeminiEnhancer()
        self.report_generator = ReportGenerator()
        
        # 設定資料目錄
        self.data_dir = project_root / "data"
        self.data_dir.mkdir(exist_ok=True)
        
    def _load_topics_config(self) -> Dict:
        """載入主題設定檔"""
        config_path = project_root / "config" / "topics.yaml"
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            self.logger.info(f"✅ 成功載入主題設定: {len(config.get('categories', []))} 個類別")
            return config
        except FileNotFoundError:
            self.logger.error(f"❌ 找不到主題設定檔: {config_path}")
            # 回傳預設設定
            return {
                'categories': ['cs.AI', 'cs.LG'],
                'keywords': {'include': [], 'exclude': []},
                'limits': {'max_papers_per_day': 50}
            }
        except yaml.YAMLError as e:
            self.logger.error(f"❌ 主題設定檔格式錯誤: {e}")
            sys.exit(1)
    
    def _get_target_date(self) -> str:
        """取得目標日期"""
        # 檢查是否有自訂日期
        custom_date = os.getenv('CUSTOM_DATE', '').strip()
        if custom_date:
            try:
                # 驗證日期格式
                datetime.strptime(custom_date, '%Y-%m-%d')
                self.logger.info(f"📅 使用自訂日期: {custom_date}")
                return custom_date
            except ValueError:
                self.logger.warning(f"⚠️ 自訂日期格式錯誤，使用今日日期: {custom_date}")
        
        # 使用台灣時區的今日日期
        try:
            from zoneinfo import ZoneInfo
            taipei_tz = ZoneInfo("Asia/Taipei")
        except ImportError:
            # fallback for older Python versions
            import pytz
            taipei_tz = pytz.timezone("Asia/Taipei")
        
        today = datetime.now(taipei_tz).strftime('%Y-%m-%d')
        self.logger.info(f"📅 使用今日日期: {today}")
        return today
    
    def _get_previous_days_files(self, target_date: str) -> List[Path]:
        """取得前幾天的資料檔案路徑"""
        target_dt = datetime.strptime(target_date, '%Y-%m-%d')
        previous_files = []
        
        # 檢查前 3 天的檔案
        for i in range(1, 4):
            prev_date = (target_dt - timedelta(days=i)).strftime('%Y-%m-%d')
            prev_file = self.data_dir / f"{prev_date}_unique.jsonl"
            if prev_file.exists():
                previous_files.append(prev_file)
                
        self.logger.info(f"📂 找到 {len(previous_files)} 個歷史檔案用於去重")
        return previous_files
    
    def run(self) -> bool:
        """執行完整的更新流程"""
        try:
            self.logger.info("🚀 開始每日 ArXiv 論文更新流程")
            
            # 1. 確定目標日期
            target_date = self._get_target_date()
            
            # 2. 定義檔案路徑
            raw_file = self.data_dir / f"{target_date}.jsonl"
            unique_file = self.data_dir / f"{target_date}_unique.jsonl"
            new_only_file = self.data_dir / f"{target_date}_new_only.jsonl"
            enhanced_file = self.data_dir / f"{target_date}_new_only_AI_enhanced.jsonl"
            report_file = self.data_dir / f"{target_date}.md"
            
            # 3. 爬取論文資料
            self.logger.info("📊 步驟 1: 爬取論文資料")
            papers = self.crawler.crawl_papers(target_date)
            if not papers:
                self.logger.warning("⚠️ 沒有爬取到任何論文")
                return False
                
            # 儲存原始資料
            self.processor.save_papers(papers, raw_file)
            self.logger.info(f"💾 儲存了 {len(papers)} 篇論文到 {raw_file}")
            
            # 4. 去除重複
            self.logger.info("🔄 步驟 2: 去除重複論文")
            unique_papers = self.processor.deduplicate_papers(papers)
            self.processor.save_papers(unique_papers, unique_file)
            self.logger.info(f"✨ 去重後剩餘 {len(unique_papers)} 篇論文")
            
            # 5. 過濾新論文
            self.logger.info("🆕 步驟 3: 過濾新論文")
            previous_files = self._get_previous_days_files(target_date)
            new_papers = self.processor.filter_new_papers(unique_papers, previous_files)
            
            # 檢查是否強制更新
            force_update = os.getenv('FORCE_UPDATE', 'false').lower() == 'true'
            
            if not new_papers and not force_update:
                self.logger.info("ℹ️ 沒有找到新論文，結束流程")
                # 清理暫存檔案
                raw_file.unlink(missing_ok=True)
                unique_file.unlink(missing_ok=True)
                return False
                
            if force_update and not new_papers:
                self.logger.info("🔄 強制更新模式：使用所有去重後的論文")
                new_papers = unique_papers
                
            self.processor.save_papers(new_papers, new_only_file)
            self.logger.info(f"🎯 過濾出 {len(new_papers)} 篇新論文")
            
            # 6. AI 增強處理
            self.logger.info("🧠 步驟 4: AI 增強處理")
            enhanced_papers = self.ai_enhancer.enhance_papers(new_papers)
            if not enhanced_papers:
                self.logger.error("❌ AI 增強處理失敗")
                return False
                
            self.processor.save_papers(enhanced_papers, enhanced_file)
            self.logger.info(f"✨ AI 增強完成，處理了 {len(enhanced_papers)} 篇論文")
            
            # 7. 生成報告
            self.logger.info("📝 步驟 5: 生成報告")
            success = self.report_generator.generate_report(
                enhanced_papers, 
                report_file, 
                target_date
            )
            
            if not success:
                self.logger.error("❌ 報告生成失敗")
                return False
                
            # 8. 更新主要 README
            self.logger.info("📋 步驟 6: 更新主要 README")
            self._update_main_readme()
            
            self.logger.info("🎉 每日更新流程完成！")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 執行過程中發生錯誤: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return False
    
    def _update_main_readme(self):
        """更新主要的 README.md 檔案"""
        try:
            # 掃描所有 .md 報告檔案
            md_files = sorted(
                [f for f in self.data_dir.glob("*.md")],
                key=lambda x: x.stem,  # 按日期排序
                reverse=True  # 最新的在前面
            )
            
            # 讀取 README 範本
            template_path = project_root / "templates" / "readme_template.md"
            if not template_path.exists():
                self.logger.warning("⚠️ README 範本檔案不存在，跳過更新")
                return
                
            with open(template_path, 'r', encoding='utf-8') as f:
                template = f.read()
            
            # 生成報告連結列表
            report_links = []
            for md_file in md_files[:10]:  # 只顯示最近 10 個報告
                date_str = md_file.stem
                relative_path = f"data/{md_file.name}"
                link = f"- **{date_str}** 👉 [點擊查看報告]({relative_path})"
                report_links.append(link)
            
            # 填入範本
            readme_content = template.format(
                report_list='\n'.join(report_links),
                last_update=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                total_reports=len(md_files)
            )
            
            # 寫入主要 README
            readme_path = project_root / "README.md"
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)
                
            self.logger.info("✅ 主要 README.md 更新完成")
            
        except Exception as e:
            self.logger.error(f"❌ 更新 README 時發生錯誤: {e}")


def main():
    """主要執行函數"""
    try:
        updater = DailyArxivUpdater()
        success = updater.run()
        
        if success:
            print("✅ 每日更新執行成功")
            sys.exit(0)
        else:
            print("⚠️ 沒有新內容需要更新")
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n⏹️ 使用者中斷執行")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 程式執行失敗: {e}")
        logging.exception("執行過程中發生未預期的錯誤")
        sys.exit(1)


if __name__ == "__main__":
    main()