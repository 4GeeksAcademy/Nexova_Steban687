"""
Tests for the Selection Communication Agent.

Validates:
- Template personalization
- Status-based communication triggers
- Interview confirmation flow
- Language detection (Spanish vs English)
- Follow-up logic
- Communication history
"""

import pytest
from agents.selection.agent import (
    SelectionCommunicationAgent,
    CommunicationRecord,
    TEMPLATES,
    run_agent_pipeline,
)


@pytest.fixture
def agent():
    return SelectionCommunicationAgent()


class TestTemplatePersonalization:
    def test_spanish_template_used_for_spanish_candidate(self, agent):
        record = agent.send_status_update(
            candidate_id="cand-001",
            candidate_name="Ana Martínez",
            candidate_email="ana@test.com",
            job_title="Data Scientist",
            new_status="new",
            language="es",
        )
        assert "Hola Ana Martínez" in record.body
        assert "Data Scientist" in record.body
        assert "Nexova" in record.body

    def test_english_template_used_for_english_candidate(self, agent):
        record = agent.send_status_update(
            candidate_id="cand-002",
            candidate_name="John Smith",
            candidate_email="john@test.com",
            job_title="Data Scientist",
            new_status="new",
            language="en",
        )
        assert "Dear John Smith" in record.body
        assert "Data Scientist" in record.body

    def test_template_contains_candidate_name(self, agent):
        record = agent.send_status_update(
            candidate_id="cand-003",
            candidate_name="Carlos López",
            candidate_email="carlos@test.com",
            job_title="UX Designer",
            new_status="shortlisted",
            language="es",
        )
        assert "Carlos López" in record.body
        assert "UX Designer" in record.body

    def test_fallback_to_english_when_unknown_language(self, agent):
        record = agent.send_status_update(
            candidate_id="cand-004",
            candidate_name="Test User",
            candidate_email="test@test.com",
            job_title="Engineer",
            new_status="new",
            language="fr",  # unsupported → fallback to en
        )
        assert "Dear Test User" in record.body


class TestStatusBasedCommunication:
    def test_new_candidate_gets_registration_email(self, agent):
        record = agent.send_status_update(
            candidate_id="cand-010",
            candidate_name="Lucía García",
            candidate_email="lucia@test.com",
            job_title="Backend Developer",
            new_status="new",
            language="en",
        )
        assert record.communication_type == "status_new"
        assert "applying" in record.body.lower() or "application" in record.body.lower()

    def test_shortlisted_candidate_gets_congratulations(self, agent):
        record = agent.send_status_update(
            candidate_id="cand-011",
            candidate_name="Pedro Ruiz",
            candidate_email="pedro@test.com",
            job_title="Frontend Developer",
            new_status="shortlisted",
            language="es",
        )
        assert "preseleccionado" in record.body or "shortlisted" in record.body.lower()

    def test_rejected_candidate_gets_feedback_email(self, agent):
        record = agent.send_status_update(
            candidate_id="cand-012",
            candidate_name="Marta Díaz",
            candidate_email="marta@test.com",
            job_title="DevOps Engineer",
            new_status="rejected",
            language="es",
        )
        assert "Gracias por el tiempo" in record.body

    def test_unknown_status_does_not_send_email(self, agent):
        record = agent.send_status_update(
            candidate_id="cand-013",
            candidate_name="Test User",
            candidate_email="test@test.com",
            job_title="Engineer",
            new_status="interviewed",  # no template for this
            language="en",
        )
        assert record.body == ""

    def test_status_map_has_all_needed_keys(self):
        needed = {"new", "shortlisted", "rejected"}
        existing_templates = set(TEMPLATES.keys())
        assert needed.issubset(existing_templates), (
            f"Missing templates for statuses: {needed - existing_templates}"
        )


class TestInterviewConfirmation:
    def test_interview_confirmation_contains_details(self, agent):
        record = agent.send_interview_confirmation(
            candidate_id="cand-020",
            candidate_name="Sofia Torres",
            candidate_email="sofia@test.com",
            job_title="Product Manager",
            interview_date="2026-12-15",
            interview_time="10:00",
            interview_type="video",
            location_or_link="https://meet.google.com/abc-def-ghi",
            language="en",
        )
        assert "2026-12-15" in record.body
        assert "10:00" in record.body
        assert "video" in record.body.lower()
        assert "meet.google.com" in record.body

    def test_interview_confirmation_spanish(self, agent):
        record = agent.send_interview_confirmation(
            candidate_id="cand-021",
            candidate_name="Jorge López",
            candidate_email="jorge@test.com",
            job_title="Analista de Datos",
            interview_date="15/12/2026",
            interview_time="11:30",
            interview_type="presencial",
            location_or_link="Calle Colón 12, Valencia",
            language="es",
        )
        assert "Entrevista confirmada" in record.subject
        assert "Calle Colón 12" in record.body


class TestFollowUp:
    def test_follow_up_contains_reminder_context(self, agent):
        record = agent.send_follow_up(
            candidate_id="cand-030",
            candidate_name="Elena Castro",
            candidate_email="elena@test.com",
            job_title="Data Analyst",
            language="en",
        )
        assert "reminder" in record.body.lower() or "waiting" in record.body.lower()
        assert "Data Analyst" in record.body

    def test_follow_up_spanish(self, agent):
        record = agent.send_follow_up(
            candidate_id="cand-031",
            candidate_name="Raúl Pérez",
            candidate_email="raul@test.com",
            job_title="Ingeniero de Software",
            language="es",
        )
        assert "Recordatorio" in record.subject


class TestLanguageDetection:
    def test_detect_spanish_from_languages(self, agent):
        languages = [
            {"language": "Spanish", "level": "native"},
            {"language": "English", "level": "C1"},
        ]
        assert agent.determine_language(languages) == "es"

    def test_detect_english_when_no_spanish(self, agent):
        languages = [
            {"language": "English", "level": "native"},
            {"language": "French", "level": "B2"},
        ]
        assert agent.determine_language(languages) == "en"

    def test_detect_spanish_low_level_returns_english(self, agent):
        languages = [
            {"language": "Spanish", "level": "A2"},
            {"language": "English", "level": "C1"},
        ]
        assert agent.determine_language(languages) == "en"


class TestCommunicationHistory:
    def test_history_records_communications(self, agent):
        agent.send_status_update("cand-050", "Test", "test@test.com", "Engineer", "new", "en")
        agent.send_status_update("cand-050", "Test", "test@test.com", "Engineer", "shortlisted", "en")
        history = agent.get_communication_history("cand-050")
        assert len(history) == 2

    def test_history_limited_to_past_communications(self, agent):
        # Send to different candidates
        agent.send_status_update("cand-a", "A", "a@test.com", "Engineer", "new", "en")
        agent.send_status_update("cand-b", "B", "b@test.com", "Engineer", "new", "en")
        agent.send_status_update("cand-a", "A", "a@test.com", "Engineer", "shortlisted", "en")
        
        history_a = agent.get_communication_history("cand-a")
        history_b = agent.get_communication_history("cand-b")
        assert len(history_a) == 2
        assert len(history_b) == 1

    def test_history_empty_for_unknown_candidate(self, agent):
        assert agent.get_communication_history("nonexistent") == []


class TestRecordStructure:
    def test_communication_record_has_all_fields(self, agent):
        record = agent.send_status_update(
            candidate_id="cand-060",
            candidate_name="Test User",
            candidate_email="test@test.com",
            job_title="Engineer",
            new_status="new",
            language="en",
        )
        assert record.id.startswith("comm-")
        assert record.sent_at is not None
        assert record.status == "sent"
        assert record.recipient_email == "test@test.com"
        assert record.candidate_id == "cand-060"


class TestFullPipeline:
    def test_pipeline_new_candidate(self):
        candidate = {
            "id": "cand-pipe-001",
            "name": "Pipeline Test",
            "email": "pipeline@test.com",
            "job_title": "ML Engineer",
            "status": "new",
            "languages": [{"language": "English", "level": "native"}],
        }
        records = run_agent_pipeline(candidate)
        assert len(records) == 1
        assert records[0].communication_type == "status_new"

    def test_pipeline_with_interview(self):
        candidate = {
            "id": "cand-pipe-002",
            "name": "Interview Pipeline",
            "email": "interview@test.com",
            "job_title": "Frontend Developer",
            "status": "interview_scheduled",
            "languages": [{"language": "Spanish", "level": "native"}],
            "interview_details": {
                "date": "2026-12-20",
                "time": "15:00",
                "type": "video",
                "location": "https://meet.google.com/xyz",
            },
        }
        records = run_agent_pipeline(candidate)
        assert len(records) == 2  # status + interview confirmation
        types = [r.communication_type for r in records]
        assert "interview_scheduled" in types

    def test_pipeline_rejected_candidate(self):
        candidate = {
            "id": "cand-pipe-003",
            "name": "Rejected Pipeline",
            "email": "rejected@test.com",
            "job_title": "Designer",
            "status": "rejected",
            "languages": [{"language": "English", "level": "native"}],
        }
        records = run_agent_pipeline(candidate)
        assert len(records) == 1
        assert records[0].communication_type == "status_rejected"