#!/usr/bin/env python3
"""
NotebookLM 索引解析器
從 surge.sh 索引頁或本地 HTML 檔案解析筆記本列表
"""

import json
import re
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

def parse_notebooklm_index(html_content: str) -> List[Dict]:
    """從 HTML 解析 NotebookLM 索引"""
    
    # 提取 notebooks JavaScript 陣列
    pattern = r'const notebooks = (\[.*?\]);'
    match = re.search(pattern, html_content, re.DOTALL)
    
    if not match:
        raise ValueError("無法在 HTML 中找到 notebooks 陣列")
    
    notebooks_json = match.group(1)
    notebooks = json.loads(notebooks_json)
    
    return notebooks

def parse_categories(html_content: str) -> List[Dict]:
    """從 HTML 解析分類列表"""
    
    pattern = r'const categories = (\[.*?\]);'
    match = re.search(pattern, html_content, re.DOTALL)
    
    if not match:
        return []
    
    categories_json = match.group(1)
    categories = json.loads(categories_json)
    
    return categories

def load_from_url(url: str = "https://jeff-notebooks-index.surge.sh/") -> str:
    """從 URL 載入 HTML"""
    import urllib.request
    
    with urllib.request.urlopen(url) as response:
        return response.read().decode('utf-8')

def load_from_file(filepath: str) -> str:
    """從本地檔案載入 HTML"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def save_index(notebooks: List[Dict], output_path: str):
    """儲存索引為 JSON"""
    
    # 添加額外欄位
    for nb in notebooks:
        nb['synced_to_github'] = False
        nb['synced_to_mempalace'] = False
        nb['last_sync'] = None
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({
            'notebooks': notebooks,
            'total': len(notebooks),
            'last_updated': datetime.now().isoformat(),
            'source': 'jeff-notebooks-index.surge.sh'
        }, f, ensure_ascii=False, indent=2)
    
    print(f"✓ 已儲存 {len(notebooks)} 本筆記本索引到 {output_path}")

def save_categories(categories: List[Dict], output_path: str):
    """儲存分類對應表"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({
            'categories': categories,
            'last_updated': datetime.now().isoformat()
        }, f, ensure_ascii=False, indent=2)
    
    print(f"✓ 已儲存 {len(categories)} 個分類到 {output_path}")

def create_sync_manifest(notebooks: List[Dict], output_path: str):
    """創建同步清單"""
    
    manifest = {
        'version': '1.0',
        'created': datetime.now().isoformat(),
        'notebooks': {}
    }
    
    for nb in notebooks:
        manifest['notebooks'][nb['id']] = {
            'title': nb['title'],
            'category': nb['category'],
            'created_at': nb['created_at'],
            'github_synced': False,
            'mempalace_synced': False,
            'last_sync': None,
            'sync_errors': []
        }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    
    print(f"✓ 已創建同步清單到 {output_path}")

def map_category_to_wing(category: str) -> str:
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

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='NotebookLM 索引解析器')
    parser.add_argument('--url', default='https://jeff-notebooks-index.surge.sh/',
                       help='索引頁 URL')
    parser.add_argument('--file', '-f', help='本地 HTML 檔案路徑')
    parser.add_argument('--output', '-o', default='index/',
                       help='輸出目錄')
    
    args = parser.parse_args()
    
    # 載入 HTML
    if args.file:
        print(f"從本地檔案載入: {args.file}")
        html = load_from_file(args.file)
    else:
        print(f"從 URL 載入: {args.url}")
        html = load_from_url(args.url)
    
    # 解析
    notebooks = parse_notebooklm_index(html)
    categories = parse_categories(html)
    
    print(f"找到 {len(notebooks)} 本筆記本")
    print(f"找到 {len(categories)} 個分類")
    
    # 創建輸出目錄
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 儲存
    save_index(notebooks, output_dir / 'notebooks-index.json')
    save_categories(categories, output_dir / 'category-map.json')
    create_sync_manifest(notebooks, output_dir / 'sync-manifest.json')
    
    # 統計
    print("\n分類統計:")
    from collections import Counter
    category_counts = Counter(nb['category'] for nb in notebooks)
    for cat, count in category_counts.most_common():
        wing = map_category_to_wing(cat)
        print(f"  {cat}: {count} → {wing}")

if __name__ == '__main__':
    main()