# Session State — RealtyExperts-Daily-Email

> 🚀 **NEXT SESSION PICKUP — read this first**
>
> **Where things stand (2026-05-03):** Bidirectional Mac ↔ VPS sync is fully shipped and verified end-to-end. Workspace is now usable on both sides:
> - Mac copy: `~/Library/CloudStorage/OneDrive-Personal/ClaudeCode/RealtyExperts-Daily-Email/`
> - VPS copy: `/home/harvey-n8n/workspaces/RealtyExperts-Daily-Email/` — attach via `claude-realty-email` Mac alias
>
> **Tomorrow's first real run is the validation event** — Harv plans to run the daily email workflow on VPS for the first time. If anything breaks, see "Where to find docs" below + the troubleshooting section in the OneNote page.

## What shipped this session (2026-05-03)

1. **VPS workspace** — rsync'd from Mac OneDrive, `npm install`'d, syntax-checked. Sensitive files (.env, both `harvrealtor-*.json`, `.credentials.enc` in `archived/`) transferred manually.
2. **VPS git auth** — ed25519 deploy key at `~/.ssh/realty_email_deploy` registered in GitHub repo Deploy Keys (write access). SSH config alias `Host github-realty-email`. Remote URL switched to SSH form. Direct `git push` from VPS works.
3. **VPS git config** — `User8888-Level3 / fremontrealtyexperts510@gmail.com` (matches Mac's push-to-github.sh for commit-author consistency).
4. **VPS auto-pull cron** — `*/15 * * * *` running `scripts/git-sync-pull.sh`. Logs to `.git-sync.log` only on changes/errors.
5. **Mac auto-pull launchd** — `~/Library/LaunchAgents/com.harvbalu.realty-email-pull.plist` running `pull-from-github.sh` every 900s. Logs to `~/Library/Logs/com.harvbalu.realty-email-pull.{out,err}.log` + workspace `.git-pull.log`.
6. **New tmux session** `claud-realty-email` on VPS in this workspace. Mac alias `claude-realty-email` in `~/.bashrc` + `~/.bash_profile`.
7. **Repo additions** — `pull-from-github.sh`, `scripts/git-sync-pull.sh`, `scripts/com.harvbalu.realty-email-pull.plist`, `scripts/README.md` (fresh-machine setup), `docs/plans/2026-05-03-mac-vps-sync-design.md`.
8. **CLAUDE.md updated** — describes Outlook-source workflow + Mac vs VPS execution differences. Synced via scp to both Mac and VPS (gitignored, so doesn't auto-sync).
9. **OneNote page** — Realty Experts notebook → Daily Reports section → "RealtyExperts Daily Email — Mac+VPS Sync & Workflow (2026-05-03)". Top has highlighted "HOW TO INITIATE THE WORKFLOW" callout.

## Where to find docs

- **OneNote (user-facing instructions):** Realty Experts → Daily Reports → "RealtyExperts Daily Email — Mac+VPS Sync & Workflow (2026-05-03)". Read top first.
- **Architecture rationale:** `docs/plans/2026-05-03-mac-vps-sync-design.md` (in repo).
- **Fresh-machine setup procedure:** `scripts/README.md` (in repo).
- **Workflow guide for Claude:** `CLAUDE.md` (gitignored, present on both Mac + VPS).
- **Daily checklist for Harv:** `DAILY-INTAKE.md` (mostly outdated re: tokens — `ensure-token.js` now auto-manages — but the structured-data template is still valid as a fallback input mode).
- **Memory pointer:** `~/.claude/projects/.../memory/claude-code-on-n8n-vps.md` "Workspace inventory on VPS" section has the full sync details.

## Tomorrow's expected workflow (first real run on VPS)

1. From Mac terminal: `claude-realty-email` (attaches to VPS Claude Code session)
2. Tell Claude: *"Run today's daily email. Source the data from my Outlook email from [sender or subject]."*
3. Claude reads via MS365 MCP → writes JSON → runs `node ensure-token.js`, `node fetch-images.js`, `node run-daily.js` (3 stages, asks Y/n between)
4. Open the generated `daily-market-glance-MMDDYY.html`, copy/paste into a fresh Outlook email, send
5. Mac auto-pulls within 15 min via launchd

## Open / deferred

- **Outlook email identity** — Harv hasn't yet specified the sender/subject pattern of the source email. CLAUDE.md says "Harv will name the sender or subject pattern; otherwise check his inbox for the most recent email matching `market` / `daily` / `At a Glance` / a vendor newsletter sender." Pin this down on first run.
- **Outlook-draft creation** — currently Harv copy/pastes HTML manually. Could automate via MS365 MCP `create-draft-email`. Documented as "future enhancement" in CLAUDE.md.
- **VPS untracked files** — 29 files on VPS that exist on Mac WIP but never made it to origin (alameda-interactive-*.html, build-json.py, archived/, daily-market-glance-*-stripped.html). Don't affect sync; sit as untracked. Cleanup is optional, not urgent.
- **15-min cadence too aggressive?** — May be over-engineered for a once-a-day workflow. Worth checking after 1-2 weeks of real use whether to dial back.

## What was NOT shipped this session (mentioned but deferred)

- Phase 5b (PDF/docx text extraction) for journal — Harv didn't ask
- Phase 6 (journal Q&A retrieval) — Harv didn't ask
- secrets-sync.sh helper for the 4 gitignored secret files — minor utility, could add when first secret rotates
- Voice-purge timer verification (~2026-05-28) for journal — could /schedule a reminder

## Live state to know about

- **Mac launchd** loaded but hasn't fired yet at write time (next fire on 15-min boundary). Verify via `tail ~/Library/Logs/com.harvbalu.realty-email-pull.out.log`.
- **VPS cron** installed but hasn't fired yet at write time. Verify via `ssh n8n 'tail ~/workspaces/RealtyExperts-Daily-Email/.git-sync.log'`.
- **Git history note:** two cosmetic commits in origin from a mistake I made (`1a9abd9` — bad gitignore commit, `661c744` — its revert). Net-zero, just visible in `git log`. Lessons captured in `~/.claude/projects/.../memory/feedback-verify-diff-direction.md`.
- **SSH master state:** warm at session end. Sliding 1h ControlPersist on `Host n8n`. Cold by next session — first VPS op needs a fresh TOTP from `n8n-vps` Authenticator entry.

## Three feedback memories added this session (relevant to future work)

- `feedback-read-workspace-files-first.md` — re-read workspace docs in the current turn, don't reconstruct from memory.
- `feedback-verify-diff-direction.md` — git diff direction is easy to read backwards under pressure; verify content before destructive commits.
- `feedback-prestage-totp-gated-workflows.md` (updated) — added sub-rule about pre-warming SSH master at session start when VPS work is obviously coming.

## Resume protocol

1. Read this file.
2. If user says "run the daily email" or similar → check OneNote page (Realty Experts > Daily Reports) for the user-facing flow, then follow CLAUDE.md.
3. If user reports sync broken → check the troubleshooting section of the OneNote page (9 common scenarios documented).
4. If user wants to extend the sync (e.g., add Outlook draft automation) → see "Future enhancement" section in CLAUDE.md + the design doc.
5. Don't re-architect. The asymmetric Mac/VPS design is intentional and documented; respect it.
