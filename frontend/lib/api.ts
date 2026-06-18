/**
 * Typed API client for the NoYou FastAPI backend.
 * Base = NEXT_PUBLIC_API_URL (default http://localhost:8013) + "/api/v1".
 * Auth = JWT bearer in localStorage. On 401 -> clear + redirect /login. On 402 -> PlanError.
 */

export const API_BASE =
  (process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ||
    "http://localhost:8000") + "/api/v1";

export const TOKEN_KEY = "noyou_token";

/* --------------------------------- Types --------------------------------- */

export type Plan = "free" | "pro" | "business" | string;

export interface User {
  id: number | string;
  email: string;
  full_name: string | null;
  plan: Plan;
  reputation_score: number;
  is_active: boolean;
  is_verified: boolean;
}

export type AccountPlatform =
  | "twitter"
  | "reddit"
  | "youtube"
  | "google"
  | "web"
  | "hackernews"
  | string;

export interface Account {
  id: number | string;
  platform: AccountPlatform;
  handle: string;
  display_name: string | null;
  profile_url: string | null;
  is_active: boolean;
}

export type ScanStatus = "pending" | "running" | "completed" | "failed";

export interface Scan {
  id: number | string;
  status: ScanStatus;
  trigger: string;
  connectors_used: string[] | null;
  mentions_found: number;
  new_mentions: number;
  score_before: number | null;
  score_after: number | null;
  started_at: string | null;
  finished_at: string | null;
}

export type SentimentLabel = "positive" | "neutral" | "negative";
export type MentionStatus =
  | "active"
  | "archived"
  | "removal_requested"
  | "removed";

export interface MentionAnalysis {
  sentiment: SentimentLabel;
  sentiment_score: number;
  risk_level: number; // 0-5
  risk_category: string;
  context: string;
  summary: string;
  recommendation: string;
  analyzer: string;
  confidence: number;
}

export interface Mention {
  id: number | string;
  source: string;
  url: string | null;
  author: string | null;
  title: string | null;
  content: string;
  status: MentionStatus;
  published_at: string | null;
  discovered_at: string | null;
  analysis: MentionAnalysis | null;
}

export type AlertSeverity = "low" | "medium" | "high" | "critical";

export interface Alert {
  id: number | string;
  severity: AlertSeverity;
  title: string;
  message: string;
  is_read: boolean;
  mention_id: number | string | null;
  created_at: string;
}

export type CleanupStatus =
  | "suggested"
  | "in_progress"
  | "completed"
  | "dismissed";

export interface CleanupAction {
  id: number | string;
  mention_id: number | string | null;
  action_type: string;
  title: string;
  instructions: string;
  status: CleanupStatus;
  automated: boolean;
  created_at: string;
}

export type DashboardBand = "low" | "medium" | "high" | "critical";

export interface SentimentCounts {
  positive: number;
  neutral: number;
  negative: number;
}

export interface DashboardSummary {
  reputation_score: number;
  band: DashboardBand;
  total_mentions: number;
  sentiment_counts: SentimentCounts;
  high_risk_count: number;
  unread_alerts: number;
  active_cleanup_actions: number;
  last_scan_at: string | null;
  top_alerts: Alert[];
  recent_high_risk: Mention[];
}

export type PublishRecommendation =
  | "safe_to_post"
  | "review_suggested"
  | "do_not_post";

export interface AnalyzeResult {
  sentiment: SentimentLabel;
  sentiment_score: number;
  risk_level: number;
  risk_category: string;
  context: string;
  summary: string;
  recommendation: string;
  analyzer: string;
  confidence: number;
  publish_recommendation: PublishRecommendation;
  flagged_terms: string[];
}

export type VisibilityBand = "low" | "medium" | "high" | "excellent";

export interface AiVisibilitySignal {
  name: string;
  present: boolean;
  weight: number;
  detail: string;
}

export interface AiVisibility {
  brand: string;
  ai_visibility_score: number; // 0-100
  band: VisibilityBand;
  signals: AiVisibilitySignal[];
  recommendations: string[];
  summary: string;
  llm_used: string;
}

export interface ScoreHistoryPoint {
  date: string;
  score: number;
  band: string;
}

export interface MentionsOverTimePoint {
  date: string;
  count: number;
}

export interface Report {
  reputation_score: number;
  band: string;
  sentiment_distribution: SentimentCounts;
  risk_by_category: Record<string, number>;
  mentions_by_source: Record<string, number>;
  score_history: ScoreHistoryPoint[];
  mentions_over_time: MentionsOverTimePoint[];
}

export interface MessageResponse {
  message: string;
}

export interface LoginResponse {
  access_token: string;
}

export interface BillingStatus {
  plan: Plan;
  subscription_status: string | null;
  has_active_subscription: boolean;
  publishable_key: string | null;
}

export interface CheckoutResponse {
  url: string;
}

/* ---------------------------- Benchmarking ------------------------------- */

export interface Competitor {
  id: string;
  name: string;
  created_at: string;
}

export interface BenchmarkEntry {
  name: string;
  is_you: boolean;
  reputation_score: number;
  band: string;
  total_mentions: number;
  sentiment: SentimentCounts;
}

export interface BenchmarkReport {
  generated_at: string;
  entries: BenchmarkEntry[];
}

/* ------------------------- Teams / organizations ------------------------- */

export type OrgRole = "owner" | "admin" | "member" | string;
export type MemberStatus = "active" | "invited" | string;

export interface Organization {
  id: string;
  name: string;
  owner_id: string;
  created_at: string;
  /** The requesting user's role in this org. */
  role: OrgRole;
}

export interface OrgMember {
  id: string;
  email: string;
  role: OrgRole;
  status: MemberStatus;
}

/* --------------------------- Automated cleanup --------------------------- */

export type CleanupOutcome = "executed" | "drafted" | "skipped" | string;

export interface CleanupAutoDetail {
  action_id: number | string;
  action_type: string;
  outcome: CleanupOutcome;
  note: string;
}

export interface CleanupAutoSummary {
  executed: number;
  drafted: number;
  skipped: number;
  dry_run: boolean;
  details: CleanupAutoDetail[];
}

/* ------------------------------ Error types ------------------------------ */

export class ApiError extends Error {
  status: number;
  payload: unknown;
  constructor(status: number, message: string, payload?: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.payload = payload;
  }
}

/** Thrown on HTTP 402 — plan upgrade required. Caught by <PlanGate>. */
export class PlanError extends ApiError {
  feature: string | undefined;
  constructor(message: string, payload?: unknown, feature?: string) {
    super(402, message, payload);
    this.name = "PlanError";
    this.feature = feature;
  }
}

/** Type guard for HTTP 402 plan-upgrade errors. */
export function isPlanError(error: unknown): error is PlanError {
  return error instanceof PlanError;
}

/* ------------------------------ Token store ------------------------------ */

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem(TOKEN_KEY);
}

function redirectToLogin(): void {
  if (typeof window === "undefined") return;
  if (window.location.pathname.startsWith("/login")) return;
  window.location.href = "/login";
}

/* ------------------------------ Core request ----------------------------- */

interface RequestOptions {
  method?: string;
  body?: unknown;
  query?: Record<string, string | number | boolean | undefined | null>;
  /** Skip attaching the bearer token (used for login/register). */
  anonymous?: boolean;
  signal?: AbortSignal;
}

function buildUrl(
  path: string,
  query?: RequestOptions["query"]
): string {
  const url = new URL(API_BASE + path);
  if (query) {
    for (const [key, value] of Object.entries(query)) {
      if (value === undefined || value === null || value === "") continue;
      url.searchParams.set(key, String(value));
    }
  }
  return url.toString();
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = "GET", body, query, anonymous, signal } = options;

  const headers: Record<string, string> = {
    Accept: "application/json",
  };
  if (body !== undefined) headers["Content-Type"] = "application/json";

  if (!anonymous) {
    const token = getToken();
    if (token) headers["Authorization"] = `Bearer ${token}`;
  }

  let res: Response;
  try {
    res = await fetch(buildUrl(path, query), {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
      signal,
      cache: "no-store",
    });
  } catch (err) {
    throw new ApiError(0, "Network error — is the API reachable?", err);
  }

  // 204 No Content
  if (res.status === 204) return undefined as T;

  let payload: unknown = null;
  const text = await res.text();
  if (text) {
    try {
      payload = JSON.parse(text);
    } catch {
      payload = text;
    }
  }

  if (res.ok) return payload as T;

  const detail = extractDetail(payload) || res.statusText || "Request failed";

  if (res.status === 401) {
    clearToken();
    redirectToLogin();
    throw new ApiError(401, "Your session expired. Please sign in again.", payload);
  }

  if (res.status === 402) {
    throw new PlanError(detail, payload, extractFeature(payload));
  }

  throw new ApiError(res.status, detail, payload);
}

function extractDetail(payload: unknown): string | null {
  if (!payload || typeof payload !== "object") {
    return typeof payload === "string" ? payload : null;
  }
  const obj = payload as Record<string, unknown>;
  if (typeof obj.detail === "string") return obj.detail;
  if (typeof obj.message === "string") return obj.message;
  if (Array.isArray(obj.detail) && obj.detail.length > 0) {
    const first = obj.detail[0] as Record<string, unknown>;
    if (first && typeof first.msg === "string") return first.msg;
  }
  return null;
}

function extractFeature(payload: unknown): string | undefined {
  if (payload && typeof payload === "object") {
    const obj = payload as Record<string, unknown>;
    if (typeof obj.feature === "string") return obj.feature;
  }
  return undefined;
}

/* -------------------------------- Auth ----------------------------------- */

export const api = {
  /* ---- auth ---- */
  login(input: { email: string; password: string }): Promise<LoginResponse> {
    return request<LoginResponse>("/auth/login", {
      method: "POST",
      body: input,
      anonymous: true,
    });
  },
  register(input: {
    email: string;
    password: string;
    full_name?: string;
  }): Promise<User> {
    return request<User>("/auth/register", {
      method: "POST",
      body: input,
      anonymous: true,
    });
  },
  me(): Promise<User> {
    return request<User>("/auth/me");
  },
  forgotPassword(input: { email: string }): Promise<MessageResponse> {
    return request<MessageResponse>("/auth/forgot-password", {
      method: "POST",
      body: input,
      anonymous: true,
    });
  },
  resetPassword(input: {
    token: string;
    new_password: string;
  }): Promise<MessageResponse> {
    return request<MessageResponse>("/auth/reset-password", {
      method: "POST",
      body: input,
      anonymous: true,
    });
  },
  resendVerification(input: { email: string }): Promise<MessageResponse> {
    return request<MessageResponse>("/auth/resend-verification", {
      method: "POST",
      body: input,
      anonymous: true,
    });
  },
  verifyEmail(input: { token: string }): Promise<MessageResponse> {
    return request<MessageResponse>("/auth/verify-email", {
      method: "POST",
      body: input,
      anonymous: true,
    });
  },

  /* ---- accounts ---- */
  listAccounts(): Promise<Account[]> {
    return request<Account[]>("/accounts");
  },
  createAccount(input: {
    platform: string;
    handle: string;
    display_name?: string;
    profile_url?: string;
  }): Promise<Account> {
    return request<Account>("/accounts", { method: "POST", body: input });
  },
  deleteAccount(id: number | string): Promise<void> {
    return request<void>(`/accounts/${id}`, { method: "DELETE" });
  },

  /* ---- scans ---- */
  startScan(): Promise<Scan> {
    return request<Scan>("/scans", { method: "POST" });
  },
  listScans(limit?: number): Promise<Scan[]> {
    return request<Scan[]>("/scans", { query: { limit } });
  },
  getScan(id: number | string): Promise<Scan> {
    return request<Scan>(`/scans/${id}`);
  },

  /* ---- mentions ---- */
  listMentions(params?: {
    sentiment?: SentimentLabel;
    min_risk?: number;
    source?: string;
    status?: MentionStatus;
    limit?: number;
    offset?: number;
  }): Promise<Mention[]> {
    return request<Mention[]>("/mentions", { query: params });
  },
  updateMentionStatus(
    id: number | string,
    status: MentionStatus
  ): Promise<Mention> {
    return request<Mention>(`/mentions/${id}/status`, {
      method: "PATCH",
      body: { status },
    });
  },

  /* ---- analyze (Pre-Post Check) ---- */
  analyze(input: { text: string; context?: string }): Promise<AnalyzeResult> {
    return request<AnalyzeResult>("/analyze", { method: "POST", body: input });
  },

  /* ---- AI visibility ---- */
  aiVisibility(): Promise<AiVisibility> {
    return request<AiVisibility>("/ai-visibility");
  },

  /* ---- dashboard ---- */
  dashboard(): Promise<DashboardSummary> {
    return request<DashboardSummary>("/dashboard");
  },

  /* ---- alerts ---- */
  listAlerts(params?: {
    unread_only?: boolean;
    limit?: number;
  }): Promise<Alert[]> {
    return request<Alert[]>("/alerts", { query: params });
  },
  markAlertRead(id: number | string): Promise<Alert> {
    return request<Alert>(`/alerts/${id}/read`, { method: "POST" });
  },
  markAllAlertsRead(): Promise<void> {
    return request<void>("/alerts/read-all", { method: "POST" });
  },

  /* ---- cleanup ---- */
  listCleanup(params?: {
    status?: CleanupStatus;
    limit?: number;
  }): Promise<CleanupAction[]> {
    return request<CleanupAction[]>("/cleanup", { query: params });
  },
  updateCleanup(
    id: number | string,
    status: CleanupStatus
  ): Promise<CleanupAction> {
    return request<CleanupAction>(`/cleanup/${id}`, {
      method: "PATCH",
      body: { status },
    });
  },

  /* ---- reports / trends ---- */
  reports(): Promise<Report> {
    return request<Report>("/reports");
  },

  /* ---- privacy ---- */
  exportData(): Promise<unknown> {
    return request<unknown>("/privacy/export");
  },
  deleteAccountData(): Promise<void> {
    return request<void>("/privacy/account", { method: "DELETE" });
  },

  /* ---- billing ---- */
  billingStatus(): Promise<BillingStatus> {
    return request<BillingStatus>("/billing");
  },
  billingCheckout(plan: string): Promise<CheckoutResponse> {
    return request<CheckoutResponse>("/billing/checkout", {
      method: "POST",
      body: { plan },
    });
  },
  billingPortal(): Promise<CheckoutResponse> {
    return request<CheckoutResponse>("/billing/portal", { method: "POST" });
  },

  /* ---- benchmarking (Pro+) ---- */
  listCompetitors(): Promise<Competitor[]> {
    return request<Competitor[]>("/benchmark/competitors");
  },
  addCompetitor(input: { name: string }): Promise<Competitor> {
    return request<Competitor>("/benchmark/competitors", {
      method: "POST",
      body: input,
    });
  },
  removeCompetitor(id: number | string): Promise<void> {
    return request<void>(`/benchmark/competitors/${id}`, { method: "DELETE" });
  },
  benchmarkReport(): Promise<BenchmarkReport> {
    return request<BenchmarkReport>("/benchmark");
  },

  /* ---- teams / organizations ---- */
  listOrgs(): Promise<Organization[]> {
    return request<Organization[]>("/orgs");
  },
  createOrg(input: { name: string }): Promise<Organization> {
    return request<Organization>("/orgs", { method: "POST", body: input });
  },
  listMembers(orgId: number | string): Promise<OrgMember[]> {
    return request<OrgMember[]>(`/orgs/${orgId}/members`);
  },
  inviteMember(
    orgId: number | string,
    input: { email: string }
  ): Promise<OrgMember> {
    return request<OrgMember>(`/orgs/${orgId}/members`, {
      method: "POST",
      body: input,
    });
  },
  removeMember(
    orgId: number | string,
    memberId: number | string
  ): Promise<void> {
    return request<void>(`/orgs/${orgId}/members/${memberId}`, {
      method: "DELETE",
    });
  },
  orgDashboard(orgId: number | string): Promise<DashboardSummary> {
    return request<DashboardSummary>(`/orgs/${orgId}/dashboard`);
  },

  /* ---- automated cleanup (Pro+) ---- */
  autoExecuteCleanup(dryRun = false): Promise<CleanupAutoSummary> {
    return request<CleanupAutoSummary>("/cleanup/auto-execute", {
      method: "POST",
      query: { dry_run: dryRun },
    });
  },
};

/**
 * A generic SWR fetcher bound to api methods is unnecessary —
 * pass the bound api function directly, e.g.
 *   useSWR("dashboard", () => api.dashboard())
 * This helper exists for keys that are plain endpoint paths.
 */
export function swrFetcher<T>(path: string): Promise<T> {
  return request<T>(path);
}
