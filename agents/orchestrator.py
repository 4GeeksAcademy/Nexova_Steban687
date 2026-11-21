"""
Agent Orchestrator for Nexova Solutions.

Coordinates multiple domain agents and routes domain events to the correct agent.
Acts as the central entry point for agent execution triggered by events from services.

In production, this would be connected to a message broker (Redis Pub/Sub, Kafka)
and orchestrated via LangGraph or CrewAI for multi-step agent workflows.
"""

import logging
from typing import Optional, List, Dict, Any

from agents.selection.agent import SelectionCommunicationAgent, CommunicationRecord

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """
    Routes domain events to the appropriate agent(s) and manages their execution.

    Current agents:
    - Selection Communication Agent: Handles candidate email communications
    
    Future agents (defined in techContext.md):
    - Training Advisor Agent: Course recommendations for clients
    - Support First-Line Agent: RAG-based chatbot for support tickets
    - Sales Proposal Agent: Suggest proposal angles for prospects
    - HR Internal Agent: Answers employee policy questions
    - Infrastructure Agent: Answers architecture questions
    - Executive Assistant Agent: Natural language business queries
    """

    def __init__(self):
        self.logger = logging.getLogger("agent.orchestrator")
        self._agents = {
            "selection-communication": SelectionCommunicationAgent(),
            # Future agents will be registered here:
            # "training-advisor": TrainingAdvisorAgent(),
            # "support-firstline": SupportFirstlineAgent(),
            # "sales-proposal": SalesProposalAgent(),
            # "hr-internal": HRInternalAgent(),
            # "infrastructure": InfrastructureAgent(),
            # "executive-assistant": ExecutiveAssistantAgent(),
        }
        # Event routing table: domain_event → list of agent names
        self._event_routes = {
            "candidate.registered": ["selection-communication"],
            "candidate.status_changed": ["selection-communication"],
            "candidate.scored": [],  # No notification needed
            "interview.scheduled": ["selection-communication"],
            "job.created": [],  # Internal only
        }

    def route_event(self, event_type: str, payload: Dict[str, Any]) -> List[CommunicationRecord]:
        """
        Route a domain event to the appropriate agents and execute them.

        Args:
            event_type: The domain event name (e.g., "candidate.registered")
            payload: Event data with relevant context

        Returns:
            List of CommunicationRecord from all triggered agents
        """
        agent_names = self._event_routes.get(event_type, [])
        if not agent_names:
            self.logger.info(f"No agents registered for event '{event_type}' — skipping")
            return []

        self.logger.info(f"Routing event '{event_type}' to agents: {agent_names}")
        results: List[CommunicationRecord] = []

        for agent_name in agent_names:
            agent = self._agents.get(agent_name)
            if agent is None:
                self.logger.warning(f"Agent '{agent_name}' not found — check registration")
                continue

            if isinstance(agent, SelectionCommunicationAgent):
                agent_results = self._handle_selection_event(agent, event_type, payload)
                results.extend(agent_results)

        return results

    def _handle_selection_event(
        self, agent: SelectionCommunicationAgent, event_type: str, payload: Dict[str, Any]
    ) -> List[CommunicationRecord]:
        """Handle selection domain events by invoking the communication agent."""
        records: List[CommunicationRecord] = []
        candidate_id = payload.get("candidate_id", "unknown")
        candidate_name = payload.get("candidate_name", payload.get("name", "Candidate"))
        candidate_email = payload.get("candidate_email", payload.get("email", ""))
        job_title = payload.get("job_title", "a position")
        language = payload.get("language", "en")

        if event_type == "candidate.registered":
            record = agent.send_status_update(
                candidate_id=candidate_id,
                candidate_name=candidate_name,
                candidate_email=candidate_email,
                job_title=job_title,
                new_status="new",
                language=language,
            )
            records.append(record)

        elif event_type == "candidate.status_changed":
            new_status = payload.get("new_status", "")
            record = agent.send_status_update(
                candidate_id=candidate_id,
                candidate_name=candidate_name,
                candidate_email=candidate_email,
                job_title=job_title,
                new_status=new_status,
                language=language,
            )
            records.append(record)

        elif event_type == "interview.scheduled":
            interview = payload.get("interview_details", {})
            # Also send status update for interview_scheduled
            status_record = agent.send_status_update(
                candidate_id=candidate_id,
                candidate_name=candidate_name,
                candidate_email=candidate_email,
                job_title=payload.get("job_title", ""),
                new_status="interview_scheduled",
                language=language,
            )
            records.append(status_record)

            # Send interview confirmation
            interview_record = agent.send_interview_confirmation(
                candidate_id=candidate_id,
                candidate_name=candidate_name,
                candidate_email=candidate_email,
                job_title=payload.get("job_title", ""),
                interview_date=interview.get("date", "TBD"),
                interview_time=interview.get("time", "TBD"),
                interview_type=interview.get("type", "video"),
                location_or_link=interview.get("location", "To be confirmed"),
                language=language,
            )
            records.append(interview_record)

        return records

    def list_registered_agents(self) -> List[Dict[str, str]]:
        """Return metadata on all registered agents."""
        return [
            {
                "name": name,
                "type": type(agent).__name__,
                "role": getattr(agent, "role", "Unknown"),
            }
            for name, agent in self._agents.items()
        ]

    def register_agent(self, name: str, agent: Any, events: List[str]):
        """Register a new agent and its event routes."""
        self._agents[name] = agent
        for event in events:
            if event not in self._event_routes:
                self._event_routes[event] = []
            if name not in self._event_routes[event]:
                self._event_routes[event].append(name)
        self.logger.info(f"Registered agent '{name}' for events: {events}")