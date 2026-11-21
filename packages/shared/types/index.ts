/**
 * Shared types for Nexova Solutions — AI Engineering Project
 * Domain types for all 8 departments of the HR & talent consulting company.
 */

// ─── Core ─────────────────────────────────────────────────────
export type Id = string;

export interface BaseEntity {
  id: Id;
  createdAt?: string;
  updatedAt?: string;
}

// ─── Common Enums ──────────────────────────────────────────────
export type Language = 'es' | 'en';
export type Status = 'active' | 'inactive' | 'archived';
export type Priority = 'low' | 'medium' | 'high' | 'critical';

// ─── Selection / Recruitment (Core Business) ──────────────────
export type CandidateStatus =
  | 'new' | 'screening' | 'interview_scheduled' | 'interviewed'
  | 'shortlisted' | 'offered' | 'hired' | 'rejected' | 'withdrawn';

export interface Candidate extends BaseEntity {
  firstName: string;
  lastName: string;
  email: string;
  phone?: string;
  cvUrl?: string;
  parsedCv?: Record<string, unknown>;
  skills: string[];
  languages: { language: string; level: string }[];
  experienceYears: number;
  currentRole?: string;
  status: CandidateStatus;
  score?: number;
  scoreExplanation?: string;
  jobId?: Id;
  recruiterId?: Id;
}

export interface JobPosition extends BaseEntity {
  title: string;
  department: string;
  description: string;
  requiredSkills: string[];
  preferredSkills: string[];
  experienceMin: number;
  location: string;
  status: 'open' | 'closed' | 'on_hold';
  clientId: Id;
}

export interface Interview extends BaseEntity {
  candidateId: Id;
  jobId: Id;
  dateTime: string;
  type: 'phone' | 'video' | 'in_person' | 'technical';
  feedback?: string;
  rating?: number;
  nextStep?: string;
}

// ─── Training / Corporate Education ────────────────────────────
export type CourseStatus = 'draft' | 'published' | 'cancelled' | 'completed';
export type EnrollmentStatus = 'pending' | 'confirmed' | 'cancelled' | 'attended';

export interface Course extends BaseEntity {
  code: string;
  title: string;
  description: string;
  category: string;
  modality: 'online' | 'in_person' | 'hybrid';
  durationHours: number;
  maxCapacity: number;
  price?: number;
  status: CourseStatus;
  language: Language;
  syllabus?: string[];
}

export interface Enrollment extends BaseEntity {
  courseId: Id;
  clientId: Id;
  studentName: string;
  studentEmail: string;
  status: EnrollmentStatus;
  progressPercent: number;
  completedModules: string[];
}

export interface TrainingRecommendation extends BaseEntity {
  clientId: Id;
  clientProfile: Record<string, unknown>;
  recommendedCourseIds: Id[];
  rationale: string;
  generatedBy: 'system' | 'agent';
}

// ─── Customer Support (Outsourcing) ────────────────────────────
export type TicketStatus = 'open' | 'in_progress' | 'waiting_client' | 'resolved' | 'escalated';
export type TicketChannel = 'phone' | 'email' | 'chat' | 'web';

export interface SupportTicket extends BaseEntity {
  clientId: Id;
  subject: string;
  description: string;
  channel: TicketChannel;
  status: TicketStatus;
  priority: Priority;
  assignedAgentId?: Id;
  slaDeadline?: string;
  resolvedAt?: string;
  sentimentScore?: number;
  sentimentLabel?: 'positive' | 'neutral' | 'negative';
  firstResponseTimeMinutes?: number;
}

export interface KnowledgeArticle extends BaseEntity {
  title: string;
  content: string;
  category: string;
  tags: string[];
  embedding?: number[];
  language: Language;
  version: number;
}

// ─── Sales / Business Development ──────────────────────────────
export type LeadStatus = 'new' | 'contacted' | 'qualified' | 'proposal' | 'negotiation' | 'won' | 'lost';
export type PipelineStage = 'discovery' | 'demo' | 'proposal' | 'closing';

export interface Lead extends BaseEntity {
  companyName: string;
  contactName: string;
  contactEmail: string;
  contactPhone?: string;
  source: string;
  status: LeadStatus;
  pipelineStage?: PipelineStage;
  estimatedValue?: number;
  probability?: number;  // 0-100
  assignedTo: Id;
  lastContactAt?: string;
  nextFollowUp?: string;
  notes?: string;
  suggestedAngle?: string;  // AI-generated
}

export interface ProspectingSequence extends BaseEntity {
  leadId: Id;
  steps: { order: number; action: string; delayDays: number; completed: boolean }[];
  currentStep: number;
  status: 'active' | 'paused' | 'completed' | 'abandoned';
}

// ─── HR (Internal) ─────────────────────────────────────────────
export type LeaveType = 'vacation' | 'sick' | 'personal' | 'other';
export type LeaveStatus = 'pending' | 'approved' | 'rejected';

export interface LeaveRequest extends BaseEntity {
  employeeId: Id;
  type: LeaveType;
  startDate: string;
  endDate: string;
  reason?: string;
  status: LeaveStatus;
  approvedBy?: Id;
}

export interface OnboardingTask extends BaseEntity {
  employeeId: Id;
  taskName: string;
  description: string;
  dueDaysAfterStart: number;
  completed: boolean;
  completedAt?: string;
  assignedDepartment: string;
}

export interface PerformanceReview extends BaseEntity {
  employeeId: Id;
  reviewerId: Id;
  period: string;  // e.g. "2026-H1"
  scores: { category: string; score: number; comment?: string }[];
  overallScore: number;
  status: 'draft' | 'submitted' | 'acknowledged';
}

// ─── Marketing ─────────────────────────────────────────────────
export interface MarketingMetrics extends BaseEntity {
  date: string;
  pageViews: number;
  uniqueVisitors: number;
  leadsGenerated: number;
  conversionRate: number;
  topSources: { source: string; count: number }[];
  campaignId?: Id;
}

export interface ContentPiece extends BaseEntity {
  title: string;
  type: 'blog' | 'newsletter' | 'landing' | 'social';
  content: string;
  seoKeywords: string[];
  schemaMarkup?: Record<string, unknown>;
  status: 'draft' | 'review' | 'published';
  publishedAt?: string;
  authorId: Id;
}

// ─── Executive Dashboard ───────────────────────────────────────
export interface ExecutiveKpi extends BaseEntity {
  area: 'selection' | 'training' | 'support' | 'sales' | 'hr' | 'marketing';
  metricName: string;
  metricValue: number;
  metricUnit: string;
  period: string;          // ISO week / month
  previousValue?: number;
  targetValue?: number;
  trend: 'up' | 'down' | 'flat';
}

export interface WeeklyReport extends BaseEntity {
  weekStart: string;
  weekEnd: string;
  generatedAt: string;
  summary: string;
  kpis: ExecutiveKpi[];
  alerts: { area: string; message: string; severity: 'info' | 'warning' | 'critical' }[];
  pdfUrl?: string;
}

// ─── Shared Service Responses ──────────────────────────────────
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  meta?: { total: number; page: number; pageSize: number };
}

export interface AgentMessage {
  role: 'system' | 'user' | 'assistant' | 'tool';
  content: string;
  toolCallId?: string;
  timestamp: string;
}
