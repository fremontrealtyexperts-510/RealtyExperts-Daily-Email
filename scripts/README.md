# Sync Infrastructure Scripts

Files in this folder set up the bidirectional Mac and VPS sync. See
`docs/plans/2026-05-03-mac-vps-sync-design.md` for the full architecture.

## Files

| File | Lives on | Purpose |
|---|---|---|
| `git-sync-pull.sh` | VPS, runs from cron | Periodic `git pull --rebase --autostash` from origin/main |
| `mac-launchd/run-pull.sh` + `com.harvbalu.realty-email-pull.plist` | Mac, launchd every 15 min | Runs `pull-from-github.sh` (repo root) from a local clone; copies only files GitHub changed into the Drive workspace |
| `mac-launchd/run-refresh.sh` + `com.harvbalu.live-inventory-refresh.plist` | Mac, launchd 9:00 / 11:00 / 15:00 PT | Runs `refresh-live-inventory.sh` from a local clone |
| `mac-launchd/run-backstop.sh` + `com.harvbalu.realty-broadcast-backstop.plist` | Mac, launchd 10:30 / 13:30 PT | Runs `broadcast-backstop.js` (gitignored, copied from Drive) from a local clone |

### Why the Mac jobs go through wrappers (2026-09-13)

launchd must not run code off the Google Drive mount. Under launchd the Drive File
Provider fails reads and writes with EDEADLK (bash exit 126 "Resource deadlock
avoided", Node "Unknown system error -11"), and all three jobs had been failing
silently: the pull since 2026-08-12. Each wrapper lives in its own folder under
`~/Library/Application Support/`, keeps a local clone of this repo reset to
origin/main every run, copies only the gitignored files it needs from Drive (keeping
the last good copies if Drive is unreadable), and runs the job from the clone. The
wrappers read nothing secret from this repo: the gh token is fetched at run time and
sent as a header, never written into a URL or `.git/config`.

## Fresh-machine setup

### VPS (n8n) one-time setup

```bash
# 1. Generate ed25519 deploy key (one-time, no passphrase)
ssh-keygen -t ed25519 -C "harvey-n8n@n8n-vps:RealtyExperts-Daily-Email-deploy" \
  -f ~/.ssh/realty_email_deploy -N ""

# 2. Add the public key to the GitHub repo Deploy Keys (write access enabled):
#    https://github.com/fremontrealtyexperts-510/RealtyExperts-Daily-Email/settings/keys/new
cat ~/.ssh/realty_email_deploy.pub

# 3. Add SSH config alias so the deploy key is used for git over ssh
cat >> ~/.ssh/config <<SSHEOF

# Deploy key for fremontrealtyexperts-510/RealtyExperts-Daily-Email
Host github-realty-email
  HostName github.com
  User git
  IdentityFile ~/.ssh/realty_email_deploy
  IdentitiesOnly yes
SSHEOF

# 4. Clone the repo using the deploy-key alias
git clone git@github-realty-email:fremontrealtyexperts-510/RealtyExperts-Daily-Email.git \
  ~/workspaces/RealtyExperts-Daily-Email
cd ~/workspaces/RealtyExperts-Daily-Email

# 5. Set git config for commit-author consistency
git config user.name "User8888-Level3"
git config user.email "fremontrealtyexperts510@gmail.com"

# 6. npm install
npm install

# 7. Install the periodic-pull cron entry (idempotent)
SCRIPT="$HOME/workspaces/RealtyExperts-Daily-Email/scripts/git-sync-pull.sh"
chmod +x "$SCRIPT"
( crontab -l 2>/dev/null | grep -v "git-sync-pull.sh" ; \
  echo "*/15 * * * * /bin/bash $SCRIPT" ) | crontab -

# 8. Verify
crontab -l | grep git-sync-pull
systemctl is-active cron

# 9. Drop in secrets manually (NOT in git): .env, harvrealtor-*.json, .credentials.enc
#    Get them from KeePassXC or scp from another working install.
```

### Mac one-time setup

```bash
# 1. Have GitHub CLI auth for the fremontrealtyexperts-510 user
gh auth login -u fremontrealtyexperts-510

# 2. The workspace lives in Google Drive (the wrappers expect this exact path):
#    ~/Library/CloudStorage/GoogleDrive-harvinder.balu@gmail.com/My Drive/ClaudeCode/RealtyExperts-Daily-Email
#    Drop in secrets manually (NOT in git): .env, harvrealtor-*.json, .credentials.enc,
#    and broadcast-backstop.js (gitignored).
WS="$HOME/Library/CloudStorage/GoogleDrive-harvinder.balu@gmail.com/My Drive/ClaudeCode/RealtyExperts-Daily-Email"

# 3. Install the three wrappers OFF Drive, one folder each (plists hardcode
#    /Users/harvinderbalu1; edit them if your username differs)
AS="$HOME/Library/Application Support"
install -d "$AS/harvbalu-realty-email-pull" "$AS/harvbalu-live-inventory" "$AS/harvbalu-broadcast-backstop"
install -m 755 "$WS/scripts/mac-launchd/run-pull.sh"     "$AS/harvbalu-realty-email-pull/"
install -m 755 "$WS/scripts/mac-launchd/run-refresh.sh"  "$AS/harvbalu-live-inventory/"
install -m 755 "$WS/scripts/mac-launchd/run-backstop.sh" "$AS/harvbalu-broadcast-backstop/"

# 4. Optional, avoids a full compare on the pull job's first pass: seed its SHA cache
cp "$WS/.git-pull-last-sha" "$AS/harvbalu-realty-email-pull/" 2>/dev/null || true

# 5. Install and load the plists
for J in realty-email-pull live-inventory-refresh realty-broadcast-backstop; do
  cp "$WS/scripts/mac-launchd/com.harvbalu.$J.plist" "$HOME/Library/LaunchAgents/"
  launchctl bootout "gui/$(id -u)/com.harvbalu.$J" 2>/dev/null || true
  launchctl bootstrap "gui/$(id -u)" "$HOME/Library/LaunchAgents/com.harvbalu.$J.plist"
done

# 6. Verify: run each once and expect "last exit code = 0"
for J in realty-email-pull live-inventory-refresh realty-broadcast-backstop; do
  launchctl kickstart -k "gui/$(id -u)/com.harvbalu.$J"
done
sleep 90
for J in realty-email-pull live-inventory-refresh realty-broadcast-backstop; do
  printf '%s: ' "$J"; launchctl print "gui/$(id -u)/com.harvbalu.$J" | grep "last exit"
done
```

The live copies of the wrappers are the ones in `~/Library/Application Support/`.
If you change one, copy it back into `scripts/mac-launchd/` and commit, so a rebuilt
Mac gets the same version.

## Removing the auto-sync

- VPS: `crontab -e`, delete the `git-sync-pull.sh` line
- Mac: `launchctl bootout gui/$(id -u)/com.harvbalu.realty-email-pull`

## Logs

- VPS: `~/workspaces/RealtyExperts-Daily-Email/.git-sync.log` (only writes on changes/errors)
- Mac: `~/Library/Logs/com.harvbalu.<job>.{out,err}.log`; the pull job's own
  `.git-pull.log` and SHA cache are in `~/Library/Application Support/harvbalu-realty-email-pull/`
  (the workspace copies are for manual runs only)
