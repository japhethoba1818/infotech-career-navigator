# InfoTech Career Navigator 🧭

A career guidance tool for South African high school learners — calculates APS (Admission Point Score), surfaces matching career paths, and runs a personality-fit assessment. Built to hand off seamlessly into **InfoTech Study Companion** once a learner has their results.

Built with **Streamlit** + **Supabase** (Postgres).

---

## ✨ Features

- **APS calculator** — works out a learner's Admission Point Score from their subjects/marks
- **Career roadmap** — surfaces career paths matching the learner's profile and APS
- **Personality assessment** — styled two-column scenario cards (not plain radio buttons), animated progress bar, live personality-type preview after 4 answers, completion celebration banner
- **Supabase persistence** — every learner's results are saved permanently, not just kept in-session
- **Bridge to Study Companion** — a styled "Continue to Study Companion" card with a redirect button, intended to carry the learner's results forward via a transfer token

---

## 🏗️ Architecture

| Layer | File(s) | Role |
|---|---|---|
| Data access | `db_service.py` | `save_learner_result()`, `create_study_companion_transfer()` — silent exception handling so a DB failure never crashes the app |
| Connection | `supabase_client.py` | Cached Supabase connection singleton (`@st.cache_resource`) |
| Data shaping | `data_loader.py` | Resolves personality-type labels from a JSON lookup |
| Roadmap page | `pages/roadmap.py` | Saves results to Supabase once per session, shows the Study Companion bridge card |
| Personality page | `pages/personality.py` | Scenario-card assessment UI, live preview, completion banner |

### Data store

Supabase (Postgres) tables:

- `learners` — base learner record
- `career_results` — career-path matches per learner
- `personality_results` — personality assessment outcomes per learner
- `study_companion_transfers` — handoff tokens linking a learner record to a Study Companion account

All four tables have indexes and Row Level Security policies enabled.

> **Note on this document:** This README was written from a session summary of the work done, not from a direct read of the current codebase. Some details below (exact file names, function signatures) reflect what was built as of that session — confirm against the live repo before treating this as authoritative, and update this file once verified.

---

## ⚙️ Setup

### 1. Requirements

```bash
pip install -r requirements.txt
```

### 2. Supabase secrets

Create `.streamlit/secrets.toml` (gitignored — never commit):

```toml
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_SERVICE_KEY = "your-service-role-key"
```

Set the same keys under **Settings → Secrets** on Streamlit Community Cloud for the deployed app.

### 3. Run locally

```bash
streamlit run app.py
```

---

## 🔗 Relationship to Study Companion

Career Navigator and Study Companion are **separate Streamlit apps sharing one Supabase project**. A learner completes their APS calculation and personality assessment here, then follows a "Continue to Study Companion" link carrying a transfer token (`study_companion_transfers` table) so their career goal, personality type, and APS score can be linked to their Study Companion account (`cn_career_goal`, `cn_personality_type`, `cn_aps_score` fields already exist on `sc_students` in Study Companion, ready to receive this data).

**Status:** the transfer *token generation and bridge UI* exist; full *activation* of the deep link (auto-populating those fields on arrival) was flagged as a next step, not yet confirmed complete.

---

## 🗺️ Roadmap

- [ ] Activate the token-based deep link end-to-end (confirm `link_career_navigator()` / arrival flow actually populates Study Companion fields)
- [ ] Align career/subject data with CAPS curriculum subject list
- [ ] Push notifications or reminders — ruled impractical without a PWA wrapper; email reminders (Resend/Brevo) recommended instead

---

*Part of the InfoTech Rural ecosystem — bringing digital tools to South African students.*