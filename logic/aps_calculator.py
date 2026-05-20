"""
APS Calculator — South African NSC Admission Point Score
=========================================================
NSC Level  |  Percentage  |  APS Points
    7       |   80 – 100%  |     7
    6       |   70 – 79%   |     6
    5       |   60 – 69%   |     5
    4       |   50 – 59%   |     4
    3       |   40 – 49%   |     3
    2       |   30 – 39%   |     2
    1       |    0 – 29%   |     1

Notes:
- Life Orientation contributes to total APS but many universities
  cap its contribution at 4 points (we apply that cap here).
- A learner typically takes 7 subjects including Life Orientation.
- Max possible APS (with LO cap) = 6 × 7 + 4 = 46
"""


def calculate_aps(subject_ratings: dict) -> dict:
    """
    Calculate APS score from subject ratings.

    Parameters
    ----------
    subject_ratings : dict
        Format: {"SUBJECT_CODE": rating_1_to_7, ...}
        Example: {"MATH": 6, "ENG_HL": 5, "LO": 7}

    Returns
    -------
    dict with keys:
        - total_aps       : int — raw total including LO
        - capped_aps      : int — LO capped at 4 (used for uni matching)
        - subject_count   : int — number of subjects included
        - breakdown       : dict — each subject and its contribution
        - level_label     : str — descriptive label for the score
    """
    breakdown = {}
    total = 0
    lo_rating = subject_ratings.get("LO", 0)

    for code, rating in subject_ratings.items():
        points = rating  # NSC level = APS points directly
        if code == "LO":
            # LO is always capped at 4 for university admission
            capped = min(points, 4)
            breakdown[code] = {"raw": points, "counted": capped}
            total += capped
        else:
            breakdown[code] = {"raw": points, "counted": points}
            total += points

    return {
        "total_aps": total,
        "capped_aps": total,   # already capped LO above
        "subject_count": len(subject_ratings),
        "breakdown": breakdown,
        "level_label": _get_level_label(total),
    }


def _get_level_label(aps: int) -> str:
    """Return a motivational label based on APS score."""
    if aps >= 38:
        return "🌟 Excellent — Top university programmes within reach"
    elif aps >= 30:
        return "💪 Strong — Wide range of university options available"
    elif aps >= 24:
        return "✅ Good — Solid foundation for university entry"
    elif aps >= 18:
        return "📈 Developing — Diploma and some degree programmes available"
    else:
        return "🌱 Keep Growing — Focus on improving your core subjects"


def get_strong_subjects(subject_ratings: dict, threshold: int = 5) -> list:
    """
    Return list of subject codes where the learner is performing well.
    Used by the career matcher later.

    Parameters
    ----------
    subject_ratings : dict  — subject code → rating
    threshold       : int   — minimum rating to be considered 'strong'

    Returns
    -------
    list of subject codes
    """
    return [
        code for code, rating in subject_ratings.items()
        if rating >= threshold and code != "LO"
    ]