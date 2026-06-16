export interface Candidate {
  id: string;
  name: string;
  email: string;
  currentRole: string;
  company: string;
  location: string;
  overallScore: number;
  dimensions: TalentDimensions;
  skills: Skill[];
  experience: Experience[];
  behavioralSignals: BehavioralSignal[];
  reasoning: string;
  rankings: RankingEntry[];
}

export interface TalentDimensions {
  titleCareer: number;
  skillMatch: number;
  behavioral: number;
  experience: number;
  location: number;
  education: number;
  domain: number;
}

export interface Skill {
  name: string;
  category: string;
  proficiency: number;
  yearsOfExperience: number;
}

export interface Experience {
  title: string;
  company: string;
  startDate: string;
  endDate: string | null;
  description: string;
}

export interface BehavioralSignal {
  type: string;
  value: string;
  confidence: number;
  source: string;
}

export interface RankingEntry {
  jobId: string;
  jobTitle: string;
  rank: number;
  score: number;
  reasoning: string;
}

export interface RankingResult {
  id: string;
  jobId: string;
  jobTitle: string;
  jobDescription: string;
  criteria: RankingCriteria;
  status: RankingStatus;
  createdAt: string;
  completedAt: string | null;
  results: RankedCandidate[];
  pipelineSteps: PipelineStep[];
}

export interface RankingCriteria {
  requiredSkills: string[];
  preferredSkills: string[];
  minExperience: number;
  maxExperience: number | null;
  location: string | null;
  remote: boolean;
}

export type RankingStatus = 'queued' | 'processing' | 'completed' | 'failed';

export interface RankedCandidate {
  candidateId: string;
  candidateName: string;
  currentRole: string;
  company: string;
  rank: number;
  score: number;
  scoreBreakdown: ScoreBreakdown;
  reasoning: string;
}

export interface ScoreBreakdown {
  skillMatch: number;
  experience: number;
  culturalFit: number;
  growthPotential: number;
  behavioralFit: number;
}

export interface PipelineStep {
  name: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  duration: number | null;
  details: string;
}

export interface SystemMetrics {
  totalCandidates: number;
  uptimeSeconds: number;
  memoryUsageMb: number;
}
