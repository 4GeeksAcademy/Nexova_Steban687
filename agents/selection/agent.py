"""
Selection Communication Agent for Nexova Solutions.

Role: Automated email communication with candidates throughout the recruitment lifecycle.
Triggers: Candidate status changes, interview scheduling, follow-ups, and offer management.

This agent follows the monorepo agent template pattern with:
- Clear system prompt / role definition
- Tools that interact with the SelectionService
- Memory of past communications
- Evaluation and tests
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)


# ─── Agent Configuration ─────────────────────────────────────────────────────

AGENT_NAME = "selection-communication-agent"
AGENT_VERSION = "0.1.0"
AGENT_ROLE = "Communication Agent for the Selection & Recruitment domain"
AGENT_SYSTEM_PROMPT = """You are the Selection Communication Agent for Nexova Solutions.
Your job is to manage automated email communication with job candidates throughout the recruitment process.

Your responsibilities:
1. Send personalized follow-up emails when a candidate's status changes
2. Schedule and confirm interview appointments
3. Send reminders for upcoming interviews
4. Follow up with candidates who haven't responded within 48 hours
5. Send offer letters and manage offer acceptance/rejection
6. Notify candidates who were not selected (rejection with constructive feedback)

You MUST:
- Use a professional but warm tone in all communications
- Personalize each message with candidate name, job title, and company name
- Include relevant details (date, time, location, interview type) when confirming interviews
- Respect candidate preferences (language: Spanish or English)
- Log all communications for audit and evaluation

You MUST NOT:
- Share confidential information about other candidates
- Make promises about salary, benefits, or job offers without approval
- Contact candidates outside of business hours (9:00-18:00)
- Use templates without personalizing them
"""


# ─── Communication Templates ─────────────────────────────────────────────────

TEMPLATES: Dict[str, Dict[str, str]] = {
    "new": {
        "es": (
            "Asunto: {candidate_name}, gracias por tu interés en {job_title}\n\n"
            "Hola {candidate_name},\n\n"
            "Hemos recibido tu candidatura para el puesto de {job_title} en Nexova Solutions. "
            "Nuestro equipo está revisando tu perfil y te mantendremos informado sobre el progreso.\n\n"
            "Mientras tanto, puedes consultar el estado de tu candidatura en nuestro portal de candidatos.\n\n"
            "Saludos cordiales,\nEl equipo de Selección de Nexova"
        ),
        "en": (
            "Subject: {candidate_name}, thank you for applying to {job_title}\n\n"
            "Dear {candidate_name},\n\n"
            "We have received your application for the position of {job_title} at Nexova Solutions. "
            "Our team is reviewing your profile and we will keep you updated on the progress.\n\n"
            "In the meantime, you can check your application status on our candidate portal.\n\n"
            "Best regards,\nThe Nexova Selection Team"
        ),
    },
    "interview_scheduled": {
        "es": (
            "Asunto: Entrevista confirmada para {job_title}\n\n"
            "Hola {candidate_name},\n\n"
            "Nos complace confirmar tu entrevista para el puesto de {job_title}.\n\n"
            "Detalles:\n"
            "- Fecha: {date}\n"
            "- Hora: {time}\n"
            "- Tipo: {interview_type}\n"
            "- Lugar/Enlace: {location_or_link}\n\n"
            "Por favor, confirma tu asistencia respondiendo a este correo.\n\n"
            "Saludos cordiales,\nEl equipo de Selección de Nexova"
        ),
        "en": (
            "Subject: Interview confirmed for {job_title}\n\n"
            "Dear {candidate_name},\n\n"
            "We are pleased to confirm your interview for the position of {job_title}.\n\n"
            "Details:\n"
            "- Date: {date}\n"
            "- Time: {time}\n"
            "- Type: {interview_type}\n"
            "- Location/Link: {location_or_link}\n\n"
            "Please confirm your attendance by replying to this email.\n\n"
            "Best regards,\nThe Nexova Selection Team"
        ),
    },
    "shortlisted": {
        "es": (
            "Asunto: Buenas noticias, {candidate_name} — has pasado a la siguiente fase\n\n"
            "Hola {candidate_name},\n\n"
            "¡Enhorabuena! Tu perfil ha sido preseleccionado para el puesto de {job_title}.\n\n"
            "Estamos muy interesados en conocer más sobre ti y tu experiencia. "
            "En los próximos días nos pondremos en contacto para coordinar los siguientes pasos.\n\n"
            "Saludos cordiales,\nEl equipo de Selección de Nexova"
        ),
        "en": (
            "Subject: Good news, {candidate_name} — you've advanced to the next stage\n\n"
            "Dear {candidate_name},\n\n"
            "Congratulations! Your profile has been shortlisted for the position of {job_title}.\n\n"
            "We are very interested in learning more about you and your experience. "
            "We will contact you in the coming days to coordinate the next steps.\n\n"
            "Best regards,\nThe Nexova Selection Team"
        ),
    },
    "rejected": {
        "es": (
            "Asunto: Actualización sobre tu candidatura para {job_title}\n\n"
            "Hola {candidate_name},\n\n"
            "Gracias por el tiempo dedicado a tu proceso de selección con nosotros.\n\n"
            "Después de una cuidadosa evaluación, hemos decidido continuar con otros candidatos "
            "cuyo perfil se ajusta más a los requisitos actuales del puesto de {job_title}.\n\n"
            "Valoramos tu interés en Nexova y te animamos a seguir atento a futuras oportunidades "
            "que puedan encajar mejor con tu perfil. Guardaremos tu información en nuestra base de datos.\n\n"
            "Saludos cordiales,\nEl equipo de Selección de Nexova"
        ),
        "en": (
            "Subject: Update on your application for {job_title}\n\n"
            "Dear {candidate_name},\n\n"
            "Thank you for the time you dedicated to your selection process with us.\n\n"
            "After careful evaluation, we have decided to proceed with other candidates "
            "whose profile better matches the current requirements for {job_title}.\n\n"
            "We appreciate your interest in Nexova and encourage you to stay tuned for future "
            "opportunities that may be a better fit. We will keep your information in our database.\n\n"
            "Best regards,\nThe Nexova Selection Team"
        ),
    },
    "follow_up": {
        "es": (
            "Asunto: Recordatorio — {candidate_name}, estamos esperando tu respuesta\n\n"
            "Hola {candidate_name},\n\n"
            "Queríamos recordarte que estamos esperando tu respuesta respecto al puesto de {job_title}.\n\n"
            "Si tienes alguna pregunta o necesitas más información, no dudes en contactarnos.\n\n"
            "Esperamos saber de ti pronto.\n\n"
            "Saludos cordiales,\nEl equipo de Selección de Nexova"
        ),
        "en": (
            "Subject: Reminder — {candidate_name}, we're waiting for your response\n\n"
            "Dear {candidate_name},\n\n"
            "We wanted to remind you that we are waiting for your response regarding the position of {job_title}.\n\n"
            "If you have any questions or need more information, please do not hesitate to contact us.\n\n"
            "We look forward to hearing from you soon.\n\n"
            "Best regards,\nThe Nexova Selection Team"
        ),
    },
}


class CommunicationRecord:
    """Record of a sent communication for audit trail."""
    def __init__(
        self,
        candidate_id: str,
        communication_type: str,
        recipient_email: str,
        subject: str,
        body: str,
        language: str = "en",
    ):
        self.id = f"comm-{candidate_id}-{datetime.now(timezone.utc).timestamp()}"
        self.candidate_id = candidate_id
        self.communication_type = communication_type
        self.recipient_email = recipient_email
        self.subject = subject
        self.body = body
        self.language = language
        self.sent_at = datetime.now(timezone.utc).isoformat()
        self.status = "sent"
        self.error: Optional[str] = None


class SelectionCommunicationAgent:
    """
    Agent that manages automated candidate communications.
    
    Tools available to the agent:
    - send_status_update: Notify candidate of status changes
    - send_interview_confirmation: Send interview details
    - send_follow_up: Send follow-up for non-responsive candidates
    - get_communication_history: Retrieve past communications with a candidate
    - get_candidate_preferences: Get candidate language/contact preferences
    """

    def __init__(self):
        self.name = AGENT_NAME
        self.version = AGENT_VERSION
        self.role = AGENT_ROLE
        self.system_prompt = AGENT_SYSTEM_PROMPT
        self._communications: Dict[str, List[CommunicationRecord]] = {}
        self.logger = logging.getLogger(f"agent.{AGENT_NAME}")

    # ─── Tool 1: Send Status Update ──────────────────────────────────────────

    def send_status_update(
        self,
        candidate_id: str,
        candidate_name: str,
        candidate_email: str,
        job_title: str,
        new_status: str,
        language: str = "en",
        additional_context: Optional[Dict[str, str]] = None,
    ) -> CommunicationRecord:
        """
        Send a personalized email to a candidate when their status changes.
        
        Args:
            candidate_id: Unique identifier for the candidate
            candidate_name: Full name for personalization
            candidate_email: Recipient email address
            job_title: Position name for context
            new_status: The new status that triggered this communication
            language: 'es' for Spanish, 'en' for English
            additional_context: Extra data (e.g., interview_date, feedback)
        
        Returns:
            CommunicationRecord with details of the sent communication
        """
        if language not in ("es", "en"):
            language = "en"
        
        # Map status to template
        template_map = {
            "new": "new",
            "shortlisted": "shortlisted",
            "rejected": "rejected",
        }
        template_key = template_map.get(new_status)
        
        if not template_key:
            self.logger.info(
                f"No template for status '{new_status}' — skipping communication for {candidate_id}"
            )
            return CommunicationRecord(
                candidate_id=candidate_id,
                communication_type=f"status_{new_status}",
                recipient_email=candidate_email,
                subject="",
                body="",
                language=language,
            )

        template = TEMPLATES[template_key][language]
        
        # Personalize
        context = {
            "candidate_name": candidate_name,
            "job_title": job_title,
            **self._parse_additional_context(additional_context or {}),
        }
        
        body = template.format(**context)
        subject_line = body.split("\n")[0] if body.split("\n")[0] else "Update from Nexova"
        
        record = CommunicationRecord(
            candidate_id=candidate_id,
            communication_type=f"status_{new_status}",
            recipient_email=candidate_email,
            subject=subject_line,
            body=body,
            language=language,
        )
        
        self._store_communication(record)
        self.logger.info(
            f"Sent '{template_key}' to {candidate_email} ({candidate_name}) "
            f"— status: {new_status}"
        )
        return record

    # ─── Tool 2: Send Interview Confirmation ─────────────────────────────────

    def send_interview_confirmation(
        self,
        candidate_id: str,
        candidate_name: str,
        candidate_email: str,
        job_title: str,
        interview_date: str,
        interview_time: str,
        interview_type: str,
        location_or_link: str = "To be confirmed",
        language: str = "en",
    ) -> CommunicationRecord:
        """
        Send interview confirmation with full details.
        
        Args:
            candidate_id: Unique identifier
            candidate_name: Full name
            candidate_email: Recipient
            job_title: Position name
            interview_date: Date of interview
            interview_time: Time of interview
            interview_type: phone | video | in_person | technical
            location_or_link: Physical address or video link
            language: 'es' or 'en'
        """
        if language not in ("es", "en"):
            language = "en"

        template = TEMPLATES["interview_scheduled"][language]
        context = {
            "candidate_name": candidate_name,
            "job_title": job_title,
            "date": interview_date,
            "time": interview_time,
            "interview_type": interview_type,
            "location_or_link": location_or_link,
        }
        
        body = template.format(**context)
        subject_line = body.split("\n")[0] if body.split("\n")[0] else "Interview Confirmation"
        
        record = CommunicationRecord(
            candidate_id=candidate_id,
            communication_type="interview_scheduled",
            recipient_email=candidate_email,
            subject=subject_line,
            body=body,
            language=language,
        )
        
        self._store_communication(record)
        self.logger.info(
            f"Sent interview confirmation to {candidate_email} "
            f"for {job_title} on {interview_date} at {interview_time}"
        )
        return record

    # ─── Tool 3: Send Follow-Up ──────────────────────────────────────────────

    def send_follow_up(
        self,
        candidate_id: str,
        candidate_name: str,
        candidate_email: str,
        job_title: str,
        language: str = "en",
    ) -> CommunicationRecord:
        """
        Send a follow-up reminder to a non-responsive candidate.
        """
        if language not in ("es", "en"):
            language = "en"
        
        template = TEMPLATES["follow_up"][language]
        context = {
            "candidate_name": candidate_name,
            "job_title": job_title,
        }
        
        body = template.format(**context)
        subject_line = body.split("\n")[0] if body.split("\n")[0] else "Follow-up from Nexova"
        
        record = CommunicationRecord(
            candidate_id=candidate_id,
            communication_type="follow_up",
            recipient_email=candidate_email,
            subject=subject_line,
            body=body,
            language=language,
        )
        
        self._store_communication(record)
        self.logger.info(f"Sent follow-up to {candidate_email} ({candidate_name})")
        return record

    # ─── Tool 4: Get Communication History ───────────────────────────────────

    def get_communication_history(
        self, candidate_id: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Retrieve past communications with a candidate.
        
        Args:
            candidate_id: The candidate to look up
            limit: Max number of records to return
            
        Returns:
            List of communication records as dicts
        """
        records = self._communications.get(candidate_id, [])
        return [
            {
                "id": r.id,
                "type": r.communication_type,
                "recipient": r.recipient_email,
                "subject": r.subject,
                "sent_at": r.sent_at,
                "status": r.status,
                "language": r.language,
            }
            for r in records[-limit:]
        ]

    # ─── Tool 5: Determine Best Language ────────────────────────────────────

    @staticmethod
    def determine_language(candidate_languages: List[Dict[str, str]]) -> str:
        """
        Determine the best language for communication based on candidate profile.
        
        Args:
            candidate_languages: List of {language, level} dicts
            
        Returns:
            'es' or 'en'
        """
        for lang in candidate_languages:
            if lang.get("language", "").lower() == "spanish" and lang.get("level") in ("native", "C2", "C1"):
                return "es"
        return "en"

    # ─── Private Helpers ─────────────────────────────────────────────────────

    def _store_communication(self, record: CommunicationRecord):
        """Persist communication record for audit trail."""
        if record.candidate_id not in self._communications:
            self._communications[record.candidate_id] = []
        self._communications[record.candidate_id].append(record)

    @staticmethod
    def _parse_additional_context(context: Dict[str, str]) -> Dict[str, str]:
        """Normalize additional context keys for template formatting."""
        normalized = {}
        for key, value in context.items():
            normalized[key.replace(" ", "_").lower()] = value
        return normalized


# ─── Agent Orchestration (optional standalone use) ───────────────────────────

def run_agent_pipeline(candidate_info: Dict[str, Any]) -> List[CommunicationRecord]:
    """
    Standalone function to run the full agent pipeline for a candidate.
    
    This simulates how the agent would be invoked by the orchestrator when
    a domain event is published (e.g., candidate.registered, interview.scheduled).
    
    Args:
        candidate_info: Dict with keys: id, name, email, job_title, status,
                       languages, interview_details (optional)
    
    Returns:
        List of CommunicationRecord objects
    """
    agent = SelectionCommunicationAgent()
    sent: List[CommunicationRecord] = []
    
    language = agent.determine_language(candidate_info.get("languages", []))
    status = candidate_info.get("status", "new")
    
    # 1. Send status update for the current stage
    status_record = agent.send_status_update(
        candidate_id=candidate_info["id"],
        candidate_name=candidate_info["name"],
        candidate_email=candidate_info["email"],
        job_title=candidate_info["job_title"],
        new_status=status,
        language=language,
    )
    sent.append(status_record)
    
    # 2. If interview was scheduled, send confirmation too
    interview = candidate_info.get("interview_details")
    if interview and status == "interview_scheduled":
        interview_record = agent.send_interview_confirmation(
            candidate_id=candidate_info["id"],
            candidate_name=candidate_info["name"],
            candidate_email=candidate_info["email"],
            job_title=candidate_info["job_title"],
            interview_date=interview["date"],
            interview_time=interview["time"],
            interview_type=interview["type"],
            location_or_link=interview.get("location", "To be confirmed"),
            language=language,
        )
        sent.append(interview_record)
    
    return sent