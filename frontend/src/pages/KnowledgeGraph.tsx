import { useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  ReactFlow,
  Background,
  Controls,
  type Node,
  type Edge,
  BackgroundVariant,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { api } from '../api/client';
import Icon from '../components/Icon';

export default function KnowledgeGraph() {
  const { data } = useQuery({ queryKey: ['candidates', 1, 'graph'], queryFn: () => api.candidates.list(1, 6) });
  const candidates = data?.candidates ?? [];

  const { nodes, edges } = useMemo(() => {
    const nodes: Node[] = [];
    const edges: Edge[] = [];

    nodes.push({
      id: 'role',
      position: { x: 520, y: 300 },
      data: { label: 'Principal Platform Engineer' },
      style: {
        background: 'var(--color-primary)', color: 'var(--color-on-primary)', border: '2px solid var(--color-primary)',
        borderRadius: 12, fontWeight: 700, fontSize: 12, padding: 10, width: 200, textAlign: 'center',
      },
    });

    const skillSet = new Map<string, { x: number; y: number }>();
    const radius = 280;

    candidates.forEach((c, i) => {
      const angle = (i / candidates.length) * Math.PI * 2;
      const x = 600 + Math.cos(angle) * radius;
      const y = 320 + Math.sin(angle) * radius;
      nodes.push({
        id: c.id,
        position: { x, y },
        data: { label: `${c.name}\n${c.overallScore.toFixed(1)}%` },
        style: {
          background: 'var(--color-surface-container)', color: 'var(--color-on-surface)', border: '2px solid var(--color-outline-variant)',
          borderRadius: 9999, fontSize: 11, fontWeight: 600, padding: 8, width: 120,
          textAlign: 'center', whiteSpace: 'pre-line',
        },
      });
      edges.push({
        id: `e-role-${c.id}`, source: 'role', target: c.id, animated: i < 2,
        style: { stroke: i < 2 ? 'var(--color-primary)' : 'var(--color-outline-variant)' },
      });

      c.skills.slice(0, 2).forEach((s, j) => {
        const sid = `skill-${s.name}`;
        if (!skillSet.has(sid)) {
          const sa = Math.random() * Math.PI * 2;
          skillSet.set(sid, { x: x + Math.cos(sa) * 140 + j * 20, y: y + Math.sin(sa) * 140 });
          const pos = skillSet.get(sid)!;
          nodes.push({
            id: sid,
            position: pos,
            data: { label: s.name },
            style: {
              background: 'var(--color-surface-container-high)', color: 'var(--color-on-surface-variant)', border: '1px solid var(--color-outline-variant)',
              borderRadius: 8, fontSize: 10, padding: 6, width: 90, textAlign: 'center',
            },
          });
        }
        edges.push({ id: `e-${c.id}-${sid}`, source: c.id, target: sid, style: { stroke: 'var(--color-outline-variant)', strokeDasharray: '4' } });
      });
    });

    return { nodes, edges };
  }, [candidates]);

  return (
    <div className="p-container-padding max-w-[1400px] mx-auto space-y-4 h-[calc(100vh-64px)] flex flex-col">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-headline-md font-semibold flex items-center gap-2"><Icon name="account_tree" className="text-primary" /> Candidate Graph</h1>
          <p className="text-label-md text-on-surface-variant mt-1">Top-ranked candidates linked to the role and their shared skills</p>
        </div>
      </div>

      <div className="flex-1 rounded-xl border border-outline-variant overflow-hidden bg-surface-container-lowest">
        <ReactFlow nodes={nodes} edges={edges} fitView proOptions={{ hideAttribution: true }}>
          <Background variant={BackgroundVariant.Dots} gap={28} size={1} color="var(--color-outline-variant)" />
          <Controls className="!bg-surface-container !border-outline-variant" />
        </ReactFlow>
      </div>
    </div>
  );
}
