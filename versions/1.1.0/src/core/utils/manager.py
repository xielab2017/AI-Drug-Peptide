#!/usr/bin/env python3
"""
AI-Drug Peptide - 工具模块
包含各种实用工具和辅助功能
"""

import os
import sys
import json
import logging
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

@dataclass
class ToolConfig:
    """工具配置"""
    name: str
    command: str
    version: str
    required: bool = True
    timeout: int = 300
    retries: int = 3

class ToolManager:
    """工具管理器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.tools = {}
        self._load_tool_configs()
    
    def _load_tool_configs(self):
        """加载工具配置"""
        # 默认工具配置
        default_tools = {
            'blast': ToolConfig(
                name='BLAST',
                command='blastp',
                version='2.13.0+',
                required=True
            ),
            'clustalw': ToolConfig(
                name='ClustalW',
                command='clustalw',
                version='2.1',
                required=False
            ),
            'autodock_tools': ToolConfig(
                name='AutoDock Tools',
                command='prepare_receptor4.py',
                version='1.5.7',
                required=False
            ),
            'vina': ToolConfig(
                name='AutoDock Vina',
                command='vina',
                version='1.2.3',
                required=False
            ),
            'signalp': ToolConfig(
                name='SignalP',
                command='signalp',
                version='6.0',
                required=False
            ),
            'tmhmm': ToolConfig(
                name='TMHMM',
                command='tmhmm',
                version='2.0',
                required=False
            )
        }
        
        # 从配置文件加载自定义工具
        custom_tools = self.config.get('tools', {})
        for tool_name, tool_config in custom_tools.items():
            if isinstance(tool_config, dict):
                default_tools[tool_name] = ToolConfig(
                    name=tool_config.get('name', tool_name),
                    command=tool_config.get('command', tool_name),
                    version=tool_config.get('version', 'unknown'),
                    required=tool_config.get('required', False),
                    timeout=tool_config.get('timeout', 300),
                    retries=tool_config.get('retries', 3)
                )
        
        self.tools = default_tools
    
    def check_tool_availability(self, tool_name: str) -> Tuple[bool, str]:
        """检查工具可用性"""
        if tool_name not in self.tools:
            return False, f"Tool '{tool_name}' not configured"
        
        tool_config = self.tools[tool_name]
        
        try:
            # 检查命令是否存在
            result = subprocess.run(
                ['which', tool_config.command],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                # 尝试获取版本信息
                version_result = subprocess.run(
                    [tool_config.command, '--version'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if version_result.returncode == 0:
                    version_info = version_result.stdout.strip()
                    return True, f"Available: {version_info}"
                else:
                    return True, "Available (version check failed)"
            else:
                return False, f"Command '{tool_config.command}' not found in PATH"
                
        except subprocess.TimeoutExpired:
            return False, "Version check timeout"
        except Exception as e:
            return False, f"Error checking tool: {e}"
    
    def check_all_tools(self) -> Dict[str, Tuple[bool, str]]:
        """检查所有工具"""
        results = {}
        for tool_name in self.tools:
            results[tool_name] = self.check_tool_availability(tool_name)
        return results
    
    def get_required_tools_status(self) -> Dict[str, bool]:
        """获取必需工具状态"""
        status = {}
        for tool_name, tool_config in self.tools.items():
            if tool_config.required:
                available, _ = self.check_tool_availability(tool_name)
                status[tool_name] = available
        return status
    
    def run_tool(self, tool_name: str, args: List[str], 
                 input_data: str = None, timeout: int = None) -> Tuple[bool, str, str]:
        """运行工具"""
        if tool_name not in self.tools:
            return False, "", f"Tool '{tool_name}' not configured"
        
        tool_config = self.tools[tool_name]
        timeout = timeout or tool_config.timeout
        
        try:
            # 构建完整命令
            command = [tool_config.command] + args
            
            # 运行命令
            result = subprocess.run(
                command,
                input=input_data,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode == 0:
                return True, result.stdout, result.stderr
            else:
                return False, result.stdout, result.stderr
                
        except subprocess.TimeoutExpired:
            return False, "", f"Tool execution timeout ({timeout}s)"
        except Exception as e:
            return False, "", f"Error running tool: {e}"

class FileManager:
    """文件管理器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.cache_dir = Path(self.config.get('cache_dir', './data/cache'))
        self.output_dir = Path(self.config.get('output_dir', './data/output'))
        self.temp_dir = Path(self.config.get('temp_dir', './data/temp'))
        
        # 创建目录
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
    
    def get_cache_path(self, filename: str) -> Path:
        """获取缓存文件路径"""
        return self.cache_dir / filename
    
    def get_output_path(self, filename: str) -> Path:
        """获取输出文件路径"""
        return self.output_dir / filename
    
    def get_temp_path(self, filename: str) -> Path:
        """获取临时文件路径"""
        return self.temp_dir / filename
    
    def save_json(self, data: Any, filepath: Union[str, Path]) -> Path:
        """保存JSON数据"""
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, default=str, indent=2, ensure_ascii=False)
        
        logger.info(f"JSON data saved: {filepath}")
        return filepath
    
    def load_json(self, filepath: Union[str, Path]) -> Any:
        """加载JSON数据"""
        filepath = Path(filepath)
        
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def save_text(self, text: str, filepath: Union[str, Path]) -> Path:
        """保存文本数据"""
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(text)
        
        logger.info(f"Text data saved: {filepath}")
        return filepath
    
    def load_text(self, filepath: Union[str, Path]) -> str:
        """加载文本数据"""
        filepath = Path(filepath)
        
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    
    def cleanup_temp_files(self, pattern: str = "*"):
        """清理临时文件"""
        temp_files = list(self.temp_dir.glob(pattern))
        for file_path in temp_files:
            try:
                if file_path.is_file():
                    file_path.unlink()
                elif file_path.is_dir():
                    shutil.rmtree(file_path)
                logger.info(f"Cleaned up temp file: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to clean up {file_path}: {e}")

class NetworkManager:
    """网络管理器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """创建HTTP会话"""
        session = requests.Session()
        
        # 配置重试策略
        retry_strategy = Retry(
            total=self.config.get('max_retries', 3),
            backoff_factor=self.config.get('backoff_factor', 1),
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # 设置超时
        session.timeout = self.config.get('timeout', 30)
        
        # 设置用户代理
        session.headers.update({
            'User-Agent': self.config.get('user_agent', 'AI-Drug-Peptide/1.0')
        })
        
        return session
    
    def get(self, url: str, params: Dict[str, Any] = None, 
            headers: Dict[str, str] = None) -> requests.Response:
        """发送GET请求"""
        try:
            response = self.session.get(
                url, 
                params=params, 
                headers=headers,
                timeout=self.config.get('timeout', 30)
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"GET request failed for {url}: {e}")
            raise
    
    def post(self, url: str, data: Any = None, json_data: Any = None,
             headers: Dict[str, str] = None) -> requests.Response:
        """发送POST请求"""
        try:
            response = self.session.post(
                url,
                data=data,
                json=json_data,
                headers=headers,
                timeout=self.config.get('timeout', 30)
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"POST request failed for {url}: {e}")
            raise
    
    def download_file(self, url: str, filepath: Union[str, Path], 
                      chunk_size: int = 8192) -> Path:
        """下载文件"""
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            response = self.session.get(url, stream=True)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
            
            logger.info(f"File downloaded: {filepath}")
            return filepath
            
        except requests.exceptions.RequestException as e:
            logger.error(f"File download failed for {url}: {e}")
            raise

class ValidationUtils:
    """验证工具"""
    
    @staticmethod
    def validate_protein_id(protein_id: str) -> bool:
        """验证蛋白质ID格式"""
        if not protein_id or not isinstance(protein_id, str):
            return False
        
        # 基本格式检查
        if len(protein_id) < 3 or len(protein_id) > 20:
            return False
        
        # 检查是否包含有效字符
        valid_chars = set('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-')
        if not all(c in valid_chars for c in protein_id.upper()):
            return False
        
        return True
    
    @staticmethod
    def validate_species_id(species_id: Union[str, int]) -> bool:
        """验证物种ID"""
        try:
            species_id = int(species_id)
            return 1 <= species_id <= 999999999
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """验证邮箱格式"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_confidence_threshold(threshold: Union[str, float]) -> bool:
        """验证置信度阈值"""
        try:
            threshold = float(threshold)
            return 0.0 <= threshold <= 1.0
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_energy_threshold(threshold: Union[str, float]) -> bool:
        """验证能量阈值"""
        try:
            threshold = float(threshold)
            return -20.0 <= threshold <= 0.0
        except (ValueError, TypeError):
            return False

class ProgressTracker:
    """进度跟踪器"""
    
    def __init__(self, total_steps: int, description: str = "Processing"):
        self.total_steps = total_steps
        self.current_step = 0
        self.description = description
        self.start_time = None
        self.step_times = []
    
    def start(self):
        """开始跟踪"""
        self.start_time = time.time()
        logger.info(f"Starting {self.description}: {self.total_steps} steps")
    
    def update(self, step_name: str = None):
        """更新进度"""
        if self.start_time is None:
            self.start()
        
        self.current_step += 1
        current_time = time.time()
        
        if self.step_times:
            step_duration = current_time - self.step_times[-1]
            self.step_times.append(current_time)
        else:
            self.step_times.append(current_time)
            step_duration = 0
        
        # 计算进度信息
        progress = (self.current_step / self.total_steps) * 100
        elapsed_time = current_time - self.start_time
        avg_time_per_step = elapsed_time / self.current_step
        remaining_steps = self.total_steps - self.current_step
        estimated_remaining_time = remaining_steps * avg_time_per_step
        
        # 记录进度
        step_info = f"Step {self.current_step}/{self.total_steps}"
        if step_name:
            step_info += f" ({step_name})"
        
        logger.info(f"{step_info} - Progress: {progress:.1f}% - "
                   f"Elapsed: {elapsed_time:.1f}s - "
                   f"ETA: {estimated_remaining_time:.1f}s")
    
    def finish(self):
        """完成跟踪"""
        if self.start_time is None:
            return
        
        total_time = time.time() - self.start_time
        logger.info(f"{self.description} completed in {total_time:.1f}s "
                   f"({self.total_steps} steps)")

# 工具工厂类
class ToolFactory:
    """工具工厂"""
    
    @staticmethod
    def create_tool_manager(config: Dict[str, Any] = None) -> ToolManager:
        """创建工具管理器"""
        return ToolManager(config)
    
    @staticmethod
    def create_file_manager(config: Dict[str, Any] = None) -> FileManager:
        """创建文件管理器"""
        return FileManager(config)
    
    @staticmethod
    def create_network_manager(config: Dict[str, Any] = None) -> NetworkManager:
        """创建网络管理器"""
        return NetworkManager(config)
    
    @staticmethod
    def create_progress_tracker(total_steps: int, description: str = "Processing") -> ProgressTracker:
        """创建进度跟踪器"""
        return ProgressTracker(total_steps, description)

# 使用示例
if __name__ == "__main__":
    import time
    
    # 配置示例
    config = {
        'cache_dir': './data/cache',
        'output_dir': './data/output',
        'temp_dir': './data/temp',
        'max_retries': 3,
        'timeout': 30,
        'user_agent': 'AI-Drug-Peptide/1.0'
    }
    
    # 创建工具管理器
    tool_manager = ToolFactory.create_tool_manager(config)
    
    # 检查工具可用性
    print("=== Tool Availability Check ===")
    tool_status = tool_manager.check_all_tools()
    for tool_name, (available, message) in tool_status.items():
        status = "✓" if available else "✗"
        print(f"{status} {tool_name}: {message}")
    
    # 检查必需工具
    print("\n=== Required Tools Status ===")
    required_status = tool_manager.get_required_tools_status()
    for tool_name, available in required_status.items():
        status = "✓" if available else "✗"
        print(f"{status} {tool_name}: {'Available' if available else 'Missing'}")
    
    # 创建文件管理器
    file_manager = ToolFactory.create_file_manager(config)
    
    # 测试文件操作
    print("\n=== File Manager Test ===")
    test_data = {"test": "data", "number": 42}
    json_path = file_manager.save_json(test_data, "test_data.json")
    print(f"✓ JSON saved: {json_path}")
    
    loaded_data = file_manager.load_json(json_path)
    print(f"✓ JSON loaded: {loaded_data}")
    
    # 创建进度跟踪器
    print("\n=== Progress Tracker Test ===")
    progress = ToolFactory.create_progress_tracker(5, "Test Process")
    progress.start()
    
    for i in range(5):
        time.sleep(0.5)  # 模拟处理时间
        progress.update(f"Step {i+1}")
    
    progress.finish()
    
    # 验证工具测试
    print("\n=== Validation Utils Test ===")
    test_cases = [
        ("THBS4", ValidationUtils.validate_protein_id),
        ("9606", ValidationUtils.validate_species_id),
        ("test@example.com", ValidationUtils.validate_email),
        ("0.9", ValidationUtils.validate_confidence_threshold),
        ("-7.0", ValidationUtils.validate_energy_threshold)
    ]
    
    for value, validator in test_cases:
        result = validator(value)
        status = "✓" if result else "✗"
        print(f"{status} {value}: {result}")
    
    print("\n=== All tests completed ===")
