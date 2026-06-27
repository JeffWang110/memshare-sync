#!/usr/bin/env python3
"""
MemPalace 導入腳本
將 NotebookLM 導出的記憶導入 MemPalace 向量資料庫
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

try:
    import chromadb
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    print("⚠ chromadb 未安裝，將使用模擬模式")

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠ openai 未安裝，將使用模擬嵌入")

class MemPalaceImporter:
    """MemPalace 導入器"""
    
    def __init__(self, palace_path: str = "~/.mempalace/palace"):
        self.palace_path = Path(palace_path).expanduser()
        self.collection_name = "mempalace_drawers"
        self.client = None
        self.collection = None
        
    def connect(self):
        """連接 MemPalace"""
        if not CHROMADB_AVAILABLE:
            print("使用模擬模式（chromadb 未安裝）")
            return
            
        self.client = chromadb.PersistentClient(path=str(self.palace_path))
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name
        )
        print(f"✓ 已連接 MemPalace: {self.palace_path}")
    
    def generate_embedding(self, text: str) -> List[float]:
        """生成文字嵌入向量"""
        
        if OPENAI_AVAILABLE:
            client = OpenAI()
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            return response.data[0].embedding
        else:
            # 模擬嵌入（僅用於測試）
            hash_obj = hashlib.md5(text.encode())
            hash_int = int(hash_obj.hexdigest(), 16)
            # 生成 1536 維的偽向量
            return [(hash_int % 1000) / 1000.0] * 1536
    
    def classify_to_wing(self, category: str) -> str:
        """將 NotebookLM 分類對應到 MemPalace wing"""
        
        mapping = {
            '財經投資': 'finance',
            '地緣政治': 'memory',
            '人物 / 訪談': 'identity',
            '教學指南 (For X)': 'technical',
            'Claude 生態系': 'workspace',
            'MCP 協議': 'technical',
            'OpenClaw 生態系': 'workspace',
            '記憶系統': 'memory',
            '模型 / 工具': 'technical',
            '通用 AI Agent': 'technical',
            '自我成長': 'consciousness',
            '宗教哲學': 'consciousness',
            '健康醫學': 'technical',
            '企業 / 資安': 'workspace',
            '產業趨勢': 'workspace',
            '組織經營': 'workspace',
            '其他': 'memory'
        }
        
        return mapping.get(category, 'memory')
    
    def import_memory(self, memory_data: Dict) -> str:
        """導入單個記憶"""
        
        # 生成記憶 ID
        memory_id = f"nlm-{memory_data['notebook_id']}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # 準備內容
        content = memory_data.get('content', {})
        summary = content.get('summary', '')
        
        if not summary:
            # 如果沒有摘要，使用標題
            summary = memory_data.get('title', '')
        
        # 分類
        category = memory_data.get('category', '其他')
        wing = self.classify_to_wing(category)
        tags = memory_data.get('tags', [])
        
        # 生成嵌入
        embedding = self.generate_embedding(summary)
        
        # 準備元數據
        metadata = {
            'source': 'notebooklm',
            'notebook_id': memory_data['notebook_id'],
            'notebook_title': memory_data.get('title', ''),
            'category': category,
            'wing': wing,
            'tags': ','.join(tags) if tags else '',
            'created_date': memory_data.get('created_at', ''),
            'imported_at': datetime.now().isoformat()
        }
        
        # 存入 MemPalace
        if self.collection:
            self.collection.add(
                ids=[memory_id],
                embeddings=[embedding],
                documents=[summary],
                metadatas=[metadata]
            )
            print(f"✓ 已導入記憶: {memory_id}")
        else:
            print(f"[模擬] 導入記憶: {memory_id}")
        
        return memory_id
    
    def search(self, query: str, n_results: int = 10) -> List[Dict]:
        """搜尋記憶"""
        
        # 生成查詢向量
        query_embedding = self.generate_embedding(query)
        
        if not self.collection:
            return []
        
        # 向量搜尋
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where={'source': 'notebooklm'},
            include=['documents', 'metadatas', 'distances']
        )
        
        # 格式化結果
        formatted = []
        for i, doc in enumerate(results['documents'][0]):
            metadata = results['metadatas'][0][i]
            distance = results['distances'][0][i]
            
            formatted.append({
                'content': doc,
                'source': 'NotebookLM',
                'notebook_id': metadata.get('notebook_id'),
                'notebook_title': metadata.get('notebook_title'),
                'category': metadata.get('category'),
                'relevance': 1 - distance,
                'tags': metadata.get('tags', '').split(',') if metadata.get('tags') else []
            })
        
        return formatted
    
    def get_sync_status(self) -> Dict[str, bool]:
        """獲取已同步的筆記本狀態"""
        
        if not self.collection:
            return {}
        
        # 查詢所有來自 NotebookLM 的記憶
        results = self.collection.get(
            where={'source': 'notebooklm'},
            include=['metadatas']
        )
        
        status = {}
        for metadata in results['metadatas']:
            nb_id = metadata.get('notebook_id')
            if nb_id:
                status[nb_id] = True
        
        return status


def create_memory_template(notebook_id: str, title: str, category: str) -> Dict:
    """創建記憶模板"""
    
    return {
        'memory_id': f"nlm-{notebook_id}",
        'notebook_id': notebook_id,
        'title': title,
        'category': category,
        'content': {
            'summary': '請填寫筆記本摘要',
            'key_concepts': ['概念1', '概念2'],
            'qa_pairs': [
                {'q': '問題1', 'a': '答案1'},
                {'q': '問題2', 'a': '答案2'}
            ]
        },
        'tags': [],
        'created_at': datetime.now().isoformat()
    }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='MemPalace 導入工具')
    parser.add_argument('--palace-path', default='~/.mempalace/palace',
                       help='MemPalace 路徑')
    parser.add_argument('--import-file', '-i', help='導入 JSON 檔案')
    parser.add_argument('--search', '-s', help='搜尋記憶')
    parser.add_argument('--status', action='store_true', help='顯示同步狀態')
    parser.add_argument('--create-template', '-t', help='創建記憶模板（指定筆記本 ID）')
    parser.add_argument('--title', help='筆記本標題（用於模板）')
    parser.add_argument('--category', default='其他', help='筆記本分類')
    
    args = parser.parse_args()
    
    importer = MemPalaceImporter(palace_path=args.palace_path)
    importer.connect()
    
    if args.import_file:
        # 導入檔案
        with open(args.import_file) as f:
            memory_data = json.load(f)
        
        memory_id = importer.import_memory(memory_data)
        print(f"記憶已導入: {memory_id}")
    
    elif args.search:
        # 搜尋
        results = importer.search(args.search)
        print(f"\n搜尋結果 ({len(results)} 筆):")
        for i, r in enumerate(results, 1):
            print(f"\n{i}. {r['notebook_title']}")
            print(f"   分類: {r['category']}")
            print(f"   相關度: {r['relevance']:.2%}")
            print(f"   內容: {r['content'][:100]}...")
    
    elif args.status:
        # 顯示狀態
        status = importer.get_sync_status()
        print(f"已同步筆記本: {len(status)} 本")
        for nb_id in list(status.keys())[:10]:
            print(f"  - {nb_id}")
    
    elif args.create_template:
        # 創建模板
        template = create_memory_template(
            args.create_template,
            args.title or '未命名筆記本',
            args.category
        )
        
        output_file = f"exports/{args.create_template}/memory.json"
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(template, f, ensure_ascii=False, indent=2)
        
        print(f"✓ 已創建記憶模板: {output_file}")
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()