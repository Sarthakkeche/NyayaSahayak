# main.py
@app.get("/")
def home():
    return {
        "status": "running",
        "service": "NyayaSahayak Backend",
        "message": "Use /docs or POST /analyze"
    }

import json
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from db import SessionLocal, engine, Base
from models import LegalSection
from nlp import extract_primary_offences

# Create tables if not exist
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="NyayaSahayak - Legal AI Advisor",
    description="Simplify incident text and map to BNS legal sections using enriched dataset.",
    version="0.4.0",
)

# CORS for Vite dev server
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://nyaya-sahayak-lilac.vercel.app/",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    text: str


class SectionOut(BaseModel):
    id: int
    section_id: str
    act_name: str
    section_number: str
    title: str
    full_text: str

    primary_offence: str | None = None
    subtype: str | None = None
    is_core_offence: bool
    victim_type: List[str]
    has_weapon: bool
    is_sexual_offence: bool
    is_property_offence: bool
    severity_level: int | None = None
    ipc_equivalent: str | None = None


class AnalyzeResponse(BaseModel):
    normalized_keywords: List[str]  # offence tags
    lemmas: List[str]
    sections: List[SectionOut]


# MAP HIGH-LEVEL TAGS -> possible values in your DB's primary_offence column
OFFENCE_TAG_TO_DB_PRIMARY = {
    "hurt_simple": ["hurt"],
    "hurt_grievous": ["hurt_grievous", "hurt"],
    "hurt_weapon": ["hurt_grievous", "hurt"],

    "murder": ["murder"],
    "attempt_murder": ["attempt_murder", "murder"],

    "criminal_intimidation": ["criminal_intimidation", "criminal_intimidation_defamation"],
    "extortion_threat": ["extortion", "criminal_intimidation", "criminal_intimidation_defamation"],

    "sexual_misconduct": ["sexual_misconduct", "sexual_offence"],
    "sexual_rape": ["sexual_offence"],

    "theft": ["theft"],
    "robbery": ["robbery"],
    "house_trespass": ["house_trespass", "theft"],

    "cheating": ["cheating"],
    "forgery": ["forgery", "property_marks"],
    "property_marks": ["property_marks"],

    "public_mischief": ["public_mischief"],
    "public_drunkenness": ["public_drunkenness", "criminal_intimidation_defamation"],
    "cyber_fraud": ["cyber_fraud", "cheating"],
}


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze_incident(payload: AnalyzeRequest):
    text = payload.text.strip()
    if not text:
        return AnalyzeResponse(normalized_keywords=[], lemmas=[], sections=[])

    offence_tags, lemmas = extract_primary_offences(text)
    lemmas_set = set(lemmas)

    # ---- CONTEXT FLAGS (derived from lemmas) ----
    has_weapon_word = any(
        w in lemmas_set
        for w in [
            "knife",
            "gun",
            "pistol",
            "rod",
            "sword",
            "weapon",
            "acid",
            "stone",
            "stick",
        ]
    )
    has_fracture = "fracture" in lemmas_set
    has_serious = any(w in lemmas_set for w in ["serious", "critical", "hospital"])
    has_grievous_hint = has_fracture or has_serious

    victim_is_woman = any(
        w in lemmas_set for w in ["woman", "women", "girl", "lady", "female", "wife"]
    )
    is_public_place = any(
        w in lemmas_set
        for w in ["road", "street", "market", "bus", "train", "station", "park"]
    )
    has_extortion = any(w in lemmas_set for w in ["extort", "extortion", "ransom"])
    has_public_servant = any(
        w in lemmas_set for w in ["police", "officer", "constable", "judge"]
    )

    db = SessionLocal()
    try:
        sections: list[LegalSection] = []
        seen_ids: set[str] = set()

        # If we have any "hurt_grievous" or "hurt_weapon" tag, we can ignore hurt_simple
        if "hurt_grievous" in offence_tags or "hurt_weapon" in offence_tags:
            offence_tags = [t for t in offence_tags if t != "hurt_simple"]

        # ---- 1) Use offence_tags + context to select best sections ----
        for tag in offence_tags:
            db_primary_values = OFFENCE_TAG_TO_DB_PRIMARY.get(tag, [tag])

            query = (
                db.query(LegalSection)
                .filter(
                    LegalSection.primary_offence.in_(db_primary_values),
                    LegalSection.is_core_offence == True,
                )
            )

            # --- SPECIAL LOGIC PER TAG ---

            # HURT (simple / grievous / weapon)
            if tag == "hurt_simple":
                # simple slap: avoid weapon + grievous, extortion, public servant
                query = query.filter(LegalSection.has_weapon == False)
                query = query.filter(LegalSection.subtype != "grievous hurt")
                query = query.filter(LegalSection.title.ilike("%extort%") == False)
                query = query.filter(
                    LegalSection.title.ilike("%public servant%") == False
                )
                query = query.order_by(LegalSection.severity_level.asc())

            elif tag == "hurt_grievous":
                # prefer grievous subtype, serious severity
                query = query.filter(LegalSection.subtype == "grievous hurt")
                if has_weapon_word:
                    query = query.filter(LegalSection.has_weapon == True)
                if not has_grievous_hint:
                    # if user didn't explicitly mention grievous, still allow but mid severity
                    query = query.order_by(LegalSection.severity_level.desc())
                else:
                    query = query.order_by(LegalSection.severity_level.desc())

            elif tag == "hurt_weapon":
                query = query.filter(LegalSection.has_weapon == True)
                query = query.order_by(LegalSection.severity_level.desc())

            # CRIMINAL INTIMIDATION / EXTORTION THREAT
            elif tag in ("criminal_intimidation", "extortion_threat"):
                query = query.order_by(LegalSection.severity_level.desc())

            # SEXUAL MISCONDUCT VS RAPE
            elif tag == "sexual_misconduct":
                # prefer lower-severity sexual misconduct sections (74, 75)
                query = query.order_by(LegalSection.severity_level.asc())
            elif tag == "sexual_rape":
                query = query.order_by(LegalSection.severity_level.desc())

            # PROPERTY / THEFT / ROBBERY / HOUSE TRESSPASS
            elif tag in ("theft", "robbery", "house_trespass"):
                query = query.order_by(LegalSection.severity_level.desc())

    # FILTER: remove "clerk/servant" theft unless text mentions employer relations
            if "employee" not in lemmas_set and "servant" not in lemmas_set and "clerk" not in lemmas_set:
                query = query.filter(LegalSection.title.ilike("%servant%") == False)
                query = query.filter(LegalSection.title.ilike("%clerk%") == False)

            # PUBLIC DRUNK / MISCHIEF
            elif tag in ("public_drunkenness", "public_mischief"):
                query = query.order_by(LegalSection.severity_level.asc())

            else:
                # default: show most serious first
                query = query.order_by(LegalSection.severity_level.desc())

            # limit per tag to avoid flooding
            results = query.limit(5).all()

            for s in results:
                if s.section_id not in seen_ids:
                    sections.append(s)
                    seen_ids.add(s.section_id)

        # ---- 2) Fallback if nothing matched: keyword search on offence tags ----
        if not sections and offence_tags:
            from sqlalchemy import or_

            filters = []
            for tag in offence_tags:
                filters.append(LegalSection.keywords.ilike(f"%{tag}%"))

            results = (
                db.query(LegalSection)
                .filter(or_(*filters))
                .limit(10)
                .all()
            )

            for s in results:
                if s.section_id not in seen_ids:
                    sections.append(s)
                    seen_ids.add(s.section_id)

        # ---- Build response ----
        sections_out: list[SectionOut] = []
        for s in sections:
            try:
                victims = json.loads(s.victim_type) if s.victim_type else []
                if not isinstance(victims, list):
                    victims = []
            except Exception:
                victims = []

            sections_out.append(
                SectionOut(
                    id=s.id,
                    section_id=s.section_id,
                    act_name=s.act_name or "",
                    section_number=s.section_number or "",
                    title=s.title or "",
                    full_text=s.full_text or "",
                    primary_offence=s.primary_offence,
                    subtype=s.subtype,
                    is_core_offence=bool(s.is_core_offence),
                    victim_type=victims,
                    has_weapon=bool(s.has_weapon),
                    is_sexual_offence=bool(s.is_sexual_offence),
                    is_property_offence=bool(s.is_property_offence),
                    severity_level=s.severity_level,
                    ipc_equivalent=s.ipc_equivalent,
                )
            )

        return AnalyzeResponse(
            normalized_keywords=offence_tags,
            lemmas=lemmas,
            sections=sections_out,
        )
    finally:
        db.close()
