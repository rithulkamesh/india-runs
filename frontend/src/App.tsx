import { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import AppLayout from './layout/AppLayout';
import './index.css';

// Route-level code splitting — heavy deps (recharts, xyflow) load on demand.
const Dashboard = lazy(() => import('./pages/Dashboard'));
const CandidateSearch = lazy(() => import('./pages/CandidateSearch'));
const CandidateDetail = lazy(() => import('./pages/CandidateDetail'));
const KnowledgeGraph = lazy(() => import('./pages/KnowledgeGraph'));
const TalentDNA = lazy(() => import('./pages/TalentDNA'));

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { staleTime: 30_000, refetchOnWindowFocus: false, retry: 1 },
  },
});

function PageFallback() {
  return <div className="p-container-padding text-on-surface-variant">Loading…</div>;
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Suspense fallback={<PageFallback />}>
          <Routes>
            <Route element={<AppLayout />}>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/candidates" element={<CandidateSearch />} />
              <Route path="/candidates/:id" element={<CandidateDetail />} />
              <Route path="/knowledge-graph" element={<KnowledgeGraph />} />
              <Route path="/talent-dna" element={<TalentDNA />} />
            </Route>
          </Routes>
        </Suspense>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
