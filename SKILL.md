---
name: thoracic-weekly-academy
description: Generate Chinese weekly thoracic-surgery academic progress reports from PubMed and export a Word document. Use when the user asks to summarize last week's thoracic research progress, weekly thoracic surgery literature, PubMed epdat reports, or reports covering lung cancer, mediastinal tumors, esophageal cancer, and a combined non-oncologic thoracic group covering pneumothorax, chest trauma, rib fracture, and chest wall deformity across a fixed high-impact journal scope.
---

# Thoracic Weekly Academy

## Purpose

Produce a Word report matching Dr. Chutong Lin's weekly thoracic academic review style:

- PubMed search is strictly limited to the previous natural week, Monday-Sunday, using `Electronic Date of Publication [epdat]`.
- Disease scope is lung cancer, mediastinal tumors, esophageal cancer, and a combined fourth section covering pneumothorax, chest trauma, rib fracture, and chest wall deformity.
- Each disease is organized into clinical research, artificial intelligence/machine learning research, and other basic/translational research.
- The report is written in Chinese, uses numbered in-text citations such as `[1]`, and formats references in AMA style.
- When adjacent citations appear together, merge them into compact ranges, e.g. write `[1-3]` instead of `[1][2][3]`, and `[1,3-5]` instead of `[1][3][4][5]`.
- Literature-review paragraphs should be relatively detailed: summarize study design/population or model/data source, key endpoint or method, main finding, and clinical/methodological implication rather than only translating titles.
- Each included-article summary table in the body must show cached JCR quartile, impact factor, and 新锐分区 values from `references/journal_metrics.json`.
- By default, do not include a standalone JCR/impact-factor/新锐分区 appendix table in the Word report. Add the standalone appendix table only when the user explicitly asks for it.

## Required Workflow

1. Read `references/workflow.md` for the search, screening, categorization, and report rules.
2. Use `references/journal_metrics.json` when constructing PubMed journal queries and when generating included-article summary tables. Do not perform live web lookups for routine journal metrics.
3. Run `scripts/search_pubmed_weekly.py` to search PubMed and fetch abstracts. If the user does not specify dates, use the previous natural week relative to the current date.
4. Screen every retrieved record. Do not summarize from titles alone. Exclude news, research summaries, comments, replies, author reflections, non-target-disease false positives, and records not substantially about the four target diseases.
5. Create a structured content JSON following `references/report_content_schema.json`.
6. Run `scripts/build_report_docx.py` to generate the Word report.
7. Use the Documents skill render workflow to render the `.docx` to page images, inspect the result, and iterate until clean.

## Output Expectations

The final response should link only to the final `.docx` unless the user asks for intermediate files. Mention the search week, included count, excluded count, and whether visual render QA was completed.

## Static Journal Metrics

`references/journal_metrics.json` contains the user-defined journal scope plus cached JCR quartile, impact factor, and 新锐分区 values:

- JCR/IF source: `/Users/linastro/Documents/LinDocuments/文稿/医学/胸外pro/7职务/宣传/公众号/※科研周报/JCR 2025所有期刊影响因子.xlsx`, using workbook columns `2025 JIF` and `JIF quartile`.
- 新锐分区 source: `/Users/linastro/Documents/LinDocuments/文稿/医学/胸外pro/7职务/宣传/公众号/※科研周报/2026新锐分区.xlsx`, using workbook columns `新锐分区` and `类型`.
- Updated: 2026-06-22.
- Treat `new_talent_quartile` as the latest 新锐分区. Do not substitute `JCI quartile` when `new_talent_quartile` is null; omit 新锐分区 for that journal until manually updated.
- Do not display TOP information in the report.
- Use these cached values in every included-article summary table to display `JCR/IF/新锐`.
- Display `未缓存` if an included journal cannot be matched by full journal title, abbreviation, or PubMed journal term.
- Refresh the file only when the user asks to update metrics or when a newer JCR release is required.
