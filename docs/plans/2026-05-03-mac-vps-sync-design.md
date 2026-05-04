# Mac and VPS Sync Design — RealtyExperts-Daily-Email

**Date:** 2026-05-03
**Status:** Implemented (asymmetric architecture, Option A from brainstorm)
**Goal:** Run the daily-email workflow on either Mac or VPS interchangeably; sync within 15 min of either side completing work.

## Architecture (asymmetric — by design)

The Mac copy lives in `OneDrive/.../RealtyExperts-Daily-Email/` which has a known issue: OneDrive cloud sync corrupts in-place git operations on the .git directory ("broken HEAD every time" per the original push-to-github.sh comment). The Mac side therefore uses a /tmp clone workaround. The VPS side has no such constraint and uses normal git.

```
                                                     GitHub: fremontrealtyexperts-510/RealtyExperts-Daily-Email
                                                                         |
            +-------------------------+         git push (via /tmp)      |          git pull --rebase (auto, every 15min)
            |  Mac OneDrive workspace |  ------------------------------> |  <----------------------------------+
            |  HEAD frozen forever    |                                  |                                     |
            |  /tmp/daily-email-push  |  <--- git pull (NEVER, would     |   git push (via deploy key)         |
            |  is the real git path   |        corrupt OneDrive .git)    |                                     |
            +-------------------------+                                  |          +--------------------------|----+
                                                                         |          |  VPS workspace            |
                                                                         +--------> |  ~/workspaces/...         |
                                                                                    |  HEAD tracks origin/main  |
                                                                                    |  Direct git operations    |
                                                                                    +---------------------------+
```

## Mac side — push-to-github.sh (existing, unchanged)

`push-to-github.sh` in the workspace root is the canonical push mechanism for Mac. It:
1. Clones a fresh copy of the repo from GitHub to `/tmp/daily-email-push/`
2. Sets git config: `user.name=User8888-Level3`, `user.email=fremontrealtyexperts510@gmail.com`
3. Copies generated outputs (today daily PNGs, HTMLs, JSON template) from the OneDrive workspace into /tmp clone
4. Commits with `Co-Authored-By: Claude Opus 4.6 (1M context)` footer
5. Pushes to origin
6. Deletes /tmp clone

The Mac OneDrive copy of `.git` HEAD stays frozen forever — that is intentional. `git status` and `git log` on Mac show stale info; do not rely on them. The on-disk file content is what matters.

**Mac never runs `git pull` against the OneDrive copy** — that would corrupt OneDrive .git and break `push-to-github.sh`.

## VPS side — normal git workflow

VPS workspace at `/home/harvey-n8n/workspaces/RealtyExperts-Daily-Email/`. No OneDrive layer, normal git works fine.

**Auth:** ed25519 deploy key at `~/.ssh/realty_email_deploy`, registered in GitHub repo Deploy Keys with write access. SSH config alias `Host github-realty-email` routes to github.com via this key. Remote URL is `git@github-realty-email:fremontrealtyexperts-510/RealtyExperts-Daily-Email.git`.

**Git config:** `user.name=User8888-Level3`, `user.email=fremontrealtyexperts510@gmail.com` (matches Mac for commit consistency).

**Periodic auto-pull:** cron entry `*/15 * * * * /bin/bash ~/workspaces/RealtyExperts-Daily-Email/scripts/git-sync-pull.sh`. Script does fetch + rebase + autostash; logs only on changes or errors to `.git-sync.log` in the workspace.

**Daily workflow on VPS:** standard sequence — edit, generate, `git add -A`, `git commit -m "..."`, `git push origin main`. No /tmp dance needed.

## What is synced where

| File | Mac | VPS | Synced via |
|---|---|---|---|
| All tracked source + generated files (.js, .html, .png, .json) | yes | yes | git via push-to-github.sh (Mac) / direct git (VPS); auto-pull on VPS |
| .env | yes | yes | manual scp when changed (rare) |
| harvrealtor-*.json (2 service accounts) | yes | yes | manual scp when changed (rare) |
| .credentials.enc | yes | yes | manual scp when changed (rare) |
| node_modules/ | yes | yes | independent (npm install per side) |
| .claude/ | yes | yes | independent (per-machine session state) |
| CLAUDE.md, DAILY-INTAKE.md, README.md | yes | yes | gitignored, currently independent |

## Sync flow

**Workflow on Mac:**
1. Edit files in OneDrive workspace
2. `node generate-daily-email.js daily-market-template.json`
3. `./push-to-github.sh` (auto-pushes via /tmp clone)
4. VPS auto-pulls within 15 min via cron

**Workflow on VPS:**
1. Attach to `claud-realty-email` tmux session (`claude-realty-email` Mac alias)
2. Work in workspace, generate as needed
3. `git add -A && git commit -m "Daily email - MM/DD/YY: ..."` then `git push origin main`
4. Mac OneDrive HEAD does NOT update (by design); on-disk files do not auto-update either, so Mac side is "out of date" until next workflow there OR a manual rsync from VPS to Mac

## Known limitations of Option A

1. **Mac OneDrive workspace is read-mostly for code edits.** Editing source code on Mac requires running push-to-github.sh manually with the JS files included (script currently only copies output files; would need extension if Mac becomes a source-code editing surface again).
2. **Mac never auto-pulls.** If you generate on VPS, the Mac OneDrive copy will not see the new outputs unless you manually rsync from VPS, or run push-to-github.sh from Mac which would re-push the OLDER Mac files and overwrite VPS content.
3. **Conflict mitigation:** Harv stated workflow is one device per day. Cross-device conflict requires both sides to push the same minute, very unlikely. If it happens, rebase-on-push-fail handles it.

## Rollback

- Stop VPS auto-pull: edit VPS crontab and remove the git-sync-pull line
- Remove deploy key: delete from GitHub repo Settings/Deploy keys + remove `~/.ssh/realty_email_deploy*` on VPS
- Workspace itself remains intact
- Mac is unaffected by anything we did (no Mac-side changes were made)
