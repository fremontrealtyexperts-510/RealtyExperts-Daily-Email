/**
 * update-master-tab.js  <clean.csv>
 * Clears the master sheet's MLS_Defined_Spread_Sheet_4 tab and writes the given
 * clean CSV (today's re-export, real prices). Same effect as mls-pipeline.js
 * updateSheet(), minus the python render + Drive PNG push (done separately).
 * Needs the service account = Editor on the master sheet.
 */
const https = require('https'), crypto = require('crypto'), fs = require('fs'), path = require('path');
const KEY = path.join(__dirname, 'harvrealtor-0819122f6566-google-drive.json');
const SHEET_ID = '1YxbK29giJO6XDQAV3RHXml2vjMejmtBpZfD3ICW_gTw';
const DATA_TAB = 'MLS_Defined_Spread_Sheet_4';
const SCOPES = 'https://www.googleapis.com/auth/spreadsheets';
const CSV = process.argv[2] || '/tmp/mls-today.csv';
const b64u = s => Buffer.from(s).toString('base64').replace(/=/g, '').replace(/\+/g, '-').replace(/\//g, '_');
function jwt(c){const n=Math.floor(Date.now()/1000);const h=b64u(JSON.stringify({alg:'RS256',typ:'JWT'}));const p=b64u(JSON.stringify({iss:c.client_email,scope:SCOPES,aud:'https://oauth2.googleapis.com/token',iat:n,exp:n+3600}));const u=`${h}.${p}`;const s=crypto.createSign('RSA-SHA256').update(u).sign(c.private_key,'base64').replace(/=/g,'').replace(/\+/g,'-').replace(/\//g,'_');return`${u}.${s}`;}
function req(m,u,t,o={}){return new Promise((res,rej)=>{const r=https.request(u,{method:m,headers:{Authorization:`Bearer ${t}`,...(o.headers||{})}},x=>{let b='';x.on('data',c=>b+=c);x.on('end',()=>res({status:x.statusCode,body:b}))});r.on('error',rej);if(o.body)r.write(o.body);r.end();});}
function parseCsv(text){const rows=[];let row=[],cell='',q=false;for(let i=0;i<text.length;i++){const ch=text[i];if(q){if(ch==='"'){if(text[i+1]==='"'){cell+='"';i++;}else q=false;}else cell+=ch;}else if(ch==='"')q=true;else if(ch===','){row.push(cell);cell='';}else if(ch==='\n'){row.push(cell);rows.push(row);row=[];cell='';}else if(ch==='\r'){}else cell+=ch;}if(cell.length||row.length){row.push(cell);rows.push(row);}return rows.filter(r=>r.some(c=>c!==''));}
// numeric-ify LP/SP/size cells so the tab holds real numbers, not strings
function coerce(rows){const numCols=new Set([2,7,8,10,11,12,13,15,16,17,18,19]);return rows.map((r,ri)=>ri===0?r:r.map((v,ci)=>{if(numCols.has(ci)&&v!==''&&v!=null&&!isNaN(v))return Number(v);return v;}));}
(async () => {
  const c = JSON.parse(fs.readFileSync(KEY, 'utf8'));
  const tr = await req('POST','https://oauth2.googleapis.com/token','',{headers:{'Content-Type':'application/x-www-form-urlencoded'},body:`grant_type=urn%3Aietf%3Aparams%3Aoauth%3Agrant-type%3Ajwt-bearer&assertion=${jwt(c)}`});
  const tok = JSON.parse(tr.body).access_token;
  if (!tok) throw new Error('auth failed: ' + tr.body.slice(0,200));
  let rows = coerce(parseCsv(fs.readFileSync(CSV, 'utf8')));
  const hashes = rows.slice(1).filter(r => String(r[7]||'').startsWith('####')).length;
  if (hashes > 0) throw new Error(`refusing to write: ${hashes} #### rows in ${CSV}`);
  console.log(`writing ${rows.length} rows x ${rows[0].length} cols (0 #### in LP) into '${DATA_TAB}'`);
  let r = await req('POST',`https://sheets.googleapis.com/v4/spreadsheets/${SHEET_ID}/values/${encodeURIComponent(DATA_TAB)}:clear`,tok,{headers:{'Content-Type':'application/json'},body:'{}'});
  if (r.status !== 200) throw new Error('clear failed: ' + r.body.slice(0,200));
  r = await req('PUT',`https://sheets.googleapis.com/v4/spreadsheets/${SHEET_ID}/values/${encodeURIComponent(DATA_TAB+'!A1')}?valueInputOption=USER_ENTERED`,tok,{headers:{'Content-Type':'application/json'},body:JSON.stringify({values:rows})});
  if (r.status !== 200) throw new Error('write failed: ' + r.body.slice(0,300));
  console.log('master tab updated:', JSON.parse(r.body).updatedCells, 'cells');
})().catch(e => { console.error('ERROR:', e.message); process.exit(1); });
