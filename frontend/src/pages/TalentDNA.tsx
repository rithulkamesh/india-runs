import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../api/client';
import type { TalentDimensions } from '../api/types';
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

export default function TalentDNA() {
  const { data } = useQuery({ queryKey: ['candidates', 1, 'dna'], queryFn: () => api.candidates.list(1, 12) });
  const candidates = data?.candidates ?? [];
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const selected = candidates.find((c) => c.id === selectedId) ?? candidates[0];

  return (
    <div className="p-container-padding max-w-[1400px] mx-auto space-y-stack-lg">
      <div>
        <h1 className="text-headline-md font-semibold flex items-center gap-2"><Icon name="fingerprint" className="text-primary" /> Talent DNA</h1>
        <p className="text-label-md text-on-surface-variant mt-1">Eight-dimension behavioral & technical fingerprint</p>
      </div>

      <div className="grid grid-cols-12 gap-gutter items-start">
        {/* Selector */}
        <aside className="col-span-12 lg:col-span-3 bg-surface-container border border-outline-variant rounded-xl p-3 space-y-1">
          {candidates.map((c) => (
            <button
              key={c.id}
              onClick={() => setSelectedId(c.id)}
              className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-left transition-colors ${
                selected?.id === c.id ? 'bg-surface-container-high text-primary' : 'text-on-surface-variant hover:bg-surface-container-low'
              }`}
            >
              <img src={avatarUrl(c.name, 48)} alt="" className="w-8 h-8 rounded-full border border-outline-variant" />
              <div className="min-w-0">
                <div className="text-label-md font-medium text-on-surface truncate">{c.name}</div>
                <div className="text-[10px] font-mono text-outline truncate">{c.currentRole}</div>
              </div>
            </button>
          ))}
        </aside>

        {/* Radar */}
        <section className="col-span-12 lg:col-span-5 bg-surface-container border border-outline-variant rounded-xl p-6">
          <h3 className="text-title-md mb-2">{selected?.name ?? '—'}</h3>
          <p className="text-label-md text-on-surface-variant mb-4">{selected?.currentRole} @ {selected?.company}</p>
          {selected && <TalentRadar dimensions={selected.dimensions} height={340} />}
        </section>

        {/* Dimension bars */}
        <section className="col-span-12 lg:col-span-4 bg-surface-container border border-outline-variant rounded-xl p-6 space-y-4">
          <h3 className="text-label-md font-bold uppercase tracking-wider text-outline">Dimension Breakdown</h3>
          {selected && (Object.keys(DIM_LABELS) as (keyof TalentDimensions)[]).map((k) => {
            const v = selected.dimensions[k];
            return (
              <div key={k}>
                <div className="flex justify-between text-label-md mb-1">
                  <span className="text-on-surface-variant">{DIM_LABELS[k]}</span>
                  <span className="font-mono text-primary">{v}</span>
                </div>
                <div className="h-1.5 w-full bg-outline-variant rounded-full overflow-hidden">
                  <div className={`h-full ${v >= 90 ? 'bg-primary' : v >= 80 ? 'bg-secondary' : 'bg-tertiary'}`} style={{ width: `${v}%` }} />
                </div>
              </div>
            );
          })}
        </section>
      </div>
    </div>
  );
}
