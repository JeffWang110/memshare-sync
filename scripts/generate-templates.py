#!/usr/bin/env python3
"""
MemPalace 記憶模板生成器
從 NotebookLM 筆記本索引建立記憶模板
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


def create_memory_template(notebook: Dict) -> Dict:
    """從筆記本資料建立記憶模板"""
    
    return {
        'memory_id': f"nlm-{notebook['id']}",
        'notebook_id': notebook['id'],
        'title': notebook['title'],
        'category': notebook.get('category', '其他'),
        'content': {
            'summary': f"請填寫《{notebook['title']}》的摘要內容",
            'key_concepts': [
                '關鍵概念 1',
                '關鍵概念 2',
                '關鍵概念 3'
            ],
            'qa_pairs': [
                {
                    'q': f'{notebook["title"]} 的核心觀點是什麼？',
                    'a': '請填寫答案'
                },
                {
                    'q': '有哪些重要實作步驟？',
                    'a': '請填寫答案'
                }
            ],
            'sources': [],
            'related_notebooks': []
        },
        'metadata': {
            'source': 'notebooklm',
            'source_url': f"https://notebooklm.google.com/notebook/{notebook['id']}",
            'created_at': notebook.get('created_at', datetime.now().isoformat()),
            'tags': [],
            'importance': 'medium',
            'last_accessed': None,
            'access_count': 0
        },
        'mempalace': {
            'wing': classify_to_wing(notebook.get('category', '其他')),
            'room': sanitize_room_name(notebook['title']),
            'synced': False,
            'last_sync': None
        }
    }


def classify_to_wing(category: str) -> str:
    """分類對應到 MemPalace wing"""
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


def sanitize_room_name(title: str) -> str:
    """清理標題作為 room 名稱"""
    # 移除特殊字元，轉小寫，用底線連接
    import re
    clean = re.sub(r'[^\w\s-]', '', title)
    clean = re.sub(r'[\s-]+', '_', clean)
    return clean.lower()[:50]


def generate_templates_for_category(notebooks: List[Dict], category: str, output_dir: Path) -> int:
    """為特定分類生成模板"""
    
    category_notebooks = [nb for nb in notebooks if nb.get('category') == category]
    
    if not category_notebooks:
        return 0
    
    # 建立分類目錄
    category_dir = output_dir / classify_to_wing(category)
    category_dir.mkdir(parents=True, exist_ok=True)
    
    for nb in category_notebooks:
        template = create_memory_template(nb)
        template_path = category_dir / f"{nb['id']}.json"
        
        with open(template_path, 'w', encoding='utf-8') as f:
            json.dump(template, f, ensure_ascii=False, indent=2)
    
    return len(category_notebooks)


def generate_all_templates(index_path: Path, output_dir: Path) -> Dict:
    """生成所有模板"""
    
    with open(index_path) as f:
        data = json.load(f)
    
    notebooks = data['notebooks']
    categories = set(nb.get('category', '其他') for nb in notebooks)
    
    stats = {
        'total': len(notebooks),
        'categories': len(categories),
        'generated': 0,
        'by_category': {}
    }
    
    for category in categories:
        count = generate_templates_for_category(notebooks, category, output_dir)
        stats['generated'] += count
        stats['by_category'][category] = count
    
    # 生成索引
    index_file = output_dir / '_index.json'
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump({
            'generated_at': datetime.now().isoformat(),
            'stats': stats,
            'wings': {
                wing: list((output_dir / wing).glob('*.json')) if (output_dir / wing).exists() else []
                for wing in ['finance', 'workspace', 'technical', 'memory', 'identity', 'consciousness']
            }
        }, f, ensure_ascii=False, indent=2)
    
    return stats


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='MemPalace 記憶模板生成器')
    parser.add_argument('--index', '-i', default='index/notebooks-index.json',
                       help='筆記本索引檔案路徑')
    parser.add_argument('--output', '-o', default='exports/templates',
                       help='輸出目錄')
    parser.add_argument('--category', '-c', help='只生成特定分類')
    parser.add_argument('--notebook-id', '-n', help='只生成特定筆記本')
    
    args = parser.parse_args()
    
    index_path = Path(args.index)
    output_dir = Path(args.output)
    
    if not index_path.exists():
        print(f"❌ 索引檔案不存在: {index_path}")
        sys.exit(1)
    
    # 載入索引
    with open(index_path) as f:
        data = json.load(f)
    
    notebooks = data['notebooks']
    
    # 單一筆記本
    if args.notebook_id:
        nb = next((n for n in notebooks if n['id'] == args.notebook_id), None)
        if not nb:
            print(f"❌ 找不到筆記本: {args.notebook_id}")
            sys.exit(1)
        
        template = create_memory_template(nb)
        output_file = output_dir / f"{nb['id']}.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(template, f, ensure_ascii=False, indent=2)
        
        print(f"✓ 已生成模板: {output_file}")
        return
    
    # 特定分類
    if args.category:
        count = generate_templates_for_category(notebooks, args.category, output_dir)
        print(f"✓ 已生成 {count} 個模板 ({args.category})")
        return
    
    # 全部生成
    stats = generate_all_templates(index_path, output_dir)
    
    print(f"\n📊 模板生成完成")
    print(f"總筆記本: {stats['total']}")
    print(f"已生成: {stats['generated']}")
    print(f"分類數: {stats['categories']}")
    print(f"\n各分類數量:")
    for cat, count in sorted(stats['by_category'].items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count}")


if __name__ == '__main__':
    main()