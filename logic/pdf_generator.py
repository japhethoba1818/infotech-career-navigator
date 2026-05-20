"""
PDF Roadmap Generator
=====================
Generates a 2-page personalised career manifesto PDF for the learner.

Page 1 — The Manifesto
    · Hero header with learner name and career title
    · Personal profile (APS, personality, subjects)
    · Career match details
    · Motivational quote

Page 2 — The Action Plan
    · 5-step success roadmap
    · University targets with APS gap
    · Subject focus advice
    · Application checklist
"""

from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas as rl_canvas
import textwrap


# ── Colour palette (matches the app theme) ────────────────────────────────────
C_PURPLE     = HexColor("#667eea")
C_VIOLET     = HexColor("#764ba2")
C_DARK       = HexColor("#1f2937")
C_MID        = HexColor("#4b5563")
C_LIGHT      = HexColor("#6b7280")
C_PALE       = HexColor("#f3f4f6")
C_GREEN      = HexColor("#10b981")
C_AMBER      = HexColor("#f59e0b")
C_RED        = HexColor("#ef4444")
C_LAVENDER   = HexColor("#ede9fe")
C_PURPLE_DIM = HexColor("#667eea33")

PAGE_W, PAGE_H = A4   # 210mm × 297mm  →  595.3pt × 841.9pt
MARGIN = 20 * mm


# ── Helpers ───────────────────────────────────────────────────────────────────

def _wrap(text: str, width: int) -> list:
    return textwrap.wrap(text, width=width)


def _subject_name(code: str) -> str:
    names = {
        "MATH": "Mathematics", "MATLIT": "Mathematical Literacy",
        "PHY_SCI": "Physical Sciences", "LIFE_SCI": "Life Sciences",
        "AGR_SCI": "Agricultural Sciences", "ACC": "Accounting",
        "BUS_STU": "Business Studies", "ECON": "Economics",
        "GEO": "Geography", "HIST": "History", "IT": "Information Technology",
        "CAT": "Computer Applications Tech", "EGD": "Engineering Graphics & Design",
        "VIS_ARTS": "Visual Arts", "DRAM": "Dramatic Arts", "MUSIC": "Music",
        "ENG_HL": "English Home Language", "ENG_FAL": "English FAL",
        "AFR_HL": "Afrikaans HL", "AFR_FAL": "Afrikaans FAL",
        "ZUL_HL": "IsiZulu HL", "XHO_HL": "IsiXhosa HL",
        "NSO_HL": "Sepedi HL", "LO": "Life Orientation",
    }
    return names.get(code, code)


def _level_label(rating: int) -> str:
    labels = {7: "80–100%", 6: "70–79%", 5: "60–69%",
              4: "50–59%", 3: "40–49%", 2: "30–39%", 1: "0–29%"}
    return labels.get(rating, "")


QUOTES = {
    "medical_doctor":      ("The good physician treats the disease; the great physician treats the patient.", "William Osler"),
    "software_engineer":   ("The computer was born to solve problems that did not exist before.", "Bill Gates"),
    "electrical_engineer": ("Scientists study the world as it is; engineers create the world that never has been.", "Theodore von Kármán"),
    "civil_engineer":      ("Engineering is the closest thing to magic that exists in the world.", "Elon Musk"),
    "chartered_accountant":("An investment in knowledge pays the best interest.", "Benjamin Franklin"),
    "data_scientist":      ("Data is the new oil. It is valuable, but if unrefined it cannot really be used.", "Clive Humby"),
    "nurse":               ("Nurses dispense comfort, compassion, and caring without even a prescription.", "Val Saintsbury"),
    "teacher":             ("Education is the most powerful weapon which you can use to change the world.", "Nelson Mandela"),
    "lawyer":              ("Injustice anywhere is a threat to justice everywhere.", "Martin Luther King Jr."),
    "architect":           ("Architecture is inhabited sculpture.", "Constantin Brancusi"),
    "graphic_designer":    ("Design is not just what it looks like. Design is how it works.", "Steve Jobs"),
    "entrepreneur":        ("Your most unhappy customers are your greatest source of learning.", "Bill Gates"),
    "agricultural_scientist": ("To forget how to dig the earth and to tend the soil is to forget ourselves.", "Mahatma Gandhi"),
    "social_worker":       ("We make a living by what we get, but we make a life by what we give.", "Winston Churchill"),
    "journalist":          ("Journalism is the first rough draft of history.", "Philip Graham"),
    "environmental_scientist": ("In every walk with nature, one receives far more than he seeks.", "John Muir"),
    "psychologist":        ("Knowing yourself is the beginning of all wisdom.", "Aristotle"),
    "it_network_admin":    ("The advance of technology is based on making it fit in so that you don't really notice it.", "Bill Gates"),
    "financial_analyst":   ("Rule No. 1: Never lose money. Rule No. 2: Never forget Rule No. 1.", "Warren Buffett"),
    "mechanical_engineer": ("One machine can do the work of fifty ordinary men. No machine can do the work of one extraordinary man.", "Elbert Hubbard"),
    "pharmacist":          ("The art of medicine consists of amusing the patient while nature cures the disease.", "Voltaire"),
    "game_developer":      ("Video games are bad for you? That's what they said about rock and roll.", "Shigeru Miyamoto"),
    "marketing_manager":   ("Make your customer the hero of your story.", "Ann Handley"),
    "biomedical_scientist":("The good news is that science has the answers. The better news is that you can find them.", "Anonymous"),
    "urban_planner":       ("A great city is not to be confounded with a populous one.", "Aristotle"),
}

DEFAULT_QUOTE = ("Success is not the key to happiness. Happiness is the key to success.", "Albert Schweitzer")


# ── Drawing utilities ─────────────────────────────────────────────────────────

def _rounded_rect(c, x, y, w, h, radius=5*mm, fill_color=None, stroke_color=None):
    if fill_color:
        c.setFillColor(fill_color)
    if stroke_color:
        c.setStrokeColor(stroke_color)
        c.setLineWidth(0.5)
    else:
        c.setStrokeColor(fill_color or C_PALE)
    c.roundRect(x, y, w, h, radius, fill=1 if fill_color else 0, stroke=1)


def _section_header(c, x, y, text, colour=C_PURPLE):
    c.setFillColor(colour)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(x, y, text)
    c.setStrokeColor(colour)
    c.setLineWidth(1.5)
    c.line(x, y - 2*mm, PAGE_W - MARGIN, y - 2*mm)


def _tag(c, x, y, text, bg=C_LAVENDER, fg=C_VIOLET, font_size=8):
    """Draw a pill-shaped tag."""
    text_width = c.stringWidth(text, "Helvetica", font_size) + 8*mm
    _rounded_rect(c, x, y - 4*mm, text_width, 6*mm, radius=3*mm, fill_color=bg)
    c.setFillColor(fg)
    c.setFont("Helvetica", font_size)
    c.drawString(x + 4*mm, y - 1*mm, text)
    return x + text_width + 2*mm   # return next x position


# ── PAGE 1 — The Manifesto ────────────────────────────────────────────────────

def _draw_page1(c, data: dict):
    w, h = PAGE_W, PAGE_H

    # ── Hero band ─────────────────────────────────────────────────────────────
    band_h = 80 * mm

    # Background gradient simulation (two stacked rects)
    c.setFillColor(C_PURPLE)
    c.rect(0, h - band_h, w, band_h / 2, fill=1, stroke=0)
    c.setFillColor(C_VIOLET)
    c.rect(0, h - band_h, w, band_h / 2, fill=1, stroke=0)
    c.setFillColor(C_PURPLE)
    c.rect(0, h - band_h / 2, w, band_h / 2, fill=1, stroke=0)

    # Decorative circle
    c.setFillColor(HexColor("#ffffff18"))
    c.circle(w - 25*mm, h - 20*mm, 30*mm, fill=1, stroke=0)
    c.circle(15*mm, h - band_h + 10*mm, 18*mm, fill=1, stroke=0)

    # "SUCCESS MANIFESTO" label
    c.setFillColor(HexColor("#ffffff88"))
    c.setFont("Helvetica", 8)
    c.drawString(MARGIN, h - 12*mm, "✦  INFOTECH CAREER NAVIGATOR  ·  SUCCESS MANIFESTO  ✦")

    # Learner name
    name = data["learner_name"]
    career_title = data["primary_career"]["title"]

    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(MARGIN, h - 28*mm, f"Future {career_title}")

    c.setFont("Helvetica-Bold", 16)
    c.drawString(MARGIN, h - 40*mm, name)

    # APS badge
    aps = data["aps_score"]
    badge_x = w - MARGIN - 28*mm
    badge_y = h - 52*mm
    c.setFillColor(white)
    c.roundRect(badge_x, badge_y, 28*mm, 18*mm, 4*mm, fill=1, stroke=0)
    c.setFillColor(C_VIOLET)
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(badge_x + 14*mm, badge_y + 9*mm, str(aps))
    c.setFont("Helvetica", 7)
    c.drawCentredString(badge_x + 14*mm, badge_y + 3*mm, "APS SCORE")

    # Tagline
    c.setFillColor(HexColor("#ffffffcc"))
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(MARGIN, h - 54*mm, f'"{data["primary_career"]["tagline"]}"')

    # Match %
    c.setFillColor(HexColor("#ffffff88"))
    c.setFont("Helvetica", 9)
    pct = data["primary_match_pct"]
    c.drawString(MARGIN, h - 65*mm, f"Career Match Score: {pct}%   ·   {data['top_personality_label']} Personality")

    # ── BODY starts below band ─────────────────────────────────────────────────
    body_y = h - band_h - 10*mm

    # ── Profile section ───────────────────────────────────────────────────────
    _section_header(c, MARGIN, body_y, "YOUR PROFILE")
    body_y -= 8*mm

    # Three profile boxes
    box_w  = (w - 2*MARGIN - 8*mm) / 3
    box_h  = 22*mm
    labels = ["APS Score", "Personality Type", "Subjects Selected"]
    values = [
        str(data["aps_score"]),
        data["top_personality_label"],
        str(data["subject_count"]),
    ]
    sub_labels = ["Your academic strength", data["top_personality_desc"][:30] + "...", "Subjects captured"]

    for i, (lbl, val, sub) in enumerate(zip(labels, values, sub_labels)):
        bx = MARGIN + i * (box_w + 4*mm)
        _rounded_rect(c, bx, body_y - box_h, box_w, box_h, radius=3*mm, fill_color=C_PALE)
        c.setFillColor(C_LIGHT)
        c.setFont("Helvetica", 7)
        c.drawCentredString(bx + box_w / 2, body_y - 5*mm, lbl.upper())
        c.setFillColor(C_PURPLE)
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(bx + box_w / 2, body_y - 13*mm, val)
        c.setFillColor(C_LIGHT)
        c.setFont("Helvetica", 7)
        c.drawCentredString(bx + box_w / 2, body_y - 18*mm, sub[:28])

    body_y -= box_h + 8*mm

    # ── Strong subjects ───────────────────────────────────────────────────────
    _section_header(c, MARGIN, body_y, "YOUR STRONGEST SUBJECTS")
    body_y -= 8*mm

    tag_x = MARGIN
    for code, rating in sorted(data["subject_ratings"].items(),
                                key=lambda x: x[1], reverse=True)[:6]:
        label = f"{_subject_name(code)} (Level {rating})"
        if tag_x + 50*mm > w - MARGIN:
            tag_x  = MARGIN
            body_y -= 8*mm
        tag_x = _tag(c, tag_x, body_y, label)

    body_y -= 12*mm

    # ── Top 3 career matches ──────────────────────────────────────────────────
    _section_header(c, MARGIN, body_y, "YOUR TOP 3 CAREER MATCHES")
    body_y -= 8*mm

    rank_icons  = ["🥇", "🥈", "🥉"]
    rank_labels = ["First Choice", "Second Choice", "Third Choice"]
    rank_colors = [C_PURPLE, HexColor("#f5576c"), HexColor("#00c6fb")]

    for i, career_result in enumerate(data["chosen_careers"][:3]):
        career = career_result["career"]
        pct    = career_result["match_pct"]
        col    = rank_colors[i]

        # Left accent bar
        c.setFillColor(col)
        c.rect(MARGIN, body_y - 10*mm, 2*mm, 10*mm, fill=1, stroke=0)

        # Career info
        c.setFillColor(C_DARK)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(MARGIN + 5*mm, body_y - 4*mm, f"{rank_labels[i]}: {career['title']}")
        c.setFillColor(C_LIGHT)
        c.setFont("Helvetica", 8)
        c.drawString(MARGIN + 5*mm, body_y - 8*mm, f"{career['tagline']}   ·   {pct}% match")

        body_y -= 13*mm

    body_y -= 4*mm

    # ── Motivational quote ────────────────────────────────────────────────────
    primary_id = data["primary_career"]["id"]
    quote_text, quote_author = QUOTES.get(primary_id, DEFAULT_QUOTE)

    quote_box_h = 22*mm
    _rounded_rect(
        c, MARGIN, body_y - quote_box_h,
        w - 2 * MARGIN, quote_box_h,
        radius=4*mm, fill_color=C_LAVENDER,
    )

    # Decorative quote mark
    c.setFillColor(C_PURPLE)
    c.setFont("Helvetica-Bold", 36)
    c.drawString(MARGIN + 4*mm, body_y - 8*mm, "\u201c")

    lines = _wrap(quote_text, 70)
    c.setFillColor(C_VIOLET)
    c.setFont("Helvetica-Oblique", 9)
    qy = body_y - 8*mm
    for line in lines[:3]:
        c.drawString(MARGIN + 14*mm, qy, line)
        qy -= 5*mm

    c.setFillColor(C_LIGHT)
    c.setFont("Helvetica", 8)
    c.drawString(MARGIN + 14*mm, body_y - quote_box_h + 4*mm, f"— {quote_author}")

    body_y -= quote_box_h + 6*mm

    # ── Footer ────────────────────────────────────────────────────────────────
    c.setFillColor(C_PURPLE)
    c.rect(0, 0, w, 10*mm, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica", 7)
    c.drawCentredString(w / 2, 3*mm, "InfoTech Career Navigator  ·  Discover Your Future  ·  Made for South African Learners")


# ── PAGE 2 — The Action Plan ──────────────────────────────────────────────────

def _draw_page2(c, data: dict):
    w, h = PAGE_W, PAGE_H

    # ── Mini header ───────────────────────────────────────────────────────────
    c.setFillColor(C_PURPLE)
    c.rect(0, h - 20*mm, w, 20*mm, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(MARGIN, h - 13*mm, f"Action Plan  ·  {data['learner_name']}")
    c.setFont("Helvetica", 9)
    c.drawRightString(w - MARGIN, h - 13*mm, f"Primary Goal: {data['primary_career']['title']}")

    body_y = h - 28*mm

    # ── 5-Step Success Roadmap ────────────────────────────────────────────────
    _section_header(c, MARGIN, body_y, "YOUR 5-STEP SUCCESS ROADMAP")
    body_y -= 8*mm

    steps = _build_roadmap_steps(data)

    for i, (step_title, step_desc) in enumerate(steps):
        # Step number circle
        cx = MARGIN + 5*mm
        cy = body_y - 5*mm
        c.setFillColor(C_PURPLE)
        c.circle(cx, cy, 4*mm, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(cx, cy - 2*mm, str(i + 1))

        # Step text
        c.setFillColor(C_DARK)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(MARGIN + 12*mm, body_y - 3*mm, step_title)
        c.setFillColor(C_MID)
        c.setFont("Helvetica", 8)
        lines = _wrap(step_desc, 85)
        ly = body_y - 8*mm
        for line in lines[:2]:
            c.drawString(MARGIN + 12*mm, ly, line)
            ly -= 4*mm

        # Connecting line (except last)
        if i < len(steps) - 1:
            c.setStrokeColor(HexColor("#667eea44"))
            c.setLineWidth(1)
            c.line(cx, cy - 4*mm, cx, cy - 13*mm)

        body_y -= 16*mm

    body_y -= 4*mm

    # ── University targets ────────────────────────────────────────────────────
    _section_header(c, MARGIN, body_y, "YOUR UNIVERSITY TARGETS (PRIMARY CAREER)")
    body_y -= 8*mm

    primary_id  = data["primary_career"]["id"]
    universities = data["guidance"].get(primary_id, {}).get("universities", [])[:4]
    learner_aps  = data["aps_score"]

    # Two columns
    col_w   = (w - 2 * MARGIN - 5*mm) / 2
    col_gap = 5*mm

    for i, uni in enumerate(universities):
        col_idx = i % 2
        ux = MARGIN + col_idx * (col_w + col_gap)

        if i == 2:
            body_y -= 14*mm

        gap   = learner_aps - uni["min_aps"]
        color = C_GREEN if gap >= 0 else (C_AMBER if gap >= -5 else C_RED)
        status = "✓ Qualifies" if gap >= 0 else (f"↑ Need +{abs(gap)}" if gap >= -10 else f"Target (+{abs(gap)})")

        _rounded_rect(c, ux, body_y - 12*mm, col_w, 12*mm, radius=2*mm, fill_color=C_PALE)
        c.setFillColor(C_DARK)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(ux + 3*mm, body_y - 5*mm, uni["short"])
        c.setFillColor(C_LIGHT)
        c.setFont("Helvetica", 7)
        c.drawString(ux + 3*mm, body_y - 9*mm, f"Min APS: {uni['min_aps']}  ·  Deadline: {uni['deadline']}")
        c.setFillColor(color)
        c.setFont("Helvetica-Bold", 7)
        c.drawRightString(ux + col_w - 3*mm, body_y - 5*mm, status)

    body_y -= 18*mm

    # ── Subject focus table ───────────────────────────────────────────────────
    _section_header(c, MARGIN, body_y, "SUBJECT IMPROVEMENT FOCUS")
    body_y -= 8*mm

    # Sort subjects by rating ascending (lowest first = biggest improvement need)
    sorted_subjects = sorted(
        data["subject_ratings"].items(), key=lambda x: x[1]
    )[:6]

    col_w3 = (w - 2 * MARGIN - 6*mm) / 3

    for i, (code, rating) in enumerate(sorted_subjects):
        col_i  = i % 3
        sx     = MARGIN + col_i * (col_w3 + 3*mm)
        if i == 3:
            body_y -= 14*mm

        target = min(rating + 1, 7)
        bar_fill_w = col_w3 * (rating / 7)

        _rounded_rect(c, sx, body_y - 12*mm, col_w3, 12*mm, radius=2*mm, fill_color=C_PALE)
        c.setFillColor(C_PURPLE)
        c.rect(sx, body_y - 12*mm, bar_fill_w, 3*mm, fill=1, stroke=0)

        c.setFillColor(C_DARK)
        c.setFont("Helvetica-Bold", 7)
        c.drawString(sx + 2*mm, body_y - 6*mm, _subject_name(code)[:22])
        c.setFillColor(C_LIGHT)
        c.setFont("Helvetica", 7)
        c.drawString(sx + 2*mm, body_y - 10*mm, f"Level {rating} → Target: Level {target} ({_level_label(target)})")

    body_y -= 18*mm

    # ── Application checklist ─────────────────────────────────────────────────
    _section_header(c, MARGIN, body_y, "APPLICATION CHECKLIST")
    body_y -= 8*mm

    checklist = [
        ("Research your top 3 universities and their requirements", False),
        ("Register for the National Benchmark Test (NBT) if needed", False),
        ("Apply before September 30 (most university deadline)", False),
        (f"Reach your APS target of {data['target_aps']} by end of Grade 12", False),
        ("Apply for bursaries (NSFAS opens March each year)", False),
        ("Request a school reference letter from your principal", False),
    ]

    left_items   = checklist[:3]
    right_items  = checklist[3:]
    check_col_w  = (w - 2 * MARGIN - 5*mm) / 2

    for row in range(3):
        # Left column
        item_l, _ = left_items[row]
        c.setFillColor(HexColor("#10b98122"))
        c.roundRect(MARGIN, body_y - 7*mm, 4*mm, 4*mm, 1*mm, fill=1, stroke=0)
        c.setFillColor(C_DARK)
        c.setFont("Helvetica", 8)
        c.drawString(MARGIN + 6*mm, body_y - 4*mm, item_l[:52])

        # Right column
        item_r, _ = right_items[row]
        rx = MARGIN + check_col_w + 5*mm
        c.setFillColor(HexColor("#10b98122"))
        c.roundRect(rx, body_y - 7*mm, 4*mm, 4*mm, 1*mm, fill=1, stroke=0)
        c.setFillColor(C_DARK)
        c.setFont("Helvetica", 8)
        c.drawString(rx + 6*mm, body_y - 4*mm, item_r[:52])

        body_y -= 9*mm

    body_y -= 4*mm

    # ── Closing banner ────────────────────────────────────────────────────────
    banner_h = 18*mm
    if body_y - banner_h > 15*mm:
        _rounded_rect(
            c, MARGIN, body_y - banner_h,
            w - 2*MARGIN, banner_h,
            radius=4*mm, fill_color=C_PURPLE,
        )
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(w / 2, body_y - 9*mm, f"You Can Do This, {data['learner_name'].split()[0]}. Your Future Starts Now.")
        c.setFont("Helvetica", 8)
        c.setFillColor(HexColor("#ffffffbb"))
        c.drawCentredString(w / 2, body_y - 14*mm, "InfoTech Career Navigator  ·  Discover Your Future  ·  Free for all South African Learners")

    # ── Footer ────────────────────────────────────────────────────────────────
    c.setFillColor(C_PURPLE)
    c.rect(0, 0, w, 10*mm, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica", 7)
    c.drawCentredString(w / 2, 3*mm, "InfoTech Career Navigator  ·  Discover Your Future  ·  Made for South African Learners")


# ── Roadmap step builder ──────────────────────────────────────────────────────

def _build_roadmap_steps(data: dict) -> list:
    career_title = data["primary_career"]["title"]
    aps          = data["aps_score"]
    target_aps   = data["target_aps"]
    qual         = data.get("qualification", "your qualification")

    steps = [
        (
            "Focus on Your Key Subjects Right Now",
            f"Identify your lowest-performing subjects and get extra help immediately. "
            f"Your target APS is {target_aps} — every level improvement counts.",
        ),
        (
            f"Research {career_title} Requirements",
            f"Visit university websites, attend open days and speak to people working "
            f"in the field. Knowledge of your path reduces fear and builds direction.",
        ),
        (
            "Apply for Bursaries Before Grade 12 Ends",
            "NSFAS, SAICA Thuthuka, Funza Lushaka and many company bursaries open early. "
            "Apply to at least 3 bursaries — financial freedom removes your biggest obstacle.",
        ),
        (
            "Submit University Applications by September",
            "Most South African universities close applications on 30 September. "
            "Apply to your top 3 choices — your first, second and third priority careers.",
        ),
        (
            f"Complete {qual} and Register Professionally",
            "After graduating, register with the relevant professional body in your field. "
            "This unlocks full earning potential and legal right to practise.",
        ),
    ]
    return steps


# ── Main export function ──────────────────────────────────────────────────────

def generate_pdf(session_data: dict) -> bytes:
    """
    Generate the career roadmap PDF and return it as bytes.

    Parameters
    ----------
    session_data : dict
        Must contain keys matching what the app stores in st.session_state.

    Returns
    -------
    bytes — PDF file content ready for st.download_button
    """
    buffer = BytesIO()
    c      = rl_canvas.Canvas(buffer, pagesize=A4)
    c.setTitle(f"Career Roadmap — {session_data['learner_name']}")
    c.setAuthor("InfoTech Career Navigator")
    c.setSubject("Personalised Career Success Manifesto")

    _draw_page1(c, session_data)
    c.showPage()
    _draw_page2(c, session_data)
    c.showPage()
    c.save()

    return buffer.getvalue()