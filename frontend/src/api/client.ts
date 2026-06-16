import type { Candidate, RankingResult, SystemMetrics } from './types';
import {
  demoCandidates,
  demoRankings,
  demoMetrics,
  paginate,
} from './demoData';

const API_BASE = '/api';

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: response.statusText }));
    throw new Error(error.message || `API Error: ${response.status}`);
  }
  return response.json();
}

/**
 * Try the live API; fall back to bundled demo data so the UI always renders.
 * `isValid` guards against a reachable-but-incompatible backend (the FastAPI
 * demo returns a leaner candidate schema than the rich UI expects).
 */
async function withFallback<T>(
  fn: () => Promise<T>,
  fallback: T,
  isValid?: (value: T) => boolean,
): Promise<T> {
  try {
    const value = await fn();
    if (isValid && !isValid(value)) return fallback;
    return value;
  } catch {
    return fallback;
  }
}

type Page = { candidates: Candidate[]; total: number; page: number; totalPages: number };

const isCandidate = (c: unknown): c is Candidate =>
  !!c && typeof (c as Candidate).overallScore === 'number' && !!(c as Candidate).dimensions;

const isCandidatePage = (p: Page) =>
  !!p && Array.isArray(p.candidates) && (p.candidates.length === 0 || isCandidate(p.candidates[0]));

export const api = {
  rankings: {
    list: () =>
      withFallback(
        () => request<RankingResult[]>('/rankings'),
        demoRankings,
        (v) => Array.isArray(v) && v.length > 0 && !!v[0].results?.[0]?.scoreBreakdown,
      ),

    get: (id: string) =>
      withFallback(
        () => request<RankingResult>(`/rankings/${id}`),
        demoRankings.find((r) => r.id === id) ?? demoRankings[0],
        (v) => !!v?.results?.[0]?.scoreBreakdown,
      ),
  },

  candidates: {
    search: (query: string, page = 1, limit = 20) =>
      withFallback(
        () =>
          request<Page>(`/candidates?q=${encodeURIComponent(query)}&page=${page}&limit=${limit}`),
        paginate(
          query
            ? demoCandidates.filter((c) =>
                `${c.name} ${c.currentRole} ${c.company} ${c.skills.map((s) => s.name).join(' ')}`
                  .toLowerCase()
                  .includes(query.toLowerCase()),
              )
            : demoCandidates,
          page,
          limit,
        ),
        isCandidatePage,
      ),

    get: (id: string) =>
      withFallback(
        () => request<Candidate>(`/candidates/${id}`),
        demoCandidates.find((c) => c.id === id) ?? demoCandidates[0],
        isCandidate,
      ),

    list: (page = 1, limit = 20) =>
      withFallback(
        () => request<Page>(`/candidates?page=${page}&limit=${limit}`),
        paginate(demoCandidates, page, limit),
        isCandidatePage,
      ),
  },

  system: {
    metrics: () =>
      withFallback(
        () => request<SystemMetrics>('/system/metrics'),
        demoMetrics,
        (v) => typeof v?.totalCandidates === 'number',
      ),
  },
};
