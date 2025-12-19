#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple
from collections import Counter
from datetime import datetime, timezone


def level_from_score(score: int) -> str:
    if 1 <= score <= 4:
        return "Low"
    if 5 <= score <= 9:
        return "Medium"
    if 10 <= score <= 14:
        return "High"
    if 15 <= score <= 25:
        return "Critical"
    return "Invalid"


def sniff_delimiter(path: Path) -> str:
    sample = path.read_text(encoding="utf-8-sig", errors="replace")[:5000]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=[",", ";", "\t"])
        return dialect.delimiter
    except Exception:
        return ","


def read_csv(path: Path) -> Tuple[List[Dict[str, str]], List[str], str]:
    delim = sniff_delimiter(path)
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter=delim)
        rows = list(reader)
        return rows, (reader.fieldnames or []), delim


def write_csv(path: Path, rows: List[Dict[str, str]], fieldnames: List[str], delimiter: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames,
            delimiter=delimiter,
            extrasaction="ignore",
            quoting=csv.QUOTE_ALL,
        )
        writer.writeheader()
        for r in rows:
            writer.writerow({k: r.get(k, "") for k in fieldnames})


def norm_treatment(x: str) -> str:
    v = (x or "").strip().lower()
    return v if v else "reduce"


def to_int(x: str, default: int = 0) -> int:
    try:
        return int(str(x).strip())
    except Exception:
        return default


def _token_pat(token: str) -> str:
    # rend les underscores tolérants: "_" ou "\_"
    esc = re.escape(token)
    return esc.replace(r"\_", r"(?:_|\\_)").replace("_", r"(?:_|\\_)")


def replace_auto_block(text: str, token: str, new_block: str) -> Tuple[str, bool]:
    token_pat = _token_pat(token)
    start_pat = rf"<!--\s*AUTO:{token_pat}(?:_|\\_)?START\s*-->"
    end_pat = rf"<!--\s*AUTO:{token_pat}(?:_|\\_)?END\s*-->"
    pattern = re.compile(rf"({start_pat})(.*?)(\s*{end_pat})", re.DOTALL | re.IGNORECASE)

    if not pattern.search(text):
        return text, False

    canonical_start = f"<!-- AUTO:{token}_START -->"
    canonical_end = f"<!-- AUTO:{token}_END -->"
    replacement = f"{canonical_start}\n{new_block.strip()}\n{canonical_end}"

    new_text = pattern.sub(replacement, text, count=1)
    return new_text, True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--inplace", action="store_true")
    parser.add_argument("--outputs", default="outputs")
    parser.add_argument("--top", type=int, default=10)
    parser.add_argument("--update-exec", action="store_true")
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    risk_path = repo / "risk_register.csv"
    exec_path = repo / "03_executive_summary.md"

    if not risk_path.exists():
        print(f"ERROR: introuvable: {risk_path}")
        return 2

    rows, cols, delim = read_csv(risk_path)

    required = [
        "risk_id", "title", "risk_category",
        "L_1to5", "I_1to5", "score", "level",
        "treatment",
        "residual_L_1to5", "residual_I_1to5", "residual_score", "residual_level", "residual_assumption",
        "owner", "target_date", "status"
    ]
    missing = [c for c in required if c not in cols]
    if missing:
        print(f"ERROR: colonnes manquantes dans risk_register.csv: {missing}")
        return 1

    errors: List[str] = []
    diffs: List[str] = []
    seen = set()

    for line_no, r in enumerate(rows, start=2):
        rid = (r.get("risk_id") or "").strip()

        if not re.fullmatch(r"R\d{2}", rid):
            errors.append(f"L{line_no}: risk_id invalide: '{rid}' (attendu R01..R99)")
        if rid in seen:
            errors.append(f"L{line_no}: risk_id dupliqué: '{rid}'")
        seen.add(rid)

        try:
            L = int((r.get("L_1to5") or "").strip())
            I = int((r.get("I_1to5") or "").strip())
        except Exception:
            errors.append(f"L{line_no} [{rid}]: L_1to5/I_1to5 non entiers")
            continue

        if not (1 <= L <= 5):
            errors.append(f"L{line_no} [{rid}]: L_1to5 hors 1..5: {L}")
        if not (1 <= I <= 5):
            errors.append(f"L{line_no} [{rid}]: I_1to5 hors 1..5: {I}")

        # Inherent
        score = L * I
        level = level_from_score(score)

        if (r.get("score") or "").strip() != str(score):
            diffs.append(f"[{rid}] score csv={r.get('score')} computed={score}")
        if (r.get("level") or "").strip() != level:
            diffs.append(f"[{rid}] level csv={r.get('level')} computed={level}")

        r["score"] = str(score)
        r["level"] = level

        # Residual v1.2
        treatment = norm_treatment(r.get("treatment", ""))
        cat = (r.get("risk_category") or "").strip()

        if treatment == "avoid":
            rL, rI = 1, 1
            default_assumption = "Avoid: activité supprimée/évité (résiduel forcé à 1x1)."
        elif treatment in ("accept", "transfer"):
            rL, rI = L, I
            default_assumption = f"{treatment.capitalize()}: pas de réduction automatique (résiduel = inhérent)."
        else:
            rL = max(L - 1, 1)
            if re.search(r"(Resilience|Backups|Incident Response)", cat, flags=re.IGNORECASE):
                rI = max(I - 1, 1)
            else:
                rI = I
            default_assumption = "Reduce v1.2: residual_L=max(L-1,1); residual_I=I (ou I-1 si catégorie résilience/backups/IR)."

        rScore = rL * rI
        rLevel = level_from_score(rScore)

        if (r.get("residual_L_1to5") or "").strip() != str(rL):
            diffs.append(f"[{rid}] residual_L_1to5 csv={r.get('residual_L_1to5')} computed={rL}")
        if (r.get("residual_I_1to5") or "").strip() != str(rI):
            diffs.append(f"[{rid}] residual_I_1to5 csv={r.get('residual_I_1to5')} computed={rI}")
        if (r.get("residual_score") or "").strip() != str(rScore):
            diffs.append(f"[{rid}] residual_score csv={r.get('residual_score')} computed={rScore}")
        if (r.get("residual_level") or "").strip() != rLevel:
            diffs.append(f"[{rid}] residual_level csv={r.get('residual_level')} computed={rLevel}")

        r["residual_L_1to5"] = str(rL)
        r["residual_I_1to5"] = str(rI)
        r["residual_score"] = str(rScore)
        r["residual_level"] = rLevel

        if not (r.get("residual_assumption") or "").strip():
            r["residual_assumption"] = default_assumption

    if errors:
        print("ERRORS:")
        for e in errors:
            print("-", e)
        return 1

    if args.check and diffs:
        print("DIFFS (CSV != computed):")
        for d in diffs[:300]:
            print("-", d)
        print("\n=> Pour appliquer automatiquement: python .\\scripts\\validate_and_score.py --write --inplace")
        return 1

    if args.write:
        out_dir = repo / args.outputs
        out_dir.mkdir(parents=True, exist_ok=True)

        if args.inplace:
            write_csv(risk_path, rows, cols, delim)
            print("OK: risk_register.csv mis à jour (score/level + résiduel v1.2).")

        inherent_levels = Counter((r.get("level") or "").strip() for r in rows)
        residual_levels = Counter((r.get("residual_level") or "").strip() for r in rows)
        treatments = Counter(norm_treatment(r.get("treatment", "")) for r in rows)
        statuses = Counter((r.get("status") or "").strip() for r in rows)

        sorted_by_residual = sorted(
            rows,
            key=lambda r: (to_int(r.get("residual_score", "0")), to_int(r.get("score", "0"))),
            reverse=True,
        )

        topn = min(max(args.top, 1), len(rows))
        top_list = []
        for r in sorted_by_residual[:topn]:
            top_list.append({
                "risk_id": (r.get("risk_id") or "").strip(),
                "title": (r.get("title") or "").strip(),
                "risk_category": (r.get("risk_category") or "").strip(),
                "score": to_int(r.get("score", "0")),
                "level": (r.get("level") or "").strip(),
                "residual_score": to_int(r.get("residual_score", "0")),
                "residual_level": (r.get("residual_level") or "").strip(),
                "treatment": (r.get("treatment") or "").strip(),
                "owner": (r.get("owner") or "").strip(),
                "target_date": (r.get("target_date") or "").strip(),
                "status": (r.get("status") or "").strip(),
            })

        now_utc = datetime.now(timezone.utc)
        kpis = {
            "generated_at": now_utc.isoformat(),
            "counts": {"total_risks": len(rows)},
            "inherent_levels": dict(inherent_levels),
            "residual_levels": dict(residual_levels),
            "treatments": dict(treatments),
            "statuses": dict(statuses),
            "top_by_residual": top_list,
        }

        kpis_path = out_dir / "kpis.json"
        kpis_path.write_text(json.dumps(kpis, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"OK: {kpis_path} généré")

        md = []
        md.append(f"# Top risks (by residual) — {now_utc.date().isoformat()}\n")
        md.append("| Rank | Risk | Title | Category | Inherent | Residual | Treatment | Status | Target | Owner |")
        md.append("|---:|---|---|---|---:|---:|---|---|---|---|")
        for i, r in enumerate(sorted_by_residual[:topn], start=1):
            md.append(
                f"| {i} | {(r.get('risk_id') or '').strip()} | {(r.get('title') or '').strip()} | {(r.get('risk_category') or '').strip()} | "
                f"{(r.get('score') or '').strip()} ({(r.get('level') or '').strip()}) | "
                f"{(r.get('residual_score') or '').strip()} ({(r.get('residual_level') or '').strip()}) | "
                f"{(r.get('treatment') or '').strip()} | {(r.get('status') or '').strip()} | {(r.get('target_date') or '').strip()} | {(r.get('owner') or '').strip()} |"
            )

        top_path = out_dir / "top_risks.md"
        top_path.write_text("\n".join(md) + "\n", encoding="utf-8")
        print(f"OK: {top_path} généré")

        if args.update_exec and exec_path.exists():
            exec_text = exec_path.read_text(encoding="utf-8", errors="replace")

            top_block = "\n".join(md)
            kpi_block = (
                "## KPI snapshot\n"
                f"- Total risks: **{len(rows)}**\n"
                f"- Residual levels: `{dict(residual_levels)}`\n"
                f"- Inherent levels: `{dict(inherent_levels)}`\n"
                f"- Treatments: `{dict(treatments)}`\n"
                f"- Statuses: `{dict(statuses)}`\n"
            )

            exec_text2, ok1 = replace_auto_block(exec_text, "TOP_RISKS", top_block)
            exec_text3, ok2 = replace_auto_block(exec_text2, "KPIS", kpi_block)

            if ok1 or ok2:
                exec_path.write_text(exec_text3, encoding="utf-8")
                print("OK: 03_executive_summary.md mis à jour (zones AUTO).")
            else:
                print("INFO: marqueurs AUTO absents, aucune mise à jour du executive summary.")

    print("OK: validation terminée.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
