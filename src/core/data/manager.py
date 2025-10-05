#!/usr/bin/env python3
"""
AI-Drug Peptide - 核心数据管理模块
统一的数据验证、缓存、文件和数据库管理
"""

import os
import json
import yaml
import logging
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# 数据库相关
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False

# Neo4j相关
try:
    from py2neo import Graph
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False

# Redis缓存
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    """数据验证结果"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    data: Optional[Dict[str, Any]] = None

@dataclass
class CacheEntry:
    """缓存条目"""
    key: str
    value: Any
    created_at: datetime
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class DataValidator:
    """统一的数据验证器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.validation_rules = self._load_validation_rules()
    
    def _load_validation_rules(self) -> Dict[str, Any]:
        """加载验证规则"""
        return {
            'protein_id': {
                'pattern': r'^[A-Z0-9_\-\.]+$',
                'min_length': 1,
                'max_length': 50
            },
            'species_id': {
                'type': int,
                'min_value': 1,
                'max_value': 999999
            },
            'sequence': {
                'pattern': r'^[ACDEFGHIKLMNPQRSTVWY]+$',
                'min_length': 10,
                'max_length': 10000
            },
            'confidence_threshold': {
                'type': float,
                'min_value': 0.0,
                'max_value': 1.0
            }
        }
    
    def validate_protein_input(self, data: Dict[str, Any]) -> ValidationResult:
        """验证蛋白质输入数据"""
        errors = []
        warnings = []
        
        # 必需字段检查
        required_fields = ['protein_id', 'species_id']
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        
        # 字段验证
        if 'protein_id' in data:
            protein_id = data['protein_id']
            if not isinstance(protein_id, str):
                errors.append("protein_id must be a string")
            elif len(protein_id) < self.validation_rules['protein_id']['min_length']:
                errors.append(f"protein_id too short (min: {self.validation_rules['protein_id']['min_length']})")
            elif len(protein_id) > self.validation_rules['protein_id']['max_length']:
                errors.append(f"protein_id too long (max: {self.validation_rules['protein_id']['max_length']})")
        
        if 'species_id' in data:
            species_id = data['species_id']
            if not isinstance(species_id, int):
                errors.append("species_id must be an integer")
            elif species_id < self.validation_rules['species_id']['min_value']:
                errors.append(f"species_id too small (min: {self.validation_rules['species_id']['min_value']})")
        
        if 'sequence' in data:
            sequence = data['sequence']
            if not isinstance(sequence, str):
                errors.append("sequence must be a string")
            elif len(sequence) < self.validation_rules['sequence']['min_length']:
                warnings.append(f"sequence very short (min recommended: {self.validation_rules['sequence']['min_length']})")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            data=data if len(errors) == 0 else None
        )
    
    def validate_analysis_parameters(self, params: Dict[str, Any]) -> ValidationResult:
        """验证分析参数"""
        errors = []
        warnings = []
        
        # 置信度阈值验证
        if 'confidence_threshold' in params:
            threshold = params['confidence_threshold']
            if not isinstance(threshold, (int, float)):
                errors.append("confidence_threshold must be a number")
            elif threshold < 0.0 or threshold > 1.0:
                errors.append("confidence_threshold must be between 0.0 and 1.0")
            elif threshold < 0.5:
                warnings.append("Low confidence threshold may result in many false positives")
        
        # 物种ID验证
        if 'species_id' in params:
            species_id = params['species_id']
            if not isinstance(species_id, int):
                errors.append("species_id must be an integer")
            elif species_id not in [9606, 10090, 10116]:  # 人、小鼠、大鼠
                warnings.append(f"Uncommon species ID: {species_id}")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            data=params if len(errors) == 0 else None
        )
    
    def validate_output_format(self, format: str) -> ValidationResult:
        """验证输出格式"""
        valid_formats = ['json', 'csv', 'excel', 'xml', 'yaml']
        
        if format.lower() not in valid_formats:
            return ValidationResult(
                is_valid=False,
                errors=[f"Invalid output format: {format}. Supported formats: {', '.join(valid_formats)}"],
                warnings=[]
            )
        
        return ValidationResult(
            is_valid=True,
            errors=[],
            warnings=[],
            data={'format': format.lower()}
        )

class CacheManager:
    """智能缓存管理器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.cache_dir = Path(self.config.get('cache_dir', './data/cache'))
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化Redis客户端（如果可用）
        self.redis_client = None
        if REDIS_AVAILABLE and self.config.get('redis', {}).get('enabled', False):
            try:
                redis_config = self.config['redis']
                self.redis_client = redis.Redis(
                    host=redis_config.get('host', 'localhost'),
                    port=redis_config.get('port', 6379),
                    db=redis_config.get('db', 0),
                    decode_responses=True
                )
                # 测试连接
                self.redis_client.ping()
                logger.info("Redis cache initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize Redis cache: {e}")
                self.redis_client = None
        
        # 内存缓存
        self.memory_cache: Dict[str, CacheEntry] = {}
        self.max_memory_entries = self.config.get('max_memory_entries', 1000)
    
    def _generate_cache_key(self, prefix: str, *args) -> str:
        """生成缓存键"""
        key_data = f"{prefix}:{':'.join(str(arg) for arg in args)}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存数据"""
        # 首先尝试Redis
        if self.redis_client:
            try:
                cached_data = self.redis_client.get(key)
                if cached_data:
                    return json.loads(cached_data)
            except Exception as e:
                logger.warning(f"Redis get error: {e}")
        
        # 然后尝试内存缓存
        if key in self.memory_cache:
            entry = self.memory_cache[key]
            if entry.expires_at is None or entry.expires_at > datetime.now():
                return entry.value
            else:
                del self.memory_cache[key]
        
        # 最后尝试文件缓存
        cache_file = self.cache_dir / f"{key}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 检查过期时间
                    if 'expires_at' in data:
                        expires_at = datetime.fromisoformat(data['expires_at'])
                        if expires_at < datetime.now():
                            cache_file.unlink()
                            return None
                    return data.get('value')
            except Exception as e:
                logger.warning(f"File cache read error: {e}")
        
        return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """设置缓存数据"""
        expires_at = datetime.now() + timedelta(seconds=ttl)
        
        # 尝试Redis
        if self.redis_client:
            try:
                self.redis_client.setex(key, ttl, json.dumps(value, default=str))
                return True
            except Exception as e:
                logger.warning(f"Redis set error: {e}")
        
        # 内存缓存
        entry = CacheEntry(
            key=key,
            value=value,
            created_at=datetime.now(),
            expires_at=expires_at
        )
        
        # 检查内存缓存大小
        if len(self.memory_cache) >= self.max_memory_entries:
            # 删除最旧的条目
            oldest_key = min(self.memory_cache.keys(), 
                           key=lambda k: self.memory_cache[k].created_at)
            del self.memory_cache[oldest_key]
        
        self.memory_cache[key] = entry
        
        # 文件缓存
        try:
            cache_file = self.cache_dir / f"{key}.json"
            cache_data = {
                'value': value,
                'created_at': datetime.now().isoformat(),
                'expires_at': expires_at.isoformat()
            }
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, default=str, indent=2)
        except Exception as e:
            logger.warning(f"File cache write error: {e}")
        
        return True
    
    def invalidate(self, pattern: str) -> int:
        """使缓存失效"""
        invalidated_count = 0
        
        # Redis模式匹配
        if self.redis_client:
            try:
                keys = self.redis_client.keys(pattern)
                if keys:
                    invalidated_count += self.redis_client.delete(*keys)
            except Exception as e:
                logger.warning(f"Redis invalidate error: {e}")
        
        # 内存缓存模式匹配
        keys_to_remove = [k for k in self.memory_cache.keys() if pattern in k]
        for key in keys_to_remove:
            del self.memory_cache[key]
            invalidated_count += 1
        
        # 文件缓存模式匹配
        for cache_file in self.cache_dir.glob(f"*{pattern}*"):
            try:
                cache_file.unlink()
                invalidated_count += 1
            except Exception as e:
                logger.warning(f"File cache delete error: {e}")
        
        return invalidated_count
    
    def clear_expired(self) -> int:
        """清理过期缓存"""
        cleared_count = 0
        now = datetime.now()
        
        # 清理内存缓存
        expired_keys = [
            k for k, v in self.memory_cache.items()
            if v.expires_at and v.expires_at < now
        ]
        for key in expired_keys:
            del self.memory_cache[key]
            cleared_count += 1
        
        # 清理文件缓存
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'expires_at' in data:
                        expires_at = datetime.fromisoformat(data['expires_at'])
                        if expires_at < now:
                            cache_file.unlink()
                            cleared_count += 1
            except Exception as e:
                logger.warning(f"File cache cleanup error: {e}")
        
        return cleared_count

class FileManager:
    """文件管理器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.base_dir = Path(self.config.get('base_dir', './data'))
        self.input_dir = self.base_dir / 'input'
        self.output_dir = self.base_dir / 'output'
        self.temp_dir = self.base_dir / 'temp'
        
        # 创建目录
        for directory in [self.input_dir, self.output_dir, self.temp_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def save_data(self, data: Any, filename: str, format: str = 'json') -> Path:
        """保存数据到文件"""
        file_path = self.output_dir / f"{filename}.{format}"
        
        try:
            if format.lower() == 'json':
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, default=str, indent=2, ensure_ascii=False)
            elif format.lower() == 'csv':
                if isinstance(data, pd.DataFrame):
                    data.to_csv(file_path, index=False, encoding='utf-8')
                else:
                    pd.DataFrame(data).to_csv(file_path, index=False, encoding='utf-8')
            elif format.lower() == 'yaml':
                with open(file_path, 'w', encoding='utf-8') as f:
                    yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            logger.info(f"Data saved to: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Failed to save data to {file_path}: {e}")
            raise
    
    def load_data(self, filename: str, format: str = 'json') -> Any:
        """从文件加载数据"""
        file_path = self.input_dir / f"{filename}.{format}"
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            if format.lower() == 'json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            elif format.lower() == 'csv':
                return pd.read_csv(file_path, encoding='utf-8')
            elif format.lower() == 'yaml':
                with open(file_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
            else:
                raise ValueError(f"Unsupported format: {format}")
                
        except Exception as e:
            logger.error(f"Failed to load data from {file_path}: {e}")
            raise
    
    def create_temp_file(self, suffix: str = '.tmp') -> Path:
        """创建临时文件"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        temp_file = self.temp_dir / f"temp_{timestamp}{suffix}"
        return temp_file
    
    def cleanup_temp_files(self, older_than_hours: int = 24) -> int:
        """清理临时文件"""
        cutoff_time = datetime.now() - timedelta(hours=older_than_hours)
        cleaned_count = 0
        
        for temp_file in self.temp_dir.glob("temp_*"):
            try:
                if temp_file.stat().st_mtime < cutoff_time.timestamp():
                    temp_file.unlink()
                    cleaned_count += 1
            except Exception as e:
                logger.warning(f"Failed to delete temp file {temp_file}: {e}")
        
        return cleaned_count

class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.pg_engine = None
        self.neo4j_graph = None
        
        if DATABASE_AVAILABLE:
            self._init_postgresql()
        
        if NEO4J_AVAILABLE:
            self._init_neo4j()
    
    def _init_postgresql(self):
        """初始化PostgreSQL连接"""
        pg_config = self.config.get('postgresql', {})
        if not pg_config:
            logger.warning("PostgreSQL configuration not found")
            return
        
        try:
            connection_string = (
                f"postgresql://{pg_config['user']}:{pg_config['password']}"
                f"@{pg_config['host']}:{pg_config['port']}"
                f"/{pg_config['database']}"
            )
            self.pg_engine = create_engine(connection_string, pool_pre_ping=True)
            logger.info("PostgreSQL connection initialized")
        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL: {e}")
    
    def _init_neo4j(self):
        """初始化Neo4j连接"""
        neo4j_config = self.config.get('neo4j', {})
        if not neo4j_config:
            logger.warning("Neo4j configuration not found")
            return
        
        try:
            self.neo4j_graph = Graph(
                uri=neo4j_config['uri'],
                user=neo4j_config['user'],
                password=neo4j_config['password']
            )
            # 测试连接
            self.neo4j_graph.run("RETURN 1").data()
            logger.info("Neo4j connection initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Neo4j: {e}")
    
    def execute_query(self, query: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """执行PostgreSQL查询"""
        if not self.pg_engine:
            raise RuntimeError("PostgreSQL not initialized")
        
        try:
            with self.pg_engine.connect() as conn:
                result = conn.execute(text(query), params or {})
                return [dict(row._mapping) for row in result]
        except Exception as e:
            logger.error(f"PostgreSQL query error: {e}")
            raise
    
    def execute_neo4j_query(self, query: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """执行Neo4j查询"""
        if not self.neo4j_graph:
            raise RuntimeError("Neo4j not initialized")
        
        try:
            return self.neo4j_graph.run(query, params or {}).data()
        except Exception as e:
            logger.error(f"Neo4j query error: {e}")
            raise
    
    def save_analysis_result(self, result: Dict[str, Any], table_name: str = 'analysis_results') -> bool:
        """保存分析结果到PostgreSQL"""
        if not self.pg_engine:
            raise RuntimeError("PostgreSQL not initialized")
        
        try:
            # 添加时间戳
            result['created_at'] = datetime.now().isoformat()
            
            # 构建插入查询
            columns = ', '.join(result.keys())
            placeholders = ', '.join([f':{key}' for key in result.keys()])
            query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            
            with self.pg_engine.connect() as conn:
                conn.execute(text(query), result)
                conn.commit()
            
            logger.info(f"Analysis result saved to {table_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save analysis result: {e}")
            return False
    
    def get_analysis_history(self, protein_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """获取分析历史"""
        query = """
        SELECT * FROM analysis_results 
        WHERE protein_id = :protein_id 
        ORDER BY created_at DESC 
        LIMIT :limit
        """
        return self.execute_query(query, {'protein_id': protein_id, 'limit': limit})

# 数据管理模块的工厂类
class DataManagerFactory:
    """数据管理器工厂"""
    
    @staticmethod
    def create_validator(config: Dict[str, Any] = None) -> DataValidator:
        """创建数据验证器"""
        return DataValidator(config)
    
    @staticmethod
    def create_cache_manager(config: Dict[str, Any] = None) -> CacheManager:
        """创建缓存管理器"""
        return CacheManager(config)
    
    @staticmethod
    def create_file_manager(config: Dict[str, Any] = None) -> FileManager:
        """创建文件管理器"""
        return FileManager(config)
    
    @staticmethod
    def create_database_manager(config: Dict[str, Any] = None) -> DatabaseManager:
        """创建数据库管理器"""
        return DatabaseManager(config)

# 使用示例
if __name__ == "__main__":
    # 配置示例
    config = {
        'cache_dir': './data/cache',
        'base_dir': './data',
        'redis': {
            'enabled': True,
            'host': 'localhost',
            'port': 6379,
            'db': 0
        },
        'postgresql': {
            'host': 'localhost',
            'port': 5432,
            'database': 'peptide_db',
            'user': 'postgres',
            'password': 'password'
        },
        'neo4j': {
            'uri': 'bolt://localhost:7687',
            'user': 'neo4j',
            'password': 'password'
        }
    }
    
    # 创建管理器实例
    validator = DataManagerFactory.create_validator()
    cache_manager = DataManagerFactory.create_cache_manager(config)
    file_manager = DataManagerFactory.create_file_manager(config)
    db_manager = DataManagerFactory.create_database_manager(config)
    
    # 使用示例
    protein_data = {
        'protein_id': 'THBS4',
        'species_id': 9606,
        'sequence': 'MKWVTFISLLFLFSSAYSRGVFRRDAHKSEVAHRFKDLGEENFKALVLIAFAQYLQQCPFEDHVKLVNEVTEFAKTCVADESAENCDKSLHTLFGDKLCTVATLRETYGEMADCCAKQEPERNECFLQHKDDNPNLPRLVRPEVDVMCTAFHDNEETFLKKYLYEIARRHPYFYAPELLFFAKRYKAAFTECCQAADKAACLLPKLDELRDEGKASSAKQRLKCASLQKFGERAFKAWAVARLSQRFPKAEFAEVSKLVTDLTKVHTECCHGDLLECADDRADLAKYICENQDSISSKLKECCEKPLLEKSHCIAEVENDEMPADLPSLAADFVESKDVCKNYAEAKDVFLGMFLYEYARRHPDYSVVLLLRLAKTYETTLEKCCAAADPHECYAKVFDEFKPLVEEPQNLIKQNCELFEQLGEYKFQNALLVRYTKKVPQVSTPTLVEVSRNLGKVGSKCCKHPEAKRMPCAEDYLSVVLNQLCVLHEKTPVSDRVTKCCTESLVNRRPCFSALEVDETYVPKEFNAETFTFHADICTLSEKERQIKKQTALVELVKHKPKATKEQLKAVMDDFAAFVEKCCKADDKETCFAEEGKKLVAASQAALGL'
    }
    
    # 数据验证
    validation_result = validator.validate_protein_input(protein_data)
    if validation_result.is_valid:
        print("✓ Protein data validation passed")
        
        # 缓存数据
        cache_key = cache_manager._generate_cache_key('protein', protein_data['protein_id'])
        cache_manager.set(cache_key, protein_data, ttl=3600)
        
        # 保存到文件
        file_manager.save_data(protein_data, 'protein_data', 'json')
        
        print("✓ Data management operations completed successfully")
    else:
        print("✗ Validation failed:", validation_result.errors)
