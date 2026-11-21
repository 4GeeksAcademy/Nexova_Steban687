"""
Tests for SelectionService — validates core business logic of candidate scoring,
job matching, interview scheduling, and communication triggers.
"""

import pytest
from services.selection.service import (
    SelectionService,
    Candidate,
    JobPosition,
    ScoreResult,
    ValidationError,
    NotFoundError,
)


@pytest.fixture
def service():
    return SelectionService()


@pytest.fixture
def sample_candidate():
    return Candidate(
        id="cand-001",
        first_name="Ana",
        last_name="Martínez",
        email="ana.martinez@email.com",
        skills=["Python", "SQL", "Machine Learning", "B2B Sales", "English"],
        languages=[{"language": "Spanish", "level": "native"}, {"language": "English", "level": "C1"}],
        experience_years=6.0,
        current_role="Senior Data Scientist",
    )


@pytest.fixture
def sample_job():
    return JobPosition(
        id="job-001",
        title="Data Science Lead",
        department="Technology",
        description="Lead a team of data scientists to build ML models for client solutions.",
        required_skills=["Python", "Machine Learning", "SQL", "Team Leadership"],
        preferred_skills=["B2B Sales", "Cloud Computing"],
        experience_min=4,
        location="Valencia, Spain",
        client_id="client-001",
    )


class TestCandidateManagement:
    def test_register_candidate(self, service, sample_candidate):
        result = service.register_candidate(sample_candidate)
        assert result.id == "cand-001"
        assert result.status == "new"

    def test_register_duplicate_candidate(self, service, sample_candidate):
        service.register_candidate(sample_candidate)
        with pytest.raises(ValidationError, match="already exists"):
            service.register_candidate(sample_candidate)

    def test_register_candidate_no_email(self, service):
        with pytest.raises(ValidationError, match="email is required"):
            service.register_candidate(Candidate(id="cand-x", first_name="No", last_name="Email", email=""))

    def test_get_candidate_not_found(self, service):
        with pytest.raises(NotFoundError, match="Candidate"):
            service.get_candidate("nonexistent")

    def test_update_candidate_status_invalid(self, service, sample_candidate):
        service.register_candidate(sample_candidate)
        with pytest.raises(ValidationError, match="Invalid status"):
            service.update_candidate_status("cand-001", "invalid_status")

    def test_candidate_lifecycle(self, service, sample_candidate):
        service.register_candidate(sample_candidate)
        statuses = ["screening", "interview_scheduled", "interviewed", "shortlisted", "hired"]
        for s in statuses:
            c = service.update_candidate_status("cand-001", s)
            assert c.status == s


class TestJobManagement:
    def test_create_job(self, service, sample_job):
        result = service.create_job(sample_job)
        assert result.id == "job-001"
        assert result.title == "Data Science Lead"

    def test_create_job_no_title(self, service):
        with pytest.raises(ValidationError, match="title is required"):
            service.create_job(JobPosition(id="job-x", title="", department="", description=""))

    def test_get_job_not_found(self, service):
        with pytest.raises(NotFoundError, match="JobPosition"):
            service.get_job("nonexistent")


class TestScoringAndMatching:
    def test_score_candidate(self, service, sample_candidate, sample_job):
        service.register_candidate(sample_candidate)
        service.create_job(sample_job)
        result = service.score_candidate_for_job("cand-001", "job-001")
        
        assert isinstance(result, ScoreResult)
        assert result.candidate_id == "cand-001"
        assert result.job_id == "job-001"
        assert 0 <= result.score <= 100
        assert result.explanation
        assert "skill_match" in result.feature_importance
        assert "experience_match" in result.feature_importance

    def test_score_high_skill_match(self, service, sample_job):
        perfect = Candidate(
            id="cand-perfect",
            first_name="Perfect",
            last_name="Match",
            email="perfect@test.com",
            skills=["Python", "Machine Learning", "SQL", "Team Leadership"],
            experience_years=8.0,
        )
        service.register_candidate(perfect)
        service.create_job(sample_job)
        result = service.score_candidate_for_job("cand-perfect", "job-001")
        assert result.score >= 80.0

    def test_score_low_skill_match(self, service, sample_job):
        poor = Candidate(
            id="cand-poor",
            first_name="Poor",
            last_name="Match",
            email="poor@test.com",
            skills=["Cooking", "Gardening"],
            experience_years=1.0,
        )
        service.register_candidate(poor)
        service.create_job(sample_job)
        result = service.score_candidate_for_job("cand-poor", "job-001")
        assert result.score < 50.0

    def test_match_candidates_to_job_returns_ranked(self, service, sample_job):
        # Register candidates with varying match quality
        candidates = [
            Candidate(id=f"cand-{i}", first_name=f"Test{i}", last_name=f"User{i}",
                      email=f"test{i}@email.com",
                      skills=sample_job.required_skills[:i+1],
                      experience_years=2.0 * (i + 1))
            for i in range(3)
        ]
        for c in candidates:
            service.register_candidate(c)
        service.create_job(sample_job)

        results = service.match_candidates_to_job("job-001", top_k=2)
        assert len(results) <= 2
        # Verify descending order
        for i in range(len(results) - 1):
            assert results[i].score >= results[i + 1].score

    def test_match_no_candidates(self, service, sample_job):
        service.create_job(sample_job)
        results = service.match_candidates_to_job("job-001")
        assert results == []


class TestInterviewScheduling:
    def test_schedule_interview(self, service, sample_candidate, sample_job):
        service.register_candidate(sample_candidate)
        service.create_job(sample_job)
        result = service.schedule_interview(
            "cand-001", "job-001", "2026-12-15T10:00:00", "video"
        )
        assert result["status"] == "scheduled"
        assert "interview_id" in result

    def test_schedule_invalid_type(self, service, sample_candidate, sample_job):
        service.register_candidate(sample_candidate)
        service.create_job(sample_job)
        with pytest.raises(ValidationError, match="Invalid interview type"):
            service.schedule_interview("cand-001", "job-001", "2026-12-15T10:00:00", "invalid")


class TestCommunicationTrigger:
    def test_pending_communications(self, service, sample_candidate):
        service.register_candidate(sample_candidate)
        pending = service.get_pending_communications()
        assert len(pending) == 1
        assert pending[0]["candidate_id"] == "cand-001"
        assert pending[0]["email"] == "ana.martinez@email.com"

    def test_no_pending_for_hired(self, service, sample_candidate):
        service.register_candidate(sample_candidate)
        service.update_candidate_status("cand-001", "hired")
        pending = service.get_pending_communications()
        assert len(pending) == 0