"""
SequenceEvaluator - 序列评估器
评估蛋白/肽序列的稳定性, 溶解度, 疏水性等性质
"""

import re
from typing import Dict, List


class SequenceEvaluator:
    """蛋白/肽序列评估器"""
    
    def __init__(self):
        # 氨基酸理化性质
        self.aa_properties = {
            # 疏水性 (Kyte-Doolittle scale)
            'A': 1.8, 'R': -4.5, 'N': -3.5, 'D': -3.5, 'C': 2.5,
            'Q': -3.5, 'E': -3.5, 'G': -0.4, 'H': -3.2, 'I': 4.5,
            'L': 3.8, 'K': -3.9, 'M': 1.9, 'F': 2.8, 'P': -1.6,
            'S': -0.8, 'T': -0.7, 'W': -0.9, 'Y': -1.3, 'V': 4.2,
            # 电荷
            'K': 1, 'R': 1, 'H': 0.5,  # 正电荷
            'D': -1, 'E': -1,           # 负电荷
            # 极性
            'S': 1, 'T': 1, 'N': 1, 'Q': 1, 'C': 1, 'Y': 1
        }
    
    def evaluate(self, sequence: str) -> Dict:
        """
        全面评估序列
        
        Args:
            sequence: 蛋白序列
            
        Returns:
            评估结果字典
        """
        return {
            'length': len(sequence),
            'hydrophobicity': self.calculate_hydrophobicity(sequence),
            'charge': self.calculate_net_charge(sequence),
            'isoelectric_point': self.calculate_pI(sequence),
            'instability_index': self.calculate_instability_index(sequence),
            'gravy': self.calculate_gravy(sequence),
            'aromaticity': self.calculate_aromaticity(sequence),
            'helix_propensity': self.calculate_helix_propensity(sequence),
            'sheet_propensity': self.calculate_sheet_propensity(sequence),
            'stability_score': self.predict_stability(sequence),
            'solubility_score': self.predict_solubility(sequence)
        }
    
    def calculate_hydrophobicity(self, sequence: str) -> float:
        """计算平均疏水性 (Kyte-Doolittle)"""
        if not sequence:
            return 0.0
        
        total = sum(self.aa_properties.get(aa, 0) for aa in sequence)
        return total / len(sequence)
    
    def calculate_net_charge(self, sequence: str, pH: float = 7.0) -> float:
        """计算净电荷"""
        positive = sequence.upper().count('K') + sequence.upper().count('R')
        # H 在 pH 7 时部分带正电
        positive += 0.1 * sequence.upper().count('H')
        negative = sequence.upper().count('D') + sequence.upper().count('E')
        
        return positive - negative
    
    def calculate_pI(self, sequence: str) -> float:
        """计算等电点 (近似)"""
        # 简化计算
        n_pos = sequence.upper().count('K') + sequence.upper().count('R') + sequence.upper().count('H')
        n_neg = sequence.upper().count('D') + sequence.upper().count('E')
        
        if n_pos == 0 and n_neg == 0:
            return 7.0
        
        # 简化 pI 估计
        if n_pos > n_neg:
            return 7.0 + (n_pos - n_neg) * 0.5
        else:
            return 7.0 - (n_neg - n_pos) * 0.5
    
    def calculate_instability_index(self, sequence: str) -> float:
        """
        计算不稳定指数 (DIU)
        < 40: 稳定, > 40: 不稳定
        """
        # 简化版本 - 基于氨基酸组成
        unstable = set('RKEDQN')  # 不稳定氨基酸
        stable = set('AVLIMCFYWHGT')  # 稳定氨基酸
        
        di = 0
        for aa in sequence:
            if aa in unstable:
                di += 1
            elif aa in stable:
                di -= 1
        
        # 规范化到 0-100
        score = 50 + di * 2
        return max(0, min(100, score))
    
    def calculate_gravy(self, sequence: str) -> float:
        """计算 GRAVY (总疏水性/残基数)"""
        return self.calculate_hydrophobicity(sequence)
    
    def calculate_aromaticity(self, sequence: str) -> float:
        """计算芳香性 (芳香氨基酸占比)"""
        aromatic = set('FWY')
        count = sum(1 for aa in sequence if aa in aromatic)
        return count / len(sequence) if sequence else 0
    
    def calculate_helix_propensity(self, sequence: str) -> float:
        """计算α螺旋倾向"""
        helix = {'A', 'E', 'L', 'M'}  # α螺旋促进氨基酸
        helix_destab = {'P', 'G'}  # α螺旋破坏
        
        score = 0
        for aa in sequence:
            if aa in helix:
                score += 1
            elif aa in helix_destab:
                score -= 1
        
        return score / len(sequence) if sequence else 0
    
    def calculate_sheet_propensity(self, sequence: str) -> float:
        """计算β折叠倾向"""
        sheet = {'V', 'I', 'Y', 'F'}
        sheet_destab = {'P', 'G'}
        
        score = 0
        for aa in sequence:
            if aa in sheet:
                score += 1
            elif aa in sheet_destab:
                score -= 1
        
        return score / len(sequence) if sequence else 0
    
    def predict_stability(self, sequence: str) -> float:
        """
        预测稳定性分数 (0-1)
        基于多个因素综合评估
        """
        score = 0.5
        
        # 疏水性 (适中最好)
        hydro = self.calculate_hydrophobicity(sequence)
        if -0.5 < hydro < 1.0:
            score += 0.1
        elif hydro < -1.0:
            score -= 0.1
        
        # 不稳定指数
        ii = self.calculate_instability_index(sequence)
        if ii < 40:
            score += 0.2
        else:
            score -= 0.2
        
        # 螺旋/折叠倾向
        helix = self.calculate_helix_propensity(sequence)
        sheet = self.calculate_sheet_propensity(sequence)
        if abs(helix - sheet) < 0.3:  # 平衡
            score += 0.1
        
        return max(0, min(1, score))
    
    def predict_solubility(self, sequence: str) -> float:
        """
        预测溶解度分数 (0-1)
        """
        score = 0.5
        
        # 电荷 (适度带电利于溶解)
        charge = abs(self.calculate_net_charge(sequence))
        charge_density = charge / len(sequence)
        
        if 0.01 < charge_density < 0.15:
            score += 0.2
        elif charge_density > 0.2:  # 过高可能影响折叠
            score -= 0.1
        
        # 疏水性 (过高降低溶解度)
        hydro = self.calculate_hydrophobicity(sequence)
        if hydro < 0:
            score += 0.1
        elif hydro > 1.5:
            score -= 0.2
        
        # 带电氨基酸比例
        charged_ratio = (sequence.upper().count('K') + 
                        sequence.upper().count('R') + 
                        sequence.upper().count('D') +
                        sequence.upper().count('E')) / len(sequence)
        
        if 0.15 < charged_ratio < 0.35:
            score += 0.1
        
        return max(0, min(1, score))
    
    def evaluate_antimicrobial_potential(self, sequence: str) -> Dict:
        """
        评估抗菌肽潜力
        
        Args:
            sequence: 肽序列
            
        Returns:
            抗菌潜力评估
        """
        charge = self.calculate_net_charge(sequence)
        hydro = self.calculate_hydrophobicity(sequence)
        length = len(sequence)
        
        # 抗菌肽特征
        score = 0
        
        # 正电荷 (重要)
        if charge > 2:
            score += 0.3
        elif charge > 0:
            score += 0.1
        
        # 适度疏水性
        if 0.2 < hydro < 1.0:
            score += 0.2
        
        # 长度 (10-30 AA 常见)
        if 10 <= length <= 30:
            score += 0.2
        
        # 特定模式
        if 'KRK' in sequence or 'KK' in sequence:
            score += 0.1
        
        # 稀有氨基酸检查
        rare = set('MCW')
        rare_count = sum(1 for aa in sequence if aa in rare)
        if rare_count > length * 0.2:
            score -= 0.1
        
        return {
            'amp_score': max(0, min(1, score)),
            'charge': charge,
            'hydrophobicity': hydro,
            'length': length,
            'recommendation': self._get_amp_recommendation(score)
        }
    
    def _get_amp_recommendation(self, score: float) -> str:
        """获取推荐"""
        if score > 0.7:
            return "高潜力抗菌肽"
        elif score > 0.4:
            return "中等潜力，需进一步优化"
        else:
            return "潜力较低，建议调整序列"
    
    def batch_evaluate(self, sequences: List[str]) -> List[Dict]:
        """批量评估"""
        return [self.evaluate(seq) for seq in sequences]
    
    def rank_sequences(
        self, 
        sequences: List[Dict], 
        metric: str = 'stability_score',
        reverse: bool = True
    ) -> List[Dict]:
        """
        排序序列
        
        Args:
            sequences: 序列及评估结果
            metric: 排序指标
            reverse: 降序
            
        Returns:
            排序后的列表
        """
        return sorted(sequences, key=lambda x: x.get(metric, 0), reverse=reverse)


# CLI 测试
if __name__ == "__main__":
    evaluator = SequenceEvaluator()
    
    # 测试序列
    seq1 = "AKLFVMGPELKAL"  # 测试序列
    
    print("=== 序列评估 ===")
    result = evaluator.evaluate(seq1)
    for k, v in result.items():
        print(f"{k}: {v}")
    
    print("\n=== 抗菌肽潜力评估 ===")
    amp_seq = "KALKKKLLKALKKK"
    amp_result = evaluator.evaluate_antimicrobial_potential(amp_seq)
    print(f"Sequence: {amp_seq}")
    for k, v in amp_result.items():
        print(f"{k}: {v}")
