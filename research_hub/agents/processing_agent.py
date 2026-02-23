"""
Processing Agent - 论文处理代理
支持: PDF 解析, HTML 解析, 文本清洗
"""

import os
import re
from typing import Optional

# 尝试导入可选依赖
try:
    import fitz  # PyMuPDF
    HAS_FITZ = True
except ImportError:
    HAS_FITZ = False

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False


class ProcessingAgent:
    """论文内容处理代理"""
    
    def __init__(self):
        self.has_fitz = HAS_FITZ
        self.has_bs4 = HAS_BS4
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        从 PDF 文件提取文本
        
        Args:
            pdf_path: PDF 文件路径
            
        Returns:
            提取的文本
        """
        if not self.has_fitz:
            raise ImportError("PyMuPDF (fitz) not installed. Run: pip install pymupdf")
        
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        text = ""
        try:
            with fitz.open(pdf_path) as doc:
                for page in doc:
                    text += page.get_text()
        except Exception as e:
            raise Exception(f"Failed to extract text from PDF: {e}")
        
        return self.clean_text(text)
    
    def extract_text_from_pdf_bytes(self, pdf_bytes: bytes) -> str:
        """
        从 PDF 字节数据提取文本
        
        Args:
            pdf_bytes: PDF 文件字节数据
            
        Returns:
            提取的文本
        """
        if not self.has_fitz:
            raise ImportError("PyMuPDF (fitz) not installed. Run: pip install pymupdf")
        
        text = ""
        try:
            with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
                for page in doc:
                    text += page.get_text()
        except Exception as e:
            raise Exception(f"Failed to extract text from PDF: {e}")
        
        return self.clean_text(text)
    
    def extract_text_from_html(self, html: str) -> str:
        """
        从 HTML 提取文本
        
        Args:
            html: HTML 内容
            
        Returns:
            提取的文本
        """
        if not self.has_bs4:
            raise ImportError("BeautifulSoup4 not installed. Run: pip install beautifulsoup4")
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # 移除脚本和样式
        for script in soup(["script", "style"]):
            script.decompose()
        
        text = soup.get_text()
        return self.clean_text(text)
    
    def extract_text_from_url(self, url: str) -> str:
        """
        从 URL 获取页面文本
        
        Args:
            url: 网页 URL
            
        Returns:
            页面文本
        """
        import requests
        
        response = requests.get(url)
        response.raise_for_status()
        
        return self.extract_text_from_html(response.text)
    
    def clean_text(self, text: str) -> str:
        """
        清洗文本
        
        Args:
            text: 原始文本
            
        Returns:
            清洗后的文本
        """
        if not text:
            return ""
        
        # 移除多余空白
        text = re.sub(r'\s+', ' ', text)
        
        # 移除特殊字符（保留基本标点）
        text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', text)
        
        # 移除页码等噪声 (如 "Page 1 of 10")
        text = re.sub(r'Page\s+\d+\s+of\s+\d+', '', text, flags=re.IGNORECASE)
        
        return text.strip()
    
    def extract_abstract(self, text: str) -> Optional[str]:
        """
        从论文文本中提取摘要
        
        Args:
            text: 论文全文
            
        Returns:
            摘要文本，如果未找到返回 None
        """
        # 常见摘要标题模式
        abstract_patterns = [
            r'(?:Abstract|SUMMARY)\s*[:\-]?\s*(.{100,2000}?)(?:\n\s*(?:Introduction|Keywords|1\.|I\.)|$)',
            r'(?:Abstract|SUMMARY)\s*[:\-]?\s*([^\n]{100,})',
        ]
        
        for pattern in abstract_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()
        
        # 如果没找到，返回前500字符作为参考
        return text[:500] if len(text) > 500 else text
    
    def extract_introduction(self, text: str) -> str:
        """
        从论文文本中提取引言部分
        
        Args:
            text: 论文全文
            
        Returns:
            引言文本
        """
        # 查找引言部分
        intro_patterns = [
            r'(?:1\.|I\.|Introduction)\s*[:\-]?\s*(.{100,5000}?)(?:\n\s*(?:2\.|II\.|Related Work|Background|2\s))',
            r'Introduction\s*[:\-]?\s*(.{100,3000}?)(?:\n\s*\n)',
        ]
        
        for pattern in intro_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()
        
        # 返回全文前3000字符
        return text[:3000]
    
    def process(self, paper: dict) -> dict:
        """
        处理论文
        
        Args:
            paper: 论文基本信息
            
        Returns:
            处理后的论文信息
        """
        result = paper.copy()
        
        # 如果有 PDF 路径，提取文本
        if 'pdf_path' in paper and os.path.exists(paper['pdf_path']):
            content = self.extract_text_from_pdf(paper['pdf_path'])
            result['content'] = content
            result['abstract'] = self.extract_abstract(content)
        
        return result


# CLI 测试
if __name__ == "__main__":
    agent = ProcessingAgent()
    
    # 测试文本清洗
    text = "  This   is  a    test   \n\n\n  with   whitespace  "
    cleaned = agent.clean_text(text)
    print(f"Cleaned: '{cleaned}'")
