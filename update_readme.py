#!/usr/bin/env python3
"""
Update README with latest reports
"""

import os
from pathlib import Path
import re
from datetime import datetime

def update_readme():
    """Update README with latest report links"""
    data_dir = Path("data")
    if not data_dir.exists():
        return
    
    # Find all markdown files
    md_files = sorted(list(data_dir.glob("*.md")), reverse=True)
    
    if not md_files:
        return
    
    # Generate report links
    report_links = []
    for md_file in md_files[:10]:  # Latest 10 reports
        date_str = md_file.stem
        link = f"- [{date_str}](data/{md_file.name})"
        report_links.append(link)
    
    # Update README
    readme_path = Path("README.md")
    if readme_path.exists():
        content = readme_path.read_text()
        
        # Find and replace the reports section
        pattern = r"(<!-- REPORTS START -->).*?(<!-- REPORTS END -->)"
        replacement = f"\\1\n{chr(10).join(report_links)}\n\\2"
        
        updated_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        
        if updated_content != content:
            readme_path.write_text(updated_content)
            print(f"Updated README with {len(md_files)} reports")

if __name__ == "__main__":
    update_readme()