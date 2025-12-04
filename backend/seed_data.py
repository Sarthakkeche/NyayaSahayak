# seed_enriched.py
import json
from pathlib import Path

from db import Base, engine, SessionLocal
from models import LegalSection


JSON_PATH = Path(__file__).resolve().parents[1] / "data" / "BNS_enriched.json"


def seed_enriched():
    print(f"Seeding enriched BNS sections from {JSON_PATH}")

    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Allow both: list OR {"sections": [...]}
    if isinstance(data, dict) and "sections" in data:
        sections = data["sections"]
    else:
        sections = data

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        count = 0
        for item in sections:
            section_id = item.get("section_id")
            if not section_id:
                continue

            existing = (
                db.query(LegalSection)
                .filter(LegalSection.section_id == section_id)
                .first()
            )
            if existing:
                continue

            act_name = item.get("act_name") or "BNS"
            section_number = item.get("section_number") or ""

            title = item.get("title") or ""
            full_text = item.get("full_text") or ""

            primary_offence = item.get("primary_offence")
            subtype = item.get("subtype")
            is_core_offence = bool(item.get("is_core_offence", True))

            victim_type_list = item.get("victim_type") or []
            victim_type_json = json.dumps(victim_type_list, ensure_ascii=False)

            has_weapon = bool(item.get("has_weapon", False))
            is_sexual_offence = bool(item.get("is_sexual_offence", False))
            is_property_offence = bool(item.get("is_property_offence", False))

            severity_level = int(item.get("severity_level") or 1)
            ipc_equivalent = item.get("ipc_equivalent")

            keywords = f"{title.lower()} {full_text.lower()} {str(primary_offence or '')}"

            sec = LegalSection(
                section_id=section_id,
                act_name=act_name,
                section_number=section_number,
                title=title,
                full_text=full_text,
                primary_offence=primary_offence,
                subtype=subtype,
                is_core_offence=is_core_offence,
                victim_type=victim_type_json,
                has_weapon=has_weapon,
                is_sexual_offence=is_sexual_offence,
                is_property_offence=is_property_offence,
                severity_level=severity_level,
                ipc_equivalent=ipc_equivalent,
                keywords=keywords,
            )

            db.add(sec)
            count += 1

        db.commit()
        print(f"✅ Inserted {count} enriched sections.")
    finally:
        db.close()


if __name__ == "__main__":
    seed_enriched()
