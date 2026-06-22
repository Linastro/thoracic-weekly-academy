# Thoracic Weekly Academy Workflow

## Date Rule

Use the previous natural week, Monday through Sunday, strictly as:

`YYYY/MM/DD:YYYY/MM/DD[epdat]`

Example: if the current date is Tuesday 2026-06-09, use `2026/06/01:2026/06/07[epdat]`.

Do not use `[dp]`, `[pdat]`, "last 7 days", or rolling windows unless the user explicitly overrides the rule.

## Disease Queries

Use four disease groups:

1. Lung cancer
2. Mediastinal tumors
3. Esophageal cancer
4. Pneumothorax, chest trauma, rib fracture, and chest wall deformity

The bundled search script contains default MeSH/title/abstract terms. Treat the fourth group as one report section, not as four separate disease sections. If a strict mediastinal tumor search returns no records, run the supplemental broad mediastinal search in the script and manually screen those hits; do not automatically include broad hits.

When creating `review_sections`, use the fourth section disease label exactly as `气胸、胸部外伤、肋骨骨折、胸壁畸形` so the Word generator can place included articles under the combined fourth section.

## Journal Scope

Use the journal list in `journal_metrics.json`. The file also contains PubMed journal-name aliases. Split journal terms into chunks to avoid overly long PubMed URLs or E-utilities failures.

## Screening Rules

Include:

- Original clinical research.
- Systematic reviews and meta-analyses.
- High-relevance translational/basic studies.
- Mechanistic or platform reviews only when closely tied to a target disease.

Exclude:

- News, briefs, research summaries, author reflections, replies, letters without original data, editorials, and comments.
- Records only incidentally mentioning the disease.
- Studies centered on a different primary disease, even if a target disease appears in a comparator, covariate, or secondary discussion.
- False-positive fourth-group or mediastinal hits where pneumothorax, chest trauma, rib fracture, chest wall deformity, or mediastinal terms appear only as imaging signs, complication descriptors, or unrelated anatomic terms.

Always keep an excluded-record audit table with PMID, hit source, title/journal, and reason.

## Categorization

For each disease, divide included papers into:

1. `临床研究`
2. `人工智能/机器学习相关研究`
3. `其他基础研究`

Use `人工智能/机器学习相关研究` for AI/ML model development, validation, systematic reviews of AI, medical imaging AI, digital-health AI, computational prediction, or algorithmic drug-discovery studies. Use `其他基础研究` for wet-lab, omics, mechanism, animal/cell, and translational platform studies not primarily clinical.

## Report Structure

Use this order:

1. Title and search metadata.
2. Search and audit results.
3. Disease-by-disease sections.
4. For each disease/type subsection:
   - One to two relatively detailed Chinese literature review paragraphs, with citations in ascending order when possible. Cover the study design/population or model/data source, core endpoint or method, main result, and clinical/methodological implication; avoid title-level summaries.
   - A table of every included article in that subsection, including cached JCR quartile, impact factor, and 新锐分区 from `journal_metrics.json`.
   - If no included article exists, state that explicitly and explain what was checked.
5. Overall interpretation.
6. AMA reference list.
7. Exclusion/audit appendix.

Show JCR quartile, impact factor, and 新锐分区 in each included-article summary table by default. Do not include a separate JCR/impact-factor/新锐分区 appendix table by default; if the user asks to add one, use `journal_metrics.json` and place it at the end.

## Citation Discipline

- Assign reference numbers by first appearance in the report body.
- Keep the same reference number in tables and reference list.
- Merge adjacent in-text citation numbers into compact ranges before finalizing paragraphs: `[1][2][3]` → `[1-3]`; `[1][3][4][5]` → `[1,3-5]`.
- Use AMA reference style:
  `Authors. Title. Journal Abbreviation. Published online Date. doi:DOI PMID: PMID.`
- For more than six authors, list the first three followed by `et al`.
- Validate that reference numbers are continuous and that every table/reference PMID is represented exactly once.

## Quality Checks

Before final delivery:

- Verify the PubMed search date range uses `[epdat]`.
- Verify all retrieved records were either included or listed in the exclusion audit.
- Verify no included PMID is duplicated.
- Verify citations are continuous and references are complete.
- Render the Word file and inspect page images for table overflow, missing glyphs, awkward page breaks, and clipped text.
