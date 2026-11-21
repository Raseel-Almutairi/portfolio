// Runs the page's own calculations in Node (no browser): node web_calc.js ../index.html [AS_OF] [NOW_ISO]
// Prints JSON with the overall figures and a few rule checks.
const fs = require('fs');
const html = fs.readFileSync(process.argv[2], 'utf8');
const blocks = [...html.matchAll(/<script([^>]*)>([\s\S]*?)<\/script>/g)];
const controls = JSON.parse(blocks.find((b) => b[1].includes('data-controls'))[2]);
const app = blocks.filter((b) => !b[1].includes('application/json')).map((b) => b[2]).find((s) => s.includes("dash.calc('by_fw'"));
const calcs = {};
const stub = () => new Proxy(function () {}, { get: (t, k) => (k === 'forEach' ? () => {} : stub()), apply: () => stub() });
global.window = {}; global.document = stub(); global.history = stub(); global.location = { hash: '' };
global.requestAnimationFrame = () => {}; global.d3 = { format: () => (x) => String(x), utcFormat: () => (x) => String(x) };
global.dash = { calc: (n, o) => (calcs[n] = o), draw() {}, onData() {}, params: () => ({}), setParams() {}, setLink() {}, data: () => ({ status: 'none', data: [] }), __start() {} };
if (process.argv[3]) window.GX_AS_OF = process.argv[3];
if (process.argv[4]) { const RD = Date, t = new RD(process.argv[4]).getTime(); global.Date = class extends RD { constructor(...a) { super(...(a.length ? a : [t])); } static now() { return t; } }; }
try { new Function('window', 'document', app)(window, document); } catch (e) { /* page wiring needs a browser; the calculations are registered before it */ }
const all = calcs.by_fw.fn(controls)[0];
const row = (id, status, na) => ({ id, status, na_approved: na });
console.log(JSON.stringify({
  compliance: Math.round(all.compliance * 1e4) / 1e4, implemented: all.implemented, denom: all.denom, open: all.open, overdue: all.overdue,
  na_pending: all.na_pending, closed_reassess: all.closed_reassess, no_due: all.no_due, crit_high: all.crit_high,
  rule_mixed_pending: window.gxMainStatus([row('X-1-1-1', 'مطبق', null), row('X-1-1-2', 'لا ينطبق', false)]),
  rule_all_pending: calcs.by_fw.fn([row('X-1-1', 'لا ينطبق', false), row('X-1-2', 'مطبق', null)].map((r) => ({ ...r, framework: 'X', gap_status: '', due: '', priority: '' })))[0].denom,
  rule_invalid: window.gxMainStatus([row('X-1-1', 'مطبق جزئيا', null)]),
  search_same: window.gxNormAr('استراتيجية') === window.gxNormAr('إستراتيجية'),
  riyadh_0030: window.gxRiyadhToday(),
}));
