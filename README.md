# MemShare × GitHub × NotebookLM 記憶閉環同步系統

這是 MemShare 記憶閉環系統的核心同步模組，用於整合：
- **NotebookLM**：知識整理與筆記本管理
- **GitHub**：版本控制與協作
- **MemPalace**：語意記憶與向量搜尋

## 目錄結構

```
memshare-sync/
├── config.json                    # 系統配置
├── index/
│   ├── notebooks-index.json       # NotebookLM 筆記本索引
│   ├── category-map.json          # 分類對應表
│   └── sync-manifest.json         # 同步狀態追蹤
├── exports/
│   ├── {notebook-id}/             # 每本筆記本的導出
│   │   ├── metadata.json
│   │   ├── content.md
│   │   ├── sources.json
│   │   ├── qa-pairs.json
│   │   └── memory.json
│   └── _mempalace/
│       ├── memories/
│       ├── entities/
│       └── relations/
├── scripts/
│   ├── parse-index.py             # 解析 NotebookLM 索引
│   ├── export-to-mempalace.py     # 導入 MemPalace
│   ├── sync-to-github.sh          # GitHub 同步
│   └── update-index.sh            # 更新索引頁
└── README.md
```

## 使用方式

### 1. 解析 NotebookLM 索引

```bash
python3 scripts/parse-index.py --url "https://jeff-notebooks-index.surge.sh/" --output index/
```

### 2. 創建記憶模板

```bash
python3 scripts/export-to-mempalace.py \
    --create-template "e0a97da9" \
    --title "Claude-GPT-Gemini 一同建置的blender專案" \
    --category "模型 / 工具"
```

### 3. 導入記憶到 MemPalace

```bash
python3 scripts/export-to-mempalace.py --import-file exports/e0a97da9/memory.json
```

### 4. 搜尋記憶

```bash
python3 scripts/export-to-mempalace.py --search "台股投資策略"
```

### 5. 同步到 GitHub

```bash
./scripts/sync-to-github.sh
```

## 同步狀態

查看哪些筆記本已同步：

```bash
python3 scripts/export-to-mempalace.py --status
```

## 配置說明

### MemPalace 對應

NotebookLM 分類會自動對應到 MemPalace 的 topic wings：

| NotebookLM 分類 | MemPalace Wing |
|----------------|----------------|
| 財經投資 | finance |
| Claude 生態系 | workspace |
| OpenClaw 生態系 | workspace |
| 通用 AI Agent | technical |
| MCP 協議 | technical |
| 模型 / 工具 | technical |
| 記憶系統 | memory |
| 人物 / 訪談 | identity |
| 自我成長 | consciousness |
| 其他 | memory |

## 自動化

使用 cron 設定定期同步：

```bash
# 每天早上 6 點同步
0 6 * * * /home/kraft110/memshare-sync/scripts/sync-to-github.sh

# 每週日凌晨 2 點導入 MemPalace
0 2 * * 0 /home/kraft110/memshare-sync/scripts/export-to-mempalace.py --import-all
```

## 相關資源

- [完整技術規劃文檔](../memshare-github-notebooklm-plan.md)
- [NotebookLM 索引頁](https://jeff-notebooks-index.surge.sh/)
- [GitHub Repository](https://github.com/JeffWang110)
- [MemPalace 文檔](~/.mempalace/)

## 授權

MIT License