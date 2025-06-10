#!/usr/bin/env python3
"""
簡化的論文處理腳本
避免複雜的模組導入問題
"""

import os
import sys
import json
import time
import logging
import requests
from datetime import datetime, timedelta
from pathlib import Path

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
            pass
    
    # 使用 UTC 日期
    return datetime.utcnow().strftime('%Y-%m-%d')

def create_test_data():
    """創建測試資料"""
    today = get_today_date()
    
    # 建立資料目錄
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # 創建測試報告
    test_report = f"""# 每日 ArXiv 論文智慧摘要: {today}

> 🤖 由 AI 自動生成的論文摘要報告
> 
> 📊 本日共處理 0 篇論文
> 
> 🕒 生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📢 系統狀態

✅ 專案已成功初始化  
⚠️ 正在等待第一次論文資料...

### 🔧 設定檢查

- **API 金鑰**: {'✅ 已設定' if os.getenv('GOOGLE_API_KEY') else '❌ 未設定'}
- **模型名稱**: {os.getenv('MODEL_NAME', 'gemini-2.0-flash-exp')}
- **輸出語言**: {os.getenv('LANGUAGE', 'Traditional Chinese')}

### 🚀 下一步

1. 檢查您的 GitHub Variables 和 Secrets 設定
2. 確認 API 金鑰有效
3. 等待下次自動執行或手動觸發

---

## 📊 本日統計

- **論文總數**: 0
- **處理狀態**: 初始化完成

## 🔗 相關連結

- [ArXiv 官網](https://arxiv.org/)
- [專案 GitHub](https://github.com/audi0417/daily-arxiv-ai-summary)

---

*本報告由 AI 自動生成，如有任何問題請提交 Issue。*
"""
    
    # 寫入測試報告
    report_file = data_dir / f"{today}.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(test_report)
    
    logger.info(f"✅ 已創建測試報告: {report_file}")

def update_readme():
    """更新 README 文件"""
    try:
        # 檢查是否存在 data 目錄中的 .md 文件
        data_dir = Path("data")
        if not data_dir.exists():
            logger.warning("⚠️ data 目錄不存在")
            return
        
        md_files = sorted(
            list(data_dir.glob("*.md")),
            key=lambda x: x.stem,
            reverse=True
        )
        
        if not md_files:
            logger.warning("⚠️ 沒有找到任何報告文件")
            return
        
        # 讀取 README 範本
        template_path = Path("templates/readme_template.md")
        if not template_path.exists():
            logger.warning("⚠️ README 範本不存在，跳過更新")
            return
            
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()
        
        # 生成報告連結
        report_links = []
        for md_file in md_files[:10]:  # 最多顯示 10 個
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
        
    except Exception as e:
        logger.error(f"❌ 更新 README 時發生錯誤: {e}")

def main():
    """主要函數"""
    try:
        logger.info("🚀 開始執行每日 ArXiv 更新")
        
        # 檢查基本設定
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            logger.warning("⚠️ GOOGLE_API_KEY 未設定，將創建測試資料")
        
        # 創建測試資料（後續版本會替換成實際功能）
        create_test_data()
        
        # 更新 README
        update_readme()
        
        logger.info("🎉 執行完成！")
        
    except Exception as e:
        logger.error(f"❌ 執行失敗: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()