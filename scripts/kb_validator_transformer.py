#!/usr/bin/env python3
"""
KB Validator & Transformer for AINS Hackathon 2026
Processes kb_raw.json → validated, structured knowledge base
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# ───────────────────────────────────────────────────────────────
# CONFIGURATION
# ───────────────────────────────────────────────────────────────
# Resolve paths relative to project root (two levels up from scripts/)
_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent
INPUT_FILE = str(_PROJECT_ROOT / "data/raw/kb_raw.json")
OUTPUT_DIR = str(_PROJECT_ROOT / "data/processed")
REQUIRED_FIELDS = ["name", "type", "operator", "source_url", "eligibility_stages"]
VALID_TYPES = {"support_program", "financing_device", "administrative_procedure", 
               "business_guide", "ecosystem_actor"}
VALID_STAGES = {"Ideation", "Validation", "Structuration", "Fundraising", 
                "Launch_Planning", "Growth"}
VALID_DOMAINS = {"financial", "legal", "market", "technical", "organisational"}

# Operators that MUST have working URLs (institutional heavyweights)
TIER_1_OPERATORS = {"APII", "BFPME", "BTS", "ANPE", "AFD", "EU", "UNDP", 
                    "Ministry_of_Industry", "Startup_Act"}

# ───────────────────────────────────────────────────────────────
# VALIDATION FUNCTIONS
# ───────────────────────────────────────────────────────────────

def validate_url(url: str) -> tuple[bool, str]:
    """Basic URL sanity check (not a live ping, but catches obvious fakes)."""
    if not url or not isinstance(url, str):
        return False, "Missing or non-string URL"

    # Must start with http(s)
    if not re.match(r'^https?://', url):
        return False, "URL does not start with http(s)"

    # Common hallucination patterns from LLMs
    suspicious_patterns = [
        r'example\.com',
        r'placeholder',
        r'xxx',
        r'\.tn/[a-z]{10,}$',  # suspicious long slugs on .tn domains
        r'\.com\.tn/index\.html$',  # generic homepage masquerading as program page
    ]

    for pattern in suspicious_patterns:
        if re.search(pattern, url, re.IGNORECASE):
            return False, f"Suspicious URL pattern matched: {pattern}"

    return True, "OK"

def normalize_stages(stages: List[str]) -> tuple[List[str], List[str]]:
    """Normalize stage names and flag invalid ones."""
    normalized = []
    errors = []
    for s in stages:
        s_clean = s.strip().replace(" ", "_").replace("-", "_")
        if s_clean in VALID_STAGES:
            normalized.append(s_clean)
        else:
            # Try fuzzy matching
            mapping = {
                "ideation": "Ideation", "idea": "Ideation",
                "validation": "Validation", "market_validation": "Validation",
                "structuration": "Structuration", "structuring": "Structuration",
                "fundraising": "Fundraising", "pre_financing": "Fundraising",
                "launch": "Launch_Planning", "launch_planning": "Launch_Planning",
                "growth": "Growth", "scaling": "Growth"
            }
            if s_clean.lower() in mapping:
                normalized.append(mapping[s_clean.lower()])
            else:
                errors.append(f"Unknown stage: {s}")
    return list(set(normalized)), errors

def generate_embedding_text(item: Dict[str, Any]) -> str:
    """Generate a dense, semantic-rich text for vector embedding."""
    parts = [
        item.get("name", ""),
        item.get("description", ""),
        f"Operated by {item.get('operator', 'unknown')}",
        f"Type: {item.get('type', 'unknown')}",
    ]

    stages = item.get("eligibility_stages", [])
    if stages:
        parts.append(f"Eligible for stages: {', '.join(stages)}")

    blockers = item.get("blockers_resolved", [])
    if blockers:
        parts.append(f"Helps overcome: {', '.join(blockers)}")

    domains = item.get("domains_addressed", [])
    if domains:
        parts.append(f"Domains: {', '.join(domains)}")

    criteria = item.get("eligibility_criteria", [])
    if criteria:
        parts.append(f"Requirements: {', '.join(criteria[:3])}")  # limit to 3

    return " ".join(parts)

# ───────────────────────────────────────────────────────────────
# MAIN PROCESSING PIPELINE
# ───────────────────────────────────────────────────────────────

def process_kb():
    print("[KB Validator] AINS Hackathon KB Validator & Transformer")
    print("=" * 60)

    # Load raw data
    if not Path(INPUT_FILE).exists():
        print(f"[ERROR] {INPUT_FILE} not found. Place it in this directory.")
        sys.exit(1)

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        try:
            raw_data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"[ERROR] Invalid JSON in {INPUT_FILE}: {e}")
            sys.exit(1)

    if not isinstance(raw_data, list):
        print("[ERROR] Expected JSON array at root level.")
        sys.exit(1)

    print(f"[DATA] Loaded {len(raw_data)} raw items\n")

    # Processing containers
    valid_items = []
    flagged_items = []
    stats = {
        "total": len(raw_data),
        "valid": 0,
        "flagged": 0,
        "by_type": {},
        "by_operator": {},
        "missing_url": 0,
        "suspicious_url": 0,
        "missing_required_field": 0,
    }

    for idx, item in enumerate(raw_data, 1):
        item_id = item.get("resource_id", f"item_{idx}")
        flags = []

        # Check required fields
        for field in REQUIRED_FIELDS:
            if field not in item or not item[field]:
                flags.append(f"Missing/empty required field: {field}")
                stats["missing_required_field"] += 1

        # Validate type
        item_type = item.get("type", "")
        if item_type and item_type not in VALID_TYPES:
            flags.append(f"Invalid type: {item_type}")

        # Validate URL
        url = item.get("source_url", "")
        url_ok, url_msg = validate_url(url)
        if not url:
            stats["missing_url"] += 1
            flags.append("No source_url provided")
        elif not url_ok:
            stats["suspicious_url"] += 1
            flags.append(f"URL issue: {url_msg}")

        # Normalize stages
        stages = item.get("eligibility_stages", [])
        if isinstance(stages, str):
            stages = [stages]
        norm_stages, stage_errors = normalize_stages(stages)
        if stage_errors:
            flags.extend(stage_errors)
        item["eligibility_stages"] = norm_stages

        # Normalize domains
        domains = item.get("domains_addressed", [])
        if isinstance(domains, str):
            domains = [domains]
        item["domains_addressed"] = [d for d in domains if d in VALID_DOMAINS]

        # Generate embedding text
        item["embedding_text"] = generate_embedding_text(item)

        # Generate resource_id if missing
        if not item.get("resource_id"):
            slug = re.sub(r'[^\w]', '-', item.get("name", f"item-{idx}").lower())[:40]
            item["resource_id"] = f"{slug}-{idx}"

        # Tier-1 operator check (must be manually verified)
        operator = item.get("operator", "")
        if operator in TIER_1_OPERATORS and (not url or not url_ok):
            flags.append(f"TIER-1 OPERATOR ({operator}) with bad URL — MUST VERIFY MANUALLY")

        # Categorize
        if flags:
            item["_validation_flags"] = flags
            flagged_items.append(item)
            stats["flagged"] += 1
        else:
            valid_items.append(item)
            stats["valid"] += 1

        # Stats
        stats["by_type"][item_type] = stats["by_type"].get(item_type, 0) + 1
        stats["by_operator"][operator] = stats["by_operator"].get(operator, 0) + 1

    # ── OUTPUT ──
    Path(OUTPUT_DIR).mkdir(exist_ok=True)

    # 1. Clean KB for ingestion
    with open(f"{OUTPUT_DIR}/kb_clean.json", "w", encoding="utf-8") as f:
        json.dump(valid_items, f, ensure_ascii=False, indent=2)

    # 2. Flagged items for manual review
    with open(f"{OUTPUT_DIR}/kb_flagged.json", "w", encoding="utf-8") as f:
        json.dump(flagged_items, f, ensure_ascii=False, indent=2)

    # 3. CSV summary for quick review
    import csv
    with open(f"{OUTPUT_DIR}/kb_summary.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["resource_id", "name", "type", "operator", "url_status", "flags_count"])
        for item in raw_data:
            rid = item.get("resource_id", "")
            flags = item.get("_validation_flags", [])
            url = item.get("source_url", "")
            url_status = "OK" if validate_url(url)[0] else "ISSUE"
            writer.writerow([
                rid, item.get("name", ""), item.get("type", ""), 
                item.get("operator", ""), url_status, len(flags)
            ])

    # 4. Report
    print(f"[OK] Valid items: {stats['valid']}")
    print(f"[WARN] Flagged items: {stats['flagged']}")
    print(f"   - Missing required fields: {stats['missing_required_field']}")
    print(f"   - Missing URLs: {stats['missing_url']}")
    print(f"   - Suspicious URLs: {stats['suspicious_url']}")
    print(f"\n[STATS] By type:")
    for t, c in sorted(stats["by_type"].items(), key=lambda x: -x[1]):
        print(f"   {t}: {c}")
    print(f"\n[STATS] By operator (top 10):")
    for op, c in sorted(stats["by_operator"].items(), key=lambda x: -x[1])[:10]:
        print(f"   {op}: {c}")

    print(f"\n[OUTPUT] Files written to ./{OUTPUT_DIR}/")
    print(f"   - kb_clean.json -- {len(valid_items)} items ready for ingestion")
    print(f"   - kb_flagged.json -- {len(flagged_items)} items needing manual review")
    print(f"   - kb_summary.csv -- quick spreadsheet view")

    tier1_flagged = [i for i in flagged_items if i.get("operator") in TIER_1_OPERATORS]
    if tier1_flagged:
        print(f"\n[CRITICAL] {len(tier1_flagged)} Tier-1 operator items flagged:")
        for i in tier1_flagged[:5]:
            print(f"   - {i.get('name')} ({i.get('operator')}) -- {i['_validation_flags'][0]}")

    if stats["valid"] < 30:
        print(f"\n[WARNING] Only {stats['valid']} clean items. Need >=30 verified resources.")

if __name__ == "__main__":
    process_kb()
