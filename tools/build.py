#!/usr/bin/env python3
"""Build the Computer & Laptop Basics standalone module.

Page chrome, progress architecture and components are reused from the
VA Foundations standalone module (pva-va-foundations). Only the course
content differs.

Content sources (this repo):
  content/lesson-N.html   lesson body, written with the shared course.css components
  content/course.json     lesson metadata, Quick Checks, next-lesson previews

A lesson with no content file yet gets a short "being rebuilt" page, so every
link in the course map and lesson pills always resolves.

Output: public/  (the only folder Cloudflare serves; see wrangler.jsonc)
Run:    python3 tools/build.py
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
OUT = ROOT / "public"
VERSION = "1.0"

COURSE = "Computer & Laptop Basics"
ACADEMY_URL = "https://probinsiyanongva.org/"
PREV_COURSE = ("VA Foundations", "https://pva-va-foundations.probinsiyanongva.workers.dev/")
NEXT_COURSE = ("Internet, Email & Google Workspace", "https://probinsiyanongva.org/internet-workspace-basics/")
OPTIONAL = [
    ("Document Basics", "https://pva-document-basics.probinsiyanongva.workers.dev/",
     "Practice creating, formatting and saving simple documents."),
    ("Spreadsheet Basics", "https://pva-spreadsheet-basics.probinsiyanongva.workers.dev/",
     "Practice rows, columns, cells and simple spreadsheet tasks."),
]
FINAL_LABEL = "Final Challenge"
FINAL_SUB = "12 questions · Diagnostic, no pass mark"

esc = lambda s: html.escape(s, quote=True)
DATA = json.loads((CONTENT / "course.json").read_text(encoding="utf-8"))
LESSONS = DATA["lessons"]  # list of {num, title, next_preview}
TOTAL = len(LESSONS)


# ---------------------------------------------------------------- page chrome (from VA Foundations)
def head(title, root, description=""):
    desc = f'\n<meta name="description" content="{esc(description)}">' if description else ""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#1B4332">{desc}
<title>{esc(title)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700&family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{root}shared/course.css">
</head>"""


def chrome_top(root):
    return f"""<a class="skip-link" href="#main-content">Skip to course content</a>
<header class="route-bar"><div class="route-inner"><a class="home-btn" href="{ACADEMY_URL}" aria-label="Back to PVA Academy home page">← PVA Academy</a><div class="route-title"><a href="{root}">{esc(COURSE)}</a></div><div class="route-tag">STAGE 2 · BUILD YOUR FOUNDATION</div></div></header>
<div class="progress-wrap"><div class="progress-inner"><div class="progress-label"><span id="progressText">Getting started</span><span id="progressPct">0%</span></div><div class="progress-track" id="progressTrack"></div></div></div>"""


STORAGE_BANNER = """<div class="storage-banner hidden" id="storageBanner" role="status" aria-live="polite"><strong>Progress can't be saved in this browser.</strong><br><span id="storageBannerText">You can continue learning, but your progress may not remain after you close or refresh this page. If you are using private browsing or have blocked site data, try a normal browser window.</span></div>"""

FOOTER = f'<footer><span class="footer-mark">PVA Academy</span> · Practical. Valuable. Authentic. · {esc(COURSE)} v{VERSION}</footer>'

WARNINGS = """<ul>
<li>Your saved progress may not be available if you switch to another device or browser.</li>
<li>Clearing your browser's site data may remove your saved progress.</li>
<li>Private or incognito browsing may prevent your saved progress from being available later.</li>
<li>You are responsible for keeping a backup. Use <strong>Export Progress</strong> to save a backup file.</li>
</ul>"""

PROGRESS_TOOLS = """<div class="progress-tools"><button class="btn subtle" type="button" id="exportBtn">Export Progress</button><button class="btn subtle" type="button" id="restoreBtn">Restore Progress</button><button class="btn subtle" type="button" id="clearBtn">Clear Progress</button><span class="save-state" data-save-state>Progress is saved in this browser.</span><input id="restoreFile" type="file" accept="application/json,.json" hidden></div>"""

JOURNEY = [
    ("1. EXPLORE", "Understand the VA world", "What VA work is, what it can look like, and where to start.", False),
    ("2. BUILD YOUR FOUNDATION", "Become ready to learn and work", "", True),
    ("3. LEARN TO WORK", "Learn how work is actually done", "Communication, professionalism, instructions, and client work.", False),
    ("4. FIND YOUR DIRECTION", "Choose work worth learning", "Explore skills and possible VA directions.", False),
    ("5. PRACTICE & PROVE", "Build functional skill and evidence", "Practice realistic tasks and create proof of what you can do.", False),
    ("6. ENTER THE MARKET", "Present yourself and begin working", "Prepare your profile, apply for work, and start entering the market.", False),
]


def render_journey():
    items = []
    for name, sub, detail, here in JOURNEY:
        cls = ' class="here"' if here else ""
        tag = '<span class="here-tag">You are here</span>' if here else ""
        det = f'<div class="flow-detail">{esc(detail)}</div>' if detail else ""
        items.append(f'<li{cls}><div class="flow-name">{esc(name)}{tag}</div><div class="flow-sub">{esc(sub)}</div>{det}</li>')
    return '<ol class="flow">' + "".join(items) + "</ol>"


def lesson_rows(prefix):
    rows = "".join(
        f'<li><a class="lesson-row" data-lesson="lesson-{l["num"]}" href="{prefix}lesson-{l["num"]}/"><span class="lesson-num">{l["num"]}</span>'
        f'<span class="row-text"><span class="row-title">{esc(l["title"])}</span><span class="row-sub">Lesson {l["num"]} of {TOTAL}</span></span>'
        f'<span class="stamp" data-stamp>Not started</span></a></li>' for l in LESSONS)
    rows += (f'<li><a class="lesson-row final" data-lesson="final-challenge" href="{prefix}final-challenge/"><span class="lesson-num">✓</span>'
             f'<span class="row-text"><span class="row-title">{FINAL_LABEL}</span><span class="row-sub">{FINAL_SUB}</span></span>'
             '<span class="stamp" data-stamp>Not started</span></a></li>')
    return rows


def journey_pager():
    """Previous / next course in the Beginner VA Journey (links out of this course)."""
    return (f'<nav class="pager" aria-label="Beginner VA Journey">'
            f'<a class="prev" href="{PREV_COURSE[1]}"><span class="pager-dir">← Previous course</span><span class="pager-title">{esc(PREV_COURSE[0])}</span></a>'
            f'<a class="next" href="{NEXT_COURSE[1]}"><span class="pager-dir">Next course →</span><span class="pager-title">{esc(NEXT_COURSE[0])}</span></a></nav>')


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


# ---------------------------------------------------------------- activities from course.json
def render_activity(act_id, act):
    """{{activity:ID}} in a lesson body -> a graded activity (same markup as VA Foundations)."""
    items = []
    for i, it in enumerate(act["items"], 1):
        key = f"act:{act_id}-{i}"
        opts = "".join(f'<label class="choice"><input type="radio" name="{esc(key)}" value="{j}"><span>{o}</span></label>'
                       for j, o in enumerate(it["options"]))
        assert 0 <= it["answer"] < len(it["options"]), (act_id, i)
        items.append(
            f'<div class="act-item act-graded" data-key="{esc(key)}" data-correct="{it["answer"]}" '
            f'data-good="{esc(it["good"])}" data-try="{esc(it.get("try", it["good"]))}">'
            f'<div class="act-q"><span class="q-num">Question {i}</span><br><p>{it["q"]}</p></div>'
            f'<div class="choice-group" role="radiogroup">{opts}</div>'
            f'<div class="feedback" aria-live="polite"></div></div>')
    intro = f'<p>{act["intro"]}</p>' if act.get("intro") else ""
    return (f'<section class="activity"><div class="activity-title">Activity</div><h2>{esc(act["title"])}</h2>{intro}'
            + "".join(items) +
            '<div class="hero-actions" style="margin:4px 0 12px"><button type="button" class="btn subtle small-btn" '
            'data-reset-activity>Reset this activity</button></div></section>')


def fill_activities(content, l):
    for act_id, act in (l.get("activities") or {}).items():
        token = "{{activity:" + act_id + "}}"
        assert token in content, (l["num"], token)
        content = content.replace(token, render_activity(act_id, act))
    assert "{{activity:" not in content, l["num"]
    # keep a key combination (Ctrl + C) on one line
    # (two keys only: longer combinations may wrap on narrow phones)
    return re.sub(r"(<kbd>[^<]*</kbd>\s*\+\s*<kbd>[^<]*</kbd>)(?!\s*\+)", r'<span class="keys">\1</span>', content)


# ---------------------------------------------------------------- lessons
def build_lesson(l):
    num, title = l["num"], l["title"]
    root = "../"
    src = CONTENT / f"lesson-{num}.html"
    built = src.exists()
    if built:
        content = fill_activities(src.read_text(encoding="utf-8").strip(), l)
    else:
        content = ('<div class="callout"><strong>This lesson is being rebuilt.</strong> '
                   'The new version of this lesson is on its way. Lessons that are ready are listed on the '
                   f'<a href="{root}">course home page</a>.</div>')

    prev_link = (f'<a class="prev" href="../lesson-{num - 1}/"><span class="pager-dir">← Previous</span><span class="pager-title">Lesson {num - 1}: {esc(LESSONS[num - 2]["title"])}</span></a>'
                 if num > 1 else f'<a class="prev" href="../"><span class="pager-dir">← Back</span><span class="pager-title">{esc(COURSE)} home</span></a>')
    next_link = (f'<a class="next" href="../lesson-{num + 1}/"><span class="pager-dir">Next →</span><span class="pager-title">Lesson {num + 1}: {esc(LESSONS[num]["title"])}</span></a>'
                 if num < TOTAL else f'<a class="next" href="../final-challenge/"><span class="pager-dir">Next →</span><span class="pager-title">{FINAL_LABEL}</span></a>')

    next_block = ""
    if built and l.get("next_preview"):
        if num < TOTAL:
            heading, href, label = LESSONS[num]["title"], f"../lesson-{num + 1}/", f"Go to Lesson {num + 1} →"
        else:
            heading, href, label = FINAL_LABEL, "../final-challenge/", "Go to the Final Challenge →"
        section = "Next Lesson" if num < TOTAL else "Next Step"
        paras = "".join(f"<p>{p}</p>" for p in l["next_preview"])
        next_block = (f'<section class="card"><div class="connection-title">{section}</div>'
                      f'<h2>{esc(heading)}</h2>{paras}'
                      f'<div class="hero-actions"><a class="btn" href="{href}">{label}</a></div></section>')

    footer = ""
    if built:
        footer = f"""<section class="quick-check" id="quickCheck" aria-label="Quick Check"></section>
<div class="lesson-footer"><span class="next-hint">Finished this lesson? Marking it complete is saved in this browser.</span><div class="footer-actions"><button class="btn" type="button" id="markBtn">Mark Lesson {num} complete</button><button class="btn subtle" type="button" id="notDoneBtn" disabled>Mark as not done</button></div></div>
<div class="tip hidden" id="donePanel" role="status"><strong>Lesson {num} is marked complete.</strong> <span class="small">It's saved in this browser.</span><div class="hero-actions" style="margin-top:10px"><button class="btn secondary small-btn" type="button" id="notesBtn">Download my Lesson {num} notes (.txt)</button></div></div>"""

    scripts = (f'<script src="{root}shared/progress.js"></script>\n<script src="{root}shared/quick-checks.js"></script>\n'
               f'<script src="{root}shared/lesson.js"></script>') if built else \
              (f'<script src="{root}shared/progress.js"></script>\n'
               f'<script>PVACB.renderProgressBar("lesson-{num}");PVACB.renderLessonNav("lesson-{num}","{root}");</script>')

    page = f"""{head(f"Lesson {num}: {title} — {COURSE} | PVA Academy", root)}
<body data-lesson-id="lesson-{num}" data-root="{root}">
{chrome_top(root)}
<main id="main-content">
{STORAGE_BANNER}
<nav class="lesson-nav" id="lessonNav" aria-label="Course lessons"></nav>
<article class="card lesson" id="lessonCard">
<div class="lesson-head"><div class="lesson-num">{num}</div><div class="lesson-title-wrap"><div class="section-label">Lesson {num} of {TOTAL}</div><h1>{esc(title)}</h1><span class="done-stamp">✓ Completed</span></div></div>
<div class="lesson-body">
{content}
</div>
{footer}
</article>
{next_block}
<nav class="pager" aria-label="Lesson navigation">{prev_link}{next_link}</nav>
{FOOTER}
</main>
{scripts}
</body>
</html>
"""
    write(OUT / f"lesson-{num}" / "index.html", page)
    return built


def build_quick_checks():
    qc = {f'lesson-{l["num"]}': l["quick_check"] for l in LESSONS if l.get("quick_check")}
    for k, v in qc.items():
        for q in v["questions"]:
            assert 0 <= q["answer"] < len(q["options"]) and len(q["options"]) >= 3, (k, q["id"])
    write(OUT / "shared" / "quick-checks.js",
          "/* Quick Checks — Computer & Laptop Basics. Not pass/fail. Built from content/course.json. */\n"
          "window.CB_QUICK_CHECKS = " + json.dumps(qc, ensure_ascii=False, indent=1) + ";\n")
    return sum(len(v["questions"]) for v in qc.values())


# ---------------------------------------------------------------- final challenge
FINAL_SRC = ROOT / "tools" / "source" / "final-challenge.json"  # private: holds the answer key
SALT = "pva-cb-2026"


def fnv(s: str) -> str:
    h = 2166136261
    for ch in s.encode("utf-8"):
        h ^= ch
        h = (h * 16777619) & 0xFFFFFFFF
    return format(h, "08x")


def build_final():
    """Final Challenge page + hashed question data.

    The source (with answers) is private and kept out of the public repo, like
    VA Foundations. Without it, the already-built public files are left as they are."""
    data_js = OUT / "shared" / "challenge-data.js"
    if not FINAL_SRC.exists():
        if data_js.exists():
            return "kept existing (private source not present)"
        raise SystemExit("Missing tools/source/final-challenge.json and no built challenge-data.js to keep.")
    src = json.loads(FINAL_SRC.read_text(encoding="utf-8"))
    qs = []
    for n, q in enumerate(src["questions"], 1):
        assert 0 <= q["answer"] < len(q["options"]) == 4, n
        qs.append({"n": n, "html": q["q"], "options": [esc(o) for o in q["options"]],
                   "k": fnv(f"{SALT}|{n}|{q['answer']}"), "review": q["review"]})
    assert len(qs) == 12
    write(data_js, "/* Final Challenge questions. Answers are hashed, not stored as letters. */\n"
          "window.CB_CHALLENGE = " + json.dumps(qs, ensure_ascii=False, indent=1) + ";\nwindow.CB_SALT = " + json.dumps(SALT) + ";\n")

    root = "../"
    page = f"""{head(f"{FINAL_LABEL} — {COURSE} | PVA Academy", root)}
<body data-root="{root}" data-next-course="{NEXT_COURSE[1]}">
{chrome_top(root)}
<main id="main-content">
{STORAGE_BANNER}
<nav class="lesson-nav" id="lessonNav" aria-label="Course lessons"></nav>
<section class="card" id="assessIntro">
<div class="section-label">{FINAL_LABEL}</div><div class="folder-tab">12 questions · Multiple choice</div>
<h1 style="font:700 clamp(1.7rem,4vw,2.3rem)/1.15 Fraunces,Georgia,serif;color:var(--green);margin:0 0 10px">{esc(COURSE)} — {FINAL_LABEL}</h1>
<p>Twelve short situations, each asking what you would do on the computer. They cover all 8 lessons.</p>
<div class="key-idea"><strong>How it works</strong><ul style="margin:.4em 0 0">
<li>One question at a time. Your answers are saved in this browser as you go.</li>
<li><strong>There is no pass mark.</strong> This challenge is diagnostic: your score shows what's solid and which lessons are worth another look.</li>
<li>After you submit, you'll see your score and a link to the lesson behind any answer that didn't match. You can take it again as many times as you like.</li>
<li>{esc(COURSE)} is complete when all 8 lessons are marked complete and you've submitted this challenge once.</li>
</ul></div>
<div id="gate" class="callout hidden"></div>
<div class="hero-actions"><button class="btn" type="button" id="startBtn">Start the challenge</button></div>
</section>
<section class="card hidden" id="assessRunner" aria-live="polite"></section>
<section class="card hidden" id="assessResult"></section>
<section class="completion hidden" id="completion"></section>
{FOOTER}
</main>
<script src="{root}shared/progress.js"></script>
<script src="{root}shared/challenge-data.js"></script>
<script src="{root}shared/challenge.js"></script>
</body>
</html>
"""
    write(OUT / "final-challenge" / "index.html", page)
    return "built"


# ---------------------------------------------------------------- home
def build_home():
    root = "./"
    fit_rows = "".join(
        f'<div class="act-item fit-row" data-key="fit-{i}" data-lesson="{f["lesson"]}"><p class="act-q">{esc(f["text"])}</p>'
        f'<div class="choice-row" role="radiogroup" aria-label="{esc(f["text"])}">'
        f'<label class="choice"><input type="radio" name="fit-{i}" value="Yes"><span>Yes, I can</span></label>'
        f'<label class="choice"><input type="radio" name="fit-{i}" value="Not yet"><span>Not yet</span></label></div></div>'
        for i, f in enumerate(DATA["fit_check"], 1))
    outcomes = "".join(f"<li>{esc(o)}</li>" for o in DATA["outcomes"])
    optional = "".join(f'<li><a href="{u}">{esc(n)}</a>: {esc(d)}</li>' for n, u, d in OPTIONAL)

    page = f"""{head(f"{COURSE} — PVA Academy", root, "A free, self-paced PVA Academy course for aspiring VAs: use a computer confidently for everyday work, and know what to do when something goes wrong.")}
<body data-root="{root}" data-page="home" data-next-course="{NEXT_COURSE[1]}">
{chrome_top(root)}
<main id="main-content">
<section class="course-header" id="top"><div class="eyebrow">PVA Academy · Beginner VA Journey · Stage 2: Build Your Foundation</div><h1>{esc(COURSE)}</h1><p>The everyday computer skills VA work depends on: using your mouse, keyboard and windows, handling files and folders, downloading and uploading, using a browser, and knowing what to do when something goes wrong.</p><div class="meta-row"><span class="meta-chip">Free</span><span class="meta-chip">Self-Paced</span><span class="meta-chip">No Login</span><span class="meta-chip">8 Lessons + Final Challenge</span></div></section>
{STORAGE_BANNER}
<div class="before-start" aria-labelledby="before-start-title"><h2 id="before-start-title">Before You Start</h2><p><strong>No login is required.</strong> You can start learning right away.</p><p>Your course progress is saved on the device and browser you are using right now. Nothing is sent to an account or a server.</p><p>For the best experience, keep using the <strong>same device and browser</strong> while you take this course.</p><p><strong>Important:</strong></p>{WARNINGS}<p class="small" style="margin-bottom:0">Your earlier Computer &amp; Laptop Basics progress on the PVA Academy site is not carried over. This version of the course starts fresh.</p></div>

<section class="card" aria-labelledby="progress-h">
<div class="section-label">Your progress</div>
<h2 id="progress-h" style="margin-bottom:6px">Where you are</h2>
<div class="progress-summary"><span class="big-pct" id="homePct">0%</span><span id="homeSummary">0 of {TOTAL} lessons complete · Final Challenge not done yet</span></div>
<div class="hero-actions"><a class="btn" id="continueBtn" href="lesson-1/">Start Lesson 1</a><a class="btn secondary" href="progress/">Progress &amp; backup</a></div>
{PROGRESS_TOOLS}
</section>

<section class="completion hidden" id="completion"></section>

<section class="card" aria-labelledby="about-h">
<div class="section-label">About this course</div>
<h2 id="about-h">Using a computer for VA work</h2>
<p>Almost every VA task happens on a computer. Before you can learn email, Google Workspace, or any specialized VA skill, you need to be comfortable with the computer itself.</p>
<p><strong>This course is for you if</strong> you are new to computers, you mostly use a phone, or you use a computer but often get stuck with files, downloads, or problems you don't know how to fix.</p>
<p>It works for both Windows laptops and Macs, and for desktop computers too. Where the steps differ, the lessons show both.</p>
<p>By the end of this course, you should be able to:</p>
<ul>{outcomes}</ul>
<p>This course teaches the computer itself. Email, Google Drive, Docs, Sheets and sharing files with other people are covered in the next course, <strong>{esc(NEXT_COURSE[0])}</strong>.</p>
</section>

<section class="card" aria-labelledby="fit-h" id="fitCheck">
<div class="section-label">Check your starting point</div>
<h2 id="fit-h">Do you need this course?</h2>
<p>Answer honestly. There is no score, and nobody else sees your answers. They are saved in this browser.</p>
{fit_rows}
<div class="feedback" id="fitResult" aria-live="polite"></div>
<div class="hero-actions" style="margin-top:12px"><button class="btn subtle small-btn" type="button" id="fitReset">Clear my answers</button></div>
</section>

<section class="card" aria-labelledby="journey-h">
<div class="section-label">The PVA Beginner VA Journey</div>
<h2 id="journey-h">You are in Stage 2: Build Your Foundation</h2>
<p>Stage 2 makes you ready to learn and work online. It has two courses, taken in this order:</p>
<ol><li><strong>{esc(COURSE)}</strong> (this course): the computer itself.</li><li><a href="{NEXT_COURSE[1]}">{esc(NEXT_COURSE[0])}</a>: working online with email and Google tools.</li></ol>
<p>You don't need to finish <a href="{PREV_COURSE[1]}">{esc(PREV_COURSE[0])}</a> first, but it gives you the bigger picture of VA work if you are completely new.</p>
{render_journey()}
<div class="tip"><div class="section-label">Optional practice</div><p style="margin-top:0">These separate PVA modules are useful alongside this stage. They are not part of this course:</p><ul style="margin-bottom:0">{optional}</ul></div>
</section>

<section class="card" aria-labelledby="map-h">
<div class="section-label">Course map</div><div class="folder-tab">8 lessons + Final Challenge</div>
<h2 id="map-h">Lessons</h2>
<ul class="lesson-list" id="lessonList">{lesson_rows("")}</ul>
</section>
{journey_pager()}
{FOOTER}
</main>
<script src="{root}shared/progress.js"></script>
<script src="{root}shared/home.js"></script>
</body>
</html>
"""
    write(OUT / "index.html", page)


def build_progress_page():
    root = "../"
    page = f"""{head(f"Progress & Backup — {COURSE} | PVA Academy", root)}
<body data-root="{root}" data-page="progress" data-next-course="{NEXT_COURSE[1]}">
{chrome_top(root)}
<main id="main-content">
{STORAGE_BANNER}
<nav class="lesson-nav" id="lessonNav" aria-label="Course lessons"></nav>
<section class="card">
<div class="section-label">Progress &amp; backup</div>
<h1 style="font:700 clamp(1.7rem,4vw,2.3rem)/1.15 Fraunces,Georgia,serif;color:var(--green);margin:0 0 10px">Your {esc(COURSE)} progress</h1>
<div class="progress-summary"><span class="big-pct" id="homePct">0%</span><span id="homeSummary">0 of {TOTAL} lessons complete</span></div>
<p>Your progress is saved only in this browser, on this device. Nothing is sent to an account or a server.</p>
{WARNINGS}
{PROGRESS_TOOLS}
<p class="small"><strong>Export Progress</strong> downloads a backup file. <strong>Restore Progress</strong> loads a {esc(COURSE)} backup and <em>replaces</em> what is saved in this browser. Backups from other PVA courses can't be restored here. <strong>Clear Progress</strong> removes only {esc(COURSE)} progress.</p>
</section>
<section class="card"><div class="section-label">Course map</div><h2>Lessons</h2><ul class="lesson-list" id="lessonList">{lesson_rows("../")}</ul></section>
{FOOTER}
</main>
<script src="{root}shared/progress.js"></script>
<script src="{root}shared/home.js"></script>
</body>
</html>
"""
    write(OUT / "progress" / "index.html", page)


def main():
    assert TOTAL == 8
    built = [build_lesson(l) for l in LESSONS]
    n_qc = build_quick_checks()
    final = build_final()
    build_home()
    build_progress_page()
    print(f"lessons built: {sum(built)} of {TOTAL} | quick check questions: {n_qc} | final challenge: {final}")


if __name__ == "__main__":
    main()
