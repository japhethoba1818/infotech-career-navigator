"""
APS Calculator — South African NSC Admission Point Score
=========================================================
CORRECTED STANDARD:
    Life Orientation is EXCLUDED from APS calculations.
    Most South African universities do not count LO in their
    admission point score.

    APS = sum of your best subjects (NOT including Life Orientation)

NSC Level  |  Percentage  |  APS Points
    7       |   80 – 100%  |     7
    6       |   70 – 79%   |     6
    5       |   60 – 69%   |     5
    4       |   50 – 59%   |     4
    3       |   40 – 49%   |     3
    2       |   30 – 39%   |     2
    1       |    0 – 29%   |     1

A typical learner takes 7 subjects including Life Orientation.
APS is calculated from the remaining 6 (excluding LO).
Maximum possible APS = 6 × 7 = 42
"""

# Subjects that are EXCLUDED from APS calculations
EXCLUDED_FROM_APS = {"LO"}


def calculate_aps(subject_ratings: dict) -> dict:
    """
    Calculate APS score from subject ratings.

    Parameters
    ----------
    subject_ratings : dict
        Format: {"SUBJECT_CODE": rating_1_to_7, ...}
        Example: {"MATH": 6, "ENG_HL": 5, "LO": 7}
        Life Orientation (LO) is automatically excluded.

    Returns
    -------
    dict with keys:
        total_aps     : int  — APS total (LO excluded)
        subject_count : int  — number of subjects counted
        lo_excluded   : bool — whether LO was found and excluded
        breakdown     : dict — each subject and its points
        level_label   : str  — motivational label for the score
    """
    breakdown  = {}
    total      = 0
    lo_found   = False

    for code, rating in subject_ratings.items():
        if code in EXCLUDED_FROM_APS:
            lo_found = True
            # Still record it in breakdown so learner can see it
            # but mark it as not counted
            breakdown[code] = {"points": rating, "counted": False}
            continue

        # Every other subject counts at face value
        breakdown[code] = {"points": rating, "counted": True}
        total += rating

    return {
        "total_aps":     total,
        "capped_aps":    total,   # kept for backward compatibility
        "subject_count": len([c for c in breakdown if breakdown[c]["counted"]]),
        "lo_excluded":   lo_found,
        "breakdown":     breakdown,
        "level_label":   _get_level_label(total),
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
    Return list of subject codes where the learner performs well.
    Used by the career matcher.

    Automatically excludes Life Orientation.
    """
    return [
        code for code, rating in subject_ratings.items()
        if rating >= threshold and code not in EXCLUDED_FROM_APS
    ]