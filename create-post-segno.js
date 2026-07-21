#!/usr/bin/env node
// Decoupled Agent Hub creator: same as create-post.js but WITHOUT require('qrcode')
// (which stalls on the Drive node_modules). QR is rendered via python segno.
const fs = require('fs');
const { execFileSync } = require('child_process');
const { TEMPLATE_PATH } = require('./lib/config');
const { readAdminToken } = require('./lib/tokens');
const { notesApiPost } = require('./lib/api');
const { buildPost } = require('./templates/agent-hub-post');

async function main() {
  const data = JSON.parse(fs.readFileSync(TEMPLATE_PATH, 'utf8'));
  console.log(`Creating Agent Hub post for ${data.date}...`);
  const { adminToken, nonce } = readAdminToken();
  const { title, body } = buildPost(data);
  console.log(`  title: ${title}`);
  console.log(`  body chars: ${body.length}`);

  const response = await notesApiPost({
    title, body,
    category: ['at-a-glance'],
    visibility: 'public',
    body_format: 'html',
    author_name: 'REALTY EXPERTS',
    notify_enabled: false,
  }, adminToken, nonce);

  const postId = response.id;
  if (!postId) {
    console.error('Error: No post ID returned. Response:', JSON.stringify(response, null, 2));
    process.exit(1);
  }
  const shortId = postId.substring(0, 8);
  const shareUrl = `https://teamrealtyexperts.com/share/${postId}`;
  const qrFile = `note-qr-${shortId}.png`;

  // QR via segno (python), not the qrcode npm module.
  execFileSync('python3.13', ['-c',
    `import segno; segno.make(${JSON.stringify(shareUrl)}, error='m').save(${JSON.stringify(qrFile)}, scale=6, border=1)`],
    { cwd: __dirname, stdio: 'inherit' });

  data.agent_hub_link = shareUrl;
  data.qr_code_path = qrFile;
  fs.writeFileSync(TEMPLATE_PATH, JSON.stringify(data, null, 2));

  console.log(`\n✅ Post created!`);
  console.log(`   Post ID:   ${postId}`);
  console.log(`   Share URL: ${shareUrl}`);
  console.log(`   QR Code:   ${qrFile}`);
  console.log(`   Template updated (agent_hub_link + qr_code_path).`);
}
main().catch(err => { console.error('Error:', err.message); process.exit(1); });
