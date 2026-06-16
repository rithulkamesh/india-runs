import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  ResponsiveContainer,
} from 'recharts';
import type { TalentDimensions } from '../api/types';

const LABELS: Record<keyof TalentDimensions, string> = {
  titleCareer: 'Title & Career',
  skillMatch: 'Skill Match',
  behavioral: 'Behavioral',
  experience: 'Experience',
  location: 'Location',
  education: 'Education',
  domain: 'Domain',
};

export default function TalentRadar({
  dimensions,
  height = 280,
}: {
  dimensions: TalentDimensions;
  height?: number;
}) {
  const data = (Object.keys(LABELS) as (keyof TalentDimensions)[]).map((k) => ({
    dim: LABELS[k],
    value: dimensions[k],
  }));

  return (
    <ResponsiveContainer width="100%" height={height}>
      <RadarChart data={data} outerRadius="72%">
        <PolarGrid stroke="var(--color-outline-variant)" strokeDasharray="2" />
        <PolarAngleAxis
          dataKey="dim"
          tick={{ fill: 'var(--color-on-surface-variant)', fontSize: 10, fontWeight: 600 }}
        />
        <Radar
          dataKey="value"
          stroke="var(--color-primary)"
          strokeWidth={2}
          fill="var(--color-primary)"
          fillOpacity={0.16}
          isAnimationActive
        />
      </RadarChart>
    </ResponsiveContainer>
  );
}
