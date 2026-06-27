#!/usr/bin/env python3
"""
MemShare 統合搜尋工具
整合 NotebookLM 索引和 MemPalace 記憶搜尋
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# MemPalace 路徑
MP_PYTHON = "/home/kraft110/.local/share/uv/tools/mempalace/bin/python3"


def load_notebooks_index(index_path: str = "index/notebooks-index.json") -> Dict:
    """載入 NotebookLM 索引"""
    path = Path(index_path)
    if not path.exists():
        # 嘗試從 repo 目錄載入
        path = Path.home() / "github-pages-repos" / "memshare-sync" / index_path
    
    if not path.exists():
        return {'notebooks': [], 'total': 0}
    
    with open(path) as f:
        return json.load(f)


def search_notebooks(keyword: str, index_path: str = None) -> List[Dict]:
    """關鍵字搜尋筆記本"""
    data = load_notebooks_index(index_path)
    notebooks = data.get('notebooks', [])
    
    keyword_lower = keyword.lower()
    results = []
    
    for nb in notebooks:
        title = nb.get('title', '').lower()
        category = nb.get('category', '').lower()
        
        if keyword_lower in title or keyword_lower in category:
            results.append({
                'id': nb['id'],
                'title': nb['title'],
                'category': nb['category'],
                'created_at': nb.get('created_at', ''),
                'match_type': 'title' if keyword_lower in title else 'category'
            })
    
    return results


def filter_by_category(category: str, index_path: str = None) -> List[Dict]:
    """分類過濾"""
    data = load_notebooks_index(index_path)
    notebooks = data.get('notebooks', [])
    
    results = []
    for nb in notebooks:
        if nb.get('category') == category:
            results.append({
                'id': nb['id'],
                'title': nb['title'],
                'category': nb['category'],
                'created_at': nb.get('created_at', '')
            })
    
    return results


def list_categories(index_path: str = None) -> Dict[str, int]:
    """列出所有分類及數量"""
    data = load_notebooks_index(index_path)
    notebooks = data.get('notebooks', [])
    
    categories = {}
    for nb in notebooks:
        cat = nb.get('category', '其他')
        categories[cat] = categories.get(cat, 0) + 1
    
    return dict(sorted(categories.items(), key=lambda x: -x[1]))


def search_mempalace(query: str, wing: str = None, limit: int = 10) -> List[Dict]:
    """在 MemPalace 中進行語意搜尋"""
    import subprocess
    
    try:
        # 使用 MemPalace MCP tool
        cmd = [
            MP_PYTHON, '-c',
            f'''
from mempalace.mcp_server import tool_search
import json

results = tool_search(
    query="{query}",
    wing="{wing}" if "{wing}" else None,
    limit={limit}
)
print(json.dumps(results, ensure_ascii=False))
'''
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            print(f"⚠ MemPalace 搜尋失敗: {result.stderr}", file=sys.stderr)
            return []
        
        return json.loads(result.stdout)
        
    except FileNotFoundError:
        print(f"⚠ MemPalace 未安裝或路徑錯誤: {MP_PYTHON}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"⚠ 搜尋錯誤: {e}", file=sys.stderr)
        return []


def get_sync_status(index_path: str = None, manifest_path: str = None) -> Dict:
    """獲取同步狀態"""
    # 載入索引
    data = load_notebooks_index(index_path)
    total = data.get('total', 0)
    
    # 載入同步清單
    if manifest_path is None:
        manifest_path = Path.home() / "github-pages-repos" / "memshare-sync" / "index" / "sync-manifest.json"
    else:
        manifest_path = Path(manifest_path)
    
    if manifest_path.exists():
        with open(manifest_path) as f:
            manifest = json.load(f)
        
        github_synced = sum(1 for nb in manifest.get('notebooks', {}).values() 
                           if nb.get('github_synced'))
        mempalace_synced = sum(1 for nb in manifest.get('notebooks', {}).values() 
                               if nb.get('mempalace_synced'))
    else:
        github_synced = 0
        mempalace_synced = 0
    
    return {
        'total_notebooks': total,
        'github_synced': github_synced,
        'mempalace_synced': mempalace_synced,
        'last_updated': data.get('last_updated', ''),
        'categories': len(list_categories(index_path))
    }


def format_results(results: List[Dict], result_type: str = 'notebook') -> str:
    """格式化輸出結果"""
    if not results:
        return "沒有找到結果"
    
    output = []
    
    if result_type == 'notebook':
        for i, r in enumerate(results, 1):
            output.append(f"\n{i}. {r['title']}")
            output.append(f"   分類: {r['category']}")
            output.append(f"   ID: {r['id']}")
            if r.get('created_at'):
                output.append(f"   建立: {r['created_at']}")
    
    elif result_type == 'mempalace':
        for i, r in enumerate(results, 1):
            output.append(f"\n{i}. {r.get('notebook_title', 'Unknown')}")
            output.append(f"   相關度: {r.get('relevance', 0):.2%}")
            output.append(f"   Wing: {r.get('wing', 'N/A')}")
            output.append(f"   內容: {r.get('content', '')[:100]}...")
    
    return '\n'.join(output)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='MemShare 統合搜尋工具')
    
    # 搜尋相關
    parser.add_argument('--search', '-s', help='關鍵字搜尋筆記本')
    parser.add_argument('--category', '-c', help='分類過濾')
    parser.add_argument('--mempalace', '-m', help='在 MemPalace 中進行語意搜尋')
    parser.add_argument('--wing', '-w', help='限制 MemPalace wing')
    parser.add_argument('--limit', '-l', type=int, default=10, help='結果數量限制')
    
    # 狀態相關
    parser.add_argument('--status', action='store_true', help='顯示同步狀態')
    parser.add_argument('--list-categories', action='store_true', help='列出所有分類')
    
    # 匯入相關
    parser.add_argument('--import', dest='import_file', help='匯入記憶到 MemPalace')
    
    # 模板生成
    parser.add_argument('--generate-templates', action='store_true', help='生成所有筆記本模板')
    
    args = parser.parse_args()
    
    # 顯示狀態
    if args.status:
        status = get_sync_status()
        print("\n📊 MemShare 同步狀態")
        print("=" * 40)
        print(f"總筆記本: {status['total_notebooks']}")
        print(f"GitHub 已同步: {status['github_synced']}")
        print(f"MemPalace 已同步: {status['mempalace_synced']}")
        print(f"分類數: {status['categories']}")
        print(f"最後更新: {status['last_updated']}")
        return
    
    # 列出分類
    if args.list_categories:
        categories = list_categories()
        print("\n📚 NotebookLM 分類列表")
        print("=" * 40)
        for cat, count in categories.items():
            print(f"  {cat}: {count} 本")
        print(f"\n總計: {sum(categories.values())} 本筆記本")
        return
    
    # 關鍵字搜尋
    if args.search:
        results = search_notebooks(args.search)
        print(f"\n🔍 搜尋結果: 「{args.search}」")
        print("=" * 40)
        print(format_results(results))
        return
    
    # 分類過濾
    if args.category:
        results = filter_by_category(args.category)
        print(f"\n📂 分類: {args.category}")
        print("=" * 40)
        print(format_results(results))
        return
    
    # MemPalace 搜尋
    if args.mempalace:
        results = search_mempalace(args.mempalace, args.wing, args.limit)
        print(f"\n🧠 MemPalace 搜尋: 「{args.mempalace}」")
        print("=" * 40)
        print(format_results(results, result_type='mempalace'))
        return
    
    # 匯入記憶
    if args.import_file:
        from mempalace.mcp_server import tool_add_drawer
        import_file = Path(args.import_file)
        
        if not import_file.exists():
            print(f"❌ 檔案不存在: {import_file}")
            sys.exit(1)
        
        with open(import_file) as f:
            memory_data = json.load(f)
        
        # TODO: 呼叫 tool_add_drawer 匯入
        print(f"✓ 準備匯入: {memory_data.get('title', 'Unknown')}")
        # ... 匯入邏輯
        return
    
    # 生成模板
    if args.generate_templates:
        import subprocess
        script_path = Path.home() / "github-pages-repos" / "memshare-sync" / "scripts" / "generate-templates.py"
        subprocess.run([sys.executable, str(script_path)], check=True)
        return
    
    # 無參數時顯示幫助
    parser.print_help()


if __name__ == '__main__':
    main()