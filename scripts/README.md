# Sync Infrastructure Scripts

Files in this folder set up the bidirectional Mac and VPS sync. See
`docs/plans/2026-05-03-mac-vps-sync-design.md` for the full architecture.

## Files

| File | Lives on | Purpose |
|---|---|---|
| `git-sync-pull.sh` | VPS, runs from cron | Periodic `git pull --rebase --autostash` from origin/main |
| `com.harvbalu.realty-email-pull.plist` | Mac, runs via launchd | Periodic `pull-from-github.sh` (which lives in repo root) |

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

# 2. Clone repo (ANY path; default is OneDrive but it works elsewhere too)
git clone https://github.com/fremontrealtyexperts-510/RealtyExperts-Daily-Email.git \
  "$HOME/Library/CloudStorage/OneDrive-Personal/ClaudeCode/RealtyExperts-Daily-Email"
cd "$HOME/Library/CloudStorage/OneDrive-Personal/ClaudeCode/RealtyExperts-Daily-Email"

# 3. npm install
npm install

# 4. Install the launchd plist (path-corrected — edit if your username differs)
PLIST_SRC="scripts/com.harvbalu.realty-email-pull.plist"
PLIST_DST="$HOME/Library/LaunchAgents/com.harvbalu.realty-email-pull.plist"
cp "$PLIST_SRC" "$PLIST_DST"
launchctl unload "$PLIST_DST" 2>/dev/null || true
launchctl load "$PLIST_DST"

# 5. Verify
launchctl list | grep realty-email-pull

# 6. Drop in secrets manually (NOT in git): .env, harvrealtor-*.json, .credentials.enc
```

## Removing the auto-sync

- VPS: `crontab -e`, delete the `git-sync-pull.sh` line
- Mac: `launchctl unload ~/Library/LaunchAgents/com.harvbalu.realty-email-pull.plist`

## Logs

- VPS: `~/workspaces/RealtyExperts-Daily-Email/.git-sync.log` (only writes on changes/errors)
- Mac: `~/Library/Logs/com.harvbalu.realty-email-pull.{out,err}.log` + workspace `.git-pull.log`
