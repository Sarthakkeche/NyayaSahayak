# main.py

import json
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from db import SessionLocal, engine, Base
from models import LegalSection
from nlp import extract_primary_offences

# -------------------------------
# CREATE DATABASE TABLES
# -------------------------------
Base.metadata.create_all(bind=engine)

# -------------------------------
# FASTAPI APP
# -------------------------------
app = FastAPI(
    title="NyayaSahayak - Legal AI Advisor",
    description="Simplify incident text and map to BNS legal sections using enriched dataset.",
    version="0.4.0",
)

# -------------------------------
# ROOT ROUTE (IMPORTANT FOR RENDER)
# -------------------------------
@app.get("/")
def home():
    return {
        "status": "running",
        "service": "NyayaSahayak Backend",
        "message": "Use /docs or POST /analyze"
    }

# -------------------------------
# CORS SETTINGS
# -------------------------------
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://nyaya-sahayak-lilac.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# REQUEST / RESPONSE SCHEMAS
# -------------------------------
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
    normalized_keywords: List[str]
    lemmas: List[str]
    sections: List[SectionOut]


# -------------------------------
# OFFENCE → DB PRIMARY MAPPING
# -------------------------------
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

# -------------------------------
# MAIN ANALYSIS ENDPOINT
# -------------------------------
@app.post("/analyze", response_model=AnalyzeResponse)
def analyze_incident(payload: AnalyzeRequest):
    text = payload.text.strip()
    if not text:
        return AnalyzeResponse(normalized_keywords=[], lemmas=[], sections=[])

    offence_tags, lemmas = extract_primary_offences(text)
    lemmas_set = set(lemmas)

    # -------------------------------
    # CONTEXT FLAGS
    # -------------------------------
    has_weapon_word = any(w in lemmas_set for w in [
        "knife", "gun", "pistol", "rod", "sword", "weapon", "acid", "stone", "stick"
    ])
    has_fracture = "fracture" in lemmas_set
    has_serious = any(w in lemmas_set for w in ["serious", "critical", "hospital"])
    has_grievous_hint = has_fracture or has_serious

    victim_is_woman = any(w in lemmas_set for w in [
        "woman", "women", "girl", "lady", "female", "wife"
    ])
    is_public_place = any(w in lemmas_set for w in [
        "road", "street", "market", "bus", "train", "station", "park"
    ])
    has_extortion = any(w in lemmas_set for w in ["extort", "extortion", "ransom"])
    has_public_servant = any(w in lemmas_set for w in [
        "police", "officer", "constable", "judge"
    ])

    db = SessionLocal()
    try:
        sections = []
        seen_ids = set()

        # Remove simple hurt if grievous/weapon identified
        if "hurt_grievous" in offence_tags or "hurt_weapon" in offence_tags:
            offence_tags = [t for t in offence_tags if t != "hurt_simple"]

        # -------------------------------
        # MAIN DB QUERY PER TAG
        # -------------------------------
        for tag in offence_tags:
            db_primary_values = OFFENCE_TAG_TO_DB_PRIMARY.get(tag, [tag])

            query = (
                db.query(LegalSection)
                .filter(
                    LegalSection.primary_offence.in_(db_primary_values),
                    LegalSection.is_core_offence == True,
                )
            )

            # HURT LOGIC
            if tag == "hurt_simple":
                query = query.filter(LegalSection.has_weapon == False)
                query = query.filter(LegalSection.subtype != "grievous hurt")
                query = query.order_by(LegalSection.severity_level.asc())

            elif tag == "hurt_grievous":
                query = query.filter(LegalSection.subtype == "grievous hurt")
                if has_weapon_word:
                    query = query.filter(LegalSection.has_weapon == True)
                query = query.order_by(LegalSection.severity_level.desc())

            elif tag == "hurt_weapon":
                query = query.filter(LegalSection.has_weapon == True)
                query = query.order_by(LegalSection.severity_level.desc())

            # INTIMIDATION / EXTORTION
            elif tag in ("criminal_intimidation", "extortion_threat"):
                query = query.order_by(LegalSection.severity_level.desc())

            # SEXUAL OFFENCES
            elif tag == "sexual_misconduct":
                query = query.order_by(LegalSection.severity_level.asc())
            elif tag == "sexual_rape":
                query = query.order_by(LegalSection.severity_level.desc())

            # PROPERTY OFFENCES
            elif tag in ("theft", "robbery", "house_trespass"):
                query = query.order_by(LegalSection.severity_level.desc())

            # PUBLIC DRUNKENNESS
            elif tag in ("public_drunkenness", "public_mischief"):
                query = query.order_by(LegalSection.severity_level.asc())

            # DEFAULT
            else:
                query = query.order_by(LegalSection.severity_level.desc())

            # SERVANT/CLERK FILTER
            if "employee" not in lemmas_set and "servant" not in lemmas_set:
                query = query.filter(LegalSection.title.ilike("%servant%") == False)

            # Limit 5 results per tag
            results = query.limit(5).all()

            for s in results:
                if s.section_id not in seen_ids:
                    seen_ids.add(s.section_id)
                    sections.append(s)

        # -------------------------------
        # FALLBACK: keyword search
        # -------------------------------
        if not sections and offence_tags:
            from sqlalchemy import or_

            filters = [LegalSection.keywords.ilike(f"%{tag}%") for tag in offence_tags]
            results = db.query(LegalSection).filter(or_(*filters)).limit(10).all()

            for s in results:
                if s.section_id not in seen_ids:
                    seen_ids.add(s.section_id)
                    sections.append(s)

        # -------------------------------
        # RESPONSE BUILD
        # -------------------------------
        sections_out = []
        for s in sections:
            try:
                victim_list = json.loads(s.victim_type) if s.victim_type else []
            except Exception:
                victim_list = []

            sections_out.append(
                SectionOut(
                    id=s.id,
                    section_id=s.section_id,
                    act_name=s.act_name,
                    section_number=s.section_number,
                    title=s.title,
                    full_text=s.full_text,
                    primary_offence=s.primary_offence,
                    subtype=s.subtype,
                    is_core_offence=s.is_core_offence,
                    victim_type=victim_list,
                    has_weapon=s.has_weapon,
                    is_sexual_offence=s.is_sexual_offence,
                    is_property_offence=s.is_property_offence,
                    severity_level=s.severity_level,
                    ipc_equivalent=s.ipc_equivalent,
                )
            )

        return AnalyzeResponse(
            normalized_keywords=offence_tags,
            lemmas=lemmas,
            sections=sections_out
        )

    finally:
        db.close()
