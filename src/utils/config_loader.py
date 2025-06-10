"""
配置載入器
載入和管理專案配置
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any


class ConfigLoader:
    """配置載入器類別"""
    
    def __init__(self, config_dir: Path = None):
        """初始化配置載入器"""
        if config_dir is None:
            # 預設配置目錄
            project_root = Path(__file__).parent.parent.parent
            self.config_dir = project_root / "config"
        else:
            self.config_dir = config_dir
        
        print(f"⚙️ 配置載入器初始化: {self.config_dir}")
    
    def load_yaml(self, filename: str) -> Dict[str, Any]:
        """載入 YAML 配置檔案"""
        config_path = self.config_dir / filename
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            print(f"✅ 成功載入配置: {filename}")
            return config or {}
            
        except FileNotFoundError:
            print(f"⚠️ 配置檔案不存在: {config_path}")
            return {}
        except yaml.YAMLError as e:
            print(f"❌ YAML 解析錯誤: {e}")
            return {}
        except Exception as e:
            print(f"❌ 載入配置時發生錯誤: {e}")
            return {}
    
    def get_env_config(self) -> Dict[str, str]:
        """取得環境變數配置"""
        return {
            'google_api_key': os.getenv('GOOGLE_API_KEY', ''),
            'model_name': os.getenv('MODEL_NAME', 'gemini-2.0-flash-exp'),
            'language': os.getenv('LANGUAGE', 'Traditional Chinese'),
            'custom_date': os.getenv('CUSTOM_DATE', ''),
            'force_update': os.getenv('FORCE_UPDATE', 'false').lower() == 'true'
        }
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """驗證配置的完整性"""
        required_fields = ['categories']
        
        for field in required_fields:
            if field not in config:
                print(f"❌ 配置缺少必要欄位: {field}")
                return False
        
        # 驗證類別格式
        categories = config.get('categories', [])
        if not isinstance(categories, list) or not categories:
            print("❌ 類別配置必須是非空列表")
            return False
        
        print("✅ 配置驗證通過")
        return True