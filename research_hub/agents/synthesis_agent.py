"""
Synthesis Agent - 论文综述合成代理
将同一主题的多篇论文合成为综述
"""

from typing import List, Dict, Optional


DEFAULT_SYNTHESIS_PROMPT = """你是一位学术研究综述专家。请将以下关于 "{topic}" 主题的多篇论文合成为一个连贯的综述。

论文列表：
{papers}

请生成一个结构化综述，包含：
1. **研究背景** - 该领域的研究意义
2. **主要方法** - 各论文使用的方法对比
3. **关键发现** - 各论文的主要贡献
4. **共同趋势** - 领域的发展方向
5. **未来展望** - 潜在的研究方向

请确保：
- 引用每篇论文的主要贡献
- 突出各论文的创新点
- 保持学术写作风格

综述："""


class SynthesisAgent:
    """论文综述合成代理"""
    
    def __init__(self, prompt_template: Optional[str] = None, llm_client=None):
        """
        初始化合成代理
        
        Args:
            prompt_template: 自定义提示词模板
            llm_client: LLM 客户端
        """
        self.prompt_template = prompt_template or DEFAULT_SYNTHESIS_PROMPT
        self.llm_client = llm_client
    
    def set_llm_client(self, llm_client):
        """
        设置 LLM 客户端
        
        Args:
            llm_client: LLM 客户端对象
        """
        self.llm_client = llm_client
    
    def synthesize(self, papers: List[Dict], topic: str) -> str:
        """
        合成综述
        
        Args:
            papers: 论文列表
            topic: 主题名称
            
        Returns:
            生成的综述
        """
        if not papers:
            return "没有论文可供综述"
        
        # 构建论文列表
        papers_text = self._format_papers(papers)
        
        # 构建提示词
        prompt = self.prompt_template.format(
            topic=topic,
            papers=papers_text
        )
        
        # 如果有 LLM 客户端
        if self.llm_client:
            try:
                response = self.llm_client.chat(prompt)
                return response.strip()
            except Exception as e:
                return f"LLM 合成失败: {str(e)}"
        
        # 回退实现
        return self._simple_synthesize(papers, topic)
    
    def _format_papers(self, papers: List[Dict]) -> str:
        """
        格式化论文列表
        
        Args:
            papers: 论文列表
            
        Returns:
            格式化的论文文本
        """
        formatted = []
        
        for i, paper in enumerate(papers, 1):
            title = paper.get('title', 'Unknown')
            authors = paper.get('authors', [])
            if isinstance(authors, list):
                authors = ', '.join(authors[:3]) + (' et al.' if len(authors) > 3 else '')
            else:
                authors = str(authors)
            
            summary = paper.get('summary') or paper.get('generated_summary', '') or paper.get('content', '')[:500]
            
            formatted.append(f"""
论文 {i}: {title}
作者: {authors}
摘要: {summary}
""")
        
        return '\n'.join(formatted)
    
    def _simple_synthesize(self, papers: List[Dict], topic: str) -> str:
        """
        简单合成（无 LLM 时使用）
        
        Args:
            papers: 论文列表
            topic: 主题
            
        Returns:
            简单综述
        """
        lines = [f"## {topic} 研究综述\n"]
        
        lines.append(f"本综述涵盖 {len(papers)} 篇相关论文。\n")
        
        # 主要方法
        lines.append("### 主要方法\n")
        methods = set()
        for paper in papers:
            # 简单提取方法关键词
            summary = paper.get('summary', '')[:200]
            if 'neural' in summary.lower() or 'network' in summary.lower():
                methods.add('神经网络')
            if 'transformer' in summary.lower():
                methods.add('Transformer')
            if 'attention' in summary.lower():
                methods.add('注意力机制')
            if 'reinforcement' in summary.lower():
                methods.add('强化学习')
        
        for m in methods:
            lines.append(f"- {m}\n")
        
        # 论文摘要
        lines.append("\n### 论文摘要\n")
        for i, paper in enumerate(papers, 1):
            title = paper.get('title', 'Unknown')[:60]
            summary = paper.get('summary', '')[:200]
            lines.append(f"**{i}. {title}**\n")
            lines.append(f"{summary}...\n\n")
        
        return ''.join(lines)
    
    def synthesize_with_citations(self, papers: List[Dict], topic: str) -> Dict:
        """
        生成带引用的综述
        
        Args:
            papers: 论文列表
            topic: 主题
            
        Returns:
            包含综述和引用信息的字典
        """
        synthesis = self.synthesize(papers, topic)
        
        # 生成引用
        citations = []
        for i, paper in enumerate(papers, 1):
            title = paper.get('title', 'Unknown')
            authors = paper.get('authors', [])
            link = paper.get('link', paper.get('id', ''))
            
            if isinstance(authors, list):
                first_author = authors[0] if authors else 'Unknown'
                if ',' in first_author:
                    first_author = first_author.split(',')[0]
            else:
                first_author = str(authors).split(',')[0] if ',' in str(authors) else str(authors)
            
            citations.append({
                'number': i,
                'title': title,
                'authors': authors,
                'link': link
            })
        
        return {
            'topic': topic,
            'synthesis': synthesis,
            'citations': citations,
            'paper_count': len(papers)
        }
    
    def compare_papers(self, papers: List[Dict], criteria: List[str] = None) -> str:
        """
        对比论文
        
        Args:
            papers: 论文列表
            criteria: 对比标准
            
        Returns:
            对比分析
        """
        if criteria is None:
            criteria = ["方法", "数据集", "性能", "创新点"]
        
        if not self.llm_client:
            return "需要 LLM 客户端来进行论文对比"
        
        papers_text = self._format_papers(papers)
        
        prompt = f"""请对比以下论文：

{papers_text}

对比标准: {', '.join(criteria)}

请以表格形式展示对比结果。"""
        
        try:
            response = self.llm_client.chat(prompt)
            return response.strip()
        except Exception as e:
            return f"对比失败: {str(e)}"


# CLI 测试
if __name__ == "__main__":
    agent = SynthesisAgent()
    
    # 测试
    papers = [
        {
            "title": "Attention Is All You Need",
            "authors": ["Vaswani et al."],
            "summary": "We the Transformer, a novel neural propose network architecture based solely on attention mechanisms.",
            "link": "https://arxiv.org/abs/1706.03762"
        },
        {
            "title": "BERT: Pre-training of Deep Bidirectional Transformers",
            "authors": ["Devlin et al."],
            "summary": "We introduce a new language representation model called BERT, which stands for Bidirectional Encoder Representations.",
            "link": "https://arxiv.org/abs/1810.04805"
        }
    ]
    
    result = agent.synthesize_with_citations(papers, "Transformer")
    print(result['synthesis'])
    print("\nCitations:")
    for c in result['citations']:
        print(f"[{c['number']}] {c['title']}")
