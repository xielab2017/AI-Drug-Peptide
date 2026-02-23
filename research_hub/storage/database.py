"""
Storage - ResearchHub 数据存储模块
"""

import sqlite3
import json
import os
from typing import List, Dict, Optional
from datetime import datetime


class Database:
    """SQLite 数据库管理"""
    
    def __init__(self, db_path: str = None):
        """
        初始化数据库
        
        Args:
            db_path: 数据库文件路径
        """
        if db_path is None:
            db_dir = os.path.expanduser("~/.openclaw/data/research-hub")
            os.makedirs(db_dir, exist_ok=True)
            db_path = os.path.join(db_dir, "research_hub.db")
        
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """初始化数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Notebooks 表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notebooks (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        
        # Papers 表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS papers (
                id TEXT PRIMARY KEY,
                notebook_id TEXT,
                title TEXT NOT NULL,
                authors TEXT,
                published TEXT,
                summary TEXT,
                content TEXT,
                link TEXT,
                source TEXT,
                tags TEXT,
                notes TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (notebook_id) REFERENCES notebooks(id)
            )
        """)
        
        # Notes 表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id TEXT PRIMARY KEY,
                notebook_id TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (notebook_id) REFERENCES notebooks(id)
            )
        """)
        
        # FTS5 虚拟表（全文搜索）
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS papers_fts USING fts5(
                id,
                title,
                authors,
                summary,
                content,
                tags,
                content='papers',
                content_rowid='rowid'
            )
        """)
        
        # 触发器：保持 FTS 同步
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS papers_ai AFTER INSERT ON papers BEGIN
                INSERT INTO papers_fts(id, title, authors, summary, content, tags)
                VALUES (new.id, new.title, new.authors, new.summary, new.content, new.tags);
            END
        """)
        
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS papers_ad AFTER DELETE ON papers BEGIN
                INSERT INTO papers_fts(papers_fts, id, title, authors, summary, content, tags)
                VALUES ('delete', old.id, old.title, old.authors, old.summary, old.content, old.tags);
            END
        """)
        
        conn.commit()
        conn.close()
    
    def _get_connection(self):
        """获取数据库连接"""
        return sqlite3.connect(self.db_path)
    
    # ========== Notebook 操作 ==========
    
    def create_notebook(self, title: str, description: str = "") -> str:
        """
        创建笔记本
        
        Args:
            title: 标题
            description: 描述
            
        Returns:
            笔记本 ID
        """
        import uuid
        notebook_id = f"nb_{uuid.uuid4().hex[:8]}"
        now = datetime.now().isoformat()
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO notebooks (id, title, description, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (notebook_id, title, description, now, now)
        )
        
        conn.commit()
        conn.close()
        
        return notebook_id
    
    def get_notebook(self, notebook_id: str) -> Optional[Dict]:
        """获取笔记本"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM notebooks WHERE id = ?", (notebook_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "created_at": row[3],
                "updated_at": row[4]
            }
        return None
    
    def list_notebooks(self) -> List[Dict]:
        """列出所有笔记本"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM notebooks ORDER BY updated_at DESC")
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "created_at": row[3],
                "updated_at": row[4]
            }
            for row in rows
        ]
    
    def update_notebook(self, notebook_id: str, title: str = None, description: str = None) -> bool:
        """更新笔记本"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        updates = []
        params = []
        
        if title:
            updates.append("title = ?")
            params.append(title)
        if description is not None:
            updates.append("description = ?")
            params.append(description)
        
        if updates:
            updates.append("updated_at = ?")
            params.append(datetime.now().isoformat())
            params.append(notebook_id)
            
            cursor.execute(
                f"UPDATE notebooks SET {', '.join(updates)} WHERE id = ?",
                params
            )
            conn.commit()
        
        conn.close()
        return cursor.rowcount > 0
    
    def delete_notebook(self, notebook_id: str) -> bool:
        """删除笔记本"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # 先删除关联的论文和笔记
        cursor.execute("DELETE FROM papers WHERE notebook_id = ?", (notebook_id,))
        cursor.execute("DELETE FROM notes WHERE notebook_id = ?", (notebook_id,))
        cursor.execute("DELETE FROM notebooks WHERE id = ?", (notebook_id,))
        
        conn.commit()
        conn.close()
        
        return True
    
    # ========== Paper 操作 ==========
    
    def add_paper(self, notebook_id: str, paper: Dict) -> str:
        """
        添加论文到笔记本
        
        Args:
            notebook_id: 笔记本 ID
            paper: 论文信息
            
        Returns:
            论文 ID
        """
        import uuid
        paper_id = f"paper_{uuid.uuid4().hex[:8]}"
        now = datetime.now().isoformat()
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """INSERT INTO papers 
               (id, notebook_id, title, authors, published, summary, content, link, source, tags, notes, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                paper_id,
                notebook_id,
                paper.get('title', ''),
                json.dumps(paper.get('authors', [])),
                paper.get('published', ''),
                paper.get('summary', ''),
                paper.get('content', ''),
                paper.get('link', ''),
                paper.get('source', ''),
                json.dumps(paper.get('tags', [])),
                paper.get('notes', ''),
                now
            )
        )
        
        # 更新笔记本时间
        cursor.execute(
            "UPDATE notebooks SET updated_at = ? WHERE id = ?",
            (now, notebook_id)
        )
        
        conn.commit()
        conn.close()
        
        return paper_id
    
    def get_paper(self, paper_id: str) -> Optional[Dict]:
        """获取论文"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM papers WHERE id = ?", (paper_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return self._row_to_paper(row)
        return None
    
    def list_papers(self, notebook_id: str = None) -> List[Dict]:
        """列出论文"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if notebook_id:
            cursor.execute(
                "SELECT * FROM papers WHERE notebook_id = ? ORDER BY created_at DESC",
                (notebook_id,)
            )
        else:
            cursor.execute("SELECT * FROM papers ORDER BY created_at DESC")
        
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_paper(row) for row in rows]
    
    def update_paper(self, paper_id: str, updates: Dict) -> bool:
        """更新论文"""
        allowed = ['title', 'authors', 'summary', 'content', 'link', 'tags', 'notes']
        filtered = {k: v for k, v in updates.items() if k in allowed}
        
        if not filtered:
            return False
        
        # 处理 JSON 字段
        if 'authors' in filtered and isinstance(filtered['authors'], list):
            filtered['authors'] = json.dumps(filtered['authors'])
        if 'tags' in filtered and isinstance(filtered['tags'], list):
            filtered['tags'] = json.dumps(filtered['tags'])
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        params = [f"{k} = ?" for k in filtered.keys()]
        values = list(filtered.values())
        values.append(paper_id)
        
        cursor.execute(
            f"UPDATE papers SET {', '.join(params)} WHERE id = ?",
            values
        )
        
        conn.commit()
        conn.close()
        
        return cursor.rowcount > 0
    
    def delete_paper(self, paper_id: str) -> bool:
        """删除论文"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM papers WHERE id = ?", (paper_id,))
        
        conn.commit()
        conn.close()
        
        return True
    
    def _row_to_paper(self, row) -> Dict:
        """行转论文字典"""
        return {
            "id": row[0],
            "notebook_id": row[1],
            "title": row[2],
            "authors": json.loads(row[3]) if row[3] else [],
            "published": row[4],
            "summary": row[5],
            "content": row[6],
            "link": row[7],
            "source": row[8],
            "tags": json.loads(row[9]) if row[9] else [],
            "notes": row[10],
            "created_at": row[11]
        }
    
    # ========== Note 操作 ==========
    
    def add_note(self, notebook_id: str, content: str) -> str:
        """添加笔记"""
        import uuid
        note_id = f"note_{uuid.uuid4().hex[:8]}"
        now = datetime.now().isoformat()
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO notes (id, notebook_id, content, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (note_id, notebook_id, content, now, now)
        )
        
        cursor.execute(
            "UPDATE notebooks SET updated_at = ? WHERE id = ?",
            (now, notebook_id)
        )
        
        conn.commit()
        conn.close()
        
        return note_id
    
    def list_notes(self, notebook_id: str) -> List[Dict]:
        """列出笔记"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM notes WHERE notebook_id = ? ORDER BY updated_at DESC",
            (notebook_id,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": row[0],
                "notebook_id": row[1],
                "content": row[2],
                "created_at": row[3],
                "updated_at": row[4]
            }
            for row in rows
        ]
    
    def delete_note(self, note_id: str) -> bool:
        """删除笔记"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        
        conn.commit()
        conn.close()
        
        return True
    
    # ========== 搜索操作 ==========
    
    def search(self, query: str, notebook_id: str = None, limit: int = 20) -> List[Dict]:
        """
        全文搜索
        
        Args:
            query: 搜索关键词
            notebook_id: 限制笔记本
            limit: 结果数量
            
        Returns:
            论文列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if notebook_id:
            sql = """
                SELECT p.* FROM papers p
                JOIN papers_fts fts ON p.id = fts.id
                WHERE papers_fts MATCH ? AND p.notebook_id = ?
                ORDER BY rank
                LIMIT ?
            """
            cursor.execute(sql, (query, notebook_id, limit))
        else:
            sql = """
                SELECT p.* FROM papers p
                JOIN papers_fts fts ON p.id = fts.id
                WHERE papers_fts MATCH ?
                ORDER BY rank
                LIMIT ?
            """
            cursor.execute(sql, (query, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_paper(row) for row in rows]


# CLI 测试
if __name__ == "__main__":
    db = Database()
    
    # 测试创建笔记本
    print("=== 测试笔记本操作 ===")
    nb_id = db.create_notebook("Transformer研究", "关于Transformer架构的研究")
    print(f"创建笔记本: {nb_id}")
    
    # 测试添加论文
    print("\n=== 测试论文操作 ===")
    paper_id = db.add_paper(nb_id, {
        "title": "Attention Is All You Need",
        "authors": ["Vaswani et al."],
        "published": "2017",
        "summary": "We propose the Transformer model...",
        "link": "https://arxiv.org/abs/1706.03762",
        "source": "arxiv"
    })
    print(f"添加论文: {paper_id}")
    
    # 测试搜索
    print("\n=== 测试搜索 ===")
    results = db.search("transformer")
    print(f"搜索结果: {len(results)} 篇")
    for p in results:
        print(f"- {p['title']}")
    
    # 测试列出
    print("\n=== 测试列出 ===")
    notebooks = db.list_notebooks()
    print(f"笔记本数: {len(notebooks)}")
