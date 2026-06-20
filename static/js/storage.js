// static/js/storage.js
// Centralized localStorage access with key constants and JSON parse safety

// ── Key constants ──
export const KEYS = {
  THEME: 'devante-cli-theme',
  TOGGLES: 'devante-cli-toggles',
  SIDEBAR_COLLAPSED: 'sidebar-collapsed',
  SIDEBAR_WIDTH: 'sidebar-width',
  SIDEBAR_SIDE: 'sidebar-side',
  CURRENT_SESSION: 'currentSessionId',
  COMPARE_SAVE: 'compare-save-results',
  COMPARE_CHAT: 'compare-continue-chat',
  COMPARE_BLIND: 'compare-blind',
  COMPARE_RANDOM: 'compare-randomize',
  MODELS_EXPANDED: 'devante-cli-model-expanded',
  MODEL_ENDPOINTS: 'devante-cli-model-endpoints',
  MODEL_SELECTED: 'devante-cli-selected-model',
  SORT_ORDER: 'devante-cli-sessions-sort',
  CHAT_SEARCH_SCOPE: 'devante-cli-search-scope',
  INCOGNITO: 'devante-cli-incognito',
  RAG_ACTIVE: 'devante-cli-rag-active',
  MCP_ACTIVE: 'devante-cli-mcp-active',
  SECTION_ORDER: 'sidebar-section-order',
  ADMIN_LAST_TAB: 'admin-last-tab',
  DENSITY: 'devante-cli-density',
  WORKSPACE: 'devante-cli-workspace',
  WORKSPACE_VERIFIED: 'devante-cli-workspace-verified',
  WORKSPACE_RISK_ACK: 'devante-cli-workspace-risk-ack',
  HOST_TERMINAL_BANNER_DISMISSED: 'devante-cli-host-terminal-banner-dismissed',
  WORKSPACE_SESSIONS: 'devante-cli-workspace-sessions',
  PLAN: 'devante-cli-plan',
  IDE_LAYOUT: 'devante-cli-ide-layout',
};

/**
 * Safely get and parse a JSON value from localStorage.
 * Returns fallback on any error.
 */
export function getJSON(key, fallback) {
  try {
    const raw = localStorage.getItem(key);
    if (raw === null) return fallback !== undefined ? fallback : null;
    return JSON.parse(raw);
  } catch (e) {
    console.warn('[Storage] Failed to parse key "' + key + '":', e.message);
    return fallback !== undefined ? fallback : null;
  }
}

/**
 * Set a JSON-serialized value in localStorage.
 */
export function setJSON(key, value) {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch (e) {
    console.warn('[Storage] Failed to set key "' + key + '":', e.message);
  }
}

/**
 * Get a raw string value from localStorage.
 */
export function get(key, fallback) {
  try {
    const val = localStorage.getItem(key);
    return val !== null ? val : (fallback !== undefined ? fallback : null);
  } catch (e) {
    return fallback !== undefined ? fallback : null;
  }
}

/**
 * Set a raw string value in localStorage.
 */
export function set(key, value) {
  try {
    localStorage.setItem(key, value);
  } catch (e) {
    console.warn('[Storage] Failed to set key "' + key + '":', e.message);
  }
}

/**
 * Remove a key from localStorage.
 */
export function remove(key) {
  try {
    localStorage.removeItem(key);
  } catch (e) {
    // Ignore removal errors
  }
}

// ── Toggle state helpers ──

export function loadToggleState() {
  return getJSON(KEYS.TOGGLES, {});
}

export function saveToggleState(state) {
  setJSON(KEYS.TOGGLES, state);
}

export function getToggle(name, fallback) {
  const state = loadToggleState();
  return state[name] !== undefined ? state[name] : (fallback !== undefined ? fallback : false);
}

export function setToggle(name, value) {
  const state = loadToggleState();
  state[name] = value;
  saveToggleState(state);
}

const Storage = {
  KEYS,
  getJSON,
  setJSON,
  get,
  set,
  remove,
  loadToggleState,
  saveToggleState,
  getToggle,
  setToggle
};

export default Storage;
