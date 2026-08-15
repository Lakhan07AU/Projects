export type SeniorityLevel = 'junior' | 'mid' | 'senior' | 'staff';

export type InterviewType = 
  | 'technical' 
  | 'system_design' 
  | 'behavioral' 
  | 'live_problem' 
  | 'mixed';

export type InterviewerPersona = 
  | 'faang_strict' 
  | 'encouraging_coach' 
  | 'startup_cto' 
  | 'behavioral_expert';

export interface RolePreset {
  id: string;
  title: string;
  category: 'engineering' | 'ai_data' | 'product_design' | 'operations';
  description: string;
  iconName: string;
  suggestedSkills: string[];
  sampleQuestions: string[];
}

export interface InterviewConfig {
  roleId: string;
  customRoleTitle?: string;
  seniority: SeniorityLevel;
  interviewType: InterviewType;
  interviewerPersona: InterviewerPersona;
  totalQuestions: number;
  companyTarget?: string;
}

export interface MetricScore {
  name: string;
  score: number; // 0 - 100
  feedback: string;
}

export interface AnswerEvaluation {
  score: number; // 0 - 100
  verdict: 'Strong Hire' | 'Hire' | 'Leaning Hire' | 'Needs Improvement' | 'Did Not Meet Bar';
  metrics: {
    technicalAccuracy: number;
    clarityAndStructure: number;
    depthAndRelevance: number;
    problemSolvingOrSTAR: number;
  };
  strengths: string[];
  areasForImprovement: string[];
  missedKeyPoints: string[];
  exemplaryAnswer: string;
  interviewerComment: string;
}

export interface InterviewTurn {
  questionNumber: number;
  question: string;
  category: string;
  difficulty: 'Standard' | 'Challenging' | 'Deep Dive';
  contextTip?: string;
  userAnswer?: string;
  evaluation?: AnswerEvaluation;
  timeSpentSeconds?: number;
}

export interface FinalReport {
  overallScore: number;
  overallVerdict: 'Strong Hire' | 'Hire' | 'Leaning Hire' | 'Needs Improvement';
  summaryAssessment: string;
  competencyBreakdown: {
    category: string;
    score: number;
    summary: string;
  }[];
  topStrengths: string[];
  topGrowthAreas: string[];
  tailoredStudyPlan: {
    week: string;
    focus: string;
    actionItems: string[];
  }[];
  hiringManagerNotes: string;
}

export interface SavedInterviewSession {
  id: string;
  timestamp: number;
  config: InterviewConfig;
  turns: InterviewTurn[];
  report?: FinalReport;
  durationSeconds: number;
}
