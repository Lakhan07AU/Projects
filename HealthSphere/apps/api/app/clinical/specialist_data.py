"""Doctor & Specialist navigation knowledge seeds.

Structured specialties, a symptom catalog, and validated symptom/condition →
specialty navigation mappings stored as configurable data (never hard-coded
in UI). Navigation support only — these mappings never diagnose; each row
carries source + version + review metadata.
"""
from app.models import (
    ConditionSpecialtyMap,
    Specialty,
    Symptom,
    SymptomSpecialtyMap,
)

NAV_SOURCE = "healthsphere-clinical-navigation-reference"
NAV_VERSION = "2026.1"
NAV_REVIEWED = "2026-01"

SPECIALTIES = [
    {"key": "primary-care", "name": "Primary Care / General Physician",
     "description": "General healthcare entry point and first point of discussion."},
    {"key": "cardiology", "name": "Cardiology",
     "description": "Heart and blood-vessel health."},
    {"key": "endocrinology", "name": "Endocrinology",
     "description": "Hormonal conditions including diabetes and thyroid."},
    {"key": "dermatology", "name": "Dermatology",
     "description": "Skin, hair and nail concerns."},
    {"key": "neurology", "name": "Neurology",
     "description": "Brain, spine and nervous-system concerns."},
    {"key": "orthopedics", "name": "Orthopedic Specialist",
     "description": "Bones, joints and musculoskeletal injuries."},
    {"key": "rheumatology", "name": "Rheumatology",
     "description": "Joint inflammation and autoimmune joint conditions."},
    {"key": "pulmonology", "name": "Pulmonology",
     "description": "Lungs and breathing-related concerns."},
    {"key": "gastroenterology", "name": "Gastroenterology",
     "description": "Digestive system, liver and gut health."},
    {"key": "nephrology", "name": "Nephrology",
     "description": "Kidney health."},
    {"key": "urology", "name": "Urology",
     "description": "Urinary tract and male reproductive health."},
    {"key": "gynecology", "name": "Gynecology",
     "description": "Women's reproductive health."},
    {"key": "ophthalmology", "name": "Ophthalmology",
     "description": "Eye health and vision."},
    {"key": "ent", "name": "ENT Specialist",
     "description": "Ear, nose and throat concerns."},
    {"key": "psychiatry", "name": "Psychiatry",
     "description": "Mental health and emotional wellbeing."},
    {"key": "pediatrics", "name": "Pediatrics",
     "description": "Health of infants, children and adolescents."},
    {"key": "oncology", "name": "Oncology",
     "description": "Assessment of growths and cancer-related care."},
    {"key": "hematology", "name": "Hematology",
     "description": "Blood and blood-forming organs."},
    {"key": "allergy-immunology", "name": "Allergist / Immunologist",
     "description": "Allergies and immune-system conditions."},
    {"key": "infectious-disease", "name": "Infectious Disease Specialist",
     "description": "Infections and fever of unknown origin."},
]

# key -> (display name, category)
SYMPTOMS = {
    "persistent-skin-rash": ("Persistent skin rash", "skin"),
    "persistent-itching": ("Persistent itching", "skin"),
    "changing-mole": ("Mole changing shape or colour", "skin"),
    "persistent-vision-changes": ("Persistent vision changes", "eye"),
    "eye-pain-or-redness": ("Eye pain or redness", "eye"),
    "persistent-headache": ("Persistent headache", "neurological"),
    "recurrent-migraine": ("Recurrent migraine", "neurological"),
    "numbness-or-tingling": ("Numbness or tingling", "neurological"),
    "persistent-dizziness": ("Persistent dizziness", "neurological"),
    "seizure-or-fits": ("Seizure or fits", "neurological"),
    "persistent-joint-pain": ("Persistent joint pain", "joints"),
    "joint-swelling-stiffness": ("Joint swelling or stiffness", "joints"),
    "chronic-back-pain": ("Chronic back pain", "joints"),
    "persistent-cough": ("Persistent cough", "respiratory"),
    "shortness-of-breath": ("Shortness of breath", "respiratory"),
    "wheezing": ("Wheezing", "respiratory"),
    "chest-pain": ("Chest pain or tightness", "cardiac"),
    "palpitations": ("Palpitations or irregular heartbeat", "cardiac"),
    "leg-swelling": ("Swelling in the legs or ankles", "cardiac"),
    "excessive-thirst": ("Excessive thirst", "metabolic"),
    "frequent-urination": ("Frequent urination", "urinary"),
    "painful-urination": ("Painful or burning urination", "urinary"),
    "blood-in-urine": ("Blood in urine", "urinary"),
    "persistent-fatigue": ("Persistent fatigue", "general"),
    "unexplained-weight-loss": ("Unexplained weight loss", "general"),
    "persistent-fever": ("Persistent or recurrent fever", "general"),
    "stomach-pain": ("Recurrent stomach pain", "digestive"),
    "acidity-reflux": ("Acidity or acid reflux", "digestive"),
    "persistent-diarrhea": ("Persistent diarrhea", "digestive"),
    "blood-in-stool": ("Blood in stool", "digestive"),
    "ear-pain": ("Ear pain", "ent"),
    "persistent-sore-throat": ("Persistent sore throat", "ent"),
    "hearing-loss": ("Hearing loss", "ent"),
    "anxiety": ("Anxiety or panic", "mental-health"),
    "low-mood": ("Low mood or loss of interest", "mental-health"),
    "insomnia": ("Insomnia or disturbed sleep", "mental-health"),
}

# symptom_key -> [(specialty_key, relevance)]
SYMPTOM_SPECIALTY_MAPS = {
    "persistent-skin-rash": [("dermatology", "high"), ("primary-care", "medium")],
    "persistent-itching": [("dermatology", "high"), ("primary-care", "medium")],
    "changing-mole": [("dermatology", "high"), ("oncology", "low")],
    "persistent-vision-changes": [("ophthalmology", "high"), ("primary-care", "medium"),
                                  ("endocrinology", "low")],
    "eye-pain-or-redness": [("ophthalmology", "high"), ("primary-care", "medium")],
    "persistent-headache": [("neurology", "medium"), ("primary-care", "high")],
    "recurrent-migraine": [("neurology", "high"), ("primary-care", "medium")],
    "numbness-or-tingling": [("neurology", "high"), ("primary-care", "medium")],
    "persistent-dizziness": [("neurology", "medium"), ("ent", "medium"), ("primary-care", "high"),
                             ("cardiology", "low")],
    "seizure-or-fits": [("neurology", "high"), ("primary-care", "medium")],
    "persistent-joint-pain": [("primary-care", "high"), ("rheumatology", "medium"),
                              ("orthopedics", "medium")],
    "joint-swelling-stiffness": [("rheumatology", "high"), ("orthopedics", "medium"),
                                 ("primary-care", "medium")],
    "chronic-back-pain": [("orthopedics", "high"), ("primary-care", "medium")],
    "persistent-cough": [("pulmonology", "medium"), ("primary-care", "high")],
    "shortness-of-breath": [("pulmonology", "high"), ("cardiology", "medium"),
                            ("primary-care", "medium")],
    "wheezing": [("pulmonology", "high"), ("primary-care", "medium")],
    "chest-pain": [("cardiology", "high"), ("pulmonology", "medium"), ("primary-care", "medium")],
    "palpitations": [("cardiology", "high"), ("primary-care", "medium")],
    "leg-swelling": [("cardiology", "medium"), ("nephrology", "medium"), ("primary-care", "high")],
    "excessive-thirst": [("endocrinology", "high"), ("primary-care", "medium")],
    "frequent-urination": [("urology", "medium"), ("endocrinology", "high"),
                           ("primary-care", "medium")],
    "painful-urination": [("urology", "high"), ("primary-care", "medium")],
    "blood-in-urine": [("urology", "high"), ("nephrology", "medium"), ("primary-care", "medium")],
    "persistent-fatigue": [("primary-care", "high"), ("hematology", "low"),
                           ("endocrinology", "low")],
    "unexplained-weight-loss": [("primary-care", "high"), ("endocrinology", "medium"),
                                ("gastroenterology", "low"), ("oncology", "low")],
    "persistent-fever": [("primary-care", "high"), ("infectious-disease", "medium")],
    "stomach-pain": [("gastroenterology", "high"), ("primary-care", "medium")],
    "acidity-reflux": [("gastroenterology", "high"), ("primary-care", "medium")],
    "persistent-diarrhea": [("gastroenterology", "high"), ("primary-care", "medium")],
    "blood-in-stool": [("gastroenterology", "high"), ("primary-care", "medium")],
    "ear-pain": [("ent", "high"), ("primary-care", "medium")],
    "persistent-sore-throat": [("ent", "high"), ("primary-care", "medium")],
    "hearing-loss": [("ent", "high"), ("primary-care", "medium")],
    "anxiety": [("psychiatry", "high"), ("primary-care", "medium")],
    "low-mood": [("psychiatry", "high"), ("primary-care", "medium")],
    "insomnia": [("psychiatry", "medium"), ("primary-care", "high")],
}

# condition keyword fragment -> [(specialty_key, relevance)]
CONDITION_SPECIALTY_MAPS = {
    "diabet": [("endocrinology", "high"), ("primary-care", "medium")],
    "thyroid": [("endocrinology", "high"), ("primary-care", "medium")],
    "pcos": [("gynecology", "high"), ("endocrinology", "medium")],
    "pcod": [("gynecology", "high"), ("endocrinology", "medium")],
    "hypertens": [("cardiology", "high"), ("primary-care", "medium")],
    "blood pressure": [("cardiology", "high"), ("primary-care", "medium")],
    "cholesterol": [("cardiology", "medium"), ("primary-care", "medium")],
    "heart diseas": [("cardiology", "high"), ("primary-care", "medium")],
    "coronary": [("cardiology", "high")],
    "asthma": [("pulmonology", "high"), ("primary-care", "medium")],
    "copd": [("pulmonology", "high")],
    "arthriti": [("rheumatology", "high"), ("orthopedics", "medium")],
    "osteoporos": [("orthopedics", "high"), ("primary-care", "medium")],
    "anemia": [("hematology", "medium"), ("primary-care", "high")],
    "anaemia": [("hematology", "medium"), ("primary-care", "high")],
    "kidney": [("nephrology", "high"), ("primary-care", "medium")],
    "liver": [("gastroenterology", "high"), ("primary-care", "medium")],
    "migraine": [("neurology", "high"), ("primary-care", "medium")],
    "epilep": [("neurology", "high"), ("primary-care", "medium")],
}


def seed_specialist_knowledge(db) -> None:
    """Idempotently insert specialties, symptoms and navigation mappings."""
    specialty_by_key = {s.key: s for s in db.query(Specialty).all()}
    for spec in SPECIALTIES:
        if spec["key"] not in specialty_by_key:
            row = Specialty(**spec)
            db.add(row)
            db.flush()
            specialty_by_key[spec["key"]] = row
    db.flush()

    existing_symptom_keys = {s.key for s in db.query(Symptom).all()}
    symptom_by_key = {s.key: s for s in db.query(Symptom).all()}
    for key, (name, category) in SYMPTOMS.items():
        if key not in existing_symptom_keys:
            row = Symptom(key=key, name=name, category=category)
            db.add(row)
            db.flush()
            symptom_by_key[key] = row
    db.flush()

    existing_pairs = {
        (m.symptom_id, m.specialty_id) for m in db.query(SymptomSpecialtyMap).all()
    }
    for sym_key, targets in SYMPTOM_SPECIALTY_MAPS.items():
        symptom = symptom_by_key.get(sym_key)
        if symptom is None:
            continue
        for spec_key, relevance in targets:
            specialty = specialty_by_key.get(spec_key)
            if specialty is None or (symptom.id, specialty.id) in existing_pairs:
                continue
            db.add(SymptomSpecialtyMap(
                symptom_id=symptom.id,
                specialty_id=specialty.id,
                relevance=relevance,
                source=NAV_SOURCE,
                source_version=NAV_VERSION,
                last_reviewed=NAV_REVIEWED,
            ))

    existing_condition_pairs = {
        (m.condition_keyword, m.specialty_id) for m in db.query(ConditionSpecialtyMap).all()
    }
    for keyword, targets in CONDITION_SPECIALTY_MAPS.items():
        for spec_key, relevance in targets:
            specialty = specialty_by_key.get(spec_key)
            if specialty is None:
                continue
            pair = (keyword.lower(), specialty.id)
            if pair in existing_condition_pairs:
                continue
            db.add(ConditionSpecialtyMap(
                condition_keyword=keyword.lower(),
                specialty_id=specialty.id,
                relevance=relevance,
                source=NAV_SOURCE,
                source_version=NAV_VERSION,
                last_reviewed=NAV_REVIEWED,
            ))
    db.commit()