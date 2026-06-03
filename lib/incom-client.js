/**
 * lib/incom-client.js
 * Minimal headless client for the InCom (Drupal) back-office at harvrealtor.com.
 * Built on curl (cross-domain cookie jar + redirects handled natively, matching
 * the repo's existing curl usage). No npm dependencies.
 *
 * Flow proven by recon:
 *   login  → POST /visitor  (edit[name]/edit[pass]/edit[form_id]=user_login/op=Log in)
 *   getForm→ GET  node form, scrape edit[form_token] / edit[form_id] / edit[changed]
 *   postNode→ POST same URL with title/body/path/nodewords + scraped tokens + op=Submit
 */

const { execFileSync } = require('child_process');
const fs = require('fs');
const os = require('os');
const path = require('path');

const UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36';

class IncomClient {
  constructor({ cookieJar } = {}) {
    this.jar = cookieJar || path.join(os.tmpdir(), `incom-cookies-${process.pid}.txt`);
    this.loggedIn = false;
  }

  // Run curl with the shared UA. `input` (string) is fed to stdin if provided.
  _curl(args) {
    return execFileSync('curl', ['-sS', '-A', UA, ...args], {
      encoding: 'utf8', maxBuffer: 64 * 1024 * 1024,
    });
  }

  /** Authenticate. Throws on failure. */
  login(loginUrl, user, pass) {
    try { fs.unlinkSync(this.jar); } catch (_) { /* fresh jar */ }
    // 1) GET the login page to establish the initial session cookie
    this._curl(['-c', this.jar, '-o', '/dev/null', loginUrl]);
    // 2) POST credentials (follow the redirect into the dashboard)
    const body = this._curl([
      '-L', '-b', this.jar, '-c', this.jar,
      '--data-urlencode', `edit[name]=${user}`,
      '--data-urlencode', `edit[pass]=${pass}`,
      '--data-urlencode', 'edit[form_id]=user_login',
      '--data-urlencode', 'op=Log in',
      `${loginUrl}?destination=visitor`,
    ]);
    if (/id="user_login"/.test(body) || /Unrecognized username|password.*(incorrect|not)/i.test(body)) {
      throw new Error('InCom login failed (still seeing the login form — check INCOM_USER / INCOM_PASS)');
    }
    this.loggedIn = true;
    return true;
  }

  /** GET a node form and scrape its Drupal tokens. */
  getForm(url) {
    if (!this.loggedIn) throw new Error('getForm called before login');
    const html = this._curl(['-L', '-b', this.jar, '-c', this.jar, url]);
    if (/id="user_login"/.test(html)) throw new Error(`session not authenticated for ${url}`);
    const grab = (name) => {
      const re = new RegExp('name="' + name.replace(/[[\]]/g, '\\$&') + '"[^>]*\\bvalue="([^"]*)"', 'i');
      const m = html.match(re);
      return m ? m[1] : null;
    };
    return {
      html,
      formToken: grab('edit[form_token]'),
      formId: grab('edit[form_id]'),
      changed: grab('edit[changed]'),
      title: grab('edit[title]'),
      pathAlias: grab('edit[path]'),
    };
  }

  /**
   * POST a node form. `fields` is a flat map of Drupal field name -> value.
   * The (possibly large) body HTML is passed via `bodyHtml` and streamed from a
   * temp file to avoid argv length limits. Returns { status, finalUrl, ok, body }.
   */
  postNode(url, fields, bodyHtml) {
    if (!this.loggedIn) throw new Error('postNode called before login');
    const bodyFile = path.join(os.tmpdir(), `incom-body-${process.pid}.html`);
    const args = ['-L', '-b', this.jar, '-c', this.jar, '-w', '\n__HTTP__%{http_code}__URL__%{url_effective}'];
    for (const [k, v] of Object.entries(fields)) {
      args.push('--data-urlencode', `${k}=${v == null ? '' : v}`);
    }
    if (bodyHtml != null) {
      fs.writeFileSync(bodyFile, bodyHtml);
      args.push('--data-urlencode', `edit[body]@${bodyFile}`);
    }
    args.push(url);
    let out;
    try {
      out = this._curl(args);
    } finally {
      try { if (bodyHtml != null) fs.unlinkSync(bodyFile); } catch (_) { /* ignore */ }
    }
    const m = out.match(/\n__HTTP__(\d+)__URL__(.*)$/s);
    const status = m ? m[1] : '?';
    const finalUrl = m ? m[2].trim() : '';
    const body = m ? out.slice(0, m.index) : out;
    const ok = /has been (created|updated)|been saved|node\/\d+/i.test(body + finalUrl)
      && !/has not been saved|error has occurred|not authorized|please correct/i.test(body);
    return { status, finalUrl, ok, body };
  }

  cleanup() {
    try { fs.unlinkSync(this.jar); } catch (_) { /* ignore */ }
  }
}

function decodeHtml(s) {
  return String(s)
    .replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"')
    .replace(/&#0?39;/g, "'").replace(/&#x27;/gi, "'").replace(/&nbsp;/g, ' ')
    .replace(/&amp;/g, '&');
}

/**
 * Extract every submittable field from the Drupal node-form so an EDIT can
 * re-POST the complete form (Drupal blanks any omitted field). Returns a flat
 * { name: value } map: text/hidden inputs, checked checkboxes/radios, textareas,
 * and the selected <option> of each <select>. Submit buttons are excluded
 * (the caller sets `op` explicitly).
 */
function extractFormFields(html) {
  let f = html;
  const start = html.search(/<form[^>]*\bid="node-form"/i);
  if (start >= 0) {
    f = html.slice(start);
    const end = f.search(/<\/form>/i);
    if (end >= 0) f = f.slice(0, end);
  }
  const fields = {};
  for (const m of f.matchAll(/<input\b[^>]*>/gi)) {
    const tag = m[0];
    const name = (tag.match(/\bname="([^"]*)"/i) || [])[1];
    if (!name) continue;
    const type = ((tag.match(/\btype="([^"]*)"/i) || [])[1] || 'text').toLowerCase();
    const value = (tag.match(/\bvalue="([^"]*)"/i) || [])[1] || '';
    if (type === 'checkbox' || type === 'radio') {
      if (/\bchecked\b/i.test(tag)) fields[name] = decodeHtml(value);
    } else if (type === 'submit' || type === 'button' || type === 'image' || type === 'file') {
      /* skip */
    } else {
      fields[name] = decodeHtml(value);
    }
  }
  for (const m of f.matchAll(/<textarea\b[^>]*\bname="([^"]*)"[^>]*>([\s\S]*?)<\/textarea>/gi)) {
    fields[m[1]] = decodeHtml(m[2]);
  }
  for (const m of f.matchAll(/<select\b[^>]*\bname="([^"]*)"[^>]*>([\s\S]*?)<\/select>/gi)) {
    const inner = m[2];
    let sel = (inner.match(/<option[^>]*\bselected\b[^>]*?\bvalue="([^"]*)"/i)
      || inner.match(/<option[^>]*\bvalue="([^"]*)"[^>]*\bselected\b/i) || [])[1];
    if (sel == null) sel = (inner.match(/<option[^>]*\bvalue="([^"]*)"/i) || [])[1] || '';
    fields[m[1]] = decodeHtml(sel);
  }
  return fields;
}

/** Read INCOM_* from a .env file (no dependency on dotenv). */
function readIncomCreds(envPath) {
  const env = {};
  for (const line of fs.readFileSync(envPath, 'utf8').split('\n')) {
    const t = line.trim();
    if (!t || t.startsWith('#') || !t.includes('=')) continue;
    const i = t.indexOf('=');
    env[t.slice(0, i).trim()] = t.slice(i + 1).trim();
  }
  const url = env.INCOM_LOGIN_URL, user = env.INCOM_USER, pass = env.INCOM_PASS;
  if (!url || !user || !pass) throw new Error('INCOM_LOGIN_URL / INCOM_USER / INCOM_PASS missing from .env');
  return { url, user, pass };
}

module.exports = { IncomClient, readIncomCreds, extractFormFields, decodeHtml };
