"""
Orchestrator - ResearchHub 工作流编排器
"""

from typing import List, Dict, Optional
import os

from ..agents.search_agent import SearchAgent
from ..agents.processing_agent import ProcessingAgent
from ..agents.classification_agent import ClassificationAgent
from ..agents.summary_agent import SummaryAgent
from ..agents.synthesis_agent import SynthesisAgent
from ..agents.audio_agent import AudioAgent


class Orchestrator:
    """ResearchHub 工作流编排器"""
    
    def __init__(
        self,
        topics: Optional[List[str]] = None,
        llm_client=None,
        audio_engine: str = "gtts",
        output_dir: str = None
    ):
        """
        初始化编排器
        
        Args:
            topics: 预定义主题列表
            llm_client: LLM 客户端
            audio_engine: 音频引擎
            output_dir: 输出目录
        """
        # 初始化各代理
        self.search_agent = SearchAgent()
        self.processing_agent = ProcessingAgent()
        self.classification_agent = ClassificationAgent(topics)
        self.summary_agent = SummaryAgent(llm_client=llm_client)
        self.synthesis_agent = SynthesisAgent(llm_client=llm_client)
        self.audio_agent = AudioAgent(
            engine=audio_engine,
            output_dir=output_dir or os.path.expanduser("~/.openclaw/data/research-hub/audio")
        )
        
        self.llm_client = llm_client
        
        # 确保输出目录存在
        os.makedirs(self.audio_agent.output_dir, exist_ok=True)
    
    def set_llm_client(self, llm_client):
        """
        设置 LLM 客户端
        
        Args:
            llm_client: LLM 客户端
        """
        self.llm_client = llm_client
        self.summary_agent.set_llm_client(llm_client)
        self.synthesis_agent.set_llm_client(llm_client)
    
    def run(
        self,
        query: str = None,
        paper_id: str = None,
        file_path: str = None,
        url: str = None,
        doi: str = None,
        source: str = "arxiv",
        max_results: int = 5,
        generate_audio: bool = False,
        classify_method: str = "tfidf"
    ) -> Dict:
        """
        运行完整研究流程
        
        Args:
            query: 搜索关键词
            paper_id: 论文 ID (arXiv/DOI)
            file_path: PDF 文件路径
            url: 论文 URL
            doi: DOI
            source: 数据源
            max_results: 最大结果数
            generate_audio: 是否生成音频
            classify_method: 分类方法
            
        Returns:
            处理结果
        """
        papers = []
        
        # 1. 搜索/获取论文
        if query:
            papers.extend(self.search_agent.search(query, source, max_results))
        if paper_id:
            papers.append(self.search_agent.get_paper_by_id(paper_id))
        if file_path:
            paper = {"title": os.path.basename(file_path), "source": "file"}
            content = self.processing_agent.extract_text_from_pdf(file_path)
            paper['content'] = content
            paper['summary'] = self.processing_agent.extract_abstract(content) or content[:500]
            papers.append(paper)
        if url:
            papers.append(self.search_agent.process_url(url))
        if doi:
            papers.append(self.search_agent.process_doi(doi))
        
        if not papers:
            return {"error": "No papers found"}
        
        # 2. 处理和分类
        processed_papers = []
        for paper in papers:
            # 处理
            processed = self.processing_agent.process(paper)
            
            # 分类
            text = processed.get('summary', '') or processed.get('content', '')[:2000]
            topic = self.classification_agent.classify(text, classify_method)
            processed['topic'] = topic
            
            processed_papers.append(processed)
        
        # 3. 按主题分组
        grouped = self.classification_agent.classify_batch(processed_papers, classify_method)
        
        # 4. 生成摘要
        summarized = {}
        for topic, topic_papers in grouped.items():
            summaries = self.summary_agent.summarize_batch(topic_papers)
            summarized[topic] = summaries
        
        # 5. 生成综述
        synthesis_results = {}
        for topic, topic_papers in grouped.items():
            synthesis = self.synthesis_agent.synthesize_with_citations(topic_papers, topic)
            synthesis_results[topic] = synthesis
            
            # 6. 生成音频（可选）
            if generate_audio:
                audio_path = self.audio_agent.generate_podcast(
                    synthesis['synthesis'],
                    intro=f"Here is the research summary for {topic}."
                )
                synthesis_results[topic]['audio_path'] = audio_path
        
        return {
            'papers': processed_papers,
            'grouped': grouped,
            'summaries': summarized,
            'synthesis': synthesis_results,
            'stats': {
                'total_papers': len(papers),
                'topics': list(grouped.keys())
            }
        }
    
    def search_only(
        self,
        query: str,
        source: str = "arxiv",
        max_results: int = 5
    ) -> List[Dict]:
        """
        仅搜索论文
        
        Args:
            query: 搜索关键词
            source: 数据源
            max_results: 最大结果数
            
        Returns:
            论文列表
        """
        return self.search_agent.search(query, source, max_results)
    
    def summarize_only(
        self,
        paper: Dict,
        generate_key_points: bool = False
    ) -> Dict:
        """
        仅生成摘要
        
        Args:
            paper: 论文信息
            generate_key_points: 是否生成要点
            
        Returns:
            摘要结果
        """
        summary = self.summary_agent.summarize(paper)
        result = {
            'paper': paper,
            'summary': summary
        }
        
        if generate_key_points:
            key_points = self.summary_agent.generate_key_points(paper)
            result['key_points'] = key_points
        
        return result
    
    def synthesize_only(
        self,
        papers: List[Dict],
        topic: str
    ) -> Dict:
        """
        仅生成综述
        
        Args:
            papers: 论文列表
            topic: 主题
            
        Returns:
            综述结果
        """
        return self.synthesis_agent.synthesize_with_citations(papers, topic)
    
    def generate_audio(
        self,
        text: str,
        filename: str = None,
        intro: str = None,
        outro: str = None
    ) -> str:
        """
        仅生成音频
        
        Args:
            text: 文本内容
            filename: 输出文件名
            intro: 开场白
            outro: 结束语
            
        Returns:
            音频文件路径
        """
        return self.audio_agent.generate_podcast(text, filename, intro, outro)


# 便捷函数
def quick_search(query: str, max_results: int = 5) -> List[Dict]:
    """快速搜索论文"""
    orchestrator = Orchestrator()
    return orchestrator.search_only(query, max_results=max_results)


def quick_summarize(paper: Dict) -> str:
    """快速生成摘要"""
    orchestrator = Orchestrator()
    return orchestrator.summarize_only(paper)['summary']


# CLI 测试
if __name__ == "__main__":
    # 测试搜索
    print("=== 测试搜索 ===")
    orchestrator = Orchestrator()
    papers = orchestrator.search_only("machine learning", max_results=3)
    
    for p in papers:
        print(f"- {p['title'][:60]}")
    
    # 测试完整流程
    print("\n=== 测试完整流程 ===")
    result = orchestrator.run(
        query="transformer attention",
        max_results=3,
        generate_audio=False
    )
    
    print(f"找到 {result['stats']['total_papers']} 篇论文")
    print(f"主题: {result['stats']['topics']}")
