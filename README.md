# Video Content Filter Assistant

[English](README.md) | [繁體中文](README.zh-TW.md)

> An AI-assisted workflow for deciding whether a video deserves your attention before you watch it.

Video Content Filter Assistant inspects a video's source information and available transcript, reconstructs its main argument, evaluates its usefulness and credibility, and recommends one of five actions:

- Skip
- Read the AI summary only
- Watch selected sections
- Watch the full video
- Study it deeply

The goal is not to replace learning with AI. The assistant acts as an **attention gate**, helping you spend less time on repetitive, weakly sourced, or low-value content while preserving videos that are genuinely worth watching.

## What this repository provides

This repository is a Markdown-based, assistant-driven workflow rather than a fully automated video-downloading application. It provides:

- A queue for videos waiting to be analyzed
- Two analysis levels for balancing cost and confidence
- A standard report template with structured metadata
- A dual scoring system for attention value and content quality
- One standalone Markdown report per source video
- A generated index for browsing all reports
- Validation tests for report metadata and index generation
- Operational rules for source verification, transcript handling, and temporary-media cleanup

The AI assistant performs the research and analysis steps using the contract in [`AGENTS.md`](AGENTS.md) and the project goals in [`PROJECT_BRIEF.txt`](PROJECT_BRIEF.txt).

## How it works

```text
Video URL or local source
          │
          ▼
Collect authoritative metadata
          │
          ▼
Choose quick-screen or full-transcript
          │
          ▼
Acquire and validate available evidence
          │
          ▼
Reconstruct claims and assess credibility
          │
          ▼
Score attention value and content quality
          │
          ▼
Write one Markdown report per video
          │
          ▼
Rebuild and validate INDEX.md
```

### Analysis levels

| Level | Evidence | Best for | Limitation |
|---|---|---|---|
| `quick-screen` | Original metadata, description, chapters, creator summary, and clearly labeled transcript fragments | Fast, low-cost filtering | The recommendation is provisional and must not claim full understanding |
| `full-transcript` | A transcript checked against the complete runtime, plus external verification when needed | Formal viewing decisions and critical analysis | Requires more time and reliable transcript access |

A quick screen should be upgraded to full-transcript analysis when the available evidence is insufficient, accurate timestamps are required, or the video makes consequential scientific, medical, legal, or financial claims.

## Recommendation and scoring model

Every new report keeps two separate scores:

1. **Recommendation score — 1 to 10**

   Answers: “Is the original video worth my attention?”

2. **Content quality score — 5 to 25**

   Adds five dimensions scored from 1 to 5: relevance, information density, originality, source quality, and action value.

The default action derived from the quality score is:

| Quality score | Default action |
|---:|---|
| 5–10 | Skip |
| 11–15 | Read AI summary only |
| 16–20 | Watch selected sections |
| 21–23 | Watch the full video |
| 24–25 | Study it deeply |

The assistant may override the default when there is a clear reason—for example, a visually essential demonstration—but the report must explain the decision.

## Repository structure

```text
.
├── AGENTS.md                  # Long-term operating contract for the assistant
├── PROJECT_BRIEF.txt          # Purpose, workflow, and analysis prompt
├── README.md                  # Project introduction and usage guide
├── INDEX.md                   # Generated report index; do not edit manually
├── inbox/
│   └── queue.md               # Videos waiting for analysis
├── summaries/                 # One standalone Markdown report per video
├── templates/
│   └── video-summary.md       # Required structure for new reports
├── tools/
│   └── rebuild_index.py       # Builds and validates INDEX.md
└── tests/
    └── test_rebuild_index.py  # Index and schema tests
```

## Quick start

### 1. Add a video to the queue

Add one source per row in [`inbox/queue.md`](inbox/queue.md). Choose `quick-screen` when uncertain; the assistant can recommend an upgrade later.

```markdown
| URL | analysis_level | Source | Tags | Priority | Status | Notes / output |
|---|---|---|---|---|---|---|
| https://example.com/video | quick-screen | manual | AI, product | normal | inbox | |
```

### 2. Ask an assistant to process it

Use an AI coding assistant with web access, transcript access, and permission to write inside this repository. For example:

```text
Read PROJECT_BRIEF.txt and AGENTS.md, then process the next inbox item.
Use the requested analysis level, create one report per source video from
templates/video-summary.md, update the queue, rebuild INDEX.md, and run validation.
Do not claim full-transcript analysis unless the transcript covers the full video.
```

You can also submit a source directly:

```text
Analyze this video using full-transcript mode:
<video URL, local video path, subtitle path, or transcript path>

Save the result as a standalone Markdown report under summaries/.
```

### 3. Rebuild the report index

```bash
python3 tools/rebuild_index.py
```

This reads both the current schema and older reports, then regenerates [`INDEX.md`](INDEX.md). Existing reports are not rewritten.

### 4. Validate the repository

```bash
python3 tools/rebuild_index.py --check
python3 -m unittest discover -s tests -v
```

The project currently uses only the Python standard library for indexing and tests.

### 5. Follow up and publish

After delivering a requested video or podcast report, keep it only in the Codex project's `summaries/` and leave the after-watching sentence blank. Do not publish it to GitHub or write a personal sentence on the user's behalf. If the user has not supplied their sentence yet, create one report-specific, one-time reminder for 30 minutes later. The reminder asks for the most important idea, the user's own judgment, and one next action. Do not create a reminder merely because the README or project was opened, and never turn this follow-up into a daily, weekly, or other recurring schedule.

When the user replies, write their sentence into the corresponding report. Then rebuild `INDEX.md`, run both validation commands, and sync the project and `summaries/` to `/Users/adrianli/Documents/GitHub/video-content-filter-assistant`; review the Git diff before committing and pushing. If the user declines to add a sentence, keep the report local unless they explicitly request publication anyway. If the publishing clone contains unrelated or unmerged changes, stop instead of overwriting them.

## How to implement the assistant

The assistant can be implemented in Codex or another tool-capable AI agent. The important part is not a specific model or SDK; it is enforcing a reliable workflow and a persistent output contract.

### Required capabilities

The agent should be able to:

- Read and write Markdown files in the repository
- Inspect original video pages for authoritative metadata
- Obtain creator captions, platform captions, or a matching public transcript
- Optionally transcribe authorized local audio when no transcript exists
- Browse primary or authoritative sources for high-risk factual claims
- Run the Python indexer and test suite
- Delete temporary media individually by exact path after analysis

### Processing algorithm

For each queue item, the assistant should:

1. Read `PROJECT_BRIEF.txt`, `AGENTS.md`, and the report template.
2. Change the queue status from `inbox` to `processing`.
3. Confirm the title, creator, URL, duration, publication date, description, and chapters from the original platform when available.
4. Select or confirm the analysis level.
5. Acquire evidence in this order: creator transcript, platform transcript, reliable matching public transcript, then authorized local audio transcription.
6. Check transcript coverage against the video's runtime and disclose every important gap.
7. Reconstruct the thesis, supporting claims, examples, sources, conclusion, and proposed actions before judging the content.
8. Separate the creator's claims, externally verified facts, and the assistant's own inferences.
9. Assess usefulness, suitable audience, reasoning quality, risk flags, and sections worth watching.
10. Assign both scores and one allowed recommendation.
11. Create exactly one `summaries/YYYY-MM-DD-video-ID-short-title.md` report for each successfully analyzed video.
12. Update the queue to `completed`, or to `needs-input` when essential evidence is unavailable.
13. Rebuild the index and run validation.
14. Deliver the report locally with the after-watching sentence blank. If the user has not supplied their sentence, create one report-specific reminder for 30 minutes later; never use a recurring schedule.
15. Wait for the user's personal summary, judgment, and next action, then write it into the corresponding report. Do not infer or invent this sentence.
16. Rebuild the index and rerun validation, sync the project and `summaries/` to the configured GitHub publishing clone, review the diff, then commit and push when the clone is clean. If the user declines to add a sentence, publish only when they explicitly request it.
17. Clean up temporary media one file at a time.

### Output contract

New reports must use [`templates/video-summary.md`](templates/video-summary.md) and include YAML front matter similar to:

```yaml
---
schema_version: 1
document_type: video-summary
analysis_level: quick-screen
status: complete
title: "Example video"
video_id: "stable-video-id"
url: "https://example.com/video"
platform: "Example platform"
creator: "Example creator"
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

Allowed `recommendation` values are:

- `skip`
- `summary-only`
- `selected-sections`
- `full-watch`
- `deep-study`

Each report must also include the source metadata, one-sentence summary, core points, usefulness assessment, suitable audience, critical analysis, recommendation reasons, useful sections or timestamps, the five-part quality score, confidence and limitations, a practical takeaway, and media-cleanup status.

### Batch and playlist handling

The unit of output is always one source video—not one request or playlist. If a playlist contains ten successfully analyzed videos, the assistant must create ten standalone reports. A playlist overview may be added as a separate index, but it cannot replace the individual reports.

Before completing a batch, verify that:

- The number of successfully analyzed videos equals the number of new standalone reports
- Every collection or playlist entry links to its corresponding report
- The generated repository index is current

## Reliability and safety principles

- Never present a title, description, comment, or transcript fragment as full-video understanding.
- Clearly label uncertainty, missing evidence, and transcription errors.
- Prefer original-platform metadata and first-party transcripts.
- Verify consequential or low-confidence claims with primary or authoritative sources.
- Mark videos whose value depends on visuals or audio as requiring the original media.
- Do not store full copyrighted transcripts or downloaded media in `summaries/`.
- Keep temporary media only as long as necessary, then remove each file by its exact path.
- Do not bulk-rewrite legacy reports merely to adopt a newer schema.
- Treat `INDEX.md` as generated output and never edit it manually.

## Current scope

Included today:

- The assistant operating contract
- Queue and report conventions
- A reusable report template
- A backward-compatible Markdown indexer
- Schema and index validation tests
- A growing library of analyzed video reports

Not yet bundled as a single automated application:

- Platform-specific video or subtitle downloaders
- A transcription engine or speech-recognition model
- A hosted web interface
- A background job runner

These components can be integrated later without changing the core report contract.

## Inspiration

This project was inspired by Bilibili creator LunaticMosfet's video [*【旧世代电台】新年的内容消费行动建议*](https://www.bilibili.com/video/BV1AAZyBGEtP/). It prompted the central question behind this repository: before committing time to a piece of content, can we first decide whether it deserves our attention?

This repository is an independent implementation of that idea, extending it into a repeatable AI-assisted workflow for collecting evidence, reconstructing arguments, evaluating quality, and deciding how deeply to engage with a video.

## Philosophy

> Video content should pass through a filtering workflow before it enters personal attention.

AI should help decide **what deserves attention**, while the human remains responsible for learning, judgment, and action.
