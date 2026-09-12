// DOM palsu berbasis Proxy: cukup untuk EVALUASI modul (bukan uji tampilan).
const mkEl = () => {
  const store = {};
  const el = new Proxy(function(){}, {
    get(t, k) {
      if (k === 'classList') return { add(){}, remove(){}, toggle(){ return false; }, contains(){ return false; } };
      if (k === 'style') return new Proxy({}, { get: () => '', set: () => true });
      if (k === 'dataset') return {};
      if (k === 'children' || k === 'childNodes') return [];
      if (k === 'querySelectorAll') return () => [];
      if (k === 'querySelector' || k === 'closest' || k === 'getElementById') return () => mkEl();
      if (k === 'getBoundingClientRect') return () => ({ width: 0, height: 0, top: 0, left: 0, right: 0, bottom: 0 });
      if (k === 'getContext') return () => new Proxy({}, { get: () => () => {} });
      if (k === 'value' || k === 'textContent' || k === 'innerHTML' || k === 'className' || k === 'id') return store[k] === undefined ? '' : store[k];
      if (k === 'checked' || k === 'disabled' || k === 'hidden') return !!store[k];
      if (k === 'length') return 0;
      if (k === Symbol.toPrimitive) return () => '';
      if (k === 'then') return undefined;
      if (typeof k === 'string' && k in store) return store[k];
      return mkEl();
    },
    set(t, k, v) { store[k] = v; return true; },
    apply() { return mkEl(); }
  });
  return el;
};
const ls = (() => { let m = {}; return {
  getItem: k => (k in m ? m[k] : null), setItem: (k, v) => { m[k] = String(v); },
  removeItem: k => { delete m[k]; }, clear: () => { m = {}; }, key: i => Object.keys(m)[i] || null, get length() { return Object.keys(m).length; } }; })();
const doc = mkEl();
globalThis.window = globalThis;
globalThis.document = doc;
globalThis.HTMLElement = function(){}; globalThis.Node = function(){}; globalThis.Element = function(){};
globalThis.localStorage = ls; globalThis.sessionStorage = ls;
globalThis.navigator = { onLine: true, userAgent: 'jsc-harness', serviceWorker: undefined, language: 'id' };
globalThis.location = { href: 'https://example.invalid/index.html', hash: '', search: '', pathname: '/index.html', reload() {} };
globalThis.history = { replaceState() {}, pushState() {} };
globalThis.alert = () => {}; globalThis.confirm = () => false; globalThis.prompt = () => null;
globalThis.addEventListener = () => {}; globalThis.removeEventListener = () => {};
globalThis.matchMedia = () => ({ matches: false, addEventListener() {}, addListener() {} });
globalThis.requestAnimationFrame = f => 0; globalThis.cancelAnimationFrame = () => {};
globalThis.getComputedStyle = () => new Proxy({}, { get: () => '' });
globalThis.innerWidth = 390; globalThis.innerHeight = 844; globalThis.devicePixelRatio = 2;
globalThis.scrollTo = () => {}; globalThis.open = () => null;
globalThis.Blob = class { constructor(p) { this.p = p; } }; globalThis.URL = { createObjectURL: () => 'blob:x', revokeObjectURL() {} };
globalThis.FileReader = class { readAsDataURL() {} readAsText() {} };
globalThis.Image = class { }; globalThis.Audio = class { play() { return Promise.resolve(); } };
globalThis.fetch = () => Promise.reject(new Error('fetch dimatikan di harness'));
globalThis.crypto = { subtle: { digest: () => Promise.resolve(new ArrayBuffer(32)) }, getRandomValues: a => a };
globalThis.TextEncoder = class { encode(s) { return new Uint8Array(String(s).length); } };
globalThis.Notification = { permission: 'denied' };
globalThis.IntersectionObserver = class { observe() {} disconnect() {} };
globalThis.ResizeObserver = class { observe() {} disconnect() {} };
globalThis.MutationObserver = class { observe() {} disconnect() {} };
globalThis.CustomEvent = class { constructor(t, d) { this.type = t; this.detail = d && d.detail; } };
globalThis.Event = globalThis.CustomEvent;
globalThis.performance = { now: () => Date.now() };
globalThis.screen = { width: 390, height: 844 };
globalThis.visualViewport = { height: 844, width: 390, addEventListener() {} };
globalThis.speechSynthesis = undefined;
globalThis.setTimeout = (f) => 0; globalThis.setInterval = (f) => 0; globalThis.clearTimeout = () => {}; globalThis.clearInterval = () => {};
globalThis.console = { log() {}, warn() {}, error() {}, info() {}, debug() {}, table() {}, group() {}, groupEnd() {} };
