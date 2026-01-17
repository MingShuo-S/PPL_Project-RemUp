"""
RemUp 工具函数
通用工具函数和辅助类
"""

import re
import os
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import hashlib


class RemUpLogger:
    """RemUp 日志记录器"""
    
    def __init__(self, verbose: bool = False, log_file: Optional[Path] = None):
        self.verbose = verbose
        self.log_file = log_file
        self.setup_logging()
    
    def setup_logging(self):
        """设置日志配置"""
        logging.basicConfig(
            level=logging.DEBUG if self.verbose else logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=self._get_handlers()
        )
    
    def _get_handlers(self):
        """获取日志处理器"""
        handlers = [logging.StreamHandler()]
        
        if self.log_file:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
            handlers.append(file_handler)
        
        return handlers
    
    def info(self, message: str):
        """信息日志"""
        if self.verbose:
            print(f"ℹ️  {message}")
        logging.info(message)
    
    def debug(self, message: str):
        """调试日志"""
        if self.verbose:
            print(f"🔍 {message}")
        logging.debug(message)
    
    def warning(self, message: str):
        """警告日志"""
        if self.verbose:
            print(f"⚠️  {message}")
        logging.warning(message)
    
    def error(self, message: str):
        """错误日志"""
        if self.verbose:
            print(f"❌ {message}")
        logging.error(message)
    
    def success(self, message: str):
        """成功日志"""
        if self.verbose:
            print(f"✅ {message}")
        logging.info(f"SUCCESS: {message}")


class FileUtils:
    """文件工具类"""
    
    @staticmethod
    def ensure_directory(path: Path) -> Path:
        """确保目录存在"""
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @staticmethod
    def read_file(file_path: Path, encoding: str = 'utf-8') -> str:
        """读取文件，支持多种编码"""
        encodings = [encoding, 'gbk', 'latin-1', 'utf-16']
        
        for enc in encodings:
            try:
                with open(file_path, 'r', encoding=enc) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
        
        raise UnicodeDecodeError(f"无法解码文件: {file_path}")
    
    @staticmethod
    def write_file(file_path: Path, content: str, encoding: str = 'utf-8') -> Path:
        """写入文件"""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding=encoding) as f:
            f.write(content)
        
        return file_path
    
    @staticmethod
    def copy_directory(src: Path, dst: Path, overwrite: bool = True) -> bool:
        """复制目录"""
        try:
            if dst.exists() and overwrite:
                import shutil
                shutil.rmtree(dst)
            
            import shutil
            shutil.copytree(src, dst)
            return True
        except Exception as e:
            logging.error(f"复制目录失败: {e}")
            return False
    
    @staticmethod
    def get_file_hash(file_path: Path) -> str:
        """计算文件哈希值"""
        if not file_path.exists():
            return ""
        
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        
        return hasher.hexdigest()
    
    @staticmethod
    def find_files(directory: Path, pattern: str = "**/*") -> List[Path]:
        """查找文件"""
        if not directory.exists():
            return []
        return list(directory.glob(pattern))


class TextUtils:
    """文本处理工具类"""
    
    @staticmethod
    def slugify(text: str) -> str:
        """生成URL友好的slug"""
        if not text:
            return ""
        
        # 转换为小写
        text = text.lower().strip()
        
        # 替换非字母数字字符为连字符
        text = re.sub(r'[^\w\s-]', '', text)
        
        # 替换空格和连字符为单个连字符
        text = re.sub(r'[-\s]+', '-', text)
        
        return text
    
    @staticmethod
    def truncate(text: str, length: int = 100, ellipsis: str = "...") -> str:
        """截断文本"""
        if len(text) <= length:
            return text
        return text[:length - len(ellipsis)] + ellipsis
    
    @staticmethod
    def escape_html(text: str) -> str:
        """转义HTML特殊字符"""
        escape_chars = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#39;'
        }
        
        for char, replacement in escape_chars.items():
            text = text.replace(char, replacement)
        
        return text
    
    @staticmethod
    def unescape_html(text: str) -> str:
        """反转义HTML特殊字符"""
        unescape_chars = {
            '&amp;': '&',
            '&lt;': '<',
            '&gt;': '>',
            '&quot;': '"',
            '&#39;': "'"
        }
        
        for entity, char in unescape_chars.items():
            text = text.replace(entity, char)
        
        return text
    
    @staticmethod
    def extract_vibe_cards(text: str) -> List[Dict[str, str]]:
        """从文本中提取注卡"""
        vibe_cards = []
        pattern = r'`([^`]+)`\[([^\]]+)\]'
        
        for match in re.finditer(pattern, text):
            vibe_cards.append({
                'content': match.group(1).strip(),
                'annotation': match.group(2).strip()
            })
        
        return vibe_cards
    
    @staticmethod
    def count_words(text: str) -> int:
        """统计单词数"""
        words = re.findall(r'\b\w+\b', text)
        return len(words)
    
    @staticmethod
    def count_lines(text: str) -> int:
        """统计行数"""
        return len(text.splitlines())


class ConfigUtils:
    """配置工具类"""
    
    @staticmethod
    def load_config(config_file: Path, default_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """加载配置文件"""
        if default_config is None:
            default_config = {}
        
        if not config_file.exists():
            return default_config.copy()
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
            
            # 深度合并配置
            return ConfigUtils.deep_merge(default_config, user_config)
        except Exception as e:
            logging.warning(f"配置文件加载失败 {config_file}: {e}")
            return default_config.copy()
    
    @staticmethod
    def save_config(config_file: Path, config: Dict[str, Any]) -> bool:
        """保存配置文件"""
        try:
            config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logging.error(f"配置文件保存失败 {config_file}: {e}")
            return False
    
    @staticmethod
    def deep_merge(base: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
        """深度合并字典"""
        result = base.copy()
        
        for key, value in update.items():
            if (key in result and isinstance(result[key], dict) 
                and isinstance(value, dict)):
                result[key] = ConfigUtils.deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result


class ValidationUtils:
    """验证工具类"""
    
    @staticmethod
    def validate_file_path(file_path: Path, allowed_extensions: List[str] = None) -> bool:
        """验证文件路径"""
        if allowed_extensions is None:
            allowed_extensions = ['.ru', '.rem', '.rup']
        
        if not file_path.exists():
            return False
        
        if file_path.suffix.lower() not in allowed_extensions:
            return False
        
        return True
    
    @staticmethod
    def validate_directory_path(dir_path: Path) -> bool:
        """验证目录路径"""
        return dir_path.exists() and dir_path.is_dir()
    
    @staticmethod
    def validate_file_size(file_path: Path, max_size_mb: int = 10) -> bool:
        """验证文件大小"""
        if not file_path.exists():
            return False
        
        file_size = file_path.stat().st_size
        max_size = max_size_mb * 1024 * 1024
        
        return file_size <= max_size


class PerformanceUtils:
    """性能工具类"""
    
    @staticmethod
    def timer(func):
        """计时装饰器"""
        import time
        from functools import wraps
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            print(f"⏱️  {func.__name__} 执行时间: {end_time - start_time:.4f}秒")
            return result
        return wrapper
    
@staticmethod
def memory_usage():
    """获取内存使用情况"""
    try:
        import psutil
    except ImportError:
        return None  # 或者 raise RuntimeError("psutil 未安装")
    import os
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024

# 工具函数
def get_version() -> str:
    """获取版本号"""
    try:
        from . import __version__
        return __version__
    except ImportError:
        return "1.0.0"

def get_timestamp() -> str:
    """获取时间戳"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def format_file_size(size_bytes: int) -> str:
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

def create_backup(file_path: Path, backup_dir: Path = None) -> Optional[Path]:
    """创建文件备份"""
    if not file_path.exists():
        return None
    
    if backup_dir is None:
        backup_dir = file_path.parent / "backups"
    
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = backup_dir / f"{file_path.stem}_{timestamp}{file_path.suffix}"
    
    import shutil
    try:
        shutil.copy2(file_path, backup_file)
        return backup_file
    except Exception as e:
        logging.error(f"备份失败 {file_path}: {e}")
        return None

# 导出主要工具类
__all__ = [
    'RemUpLogger',
    'FileUtils', 
    'TextUtils',
    'ConfigUtils',
    'ValidationUtils',
    'PerformanceUtils',
    'get_version',
    'get_timestamp',
    'format_file_size',
    'create_backup'
]