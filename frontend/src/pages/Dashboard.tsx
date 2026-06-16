import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import type { SystemMetrics, RankingResult } from '../api/types';
import Icon from '../components/Icon';
import { avatarUrl } from '../lib/avatar';

function fmt(n: number) {
  return n >= 1_000_000 ? `${(n / 1_000_000).toFixed(1)}M` : n.toLocaleString();
}

function Kpi({ icon, label, value, foot, bar }: {
  icon: string; label: string; value: string; foot?: string; bar?: number;
}) {
  return (
    <div className="bg-surface-container p-6 rounded-xl border border-outline-variant">
      <div className="text-on-surface-variant text-label-md mb-2 flex items-center gap-2">
        <Icon name={icon} size={18} /> {label}
      </div>
      <div className="text-headline-md font-bold text-on-surface">{value}</div>
      {bar != null ? (
        <div className="w-full bg-outline-variant h-1 rounded-full mt-3 overflow-hidden">
          <div className="bg-primary h-full" style={{ width: `${bar}%` }} />
        </div>
      ) : (
        foot && <div className="text-[10px] mt-2 font-mono text-on-surface-variant">{foot}</div>
      )}
    </div>
  );
}

function KpiSkeleton() {
  return (
    <div className="bg-surface-container p-6 rounded-xl border border-outline-variant animate-pulse">
      <div className="h-3 w-28 bg-surface-container-highest rounded mb-3" />
      <div className="h-7 w-20 bg-surface-container-highest rounded" />
    </div>
  );
}

export default function Dashboard() {
  const navigate = useNavigate();
  const { data: metrics, isLoading: metricsLoading } = useQuery<SystemMetrics>({ queryKey: ['metrics'], queryFn: api.system.metrics });
  const { data: rankings, isLoading: rankingsLoading } = useQuery<RankingResult[]>({ queryKey: ['rankings'], queryFn: api.rankings.list });

  const top = rankings?.[0];
  const results = top?.results ?? [];
  const avgMatch = results.length ? results.reduce((s, r) => s + r.score, 0) / results.length : 0;

  return (
    <div className="p-container-padding max-w-[1400px] mx-auto space-y-stack-lg">
      <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-gutter">
        {metricsLoading || rankingsLoading ? (
          [0, 1, 2, 3].map((i) => <KpiSkeleton key={i} />)
        ) : (
          <>
            <Kpi icon="group" label="Candidates Indexed" value={fmt(metrics?.totalCandidates ?? 0)} foot="From candidates.jsonl" />
            <Kpi icon="format_list_numbered" label="Shortlisted" value={`${results.length}`} foot={top?.jobTitle} />
            <Kpi icon="stars" label="Avg Match Score" value={`${avgMatch.toFixed(1)}%`} bar={avgMatch} />
            <Kpi icon="emoji_events" label="Top Score" value={`${(results[0]?.score ?? 0).toFixed(1)}%`} foot={results[0]?.candidateName} />
          </>
        )}
      </section>

      <section className="bg-surface-container border border-outline-variant rounded-xl overflow-hidden">
        <div className="p-4 border-b border-outline-variant flex items-center gap-2">
          <h3 className="text-title-md">Candidate Ranking{top ? ` · ${top.jobTitle}` : ''}</h3>
          {rankingsLoading && (
            <span className="text-label-md text-on-surface-variant flex items-center gap-1.5">
              <Icon name="progress_activity" size={16} className="animate-spin" /> ranking…
            </span>
          )}
        </div>
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-surface-container-low border-b border-outline-variant text-on-surface-variant">
              <th className="p-4 text-label-md font-bold">Candidate</th>
              <th className="p-4 text-label-md font-bold">Match</th>
              <th className="p-4 text-label-md font-bold">Skill</th>
              <th className="p-4 text-label-md font-bold">Behavioral</th>
            </tr>
          </thead>
          <tbody>
            {rankingsLoading &&
              Array.from({ length: 8 }).map((_, i) => (
                <tr key={`sk-${i}`} className="border-b border-outline-variant">
                  <td className="p-4">
                    <div className="flex items-center gap-3 animate-pulse">
                      <div className="w-9 h-9 rounded-full bg-surface-container-highest" />
                      <div className="space-y-1.5">
                        <div className="h-3 w-32 bg-surface-container-highest rounded" />
                        <div className="h-2 w-24 bg-surface-container-highest rounded" />
                      </div>
                    </div>
                  </td>
                  <td className="p-4"><div className="h-4 w-12 bg-surface-container-highest rounded animate-pulse" /></td>
                  <td className="p-4"><div className="h-4 w-16 bg-surface-container-highest rounded animate-pulse" /></td>
                  <td className="p-4"><div className="h-4 w-10 bg-surface-container-highest rounded animate-pulse" /></td>
                </tr>
              ))}
            {!rankingsLoading && results.map((r, i) => (
              <tr key={r.candidateId}
                onClick={() => navigate(`/candidates/${r.candidateId}`)}
                className={`cursor-pointer transition-colors ${
                  i === 0 ? 'bg-surface-container-high border-l-4 border-primary hover:bg-surface-container-highest'
                  : 'border-b border-outline-variant hover:bg-surface-container-low'
                }`}>
                <td className="p-4">
                  <div className="flex items-center gap-3">
                    <span className="text-label-md font-mono text-outline w-6">{r.rank}</span>
                    <img src={avatarUrl(r.candidateName)} alt="" className="w-9 h-9 rounded-full border border-outline-variant" />
                    <div>
                      <div className="font-bold text-on-surface">{r.candidateName}</div>
                      <div className="text-[10px] text-on-surface-variant font-mono">{r.currentRole} • {r.company}</div>
                    </div>
                  </div>
                </td>
                <td className="p-4">
                  <span className={`font-mono text-mono-sm px-2 py-0.5 rounded-lg ${
                    i === 0 ? 'bg-primary-container text-on-primary-container' : 'bg-surface-container-highest text-on-surface'
                  }`}>{r.score.toFixed(1)}%</span>
                </td>
                <td className="p-4">
                  <div className="flex items-center gap-2">
                    <div className="w-14 bg-outline-variant h-1 rounded-full overflow-hidden">
                      <div className="bg-primary h-full" style={{ width: `${r.scoreBreakdown.skillMatch}%` }} />
                    </div>
                    <span className="font-mono text-mono-sm">{r.scoreBreakdown.skillMatch}%</span>
                  </div>
                </td>
                <td className="p-4 font-mono text-mono-sm text-on-surface-variant">{r.scoreBreakdown.behavioralFit}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}
