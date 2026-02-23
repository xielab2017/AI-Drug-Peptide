"""
Summary Agent - 论文摘要代理
使用 LLM 生成论文摘要
"""

from typing import Optional, Dict
import os


# 默认提示词
DEFAULT_SUMMARY_PROMPT = """你是一位学术论文摘要专家。请为以下学术论文生成一个简洁、准确的摘要。

论文信息：
- 标题: {title}
- 作者: {authors}
- 发表日期: {published}

论文内容：
{content}

请生成一个 200-300 字的摘要，包含：
1. 研究问题/目标
2. 主要方法
3. 关键结果
4. 贡献/意义

摘要："""


class SummaryAgent:
    """论文摘要生成代理"""
    
    def __init__(self, prompt_template: Optional[str] = None, llm_client=None):
        """
        初始化摘要代理
        
        Args:
            prompt_template: 自定义提示词模板
            llm_client: LLM 客户端
        """
        self.prompt_template = prompt_template or DEFAULT_SUMMARY_PROMPT
        self.llm_client = llm_client
    
    def set_llm_client(self, llm_client):
        """
        设置 LLM 客户端
        
        Args:
            llm_client: LLM 客户端对象
        """
        self.llm_client = llm_client
    
    def summarize(self, paper: Dict, max_length: int = 300) -> str:
        """
        生成论文摘要
        
        Args:
            paper: 论文信息 (包含 title, authors, published, summary/content)
            max_length: 最大摘要长度
            
        Returns:
            生成的摘要
        """
        # 提取论文信息
        title = paper.get('title', 'Unknown Title')
        authors = ', '.join(paper.get('authors', [])) if isinstance(paper.get('authors'), list) else str(paper.get('authors', 'Unknown'))
        published = paper.get('published', 'Unknown Date')
        
        # 获取内容
        content = paper.get('summary') or paper.get('content', '')
        
        if not content:
            return "无法生成摘要：论文内容为空"
        
        # 截取内容（避免过长）
        content = content[:3000]
        
        # 构建提示词
        prompt = self.prompt_template.format(
            title=title,
            authors=authors,
            published=published,
            content=content
        )
        
        # 如果有 LLM 客户端，使用它
        if self.llm_client:
            try:
                response = self.llm_client.chat(prompt)
                return response.strip()
            except Exception as e:
                return f"LLM 生成失败: {str(e)}"
        
        # 否则返回内容摘要
        return self._simple_summarize(content, max_length)
    
    def _simple_summarize(self, text: str, max_length: int = 300) -> str:
        """
        简单的文本摘要（无 LLM 时使用）
        
        Args:
            text: 文本内容
            max_length: 最大长度
            
        Returns:
            摘要
        """
        # 简单实现：取前几句和后几句
        sentences = text.split('. ')
        
        if len(sentences) <= 3:
            return text[:max_length]
        
        # 取开头和结尾的句子
        summary_parts = [sentences[0]]
        if len(sentences) > 2:
            summary_parts.append(sentences[-1])
        
        summary = '. '.join(summary_parts)
        
        if len(summary) > max_length:
            summary = summary[:max_length] + '...'
        
        return summary
    
    def summarize_batch(self, papers: list) -> list:
        """
        批量生成摘要
        
        Args:
            papers: 论文列表
            
        Returns:
            带摘要的论文列表
        """
        results = []
        
        for paper in papers:
            summary = self.summarize(paper)
            result = paper.copy()
            result['generated_summary'] = summary
            results.append(result)
        
        return results
    
    def generate_key_points(self, paper: Dict) -> list:
        """
        生成论文要点
        
        Args:
            paper: 论文信息
            
        Returns:
            要点列表
        """
        content = paper.get('summary') or paper.get('content', '')
        
        if not content:
            return []
        
        # 简单实现：提取关键句子
        prompt = f"""从以下论文中提取 3-5 个关键要点：

标题: {paper.get('title', '')}

内容:
{content[:2000]}

要点（每行一个）："""
        
        if self.llm_client:
            try:
                response = self.llm_client.chat(prompt)
                points = [line.strip() for line in response.strip().split('\n') if line.strip()]
                return points
            except:
                pass
        
        # 回退实现
        sentences = content.split('. ')
        return [s.strip() + '.' for s in sentences[:3] if s.strip()]


# 简单的 LLM 客户端示例
class SimpleLLMClient:
    """简单的 LLM 客户端（需要根据实际情况实现）"""
    
    def __init__(self, model: str = None, api_key: str = None):
        self.model = model or os.getenv("LLM_MODEL", "gpt-4")
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
    
    def chat(self, prompt: str) -> str:
        """发送聊天请求"""
        # TODO: 实现实际的 API 调用
        raise NotImplementedError("请实现实际的 LLM API 调用")


# CLI 测试
if __name__ == "__main__":
    agent = SummaryAgent()
    
    # 测试
    paper = {
        "title": "Attention Is All You Need",
        "authors": ["Ashish Vaswani", "Noam Shazeer", "Niki Parmar"],
        "published": "2017-06-12",
        "summary": """
        The dominant sequence transduction models are based on complex recurrent or 
        convolutional neural networks that include an encoder and a decoder. 
        The best performing models also connect the encoder and the decoder through 
        an attention mechanism. We propose a new simple network architecture, 
        the Transformer, based solely on attention mechanisms.
        """
    }
    
    summary = agent.summarize(paper)
    print("Generated Summary:")
    print(summary)
