# MemShare 記憶閉環 - 快速入門指南

## 系統狀態

✅ 已完成初始化：
- NotebookLM 索引解析：196 本筆記本
- 分類對應表：17 個分類
- 同步清單：已創建
- Git 倉庫：已初始化

## 當前環境

### NotebookLM 索引
- URL: https://jeff-notebooks-index.surge.sh/
- 總筆記本數: 196 本
- 最後更新: 2026-06-23

### MemPalace
- 路徑: ~/.mempalace/
- 向量資料庫: chroma.sqlite3 (約 180MB)
- 分類 wings: 9 個主題

### GitHub
- 帳號: JeffWang110
- 已認證: ✅
- 相關 repo: JeffWang110.github.io, julia-hermes-monitor 等

## 下一步操作

### 1. 創建 GitHub 遠端倉庫

```bash
# 在 GitHub 創建新倉庫（手動或使用 gh CLI）
gh repo create memshare-sync --public --description "MemShare × GitHub × NotebookLM 記憶閉環同步系統"

# 設定遠端
cd /home/kraft110/memshare-sync
git remote add origin https://github.com/JeffWang110/memshare-sync.git
git push -u origin master
```

### 2. 創建第一個記憶模板

```bash
# 為最新筆記本創建記憶模板
cd /home/kraft110/memshare-sync

python3 scripts/export-to-mempalace.py \
    --create-template "e0a97da9" \
    --title "Claude-GPT-Gemini 一同建置的blender專案" \
    --category "模型 / 工具"

# 編輯生成的模板
# exports/e0a97da9/memory.json
```

### 3. 導入記憶到 MemPalace

```bash
# 安裝依賴
pip install chromadb openai

# 導入記憶
python3 scripts/export-to-mempalace.py \
    --import-file exports/e0a97da9/memory.json
```

### 4. 搜尋記憶

```bash
# 搜尋測試
python3 scripts/export-to-mempalace.py --search "投資策略"
```

### 5. 設定定期同步

```bash
# 編輯 crontab
crontab -e

# 添加以下行
# 每天早上 6 點同步
0 6 * * * /home/kraft110/memshare-sync/scripts/sync-to-github.sh

# 每週日凌晨 2 點導入 MemPalace
0 2 * * 0 /home/kraft110/memshare-sync/scripts/export-to-mempalace.py --import-all
```

## 目錄結構

```
memshare-sync/
├── config.json                    # ✅ 系統配置
├── README.md                      # ✅ 使用說明
├── index/
│   ├── notebooks-index.json       # ✅ 196 本筆記本索引
│   ├── category-map.json          # ✅ 17 個分類對應
│   └── sync-manifest.json         # ✅ 同步狀態追蹤
├── exports/                       # 📝 待填充
│   ├── {notebook-id}/
│   └── _mempalace/
└── scripts/
    ├── parse-index.py             # ✅ 索引解析
    ├── export-to-mempalace.py     # ✅ MemPalace 導入
    ├── sync-to-github.sh           # ✅ GitHub 同步
    └── update-index.sh             # ✅ 索引更新
```

## 分類對應表

NotebookLM 分類 → MemPalace Wing：

| 分類 | 數量 | Wing |
|------|------|------|
| 財經投資 | 40 | finance |
| 其他 | 30 | memory |
| OpenClaw 生態系 | 22 | workspace |
| 通用 AI Agent | 19 | technical |
| Claude 生態系 | 17 | workspace |
| 模型 / 工具 | 13 | technical |
| 教學指南 | 13 | technical |
| 人物 / 訪談 | 8 | identity |
| 組織經營 | 6 | workspace |
| 自我成長 | 6 | consciousness |
| 記憶系統 | 5 | memory |
| MCP 協議 | 5 | technical |
| 宗教哲學 | 3 | consciousness |
| 健康醫學 | 3 | technical |
| 企業 / 資安 | 3 | workspace |
| 地緣政治 | 2 | memory |
| 產業趨勢 | 1 | workspace |

## 疑難排解

### Q: chromadb 未安裝

```bash
pip install chromadb
```

### Q: openai 未安裝

```bash
pip install openai
```

### Q: 需要設定 OpenAI API Key

```bash
export OPENAI_API_KEY='your-key-here'
```

或使用本地模型（Ollama）替代。

## 相關文檔

- [完整技術規劃](../memshare-github-notebooklm-plan.md)
- [MemPalace 配置](~/.mempalace/config.json)
- [Hermes Agent 身份](~/.mempalace/identity.txt)