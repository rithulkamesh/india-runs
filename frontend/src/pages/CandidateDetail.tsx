import { useQuery } from '@tanstack/react-query';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { api } from '../api/client';
import type { Candidate, TalentDimensions } from '../api/types';
import Icon from '../components/Icon';
import TalentRadar from '../components/TalentRadar';
import { avatarUrl } from '../lib/avatar';

const DIM_LABELS: Record<keyof TalentDimensions, string> = {
  titleCareer: 'Title & Career',
  skillMatch: 'Skill Match',
  behavioral: 'Behavioral',
  experience: 'Experience',
  location: 'Location',
  education: 'Education',
  domain: 'Domain',
};

function Driver({ label, value, tone, text }: { label: string; value: number; tone: 'primary' | 'tertiary'; text: string }) {
  const border = tone === 'primary' ? 'border-primary' : 'border-tertiary-container';
  const tag = tone === 'primary' ? 'text-primary' : 'text-tertiary';
  return (
    <div className={`p-3 bg-surface-container-low border-l-2 ${border} rounded-r-lg`}>
      <div className="flex items-center justify-between mb-1">
        <span className="text-label-md text-on-surface font-bold">{label}</span>
        <span className={`${tag} font-mono text-mono-sm`}>{value}/100</span>
      </div>
      <p className="text-body-md text-on-surface-variant leading-relaxed">{text}</p>
    </div>
  );
}

function Meta({ label, value, accent }: { label: string; value: string; accent?: boolean }) {
  return (
    <div className="flex items-center justify-between text-label-md">
      <span className="text-outline">{label}</span>
      <span className={accent ? 'text-primary font-bold' : 'text-on-surface'}>{value}</span>
    </div>
  );
}

function Stat({ label, value, sub }: { label: string; value: string; sub: string }) {
  return (
    <div className="bg-surface-container rounded-xl border border-outline-variant p-6 flex flex-col justify-between">
      <span className="text-label-md text-outline uppercase tracking-wider">{label}</span>
      <div className="mt-4">
        <span className="text-display-lg font-bold text-primary">{value}</span>
        <p className="text-label-md text-on-surface-variant">{sub}</p>
      </div>
    </div>
  );
}

export default function CandidateDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: c, isLoading } = useQuery<Candidate>({
    queryKey: ['candidate', id],
    queryFn: () => api.candidates.get(id!),
    enabled: !!id,
  });

  if (isLoading || !c) {
    return <div className="p-container-padding text-on-surface-variant">Loading candidate…</div>;
  }

  const rank = c.rankings[0];
  const dimEntries = (Object.keys(DIM_LABELS) as (keyof TalentDimensions)[])
    .map((k) => ({ key: k, label: DIM_LABELS[k], value: c.dimensions[k] }))
    .sort((a, b) => b.value - a.value);
  const strengths = dimEntries.slice(0, 3);
  const gaps = dimEntries.slice(-2).reverse();
  const avgProf = c.skills.length ? Math.round(c.skills.reduce((s, k) => s + k.proficiency, 0) / c.skills.length) : 0;
  const topSkills = [...c.skills].sort((a, b) => b.proficiency - a.proficiency).slice(0, 6);

  return (
    <div className="flex h-[calc(100vh-64px)]">
      {/* Left profile panel */}
      <aside className="w-80 shrink-0 border-r border-outline-variant bg-surface-container-lowest overflow-y-auto custom-scrollbar">
        <div className="p-container-padding">
          <button onClick={() => navigate(-1)} className="text-on-surface-variant hover:text-on-surface text-label-md flex items-center gap-1 mb-4">
            <Icon name="arrow_back" size={18} /> Back
          </button>
          <div className="relative w-24 h-24 rounded-xl overflow-hidden border border-outline-variant mb-4 bg-surface-container">
            <img src={avatarUrl(c.name, 192)} alt={c.name} className="w-full h-full object-cover" />
          </div>
          <h2 className="text-headline-md font-semibold mb-1">{c.name}</h2>
          <p className="text-body-md text-on-surface-variant mb-6">{c.currentRole} @ {c.company}</p>

          <div className="space-y-4">
            {rank && <Meta label="Rank" value={`#${rank.rank}`} accent />}
            <Meta label="Match Score" value={`${c.overallScore.toFixed(1)}%`} />
            <Meta label="Location" value={c.location || '—'} />
            <Meta label="Skills tracked" value={`${c.skills.length}`} />
          </div>

          <div className="mt-8 pt-8 border-t border-outline-variant">
            <h3 className="text-label-md font-bold uppercase tracking-wider text-outline mb-4">Top Skills</h3>
            <div className="flex flex-wrap gap-2">
              {topSkills.slice(0, 6).map((s) => (
                <span key={s.name} className="px-2 py-1 bg-surface-container-high border border-outline-variant rounded-lg text-label-md">
                  {s.name}
                </span>
              ))}
            </div>
          </div>

          <div className="mt-8 pt-8 border-t border-outline-variant">
            <h3 className="text-label-md font-bold uppercase tracking-wider text-outline mb-4">Behavioral Signals</h3>
            <div className="space-y-3">
              {c.behavioralSignals.map((b) => (
                <div key={b.type} className="flex items-center justify-between text-label-md">
                  <span className="text-on-surface-variant">{b.type}</span>
                  <span className="text-on-surface font-medium">{b.value}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </aside>

      {/* Main scroll area */}
      <div className="flex-1 overflow-y-auto custom-scrollbar bg-surface p-container-padding">
        <div className="grid grid-cols-12 gap-gutter max-w-7xl mx-auto">
          {/* Explainability */}
          <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}
            className="col-span-12 lg:col-span-8 bg-surface-container rounded-xl border border-outline-variant p-6 flex flex-col gap-6">
            <h3 className="text-title-md font-bold flex items-center gap-2"><Icon name="psychology" className="text-primary" /> Why this rank</h3>
            <p className="text-body-md text-on-surface-variant leading-relaxed border-l-2 border-primary pl-4">{c.reasoning}</p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <h4 className="text-label-md font-bold text-outline uppercase tracking-wider">Strengths</h4>
                <div className="space-y-3">
                  {strengths.map((s) => (
                    <Driver key={s.key} label={s.label} value={s.value} tone="primary"
                      text={`Top-tier signal — drives this candidate's match for ${s.label.toLowerCase()}.`} />
                  ))}
                </div>
              </div>
              <div className="space-y-4">
                <h4 className="text-label-md font-bold text-outline uppercase tracking-wider">Gaps</h4>
                <div className="space-y-3">
                  {gaps.map((g) => (
                    <Driver key={g.key} label={g.label} value={g.value} tone="tertiary"
                      text={`Lowest dimension — probe ${g.label.toLowerCase()} in the interview.`} />
                  ))}
                </div>
              </div>
            </div>
          </motion.div>

          {/* Radar */}
          <div className="col-span-12 lg:col-span-4 bg-surface-container rounded-xl border border-outline-variant p-6 flex flex-col">
            <h3 className="text-label-md font-bold text-outline uppercase tracking-wider mb-2">Talent DNA</h3>
            <TalentRadar dimensions={c.dimensions} height={300} />
          </div>

          {/* Experience */}
          <div className="col-span-12 lg:col-span-7 bg-surface-container rounded-xl border border-outline-variant p-6 flex flex-col gap-4">
            <h3 className="text-title-md font-bold flex items-center gap-2"><Icon name="work_history" className="text-primary" /> Experience</h3>
            <div className="space-y-3">
              {c.experience.map((e) => (
                <div key={`${e.company}-${e.startDate}`} className="flex gap-3">
                  <div className="mt-1.5 w-2 h-2 rounded-full bg-primary shrink-0" />
                  <div>
                    <div className="text-body-md text-on-surface font-medium">{e.title} · {e.company}</div>
                    <div className="text-[10px] font-mono text-outline">{e.startDate || '—'} – {e.endDate ?? 'Present'}</div>
                    {e.description && <p className="text-label-md text-on-surface-variant mt-0.5">{e.description}</p>}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Real stats + skill proficiency */}
          <div className="col-span-12 lg:col-span-5 grid grid-cols-2 gap-4 content-start">
            <Stat label="Match Score" value={`${c.overallScore.toFixed(0)}`} sub="Overall fit" />
            <Stat label="Avg Proficiency" value={`${avgProf}`} sub={`Across ${c.skills.length} skills`} />
            <div className="col-span-2 bg-surface-container rounded-xl border border-outline-variant p-6">
              <div className="flex items-center justify-between mb-4">
                <span className="text-label-md text-outline uppercase tracking-wider">Top skill proficiency</span>
                <Icon name="bar_chart" className="text-outline" />
              </div>
              <div className="space-y-3">
                {topSkills.map((s) => (
                  <div key={s.name}>
                    <div className="flex justify-between text-label-md mb-1">
                      <span className="text-on-surface-variant">{s.name}</span>
                      <span className="font-mono text-primary">{s.proficiency}</span>
                    </div>
                    <div className="h-1.5 w-full bg-outline-variant rounded-full overflow-hidden">
                      <div className="bg-primary h-full" style={{ width: `${s.proficiency}%` }} />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
