# models.py
from sqlalchemy import Column, Integer, String, Text, Boolean
from db import Base


class LegalSection(Base):
    __tablename__ = "legal_sections"

    id = Column(Integer, primary_key=True, index=True)

    section_id = Column(String(50), unique=True, index=True)   # e.g. "BNS_351"
    act_name = Column(String(50), index=True)                  # e.g. "BNS"
    section_number = Column(String(20), index=True)            # "351"

    title = Column(Text)                                       # section title
    full_text = Column(Text)                                   # full description

    # --- enriched fields ---
    primary_offence = Column(String(100), index=True, nullable=True)
    subtype = Column(String(100), nullable=True)
    is_core_offence = Column(Boolean, default=True)

    victim_type = Column(Text, nullable=True)                  # JSON string list
    has_weapon = Column(Boolean, default=False)

    is_sexual_offence = Column(Boolean, default=False)
    is_property_offence = Column(Boolean, default=False)

    severity_level = Column(Integer, default=1)
    ipc_equivalent = Column(String(50), nullable=True)

    # Optional free-text for fallback search (title + text + offence)
    keywords = Column(Text, nullable=True)
