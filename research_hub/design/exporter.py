"""
DesignExporter - 设计结果导出器
导出蛋白/肽设计结果为多种格式
"""

import json
import csv
import os
from typing import List, Dict
from datetime import datetime


class DesignExporter:
    """设计结果导出器"""
    
    def __init__(self, output_dir: str = None):
        """
        初始化导出器
        
        Args:
            output_dir: 输出目录
        """
        self.output_dir = output_dir or os.path.expanduser("~/.openclaw/data/research-hub/designs")
        os.makedirs(self.output_dir, exist_ok=True)
    
    def export_json(
        self, 
        data: List[Dict], 
        filename: str = None
    ) -> str:
        """
        导出为 JSON
        
        Args:
            data: 设计数据
            filename: 文件名
            
        Returns:
            文件路径
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"protein_design_{timestamp}.json"
        
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return filepath
    
    def export_csv(
        self, 
        data: List[Dict], 
        filename: str = None,
        fields: List[str] = None
    ) -> str:
        """
        导出为 CSV
        
        Args:
            data: 设计数据
            filename: 文件名
            fields: 导出字段
            
        Returns:
            文件路径
        """
        if not data:
            raise ValueError("No data to export")
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"protein_design_{timestamp}.csv"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # 确定字段
        if fields is None:
            fields = list(data[0].keys())
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            for row in data:
                writer.writerow({k: row.get(k, '') for k in fields})
        
        return filepath
    
    def export_fasta(
        self, 
        sequences: List[Dict], 
        filename: str = None
    ) -> str:
        """
        导出为 FASTA 格式
        
        Args:
            sequences: 序列列表 [{'id': 'seq1', 'sequence': 'MVLSP...'}, ...]
            filename: 文件名
            
        Returns:
            文件路径
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"protein_design_{timestamp}.fasta"
        
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            for i, item in enumerate(sequences):
                seq_id = item.get('id', f"seq_{i+1}")
                sequence = item.get('sequence', '')
                description = item.get('description', '')
                
                f.write(f">{seq_id} {description}\n")
                
                # 每行60个氨基酸
                for j in range(0, len(sequence), 60):
                    f.write(sequence[j:j+60] + "\n")
        
        return filepath
    
    def export_excel(
        self, 
        data: List[Dict], 
        filename: str = None,
        sheets: Dict[str, List[Dict]] = None
    ) -> str:
        """
        导出为 Excel (需要 openpyxl)
        
        Args:
            data: 数据
            filename: 文件名
            sheets: 多工作表 {'Sheet1': [...], 'Sheet2': [...]}
            
        Returns:
            文件路径
        """
        try:
            import openpyxl
            from openpyxl import Workbook
        except ImportError:
            raise ImportError("openpyxl not installed. Run: pip install openpyxl")
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"protein_design_{timestamp}.xlsx"
        
        filepath = os.path.join(self.output_dir, filename)
        
        wb = Workbook()
        
        if sheets:
            # 多工作表
            wb.remove(wb.active)
            for sheet_name, sheet_data in sheets.items():
                ws = wb.create_sheet(title=sheet_name)
                self._write_sheet(ws, sheet_data)
        else:
            # 单工作表
            ws = wb.active
            ws.title = "Designs"
            self._write_sheet(ws, data)
        
        wb.save(filepath)
        return filepath
    
    def _write_sheet(self, ws, data: List[Dict]):
        """写入工作表"""
        if not data:
            return
        
        # 写入表头
        headers = list(data[0].keys())
        ws.append(headers)
        
        # 写入数据
        for row in data:
            ws.append([row.get(h, '') for h in headers])
    
    def export_summary_report(
        self, 
        designs: List[Dict], 
        evaluations: List[Dict] = None,
        filename: str = None
    ) -> str:
        """
        导出摘要报告 (Markdown)
        
        Args:
            designs: 设计结果
            evaluations: 评估结果
            filename: 文件名
            
        Returns:
            文件路径
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"design_report_{timestamp}.md"
        
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("# Protein Design Report\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write(f"## Summary\n\n")
            f.write(f"- Total Designs: {len(designs)}\n\n")
            
            if evaluations:
                # 统计
                avg_stability = sum(e.get('stability_score', 0) for e in evaluations) / len(evaluations)
                avg_solubility = sum(e.get('solubility_score', 0) for e in evaluations) / len(evaluations)
                
                f.write(f"- Average Stability: {avg_stability:.2f}\n")
                f.write(f"- Average Solubility: {avg_solubility:.2f}\n\n")
            
            f.write("## Designs\n\n")
            for i, design in enumerate(designs, 1):
                f.write(f"### {i}. {design.get('id', f'Design_{i}')}\n\n")
                
                if 'sequence' in design:
                    f.write("**Sequence:**\n```\n")
                    f.write(f"{design['sequence']}\n```\n\n")
                
                if evaluations and i-1 < len(evaluations):
                    eval_result = evaluations[i-1]
                    f.write("**Evaluation:**\n\n")
                    for k, v in eval_result.items():
                        if isinstance(v, float):
                            f.write(f"- {k}: {v:.3f}\n")
                        else:
                            f.write(f"- {k}: {v}\n")
                    f.write("\n")
        
        return filepath
    
    def export_all(
        self, 
        data: List[Dict],
        prefix: str = None
    ) -> Dict[str, str]:
        """
        导出所有格式
        
        Args:
            data: 设计数据
            prefix: 文件名前缀
            
        Returns:
            导出文件路径字典
        """
        prefix = prefix or datetime.now().strftime("%Y%m%d_%H%M%S")
        
        results = {}
        
        # JSON
        results['json'] = self.export_json(data, f"{prefix}.json")
        
        # CSV
        results['csv'] = self.export_csv(data, f"{prefix}.csv")
        
        # FASTA
        sequences = [{'id': d.get('id', f"seq_{i}"), 
                    'sequence': d.get('sequence', '')} 
                   for i, d in enumerate(data)]
        results['fasta'] = self.export_fasta(sequences, f"{prefix}.fasta")
        
        # Report
        results['report'] = self.export_summary_report(data, filename=f"{prefix}_report.md")
        
        return results


# CLI 测试
if __name__ == "__main__":
    exporter = DesignExporter(output_dir="/tmp")
    
    # 测试数据
    test_data = [
        {
            'id': 'AMP_001',
            'sequence': 'KALKKKLLKALKKK',
            'charge': 5,
            'hydrophobicity': 0.35,
            'stability_score': 0.75,
            'solubility_score': 0.82
        },
        {
            'id': 'AMP_002', 
            'sequence': 'RRLFKRGLK',
            'charge': 4,
            'hydrophobicity': 0.28,
            'stability_score': 0.68,
            'solubility_score': 0.88
        }
    ]
    
    print("=== 测试导出 ===")
    
    # 导出 JSON
    path = exporter.export_json(test_data)
    print(f"JSON: {path}")
    
    # 导出 CSV
    path = exporter.export_csv(test_data)
    print(f"CSV: {path}")
    
    # 导出 FASTA
    path = exporter.export_fasta(test_data)
    print(f"FASTA: {path}")
    
    # 导出报告
    path = exporter.export_summary_report(test_data)
    print(f"Report: {path}")
