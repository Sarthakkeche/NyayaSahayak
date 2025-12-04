# nlp.py
import spacy

nlp = spacy.load("en_core_web_sm")

"""
We output HIGH-LEVEL offence tags like:
  - "hurt_simple"
  - "hurt_grievous"
  - "hurt_weapon"
  - "murder"
  - "attempt_murder"
  - "criminal_intimidation"
  - "sexual_misconduct"
  - "sexual_rape"
  - "theft"
  - "robbery"
  - "house_trespass"
  - "cheating"
  - "forgery"
  - "property_marks"
  - "public_mischief"
  - "public_drunkenness"
  - "cyber_fraud"
  - "extortion_threat"
These are then mapped to your DB primary_offence values in main.py.
"""


def extract_primary_offences(text: str) -> tuple[list[str], list[str]]:
    """
    Return:
      - offence_tags: list of strings (see above)
      - lemmas: list of lemmas, for debug and context rules
    """
    doc = nlp(text.lower())
    lemmas: list[str] = []

    for token in doc:
        if token.is_stop or token.is_punct or token.is_space:
            continue
        lemmas.append(token.lemma_)

    lemmas_set = set(lemmas)
    offences: set[str] = set()

    # --- BASIC FLAGS ---
    has_weapon_word = any(
        w in lemmas_set
        for w in ["knife", "gun", "pistol", "rod", "stick", "sword", "weapon", "acid"]
    )
    has_fracture = "fracture" in lemmas_set
    has_serious = any(w in lemmas_set for w in ["serious", "critical", "hospital"])
    has_death_word = any(w in lemmas_set for w in ["dead", "death", "die", "died"])
    has_threat_word = any(w in lemmas_set for w in ["threaten", "threat", "warn"])

    is_public_place = any(
        w in lemmas_set
        for w in ["road", "street", "market", "bus", "train", "station", "park"]
    )
    victim_is_woman = any(
        w in lemmas_set for w in ["woman", "women", "girl", "lady", "female", "wife"]
    )

    has_money = any(w in lemmas_set for w in ["money", "cash", "amount", "rupee"])
    has_pay = "pay" in lemmas_set

    # --- HURT / ASSAULT ---
    if any(w in lemmas_set for w in ["slap", "hit", "beat", "punch", "kick", "hurt"]):
        # default simple hurt
        offences.add("hurt_simple")

        # upgrade to weapon / grievous if indicators present
        if has_weapon_word:
            offences.add("hurt_weapon")
        if has_fracture or has_serious:
            offences.add("hurt_grievous")

    # --- GRIEVOUS WITHOUT CLASSIC HURT WORDS ---
    if has_fracture or ("acid" in lemmas_set):
        offences.add("hurt_grievous")
        if has_weapon_word:
            offences.add("hurt_weapon")

    # --- MURDER / ATTEMPT TO MURDER VS THREAT TO KILL ---
    if "kill" in lemmas_set or "murder" in lemmas_set or "shoot" in lemmas_set:
        if has_threat_word and not has_death_word:
            # "threaten to kill" -> criminal intimidation, NOT murder
            offences.add("criminal_intimidation")
        else:
            # actual killing or serious attack
            if has_death_word:
                offences.add("murder")
            else:
                # serious attack with killing words but no explicit death
                offences.add("attempt_murder")

    # --- SEXUAL OFFENCES ---
    if any(w in lemmas_set for w in ["rape", "raped"]):
        offences.add("sexual_rape")
    if any(w in lemmas_set for w in ["touch", "molest", "harass"]) and victim_is_woman:
        offences.add("sexual_misconduct")

    # --- THEFT / ROBBERY / HOUSE TRESPASS ---
    if any(w in lemmas_set for w in ["steal", "stole", "theft", "pick", "pickpocket"]):
        offences.add("theft")

    if any(w in lemmas_set for w in ["snatch", "snatching", "loot", "rob", "robbery"]):
        offences.add("robbery")

    if any(w in lemmas_set for w in ["house", "home", "shop"]) and any(
        w in lemmas_set for w in ["break", "broke", "enter", "trespass", "trespasser"]
    ):
        offences.add("house_trespass")

    # --- CHEATING / FORGERY / PROPERTY MARKS / CYBER FRAUD ---
    if any(w in lemmas_set for w in ["cheat", "cheating", "fraud", "scam"]):
        offences.add("cheating")

    if any(w in lemmas_set for w in ["forge", "forgery", "fake", "counterfeit"]):
        offences.add("forgery")

    if any(w in lemmas_set for w in ["brand", "label", "mark"]) and any(
        w in lemmas_set for w in ["fake", "counterfeit"]
    ):
        offences.add("property_marks")

    if any(w in lemmas_set for w in ["online", "upi", "gpay", "phonepe", "account"]):
        if "fraud" in lemmas_set or "cheat" in lemmas_set or "scam" in lemmas_set:
            offences.add("cyber_fraud")
            offences.add("cheating")

    # --- THREATS / PUBLIC MISCHIEF / DRUNKENNESS ---
    if has_threat_word:
        offences.add("criminal_intimidation")

    if any(w in lemmas_set for w in ["burn", "fire", "riot", "stone"]):
        if has_threat_word:
            offences.add("criminal_intimidation")
            if has_money or has_pay:
                offences.add("extortion_threat")
        else:
            offences.add("public_mischief")

    if any(w in lemmas_set for w in ["drunk", "intoxicated", "drink", "liquor"]):
        offences.add("public_drunkenness")

    # ensure deterministic order (for stable UI)
    ordered = sorted(offences)

    return ordered, lemmas
