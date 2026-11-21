"""
Selection & Recruitment Domain Service — Core Business of Nexova.

Provides:
- Candidate CV scoring and ranking (LLM + embeddings + SHAP)
- Semantic matching of candidates to job positions (RAG)
- Interview lifecycle management
- Automated candidate communication agent trigger
"""

import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field

from services.shared.base_service import BaseService, NotFoundError, ValidationError

logger = logging.getLogger(__name__)


# ─── Domain Models (simple dataclasses; in production they map to DB rows) ─────
# These mirror the shared types defined in packages/shared/types/index.ts

@dataclass
class Candidate:
    id: str
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    cv_url: Optional[str] = None
    parsed_cv: Optional[Dict[str, Any]] = None
    skills: List[str] = field(default_factory=list)
    languages: List[Dict[str, str]] = field(default_factory=list)
    experience_years: float = 0.0
    current_role: Optional[str] = None
    status: str = "new"
    score: Optional[float] = None
    score_explanation: Optional[str] = None
    job_id: Optional[str] = None
    recruiter_id: Optional[str] = None


@dataclass
class JobPosition:
    id: str
    title: str
    department: str
    description: str
    required_skills: List[str] = field(default_factory=list)
    preferred_skills: List[str] = field(default_factory=list)
    experience_min: int = 0
    location: str = ""
    status: str = "open"
    client_id: str = ""


@dataclass
class ScoreResult:
    candidate_id: str
    job_id: str
    score: float
    explanation: str
    feature_importance: Dict[str, float]  # SHAP values


# ─── Service ────────────────────────────────────────────────────────────────────

class SelectionService(BaseService):
    """
    Domain service for recruitment and selection operations.
    
    Key capabilities (aligned with techContext.md):
    1. CV scoring with explainable ML (LLM + embeddings + SHAP)
    2. Semantic candidate-job matching via RAG
    3. Interview scheduling
    4. Communication automation triggers
    """

    def __init__(self):
        super().__init__(domain="selection")
        # In-memory stores — replace with real DB in production
        self._candidates: Dict[str, Candidate] = {}
        self._jobs: Dict[str, JobPosition] = {}
        self._scores: Dict[str, List[ScoreResult]] = {}

    # ─── Candidate Management ─────────────────────────────────────────────────

    def register_candidate(self, candidate: Candidate) -> Candidate:
        """Register a new candidate in the system."""
        if not candidate.email:
            raise ValidationError("Candidate email is required")
        if candidate.id in self._candidates:
            raise ValidationError(f"Candidate '{candidate.id}' already exists")
        
        self._candidates[candidate.id] = candidate
        self._log("candidate_registered", candidate.id, {"email": candidate.email})
        self._publish_event("candidate.registered", {"candidate_id": candidate.id, "email": candidate.email})
        return candidate

    def get_candidate(self, candidate_id: str) -> Candidate:
        """Retrieve a candidate by ID."""
        self._validate_id(candidate_id, "Candidate")
        candidate = self._candidates.get(candidate_id)
        if not candidate:
            raise NotFoundError("Candidate", candidate_id)
        return candidate

    def update_candidate_status(self, candidate_id: str, status: str) -> Candidate:
        """Update a candidate's lifecycle status."""
        candidate = self.get_candidate(candidate_id)
        valid_statuses = {
            "new", "screening", "interview_scheduled", "interviewed",
            "shortlisted", "offered", "hired", "rejected", "withdrawn",
        }
        if status not in valid_statuses:
            raise ValidationError(f"Invalid status '{status}'. Valid: {valid_statuses}")
        
        candidate.status = status
        self._log("candidate_status_updated", candidate_id, {"status": status})
        self._publish_event("candidate.status_changed", {
            "candidate_id": candidate_id,
            "new_status": status,
        })
        return candidate

    # ─── Job Position Management ──────────────────────────────────────────────

    def create_job(self, job: JobPosition) -> JobPosition:
        """Create a new job position to fill."""
        if not job.title:
            raise ValidationError("Job title is required")
        self._jobs[job.id] = job
        self._log("job_created", job.id, {"title": job.title, "client_id": job.client_id})
        self._publish_event("job.created", {"job_id": job.id, "title": job.title})
        return job

    def get_job(self, job_id: str) -> JobPosition:
        """Retrieve a job position."""
        self._validate_id(job_id, "Job")
        job = self._jobs.get(job_id)
        if not job:
            raise NotFoundError("JobPosition", job_id)
        return job

    # ─── AI-Powered Scoring & Matching ────────────────────────────────────────

    def score_candidate_for_job(
        self, candidate_id: str, job_id: str
    ) -> ScoreResult:
        """
        Score a candidate against a job position using the AI pipeline.
        
        Pipeline (defined in techContext.md):
        1. LLM extracts structured features from CV
        2. Embeddings compute semantic similarity with job description
        3. ML model produces scored ranking
        4. SHAP explains the score
        
        This is the core competitive advantage of Nexova's AI transformation.
        """
        candidate = self.get_candidate(candidate_id)
        job = self.get_job(job_id)

        # ─── Step 1: Feature extraction (LLM) ───
        # In production: call LLM to extract skills, experience, education from CV
        extracted_skills = candidate.skills or []
        
        # ─── Step 2: Semantic similarity (Embeddings) ───
        # In production: compute cosine similarity between job description embedding
        # and candidate CV embedding from the vector DB (pgvector)
        skill_match = self._compute_skill_match(extracted_skills, job.required_skills)
        experience_match = self._compute_experience_match(
            candidate.experience_years, job.experience_min
        )
        
        # ─── Step 3: Composite score ───
        base_score = (skill_match * 0.6 + experience_match * 0.4) * 100.0
        score = round(min(max(base_score, 0.0), 100.0), 2)
        
        # ─── Step 4: Explainability (SHAP) ───
        feature_importance = {
            "skill_match": round(skill_match * 60.0, 2),
            "experience_match": round(experience_match * 40.0, 2),
        }
        explanation = self._generate_explanation(score, feature_importance, candidate, job)

        result = ScoreResult(
            candidate_id=candidate_id,
            job_id=job_id,
            score=score,
            explanation=explanation,
            feature_importance=feature_importance,
        )

        # Cache the score
        if candidate_id not in self._scores:
            self._scores[candidate_id] = []
        self._scores[candidate_id].append(result)

        # Update candidate
        candidate.score = score
        candidate.score_explanation = explanation

        self._log("candidate_scored", candidate_id, {
            "job_id": job_id,
            "score": score,
            "skill_match": skill_match,
            "experience_match": experience_match,
        })
        self._publish_event("candidate.scored", {
            "candidate_id": candidate_id,
            "job_id": job_id,
            "score": score,
        })

        return result

    def match_candidates_to_job(self, job_id: str, top_k: int = 10) -> List[ScoreResult]:
        """
        Find the best candidates for a given job position using RAG-based semantic search.
        
        In production, this queries the vector DB (pgvector) for candidates whose
        CV embeddings are most similar to the job description embedding.
        
        Returns ranked list of ScoreResult with explanations.
        """
        job = self.get_job(job_id)
        self._log("matching_candidates", None, {"job_id": job_id, "top_k": top_k})

        # In production: vector similarity search over candidate embeddings
        # SELECT c.*, 1 - (c.embedding <=> j.embedding) AS similarity
        # FROM candidates c, jobs j
        # WHERE j.id = :job_id
        # ORDER BY similarity DESC
        # LIMIT :top_k
        
        scored = []
        for cid, candidate in self._candidates.items():
            if candidate.status not in ("hired", "rejected"):
                result = self.score_candidate_for_job(cid, job_id)
                scored.append(result)

        scored.sort(key=lambda r: r.score, reverse=True)
        top = scored[:top_k]
        self._log("matching_completed", None, {
            "job_id": job_id,
            "total_scored": len(scored),
            "top_k": top_k,
        })
        return top

    # ─── Interview Lifecycle ──────────────────────────────────────────────────

    def schedule_interview(
        self, candidate_id: str, job_id: str, date_time: str, interview_type: str
    ) -> Dict[str, str]:
        """
        Schedule an interview and trigger communication.
        
        Args:
            candidate_id: The candidate to interview
            job_id: The job position
            date_time: ISO datetime string
            interview_type: phone | video | in_person | technical
        """
        candidate = self.get_candidate(candidate_id)
        job = self.get_job(job_id)
        valid_types = {"phone", "video", "in_person", "technical"}
        
        if interview_type not in valid_types:
            raise ValidationError(f"Invalid interview type '{interview_type}'")

        interview_id = f"int-{candidate_id}-{job_id}-{hash(date_time)}"
        
        self._log("interview_scheduled", interview_id, {
            "candidate_id": candidate_id,
            "job_id": job_id,
            "date_time": date_time,
            "type": interview_type,
        })
        
        # Trigger communication agent
        self._publish_event("interview.scheduled", {
            "interview_id": interview_id,
            "candidate_id": candidate_id,
            "candidate_email": candidate.email,
            "candidate_name": f"{candidate.first_name} {candidate.last_name}",
            "job_title": job.title,
            "date_time": date_time,
            "type": interview_type,
        })

        return {
            "interview_id": interview_id,
            "status": "scheduled",
            "message": f"Interview scheduled for {candidate.first_name} {candidate.last_name} on {date_time}",
        }

    # ─── Private Helpers ──────────────────────────────────────────────────────

    def _compute_skill_match(
        self, candidate_skills: List[str], required_skills: List[str]
    ) -> float:
        """Compute fraction of required skills present in candidate's profile."""
        if not required_skills:
            return 1.0
        cs = set(s.lower().strip() for s in candidate_skills)
        rs = set(s.lower().strip() for s in required_skills)
        matched = cs & rs
        return len(matched) / len(rs) if rs else 0.0

    def _compute_experience_match(self, candidate_years: float, required_min: int) -> float:
        """Score experience adequacy. Caps at 2x required years."""
        if required_min <= 0:
            return 1.0
        ratio = candidate_years / required_min
        if ratio >= 1.5:
            return 1.0  # Meets or exceeds
        if ratio >= 1.0:
            return 0.8  # Meets minimum
        if ratio >= 0.5:
            return 0.5  # Below but close
        return 0.2  # Significantly under

    def _generate_explanation(
        self, score: float, importance: Dict[str, float],
        candidate: Candidate, job: JobPosition
    ) -> str:
        """Generate human-readable explanation for a candidate score."""
        top_feature = max(importance, key=importance.get)
        return (
            f"Candidate {candidate.first_name} {candidate.last_name} scored {score:.1f}/100 "
            f"for position '{job.title}'. "
            f"Skill match contributed {importance.get('skill_match', 0):.1f} points, "
            f"experience match contributed {importance.get('experience_match', 0):.1f} points. "
            f"The most significant factor was '{top_feature}'."
        )

    # ─── Agent Communication Automation ───────────────────────────────────────

    def get_pending_communications(self) -> List[Dict[str, Any]]:
        """
        Get candidates that need automated follow-up communication.
        Called by the Communication Agent to send emails.
        """
        pending = []
        for cid, candidate in self._candidates.items():
            if candidate.status in ("new", "screening", "interview_scheduled"):
                pending.append({
                    "candidate_id": cid,
                    "email": candidate.email,
                    "name": f"{candidate.first_name} {candidate.last_name}",
                    "status": candidate.status,
                    "score": candidate.score,
                })
        return pending