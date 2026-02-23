"""
Protein Language Models - 蛋白质语言模型封装
"""

import os
from typing import List, Dict, Optional


class ESM2Wrapper:
    """
    ESM-2 模型封装
    
    使用方法:
    1. 安装: pip install fair-esm
    2. 下载模型: esm2 available 或自动下载
    """
    
    def __init__(self, model_size: str = "esm2_t33_650M_UR50D"):
        """
        初始化 ESM-2 包装器
        
        Args:
            model_size: 模型大小
                - esm2_t6_8M_UR50D (8M 参数)
                - esm2_t12_35M_UR50D (35M 参数)  
                - esm2_t30_150M_UR50D (150M 参数)
                - esm2_t33_650M_UR50D (650M 参数)
        """
        self.model_name = model_size
        self.model = None
        self.alphabet = None
        self.batch_converter = None
    
    def load_model(self):
        """加载模型"""
        try:
            import esm
        except ImportError:
            raise ImportError(
                "fair-esm not installed. Run: pip install fair-esm"
            )
        
        # 加载模型
        self.model, self.alphabet = esm.pretrained(self.model_name)
        self.batch_converter = self.alphabet.get_batch_converter()
        self.model.eval()
        
        return self
    
    def extract_embeddings(
        self, 
        sequences: List[str],
        batch_size: int = 4
    ) -> Dict[str, List[float]]:
        """
        提取序列嵌入
        
        Args:
            sequences: 蛋白序列列表
            batch_size: 批大小
            
        Returns:
            {序列: 嵌入向量}
        """
        if self.model is None:
            self.load_model()
        
        import torch
        
        embeddings = {}
        
        with torch.no_grad():
            for i in range(0, len(sequences), batch_size):
                batch = sequences[i:i+batch_size]
                batch_labels, batch_strs, batch_tokens = self.batch_converter(
                    [(f"seq_{j}", seq) for j, seq in enumerate(batch)]
                )
                
                results = self.model(batch_tokens, repr_layers=[33], return_contacts=True)
                token_representations = results["representations"][33]
                
                # 取平均作为序列表示
                for j, seq in enumerate(batch):
                    seq_embedding = token_representations[j, 1:len(seq)+1].mean(0)
                    embeddings[seq] = seq_embedding.cpu().numpy().tolist()
        
        return embeddings
    
    def predict_structure(
        self, 
        sequence: str
    ) -> Dict:
        """
        预测结构 (需要 ESMFold)
        
        Args:
            sequence: 蛋白序列
            
        Returns:
            结构预测结果
        """
        # ESMFold 需要单独安装
        raise NotImplementedError(
            "Structure prediction requires ESMFold. "
            "Use AlphaFoldDB client for predictions."
        )


class ProtGPT2Wrapper:
    """
    ProtGPT2 模型封装 - 蛋白序列生成
    """
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
    
    def load_model(self):
        """加载 ProtGPT2 模型"""
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
        except ImportError:
            raise ImportError(
                "transformers not installed. Run: pip install transformers"
            )
        
        model_name = "ncbi/ProtGPT2"
        
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        self.model.eval()
        
        return self
    
    def generate(
        self,
        max_length: int = 100,
        num_return_sequences: int = 1,
        temperature: float = 0.7,
        top_p: float = 0.9
    ) -> List[str]:
        """
        生成蛋白序列
        
        Args:
            max_length: 最大长度
            num_return_sequences: 返回数量
            temperature: 温度
            top_p: nucleus sampling
            
        Returns:
            生成的序列列表
        """
        if self.model is None:
            self.load_model()
        
        import torch
        
        # 蛋白质开始标记
        input_text = "<|prime|> "
        
        inputs = self.tokenizer(
            input_text, 
            return_tensors="pt"
        )
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=max_length,
                num_return_sequences=num_return_sequences,
                temperature=temperature,
                top_p=top_p,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        sequences = []
        for output in outputs:
            text = self.tokenizer.decode(output, skip_special_tokens=True)
            # 提取序列
            seq = text.replace(input_text, "").strip()
            sequences.append(seq)
        
        return sequences


class ModelHub:
    """模型中心 - 统一接口"""
    
    MODELS = {
        "esm2_8m": "esm2_t6_8M_UR50D",
        "esm2_35m": "esm2_t12_35M_UR50D", 
        "esm2_150m": "esm2_t30_150M_UR50D",
        "esm2_650m": "esm2_t33_650M_UR50D",
        "protgpt2": "protgpt2"
    }
    
    @staticmethod
    def get_model(model_name: str):
        """
        获取模型
        
        Args:
            model_name: 模型名 (esm2_8m, esm2_650m, protgpt2)
            
        Returns:
            模型实例
        """
        if model_name.startswith("esm"):
            model_size = ModelHub.MODELS.get(model_name, "esm2_t33_650M_UR50D")
            return ESM2Wrapper(model_size)
        elif model_name == "protgpt2":
            return ProtGPT2Wrapper()
        else:
            raise ValueError(f"Unknown model: {model_name}")


# CLI 测试
if __name__ == "__main__":
    print("=== 模型中心测试 ===")
    
    # 列出可用模型
    print("Available models:")
    for name in ModelHub.MODELS.keys():
        print(f"  - {name}")
