"""
ResearchHub Web Application
本地/开放双模式网页界面
"""

from flask import Flask, render_template_string, request, jsonify, send_file
import sys
import os

# 添加模块路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from design.generator import ProteinGenerator
from design.evaluator import SequenceEvaluator
from design.exporter import DesignExporter
from agents.search_agent import SearchAgent
from storage.database import Database

app = Flask(__name__)

# ========== HTML 模板 ==========
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ResearchHub - 蛋白/肽设计工具</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 900px; margin: 0 auto; }
        .card {
            background: white;
            border-radius: 16px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }
        h1 { color: #333; text-align: center; margin-bottom: 10px; }
        .subtitle { text-align: center; color: #666; margin-bottom: 30px; }
        
        .tab-nav { display: flex; gap: 10px; margin-bottom: 20px; }
        .tab-btn {
            flex: 1;
            padding: 12px;
            border: none;
            background: #f0f0f0;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            transition: all 0.3s;
        }
        .tab-btn.active { background: #667eea; color: white; }
        
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; color: #333; font-weight: 500; }
        input, select, textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        input:focus, select:focus, textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .btn {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
        }
        .btn:hover { transform: translateY(-2px); }
        
        .result {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            margin-top: 20px;
            display: none;
        }
        .result.show { display: block; }
        
        .sequence-item {
            background: white;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 10px;
            border-left: 4px solid #667eea;
        }
        .sequence-item .seq { 
            font-family: monospace; 
            font-size: 14px;
            word-break: break-all;
            color: #333;
        }
        .sequence-item .meta {
            margin-top: 8px;
            font-size: 12px;
            color: #666;
        }
        
        .score-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }
        .score-high { background: #d4edda; color: #155724; }
        .score-mid { background: #fff3cd; color: #856404; }
        .score-low { background: #f8d7da; color: #721c24; }
        
        .paper-item {
            padding: 15px;
            border-bottom: 1px solid #eee;
        }
        .paper-item:last-child { border-bottom: none; }
        .paper-title { font-weight: 600; color: #333; }
        .paper-meta { font-size: 12px; color: #666; margin-top: 5px; }
        
        .loading { text-align: center; padding: 20px; color: #666; }
        
        .mode-badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            margin-left: 10px;
        }
        .mode-local { background: #e3f2fd; color: #1565c0; }
        .mode-public { background: #e8f5e9; color: #2e7d32; }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <h1>🧬 ResearchHub</h1>
            <p class="subtitle">AI蛋白/肽设计与文献研究平台</p>
            
            <div class="tab-nav">
                <button class="tab-btn active" onclick="switchTab('design')">🧪 蛋白设计</button>
                <button class="tab-btn" onclick="switchTab('search')">🔍 论文搜索</button>
                <button class="tab-btn" onclick="switchTab('notebook')">📓 笔记本</button>
            </div>
            
            <!-- 蛋白设计界面 -->
            <div id="design-tab">
                <div class="form-group">
                    <label>设计类型</label>
                    <select id="designType">
                        <option value="amp">抗菌肽 (AMP)</option>
                        <option value="random">随机蛋白</option>
                        <option value="diverse">多样化集合</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label>序列长度</label>
                    <input type="text" id="lengthRange" placeholder="15-25" value="15-25">
                </div>
                
                <div class="form-group">
                    <label>生成数量</label>
                    <input type="number" id="numSequences" value="5" min="1" max="20">
                </div>
                
                <button class="btn" onclick="generatePeptides()">🚀 生成序列</button>
                
                <div id="design-result" class="result">
                    <h3>生成结果</h3>
                    <div id="sequences"></div>
                </div>
            </div>
            
            <!-- 论文搜索界面 -->
            <div id="search-tab" style="display:none;">
                <div class="form-group">
                    <label>搜索关键词</label>
                    <input type="text" id="searchQuery" placeholder="输入研究主题...">
                </div>
                
                <div class="form-group">
                    <label>数据源</label>
                    <select id="searchSource">
                        <option value="arxiv">arXiv</option>
                        <option value="openalex">OpenAlex</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label>返回数量</label>
                    <input type="number" id="maxResults" value="5" min="1" max="20">
                </div>
                
                <button class="btn" onclick="searchPapers()">🔍 搜索论文</button>
                
                <div id="search-result" class="result">
                    <h3>搜索结果</h3>
                    <div id="papers"></div>
                </div>
            </div>
            
            <!-- 笔记本界面 -->
            <div id="notebook-tab" style="display:none;">
                <div class="form-group">
                    <label>笔记本名称</label>
                    <input type="text" id="notebookTitle" placeholder="我的研究...">
                </div>
                
                <button class="btn" onclick="createNotebook()">📓 创建笔记本</button>
                
                <div id="notebook-result" class="result">
                    <h3>我的笔记本</h3>
                    <div id="notebooks"></div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        function switchTab(tab) {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            event.target.classList.add('active');
            
            document.getElementById('design-tab').style.display = tab === 'design' ? 'block' : 'none';
            document.getElementById('search-tab').style.display = tab === 'search' ? 'block' : 'none';
            document.getElementById('notebook-tab').style.display = tab === 'notebook' ? 'block' : 'none';
        }
        
        async function generatePeptides() {
            const resultDiv = document.getElementById('design-result');
            const seqDiv = document.getElementById('sequences');
            
            resultDiv.classList.add('show');
            seqDiv.innerHTML = '<div class="loading">🧪 生成中...</div>';
            
            const data = {
                type: document.getElementById('designType').value,
                length_range: document.getElementById('lengthRange').value,
                num: parseInt(document.getElementById('numSequences').value)
            };
            
            try {
                const response = await fetch('/api/generate', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                const result = await response.json();
                
                seqDiv.innerHTML = '';
                result.sequences.forEach((seq, i) => {
                    const scoreClass = seq.score >= 0.7 ? 'score-high' : (seq.score >= 0.4 ? 'score-mid' : 'score-low');
                    seqDiv.innerHTML += `
                        <div class="sequence-item">
                            <div class="seq">${seq.sequence}</div>
                            <div class="meta">
                                <span class="score-badge ${scoreClass}">评分: ${seq.score.toFixed(2)}</span>
                                | 电荷: ${seq.charge} | 疏水性: ${seq.hydrophobicity.toFixed(2)}
                            </div>
                        </div>
                    `;
                });
            } catch(e) {
                seqDiv.innerHTML = '<div style="color:red;">错误: ' + e.message + '</div>';
            }
        }
        
        async function searchPapers() {
            const resultDiv = document.getElementById('search-result');
            const papersDiv = document.getElementById('papers');
            
            resultDiv.classList.add('show');
            papersDiv.innerHTML = '<div class="loading">🔍 搜索中...</div>';
            
            const data = {
                query: document.getElementById('searchQuery').value,
                source: document.getElementById('searchSource').value,
                max_results: parseInt(document.getElementById('maxResults').value)
            };
            
            try {
                const response = await fetch('/api/search', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                const result = await response.json();
                
                papersDiv.innerHTML = '';
                result.papers.forEach(p => {
                    papersDiv.innerHTML += `
                        <div class="paper-item">
                            <div class="paper-title">${p.title}</div>
                            <div class="paper-meta">${p.authors} | ${p.published}</div>
                        </div>
                    `;
                });
            } catch(e) {
                papersDiv.innerHTML = '<div style="color:red;">错误: ' + e.message + '</div>';
            }
        }
        
        async function createNotebook() {
            const resultDiv = document.getElementById('notebook-result');
            const nbDiv = document.getElementById('notebooks');
            
            resultDiv.classList.add('show');
            
            const data = { title: document.getElementById('notebookTitle').value };
            
            try {
                const response = await fetch('/api/notebook', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                const result = await response.json();
                
                nbDiv.innerHTML = `<div style="color:green;">✅ 笔记本创建成功: ${result.title}</div>`;
            } catch(e) {
                nbDiv.innerHTML = '<div style="color:red;">错误: ' + e.message + '</div>';
            }
        }
    </script>
</body>
</html>
'''

# ========== API 路由 ==========

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/generate', methods=['POST'])
def generate():
    data = request.json
    
    gen = ProteinGenerator()
    eval = SequenceEvaluator()
    
    results = []
    
    if data['type'] == 'amp':
        length_range = tuple(map(int, data['length_range'].split('-')))
        peptides = gen.generate_antimicrobial_peptide(length_range, data['num'])
        
        for p in peptides:
            eval_result = eval.evaluate_antimicrobial_potential(p['sequence'])
            results.append({
                'sequence': p['sequence'],
                'score': eval_result['amp_score'],
                'charge': p['charge'],
                'hydrophobicity': p['hydrophobicity']
            })
    
    return jsonify({'sequences': results})

@app.route('/api/search', methods=['POST'])
def search():
    data = request.json
    
    agent = SearchAgent()
    papers = agent.search(data['query'], data['source'], data['max_results'])
    
    return jsonify({
        'papers': [
            {
                'title': p['title'][:100],
                'authors': ', '.join(p['authors'][:3]),
                'published': p['published'][:10]
            }
            for p in papers
        ]
    })

@app.route('/api/notebook', methods=['POST'])
def notebook():
    data = request.json
    
    db = Database()
    nb_id = db.create_notebook(data['title'])
    
    return jsonify({'id': nb_id, 'title': data['title']})

# ========== 运行配置 ==========

def run(host='0.0.0.0', port=5000, debug=False):
    """运行服务器"""
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='ResearchHub Web App')
    parser.add_argument('--host', default='0.0.0.0', help='Host地址')
    parser.add_argument('--port', type=int, default=5000, help='端口')
    parser.add_argument('--local', action='store_true', help='本地模式(仅localhost)')
    
    args = parser.parse_args()
    
    host = '127.0.0.1' if args.local else args.host
    
    print(f"""
🧬 ResearchHub Web 启动中...
   
   本地模式: http://localhost:{args.port}
   {'(仅本机访问)' if args.local else '(可外网访问)'}
   
   按 Ctrl+C 停止
    """)
    
    run(host=host, port=args.port, debug=True)
