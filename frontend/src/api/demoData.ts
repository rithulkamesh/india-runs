import type {
  Candidate,
  RankingResult,
  RankedCandidate,
  SystemMetrics,
} from './types';

const dims = (
  titleCareer: number,
  skillMatch: number,
  behavioral: number,
  experience: number,
  location: number,
  education: number,
  domain: number,
) => ({ titleCareer, skillMatch, behavioral, experience, location, education, domain });

export const demoCandidates: Candidate[] = [
  {
    id: 'cand-001',
    name: 'Arjun Mehta',
    email: 'arjun.mehta@neurasync.ai',
    currentRole: 'Staff Systems Architect',
    company: 'NeuraSync',
    location: 'San Francisco, CA',
    overallScore: 98.4,
    dimensions: dims(96, 88, 90, 92, 78, 95, 70),
    skills: [
      { name: 'Rust', category: 'Languages', proficiency: 95, yearsOfExperience: 7 },
      { name: 'Distributed Systems', category: 'Architecture', proficiency: 93, yearsOfExperience: 9 },
      { name: 'Kubernetes', category: 'Infra', proficiency: 88, yearsOfExperience: 6 },
      { name: 'LLM Ops', category: 'AI', proficiency: 84, yearsOfExperience: 3 },
      { name: 'Go', category: 'Languages', proficiency: 90, yearsOfExperience: 8 },
      { name: 'Team Leadership', category: 'Leadership', proficiency: 87, yearsOfExperience: 5 },
    ],
    experience: [
      {
        title: 'Staff Systems Architect',
        company: 'NeuraSync',
        startDate: '2021-03',
        endDate: null,
        description: 'Owns cross-org architecture for the real-time inference platform serving 2.4M req/s.',
      },
      {
        title: 'Principal Engineer',
        company: 'Stripe',
        startDate: '2017-06',
        endDate: '2021-02',
        description: 'Led decoupling of the legacy ledger into geo-redundant microservices.',
      },
      {
        title: 'Senior SWE',
        company: 'Meta',
        startDate: '2014-01',
        endDate: '2017-05',
        description: 'Built high-throughput messaging infrastructure on the Infra team.',
      },
    ],
    behavioralSignals: [
      { type: 'Responsiveness', value: 'Replies < 4h', confidence: 0.92, source: 'Email graph' },
      { type: 'Availability', value: 'Open to offers', confidence: 0.81, source: 'Activity model' },
      { type: 'Mentorship', value: 'High signal', confidence: 0.77, source: 'Peer endorsements' },
    ],
    reasoning:
      'Linear Accelerator profile. 7-year upward trajectory in high-throughput system architecture across fintech and AI infra. Strong peer-graph overlap with the current Infra team (92% cultural alignment predicted).',
    rankings: [
      { jobId: 'job-101', jobTitle: 'Principal Platform Engineer', rank: 1, score: 98.4, reasoning: 'Top driver: domain expertise consistency.' },
    ],
  },
  {
    id: 'cand-002',
    name: 'Alex Rivera',
    email: 'alex.rivera@orbital.dev',
    currentRole: 'Principal SDE',
    company: 'Orbital Labs',
    location: 'Seattle, WA',
    overallScore: 98.2,
    dimensions: dims(92, 85, 86, 90, 72, 88, 64),
    skills: [
      { name: 'Rust', category: 'Languages', proficiency: 92, yearsOfExperience: 6 },
      { name: 'Systems Design', category: 'Architecture', proficiency: 94, yearsOfExperience: 10 },
      { name: 'Postgres', category: 'Data', proficiency: 89, yearsOfExperience: 9 },
      { name: 'Observability', category: 'Infra', proficiency: 85, yearsOfExperience: 5 },
    ],
    experience: [
      { title: 'Principal SDE', company: 'Orbital Labs', startDate: '2020-01', endDate: null, description: 'Strategic architect for the data plane; high-velocity learner.' },
      { title: 'Staff Engineer', company: 'Amazon', startDate: '2015-04', endDate: '2019-12', description: 'Owned a tier-1 service powering checkout.' },
    ],
    behavioralSignals: [
      { type: 'Responsiveness', value: 'Replies < 8h', confidence: 0.88, source: 'Email graph' },
      { type: 'Availability', value: 'Passive', confidence: 0.6, source: 'Activity model' },
    ],
    reasoning: 'Strategic architect with high-velocity learning signal. 85% skill overlap, 94.1% future-fit.',
    rankings: [{ jobId: 'job-101', jobTitle: 'Principal Platform Engineer', rank: 2, score: 98.2, reasoning: 'Exceptional execution dimension.' }],
  },
  {
    id: 'cand-003',
    name: 'Sam Chen',
    email: 'sam.chen@vectorize.io',
    currentRole: 'Senior Engineer',
    company: 'Vectorize',
    location: 'Remote',
    overallScore: 92.4,
    dimensions: dims(84, 92, 80, 86, 90, 82, 88),
    skills: [
      { name: 'Python', category: 'Languages', proficiency: 94, yearsOfExperience: 8 },
      { name: 'PyTorch', category: 'AI', proficiency: 90, yearsOfExperience: 5 },
      { name: 'Vector DBs', category: 'Data', proficiency: 88, yearsOfExperience: 3 },
      { name: 'CUDA', category: 'AI', proficiency: 80, yearsOfExperience: 4 },
    ],
    experience: [
      { title: 'Senior Engineer', company: 'Vectorize', startDate: '2019-08', endDate: null, description: 'Deep-tech IC building retrieval infrastructure.' },
      { title: 'ML Engineer', company: 'Cohere', startDate: '2016-09', endDate: '2019-07', description: 'Trained and served embedding models.' },
    ],
    behavioralSignals: [
      { type: 'Responsiveness', value: 'Replies < 24h', confidence: 0.7, source: 'Email graph' },
      { type: 'Open source', value: 'Active maintainer', confidence: 0.9, source: 'GitHub graph' },
    ],
    reasoning: 'Strong individual contributor, deep-tech specialist. 92% skill overlap is the highest in the pool.',
    rankings: [{ jobId: 'job-101', jobTitle: 'Principal Platform Engineer', rank: 3, score: 92.4, reasoning: 'Highest raw skill overlap.' }],
  },
  {
    id: 'cand-004',
    name: 'Jordan Smyth',
    email: 'jordan.smyth@kernel.systems',
    currentRole: 'Staff Engineer',
    company: 'Kernel Systems',
    location: 'Austin, TX',
    overallScore: 89.1,
    dimensions: dims(86, 78, 84, 92, 80, 76, 60),
    skills: [
      { name: 'C++', category: 'Languages', proficiency: 91, yearsOfExperience: 12 },
      { name: 'Linux Kernel', category: 'Systems', proficiency: 89, yearsOfExperience: 10 },
      { name: 'gRPC', category: 'Architecture', proficiency: 84, yearsOfExperience: 7 },
    ],
    experience: [
      { title: 'Staff Engineer', company: 'Kernel Systems', startDate: '2018-02', endDate: null, description: 'High ownership, multi-team lead experience.' },
    ],
    behavioralSignals: [{ type: 'Leadership', value: 'Multi-team lead', confidence: 0.85, source: 'Org graph' }],
    reasoning: 'High ownership with multi-team lead experience across 15 years.',
    rankings: [{ jobId: 'job-101', jobTitle: 'Principal Platform Engineer', rank: 4, score: 89.1, reasoning: 'Leadership breadth.' }],
  },
  {
    id: 'cand-005',
    name: 'Priya Nair',
    email: 'priya.nair@lumen.ai',
    currentRole: 'ML Platform Lead',
    company: 'Lumen AI',
    location: 'Bengaluru, IN',
    overallScore: 87.6,
    dimensions: dims(83, 80, 88, 84, 94, 78, 66),
    skills: [
      { name: 'Kubernetes', category: 'Infra', proficiency: 88, yearsOfExperience: 6 },
      { name: 'Ray', category: 'AI', proficiency: 82, yearsOfExperience: 3 },
      { name: 'Python', category: 'Languages', proficiency: 90, yearsOfExperience: 9 },
    ],
    experience: [{ title: 'ML Platform Lead', company: 'Lumen AI', startDate: '2020-05', endDate: null, description: 'Built the internal training platform from zero to 400 users.' }],
    behavioralSignals: [{ type: 'Availability', value: 'Open to offers', confidence: 0.86, source: 'Activity model' }],
    reasoning: 'Platform builder with strong culture-fit and collaboration markers.',
    rankings: [{ jobId: 'job-101', jobTitle: 'Principal Platform Engineer', rank: 5, score: 87.6, reasoning: 'Platform-from-zero track record.' }],
  },
  {
    id: 'cand-006',
    name: 'Diego Fernández',
    email: 'diego.f@flux.engineering',
    currentRole: 'Senior Backend Engineer',
    company: 'Flux',
    location: 'Lisbon, PT',
    overallScore: 84.3,
    dimensions: dims(81, 76, 82, 80, 70, 74, 52),
    skills: [
      { name: 'Elixir', category: 'Languages', proficiency: 89, yearsOfExperience: 5 },
      { name: 'PostgreSQL', category: 'Data', proficiency: 86, yearsOfExperience: 8 },
      { name: 'Kafka', category: 'Infra', proficiency: 80, yearsOfExperience: 4 },
    ],
    experience: [{ title: 'Senior Backend Engineer', company: 'Flux', startDate: '2019-11', endDate: null, description: 'Event-driven payments backend at scale.' }],
    behavioralSignals: [{ type: 'Responsiveness', value: 'Replies < 12h', confidence: 0.74, source: 'Email graph' }],
    reasoning: 'Reliable execution-heavy backend engineer; growth potential trending up.',
    rankings: [{ jobId: 'job-101', jobTitle: 'Principal Platform Engineer', rank: 6, score: 84.3, reasoning: 'Consistent delivery signal.' }],
  },
];

function rankedFrom(c: Candidate, rank: number): RankedCandidate {
  return {
    candidateId: c.id,
    candidateName: c.name,
    currentRole: c.currentRole,
    company: c.company,
    rank,
    score: c.overallScore,
    scoreBreakdown: {
      skillMatch: c.dimensions.skillMatch,
      experience: c.dimensions.experience,
      culturalFit: c.dimensions.education,
      growthPotential: c.dimensions.domain,
      behavioralFit: c.dimensions.behavioral,
    },
    reasoning: c.reasoning,
  };
}

const pipelineSteps = (allDone = true) => [
  { name: 'JD Upload', status: 'completed' as const, duration: 120, details: 'Parsed job description' },
  { name: 'Skill Extraction', status: allDone ? ('completed' as const) : ('running' as const), duration: 340, details: '30 skills extracted' },
  { name: 'Graph Expansion', status: allDone ? ('completed' as const) : ('pending' as const), duration: 210, details: 'Ontology-expanded skills' },
  { name: 'Hybrid Retrieval', status: allDone ? ('completed' as const) : ('pending' as const), duration: 890, details: '12.4k candidates retrieved' },
  { name: 'AI Ranking', status: allDone ? ('completed' as const) : ('pending' as const), duration: 1420, details: 'LTR model v4.2' },
  { name: 'Explainability', status: allDone ? ('completed' as const) : ('pending' as const), duration: 142, details: 'Per-candidate reasoning' },
];

export const demoRankings: RankingResult[] = [
  {
    id: 'rank-001',
    jobId: 'job-101',
    jobTitle: 'Principal Platform Engineer',
    jobDescription: 'Own the real-time inference platform; geo-redundant data plane; Rust + K8s.',
    criteria: {
      requiredSkills: ['Rust', 'Distributed Systems', 'Kubernetes'],
      preferredSkills: ['LLM Ops', 'Go'],
      minExperience: 8,
      maxExperience: null,
      location: 'San Francisco, CA',
      remote: true,
    },
    status: 'completed',
    createdAt: '2024-11-24T14:22:11Z',
    completedAt: '2024-11-24T14:22:14Z',
    results: demoCandidates.map((c, i) => rankedFrom(c, i + 1)),
    pipelineSteps: pipelineSteps(true),
  },
  {
    id: 'rank-002',
    jobId: 'job-102',
    jobTitle: 'Senior ML Infrastructure Engineer',
    jobDescription: 'Scale the training platform; Ray, K8s, Python.',
    criteria: {
      requiredSkills: ['Python', 'Kubernetes', 'Ray'],
      preferredSkills: ['PyTorch'],
      minExperience: 5,
      maxExperience: null,
      location: null,
      remote: true,
    },
    status: 'processing',
    createdAt: '2024-11-24T15:05:00Z',
    completedAt: null,
    results: demoCandidates.slice(2, 6).map((c, i) => rankedFrom(c, i + 1)),
    pipelineSteps: pipelineSteps(false),
  },
  {
    id: 'rank-003',
    jobId: 'job-103',
    jobTitle: 'Founding Backend Engineer',
    jobDescription: 'Greenfield event-driven backend; Elixir or Go.',
    criteria: {
      requiredSkills: ['Go', 'PostgreSQL'],
      preferredSkills: ['Kafka', 'Elixir'],
      minExperience: 4,
      maxExperience: 12,
      location: 'Remote',
      remote: true,
    },
    status: 'completed',
    createdAt: '2024-11-23T09:12:00Z',
    completedAt: '2024-11-23T09:12:05Z',
    results: demoCandidates.slice(3).map((c, i) => rankedFrom(c, i + 1)),
    pipelineSteps: pipelineSteps(true),
  },
];

export const demoMetrics: SystemMetrics = {
  totalCandidates: 100_000,
  uptimeSeconds: 0,
  memoryUsageMb: 0,
};

export function paginate(items: Candidate[], page: number, limit: number) {
  const start = (page - 1) * limit;
  return {
    candidates: items.slice(start, start + limit),
    total: items.length,
    page,
    totalPages: Math.max(1, Math.ceil(items.length / limit)),
  };
}
