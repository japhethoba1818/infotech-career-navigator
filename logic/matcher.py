"""
Career Matcher
==============
Combines three signals to score every career for a learner:

  Signal 1 — Subject Match  (40% of total score)
    · +3 points per required subject the learner has
    · +1 point per preferred subject the learner has
    · Each point is multiplied by the learner's rating for that subject
      (rating / 7) so a Level 7 student scores higher than a Level 4

  Signal 2 — APS Match  (30% of total score)
    · 100 pts → learner APS meets or exceeds minimum
    · 70 pts  → learner is within 5 points of minimum
    · 40 pts  → learner is within 10 points of minimum
    · 15 pts  → learner is more than 10 below minimum

  Signal 3 — Personality Match  (30% of total score)
    · Each career has personality weights (0–3 per type)
    · Learner's personality score for that type × career weight
    · Normalised to 0–100

Final match % is the weighted average of the three signals.
"""

import json


def load_careers() -> list:
    with open("data/careers.json") as f:
        return json.load(f)["careers"]


# ── Individual signal scorers ─────────────────────────────────────────────────

def _subject_score(career: dict, subject_ratings: dict) -> float:
    """Return a 0–100 subject match score."""
    raw   = 0.0
    max_r = 0.0

    for code in career.get("required_subjects", []):
        max_r += 3.0          # maximum possible for a required subject
        if code in subject_ratings:
            raw += 3.0 * (subject_ratings[code] / 7.0)

    for code in career.get("preferred_subjects", []):
        max_r += 1.0
        if code in subject_ratings:
            raw += 1.0 * (subject_ratings[code] / 7.0)

    if max_r == 0:
        return 60.0           # career has no subject requirements → neutral score
    return round((raw / max_r) * 100, 1)


def _aps_score(career: dict, learner_aps: int) -> float:
    """Return a 0–100 APS match score."""
    min_aps = career.get("min_aps", 0)
    gap     = learner_aps - min_aps

    if gap >= 0:
        return 100.0
    elif gap >= -5:
        return 70.0
    elif gap >= -10:
        return 40.0
    else:
        return 15.0


def _personality_score(career: dict, personality_scores: dict) -> float:
    """Return a 0–100 personality match score."""
    weights   = career.get("personality_match", {})
    max_score = sum(w * 24 for w in weights.values())  # max learner score per type ≈ 24
    raw       = sum(
        weights.get(code, 0) * personality_scores.get(code, 0)
        for code in weights
    )
    if max_score == 0:
        return 50.0
    return round(min((raw / max_score) * 100, 100), 1)


# ── Explanation builder ───────────────────────────────────────────────────────

def _build_reasons(
    career: dict,
    subject_ratings: dict,
    learner_aps: int,
    top_personality: list,
    personality_labels: dict,
    personality_icons: dict,
) -> list:
    """
    Build up to 4 short human-readable reason strings explaining
    why this career matches the learner.
    """
    reasons = []

    # Subject reasons
    matched_required  = [c for c in career.get("required_subjects", []) if c in subject_ratings]
    matched_preferred = [c for c in career.get("preferred_subjects", []) if c in subject_ratings]

    if matched_required:
        subj_names = _codes_to_names(matched_required)
        reasons.append(f"📚 You take {subj_names} — key subjects for this career")

    if matched_preferred and len(reasons) < 2:
        subj_names = _codes_to_names(matched_preferred[:2])
        reasons.append(f"✅ Your {subj_names} background gives you an advantage")

    # APS reason
    min_aps = career.get("min_aps", 0)
    gap     = learner_aps - min_aps
    if gap >= 0:
        reasons.append(f"🎯 Your APS of {learner_aps} meets the minimum requirement of {min_aps}")
    elif gap >= -5:
        reasons.append(
            f"📈 Your APS of {learner_aps} is close to the {min_aps} requirement — "
            f"improving {abs(gap)} points gets you there"
        )

    # Personality reasons
    career_weights = career.get("personality_match", {})
    matched_types  = [
        t for t in top_personality
        if career_weights.get(t, 0) >= 2
    ]
    if matched_types:
        type_name = personality_labels.get(matched_types[0], matched_types[0])
        icon      = personality_icons.get(matched_types[0], "💡")
        reasons.append(f"{icon} Your {type_name} personality is a strong match for this career")

    return reasons if reasons else ["This career aligns with your overall profile."]


def _codes_to_names(codes: list) -> str:
    """Convert subject codes to readable names for display."""
    code_map = {
        "MATH": "Mathematics", "MATLIT": "Mathematical Literacy",
        "PHY_SCI": "Physical Sciences", "LIFE_SCI": "Life Sciences",
        "AGR_SCI": "Agricultural Sciences", "ACC": "Accounting",
        "BUS_STU": "Business Studies", "ECON": "Economics",
        "GEO": "Geography", "HIST": "History", "IT": "IT",
        "CAT": "CAT", "EGD": "Engineering Graphics & Design",
        "VIS_ARTS": "Visual Arts", "DRAM": "Dramatic Arts",
        "ENG_HL": "English", "ENG_FAL": "English",
    }
    names = [code_map.get(c, c) for c in codes]
    if len(names) == 1:
        return names[0]
    if len(names) == 2:
        return f"{names[0]} and {names[1]}"
    return f"{', '.join(names[:-1])} and {names[-1]}"


# ── Main matching function ────────────────────────────────────────────────────

def match_careers(
    subject_ratings: dict,
    learner_aps: int,
    personality_scores: dict,
    top_personality: list,
    personality_labels: dict,
    personality_icons: dict,
    top_n: int = 3,
) -> list:
    """
    Score all careers and return the top N matches.

    Returns
    -------
    list of dicts, each containing:
        career        : original career dict from JSON
        match_pct     : int — overall match percentage (0–100)
        subject_score : float
        aps_score     : float
        personality_score : float
        reasons       : list of str — explanation bullets
    """
    careers = load_careers()
    scored  = []

    for career in careers:
        s_score = _subject_score(career, subject_ratings)
        a_score = _aps_score(career, learner_aps)
        p_score = _personality_score(career, personality_scores)

        # Weighted total
        total = (s_score * 0.40) + (a_score * 0.30) + (p_score * 0.30)

        reasons = _build_reasons(
            career, subject_ratings, learner_aps,
            top_personality, personality_labels, personality_icons,
        )

        scored.append({
            "career":            career,
            "match_pct":         round(total),
            "subject_score":     round(s_score),
            "aps_score":         round(a_score),
            "personality_score": round(p_score),
            "reasons":           reasons,
        })

    # Sort by match percentage descending
    scored.sort(key=lambda x: x["match_pct"], reverse=True)
    return scored[:top_n]