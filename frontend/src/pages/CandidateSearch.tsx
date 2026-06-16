import { useEffect, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { api } from '../api/client';
import Icon from '../components/Icon';
import { avatarUrl } from '../lib/avatar';

export default function CandidateSearch() {
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const urlQuery = params.get('q') ?? '';
  const [input, setInput] = useState(urlQuery);
  const [query, setQuery] = useState(urlQuery);

  useEffect(() => {
    setInput(urlQuery);
    setQuery(urlQuery);
  }, [urlQuery]);

  const { data, isLoading } = useQuery({
    queryKey: ['search', query],
    queryFn: () => api.candidates.search(query, 1, 24),
  });

  return (
    <div className="p-container-padding max-w-[1400px] mx-auto space-y-stack-lg">
      <div>
        <h1 className="text-headline-md font-semibold">Candidate Search</h1>
        <p className="text-label-md text-on-surface-variant mt-1">Semantic + graph-expanded search across the indexed talent pool</p>
      </div>

      <form
        onSubmit={(e) => { e.preventDefault(); setQuery(input); }}
        className="relative max-w-2xl"
      >
        <Icon name="search" className="absolute left-4 top-1/2 -translate-y-1/2 text-on-surface-variant" size={20} />
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Search skills, roles, companies… (e.g. “Rust distributed systems”)"
          className="w-full bg-surface-container-low border border-outline-variant rounded-full py-3 pl-12 pr-4 text-body-md placeholder:text-outline focus:outline-none focus:border-primary transition-colors"
        />
      </form>

      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-gutter">
          {[...Array(6)].map((_, i) => <div key={i} className="h-44 bg-surface-container border border-outline-variant rounded-xl animate-pulse" />)}
        </div>
      ) : data && data.candidates.length > 0 ? (
        <>
          <p className="text-label-md text-on-surface-variant">{data.total} candidates</p>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-gutter">
            {data.candidates.map((c, i) => (
              <motion.button
                key={c.id}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.03 }}
                onClick={() => navigate(`/candidates/${c.id}`)}
                className="text-left bg-surface-container border border-outline-variant rounded-xl p-5 hover:border-primary transition-colors group"
              >
                <div className="flex items-start gap-3 mb-4">
                  <img src={avatarUrl(c.name)} alt="" className="w-12 h-12 rounded-full border border-outline-variant" />
                  <div className="flex-1 min-w-0">
                    <div className="font-bold text-on-surface truncate">{c.name}</div>
                    <div className="text-label-md text-on-surface-variant truncate">{c.currentRole}</div>
                    <div className="text-[10px] font-mono text-outline truncate">{c.company} • {c.location}</div>
                  </div>
                  <span className="px-2 py-0.5 bg-primary-container text-on-primary-container rounded-lg font-mono text-mono-sm shrink-0">
                    {c.overallScore.toFixed(1)}
                  </span>
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {c.skills.slice(0, 4).map((s) => (
                    <span key={s.name} className="px-2 py-0.5 bg-surface-container-high border border-outline-variant rounded-lg text-[10px]">{s.name}</span>
                  ))}
                </div>
              </motion.button>
            ))}
          </div>
        </>
      ) : (
        <div className="border border-outline-variant rounded-xl p-12 bg-surface-container text-center">
          <Icon name="search_off" className="text-outline mx-auto" size={32} />
          <p className="text-body-md text-on-surface-variant mt-3">No candidates match “{query}”.</p>
        </div>
      )}
    </div>
  );
}
