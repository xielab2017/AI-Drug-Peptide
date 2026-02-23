"""
Search Agent - 论文搜索代理
支持: arXiv, OpenAlex, DOI, URL, PDF上传
"""

import requests
import xml.etree.ElementTree as ET
import os
from typing import List, Dict, Optional


class SearchAgent:
    """学术论文搜索代理"""
    
    def __init__(self):
        self.arxiv_api = "http://export.arxiv.org/api/query?"
        self.openalex_api = "https://api.openalex.org/works"
    
    def search_arxiv(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        从 arXiv 搜索论文
        
        Args:
            query: 搜索关键词
            max_results: 最大结果数
            
        Returns:
            论文列表
        """
        params = {
            "search_query": query,
            "start": 0,
            "max_results": max_results,
            "sortBy": "relevance",
            "sortOrder": "descending"
        }
        
        response = requests.get(self.arxiv_api, params=params)
        if response.status_code != 200:
            raise Exception("Failed to fetch data from arXiv API")
        
        # 解析 XML
        root = ET.fromstring(response.content)
        namespace = {'n': 'http://www.w3.org/2005/Atom'}
        
        papers = []
        for entry in root.findall('n:entry', namespace):
            paper = {
                'id': entry.find('n:id', namespace).text.strip(),
                'title': entry.find('n:title', namespace).text.strip().replace('\n', ' '),
                'authors': [author.text for author in entry.findall('n:author/n:name', namespace)],
                'published': entry.find('n:published', namespace).text.strip(),
                'summary': entry.find('n:summary', namespace).text.strip().replace('\n', ' '),
                'link': entry.find('n:id', namespace).text.strip(),
                'source': 'arxiv'
            }
            papers.append(paper)
        
        return papers
    
    def search_openalex(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        从 OpenAlex 搜索论文
        
        Args:
            query: 搜索关键词
            max_results: 最大结果数
            
        Returns:
            论文列表
        """
        params = {
            "search": query,
            "per_page": max_results,
            "sort": "relevance_score"
        }
        
        headers = {"Accept": "application/json"}
        
        response = requests.get(
            self.openalex_api, 
            params=params, 
            headers=headers
        )
        
        if response.status_code != 200:
            raise Exception("Failed to fetch data from OpenAlex API")
        
        data = response.json()
        
        papers = []
        for work in data.get('results', []):
            paper = {
                'id': work.get('doi', ''),
                'title': work.get('title', ''),
                'authors': [author.get('display_name', '') for author in work.get('authorships', [])],
                'published': work.get('publication_date', ''),
                'summary': work.get('abstract', ''),
                'link': work.get('doi', ''),
                'source': 'openalex',
                'cited_by_count': work.get('cited_by_count', 0)
            }
            papers.append(paper)
        
        return papers
    
    def search(self, query: str, source: str = 'arxiv', max_results: int = 5) -> List[Dict]:
        """
        统一搜索接口
        
        Args:
            query: 搜索关键词
            source: 数据源 (arxiv, openalex)
            max_results: 最大结果数
            
        Returns:
            论文列表
        """
        if source.lower() == 'arxiv':
            return self.search_arxiv(query, max_results)
        elif source.lower() == 'openalex':
            return self.search_openalex(query, max_results)
        else:
            raise ValueError(f"Unsupported source: {source}")
    
    def process_doi(self, doi: str) -> Dict:
        """
        通过 DOI 获取论文信息
        
        Args:
            doi: DOI 链接或 ID
            
        Returns:
            论文信息
        """
        # 清理 DOI
        doi = doi.strip()
        if doi.startswith('https://doi.org/'):
            doi = doi.replace('https://doi.org/', '')
        
        url = f"https://doi.org/{doi}"
        headers = {"Accept": "application/json"}
        
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"Failed to fetch DOI: {doi}")
        
        data = response.json()
        
        return {
            'id': doi,
            'title': data.get('title', ''),
            'authors': [author.get('given', '') + ' ' + author.get('family', '') 
                       for author in data.get('author', [])],
            'published': data.get('created', {}).get('date-parts', [['']])[0][0],
            'summary': data.get('abstract', ''),
            'link': f"https://doi.org/{doi}",
            'source': 'doi'
        }
    
    def process_url(self, url: str) -> Dict:
        """
        通过 URL 获取论文
        
        Args:
            url: 论文 URL
            
        Returns:
            论文信息
        """
        # 简单实现，实际需要根据不同出版社定制
        return {
            'id': url,
            'title': 'Paper from URL',
            'authors': [],
            'published': '',
            'summary': '',
            'link': url,
            'source': 'url',
            'note': '需要安装 processing_agent 进行全文提取'
        }
    
    def get_paper_by_id(self, paper_id: str) -> Dict:
        """
        根据 ID 获取论文
        
        Args:
            paper_id: arXiv ID 或 DOI
            
        Returns:
            论文信息
        """
        # 判断 ID 类型
        if paper_id.startswith('10.'):
            return self.process_doi(paper_id)
        elif paper_id.startswith('http'):
            if 'doi.org' in paper_id:
                return self.process_doi(paper_id)
            else:
                return self.process_url(paper_id)
        else:
            # 假设是 arXiv ID
            return self.search_arxiv(f"id:{paper_id}", 1)[0]


# CLI 测试
if __name__ == "__main__":
    agent = SearchAgent()
    
    # 测试 arXiv 搜索
    print("=== arXiv 搜索测试 ===")
    papers = agent.search_arxiv("machine learning", max_results=3)
    for p in papers:
        print(f"- {p['title'][:50]}...")
    
    # 测试 OpenAlex 搜索
    print("\n=== OpenAlex 搜索测试 ===")
    papers = agent.search_openalex("transformer", max_results=3)
    for p in papers:
        print(f"- {p['title'][:50]}...")
