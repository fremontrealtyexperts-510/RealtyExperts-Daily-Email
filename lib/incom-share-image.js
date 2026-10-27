/**
 * lib/incom-share-image.js
 * Gives a harvrealtor.com (InCom / Drupal) blog post a share image (og:image) that loads.
 *
 * Found Monday, October 26, 2026 (PT): InCom writes a post's og:image as "https://www.harvrealtor.com" + the src of
 * the FIRST <img> in the body (a Featured Image does not feed it). The daily post's first picture is hosted on
 * dscloud or GitHub, so every daily glance shared "https://www.harvrealtor.comhttps://...", which no link preview
 * (Facebook, LinkedIn, iMessage, Slack) can load. 107 daily posts were fixed by hand that day with the Web
 * workspace's com-fix-share-image.js; this module is the same fix on this repo's IncomClient, so the daily
 * publish applies it on the Mac and on the VPS. Per post, same picture, no visible change:
 *   1. download the first picture; if the post already has a Featured Image of the same picture, reuse it;
 *      otherwise prepare one (a JPEG up to 1600 px wide goes up byte for byte, anything else becomes a web JPEG,
 *      python3 + Pillow, both present on the Mac and the VPS);
 *   2. upload it as the post's "Featured Image" (edit[main_image]); InCom stores it at /files/blog/3316/<nid>.jpg;
 *   3. repoint ONLY that first <img src> to the stored relative path (every other field re-posted as scraped);
 *   4. verify: the node re-reads with only that change, and the live og:image is the .com path.
 * Page nodes (the alameda-Interactive landing) have no Featured Image field: they share the blog's hosted copy
 * via repointFirstImg() when their first <img> is the same picture (sameTagApartFromSrc()).
 */

const fs = require('fs');
const os = require('os');
const path = require('path');
const { execFileSync } = require('child_process');
const { extractFormFields } = require('./incom-client');

const SITE = 'https://www.harvrealtor.com';
const HOSTED = /^\/files\/blog\/\d+\/\d+\.(?:jpe?g|png|gif)$/i;
const SRC = /(?<![\w-])src\s*=\s*"([^"]*)"/i;   // the src attribute only (never data-src or srcset)
const KEEP = ['edit[title]', 'edit[format]', 'edit[path]', 'edit[nodewords][description]', 'edit[nodewords][keywords]'];
const norm = (s) => String(s ?? '').replace(/\r\n/g, '\n').trim();
const sleep = (ms) => Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, ms);
const decodeAttr = (s) => String(s).replace(/&amp;/g, '&');

/** The first <img> in an HTML body: { tag, src, index }, or null. */
function firstImg(body) {
  const m = String(body ?? '').match(/<img\b[^>]*>/i);
  if (!m) return null;
  const s = m[0].match(SRC);
  return s ? { tag: m[0], src: s[1], index: m.index } : null;
}

/** The body with ONLY the first <img>'s src attribute set to `src`. */
function repointFirstImg(body, src) {
  const fi = firstImg(body);
  if (!fi) return body;
  const tag = fi.tag.replace(SRC, (whole, old) => whole.slice(0, whole.length - old.length - 1) + src + '"');
  return body.slice(0, fi.index) + tag + body.slice(fi.index + fi.tag.length);
}

/** True when two <img> tags are the same picture tag apart from their src (alt, size and class all equal). */
function sameTagApartFromSrc(a, b) {
  if (!a || !b) return false;
  const strip = (t) => t.replace(SRC, '').replace(/\s+/g, ' ').trim();
  return strip(a) === strip(b);
}

/** True when a src is a picture InCom hosts for a post's Featured Image. */
const isHosted = (src) => HOSTED.test(decodeAttr(src || ''));

// GETs are retried with a growing pause (InCom reset connections under fast bursts on 10/26); POSTs never are:
// the caller re-reads the node to see what actually landed.
function get(c, args, tries = 4) {
  for (let i = 1; ; i++) {
    try { return c._curl(args); } catch (e) { if (i >= tries) throw e; sleep(3000 * i); }
  }
}

/** The node id behind a public alias, read off the logged-in page's Edit tab link, or ''. */
function nodeIdForAlias(c, alias) {
  let html = '';
  for (let i = 1; ; i++) {
    try { html = c.getForm(`${SITE}/${alias}`).html || ''; break; } catch (e) { if (i >= 3) throw e; sleep(3000 * i); }
  }
  const ids = [...new Set([...html.matchAll(/node\/(\d+)\/edit/g)].map((m) => m[1]))];
  return ids.length === 1 ? ids[0] : '';
}

function loadNode(c, node, alias) {
  const editUrl = `${SITE}/node/${node}/edit`;
  let html;
  for (let i = 1; ; i++) {
    try { html = c.getForm(editUrl).html || ''; break; } catch (e) { if (i >= 4) throw e; sleep(3000 * i); }
  }
  const fields = extractFormFields(html);
  if (!fields['edit[form_token]']) throw new Error(`no form_token on node ${node}'s edit form: not signed in as the editor`);
  if (alias && fields['edit[path]'] !== alias) throw new Error(`node ${node} has alias "${fields['edit[path]']}", not "${alias}"`);
  if (fields['edit[body]'] == null) throw new Error(`no edit[body] on node ${node}'s edit form`);
  const preview = (html.match(/<div id="file_preview"><img src="([^"]*)"/i) || [])[1] || '';
  return { editUrl, fields, preview, hasFeaturedField: /name="edit\[main_image\]"/i.test(html) };
}

/** Read-only: the node's first picture as { src, tag, hosted } (hosted = the .com path, or ''). */
function readFirstPicture(c, node, alias) {
  const a = loadNode(c, node, alias);
  const fi = firstImg(a.fields['edit[body]']);
  if (!fi) return null;
  const src = decodeAttr(fi.src);
  return { src, tag: fi.tag, hosted: isHosted(src) ? src : '' };
}

// The edit form is multipart (it carries the Featured Image file input), so the whole form is re-posted with
// curl -F: every text field with --form-string (an "@" or "<" in a plain -F value is read as a file), the body
// from a temp file. Returns the HTTP code only; a save can answer 200 and still fail, so trust the re-read.
function postMultipart(c, editUrl, fields, body, imagePath) {
  const tmp = path.join(os.tmpdir(), `incom-share-body-${process.pid}.html`);
  fs.writeFileSync(tmp, body);
  const args = ['-L', '-b', c.jar, '-c', c.jar, '-o', '/dev/null', '-w', '%{http_code}'];
  for (const [k, v] of Object.entries(fields)) {
    if (k === 'edit[body]' || k === 'op') continue;
    args.push('--form-string', `${k}=${v == null ? '' : v}`);
  }
  args.push('-F', `edit[body]=<${tmp}`);
  if (imagePath) args.push('-F', `edit[main_image]=@${imagePath};type=image/jpeg`);
  args.push('--form-string', 'op=Submit', editUrl);
  try { return c._curl(args).trim(); } finally { try { fs.unlinkSync(tmp); } catch (_) { /* ignore */ } }
}

const PY_SAME = `
import sys
from PIL import Image, ImageChops, ImageStat
a, b = Image.open(sys.argv[1]), Image.open(sys.argv[2])
same_shape = abs(a.width / a.height - b.width / b.height) < 0.02
x, y = a.convert("L").resize((48, 48)), b.convert("L").resize((48, 48))
print("same" if same_shape and ImageStat.Stat(ImageChops.difference(x, y)).mean[0] < 10 else "different")
`;
const PY_PREP = `
import sys, shutil
from PIL import Image
im = Image.open(sys.argv[1])
if im.format == "JPEG" and im.width <= 1600 and im.mode in ("RGB", "L"):
    shutil.copyfile(sys.argv[1], sys.argv[2]); print("original", im.width, im.height); sys.exit(0)
if im.mode in ("RGBA", "LA", "P"):
    im = im.convert("RGBA"); bg = Image.new("RGB", im.size, (255, 255, 255)); bg.paste(im, mask=im.split()[-1]); im = bg
else:
    im = im.convert("RGB")
if im.width > 1600:
    im = im.resize((1600, round(im.height * 1600 / im.width)), Image.LANCZOS)
im.save(sys.argv[2], "JPEG", quality=85, optimize=True, progressive=True)
print("converted", im.width, im.height)
`;
const python = (code, args) => execFileSync('python3', ['-E', '-P', '-c', code, ...args], { encoding: 'utf8' }).trim();

/**
 * Give one blog node a working og:image. `live: false` downloads and plans but changes nothing.
 * Returns { result, first, tag, hosted, ... } where result is one of:
 *   'fixed'                  the picture is hosted, the src repointed, the live og:image checked
 *   'saved-og-unexpected'    saved and re-read, but the live og:image did not read back as expected (yet)
 *   'skip'                   nothing to do (no picture, or already hosted: `hosted` is set) or cannot (`why`)
 *   'dry-run'                the plan, nothing sent
 * Throws when a save does not read back as intended (the message says what to check).
 */
function fixShareImage(c, { node, alias, live = true }) {
  const a = loadNode(c, node, alias);
  const body0 = a.fields['edit[body]'];
  const fi = firstImg(body0);
  if (!fi) return { result: 'skip', why: 'no <img> in the body' };
  const first = decodeAttr(fi.src);
  if (isHosted(first)) return { result: 'skip', why: 'first picture already hosted on harvrealtor.com', first, tag: fi.tag, hosted: first };
  if (!/^https?:\/\//i.test(first)) return { result: 'skip', why: 'first picture src is relative but not a Featured Image path', first, tag: fi.tag };
  if (!a.hasFeaturedField) return { result: 'skip', why: 'this node type has no Featured Image field', first, tag: fi.tag };

  // 1. download; reuse an existing Featured Image when it is the same picture, else prepare one
  const work = fs.mkdtempSync(path.join(os.tmpdir(), `incom-share-${node}-`));
  try {
    const raw = path.join(work, 'raw.bin'), jpg = path.join(work, `${node}.jpg`), cur = path.join(work, 'featured.bin');
    const head = get(c, ['-L', '-o', raw, '-w', '%{http_code} %{content_type}', first]);
    if (!/^200 image\//i.test(head)) return { result: 'skip', why: `could not download the first picture (${head})`, first, tag: fi.tag };
    let reuse = false;
    const hasFeatured = isHosted(a.preview);
    if (hasFeatured) {
      const fh = get(c, ['-o', cur, '-w', '%{http_code} %{content_type}', `${SITE}${a.preview}`]);
      if (/^200 image\//i.test(fh)) reuse = python(PY_SAME, [raw, cur]) === 'same';
    }
    const plan = reuse ? `reuse ${a.preview}` : python(PY_PREP, [raw, jpg]);
    const bytes = fs.statSync(reuse ? cur : jpg).size;
    if (!live) return { result: 'dry-run', first, tag: fi.tag, plan, bytes, featuredNow: a.preview };

    // 2. Featured Image (the body re-posted unchanged), unless the existing one is the same picture
    let b = a, stored = a.preview;
    if (!reuse) {
      postMultipart(c, a.editUrl, a.fields, body0, jpg);
      b = loadNode(c, node, alias);
      stored = b.preview;
      if (!/^\/files\/blog\/\d+\/\d+\.jpg$/.test(stored)) throw new Error(`the Featured Image was not stored as expected (preview "${stored}"); the body is unchanged`);
      const bad = [...KEEP, 'edit[body]'].filter((k) => norm(b.fields[k]) !== norm(a.fields[k]));
      if (bad.length) throw new Error(`after the Featured Image upload ${bad.join(', ')} changed: check node ${node} by hand`);
    }
    const got = get(c, ['-o', '/dev/null', '-w', '%{http_code} %{content_type}', `${SITE}${stored}`]);
    if (!/^200 image\//i.test(got)) throw new Error(`the stored picture ${stored} does not serve (${got}); the body is unchanged`);

    // 3. repoint only the first <img src>
    const body1 = repointFirstImg(body0, stored);
    postMultipart(c, b.editUrl, b.fields, body1, null);
    const d = loadNode(c, node, alias);
    const bad = KEEP.filter((k) => norm(d.fields[k]) !== norm(a.fields[k]));
    if (norm(d.fields['edit[body]']) !== norm(body1)) bad.push('edit[body] (not the intended single change)');
    if (bad.length) throw new Error(`after the src edit ${bad.join(', ')} not as intended: check node ${node} by hand`);

    // 4. the live og:image (anonymous, cache-busted)
    let og = '';
    for (let i = 1; i <= 3 && !og.endsWith(stored); i++) {
      const page = get(c, [`${SITE}/${alias || `node/${node}`}?ogcheck=${Date.now()}`]);
      og = ((page.match(/<meta property="og:image" content="([^"]*)"/i) || [])[1]) || '';
      if (!og.endsWith(stored)) sleep(2000);
    }
    return {
      result: og === `${SITE}${stored}` ? 'fixed' : 'saved-og-unexpected',
      first, tag: fi.tag, hosted: stored, og, plan: reuse ? 'reused the existing Featured Image' : plan, bytes,
    };
  } finally {
    fs.rmSync(work, { recursive: true, force: true });
  }
}

/** One status line for a fixShareImage() result, for the publish scripts' logs. */
function describe(s) {
  const kb = (n) => `${Math.round(n / 1024)} KB`;
  switch (s.result) {
    case 'fixed': return `✅ og:image ${s.og} (${s.plan}, ${kb(s.bytes)})`;
    case 'saved-og-unexpected': return `⚠️  saved (${s.hosted}), but the live og:image reads "${s.og || 'none'}": re-check with node verify-cms-publish.js`;
    case 'dry-run': return `(dry run) would host ${s.first} as the Featured Image (${s.plan}, ${kb(s.bytes)}) and point the first picture at it`;
    case 'skip':
      if (s.hosted) return `⏭️  already hosted: ${s.hosted}`;
      if (/no <img>/.test(s.why)) return '⏭️  no picture in this post, so InCom writes no og:image (nothing to share)';
      return `⚠️  skipped: ${s.why}`;
    default: return `❌ ${s.error || s.result}`;
  }
}

module.exports = {
  fixShareImage, readFirstPicture, nodeIdForAlias, firstImg, repointFirstImg, sameTagApartFromSrc, isHosted, describe,
};
