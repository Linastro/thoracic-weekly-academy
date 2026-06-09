# Thoracic Weekly Academy

Codex Skill for generating Chinese weekly thoracic-surgery academic progress reports from PubMed.

## What It Does

- Searches PubMed for the previous natural week using strict `Electronic Date of Publication [epdat]`.
- Covers lung cancer, mediastinal tumors, esophageal cancer, and pneumothorax.
- Categorizes papers into clinical research, AI/machine learning research, and other basic/translational research.
- Produces a Chinese Word report with literature-review paragraphs, article tables, AMA references, and an exclusion audit.
- Includes a cached journal scope with 2025 JCR / 2024 Journal Impact Factor values in `references/journal_metrics.json`.

## Usage

Install the folder into your global Codex skills directory:

```bash
cp -R thoracic-weekly-academy ~/.codex/skills/
```

Then invoke it in Codex:

```text
用 $thoracic-weekly-academy 帮我总结上一周的胸外科研究进展，生成 Word 报告。
```

## Contents

- `SKILL.md`: core skill instructions.
- `references/workflow.md`: search, screening, categorization, citation, and report rules.
- `references/journal_metrics.json`: fixed journal scope with cached JCR quartile and impact factor values.
- `references/report_content_schema.json`: structured content schema for Word report generation.
- `scripts/search_pubmed_weekly.py`: PubMed search and abstract-fetching utility.
- `scripts/build_report_docx.py`: Word report builder.
