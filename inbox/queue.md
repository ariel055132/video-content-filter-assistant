# 影片分析佇列

把待分析影片一列一支貼到下表。`analysis_level` 填 `quick-screen` 或 `full-transcript`；不確定時先填 `quick-screen`，由初篩結果決定是否升級。

狀態可用：`inbox`、`processing`、`needs-input`、`completed`、`skipped`。

| URL | analysis_level | 來源 | 標籤 | 優先度 | 狀態 | 備註／輸出檔 |
|---|---|---|---|---|---|---|
| https://www.youtube.com/watch?v=BwD52k--KyE&list=PLhj0Av_L8Rg9V4ZTNUTtIe9qhWk2nQs8J | full-transcript | manual | 投資、波克夏、AI | normal | completed | summaries/2026-08-20-BwD52k--KyE-巴菲特2026股東大會十大看點.md |
| https://www.youtube.com/watch?v=qMkLFdHbzSA | full-transcript | chat | 投資、價值投資、李錄 | normal | completed | summaries/2026-08-21-qMkLFdHbzSA-李錄談投資的意義.md |
| https://www.youtube.com/watch?v=Igft9InNXrc | full-transcript | chat | 投資、巴菲特、Alphabet、AI、慈善 | normal | completed | summaries/2026-08-21-Igft9InNXrc-巴菲特2026-CNBC訪談.md |
| https://www.youtube.com/watch?v=SedPLXT6__w | full-transcript | chat | 投資、巴菲特、價值投資、人生哲學 | normal | completed | summaries/2026-08-21-SedPLXT6__w-巴菲特1998佛羅里達大學演講.md |
| https://www.youtube.com/watch?v=qfnYmXcFu5o | full-transcript | chat | AI、開發工作流、Codex、AeroSpace | normal | completed | summaries/2026-08-23-qfnYmXcFu5o-AI時代的視窗與Agent工作流.md |

## 處理約定

- 一列只放一支影片；播放清單可放一列，但處理後仍要為每支成功分析的影片建立獨立摘要。
- `quick-screen` 只做初步注意力判斷，不代表讀過完整逐字稿。
- `full-transcript` 必須取得並核對完整逐字稿；若無法取得，將狀態改為 `needs-input` 並說明缺少的素材。
- 完成後把狀態改為 `completed`，在最後一欄填入 `summaries/...md`，再重建 `INDEX.md`。
