#!/usr/bin/env python3
"""Search PubMed for the Thoracic Weekly Academy report.

This script uses NCBI E-utilities directly so the skill does not depend on a
separate PubMed wrapper. It writes a JSON bundle containing search summaries,
disease-hit maps, and fetched article metadata/abstracts.
"""

from __future__ import annotations

import argparse
import json
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date, timedelta
from pathlib import Path


BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

DISEASES = {
    "lung_cancer": (
        '"Lung Neoplasms"[Mesh] OR lung cancer[tiab] OR lung cancers[tiab] '
        'OR lung neoplasm*[tiab] OR lung carcinoma*[tiab] OR NSCLC[tiab] OR SCLC[tiab] '
        'OR non-small cell lung[tiab] OR non small cell lung[tiab] OR small cell lung[tiab] '
        'OR lung adenocarcinoma[tiab] OR lung squamous cell carcinoma[tiab]'
    ),
    "mediastinal_tumor": (
        '"Mediastinal Neoplasms"[Mesh] OR mediastinal tumor*[tiab] OR mediastinal tumour*[tiab] '
        'OR mediastinal neoplasm*[tiab] OR mediastinal mass*[tiab] OR thymoma[tiab] '
        'OR thymomas[tiab] OR thymic carcinoma*[tiab] OR thymic cancer*[tiab] '
        'OR thymic epithelial tumor*[tiab] OR thymic epithelial tumour*[tiab] '
        'OR mediastinal germ cell tumor*[tiab] OR mediastinal germ cell tumour*[tiab]'
    ),
    "esophageal_cancer": (
        '"Esophageal Neoplasms"[Mesh] OR esophageal cancer[tiab] OR esophageal cancers[tiab] '
        'OR oesophageal cancer[tiab] OR oesophageal cancers[tiab] '
        'OR esophageal carcinoma*[tiab] OR oesophageal carcinoma*[tiab] '
        'OR esophagus cancer[tiab] OR oesophagus cancer[tiab] '
        'OR esophageal squamous cell carcinoma[tiab] OR oesophageal squamous cell carcinoma[tiab] '
        'OR esophageal adenocarcinoma[tiab] OR oesophageal adenocarcinoma[tiab] OR ESCC[tiab]'
    ),
    "pneumothorax_chest_trauma_rib_fracture_chest_wall_deformity": (
        '"Pneumothorax"[Mesh] OR pneumothorax[tiab] OR pneumothoraces[tiab] '
        'OR spontaneous pneumothorax[tiab] OR tension pneumothorax[tiab] OR secondary pneumothorax[tiab] '
        'OR "Thoracic Injuries"[Mesh] OR chest trauma[tiab] OR thoracic trauma[tiab] '
        'OR thoracic injur*[tiab] OR chest injur*[tiab] OR blunt chest trauma[tiab] '
        'OR penetrating chest trauma[tiab] OR "Rib Fractures"[Mesh] OR rib fracture*[tiab] '
        'OR multiple rib fracture*[tiab] OR fractured rib*[tiab] OR flail chest[tiab] '
        'OR surgical stabilization of rib fracture*[tiab] OR SSRF[tiab] OR rib fixation[tiab] '
        'OR sternal fracture*[tiab] OR traumatic pneumothorax[tiab] OR traumatic hemothorax[tiab] '
        'OR traumatic haemothorax[tiab] OR "Pulmonary Contusion"[Mesh] OR pulmonary contusion[tiab] '
        'OR chest wall deformit*[tiab] OR thoracic deformit*[tiab] OR chest wall malformation*[tiab] '
        'OR pectus excavatum[tiab] OR pectus carinatum[tiab] OR Nuss procedure[tiab] '
        'OR Ravitch procedure[tiab] OR MIRPE[tiab] OR minimally invasive repair of pectus excavatum[tiab] '
        'OR chest wall reconstruction[tiab] OR chest wall injur*[tiab] OR chest wall trauma[tiab]'
    ),
}

MEDIASTINAL_SUPPLEMENT = (
    '"Mediastinum"[Mesh] OR mediastin*[tiab] OR thymic[tiab] OR thymus[tiab] '
    'OR thymoma[tiab] OR thymomas[tiab] OR "Thymus Neoplasms"[Mesh] '
    'OR "Mediastinal Neoplasms"[Mesh] OR anterior mediastinal[tiab]'
)


def previous_week(today: date) -> tuple[date, date]:
    this_monday = today - timedelta(days=today.weekday())
    start = this_monday - timedelta(days=7)
    end = this_monday - timedelta(days=1)
    return start, end


def fmt_epdat(start: date, end: date) -> str:
    return f"{start:%Y/%m/%d}:{end:%Y/%m/%d}[epdat]"


def chunks(seq, size):
    for idx in range(0, len(seq), size):
        yield seq[idx : idx + size]


def request_json(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def request_xml(url: str) -> ET.Element:
    with urllib.request.urlopen(url, timeout=90) as response:
        return ET.fromstring(response.read())


def esearch(query: str, retmax: int, api_key: str | None = None) -> list[str]:
    params = {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": str(retmax),
        "sort": "pub date",
    }
    if api_key:
        params["api_key"] = api_key
    url = f"{BASE}/esearch.fcgi?{urllib.parse.urlencode(params)}"
    data = request_json(url)
    return data.get("esearchresult", {}).get("idlist", [])


def efetch(pmids: list[str], api_key: str | None = None) -> list[dict]:
    records = []
    for batch in chunks(pmids, 200):
        params = {"db": "pubmed", "id": ",".join(batch), "retmode": "xml"}
        if api_key:
            params["api_key"] = api_key
        url = f"{BASE}/efetch.fcgi?{urllib.parse.urlencode(params)}"
        root = request_xml(url)
        for article in root.findall(".//PubmedArticle"):
            records.append(parse_article(article))
        time.sleep(0.34 if not api_key else 0.12)
    return records


def text_of(node, default=""):
    if node is None:
        return default
    return "".join(node.itertext()).strip()


def parse_pubdate(pubdate_node) -> str:
    if pubdate_node is None:
        return ""
    year = text_of(pubdate_node.find("Year"))
    month = text_of(pubdate_node.find("Month"))
    day = text_of(pubdate_node.find("Day"))
    medline = text_of(pubdate_node.find("MedlineDate"))
    return " ".join([x for x in [year, month, day] if x]) or medline


def parse_article(article) -> dict:
    medline = article.find("MedlineCitation")
    pmid = text_of(medline.find("PMID") if medline is not None else None)
    art = medline.find("Article") if medline is not None else None
    journal = art.find("Journal") if art is not None else None
    journal_title = text_of(journal.find("Title") if journal is not None else None)
    journal_abbr = text_of(journal.find("ISOAbbreviation") if journal is not None else None)
    pubdate = parse_pubdate(journal.find(".//PubDate") if journal is not None else None)
    title = text_of(art.find("ArticleTitle") if art is not None else None)
    abstract_parts = []
    for node in art.findall(".//AbstractText") if art is not None else []:
        label = node.attrib.get("Label")
        txt = text_of(node)
        if txt:
            abstract_parts.append(f"{label}: {txt}" if label else txt)
    authors = []
    for author in art.findall(".//Author") if art is not None else []:
        collective = text_of(author.find("CollectiveName"))
        if collective:
            authors.append(collective)
            continue
        last = text_of(author.find("LastName"))
        initials = text_of(author.find("Initials"))
        if last:
            authors.append(f"{last} {initials}".strip())
    doi = ""
    for aid in article.findall(".//ArticleId"):
        if aid.attrib.get("IdType") == "doi":
            doi = text_of(aid)
            break
    pub_types = [text_of(x) for x in art.findall(".//PublicationType") if art is not None]
    return {
        "pmid": pmid,
        "title": title,
        "authors": authors,
        "journal": journal_title,
        "journal_abbr": journal_abbr,
        "pubdate": pubdate,
        "doi": doi,
        "publication_types": pub_types,
        "abstract": "\n".join(abstract_parts),
    }


def load_journal_terms(skill_dir: Path) -> list[str]:
    data = json.loads((skill_dir / "references" / "journal_metrics.json").read_text())
    terms = []
    for journal in data["journals"]:
        terms.extend(journal.get("pubmed_journal_terms") or [journal["journal"]])
    return list(dict.fromkeys(terms))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", help="Start date YYYY-MM-DD. Defaults to previous Monday.")
    parser.add_argument("--end", help="End date YYYY-MM-DD. Defaults to previous Sunday.")
    parser.add_argument("--today", help="Override today's date YYYY-MM-DD for testing.")
    parser.add_argument("--outdir", default="thoracic_weekly_pubmed_output")
    parser.add_argument("--chunk-size", type=int, default=18)
    parser.add_argument("--retmax", type=int, default=500)
    parser.add_argument("--api-key", default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    skill_dir = Path(__file__).resolve().parents[1]
    today = date.fromisoformat(args.today) if args.today else date.today()
    if args.start and args.end:
        start, end = date.fromisoformat(args.start), date.fromisoformat(args.end)
    else:
        start, end = previous_week(today)
    epdat = fmt_epdat(start, end)
    journal_terms = load_journal_terms(skill_dir)
    journal_chunks = list(chunks(journal_terms, args.chunk_size))
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    summary = {}
    disease_hits = {}
    all_pmids = set()
    planned_queries = []
    disease_queries = dict(DISEASES)
    disease_queries["mediastinal_tumor_supplement"] = MEDIASTINAL_SUPPLEMENT

    for disease, disease_query in disease_queries.items():
        disease_pmids = set()
        chunk_counts = []
        for idx, js in enumerate(journal_chunks, start=1):
            journal_query = " OR ".join([f'"{j}"[jour]' for j in js])
            query = f"(({disease_query}) AND ({journal_query}) AND {epdat})"
            planned_queries.append({"disease": disease, "chunk": idx, "query": query})
            if args.dry_run:
                continue
            pmids = esearch(query, args.retmax, args.api_key)
            time.sleep(0.34 if not args.api_key else 0.12)
            disease_pmids.update(pmids)
            all_pmids.update(pmids)
            chunk_counts.append({"chunk": idx, "count": len(pmids), "pmids": pmids})
        summary[disease] = {"count": len(disease_pmids), "pmids": sorted(disease_pmids), "chunk_counts": chunk_counts}
        for pmid in disease_pmids:
            disease_hits.setdefault(pmid, []).append(disease)

    if args.dry_run:
        (outdir / "planned_queries.json").write_text(json.dumps(planned_queries, indent=2), encoding="utf-8")
        print(json.dumps({"epdat": epdat, "queries": len(planned_queries), "outdir": str(outdir)}, indent=2))
        return

    records = efetch(sorted(all_pmids), args.api_key) if all_pmids else []
    bundle = {
        "metadata": {
            "epdat": epdat,
            "start": f"{start:%Y-%m-%d}",
            "end": f"{end:%Y-%m-%d}",
            "generated_date": f"{today:%Y-%m-%d}",
            "journal_terms_count": len(journal_terms),
        },
        "summary": summary,
        "disease_hits": disease_hits,
        "records": records,
    }
    (outdir / "pubmed_search_bundle.json").write_text(json.dumps(bundle, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"epdat": epdat, "unique_records": len(records), "summary": {k: v["count"] for k, v in summary.items()}}, indent=2))


if __name__ == "__main__":
    main()
