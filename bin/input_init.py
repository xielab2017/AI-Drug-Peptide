#!/usr/bin/env python3
"""
肽段药物开发 - 输入初始化和参数配置系统
功能：接收用户输入、验证物种ID、生成配置文件、输出分析流程清单
"""

import json
import requests
import re
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import time
from datetime import datetime

class ProteinInputInitializer:
    """蛋白质分析输入初始化和参数配置系统"""
    
    def __init__(self, config_dir: str = "~/.peptide_env"):
        self.config_dir = Path(config_dir).expanduser()
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # NCBI API配置
        self.ncbi_base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
        self.max_retries = 3
        self.request_delay = 0.5  # API请求间隔
        
        # 数据库路径配置
        self.database_paths = {
            "uniprot": "./data/uniprot/",
            "pdb": "./data/pdb/",
            "string": "./data/string/",
            "kegg": "./data/kegg/",
            "pfam": "./data/pfam/",
            "reactome": "./data/reactome/"
        }
        
        # 实验设备API接口（预留）
        self.equipment_apis = {
            "peptide_synthesizer": "http://localhost:8080/api/synthesizer",
            "mass_spectrometer": "http://localhost:8081/api/ms",
            "hplc": "http://localhost:8082/api/hplc",
            "cd_spectrometer": "http://localhost:8083/api/cd"
        }
        
        # 分析目标选项
        self.analysis_options = {
            "1": "分泌路径解析",
            "2": "受体发现", 
            "3": "肽段优化",
            "4": "毒性预测",
            "5": "生物活性评估",
            "6": "稳定性分析"
        }

    def get_user_input(self) -> Dict[str, Any]:
        """获取用户输入"""
        print("🧬 肽段药物开发 - 输入初始化系统")
        print("=" * 60)
        
        input_data = {}
        
        # 1. 蛋白名称输入
        while True:
            protein_name = input("\n🔬 请输入蛋白质名称 (如: THBS4, TNF-α, IL-6): ").strip()
            if self.validate_protein_name(protein_name):
                input_data['protein_name'] = protein_name
                break
            else:
                print("❌ 请输入有效的蛋白质名称（字母、数字、连字符、下划线）")
        
        # 2. 物种ID输入
        print(f"\n🌍 请输入目标物种ID (格式: 物种名+蛋白ID, 多物种用逗号分隔)")
        print("示例: 人NP_003253.1,小鼠NP_035712.1,细菌YP_123456.1")
        
        species_input = input("物种列表: ").strip()
        validated_species = self.get_and_validate_species(species_input)
        input_data['species_data'] = validated_species
        
        # 3. 分析目标选择
        print(f"\n🎯 请选择分析目标 (多选，输入数字序号):")
        for key, value in self.analysis_options.items():
            print(f"  {key}. {value}")
        
        selected_analyses = self.get_analysis_selections()
        input_data['analysis_targets'] = selected_analyses
        
        # 4. 额外配置
        input_data.update(self.get_additional_config())
        
        return input_data

    def validate_protein_name(self, name: str) -> bool:
        """验证蛋白质名称格式"""
        if not name:
            return False
        
        # 允许字母、数字、连字符、下划线、希腊字母等
        pattern = r'^[a-zA-Z0-9αβγδεζηθικλμνξοπρστυφχψωΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ\-_\.\s]+$'
        return bool(re.match(pattern, name))

    def get_and_validate_species(self, species_input: str) -> List[Dict[str, str]]:
        """解析和验证物种ID"""
        species_list = [s.strip() for s in species_input.split(',') if s.strip()]
        validated_species = []
        
        print(f"\n🔍 正在验证 {len(species_list)} 个物种ID...")
        
        for i, species_entry in enumerate(species_list, 1):
            print(f"  验证第 {i}/{len(species_list)} 个: {species_entry}")
            
            parsed_species = self.parse_species_entry(species_entry)
            if parsed_species:
                validation_result = self.validate_ncbi_id(parsed_species['protein_id'])
                
                if validation_result['valid']:
                    parsed_species['validation'] = validation_result
                    validated_species.append(parsed_species)
                    print(f"    ✅ {validation_result['title']} - {validation_result['organism']}")
                else:
                    print(f"    ❌ ID无效: {validation_result.get('error', '未知错误')}")
                    
                    # 自动修正建议
                    corrections = self.suggest_protein_corrections(parsed_species['species'], parsed_species['protein_id'])
                    if corrections:
                        print(f"    💡 建议修正为:")
                        for correction in corrections[:3]:  # 显示前3个建议
                            print(f"      - {correction}")
            else:
                print(f"    ❌ 格式错误: 请使用 '物种名+蛋白ID' 格式")
            
            # API请求间隔
            time.sleep(self.request_delay)
        
        return validated_species

    def parse_species_entry(self, entry: str) -> Optional[Dict[str, str]]:
        """解析物种条目"""
        # 匹配格式: 物种名 + 蛋白ID
        patterns = [
            r'(.+?)([NPGQY]P_\d+\.\d+)',  # NP_123456.1, YP_123456.1等
            r'(.+?)([A-Z]{1,4}\d{5,8}\.?\d*)',  # 其他格式ID
        ]
        
        for pattern in patterns:
            match = re.search(pattern, entry)
            if match:
                species_name = match.group(1).strip()
                protein_id = match.group(2).strip()
                return {
                    'species': species_name,
                    'protein_id': protein_id,
                    'original_entry': entry
                }
        
        return None

    def validate_ncbi_id(self, protein_id: str) -> Dict[str, Any]:
        """验证NCBID蛋白ID"""
        try:
            # 搜索protein数据库
            search_url = f"{self.ncbi_base_url}esearch.fcgi"
            params = {
                'db': 'protein',
                'term': protein_id,
                'retmode': 'json',
                'retmax': 1
            }
            
            response = None
            for attempt in range(self.max_retries):
                try:
                    response = requests.get(search_url, params=params, timeout=10)
                    if response.status_code == 200:
                        break
                    else:
                        time.sleep(self.request_delay)
                except Exception as e:
                    if attempt == self.max_retries - 1:
                        return {'valid': False, 'error': f'网络错误: {str(e)}'}
                    time.sleep(self.request_delay)
            
            if not response or response.status_code != 200:
                return {'valid': False, 'error': 'API请求失败'}
            
            data = response.json()
            
            if 'esearchresult' not in data:
                return {'valid': False, 'error': 'API响应格式错误'}
            
            id_list = data['esearchresult'].get('idlist', [])
            
            if not id_list:
                return {'valid': False, 'error': '未找到对应的蛋白质记录'}
            
            # 获取详细信息
            detail_url = f"{self.ncbi_base_url}efetch.fcgi"
            detail_params = {
                'db': 'protein',
                'id': id_list[0],
                'retmode': 'xml',
                'rettype': 'fasta'
            }
            
            detail_response = None
            for attempt in range(self.max_retries):
                try:
                    detail_response = requests.get(detail_url, params=detail_params, timeout=15)
                    if detail_response.status_code == 200:
                        break
                    else:
                        time.sleep(self.request_delay)
                except Exception as e:
                    if attempt == self.max_retries - 1:
                        return {'valid': False, 'error': f'获取详细信息失败: {str(e)}'}
                    time.sleep(self.request_delay)
            
            if detail_response and detail_response.status_code == 200:
                fasta_data = detail_response.text
                
                # 简单解析FASTA标题
                lines = fasta_data.split('\n')
                for line in lines:
                    if line.startswith('>'):
                        title = line[1:].strip()
                        return {
                            'valid': True,
                            'ncbi_id': id_list[0],
                            'title': title,
                            'organism': self.extract_organism_from_title(title),
                            'length': len(''.join(lines[1:]).replace('\n', ''))
                        }
            
            return {'valid': False, 'error': '解析详细信息失败'}
            
        except Exception as e:
            return {'valid': False, 'error': f'验证过程错误: {str(e)}'}

    def extract_organism_from_title(self, title: str) -> str:
        """从FASTA标题提取物种名"""
        # 简单提取第一个方括号或括号内的内容
        patterns = [
            r'\[([^\]]+)\]',  # [物种名]
            r'\(([^\)]+)\)',  # (物种名)
            r'(\w+)\s*\w*\s*gene',  # 物种名 gene
        ]
        
        for pattern in patterns:
            match = re.search(pattern, title)
            if match:
                org = match.group(1).strip()
                if len(org) > 3:  # 物种名通常较长
                    return org
        
        # 如果没找到，返回前几个词
        words = title.split()
        if len(words) >= 2:
            return f"{words[0]} {words[1]}"
        
        return "未知物种"

    def suggest_protein_corrections(self, species: str, protein_id: str) -> List[str]:
        """为无效ID提供修正建议"""
        try:
            # 基于物种名搜索相关蛋白质
            search_term = f"{species}[organism] AND {protein_id.split('.')[0]}[accession]"
            search_url = f"{self.ncbi_base_url}esearch.fcgi"
            params = {
                'db': 'protein',
                'term': search_term,
                'retmode': 'json',
                'retmax': 5
            }
            
            response = requests.get(search_url, params=params, timeout=10)
            if response.status_code != 200:
                return []
            
            data = response.json()
            if 'esearchresult' not in data:
                return []
            
            suggestions = []
            id_list = data['esearchresult'].get('idlist', [])[:3]
            
            for ncbi_id in id_list:
                detail_url = f"{self.ncbi_base_url}efetch.fcgi"
                detail_params = {
                    'db': 'protein',
                    'id': ncbi_id,
                    'retmode': 'xml',
                    'rettype': 'fasta'
                }
                
                detail_response = requests.get(detail_url, params=detail_params, timeout=10)
                if detail_response.status_code == 200:
                    fasta_data = detail_response.text
                    title_line = None
                    accession_line = None
                    
                    for line in fasta_data.split('\n'):
                        if line.startswith('>'):
                            title_line = line[1:].strip()
                        elif 'VERSION' in line and 'ACCESSION' in line:
                            accession_match = re.search(r'ACCESSION\s+(\S+)', line)
                            if accession_match:
                                accession_line = accession_match.group(1)
                    
                    if title_line and accession_line:
                        org_name = self.extract_organism_from_title(title_line)
                        suggestions.append(f"{org_name} {accession_line}")
                break
            
            return suggestions
            
        except Exception:
            return []

    def get_analysis_selections(self) -> List[str]:
        """获取分析目标选择"""
        while True:
            selections = input("\n请选择分析目标 (多个用逗号分隔，如: 1,3,5): ").strip()
            
            if not selections:
                print("❌ 请至少选择一个分析目标")
                continue
            
            try:
                selected_numbers = [s.strip() for s in selections.split(',')]
                validated_selections = []
                
                for num in selected_numbers:
                    if num in self.analysis_options:
                                validated_selections.append(self.analysis_options[num])
                    else:
                        print(f"❌ 无效选择: {num}")
                        break
                else:
                    # 所有选择都有效
                    return validated_selections
                    
            except Exception:
                print("❌ 输入格式错误，请重新输入")

    def get_additional_config(self) -> Dict[str, Any]:
        """获取额外配置"""
        additional = {}
        
        print(f"\n⚙️  额外配置选项:")
        
        # 优先级设置
        priority = input("设置分析优先级 (high/medium/low，默认: medium): ").strip().lower()
        if priority in ['high', 'medium', 'low']:
            additional['priority'] = priority
        else:
            additional['priority'] = 'medium'
        
        # 输出路径
        output_path = input("指定输出路径 (回车使用默认): ").strip()
        if output_path:
            additional['custom_output_path'] = Path(output_path).resolve()
        
        # 邮件通知
        email = input("邮箱通知地址 (可选): ").strip()
        if email and '@' in email:
            additional['notification_email'] = email
        
        return additional

    def generate_config_json(self, input_data: Dict[str, Any]) -> Path:
        """生成配置文件"""
        config = {
            "project_info": {
                "protein_name": input_data['protein_name'],
                "created_time": datetime.now().isoformat(),
                "version": "1.0"
            },
            "species_data": input_data['species_data'],
            "analysis_targets": input_data['analysis_targets'],
            "priority": input_data.get('priority', 'medium'),
            "database_paths": self.database_paths,
            "equipment_apis": self.equipment_apis,
            "output_settings": {
                "default_path": str(Path.home() / "peptide_analysis_results"),
                "custom_path": input_data.get('custom_output_path'),
                "formats": ["json", "pdf", "excel"],
                "images_format": "png"
            },
            "notification": {
                "email": input_data.get('notification_email'),
                "webhook_url": None
            },
            "advanced_settings": {
                "api_timeout": 30,
                "max_retries": 3,
                "parallel_processing": True,
                "cache_results": True
            }
        }
        
        config_file = self.config_dir / f"{input_data['protein_name'].lower()}_config.json"
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 配置文件已生成: {config_file}")
        return config_file

    def generate_analysis_workflow(self, input_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成分析流程清单"""
        workflow = []
        
        protein_name = input_data['protein_name']
        analysis_targets = input_data['analysis_targets']
        species_count = len(input_data['species_data'])
        
        # 通用预处理步骤
        workflow.append({
            "step": 1,
            "task": "数据收集和验证",
            "description": f"收集 {protein_name} 的多物种序列数据",
            "dependencies": [],
            "estimated_time": "2-5分钟",
            "status": "待开始"
        })
        
        workflow.append({
            "step": 2,
            "task": "序列比对和保守性分析",
            "description": f"分析 {protein_name} 在{species_count}个物种间的保守性",
            "dependencies": [1],
            "estimated_time": "5-10分钟",
            "status": "待开始"
        })
        
        # 根据分析目标添加步骤
        step_counter = 3
        
        if "分泌路径解析" in analysis_targets:
            workflow.append({
                "step": step_counter,
                "task": "分泌路径预测",
                "description": f"使用SignalP-6分析 {protein_name} 的信号肽和分泌特性",
                "dependencies": [1, 2],
                "estimated_time": "3-5分钟",
                "status": "待开始",
                "tools": ["SignalP-6", "PSORTb", "SecretP"]
            })
            step_counter += 1
        
        if "受体发现" in analysis_targets:
            workflow.append({
                "step": step_counter,
                "task": "受体相互作用预测",
                "description": f"预测 {protein_name} 可能结合的受体和相互作用位点",
                "dependencies": [1, 2],
                "estimated_time": "10-15分钟",
                "status": "待开始",
                "tools": ["STRING", "HINTdb", "Interactome3D"]
            })
            workflow.append({
                "step": step_counter + 1,
                "task": "受体-配体结合模型",
                "description": f"构建 {protein_name} 与受体蛋白的结合模型",
                "dependencies": [step_counter],
                "estimated_time": "15-30分钟",
                "status": "待开始",
                "tools": ["AutoDock Vina", "PyMOL"]
            })
            step_counter += 2
        
        if "肽段优化" in analysis_targets:
            workflow.append({
                "step": step_counter,
                "task": "肽段设计优化",
                "description": f"基于保守性分析设计优化的 {protein_name} 肽段",
                "dependencies": [1, 2],
                "estimated_time": "20-40分钟",
                "status": "待开始",
                "tools": ["ProGen2", "AlphaFold2", "Rosetta"]
            })
            workflow.append({
                "step": step_counter + 1,
                "task": "生物活性评分",
                "description": f"评估优化后肽段的生物活性和功能评分",
                "dependencies": [step_counter],
                "estimated_time": "10-20分钟",
                "status": "待开始",
                "tools": ["Bio-Activity-Predictor", "QSAR"]
            })
            step_counter += 2
        
        if "毒性预测" in analysis_targets:
            workflow.append({
                "step": step_counter,
                "task": "毒性评估",
                "description": f"预测 {protein_name} 肽段的潜在毒性和副作用",
                "dependencies": [2],
                "estimated_time": "5-10分钟",
                "status": "待开始",
                "tools": ["ToxPred", "ADMET-SAR"]
            })
            step_counter += 1
        
        if "生物活性评估" in analysis_targets:
            workflow.append({
                "step": step_counter,
                "task": "生物活性预测",
                "description": f"预测 {protein_name} 肽段的生物活性和药理作用",
                "dependencies": [2],
                "estimated_time": "10-15分钟",
                "status": "待开始",
                "tools": ["ChEMBL", "PADIF", "Activity-Predictor"]
            })
            step_counter += 1
        
        if "稳定性分析" in analysis_targets:
            workflow.append({
                "step": step_counter,
                "task": "稳定性预测",
                "description": f"分析 {protein_name} 肽段的结构稳定性和降解特性",
                "dependencies": [2],
                "estimated_time": "8-12分钟",
                "status": "待开始",
                "tools": ["FoldX", "PELE", "GROMACS"]
            })
            step_counter += 1
        
        # 通用后处理步骤
        workflow.append({
            "step": step_counter,
            "task": "结果整合与报告生成",
            "description": f"整合所有分析结果，生成 {protein_name} 的综合分析报告",
            "dependencies": list(range(step_counter)),
            "estimated_time": "5-10分钟",
            "status": "待开始",
            "tools": ["ReportLab", "Matplotlib", "Streamlit"]
        })
        
        return workflow

    def display_workflow_summary(self, workflow: List[Dict[str, Any]]):
        """显示流程启动清单"""
        print(f"\n📋 分析流程启动清单")
        print("=" * 80)
        
        total_steps = len(workflow)
        estimated_total_time = 0
        
        for step_info in workflow:
            step = step_info['step']
            task = step_info['task']
            desc = step_info['description']
            deps = step_info['dependencies']
            time_est = step_info['estimated_time']
            tools = step_info.get('tools', [])
            
            print(f"\n{step:2d}. {task}")
            print(f"    📝 {desc}")
            
            if deps:
                dep_str = ', '.join([f"步骤{d}" for d in deps])
                print(f"    📌 依赖: {dep_str}")
            
            print(f"    ⏱️  预计时间: {time_est}")
            
            if tools:
                tools_str = ', '.join(tools)
                print(f"    🛠️  使用工具: {tools_str}")
            
            print(f"    📊 状态: {step_info['status']}")
        
        # 统计信息
        print(f"\n📊 流程统计:")
        print(f"    总步骤数: {total_steps}")
        print(f"    分析目标: {', '.join(self.analysis_targets)}")
        
        # 预估总体时间
        time_ranges = []
        for step in workflow:
            time_str = step['estimated_time']
            if '-' in time_str and '分钟' in time_str:
                min_time, max_time = map(int, time_str.replace('分钟', '').split('-'))
                time_ranges.append((min_time, max_time))
        
        if time_ranges:
            total_min = sum(r[0] for r in time_ranges)
            total_max = sum(r[1] for r in time_ranges)
            print(f"    预计总时间: {total_min}-{total_max}分钟")
        
        print(f"\n🚀 准备启动分析流程!")

    def run(self):
        """运行输入初始化系统"""
        try:
            # 获取用户输入
            input_data = self.get_user_input()
            
            # 生成配置文件
            config_file = self.generate_config_json(input_data)
            
            # 生成分析流程
            workflow = self.generate_analysis_workflow(input_data)
            
            # 显示流程清单
            self.display_workflow_summary(workflow)
            
            # 保存流程配置
            workflow_file = self.config_dir / f"{input_data['protein_name'].lower()}_workflow.json"
            with open(workflow_file, 'w', encoding='utf-8') as f:
                json.dump(workflow, f, ensure_ascii=False, indent=2)
            
            print(f"\n✅ 流程配置已保存: {workflow_file}")
            print(f"\n🎯 下一步: 运行分析脚本开始处理!")
            print(f"   配置文件: {config_file}")
            print(f"   流程文件: {workflow_file}")
            
            return {
                'config_file': config_file,
                'workflow_file': workflow_file,
                'input_data': input_data,
                'workflow': workflow
            }
            
        except KeyboardInterrupt:
            print(f"\n\n⏹️  用户取消操作")
            return None
        except Exception as e:
            print(f"\n❌ 系统错误: {str(e)}")
            return None

def main():
    """主函数"""
    initializer = ProteinInputInitializer()
    result = initializer.run()
    
    if result:
        print(f"\n🎉 输入初始化完成!")
        print(f"📁 配置文件: {result['config_file']}")
        print(f"📋 流程文件: {result['workflow_file']}")
        
        # 返回结果以便后续脚本使用
        return result
    else:
        print(f"\n❌ 初始化失败")
        return None

if __name__ == "__main__":
    main()
