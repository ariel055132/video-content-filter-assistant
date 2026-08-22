# 影片內容篩選助理

[English](README.md) | [繁體中文](README.zh-TW.md)

> 一套在觀看影片前，協助你判斷影片是否值得投入注意力的 AI 輔助工作流程。

影片內容篩選助理會檢查影片的來源資訊與可取得的逐字稿、重建主要論點、評估實用性與可信度，最後提出以下五種觀看建議之一：

- 略過
- 只讀 AI 摘要
- 觀看重點片段
- 完整觀看
- 深入研讀

這個專案的目的不是讓 AI 取代學習，而是讓 Assistant 成為一道**注意力閘門**：減少花在重複、來源薄弱或低價值內容上的時間，同時保留真正值得觀看的影片。

## 這個儲存庫提供什麼

本專案是一套以 Markdown 為核心、由 Assistant 執行的半自動工作流程，而不是已完全自動化的影片下載應用程式。它提供：

- 等待分析的影片佇列
- 在成本與可信度之間取捨的兩種分析層級
- 包含結構化 metadata 的標準報告範本
- 同時衡量注意力價值與內容品質的雙評分系統
- 每支來源影片一份獨立 Markdown 報告
- 用來瀏覽所有報告的自動產生索引
- 驗證報告 metadata 與索引產生結果的測試
- 來源查證、逐字稿處理與暫存媒體清理規則

AI Assistant 會依照 [`AGENTS.md`](AGENTS.md) 的作業契約，以及 [`PROJECT_BRIEF.txt`](PROJECT_BRIEF.txt) 的專案目標，執行研究與分析工作。

## 運作方式

```text
影片網址或本機來源
        │
        ▼
取得權威來源的 metadata
        │
        ▼
選擇 quick-screen 或 full-transcript
        │
        ▼
取得並驗證可用素材
        │
        ▼
重建主張並評估可信度
        │
        ▼
評估注意力價值與內容品質
        │
        ▼
每支影片建立一份 Markdown 報告
        │
        ▼
重建並驗證 INDEX.md
```

### 分析層級

| 層級 | 分析依據 | 適合情境 | 限制 |
|---|---|---|---|
| `quick-screen` | 原始 metadata、說明欄、章節、創作者摘要，以及明確標示的逐字稿片段 | 快速、低成本的大量初篩 | 結論是暫定的，不得宣稱已完整理解影片 |
| `full-transcript` | 已對照完整片長的逐字稿，以及必要的外部查證 | 正式的觀看決策與批判分析 | 需要更多時間及可靠的逐字稿來源 |

當現有素材不足、需要精準時間碼，或影片涉及重要的科學、醫療、法律或財務主張時，應將快速初篩升級為完整逐字稿分析。

## 推薦與評分模型

每份新報告都會保留兩種用途不同的分數：

1. **推薦程度：1～10 分**

   回答：「這支原片是否值得投入注意力？」

2. **內容品質：5～25 分**

   由相關性、資訊密度、原創性、來源品質及行動價值五個項目組成，每項 1～5 分。

內容品質分數對應的預設動作如下：

| 內容品質 | 預設動作 |
|---:|---|
| 5～10 | 略過 |
| 11～15 | 只讀 AI 摘要 |
| 16～20 | 觀看重點片段 |
| 21～23 | 完整觀看 |
| 24～25 | 深入研讀 |

如果有明確理由，例如影片的核心價值來自視覺示範，Assistant 可以覆寫預設動作，但必須在報告中解釋原因。

## 專案結構

```text
.
├── AGENTS.md                  # Assistant 的長期作業契約
├── PROJECT_BRIEF.txt          # 專案目的、流程與分析提示詞
├── README.md                  # 英文專案說明
├── README.zh-TW.md            # 繁體中文專案說明
├── INDEX.md                   # 自動產生的報告索引，請勿手動編輯
├── inbox/
│   └── queue.md               # 等待分析的影片佇列
├── summaries/                 # 每支影片一份獨立 Markdown 報告
├── templates/
│   └── video-summary.md       # 新報告必須使用的結構
├── tools/
│   └── rebuild_index.py       # 建立並驗證 INDEX.md
└── tests/
    └── test_rebuild_index.py  # 索引與格式測試
```

## 快速開始

### 1. 將影片加入佇列

在 [`inbox/queue.md`](inbox/queue.md) 中加入一列，每列只放一個來源。如果不確定分析層級，先選擇 `quick-screen`，Assistant 可在初篩後建議是否升級。

```markdown
| URL | analysis_level | 來源 | 標籤 | 優先度 | 狀態 | 備註／輸出檔 |
|---|---|---|---|---|---|---|
| https://example.com/video | quick-screen | manual | AI、產品 | normal | inbox | |
```

### 2. 請 Assistant 處理影片

使用具備網頁存取、逐字稿取得能力，並能寫入本儲存庫的 AI 程式助理。例如：

```text
請先閱讀 PROJECT_BRIEF.txt 與 AGENTS.md，再處理下一個 inbox 項目。
依照指定的分析層級，使用 templates/video-summary.md，為每支來源影片
建立一份獨立報告，接著更新佇列、重建 INDEX.md，並執行驗證。
除非逐字稿已涵蓋完整影片，否則不得宣稱完成 full-transcript 分析。
```

也可以直接提交影片來源：

```text
請使用 full-transcript 模式分析這支影片：
<影片網址、本機影片路徑、字幕路徑或逐字稿路徑>

請將結果儲存成 summaries/ 下的一份獨立 Markdown 報告。
```

### 3. 重建報告索引

```bash
python3 tools/rebuild_index.py
```

工具會同時讀取目前格式與舊版報告，接著重新產生 [`INDEX.md`](INDEX.md)，但不會改寫既有報告。

### 4. 驗證儲存庫

```bash
python3 tools/rebuild_index.py --check
python3 -m unittest discover -s tests -v
```

目前的索引器與測試只使用 Python 標準函式庫。

### 5. 交付後追蹤與發佈

影片或 Podcast 報告交付後，建立一次性的 30 分鐘後提醒，請使用者寫下一段簡短的個人總結，其中包含最重要的觀點、自己的判斷，以及一個後續行動。這能將 Assistant 的篩選結果與使用者自己的學習反思清楚分開。

完成的報告統一保存於 `summaries/`。在這台工作站上，GitHub 發佈 clone 為 `/Users/adrianli/Documents/GitHub/video-content-filter-assistant`。發佈前必須重建 `INDEX.md`、執行兩項驗證、檢查 Git diff，確認無誤後才 commit 與 push。若發佈 clone 已有無關或未合併的變更，應停止發佈，不可直接覆寫。

## 如何實作 Assistant

這個 Assistant 可以實作於 Codex 或其他具備工具操作能力的 AI Agent。重點不是使用特定模型或 SDK，而是落實可靠的工作流程與持久化的輸出契約。

### 必要能力

Agent 應具備以下能力：

- 讀取與寫入儲存庫內的 Markdown 檔案
- 檢查原始影片頁面並取得權威 metadata
- 取得創作者字幕、平台字幕或可靠且對應同一影片的公開逐字稿
- 沒有逐字稿時，視授權情況轉錄本機音訊
- 使用一手或權威來源查證高風險事實主張
- 執行 Python 索引器與測試套件
- 完成分析後，以明確路徑逐一刪除暫存媒體

### 處理演算法

Assistant 應針對佇列中的每個項目執行以下步驟：

1. 閱讀 `PROJECT_BRIEF.txt`、`AGENTS.md` 與報告範本。
2. 將佇列狀態從 `inbox` 更新為 `processing`。
3. 優先從原始平台確認標題、創作者、網址、片長、發布日期、說明與章節。
4. 選擇或確認分析層級。
5. 依序取得素材：創作者逐字稿、平台逐字稿、可靠且對應同一影片的公開逐字稿，最後才是經授權的本機音訊轉錄。
6. 將逐字稿覆蓋範圍與影片片長互相核對，並揭露所有重要缺漏。
7. 在評價內容前，先重建中心論點、支持主張、例子、來源、結論與建議行動。
8. 區分創作者的主張、外部查證的事實與 Assistant 自己的推論。
9. 評估實用性、適合觀眾、推理品質、風險標記，以及值得觀看的段落。
10. 填寫兩種分數，並選擇一個允許的觀看建議。
11. 每支成功分析的影片建立一份 `summaries/YYYY-MM-DD-video-ID-short-title.md`。
12. 完成時將佇列更新為 `completed`；缺少必要素材時改為 `needs-input`。
13. 重建索引並執行驗證。
14. 建立一次性的 30 分鐘後提醒，請使用者寫下自己的總結、判斷與一個後續行動。
15. 將已驗證的專案與 `summaries/` 同步到設定的 GitHub 發佈 clone，檢查 diff 後，在 clone 乾淨時 commit 並 push。
16. 逐一清理暫存媒體。

### 輸出契約

所有新報告都必須使用 [`templates/video-summary.md`](templates/video-summary.md)，並包含類似以下內容的 YAML front matter：

```yaml
---
schema_version: 1
document_type: video-summary
analysis_level: quick-screen
status: complete
title: "範例影片"
video_id: "stable-video-id"
url: "https://example.com/video"
platform: "範例平台"
creator: "範例創作者"
published_at: "YYYY-MM-DD"
duration: "HH:MM:SS"
analyzed_at: "YYYY-MM-DD"
source: "manual"
tags: [example]
recommendation: summary-only
recommendation_score: 5
quality_score: 13
transcript_coverage: partial
confidence: medium
---
```

`recommendation` 只允許以下值：

- `skip`
- `summary-only`
- `selected-sections`
- `full-watch`
- `deep-study`

每份報告還必須包含來源 metadata、一句話總結、核心重點、實用性評估、適合觀眾、批判分析、推薦理由、值得觀看的段落或時間碼、五項內容品質分數、可信度與限制、實際解讀，以及媒體清理狀態。

### 批次與播放清單處理

輸出單位永遠是一支來源影片，而不是一次請求或一份播放清單。如果播放清單中有十支影片成功完成分析，就必須建立十份獨立報告。可以另外建立播放清單總覽，但不能用總覽取代每支影片的獨立報告。

完成批次前必須確認：

- 成功分析的影片數量等於新增的獨立報告數量
- 每個集合或播放清單項目都能連到對應報告
- 儲存庫索引已更新

## 可靠性與安全原則

- 不得將標題、說明、留言或逐字稿片段當成對完整影片的理解。
- 清楚標記不確定之處、缺少的素材及轉錄錯誤。
- 優先使用原始平台 metadata 與第一方逐字稿。
- 使用一手或權威來源查證重大或低信心主張。
- 如果影片價值依賴視覺或聲音，必須標記為需要觀看原片。
- 不得在 `summaries/` 保存完整受版權保護的逐字稿或下載媒體。
- 暫存媒體只保留到必要工作完成，之後依明確路徑逐一刪除。
- 不得只為採用新版格式而批次改寫舊報告。
- `INDEX.md` 是衍生檔，不得手動編輯。

## 目前範圍

目前已包含：

- Assistant 作業契約
- 佇列與報告規範
- 可重複使用的報告範本
- 向下相容舊報告的 Markdown 索引器
- 格式與索引驗證測試
- 持續增加的影片分析報告

目前尚未封裝成單一自動化應用程式的功能：

- 各影片平台專用的影片或字幕下載器
- 轉錄引擎或語音辨識模型
- 託管式網頁介面
- 背景工作排程器

未來可以整合這些元件，而不需要改變核心報告契約。

## 創作來源

本專案的創作靈感來自 Bilibili 創作者 LunaticMosfet 的影片[《【旧世代电台】新年的内容消费行动建议》](https://www.bilibili.com/video/BV1AAZyBGEtP/)。這支影片促使本專案思考一個核心問題：在投入時間消費一項內容之前，能不能先判斷它是否值得占用注意力？

本儲存庫是在此概念上的獨立實作，進一步將其延伸為可重複使用的 AI 輔助工作流程，用於蒐集資料、重建論點、評估品質，以及決定要對一支影片投入多深的注意力。

## 核心理念

> 在影片內容進入個人注意力之前，應先通過一道篩選流程。

AI 應協助人類判斷**哪些內容值得投入注意力**；真正的學習、判斷與行動，仍由人類負責。
