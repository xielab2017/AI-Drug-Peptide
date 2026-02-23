"""
ProteinGenerator - 蛋白序列生成器
支持多种生成方法: 随机生成, 基于模板, 微调模型
"""

import random
from typing import List, Dict, Optional


# 氨基酸
AMINO_ACIDS = list("ACDEFGHIKLMNPQRSTVWY")
AMINO_ACID_PROPERTIES = {
    'hydrophobic': set('AVILMFYW'),
    'hydrophilic': set('RKDENQ'),
    'charged_positive': set('RKH'),
    'charged_negative': set('DE'),
    'polar': set('STNQ'),
    'aromatic': set('FYW'),
    'small': set('AGS'),
    'tiny': set('AGS')
}


class ProteinGenerator:
    """蛋白序列生成器"""
    
    def __init__(self, model: str = "random"):
        """
        初始化生成器
        
        Args:
            model: 生成模型 (random, template, esm2)
        """
        self.model = model
    
    def generate_random(
        self, 
        length: int = 100,
        weighted: bool = False,
        property_constraint: str = None
    ) -> str:
        """
        随机生成蛋白序列
        
        Args:
            length: 序列长度
            weighted: 是否使用加权概率
            property_constraint: 属性约束
            
        Returns:
            蛋白序列
        """
        if weighted:
            # 使用自然界常见氨基酸频率
            weights = {
                'L': 0.095, 'A': 0.087, 'G': 0.074, 'V': 0.067,
                'E': 0.063, 'S': 0.056, 'I': 0.052, 'T': 0.051,
                'K': 0.048, 'D': 0.047, 'R': 0.042, 'N': 0.039,
                'P': 0.038, 'F': 0.037, 'Q': 0.036, 'M': 0.024,
                'C': 0.019, 'H': 0.015, 'Y': 0.012, 'W': 0.010
            }
            seq = random.choices(
                list(weights.keys()), 
                weights=list(weights.values()), 
                k=length
            )
            return ''.join(seq)
        
        if property_constraint:
            allowed = AMINO_ACID_PROPERTIES.get(property_constraint, set(AMINO_ACIDS))
            return ''.join(random.choices(list(allowed), k=length))
        
        return ''.join(random.choices(AMINO_ACIDS, k=length))
    
    def generate_antimicrobial_peptide(
        self,
        length_range: tuple = (10, 30),
        num_sequences: int = 10
    ) -> List[Dict]:
        """
        生成抗菌肽序列
        
        Args:
            length_range: 长度范围
            num_sequences: 生成数量
            
        Returns:
            肽序列列表
        """
        peptides = []
        
        for _ in range(num_sequences):
            length = random.randint(*length_range)
            
            # 抗菌肽特征: 带正电荷, 疏水性
            # 常见抗菌肽模式
            patterns = [
                # α螺旋模式
                lambda: self._generate_alpha_helix(length),
                # β折叠模式  
                lambda: self._generate_beta_sheet(length),
                # 混合模式
                lambda: self._generate_amp_pattern(length)
            ]
            
            pattern_fn = random.choice(patterns)
            sequence = pattern_fn()
            
            peptides.append({
                'sequence': sequence,
                'length': len(sequence),
                'charge': self._calculate_charge(sequence),
                'hydrophobicity': self._calculate_hydrophobicity(sequence),
                'type': 'antimicrobial'
            })
        
        return peptides
    
    def _generate_alpha_helix(self, length: int) -> str:
        """生成α螺旋偏好序列"""
        helix_formers = ['A', 'E', 'L', 'M']  # α螺旋促进氨基酸
        return ''.join(random.choices(helix_formers, k=length))
    
    def _generate_beta_sheet(self, length: int) -> str:
        """生成β折叠偏好序列"""
        sheet_formers = ['V', 'I', 'Y', 'F']  # β折叠促进氨基酸
        return ''.join(random.choices(sheet_formers, k=length))
    
    def _generate_amp_pattern(self, length: int) -> str:
        """生成抗菌肽模式"""
        # 正电荷+疏水+亲水交替
        charged = ['K', 'R', 'H']
        hydrophobic = ['A', 'L', 'V', 'I']
        polar = ['S', 'T', 'N', 'Q']
        
        pattern = []
        for i in range(length):
            if i % 3 == 0:
                pattern.append(random.choice(charged))
            elif i % 3 == 1:
                pattern.append(random.choice(hydrophobic))
            else:
                pattern.append(random.choice(polar))
        
        return ''.join(pattern)
    
    def _calculate_charge(self, sequence: str) -> float:
        """计算净电荷 (pH 7)"""
        positive = sum(1 for aa in sequence if aa in 'KRH')
        negative = sum(1 for aa in sequence if aa in 'DE')
        return positive - negative
    
    def _calculate_hydrophobicity(self, sequence: str) -> float:
        """计算疏水性"""
        hydrophobic = sum(1 for aa in sequence if aa in 'AVILMFYW')
        return hydrophobic / len(sequence)
    
    def generate_template_based(
        self,
        template: str,
        mutations: int = 5,
        positions: List[int] = None
    ) -> str:
        """
        基于模板生成变体
        
        Args:
            template: 模板序列
            mutations: 突变数量
            positions: 指定突变位置 (None则随机)
            
        Returns:
            突变后的序列
        """
        seq_list = list(template)
        
        if positions is None:
            positions = random.sample(range(len(seq_list)), 
                                   min(mutations, len(seq_list)))
        
        for pos in positions:
            seq_list[pos] = random.choice(AMINO_ACIDS)
        
        return ''.join(seq_list)
    
    def generate_diverse_set(
        self,
        length: int,
        num_sequences: int,
        similarity_threshold: float = 0.3
    ) -> List[str]:
        """
        生成多样化序列集
        
        Args:
            length: 序列长度
            num_sequences: 数量
            similarity_threshold: 相似度阈值
            
        Returns:
            序列列表
        """
        sequences = []
        
        while len(sequences) < num_sequences:
            seq = self.generate_random(length, weighted=True)
            
            # 检查与已有序列的相似度
            is_diverse = True
            for existing in sequences:
                similarity = self._calculate_similarity(seq, existing)
                if similarity > (1 - similarity_threshold):
                    is_diverse = False
                    break
            
            if is_diverse:
                sequences.append(seq)
        
        return sequences
    
    def _calculate_similarity(self, seq1: str, seq2: str) -> float:
        """计算两序列相似度"""
        if len(seq1) != len(seq2):
            return 0.0
        
        matches = sum(1 for a, b in zip(seq1, seq2) if a == b)
        return matches / len(seq1)


# CLI 测试
if __name__ == "__main__":
    gen = ProteinGenerator()
    
    # 测试随机生成
    print("=== 随机生成 ===")
    seq = gen.generate_random(20, weighted=True)
    print(f"Sequence: {seq}")
    
    # 测试抗菌肽生成
    print("\n=== 抗菌肽生成 ===")
    amps = gen.generate_antimicrobial_peptide(length_range=(15, 25), num_sequences=3)
    for amp in amps:
        print(f"Seq: {amp['sequence']}")
        print(f"  Charge: {amp['charge']}, Hydro: {amp['hydrophobicity']:.2f}")
    
    # 测试多样化生成
    print("\n=== 多样化集合 ===")
    diverse = gen.generate_diverse_set(length=30, num_sequences=5)
    print(f"Generated {len(diverse)} diverse sequences")
