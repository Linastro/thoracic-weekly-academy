---
name: thoracic-weekly-academy
description: Generate Chinese weekly thoracic-surgery academic progress reports from PubMed and export a Word document. Use when the user asks to summarize last week's thoracic research progress, weekly thoracic surgery literature, PubMed epdat reports, or reports covering lung cancer, mediastinal tumors, esophageal cancer, and pneumothorax across a fixed high-impact journal scope.
---

# Thoracic Weekly Academy

## Purpose

Produce a Word report matching Dr. Chutong Lin's weekly thoracic academic review style:

- PubMed search is strictly limited to the previous natural week, Monday-Sunday, using `Electronic Date of Publication [epdat]`.
- Disease scope is lung cancer, mediastinal tumors, esophageal cancer, and pneumothorax.
- Each disease is organized into clinical research, artificial intelligence/machine learning research, and other basic/translational research.
- The report is written in Chinese, uses numbered in-text citations such as `[1]`, and formats references in AMA style.
- Each included-article summary table in the body must show cached JCR quartile and impact factor values from `references/journal_metrics.json`.
- By default, do not include a standalone JCR/impact-factor appendix table in the Word report. Add the standalone appendix table only when the user explicitly asks for it.

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

`references/journal_metrics.json` contains the user-defined journal scope plus cached JCR quartile and impact factor values:

- Source: 2025 JCR list, using 2024 Journal Impact Factor.
- Created: 2026-06-09.
- Use these cached values in every included-article summary table to display `JCR/IF`.
- Display `未缓存` if an included journal cannot be matched by full journal title, abbreviation, or PubMed journal term.
- Refresh the file only when the user asks to update metrics or when a newer JCR release is required.
