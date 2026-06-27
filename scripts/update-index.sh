#!/bin/bash
# 更新 NotebookLM 索引頁面
# 部署到 surge.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
INDEX_DIR="$ROOT_DIR/index"
DIST_DIR="$ROOT_DIR/dist"

# 顏色輸出
GREEN='\033[0;32m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

# 生成索引頁面
generate_html() {
    log_info "生成索引頁面..."
    
    python3 "$SCRIPT_DIR/generate-html.py" \
        --index "$INDEX_DIR/notebooks-index.json" \
        --output "$DIST_DIR/index.html"
}

# 部署到 surge.sh
deploy() {
    log_info "部署到 surge.sh..."
    
    cd "$DIST_DIR"
    
    if command -v surge &> /dev/null; then
        surge . jeff-notebooks-index.surge.sh
        log_info "部署完成: https://jeff-notebooks-index.surge.sh/"
    else
        log_info "surge 未安裝，請手動部署"
        log_info "檔案位置: $DIST_DIR"
    fi
}

# 主流程
main() {
    mkdir -p "$DIST_DIR"
    generate_html
    deploy
}

case "${1:-}" in
    --generate-only)
        mkdir -p "$DIST_DIR"
        generate_html
        ;;
    --deploy-only)
        deploy
        ;;
    --help)
        echo "使用方式: $0 [選項]"
        echo ""
        echo "選項:"
        echo "  --generate-only  僅生成 HTML"
        echo "  --deploy-only     僅部署"
        echo "  --help            顯示幫助"
        ;;
    *)
        main
        ;;
esac