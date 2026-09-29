# PVA Academy — Computer & Laptop Basics (standalone module) v1.0

Stage 2 of the PVA Beginner VA Journey (Build Your Foundation), first course.
8 lessons + a diagnostic Final Challenge. No login. Progress is saved in the
learner's browser only (`pva-computer-basics-progress`), with Export / Restore / Clear.

Live URL (after Cloudflare connection): `https://pva-computer-basics.probinsiyanongva.workers.dev/`

Built on the VA Foundations standalone module (`pva-va-foundations`): same
`course.css`, same progress architecture, same page chrome and components.
Only the course content differs.

## Structure

- `public/` — the only folder Cloudflare serves (see `wrangler.jsonc`)
  - `index.html` — course home: identity, "Do you need this course?" check, journey position, progress, course map
  - `lesson-1/` … `lesson-8/` — lessons with activities and Quick Checks
  - `final-challenge/` — diagnostic Final Challenge
  - `progress/` — progress list, Export / Restore / Clear
  - `shared/` — `course.css`, `progress.js`, `lesson.js`, `home.js`, `challenge.js`, generated `quick-checks.js` and `challenge-data.js`
- `content/` — lesson bodies (`lesson-N.html`, with `{{activity:ID}}` placeholders) and `course.json` (titles, activities, Quick Checks, next-lesson previews, home page lists)
- `tools/build.py` — builds `public/` from `content/`

## Rebuild

```text
python3 tools/build.py
```

**The Final Challenge answer key is private.** Its source, `tools/source/final-challenge.json`,
is kept out of this public repository (see `.gitignore`), as in VA Foundations. The site stores
each answer only as a hash. Without the private file, the build keeps the already-built
Final Challenge as it is and rebuilds everything else. When uploading through the GitHub
website, do **not** upload the `tools/source/` folder: `.gitignore` does not apply to web uploads.

## Cloudflare deployment

Workers & Pages → Create → Import a repository → `pva-computer-basics`.

```text
Build command: (blank)
Deploy command: npx wrangler deploy
```

Then enable the `workers.dev` route under **Domains** if the dashboard shows "No URLs enabled".

## Rules

- Completion = all 8 lessons marked complete **and** the Final Challenge submitted once.
- The Final Challenge is diagnostic: the score is shown and kept, but never blocks completion.
- Completion is an acknowledgment, not a certification. No portfolio-portal route.
- Mark as done is never gated.
- Scope: the computer itself. Email, Gmail, Google Drive/Docs/Sheets and sharing
  permissions belong to Internet, Email & Google Workspace. Client instructions
  belong to Stage 3. Formulas belong to Spreadsheet Basics.
- Links out: "← PVA Academy" goes to `https://probinsiyanongva.org/` (same tab);
  previous course VA Foundations; next course Internet, Email & Google Workspace.
