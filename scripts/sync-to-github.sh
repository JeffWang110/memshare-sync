#!/bin/bash
# MemShare 同步腳本
# 將 NotebookLM 記憶同步到 GitHub

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
INDEX_DIR="$ROOT_DIR/index"
EXPORTS_DIR="$ROOT_DIR/exports"

# 顏色輸出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 檢查依賴
check_dependencies() {
    log_info "檢查依賴..."
    
    if ! command -v python3 &> /dev/null; then
        log_error "需要 python3"
        exit 1
    fi
    
    if ! command -v git &> /dev/null; then
        log_error "需要 git"
        exit 1
    fi
    
    log_info "依賴檢查通過"
}

# 解析索引
parse_index() {
    log_info "解析 NotebookLM 索引..."
    
    python3 "$SCRIPT_DIR/parse-index.py" \
        --url "https://jeff-notebooks-index.surge.sh/" \
        --output "$INDEX_DIR"
}

# 檢查是否有新的筆記本
check_new_notebooks() {
    log_info "檢查新增筆記本..."
    
    if [ ! -f "$INDEX_DIR/sync-manifest.json" ]; then
        log_warn "同步清單不存在，將創建新的"
        return 0
    fi
    
    # 比對本地和遠端索引
    # TODO: 實作詳細的比對邏輯
    
    log_info "檢查完成"
}

# 提交到 GitHub
sync_to_github() {
    log_info "同步到 GitHub..."
    
    cd "$ROOT_DIR"
    
    # 檢查是否有變更
    if git diff --quiet && git diff --staged --quiet; then
        log_info "沒有變更需要提交"
        return 0
    fi
    
    # 提交變更
    TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
    git add .
    git commit -m "sync: NotebookLM 記憶同步 $TIMESTAMP"
    
    # 推送
    if git remote | grep -q "origin"; then
        git push origin main || git push origin master
        log_info "已推送到 GitHub"
    else
        log_warn "未設定 remote origin，請手動推送"
    fi
}

# 主流程
main() {
    log_info "開始同步流程"
    
    check_dependencies
    parse_index
    check_new_notebooks
    sync_to_github
    
    log_info "同步完成"
}

# 參數處理
case "${1:-}" in
    --parse-only)
        parse_index
        ;;
    --github-only)
        sync_to_github
        ;;
    --help)
        echo "使用方式: $0 [選項]"
        echo ""
        echo "選項:"
        echo "  --parse-only   僅解析索引"
        echo "  --github-only  僅同步 GitHub"
        echo "  --help         顯示幫助"
        ;;
    *)
        main
        ;;
esac