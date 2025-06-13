import scrapy
import os
import re


class ArxivSpider(scrapy.Spider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        categories = os.environ.get("CATEGORIES", "cs.AI,cs.LG,cs.CV,cs.CL")
        categories = categories.split(",")
        # 保存目標分類列表，用於後續驗證
        self.target_categories = set(map(str.strip, categories))
        self.start_urls = [
            f"https://arxiv.org/list/{cat}/new" for cat in self.target_categories
        ]  # 起始URL（計算機科學領域的最新論文）

    name = "arxiv"  # 爬蟲名稱
    allowed_domains = ["arxiv.org"]  # 允許爬取的域名

    def parse(self, response):
        # 提取每篇論文的信息
        anchors = []
        for li in response.css("div[id=dlpage] ul li"):
            href = li.css("a::attr(href)").get()
            if href and "item" in href:
                anchors.append(int(href.split("item")[-1]))

        # 遍歷每篇論文的詳細信息
        for paper in response.css("dl dt"):
            paper_anchor = paper.css("a[name^='item']::attr(name)").get()
            if not paper_anchor:
                continue
                
            paper_id = int(paper_anchor.split("item")[-1])
            if anchors and paper_id >= anchors[-1]:
                continue

            # 獲取論文ID
            abstract_link = paper.css("a[title='Abstract']::attr(href)").get()
            if not abstract_link:
                continue
                
            arxiv_id = abstract_link.split("/")[-1]
            
            # 獲取對應的論文描述部分 (dd元素)
            paper_dd = paper.xpath("following-sibling::dd[1]")
            if not paper_dd:
                continue
            
            # 提取論文分類信息 - 在subjects部分
            subjects_text = paper_dd.css(".list-subjects .primary-subject::text").get()
            if not subjects_text:
                # 如果找不到主分類，嘗試其他方式獲取分類
                subjects_text = paper_dd.css(".list-subjects::text").get()
            
            if subjects_text:
                # 解析分類信息，通常格式如 "Computer Vision and Pattern Recognition (cs.CV)"
                # 提取括號中的分類代碼
                categories_in_paper = re.findall(r'\(([^)]+)\)', subjects_text)
                
                # 檢查論文分類是否與目標分類有交集
                paper_categories = set(categories_in_paper)
                if paper_categories.intersection(self.target_categories):
                    yield {
                        "id": arxiv_id,
                        "categories": list(paper_categories),  # 添加分類信息用於調試
                    }
                    self.logger.info(f"Found paper {arxiv_id} with categories {paper_categories}")
                else:
                    self.logger.debug(f"Skipped paper {arxiv_id} with categories {paper_categories} (not in target {self.target_categories})")
            else:
                # 如果無法獲取分類信息，記錄警告但仍然返回論文（保持向後兼容）
                self.logger.warning(f"Could not extract categories for paper {arxiv_id}, including anyway")
                yield {
                    "id": arxiv_id,
                    "categories": [],
                }
