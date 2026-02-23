"""
Classification Agent - 论文分类代理
支持: TF-IDF + 余弦相似度, LLM 零样本分类
"""

from typing import List, Dict, Tuple, Optional
import re


class ClassificationAgent:
    """论文主题分类代理"""
    
    def __init__(self, topics: Optional[List[str]] = None):
        """
        初始化分类代理
        
        Args:
            topics: 预定义主题列表，如果为 None 则使用默认主题
        """
        self.default_topics = [
            "Machine Learning",
            "Computer Vision", 
            "Natural Language Processing",
            "Reinforcement Learning",
            "Robotics",
            "Data Mining",
            "Computer Graphics",
            "Human-Computer Interaction",
            "Security",
            "Networking"
        ]
        self.topics = topics or self.default_topics
    
    def classify_tfidf(self, text: str, threshold: float = 0.3) -> Tuple[str, float]:
        """
        使用 TF-IDF 和关键词匹配进行分类
        
        Args:
            text: 待分类文本
            threshold: 相似度阈值
            
        Returns:
            (主题, 相似度)
        """
        # 简单关键词匹配
        topic_keywords = {
            "Machine Learning": ["machine learning", "neural network", "deep learning", "model", "training", "algorithm"],
            "Computer Vision": ["image", "video", "vision", "object detection", "segmentation", "cnn", "recognition"],
            "Natural Language Processing": ["nlp", "text", "language", "translation", "parsing", "bert", "gpt", "transformer"],
            "Reinforcement Learning": ["reinforcement", "reward", "policy", "agent", "environment", "DQN", "PPO"],
            "Robotics": ["robot", "robotics", "manipulation", "navigation", "autonomous"],
            "Data Mining": ["data mining", "clustering", "recommendation", "association", "pattern"],
            "Computer Graphics": ["graphics", "rendering", "animation", "3d", "geometry"],
            "Human-Computer Interaction": ["hci", "interaction", "user", "interface", "vr", "ar"],
            "Security": ["security", "privacy", "attack", "defense", "encryption"],
            "Networking": ["network", "protocol", "routing", "wireless", "distributed"]
        }
        
        text_lower = text.lower()
        scores = {}
        
        for topic, keywords in topic_keywords.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            scores[topic] = score / len(keywords)
        
        if not scores or max(scores.values()) < threshold:
            return ("Other", 0.0)
        
        best_topic = max(scores, key=scores.get)
        return (best_topic, scores[best_topic])
    
    def classify_llm(self, text: str, llm_client=None) -> Tuple[str, float]:
        """
        使用 LLM 进行零样本分类
        
        Args:
            text: 待分类文本
            llm_client: LLM 客户端（需要实现 chat 方法）
            
        Returns:
            (主题, 置信度)
        """
        if llm_client is None:
            # 回退到 TF-IDF
            return self.classify_tfidf(text)
        
        # 构建提示词
        prompt = f"""Classify the following research paper into one of these categories:
{', '.join(self.topics)}

Paper content:
{text[:1500]}

Return ONLY the category name, nothing else."""

        try:
            response = llm_client.chat(prompt)
            topic = response.strip()
            
            # 验证返回的主题是否有效
            if topic not in self.topics:
                # 尝试模糊匹配
                for t in self.topics:
                    if t.lower() in topic.lower():
                        topic = t
                        break
                else:
                    topic = "Other"
            
            return (topic, 0.9)
        except Exception as e:
            print(f"LLM classification failed: {e}")
            return self.classify_tfidf(text)
    
    def classify(self, text: str, method: str = "tfidf", llm_client=None) -> str:
        """
        分类论文
        
        Args:
            text: 待分类文本
            method: 分类方法 ("tfidf" 或 "llm")
            llm_client: LLM 客户端
            
        Returns:
            主题名称
        """
        if method == "llm":
            topic, _ = self.classify_llm(text, llm_client)
        else:
            topic, _ = self.classify_tfidf(text)
        
        return topic
    
    def classify_batch(self, papers: List[Dict], method: str = "tfidf") -> Dict[str, List[Dict]]:
        """
        批量分类论文
        
        Args:
            papers: 论文列表
            method: 分类方法
            
        Returns:
            按主题分组的论文字典
        """
        grouped = {}
        
        for paper in papers:
            text = paper.get('summary', '') or paper.get('content', '')[:2000]
            topic = self.classify(text, method)
            
            if topic not in grouped:
                grouped[topic] = []
            grouped[topic].append(paper)
        
        return grouped
    
    def add_topic(self, topic: str):
        """
        添加新主题
        
        Args:
            topic: 主题名称
        """
        if topic not in self.topics:
            self.topics.append(topic)
    
    def remove_topic(self, topic: str):
        """
        移除主题
        
        Args:
            topic: 主题名称
        """
        if topic in self.topics:
            self.topics.remove(topic)


# CLI 测试
if __name__ == "__main__":
    agent = ClassificationAgent()
    
    # 测试文本
    test_text = """
    We propose a novel deep learning approach for image classification 
    using convolutional neural networks. Our method achieves state-of-the-art 
    results on ImageNet with 95% accuracy.
    """
    
    topic, score = agent.classify_tfidf(test_text)
    print(f"TF-IDF 分类: {topic} (score: {score:.2f})")
    
    # 测试批量分类
    papers = [
        {"title": "Paper 1", "summary": "Deep learning for image classification"},
        {"title": "Paper 2", "summary": "Transformer for machine translation"},
        {"title": "Paper 3", "summary": "Reinforcement learning for robotics"}
    ]
    
    grouped = agent.classify_batch(papers)
    for topic, ps in grouped.items():
        print(f"\n{topic}:")
        for p in ps:
            print(f"  - {p['title']}")
